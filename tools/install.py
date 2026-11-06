#!/usr/bin/env python3
"""Install the Tibbo skills (tibbo-firmware + appblocks) into AI coding agents.
Установка скиллов Tibbo (tibbo-firmware + appblocks) в ИИ-агенты.

Usage / запуск (from the unpacked repository / из распакованного репозитория):
  python tools/install.py                  # ~/.agents/skills + ~/.claude/skills (if Claude Code is installed)
  python tools/install.py --agent codex --agent gemini
  python tools/install.py --list           # supported agents and folders
  python tools/install.py --project .      # into ./.agents/skills of one project only
  python tools/install.py --uninstall      # remove from the same folders

On Windows use "python", on macOS/Linux "python3". Python 3.9+, no extra packages.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SKILLS = ["tibbo-firmware", "appblocks"]
HOME = Path.home()

# agent -> (global skills folder, who reads it)
AGENTS = {
    "agents":   (HOME / ".agents" / "skills", "Codex (CLI, IDE extension), Gemini CLI, Kimi Code, Deep Code (DeepSeek), Cline, Zed"),
    "claude":   (HOME / ".claude" / "skills", "Claude Code (also GLM/DeepSeek models running inside Claude Code)"),
    "gemini":   (HOME / ".gemini" / "skills", "Gemini CLI (it also reads ~/.agents/skills)"),
    "opencode": (HOME / ".config" / "opencode" / "skills", "OpenCode (any model: GLM, DeepSeek, Kimi, Qwen...)"),
    "cursor":   (HOME / ".cursor" / "skills", "Cursor"),
    "copilot":  (HOME / ".copilot" / "skills", "GitHub Copilot"),
    "kimi":     (HOME / ".kimi-code" / "skills", "Kimi Code (it also reads ~/.agents/skills)"),
}
ALIASES = {"codex": "agents", "deepseek": "agents", "deepcode": "agents", "kimi-code": "agents", "glm": "opencode",
           "zcode": "claude", "claude-code": "claude", "gemini-cli": "gemini"}


def source_dir():
    here = Path(__file__).resolve().parent
    for cand in (here.parent / "skills", here / "skills", here.parent):
        if all((cand / s / "SKILL.md").is_file() for s in SKILLS):
            return cand
    sys.exit("Skills not found next to this script. Unpack the whole repository and run tools/install.py from it.\n"
             "Скиллы не найдены рядом со скриптом. Распакуйте репозиторий целиком и запустите tools/install.py из него.")


def install(src, dest):
    dest.mkdir(parents=True, exist_ok=True)
    for s in SKILLS:
        target = dest / s
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(src / s, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    # quick self-test from the installed copy: both skills, including the appblocks -> tps_check bridge
    py = sys.executable or "python3"
    ok = subprocess.run([py, str(dest / "tibbo-firmware" / "scripts" / "tps_check.py"), "find", "rs485"],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0
    ok = ok and subprocess.run([py, str(dest / "tibbo-firmware" / "scripts" / "tibbo_lint.py"),
                                str(dest / "tibbo-firmware" / "tests" / "lint" / "good.tbs")],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE).returncode == 0
    return ok


def main():
    ap = argparse.ArgumentParser(description="Install Tibbo skills into AI agents / установка скиллов Tibbo в ИИ-агенты")
    ap.add_argument("--agent", action="append", default=[], help="agents, claude, gemini, opencode, cursor, copilot, kimi, all "
                    "(codex/deepseek/kimi-code = agents, glm = opencode)")
    ap.add_argument("--project", metavar="DIR", help="install into DIR/.agents/skills (one project) instead of your home folder")
    ap.add_argument("--uninstall", action="store_true", help="remove the skills from the chosen folders")
    ap.add_argument("--list", action="store_true", help="show supported agents and folders")
    a = ap.parse_args()

    if a.list:
        for k, (path, who) in AGENTS.items():
            print("%-9s %s\n          %s" % (k, path, who))
        return 0

    if a.project:
        targets = [("project", Path(a.project).resolve() / ".agents" / "skills", "this project, all agents that read .agents/skills")]
    else:
        names = [ALIASES.get(n.lower(), n.lower()) for n in a.agent]
        if "all" in names:
            names = list(AGENTS)
        if not names:
            names = ["agents"] + (["claude"] if (HOME / ".claude").exists() else [])
        bad = [n for n in names if n not in AGENTS]
        if bad:
            ap.error("unknown agent: %s (see --list)" % ", ".join(bad))
        targets = [(n, AGENTS[n][0], AGENTS[n][1]) for n in dict.fromkeys(names)]

    src = None if a.uninstall else source_dir()
    failed = False
    for name, path, who in targets:
        if a.uninstall:
            removed = [s for s in SKILLS if (path / s).exists()]
            for s in removed:
                shutil.rmtree(path / s)
            print("%s: %s" % (path, "removed / удалено" if removed else "nothing to remove / нечего удалять"))
            continue
        ok = install(src, path)
        failed |= not ok
        print("%s -> %s\n  %s\n  self-test / самопроверка: %s" % (name, path, who, "ok" if ok else "FAILED / ОШИБКА"))
    if not a.uninstall:
        print("\nDone. Restart your agent and ask about Tibbo. / Готово. Перезапустите агента и задайте вопрос про Tibbo.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
