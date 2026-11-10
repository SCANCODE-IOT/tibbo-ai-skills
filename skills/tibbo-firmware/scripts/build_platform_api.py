#!/usr/bin/env python3
"""Build data/platform_api.json - the exact TiOS API of every platform - from a dump made by Tibbo's own compiler.

The dump (tools/dump_platform_api.js in the repository) asks the compiler what it knows after parsing a platform's
headers: objects, properties (readable/writable, type), methods (number of arguments), events (exact arguments),
enums and their constants, built-in functions, and the objects a project must switch on with "defines=" in the .tpr.
Identical definitions are stored once ("variants") and platforms point to them, so the file stays small.

Usage: python3 scripts/build_platform_api.py <dump.json> [<dump of the compiler's own platform files>]

The second dump is made with the platform files that come with the compiler (older than Tibbo's latest). Names that
exist only in the latest files go to "newer_only": the default compiler, the cloud compiler and most TIDE installations
do not know them, and the linter warns about them.
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
    newer = {}
    if len(argv) > 1:
        def names(pl):
            out = set()
            for o, v in (pl.get("objects") or {}).items():
                for grp in ("props", "methods"):
                    out.update("%s.%s" % (o.lower(), m.lower()) for m in (v.get(grp) or {}))
            for vals in (pl.get("enums") or {}).values():
                out.update(str(c).upper() for c in vals)
            out.update(e.lower() for e in (pl.get("events") or {}))
            return out
        older = json.load(open(argv[1], encoding="utf-8"))
        for p in dump:
            if p in older and "objects" in dump[p] and "objects" in older[p]:
                for n in names(dump[p]) - names(older[p]):
                    newer.setdefault(n, []).append(p)
    else:       # keep what the previous build found
        try:
            newer = json.load(open(os.path.join(ROOT, "data", "platform_api.json"), encoding="utf-8")).get("newer_only", {})
        except (OSError, ValueError):
            pass
    out = {"_source": "Tibbo BASIC compiler (github.com/tibbotech/tibbo-basic, feature/compiler) on github.com/tibbotech/platforms",
           "objects": objects, "events": events, "enums": enums, "functions": functions, "platforms": platforms,
           "not_buildable": broken, "newer_only": {k: sorted(v) for k, v in sorted(newer.items())}}
    path = os.path.join(ROOT, "data", "platform_api.json")
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    print("%s: %d platforms, %d objects (%d variants), %d events, %d enums (%d variants), %d KB; not buildable: %s" % (
        path, len(platforms), len(objects), sum(len(v) for v in objects.values()), len(events), len(enums),
        sum(len(v) for v in enums.values()), os.path.getsize(path) // 1024, ", ".join(broken) or "-"))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except BrokenPipeError:      # the reader (head, grep -q) closed the pipe: not an error
        try:
            sys.stdout.close()
        except OSError:
            pass
        os._exit(0)
