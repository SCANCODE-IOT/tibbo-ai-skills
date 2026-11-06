#!/usr/bin/env python3
"""Static check of Tibbo BASIC / Tibbo C sources against the TiOS API reference.

Catches invented or misspelled API names before TIDE does:
  - unknown property, method or event of a TiOS object (sock.conect, ser.baud, sys.delay);
  - unknown PL_* constant (PL_SSTS_CONNECTED, PL_IO_NUM_99);
  - object or PL_* constant that the chosen platform does not have (--platform TPP2W(G2): adc, PL_ADC_NUM_0);
  - "elseif" in Tibbo BASIC (the grammar only has "else if").

Usage:
  python3 scripts/tibbo_lint.py <file or folder>... [--platform "TPP3W(G2)"] [--json]
Files: .tbs .tbh (Tibbo BASIC), .tc .th (Tibbo C). Folders are scanned recursively.
Exit codes: 0 - no errors, 1 - errors found, 2 - bad input.
Data: data/tios_api.json (rebuild with scripts/build_lint_data.py).
"""
import difflib
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data", "tios_api.json")
BASIC_EXT = (".tbs", ".tbh")
C_EXT = (".tc", ".th")


def strip_basic(line):
    """Remove string literals and ' comments from one Tibbo BASIC line, keep positions."""
    out, in_str = [], False
    for ch in line:
        if in_str:
            out.append(" ")
            if ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
            out.append(" ")
        elif ch == "'":
            break
        else:
            out.append(ch)
    return "".join(out)


def strip_c(text):
    """Remove comments and string/char literals from C text, keep line breaks."""
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))
    return re.sub(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'', blank, text, flags=re.S)


def collect_files(paths):
    files = []
    for p in paths:
        if os.path.isdir(p):
            for dirpath, _, names in os.walk(p):
                for n in sorted(names):
                    if n.lower().endswith(BASIC_EXT + C_EXT):
                        files.append(os.path.join(dirpath, n))
        elif os.path.isfile(p):
            files.append(p)
        else:
            raise FileNotFoundError(p)
    return files


