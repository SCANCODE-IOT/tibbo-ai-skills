#!/usr/bin/env python3
"""Is the skill's data still what Tibbo publishes? Run before every release.

Compares with a fresh clone of github.com/tibbotech/platforms:
  - references/platforms.md: every platform row (ROM, RAM, TiOS file) against <platform>.tp and firmware/;
  - platforms Tibbo has and the skill does not;
  - data/platform_api.json and data/libraries.json: platform list and library version.
Usage: python3 tools/check_freshness.py --platforms-repo PATH     exit code 1 if something is stale.
The AppBlocks registry is checked separately (skills/appblocks/scripts/extract_registry.js in the editor).
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills", "tibbo-firmware")
repo = sys.argv[sys.argv.index("--platforms-repo") + 1] if "--platforms-repo" in sys.argv else None
if not repo:
    sys.exit(__doc__)
P = os.path.join(repo, "Platforms")
md = open(os.path.join(SK, "references", "platforms.md"), encoding="utf-8").read()
rows = {m.group(1): m for m in re.finditer(r"(?m)^\| ([A-Za-z0-9_]+(?:\([A-Za-z0-9]+\))?) \| [^|]+ \| (\d+) \| (\d+) \| (\d+) \| [^|]* \| ([^|]*?) \|$", md)}
stale = []
upstream = sorted(d for d in os.listdir(P) if os.path.isfile(os.path.join(P, d, d + ".tp")))
for p in upstream:
    tp = open(os.path.join(P, p, p + ".tp"), encoding="latin-1").read()
    get = lambda k: (re.search(r"(?mi)^%s\s*=\s*(\S+)" % k, tp) or [None, None])[1]
    fw = sorted(f for f in os.listdir(os.path.join(P, p, "firmware"))) if os.path.isdir(os.path.join(P, p, "firmware")) else []
    if p not in rows:
        stale.append("%s: platform is not in platforms.md" % p)
        continue
    m = rows[p]
    if get("rom") and m.group(3) != get("rom"):
        stale.append("%s: ROM %s in platforms.md, %s upstream" % (p, m.group(3), get("rom")))
    if get("ram") and m.group(4) != get("ram"):
        stale.append("%s: RAM %s in platforms.md, %s upstream" % (p, m.group(4), get("ram")))
    ours = sorted(re.findall(r"tios-[^\s,;]+?\.bin", m.group(5)))
    if fw and ours != [f for f in fw if f.endswith(".bin")]:
        stale.append("%s: TiOS file %s in platforms.md, %s upstream (%s)" % (p, ", ".join(ours) or "-", ", ".join(fw), get("version")))
api = json.load(open(os.path.join(SK, "data", "platform_api.json"), encoding="utf-8"))
known = set(api["platforms"]) | set(api.get("not_buildable", {}))
for p in upstream:
    if p not in known:
        stale.append("%s: not in data/platform_api.json (run tools/dump_platform_api.js)" % p)
libs = json.load(open(os.path.join(SK, "data", "libraries.json"), encoding="utf-8"))
vers = sorted(v for v in os.listdir(os.path.join(P, "src")) if re.fullmatch(r"\d+(_\d+)+", v))
if vers and libs["src_lib_ver"] != vers[-1]:
    stale.append("libraries: data is for %s, upstream has %s" % (libs["src_lib_ver"], vers[-1]))
for s in stale:
    print("STALE " + s)
print("platforms upstream: %d, stale items: %d" % (len(upstream), len(stale)))
sys.exit(1 if stale else 0)
