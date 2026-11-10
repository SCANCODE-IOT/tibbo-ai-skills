#!/usr/bin/env python3
"""Lint every recipe and compile it with Tibbo's compiler on its platform and on every platform in "also".
Recipes in Tibbo C are compiled by Tibbo's cloud compiler (the Node.js compiler builds Tibbo BASIC only): add --cloud,
the recipe files are then sent to api.appblocks.io. Without --cloud they are only linted.
Usage: python3 tools/check_recipes.py <tibbo-basic folder> [--cloud] [name part ...]     exit code 1 if anything fails."""
import json, os, re, shutil, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills", "tibbo-firmware")
R = os.environ.get("RECIPES_OUT") or os.path.join(SK, "recipes")
env = dict(os.environ, TIBBO_BASIC_HOME=sys.argv[1], TIDE_DIR="/nonexistent")
cloud = "--cloud" in sys.argv
only = [a for a in sys.argv[2:] if not a.startswith("--")]
ok = bad = 0
for name in sorted(os.listdir(R)):
    d = os.path.join(R, name)
    if not os.path.isdir(d) or (only and not any(o in name for o in only)):
        continue
    meta = json.load(open(os.path.join(d, "recipe.json"), encoding="utf-8"))
    l = subprocess.run([sys.executable, os.path.join(SK, "scripts", "tibbo_lint.py"), d, "--json"], capture_output=True, text=True)
    for x in json.loads(l.stdout)["findings"]:
        print("  LINT", name, os.path.basename(x["file"]), x["line"], x["level"], x["message"][:150]); bad += 1
    for p in [meta["platform"]] + meta.get("also", []):
        t = os.path.join(tempfile.mkdtemp(prefix="rc-"), "p")
        shutil.copytree(d, t)
        if p != meta["platform"]:   # the same sources on another board
            tpr = open(os.path.join(t, "app.tpr"), newline="").read()
            open(os.path.join(t, "app.tpr"), "w", newline="").write(re.sub(r"(?m)^platform=.*$", "platform=" + p, tpr))
        if meta.get("compiler") == "cloud" and not cloud:
            shutil.rmtree(os.path.dirname(t), ignore_errors=True)
            print("  skip (Tibbo C, needs --cloud)", name, p)
            continue
        how = ["--cloud", "--cloud-ok"] if meta.get("compiler") == "cloud" else ["--node"]
        b = subprocess.run([sys.executable, os.path.join(SK, "scripts", "tibbo_build.py"), t, *how, "--json"],
                           capture_output=True, text=True, env={k: v for k, v in env.items() if k != "APPBLOCKS_API_KEY"})
        shutil.rmtree(os.path.dirname(t), ignore_errors=True)
        try:
            j = json.loads(b.stdout)
        except ValueError:
            print("  BUILD?", name, p, b.stdout[-200:]); bad += 1; continue
        if j["ok"]:
            ok += 1
        else:
            bad += 1
            e = j["errors"][0]
            print("  FAIL", name, p, e.get("file"), e.get("line"), e["message"][:160])
print("recipe builds OK: %d, problems: %d" % (ok, bad))
sys.exit(1 if bad else 0)
