#!/usr/bin/env python3
"""Build data/tios_api.json for tibbo_lint.py from the skill's own references.

Sources (shipped with the skill, so no network is needed):
  references/tios-api.md  - objects, members, enums and syscalls (extracted from tibbotech/platforms *.tph)
  references/platforms.md - which object headers every platform includes and its platform-specific PL_* constants

Optional: --platforms-repo <path to a clone of github.com/tibbotech/platforms> also collects internal members
(declared with "!" in *.tph and left out of tios-api.md) and exact PL_* constants; --libraries-repo <clone of
github.com/tibbotech/libraries> adds PL_* names the libraries declare. Both are kept in the JSON between rebuilds.

Usage: python3 scripts/build_lint_data.py [--platforms-repo PATH] [--libraries-repo PATH]   (run after the references are updated)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OBJECTS = ["sys", "io", "net", "sock", "ser", "romfile", "stor", "fd", "wln", "bt", "tls", "i2c", "ssi", "adc",
           "pwm", "kp", "lcd", "beep", "pat", "button", "rtc", "ppp", "pppoe", "tpram", "lsock", "lfd", "sled"]

# object header (as listed in platforms.md "Object headers included") -> objects it brings
GEN = ["button", "pat", "ppp", "romfile", "ser", "sock", "stor", "sys", "io"]
HEADER_OBJECTS = {
    "sys-1xxx": ["sys"], "sys-2xxx": ["sys"], "sys-linux": ["sys"],
    "io-1xxx": ["io"], "io-2xxx": ["io"], "io-5xx": ["io"],
}


def header_to_objects(h):
    h = h.strip().lower()
    if h == "gen" or h.startswith("gen-"):
        return GEN
    if h in HEADER_OBJECTS:
        return HEADER_OBJECTS[h]
    return [h] if h in OBJECTS else []


def main():
    api = open(os.path.join(ROOT, "references", "tios-api.md"), encoding="utf-8").read()
    plat = open(os.path.join(ROOT, "references", "platforms.md"), encoding="utf-8").read()

    obj_re = r"(?<![\w.])(%s)\.([a-z_][a-z0-9_]*)" % "|".join(OBJECTS)
    members = {o: set() for o in OBJECTS}
    for o, m in re.findall(obj_re, api, re.I):
        if m.lower() != "tph":  # "adc.tph" etc. are header file names, not members
            members[o.lower()].add(m.lower())

    constants = set(c.upper() for c in re.findall(r"\bPL_[A-Z0-9_]+\b", api + plat, re.I))

    # syscalls / functions: "- `name(" at line start in the syscalls section
    functions = set()
    sec = re.search(r"^## syscalls\.tph(.*?)^## ", api, re.S | re.M)
    if sec:
        functions.update(f.lower() for f in re.findall(r"^- `([a-z_][a-z0-9_]*)\s*\(", sec.group(1), re.M))

    platforms = {}
    for m in re.finditer(r"^## (\S+) — .*?(?=^## |\Z)", plat, re.S | re.M):
        name, body = m.group(1), m.group(0)
        hdr = re.search(r"Object headers included:\s*(.*)", body)
        if not hdr:
            continue
        objs = set()
        for h in hdr.group(1).split(","):
            objs.update(header_to_objects(h))
        consts = sorted(set(c.upper() for c in re.findall(r"\bPL_[A-Z0-9_]+\b", body)))
        pid = re.search(r"PLATFORM_ID:\s*(\d+)", body)
        platforms[name] = {"objects": sorted(objs), "constants": consts,
                           "symbol": re.sub(r"[()]", "", name).upper(), "id": int(pid.group(1)) if pid else None}

    # platform-specific = listed under some platform but not part of the generic object API
    generic = set(c.upper() for c in re.findall(r"\bPL_[A-Z0-9_]+\b", api, re.I))
    platform_specific = set()
    for p in platforms.values():
        platform_specific.update(c for c in p["constants"] if c not in generic)

    # enum type names (used in declarations: "as pl_sock_state")
    enum_types = set(t.upper() for t in re.findall(r"`(pl_\w+)`", api + plat, re.I))

    path = os.path.join(ROOT, "data", "tios_api.json")
    internal, tph_constants = {}, []
    if os.path.exists(path):
        old = json.load(open(path, encoding="utf-8"))
        internal, tph_constants = old.get("internal", {}), old.get("tph_constants", [])
    if "--platforms-repo" in sys.argv:
        repo = sys.argv[sys.argv.index("--platforms-repo") + 1]
        internal, tph = {}, set()
        decl = re.compile(r"^\s*(?:property|syscall\([^)]*\))\s+!(%s)\.([a-z_][a-z0-9_]*)" % "|".join(OBJECTS), re.I | re.M)
        for dirpath, _, files in os.walk(repo):
            if os.sep + "src" + os.sep in dirpath + os.sep:
                continue  # library copies, not platform declarations
            for fn in files:
                if fn.lower().endswith(".tph"):
                    text = open(os.path.join(dirpath, fn), encoding="latin-1").read()
                    for o, m in decl.findall(text):
                        if m.lower() not in members[o.lower()]:
                            internal.setdefault(o.lower(), set()).add(m.lower())
                    tph.update(c.upper() for c in re.findall(r"^\s*(PL_\w+)\s*(?:=|,|'|$)", text, re.M | re.I))
                    tph.update(c.upper() for c in re.findall(r"^\s*enum\s+(pl_\w+)", text, re.M | re.I))
        internal = {o: sorted(v) for o, v in internal.items()}
        tph_constants = sorted(tph - constants)
    library_names = old.get("library_names", []) if os.path.exists(path) else []
    if "--libraries-repo" in sys.argv:
        # PL_* names that Tibbo libraries declare themselves (enum types and members, defines)
        repo = sys.argv[sys.argv.index("--libraries-repo") + 1]
        lib = set()
        for dirpath, _, files in os.walk(repo):
            for fn in files:
                if fn.lower().endswith((".tbh", ".tbs")):
                    text = open(os.path.join(dirpath, fn), encoding="latin-1").read()
                    lib.update(n.upper() for n in re.findall(r"^\s*(?:enum|type|#\s*define)\s+(PL_\w+)", text, re.M | re.I))
                    for body in re.findall(r"^\s*enum\s+\w+(.*?)^\s*end\s+enum", text, re.I | re.S | re.M):
                        lib.update(n.upper() for n in re.findall(r"^\s*(PL_\w+)", body, re.M | re.I))
        library_names = sorted(lib - constants - set(tph_constants))
    constants |= enum_types | set(tph_constants) | set(library_names)

    out = {
        "internal": internal,
        "tph_constants": tph_constants,
        "library_names": library_names,
        "_source": "Built by scripts/build_lint_data.py from references/tios-api.md and references/platforms.md",
        "objects": {o: sorted(v) for o, v in members.items() if v},
        "constants": sorted(constants),
        "platform_specific_constants": sorted(platform_specific),
        "functions": sorted(functions),
        "platforms": platforms,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    n = sum(len(v) for v in out["objects"].values())
    print("%s: %d objects, %d members, %d constants, %d platforms" % (
        os.path.relpath(path, ROOT), len(out["objects"]), n, len(out["constants"]), len(platforms)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:      # the reader (head, grep -q) closed the pipe: not an error
        try:
            sys.stdout.close()
        except OSError:
            pass
        os._exit(0)