def load_sources(files):
    src = []
    for f in files:
        with open(f, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        if f.lower().endswith(C_EXT):
            lines = strip_c(text).split("\n")
        else:
            lines = [strip_basic(l) for l in text.split("\n")]
        src.append((f, lines, f.lower().endswith(BASIC_EXT)))
    return src


def user_identifiers(src):
    """Names the project defines itself: #define, enum members, dim/const - they are not TiOS constants."""
    names = set()
    for _, lines, _ in src:
        text = "\n".join(lines)
        names.update(n.upper() for n in re.findall(r"#\s*define\s+(\w+)", text, re.I))
        names.update(n.upper() for n in re.findall(r"^\s*(?:enum|type)\s+(\w+)", text, re.I | re.M))
        for body in re.findall(r"^\s*enum\s+\w+(.*?)^\s*end\s+enum", text, re.I | re.S | re.M):
            names.update(n.upper() for n in re.findall(r"^\s*(\w+)", body, re.M))
        for body in re.findall(r"\benum\s+\w*\s*\{(.*?)\}", text, re.S):
            names.update(n.upper() for n in re.findall(r"(\w+)\s*(?:=[^,]*)?(?:,|$)", body))
        names.update(n.upper() for n in re.findall(r"\bconst\s+(\w+)", text, re.I))
    return names


def lint(paths, platform=None):
    data = json.load(open(DATA, encoding="utf-8"))
    members = {o: set(v) for o, v in data["objects"].items()}
    internal = {o: set(v) for o, v in data.get("internal", {}).items()}
    constants = set(data["constants"])
    plat_specific = set(data["platform_specific_constants"])
    plat = None
    if platform:
        lookup = {k.lower(): k for k in data["platforms"]}
        if platform.lower() not in lookup:
            raise KeyError(platform)
        plat = data["platforms"][lookup[platform.lower()]]
        plat_objects = set(plat["objects"])
        plat_consts = set(plat["constants"])

    src = load_sources(collect_files(paths))
    own = user_identifiers(src)
    symbol = (plat or {}).get("symbol")
    pid = (plat or {}).get("id")

    def branch_for_platform(cond):
        """True/False if the #if condition tests PLATFORM_ID, None if it does not."""
        eq = re.findall(r"PLATFORM_ID\s*=\s*(\w+)", cond, re.I)
        ne = re.findall(r"PLATFORM_ID\s*<>\s*(\w+)", cond, re.I)
        ours = lambda v: v.upper() == symbol or (pid is not None and v == str(pid))
        if eq:
            return any(ours(v) for v in eq)
        if ne:
            return not any(ours(v) for v in ne)
        return None
    obj_re = re.compile(r"(?<![\w.])(%s)\s*\.\s*([a-z_]\w*)" % "|".join(sorted(members, key=len, reverse=True)), re.I)
    const_re = re.compile(r"(?<![\w.])(PL_\w+)", re.I)
    findings = []

    def add(level, f, n, msg):
        findings.append({"level": level, "file": f, "line": n, "message": msg})

    for f, lines, is_basic in src:
        stack = []  # [is_platform_branch(None|bool), taken]: code for other platforms is not checked against ours
        for n, line in enumerate(lines, 1):
            pp = re.match(r"\s*#\s*(if|ifdef|ifndef|elif|else|endif)\b(.*)", line, re.I)
            if pp and plat is not None:
                kw, cond = pp.group(1).lower(), pp.group(2)
                if kw in ("if", "ifdef", "ifndef"):
                    act = branch_for_platform(cond) if kw == "if" else None
                    stack.append([act, bool(act)])
                elif kw == "elif" and stack:
                    act = branch_for_platform(cond)
                    if stack[-1][1] and act is not None:
                        act = False
                    stack[-1] = [act, stack[-1][1] or bool(act)]
                elif kw == "else" and stack:
                    stack[-1] = [None if stack[-1][0] is None and not stack[-1][1] else not stack[-1][1], True]
                elif kw == "endif" and stack:
                    stack.pop()
                continue
            other_platform = any(s[0] is False for s in stack)
            for m in obj_re.finditer(line):
                o, mem = m.group(1).lower(), m.group(2).lower()
                name = "%s.%s" % (o, mem)
                if plat is not None and not other_platform and o not in plat_objects:
                    add("error", f, n, "%s: объекта %s нет на платформе %s (platforms.md)" % (name, o, platform))
                if mem in members[o]:
                    continue
                if mem in internal.get(o, ()):
                    add("warning", f, n, "%s: внутренний член TiOS (в .tph со знаком !), в документации его нет" % name)
                    continue
                hint = difflib.get_close_matches(mem, members[o], n=2, cutoff=0.7)
                tip = " (похоже: %s)" % ", ".join("%s.%s" % (o, h) for h in hint) if hint else ""
                add("error", f, n, "%s: нет в справочнике TiOS%s - проверь tios-api.md" % (name, tip))
            for m in const_re.finditer(line):
                c = m.group(1).upper()
                if c in own:
                    continue
                if c not in constants:
                    hint = difflib.get_close_matches(c, constants, n=2, cutoff=0.8)
                    tip = " (похоже: %s)" % ", ".join(hint) if hint else ""
                    add("error", f, n, "%s: такой константы нет в TiOS%s" % (c, tip))
                elif plat is not None and not other_platform and c in plat_specific and c not in plat_consts:
                    add("error", f, n, "%s: этой константы нет на платформе %s (platforms.md)" % (c, platform))
            if is_basic and re.search(r"(?<!\w)elseif(?!\w)", line, re.I):
                add("error", f, n, "elseif: в Tibbo BASIC пишется раздельно - else if")
    return findings, len(src)


def main(argv):
    args, platform, as_json = [], None, False
    it = iter(argv)
    for a in it:
        if a == "--platform":
            platform = next(it, None)
        elif a == "--json":
            as_json = True
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            args.append(a)
    if not args:
        print(__doc__)
        return 2
    try:
        findings, nfiles = lint(args, platform)
    except FileNotFoundError as e:
        print("нет такого файла или папки: %s" % e, file=sys.stderr)
        return 2
    except KeyError as e:
        print("неизвестная платформа %s; список - в platforms.md" % e, file=sys.stderr)
        return 2
    errors = sum(1 for x in findings if x["level"] == "error")
    if as_json:
        print(json.dumps({"files": nfiles, "errors": errors, "findings": findings}, ensure_ascii=False, indent=1))
    else:
        for x in findings:
            tag = "[ОШИБКА]" if x["level"] == "error" else "[ВНИМАНИЕ]"
            print("%s:%d: %s %s" % (x["file"], x["line"], tag, x["message"]))
        print("Файлов: %d, ошибок: %d, предупреждений: %d" % (nfiles, errors, len(findings) - errors))
        if nfiles == 0:
            print("Файлы .tbs/.tbh/.tc/.th не найдены")
    if nfiles == 0:
        return 2
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
