#!/usr/bin/env python3
"""Build data/platform_api.json - the exact TiOS API of every platform - from a dump made by Tibbo's own compiler.

The dump (tools/dump_platform_api.js in the repository) asks the compiler what it knows after parsing a platform's
headers: objects, properties (readable/writable, type), methods (number of arguments), events (exact arguments),
enums and their constants, built-in functions, and the objects a project must switch on with "defines=" in the .tpr.
Identical definitions are stored once ("variants") and platforms point to them, so the file stays small.

Usage: python3 scripts/build_platform_api.py <dump.json>
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def variant(table, key, value):
    """Index of `value` among the variants of `key` (added if new)."""
    lst = table.setdefault(key, [])
    for i, v in enumerate(lst):
        if v == value:
            return i
    lst.append(value)
    return len(lst) - 1


def pack_object(o):
    members = {}
    for n, p in o["props"].items():
        members[n.lower()] = "p" + ("r" if p["r"] else "") + ("w" if p["w"] else "") + ":" + (p["t"] or "")
    for n, argc in o["methods"].items():
        members[n.lower()] = "m%d" % argc
    return members


def pack_event(args):
    return ", ".join("%s as %s" % (a["n"], a["t"]) for a in args)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    dump = json.load(open(argv[0], encoding="utf-8"))
    objects, events, enums, platforms, broken = {}, {}, {}, {}, {}
    functions = {}
    for p, v in dump.items():
        if "error" in v:
            broken[p] = v["error"]
            continue
        entry = {"objects": {}, "events": {}, "enums": {}, "optional": {}}
        for name, o in v["objects"].items():
            if name.startswith("!"):
                continue
            entry["objects"][name.lower()] = variant(objects, name.lower(), pack_object(o))
        for name, args in v["events"].items():
            entry["events"][name.lower()] = variant(events, name.lower(), pack_event(args))
        for name, members in v["enums"].items():
            entry["enums"][name.lower()] = variant(enums, name.lower(), members)
        for name, argc in v["functions"].items():
            if not name.startswith("!"):
                functions.setdefault(name.lower(), argc)
        for name, o in v.get("optional", {}).items():
            entry["optional"][name.lower()] = {
                "define": o["define"], "object": variant(objects, name.lower(), pack_object(o)),
                "events": {e.lower(): variant(events, e.lower(), pack_event(a)) for e, a in o["events"].items()},
                "enums": {e.lower(): variant(enums, e.lower(), m) for e, m in o["enums"].items()}}
        platforms[p] = entry
    out = {"_source": "Tibbo BASIC compiler (github.com/tibbotech/tibbo-basic, feature/compiler) on github.com/tibbotech/platforms",
           "objects": objects, "events": events, "enums": enums, "functions": functions, "platforms": platforms,
           "not_buildable": broken}
    path = os.path.join(ROOT, "data", "platform_api.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    print("%s: %d platforms, %d objects (%d variants), %d events, %d enums (%d variants), %d KB; not buildable: %s" % (
        path, len(platforms), len(objects), sum(len(v) for v in objects.values()), len(events), len(enums),
        sum(len(v) for v in enums.values()), os.path.getsize(path) // 1024, ", ".join(broken) or "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
