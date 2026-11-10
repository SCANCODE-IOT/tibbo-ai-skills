#!/usr/bin/env python3
"""Dev tool: check tibbo_new.py against Tibbo's compiler and record the truth in data/libraries.json.

For every library the generator supports:
  1. which callback_* the linker really needs (start with none, add each "unresolved address" until it links);
  2. on which platforms a project with this library compiles; known library defects get a workaround define,
     the rest are recorded in "broken_on" and the generator refuses them with the compiler's message.
Usage: python3 tools/verify_libraries.py <tibbo-basic folder>     (needs Node.js; ~5 minutes)
"""
import json, os, re, shutil, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills", "tibbo-firmware")
NODE = os.path.join(sys.argv[1], "server", "out", "compiler", "compile-project.js")
DATA = os.path.join(SK, "data", "libraries.json")
REF = "TPP3W(G2)"
WORKAROUNDS = {"mqtt": ["#define MQTT_DEBUG_PRINT 1        'mqtt 2_01_05 does not compile on this platform without it"]}


def build(lib, platform, callbacks=None):
    d = tempfile.mkdtemp(prefix="tbnew-")
    env = dict(os.environ)
    if callbacks is not None:
        env["TIBBO_NEW_CALLBACKS"] = ",".join(callbacks)
    g = subprocess.run([sys.executable, os.path.join(SK, "scripts", "tibbo_new.py"), os.path.join(d, "p"), "--platform", platform,
                        "--name", "app"] + (["--libs", lib] if lib else []), capture_output=True, text=True, env=env)
    if g.returncode:
        shutil.rmtree(d); return "refused", g.stdout.strip()
    c = subprocess.run(["node", NODE, os.path.join(d, "p"), "-o", os.path.join(d, "x.tpc")], capture_output=True, text=True)
    shutil.rmtree(d)
    if c.returncode == 0:
        return "ok", ""
    err = [l for l in (c.stdout + c.stderr).splitlines() if " error" in l]
    return "fail", (err[0].split("error:")[-1].strip() if err else "compiler failed")


def save(d):
    json.dump(d, open(DATA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


d = json.load(open(DATA, encoding="utf-8"))
libs = d["libraries"]
api = json.load(open(os.path.join(SK, "data", "platform_api.json"), encoding="utf-8"))
for v in libs.values():
    v.pop("broken_on", None); v.pop("extra_defines", None)
    for c in v["callbacks"]:
        c.pop("required", None)
save(d)
# 1. callbacks the linker needs
for name, v in libs.items():
    if not v.get("supported"):
        continue
    need = []
    for _ in range(40):
        st, msg = build(name, REF, need)
        m = re.search(r"unresolved address '\?F:(\w+)'", msg)
        if st != "fail" or not m:
            break
        need.append(m.group(1).lower())
    for other in libs.values():
        for c in other["callbacks"]:
            if c["name"].lower() in need:
                c["required"] = True
    save(d)
    print("%-10s callbacks needed: %d of %d  -> %s %s" % (name, len([c for c in v["callbacks"] if c.get("required")]), len(v["callbacks"]), st, msg[:90]))
# 2. every platform
bad = 0
for name, v in libs.items():
    if not v.get("supported"):
        continue
    for p in sorted(api["platforms"]):
        st, msg = build(name, p)
        if st == "fail" and name in WORKAROUNDS:
            v.setdefault("extra_defines", {})[p] = WORKAROUNDS[name]; save(d)
            st, msg = build(name, p)
            if st != "ok":
                v["extra_defines"].pop(p)
        if st == "fail":
            v.setdefault("broken_on", {})[p] = msg; save(d); bad += 1
            print("  BROKEN %-10s %-12s %s" % (name, p, msg[:110]))
save(d)
# 3. everything together and nothing at all
allok = 0
for p in sorted(api["platforms"]):
    for libset in ("", ",".join(n for n, v in libs.items() if v.get("supported") and p not in v.get("broken_on", {}))):
        st, msg = build(libset, p)
        if st == "refused" and libset:      # drop what this platform cannot have, keep the rest
            keep = [n for n in libset.split(",") if build(n, p)[0] == "ok"]
            st, msg = build(",".join(keep), p)
        allok += st == "ok"
        if st != "ok":
            print("  SET FAILS %-12s [%s] %s %s" % (p, libset[:40], st, msg[:120])); bad += 1
print("platforms: %d, full-set and empty projects compiled: %d, problems: %d" % (len(api["platforms"]), allok, bad))
sys.exit(1 if bad else 0)
