#!/usr/bin/env python3
"""Dev tool: (re)create skills/tibbo-firmware/recipes/* from the sources in tools/recipes_src/.

Every recipe = a project made by tibbo_new.py (so the .tpr, libraries, hooks and callbacks are right) plus the
recipe's own main.tbs, extra files and callback bodies. Sources: tools/recipes_src/<name>/recipe.json + files.
After building, tests/run.sh lints every recipe and, when Tibbo's compiler is installed, compiles it.

Usage: python3 tools/build_recipes.py
"""
import json, os, re, shutil, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills", "tibbo-firmware")
SRC = os.path.join(ROOT, "tools", "recipes_src")
OUT = os.path.join(SK, "recipes")


def crlf(text):
    return text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8")


shutil.rmtree(OUT, ignore_errors=True)
index = []
for name in sorted(os.listdir(SRC)):
    d = os.path.join(SRC, name)
    meta = json.load(open(os.path.join(d, "recipe.json"), encoding="utf-8"))
    dst = os.path.join(OUT, name)
    cmd = [sys.executable, os.path.join(SK, "scripts", "tibbo_new.py"), dst, "--platform", meta["platform"], "--name", "app"]
    if meta.get("libs"):
        cmd += ["--libs", meta["libs"]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("%s: tibbo_new.py refused: %s" % (name, r.stdout))
    # own files replace generated ones (main.tbs always; others when present)
    extra = []
    for fn in sorted(os.listdir(d)):
        if fn in ("recipe.json", "callbacks.tbs", "global_add.tbh", "init_add.tbs"):
            continue
        data = open(os.path.join(d, fn), "rb").read()
        open(os.path.join(dst, fn), "wb").write(crlf(data.decode("utf-8")) if fn.lower().endswith((".tbs", ".tbh", ".html", ".txt")) else data)
        if fn not in ("main.tbs", "settings.txt", "tables.txt"):
            extra.append(fn)
    # extra lines for global.tbh (defines go before the includes, declarations after)
    g = open(os.path.join(dst, "global.tbh"), encoding="utf-8", newline="").read()
    for line in meta.get("defines", []):
        key = line.split()[1]
        if re.search(r"(?m)^#define %s\b.*$" % re.escape(key), g):
            g = re.sub(r"(?m)^#define %s\b.*$" % re.escape(key), line, g)
        else:
            g = g.replace("\r\n\r\n'INCLUDES", "\r\n" + line + "\r\n\r\n'INCLUDES")
    if meta.get("declares"):
        g = g.rstrip("\r\n") + "\r\n" + "\r\n".join(meta["declares"]) + "\r\n"
    open(os.path.join(dst, "global.tbh"), "wb").write(g.encode("utf-8"))
    # callback bodies
    cbfile = os.path.join(d, "callbacks.tbs")
    if os.path.exists(cbfile):
        bodies = {}
        cur = None
        for line in open(cbfile, encoding="utf-8").read().splitlines():
            m = re.match(r"^@(\w+)\s*$", line)
            if m:
                cur = m.group(1).lower(); bodies[cur] = []
            elif cur:
                bodies[cur].append(line)
        dev = open(os.path.join(dst, "device.tbs"), encoding="utf-8", newline="").read().split("\r\n")
        out, i = [], 0
        while i < len(dev):
            m = re.match(r"^(sub|function)\s+(\w+)", dev[i], re.I)
            if m and m.group(2).lower() in bodies:
                out.append(dev[i])
                j = i + 1
                while not re.match(r"^end (sub|function)", dev[j], re.I):
                    j += 1
                out += bodies.pop(m.group(2).lower())
                i = j
                continue
            out.append(dev[i]); i += 1
        if bodies:
            sys.exit("%s: no such callbacks in device.tbs: %s" % (name, ", ".join(bodies)))
        open(os.path.join(dst, "device.tbs"), "wb").write("\r\n".join(out).encode("utf-8"))
    # extra files into the .tpr
    if extra or meta.get("project"):
        t = open(os.path.join(dst, "app.tpr"), encoding="utf-8", newline="").read()
        for k, v in meta.get("project", {}).items():
            t = re.sub(r"(?m)^%s=.*$" % k, "%s=%s" % (k, v), t) if re.search(r"(?m)^%s=" % k, t) else t.replace("[project]\r\n", "[project]\r\n%s=%s\r\n" % (k, v))
        n = len(re.findall(r"(?m)^\[file\d+\]", t))
        types = {".tbs": "basic", ".tbh": "header", ".html": "html", ".txt": "text"}
        for fn in extra:
            n += 1
            t = t.rstrip("\r\n") + "\r\n\r\n[file%d]\r\npath=%s\r\ntype=%s\r\nlocation=project\r\n" % (n, fn, types.get(os.path.splitext(fn)[1].lower(), "binary"))
        open(os.path.join(dst, "app.tpr"), "wb").write(t.encode("utf-8"))
    json.dump({k: meta[k] for k in ("title", "platform", "also", "tibbits", "libs") if k in meta},
              open(os.path.join(dst, "recipe.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    index.append((name, meta))
print("recipes built: %d -> %s" % (len(index), OUT))
