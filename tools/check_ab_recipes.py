#!/usr/bin/env python3
"""Check every AppBlocks recipe: ab_tool.py check (0 errors), Tibbo's code generator, Tibbo's compiler.

The generator and the compiler are Tibbo's services (api.appblocks.io): the recipe projects are sent there. No API key
is needed and nothing is stored in an account. Usage: python3 tools/check_ab_recipes.py [--offline] [name part ...]
exit code 1 if anything fails."""
import json, os, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AB = os.path.join(ROOT, "skills", "appblocks")
R = os.path.join(AB, "recipes")
offline = "--offline" in sys.argv
only = [a for a in sys.argv[1:] if not a.startswith("--")]
env = {k: v for k, v in os.environ.items() if k != "APPBLOCKS_API_KEY"}
run = lambda *a: subprocess.run([sys.executable, *a], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
bad = 0
for it in json.load(open(os.path.join(R, "index.json"), encoding="utf-8"))["recipes"]:
    if only and not any(o in it["file"] for o in only):
        continue
    f = os.path.join(R, it["file"])
    c = run(os.path.join(AB, "scripts", "ab_tool.py"), "check", f)
    res = ["check " + ("OK" if c.returncode == 0 else "FAIL")]
    warn = [l for l in c.stdout.splitlines() if "[ВНИМАНИЕ]" in l or "[ОШИБКА]" in l]
    ok = c.returncode == 0
    cfg = os.path.join(tempfile.mkdtemp(prefix="abr-"), "cfg.json")
    run(os.path.join(AB, "scripts", "ab_tool.py"), "tps", f, "--vin", "12", "--out", cfg)
    h = run(os.path.join(ROOT, "skills", "tibbo-firmware", "scripts", "tps_check.py"), "check", cfg)
    res.append("board " + ("OK" if h.returncode == 0 else "FAIL"))
    warn += [l for l in h.stdout.splitlines() if "[ОШИБКА]" in l]
    ok = ok and h.returncode == 0
    if not offline:
        out = tempfile.mkdtemp(prefix="abr-")
        g = run(os.path.join(AB, "scripts", "ab_api.py"), "code", f, "--outdir", out)
        gen = g.returncode == 0 and os.path.exists(os.path.join(out, "main.tbs"))
        res.append("code " + ("OK" if gen else "FAIL"))
        for attempt in (1, 2):          # the build service sometimes fails without any compiler message: try once more
            b = run(os.path.join(AB, "scripts", "ab_api.py"), "build", f, "--release", "--out", os.path.join(out, "fw"))
            if b.returncode == 0 or "error" in b.stdout:
                break
        res.append("build " + (b.stdout.strip().splitlines()[-1] if b.stdout.strip() else "FAIL"))
        ok = ok and gen and b.returncode == 0
        if not gen:
            warn.append((g.stdout + g.stderr)[-300:])
        if b.returncode:
            warn += (b.stdout + b.stderr).splitlines()[-6:]
    print("%-4s %-28s %s" % ("ok" if ok else "FAIL", it["file"], " | ".join(res)))
    for w in warn:
        print("       " + w[:230])
    bad += 0 if ok else 1
sys.exit(1 if bad else 0)
