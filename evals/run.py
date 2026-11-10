#!/usr/bin/env python3
"""Control tasks for the Tibbo skills: run an agent on every task and check the result automatically.

    python3 evals/run.py --agent claude                     # every task, skills installed into the task folder
    python3 evals/run.py --agent claude --model haiku       # a smaller model
    python3 evals/run.py --agent claude --no-skills         # the same model without the skills (baseline)
    python3 evals/run.py --agent codex | gemini             # other agents (presets; check them with --dry)
    python3 evals/run.py --cmd 'mycli run --prompt-file {prompt_file}'    # any agent: {prompt_file} or {prompt}
    python3 evals/run.py --grade RUN_DIR                    # check results again, without running the agent
    python3 evals/run.py --report RUN_DIR [RUN_DIR ...]     # one table for several runs

Options: --tasks id,id   --jobs N (parallel tasks, default 2)   --timeout SEC (per task, default 900)
         --out DIR (default evals/runs/<agent>-<model>-<skills|plain>-<time>)   --dry (print commands only)
         --claude-config DIR (separate settings folder for the claude preset)

What a run does: for every task it makes an empty folder, copies the task's input files and (unless --no-skills) both
skills into .agents/skills and .claude/skills, starts the agent in that folder with the task text, saves what the agent
printed as answer.md, then checks the folder: project compiles with Tibbo's compiler, linter is clean, tps_check /
ab_tool pass, required facts are in the answer. The checks use the tools of THIS repository, whatever the agent used.
Compiling needs Tibbo's compiler (python3 skills/tibbo-firmware/scripts/tibbo_build.py --setup-node --yes); without it
the "compiles" checks are reported as "not checked". Standard library only.
"""
import concurrent.futures
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FW = os.path.join(ROOT, "skills", "tibbo-firmware")
AB = os.path.join(ROOT, "skills", "appblocks")
SKIP_DIRS = (".agents", ".claude", ".git", "node_modules", "tmp")

# Tools the agent may use in the claude preset: files in the task folder, Python scripts and read-only shell commands.
CLAUDE_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Skill"] + ["Bash(%s:*)" % c for c in (
    "python3", "python", "ls", "mkdir", "cp", "cd", "cat", "grep", "head", "tail", "sed", "find", "wc", "echo", "sort")]
# The same note for every run of this preset: it describes the sandbox, not the task.
CLAUDE_NOTE = ("Среда запуска: команды оболочки ограничены - разрешены python3, ls, cat, grep, head, tail, sed, find, cp, mkdir "
               "без перенаправления вывода в файл. Файлы создавай и меняй инструментами Write и Edit. Сети нет.")
PRESETS = {
    "claude": lambda a: ["claude", "-p", "{prompt}", "--output-format", "stream-json", "--verbose", "--strict-mcp-config",
                         "--append-system-prompt", CLAUDE_NOTE, "--permission-mode", "acceptEdits", "--allowedTools"] + CLAUDE_TOOLS
                        + (["--model", a["model"]] if a.get("model") else []),
    # Not run by the authors: check the flags with your version (--dry prints the command).
    "codex": lambda a: ["codex", "exec", "--full-auto", "--skip-git-repo-check"]
                       + (["--model", a["model"]] if a.get("model") else []) + ["{prompt}"],
    "gemini": lambda a: ["gemini", "--yolo"] + (["--model", a["model"]] if a.get("model") else []) + ["-p", "{prompt}"],
}


def utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def opt(argv, name, default=None):
    return argv[argv.index(name) + 1] if name in argv and argv.index(name) + 1 < len(argv) else default


def py(script, *args, env=None, cwd=None, timeout=300):
    r = subprocess.run([sys.executable, script, *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=env, cwd=cwd, timeout=timeout)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# ---------------------------------------------------------------- workspace

def prepare(task, ws, skills):
    os.makedirs(ws, exist_ok=True)
    if task.get("fixture"):
        src = os.path.join(HERE, task["fixture"])
        for n in os.listdir(src):
            s, d = os.path.join(src, n), os.path.join(ws, n)
            shutil.copytree(s, d) if os.path.isdir(s) else shutil.copy(s, d)
    if task.get("fixture_file"):
        shutil.copy(os.path.join(ROOT, task["fixture_file"]["from"]), os.path.join(ws, task["fixture_file"]["to"]))
    if skills:
        for base in (".agents", ".claude"):
            for sk in (FW, AB):
                shutil.copytree(sk, os.path.join(ws, base, "skills", os.path.basename(sk)),
                                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "tmp", "tests"))


