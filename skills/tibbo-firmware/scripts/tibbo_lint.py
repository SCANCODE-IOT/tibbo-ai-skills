#!/usr/bin/env python3
"""Static check of Tibbo BASIC / Tibbo C sources against the TiOS API reference.

Catches what AI models and newcomers get wrong, before the compiler does - and a few things no compiler reports:
  - unknown property, method or constant (sock.conect, sys.delay, PL_SSTS_CONNECTED, PL_IO_NUM_99);
  - a member, object or event the CHOSEN PLATFORM does not have (ser.baud on TPP3W(G2)); an optional object
    (fd, kp, lcd, wln) the project has not switched on with defines= in the .tpr;
  - writing to a read-only property, wrong number of arguments of a method;
  - event handlers: an invented event (the handler would never be called - no compiler error!), wrong arguments,
    the same handler written twice, a handler called as a sub;
  - a callback_* of an included Tibbo library that the project does not define (linker error otherwise);
  - other languages' habits: elseif, return, print, sleep, != && || ==, +=, & for strings, string(300), unknown types;
  - the .tpr itself: no platform, a listed file is missing, a library file without location = commonlib.
The platform is taken from --platform or from the .tpr in the checked folder.

Usage:
  python3 scripts/tibbo_lint.py <file or folder>... [--platform "TPP3W(G2)"] [--json]
Files: .tbs .tbh (Tibbo BASIC), .tc .th (Tibbo C). Folders are scanned recursively.
Exit codes: 0 - no errors, 1 - errors found, 2 - bad input.
Data: data/platform_api.json (exact API per platform, from Tibbo's compiler), data/tios_api.json, data/libraries.json.
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


def keep_basic(line):
    """Like strip_basic, but every string literal becomes "" - arguments stay countable."""
    out, in_str = [], False
    for ch in line:
        if in_str:
            if ch == '"':
                in_str = False
                out.append('"')
        elif ch == '"':
            in_str = True
            out.append('"')
        elif ch == "'":
            break
        else:
            out.append(ch)
    return "".join(out)


def find_tpr(paths):
    """The project file of the checked folder: platform, defines=, listed files. None if there is not exactly one."""
    found = []
    for p in paths:
        d = p if os.path.isdir(p) else os.path.dirname(os.path.abspath(p))
        found += [os.path.join(d, n) for n in sorted(os.listdir(d)) if n.lower().endswith(".tpr")]
    found = sorted(set(found))
    if len(found) != 1:
        return None
    info = {"path": found[0], "platform": None, "defines": "", "files": []}
    section = None
    for line in open(found[0], encoding="utf-8", errors="replace"):
        line = line.strip()
        m = re.match(r"\[(.+)\]$", line)
        if m:
            section = m.group(1).lower()
        elif "=" in line and not line.startswith(";"):
            k, v = [x.strip() for x in line.split("=", 1)]
            if section == "project" and k.lower() in ("platform", "defines"):
                info[k.lower()] = v
            elif section and section.startswith("file") and k.lower() == "path":
                info["files"].append({"path": v, "condition": ""})
            elif section and section.startswith("file") and k.lower() == "condition" and info["files"]:
                info["files"][-1]["condition"] = v
    return info


def project_files(tpr, scanned):
    """Which of the scanned files the project really compiles: (to check, skipped: conditional, not in the project)."""
    root = os.path.dirname(tpr["path"])
    norm = lambda p: os.path.normcase(os.path.abspath(p))
    listed, conditional = set(), set()
    for e in tpr["files"]:
        full = norm(os.path.join(root, e["path"].replace("\\", os.sep)))
        (conditional if e["condition"].strip() else listed).add(full)
    check, cond, stray = [], [], []
    for f in scanned:
        n = norm(f)
        rel = os.path.relpath(n, norm(root)).replace(os.sep, "/")
        if n in listed:
            check.append(f)
        elif n in conditional:
            cond.append(f)
        elif rel.startswith("..") :
            check.append(f)                       # given explicitly from outside the project folder
        elif rel.lower().startswith("platforms/"):
            continue                              # the project's own copy of TIDE platforms and old libraries
        elif f.lower().endswith((".tbh", ".th")):
            check.append(f)                       # headers get in through include
        else:
            stray.append(f)
    return check, cond, stray


def split_args(text):
    """Arguments of a call: text right after the opening bracket -> list, or None if the bracket is not closed."""
    depth, cur, args = 0, "", []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            if depth == 0:
                args.append(cur)
                return [] if len(args) == 1 and not args[0].strip() else args
            depth -= 1
        elif ch == "," and depth == 0:
            args.append(cur)
            cur = ""
            continue
        cur += ch
    return None


BASIC_TYPES = {"byte", "char", "word", "short", "integer", "dword", "long", "real", "float", "string", "boolean"}
FOREIGN_TYPES = {"int", "uint", "uint8", "uint16", "uint32", "int8", "int16", "int32", "double", "single", "bool",
                 "unsigned", "str", "number", "variant", "object", "uint8_t", "uint16_t", "uint32_t"}
FOREIGN_CALLS = {"print": "вывод - sys.debugprint(\"...\")", "printf": "вывод - sys.debugprint(\"...\")",
                 "sleep": "пауз нет: считай тики в on_sys_timer", "delay": "пауз нет: считай тики в on_sys_timer",
                 "wait": "пауз нет: считай тики в on_sys_timer", "cstr": "число в строку - str() или lstr()",
                 "cint": "строка в число - val() или lval()", "tostring": "число в строку - str() или lstr()",
                 "format": "форматирования нет: str(), hex(), ftostr()", "substring": "подстрока - mid(s, pos, len)",
                 "ucase": "такой функции нет", "lcase": "такой функции нет", "trim": "такой функции нет",
                 "replace": "такой функции нет: instr() + left()/mid()/right()", "split": "такой функции нет: instr() + mid()"}


def basic_checks(src_files, exact, api, enabled_optional, platform, tpr, libs, add):
    """Checks that need the whole project: events, callbacks, habits of other languages. Tibbo BASIC files only."""
    files = []
    for f in src_files:
        if f.lower().endswith(BASIC_EXT):
            with open(f, encoding="utf-8", errors="replace") as fh:
                files.append((f, [keep_basic(l) for l in fh.read().split("\n")]))
    defined, declared, called = {}, set(), set()
    conditional_defs = set()    # procedures written inside #if: there may be two variants of one handler
    proc_re = re.compile(r"^\s*(?:public\s+|private\s+)?(sub|function)\s+([a-z_]\w*)\s*(\((.*))?", re.I)
    for f, lines in files:
        depth = 0
        for n, line in enumerate(lines, 1):
            pp = re.match(r"\s*#\s*(if|ifdef|ifndef|endif)\b", line, re.I)
            if pp:
                depth += -1 if pp.group(1).lower() == "endif" else 1
                continue
            m = proc_re.match(line)
            if m:
                defined.setdefault(m.group(2).lower(), []).append((f, n, m))
                if depth > 0:
                    conditional_defs.add(m.group(2).lower())
                continue
            d = re.match(r"^\s*declare\s+(?:sub|function)\s+([a-z_]\w*)", line, re.I)
            if d:
                declared.add(d.group(1).lower())
                continue
            for w in re.findall(r"(?<![\w.])([a-z_]\w*)", line, re.I):
                called.add(w.lower())
    own = set(defined) | declared

    events_here = {}       # event -> signature on this platform
    all_events = set(api["events"]) if api else set()
    if exact:
        for e, v in exact["events"].items():
            events_here[e] = api["events"][e][v]
        for o, opt in exact["optional"].items():
            if o in enabled_optional:
                for e, v in opt["events"].items():
                    events_here[e] = api["events"][e][v]
    objects_all = set(api["objects"]) if api else set()

    # ---- event handlers
    for name, places in defined.items():
        if not name.startswith("on_"):
            continue
        f, n, m = places[0]
        if exact and name not in events_here:
            obj = name.split("_")[1] if name.count("_") >= 2 else ""
            if name in all_events:
                add("error", f, n, "%s: на платформе %s такого события нет - обработчик никогда не вызовется" % (name, platform))
            elif obj in objects_all and name not in called:
                near = difflib.get_close_matches(name, events_here, n=2, cutoff=0.6)
                add("error", f, n, "%s: такого события в TiOS нет - обработчик никогда не вызовется, а компилятор промолчит%s"
                    % (name, (" (есть: %s)" % ", ".join(near)) if near else " (события - references/tios-api.md)"))
            continue
        if name in events_here or (not exact and name in all_events):
            if len(places) > 1 and name not in conditional_defs:
                f2, n2, _ = places[1]
                add("error", f2, n2, "%s написан дважды (первый раз: %s:%d) - обработчик события один на проект, объедини код"
                    % (name, os.path.basename(f), n))
            if exact:
                want = events_here[name]
                got = split_args(m.group(4)) if m.group(3) else []
                nwant = len([a for a in want.split(",") if a.strip()])
                if got is not None and len(got) != nwant:
                    add("error", f, n, "%s: у события %d аргумент(ов), а написано %d. Точно: sub %s(%s)"
                        % (name, nwant, len(got), name, want))
    known_events = set(events_here) if exact else all_events

    # ---- callbacks of included libraries
    if libs:
        included = set()
        for f, lines in files:
            for line in lines:
                pass
        text_all = "\n".join(open(f, encoding="utf-8", errors="replace").read() for f, _ in files).lower()
        for lib, v in libs.items():
            if (v["header"].lower() in text_all) or ("\\%s.tbh" % lib in text_all and "%s\\" % lib in text_all):
                included.add(lib)
        for lib in sorted(included):
            for cb in libs[lib]["callbacks"]:
                if cb.get("required") and cb["name"].lower() not in defined:
                    where = tpr["path"] if tpr else files[0][0]
                    add("error", where, 0, "библиотека %s: в проекте нет %s - компоновщик выдаст unresolved address. Добавь: %s ... end %s"
                        % (lib, cb["name"], cb["decl"], cb["kind"]))

    # ---- line by line
    for f, lines in files:
        current = None       # (kind, name) of the procedure we are inside
        for n, line in enumerate(lines, 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            low = line.lower()
            m = proc_re.match(line)
            if m:
                current = (m.group(1).lower(), m.group(2).lower())
                continue
            if re.match(r"^\s*end\s+(sub|function)\b", low):
                current = None
                continue
            if re.match(r"^\s*declare\b", low):
                continue
            code = re.sub(r'""', " S ", line)
            # event handler called like a sub
            for ev in re.findall(r"(?<![\w.])(on_[a-z0-9_]+)", low):
                if ev in known_events and ev in defined:
                    add("error", f, n, "%s - обработчик события, его нельзя вызывать: вынеси код в свою sub и зови её из обоих мест" % ev)
            # direct recursion (subs: any mention; functions: a call with brackets that is not the return assignment)
            if current and current[1] not in known_events:
                me = current[1]
                if current[0] == "sub" and re.search(r"(?<![\w.])%s(?!\w)" % re.escape(me), low):
                    add("error", f, n, "%s вызывает сама себя: рекурсии в Tibbo BASIC нет - перепиши циклом" % me)
                elif current[0] == "function" and re.search(r"(?<![\w.])%s\s*\(" % re.escape(me), re.sub(r"^\s*%s\s*\([^)]*\)\s*=" % re.escape(me), "", low)) \
                        and re.search(r"[=(,+\-*/]\s*%s\s*\(" % re.escape(me), low):
                    add("error", f, n, "%s вызывает сама себя: рекурсии в Tibbo BASIC нет - перепиши циклом" % me)
            # string capacity
            for cap in re.findall(r"\bstring\s*\(\s*(\d+)\s*\)", low):
                if int(cap) > 255:
                    add("error", f, n, "string(%s): строка не длиннее 255 символов" % cap)
            # types from other languages
            for ty in re.findall(r"\bas\s+([a-z_]\w*)", low):
                if ty in FOREIGN_TYPES and ty not in own:
                    add("error", f, n, "тип %s: в Tibbo BASIC его нет. Есть: byte, char, word, short, dword, long, real, string, boolean" % ty)
            # statements and operators of other languages
            if re.match(r"^\s*return\b", low) and "return" not in own:
                add("error", f, n, "return: в Tibbo BASIC значение функции присваивают её имени (f = 5), выход - exit function / exit sub")
            if re.search(r"!=|&&|\|\||==", code):
                add("error", f, n, "операторы из C (!= && || ==): в Tibbo BASIC это <> and or =")
            if re.search(r"(\+=|-=|\*=|/=|\+\+|--)", code) and not re.search(r"[=<>(,]\s*--?\s*\d", code):
                if re.search(r"[\w)\]]\s*(\+=|-=|\*=|/=)|\w\s*(\+\+|--)\s*$", code):
                    add("error", f, n, "+= -= ++ --: таких операторов нет, пиши x = x + 1")
            if re.search(r"&(?!\s*[hb][0-9a-f])", low) and re.search(r"[\w\")]\s*&\s*[\w\"(]", line):
                add("error", f, n, "& не склеивает строки: в Tibbo BASIC это + (а &h1F и &b1010 - числа)")
            st = re.match(r"^\s*(?:(?:if\b.*\bthen|else)\s+)?([a-z_]\w*)\s*(\(|\s+\"|\s+[a-z_0-9])", low)
            if st and st.group(1) in FOREIGN_CALLS and st.group(1) not in own:
                add("error", f, n, "%s: в Tibbo BASIC такого нет - %s" % (st.group(1), FOREIGN_CALLS[st.group(1)]))
            else:
                for fn in re.findall(r"(?<![\w.])([a-z_]\w*)\s*\(", low):
                    if fn in FOREIGN_CALLS and fn not in own and fn not in ("format", "replace", "split", "trim", "wait"):
                        add("error", f, n, "%s(): в Tibbo BASIC такого нет - %s" % (fn, FOREIGN_CALLS[fn]))


def lint(paths, platform=None):
    data = json.load(open(DATA, encoding="utf-8"))
    try:
        api = json.load(open(os.path.join(os.path.dirname(DATA), "platform_api.json"), encoding="utf-8"))
    except (OSError, ValueError):
        api = None
    try:
        libs = {k: v for k, v in json.load(open(os.path.join(os.path.dirname(DATA), "libraries.json"), encoding="utf-8"))["libraries"].items()}
    except (OSError, ValueError):
        libs = None
    tpr = find_tpr(paths)
    if not platform and tpr and tpr["platform"]:
        platform = tpr["platform"]
    members = {o: set(v) for o, v in data["objects"].items()}
    internal = {o: set(v) for o, v in data.get("internal", {}).items()}
    constants = set(data["constants"])
    plat_specific = set(data["platform_specific_constants"])
    plat = None
    if platform:
        lookup = {k.lower(): k for k in data["platforms"]}
        if platform.lower() not in lookup:
            raise KeyError(platform)
        platform = lookup[platform.lower()]
        plat = data["platforms"][platform]
        plat_objects = set(plat["objects"])
        plat_consts = set(plat["constants"])

    all_files = collect_files(paths)
    skipped_cond, stray = [], []
    if tpr:
        all_files, skipped_cond, stray = project_files(tpr, all_files)
    src = load_sources(all_files)
    own = user_identifiers(src)
    exact, enabled_optional = None, set()
    if api and platform:
        ex = {k.lower(): k for k in api["platforms"]}
        if platform.lower() in ex:
            exact = api["platforms"][ex[platform.lower()]]
            defs = (tpr or {}).get("defines", "").upper().replace(" ", "")
            for o, opt in exact["optional"].items():
                if tpr is None or opt["define"].upper() in defs:
                    enabled_optional.add(o)   # no .tpr to look into: assume the project switches it on

    def exact_members(o):
        """Members of object o on this platform: {name: kind}, or None if the object is not there."""
        if o in exact["objects"]:
            return api["objects"][o][exact["objects"][o]]
        if o in exact["optional"] and o in enabled_optional:
            return api["objects"][o][exact["optional"][o]["object"]]
        return None
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
        item = {"level": level, "file": f, "line": n, "message": msg}
        if item not in findings:
            findings.append(item)

    raw_keep = {}
    for f in all_files:
        if f.lower().endswith(BASIC_EXT):
            with open(f, encoding="utf-8", errors="replace") as fh:
                raw_keep[f] = [keep_basic(l) for l in fh.read().split("\n")]

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
            maybe_off = any(s[0] is None for s in stack)   # inside #if we cannot evaluate: the branch may be off
            for m in obj_re.finditer(line):
                o, mem = m.group(1).lower(), m.group(2).lower()
                name = "%s.%s" % (o, mem)
                if exact is not None and is_basic:
                    if other_platform or mem in internal.get(o, ()):
                        continue
                    lvl = "warning" if maybe_off else "error"
                    tail = " (строка внутри #if - если эта ветка включена)" if maybe_off else ""
                    mm = exact_members(o)
                    if mm is None:
                        if o in exact["optional"]:
                            add(lvl, f, n, "%s: объект %s на платформе %s выключен. Включи в проекте: строка defines= /d%s в [project] файла .tpr (TIDE: Project Settings → Customize)%s"
                                % (name, o, platform, exact["optional"][o]["define"], tail))
                        elif o in api["objects"]:
                            add(lvl, f, n, "%s: объекта %s нет на платформе %s (platforms.md)%s" % (name, o, platform, tail))
                        continue
                    if mem not in mm:
                        has = sorted(p for p, v in api["platforms"].items() if mem in api["objects"][o][v["objects"][o]]) if any(
                            mem in var for var in api["objects"][o]) else []
                        has = [p for p in has if o in api["platforms"][p]["objects"]]
                        if has:
                            add(lvl, f, n, "%s: на платформе %s этого нет (есть на: %s)%s" % (name, platform, ", ".join(has[:6]) + (" ..." if len(has) > 6 else ""), tail))
                        elif mem in members.get(o, ()):
                            add(lvl, f, n, "%s: на платформе %s этого нет%s" % (name, platform, tail))
                        else:
                            hint = difflib.get_close_matches(mem, mm, n=2, cutoff=0.7)
                            add("error", f, n, "%s: нет в справочнике TiOS%s - проверь tios-api.md" % (name, (" (похоже: %s)" % ", ".join("%s.%s" % (o, h) for h in hint)) if hint else ""))
                        continue
                    kind = mm[mem]
                    rest = raw_keep[f][n - 1][m.end():] if f in raw_keep and n - 1 < len(raw_keep[f]) else ""
                    before = line[:m.start()]
                    if kind.startswith("p") and "w" not in kind.split(":")[0] and re.match(r"\s*=(?!=)", rest) and \
                            re.match(r"^\s*(?:(?:if\b.*\bthen|else)\s+)?$", before, re.I):
                        add("error", f, n, "%s только для чтения: присвоить нельзя (состояние меняют методами, например sock.connect / sock.close)" % name)
                    if kind.startswith("m") and rest.lstrip().startswith("("):
                        got = split_args(rest.lstrip()[1:])
                        if got is not None and len(got) != int(kind[1:]):
                            add("error", f, n, "%s: аргументов должно быть %s, а передано %d (references/tios-api.md)" % (name, kind[1:], len(got)))
                    continue
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
    for f in stray:
        add("warning", f, 0, "файла нет в .tpr - в сборку он не попадёт (добавь секцию [fileN] или удали файл)")
    if skipped_cond:
        add("warning", tpr["path"], 0, "не проверено файлов с условием включения (condition= в .tpr): %d" % len(skipped_cond))
    basic_checks(all_files, exact, api, enabled_optional, platform, tpr, libs, add)
    if tpr:   # the project file itself (same checks as tibbo_build.py runs before a build)
        try:
            sys.path.insert(0, HERE)
            import tibbo_build
            from pathlib import Path
            for m in tibbo_build.preflight(Path(tpr["path"])):
                add("error", tpr["path"], 0, m["message"])
        except Exception:
            pass
    findings.sort(key=lambda x: (x["file"], x["line"]))
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