def agent_env(args):
    env = dict(os.environ)
    # an agent started from inside another agent session must not inherit that session's skills and plugins
    for k in ("CLAUDE_CODE_SYNC_SKILLS", "CLAUDE_CODE_SYNC_PLUGINS", "CLAUDE_CODE_CCR_EARLY_PLUGINS_SYNC"):
        env.pop(k, None)
    if args.get("claude_config"):
        env["CLAUDE_CONFIG_DIR"] = args["claude_config"]
    return env


def run_agent(task, ws, args, tail):
    prompt = task["prompt"] + tail
    pf = os.path.join(ws, ".task_prompt.txt")
    open(pf, "w", encoding="utf-8").write(prompt)
    if args.get("cmd"):
        cmd = [x.replace("{prompt_file}", pf).replace("{prompt}", prompt) for x in shlex.split(args["cmd"])]
    else:
        cmd = [x.replace("{prompt}", prompt) for x in PRESETS[args["agent"]](args)]
    if args.get("dry"):
        print("cd %s && %s" % (ws, " ".join(shlex.quote(c) for c in cmd)))
        return {"skipped": True}
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=ws, env=agent_env(args), capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=args["timeout"], stdin=subprocess.DEVNULL)
        out, err, rc, timed_out = r.stdout or "", r.stderr or "", r.returncode, False
    except subprocess.TimeoutExpired as e:
        dec = lambda b: b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")
        out, err, rc, timed_out = dec(e.stdout), dec(e.stderr), -1, True
    except FileNotFoundError:
        return {"error": "agent program not found: %s" % cmd[0]}
    info = {"seconds": round(time.time() - t0), "rc": rc, "timed_out": timed_out}
    open(os.path.join(ws, ".agent_stdout.txt"), "w", encoding="utf-8").write(out)
    open(os.path.join(ws, ".agent_stderr.txt"), "w", encoding="utf-8").write(err[-20000:])
    answer, tools = out, None
    if args["agent"] == "claude" and not args.get("cmd"):
        answer, tools, extra = parse_claude(out)
        info.update(extra)
    open(os.path.join(ws, "answer.md"), "w", encoding="utf-8").write(answer)
    if tools is not None:
        json.dump(tools, open(os.path.join(ws, ".agent_tools.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return info


def parse_claude(out):
    """stream-json: the final answer, every tool call (to see which checks the agent ran itself), cost."""
    answer, tools, extra, texts = "", [], {}, []
    for line in out.splitlines():
        try:
            e = json.loads(line)
        except ValueError:
            continue
        if e.get("type") == "system" and e.get("subtype") == "init":
            extra["model"] = e.get("model")
            extra["skills_seen"] = [s for s in (e.get("skills") or []) if "tibbo" in s or "appblocks" in s]
        elif e.get("type") == "assistant":
            for c in (e.get("message") or {}).get("content") or []:
                if c.get("type") == "tool_use":
                    i = c.get("input") or {}
                    tools.append({"tool": c.get("name"), "arg": str(i.get("command") or i.get("file_path") or i.get("skill")
                                                                   or i.get("pattern") or i.get("path") or "")[:400]})
                elif c.get("type") == "text" and c.get("text"):
                    texts.append(c["text"])
        elif e.get("type") == "result":
            answer = e.get("result") or ""
            extra["cost_usd"] = e.get("total_cost_usd")
            extra["turns"] = e.get("num_turns")
            extra["denied"] = len(e.get("permission_denials") or [])
            if e.get("is_error"):
                extra["agent_error"] = str(e.get("result"))[:300]
    if not answer:
        answer = "\n\n".join(texts[-3:])
    return answer, tools, extra


# ---------------------------------------------------------------- checks

def find_project(ws):
    hits = []
    for base, dirs, files in os.walk(ws):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        hits += [os.path.join(base, f) for f in files if f.lower().endswith(".tpr")]
    hits.sort(key=lambda p: (0 if os.sep + "project" + os.sep in p else 1, len(p)))
    return hits[0] if hits else None


def no_comment(line):
    """A Tibbo BASIC line without its comment (an apostrophe outside a string starts a comment)."""
    q = False
    for i, ch in enumerate(line):
        if ch == '"':
            q = not q
        elif ch == "'" and not q:
            return line[:i]
    return line


def sources_text(ws):
    tpr = find_project(ws)
    if not tpr:
        return ""
    out = []
    for base, dirs, files in os.walk(os.path.dirname(tpr)):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.lower().endswith((".tbs", ".tbh", ".tc", ".th")):
                raw = open(os.path.join(base, f), encoding="utf-8", errors="replace").read()
                out.append("\n".join(no_comment(l) for l in raw.splitlines()))       # comments do not count
    return "\n".join(out)


def tpr_value(tpr, key):
    for line in open(tpr, encoding="utf-8", errors="replace"):
        m = re.match(r"\s*%s\s*=\s*(.*?)\s*(;.*)?$" % key, line, re.I)
        if m:
            return m.group(1).strip()
    return ""


def compiler_env():
    home = os.environ.get("TIBBO_BASIC_HOME") or os.path.join(os.path.expanduser("~"), ".tibbo", "tibbo-basic")
    js = os.path.join(home, "server", "out", "compiler", "compile-project.js")
    if not os.path.exists(js) or not shutil.which("node"):
        return None
    return dict(os.environ, TIBBO_BASIC_HOME=home, TIDE_DIR=os.path.join(HERE, "no-tide"))


def load_json(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def nodes_of(d):
    return sorted((f["id"], json.dumps(f.get("settings"), sort_keys=True, ensure_ascii=False))
                  for f in (d or {}).get("features", []) if str(f.get("id", "")).startswith("node_"))


def check(c, ws, answer):
    """-> (True | False | None, detail). None = could not be checked here."""
    t = c["type"]
    flags = re.I | re.S
    text = answer if c.get("where") == "answer" else None
    if t in ("regex", "regex_all", "regex_absent") and text is None:
        text = sources_text(ws)
        if not text and t != "regex_absent":
            return False, "нет исходников проекта"
    if t == "regex":
        return bool(re.search(c["pattern"], text, flags)), ""
    if t == "regex_all":
        miss = [p for p in c["patterns"] if not re.search(p, text, flags)]
        return not miss, ("нет: " + ", ".join(miss)) if miss else ""
    if t == "regex_absent":
        m = re.search(c["pattern"], text, flags)
        return not m, ("найдено: " + m.group(0)[:60]) if m else ""
    if t == "no_file":
        hits = [p for p in glob.glob(os.path.join(ws, c["glob"]), recursive=True)
                if not any(os.sep + d + os.sep in p for d in SKIP_DIRS)]
        return not hits, ("есть " + os.path.relpath(hits[0], ws)) if hits else ""
    if t in ("tpr_platform", "lint_clean", "compiles"):
        tpr = find_project(ws)
        if not tpr:
            return False, "нет файла .tpr"
        if t == "tpr_platform":
            p = tpr_value(tpr, "platform")
            return p in c["platforms"], "platform=" + p
        if t == "lint_clean":
            rc, out = py(os.path.join(FW, "scripts", "tibbo_lint.py"), os.path.dirname(tpr), "--json")
            try:
                errs = [f for f in json.loads(out)["findings"] if f["level"] == "error"]
            except (ValueError, KeyError):
                return False, out[-200:]
            return not errs, "; ".join("%s:%s %s" % (os.path.basename(f["file"]), f["line"], f["message"][:90]) for f in errs[:3])
        env = compiler_env()
        if not env:
            return None, "компилятор Tibbo не установлен"
        tmp = os.path.join(ws, ".build_copy")
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.copytree(os.path.dirname(tpr), tmp, ignore=shutil.ignore_patterns(*SKIP_DIRS, ".build_copy"))
        rc, out = py(os.path.join(FW, "scripts", "tibbo_build.py"), os.path.join(tmp, os.path.basename(tpr)), "--node", "--json", env=env)
        try:
            j = json.loads(out[out.index("{"):])
        except ValueError:
            return False, out[-300:].strip()
        return bool(j.get("ok")), "; ".join("%s(%s) %s" % (e.get("file"), e.get("line"), e.get("message", "")[:90]) for e in (j.get("errors") or [])[:3])
    if t in ("tps_check_ok", "cfg"):
        path = os.path.join(ws, c.get("file", "cfg.json"))
        cfg = load_json(path)
        if not isinstance(cfg, dict):
            return False, "нет файла %s или это не JSON" % c.get("file", "cfg.json")
        if t == "tps_check_ok":
            rc, out = py(os.path.join(FW, "scripts", "tps_check.py"), "check", path)
            errs = [l for l in out.splitlines() if "[ОШИБКА]" in l]
            return rc == 0, "; ".join(e[:140] for e in errs[:3])
        models = []
        for v in (cfg.get("slots") or {}).values():
            models.append(str(v.get("model") if isinstance(v, dict) else v).lstrip("#"))
        try:
            return bool(eval(c["expr"], {"__builtins__": {}}, {"cfg": cfg, "models": models, "any": any, "all": all, "str": str,
                                                                "float": float, "bool": bool, "len": len})), "Tibbit: " + ", ".join(models)
        except Exception as e:      # a malformed cfg is a failed check, not a crash of the run
            return False, "cfg: %s" % e
    if t in ("ab_check_ok", "ab_variable", "ab_no_node", "ab_same_nodes"):
        path = os.path.join(ws, c["file"])
        d = load_json(path)
        if t == "ab_no_node":
            if d is None:
                return True, "файла %s нет" % c["file"]
            n = sum(1 for f in d.get("features", []) if f.get("id") == c["node"])
            return n == 0, "блоков %s: %d" % (c["node"], n)
        if not isinstance(d, dict) or not isinstance(d.get("features"), list):
            return False, "нет файла %s или это не проект AppBlocks" % c["file"]
        if t == "ab_check_ok":
            rc, out = py(os.path.join(AB, "scripts", "ab_tool.py"), "check", path)
            errs = [l for l in out.splitlines() if "[ОШИБКА]" in l]
            return rc == 0, "; ".join(e[:140] for e in errs[:3])
        if t == "ab_variable":
            gv = [f for f in d["features"] if f.get("id") == "global_vars"]
            names = [v.get("settings", {}).get("VARNAME") for f in gv for k in ("VARS", "AUTOVARS") for v in f.get("settings", {}).get(k, [])]
            return c["name"] in names, ""
        base = load_json(os.path.join(ws, c["base"]))
        return nodes_of(d) == nodes_of(base), ""
    return None, "неизвестная проверка " + t


def process_facts(ws):
    """Which checking tools the agent ran itself (known only for agents that give a transcript)."""
    tools = load_json(os.path.join(ws, ".agent_tools.json"))
    if tools is None:
        return None
    cmds = " ".join(t["arg"] for t in tools if t["tool"] == "Bash")
    used = [n for n in ("tibbo_new.py", "tibbo_lint.py", "tibbo_build.py", "tps_check.py", "ab_tool.py") if n in cmds]
    skill = any(t["tool"] == "Skill" for t in tools) or any("SKILL.md" in t["arg"] for t in tools)
    outside = sorted({t["arg"][:120] for t in tools if re.search(r"skills/(tibbo-firmware|appblocks)\b", t["arg"])
                      and ".claude/skills/" not in t["arg"] and ".agents/skills/" not in t["arg"]})
    return {"ran": used, "read_skill": skill, "tool_calls": len(tools), "outside_skills": outside}


def grade(task, ws):
    answer = ""
    try:
        answer = open(os.path.join(ws, "answer.md"), encoding="utf-8").read()
    except OSError:
        pass
    res = []
    for c in task["checks"]:
        try:
            ok, detail = check(c, ws, answer)
        except subprocess.TimeoutExpired:
            ok, detail = False, "проверка не уложилась во время"
        res.append({"id": c["id"], "what": c["what"], "ok": ok, "detail": detail, "critical": c.get("critical", True)})
    crit = [r for r in res if r["critical"] and r["ok"] is not None]
    return {"id": task["id"], "group": task["group"], "title": task["title"], "checks": res,
            "passed": bool(crit) and all(r["ok"] for r in crit), "score": sum(1 for r in res if r["ok"]),
            "of": sum(1 for r in res if r["ok"] is not None), "process": process_facts(ws)}


# ---------------------------------------------------------------- report

def report(run_dirs):
    runs = []
    for d in run_dirs:
        j = load_json(os.path.join(d, "result.json"))
        if j:
            runs.append(j)
    if not runs:
        print("нет result.json в указанных папках")
        return 2
    L = ["| Задача | " + " | ".join(r["label"] for r in runs) + " |", "|---|" + "---|" * len(runs)]
    ids = [t["id"] for t in runs[0]["tasks"]]
    for i in ids:
        row = []
        title = ""
        for r in runs:
            t = next((x for x in r["tasks"] if x["id"] == i), None)
            if not t:
                row.append("-")
                continue
            title = t["title"]
            row.append("%s %d/%d" % ("да" if t["passed"] else "НЕТ", t["score"], t["of"]))
        L.append("| %s | %s |" % (title, " | ".join(row)))
    L.append("| **Задач решено** | " + " | ".join("**%d из %d**" % (sum(1 for t in r["tasks"] if t["passed"]), len(r["tasks"])) for r in runs) + " |")
    L.append("| Проверок пройдено | " + " | ".join("%d из %d" % (sum(t["score"] for t in r["tasks"]), sum(t["of"] for t in r["tasks"])) for r in runs) + " |")
    print("\n".join(L))
    for r in runs:
        bad = [(t, c) for t in r["tasks"] for c in t["checks"] if c["ok"] is False]
        if bad:
            print("\n%s - не пройдено:" % r["label"])
            for t, c in bad:
                print("  %-16s %s%s" % (t["id"], c["what"], (" [" + c["detail"][:160] + "]") if c["detail"] else ""))
    return 0


def main(argv):
    utf8()
    if "--help" in argv or "-h" in argv or not argv:
        print(__doc__)
        return 0
    if "--report" in argv:
        return report(argv[argv.index("--report") + 1:])
    spec = json.load(open(os.path.join(HERE, "tasks.json"), encoding="utf-8"))
    only = (opt(argv, "--tasks") or "").split(",") if "--tasks" in argv else None
    tasks = [t for t in spec["tasks"] if not only or t["id"] in only]
    if "--grade" in argv:
        out = opt(argv, "--grade")
        old = load_json(os.path.join(out, "result.json")) or {"label": os.path.basename(out.rstrip("/")), "tasks": []}
        info = {t["id"]: t.get("run") for t in old["tasks"]}
        res = []
        for t in tasks:
            if os.path.isdir(os.path.join(out, t["id"])):
                g = grade(t, os.path.join(out, t["id"]))
                g["run"] = info.get(t["id"])
                res.append(g)
        old["tasks"] = res
        json.dump(old, open(os.path.join(out, "result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return report([out])
    args = {"agent": opt(argv, "--agent", "claude"), "model": opt(argv, "--model"), "cmd": opt(argv, "--cmd"),
            "timeout": int(opt(argv, "--timeout", "900")), "dry": "--dry" in argv, "claude_config": opt(argv, "--claude-config")}
    if not args["cmd"] and args["agent"] not in PRESETS:
        print("неизвестный агент %s: есть %s или --cmd '...'" % (args["agent"], ", ".join(PRESETS)))
        return 2
    skills = "--no-skills" not in argv
    label = "%s%s, %s" % (args["agent"] if not args["cmd"] else "свой агент", (" " + args["model"]) if args["model"] else "",
                          "со скиллами" if skills else "без скиллов")
    out = opt(argv, "--out") or os.path.join(HERE, "runs", "%s-%s-%s-%s" % (
        args["agent"], args["model"] or "default", "skills" if skills else "plain", time.strftime("%Y%m%d-%H%M%S")))
    os.makedirs(out, exist_ok=True)
    tail = spec["tail"]["ru"]

    def one(t):
        ws = os.path.join(out, t["id"])
        if os.path.isdir(ws):
            shutil.rmtree(ws)
        prepare(t, ws, skills)
        info = run_agent(t, ws, args, tail)
        if info.get("skipped"):
            return None
        g = grade(t, ws)
        g["run"] = info
        print("%-4s %-16s %d/%d  %s с%s" % ("да" if g["passed"] else "НЕТ", t["id"], g["score"], g["of"], info.get("seconds", "?"),
                                           "  (" + info["error"] + ")" if info.get("error") else ""), flush=True)
        return g

    with concurrent.futures.ThreadPoolExecutor(max_workers=int(opt(argv, "--jobs", "2"))) as ex:
        res = [r for r in ex.map(one, tasks) if r]
    if args["dry"]:
        return 0
    json.dump({"label": label, "agent": args["agent"], "model": args["model"], "skills": skills,
               "date": time.strftime("%Y-%m-%d"), "tasks": res},
              open(os.path.join(out, "result.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print()
    report([out])
    print("\nПапка прогона: %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
