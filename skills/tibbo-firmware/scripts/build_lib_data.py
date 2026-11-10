#!/usr/bin/env python3
"""Build data/libraries.json for tibbo_new.py from the libraries bundled with TIDE.

Source: a clone of github.com/tibbotech/platforms (folder Platforms/src/<version>/<lib>/trunk/*.tbh).
For every library it records its files, every callback_* the library declares and expects the application to
implement (exact declaration), and its *_proc_* hooks with the TiOS event each one must be called from.

Usage: python3 scripts/build_lib_data.py --platforms-repo PATH [--ver 2_01_05]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# *_proc_* hook suffix -> (TiOS event, the call to put into the handler; {lib} = hook name)
HOOK_EVENTS = [
    (r"_proc_timer$", "on_sys_timer", "{h}()"),
    (r"^gprs_proc_ser_data$", "on_ser_data_arrival", "{h}()"),
    (r"_proc_(sock_)?data$", "on_sock_data_arrival", "{h}()"),
    (r"_proc_data_sent$", "on_sock_data_sent", "{h}()"),
    (r"^sntp_proc_sock_event$", "on_sock_event", "{h}(newstatesimple)"),
    (r"_proc_sock_event$", "on_sock_event", "{h}(newstate, newstatesimple)"),
    (r"^mqtt_sock_event$", "on_sock_event", "{h}(newstate, newstatesimple)"),
    (r"^wln_proc_event$", "on_wln_event", "{h}(wln_event)"),
    (r"^wln_proc_task_complete$", "on_wln_task_complete", "{h}(completed_task)"),
]

# What the generator must know and no header says. Checked by compiling (tests/run.sh, "new project" matrix).
MANUAL = {
    "sock": {"title": "раздаёт сокеты библиотекам и программе (sock_get)"},
    "dhcp": {"needs": ["sock"], "needs_wifi": ["wln"], "title": "получение IP по DHCP"},
    "wln": {"needs": ["sock"], "objects": ["wln"], "title": "Wi-Fi: поиск сети, подключение, WPA2"},
    "dns": {"needs": ["sock"], "title": "имя сайта -> IP"},
    "sntp": {"needs": ["sock"], "title": "время из интернета"},
    "mqtt": {"needs": ["sock", "dns"], "title": "клиент MQTT"},
    "time": {"title": "дата и время: преобразования"},
    "filenum": {"objects": ["fd"], "title": "раздаёт номера файлов флеш-диска (fd)"},
    "settings": {"title": "настройки в EEPROM/флеш по описанию settings.txt"},
    "tables": {"needs": ["filenum", "time"], "objects": ["fd"], "title": "таблицы на флеш-диске по описанию tables.txt"},
    "ssi": {"objects": ["ssi"], "title": "раздаёт каналы SSI (SPI/I2C программно)"},
    "super_i2c": {"needs": ["ssi"], "title": "I2C на любых линиях"},
    "super_spi": {"needs": ["ssi"], "title": "SPI на любых линиях"},
}


def main(argv):
    if "--platforms-repo" not in argv:
        print(__doc__)
        return 2
    repo = argv[argv.index("--platforms-repo") + 1]
    ver = argv[argv.index("--ver") + 1] if "--ver" in argv else "2_01_05"
    src = os.path.join(repo, "Platforms", "src", ver)
    if not os.path.isdir(src):
        print("no such folder: %s" % src)
        return 2
    libs = {}
    try:
        previous = json.load(open(os.path.join(ROOT, "data", "libraries.json"), encoding="utf-8"))["libraries"]
    except (OSError, ValueError, KeyError):
        previous = {}
    for name in sorted(os.listdir(src)):
        trunk = os.path.join(src, name, "trunk")
        if not os.path.isdir(trunk):
            continue
        files = sorted(f for f in os.listdir(trunk) if f.lower().endswith((".tbs", ".tbh")))
        if not files:
            continue
        callbacks, hooks = [], []
        for f in files:
            if not f.lower().endswith(".tbh"):
                continue
            text = open(os.path.join(trunk, f), encoding="latin-1").read()
            # A callback declared inside #if exists only for some library settings: the generator and the linter
            # use the ones declared unconditionally (include guards "#ifndef X / #define X" do not count).
            stack = []
            for line in text.splitlines():
                pp = re.match(r"\s*#\s*(if|ifdef|ifndef|else|elif|endif)\b(.*)", line, re.I)
                if pp:
                    kw = pp.group(1).lower()
                    if kw in ("if", "ifdef", "ifndef"):
                        stack.append(pp.group(2).strip())
                    elif kw == "endif" and stack:
                        stack.pop()
                    continue
                m = re.match(r"[ \t]*declare[ \t]+((sub|function)[ \t]+(\w+)[ \t]*\(([^)\r\n]*)\)([ \t]+as[ \t]+[\w()]+)?)", line, re.I)
                if not m:
                    continue
                decl, kind, fn = re.sub(r"\s+", " ", m.group(1).strip()), m.group(2).lower(), m.group(3)
                if fn.lower().startswith("callback_"):
                    cb = {"name": fn, "decl": decl, "kind": kind}
                    if stack:
                        cb["when"] = " and ".join(stack)
                    callbacks.append(cb)
                elif "_proc_" in fn.lower() or fn.lower() == "mqtt_sock_event":
                    for pat, event, call in HOOK_EVENTS:
                        if re.search(pat, fn.lower()):
                            hooks.append({"name": fn, "event": event, "call": call.format(h=fn)})
                            break
        entry = {"files": ["%s\\trunk\\%s" % (name, f) for f in files], "header": "%s\\trunk\\%s.tbh" % (name, name),
                 "callbacks": callbacks, "hooks": hooks}
        entry.update(MANUAL.get(name, {}))
        prev = previous.get(name, {})      # results of tools/verify_libraries.py survive a rebuild
        for k in ("broken_on", "extra_defines"):
            if k in prev:
                entry[k] = prev[k]
        req = {c["name"] for c in prev.get("callbacks", []) if c.get("required")}
        for c in entry["callbacks"]:
            if c["name"] in req:
                c["required"] = True
        entry["supported"] = name in MANUAL
        libs[name] = entry
    out = os.path.join(ROOT, "data", "libraries.json")
    json.dump({"_source": "github.com/tibbotech/platforms Platforms/src/%s (libraries bundled with TIDE)" % ver,
               "src_lib_ver": ver, "libraries": libs}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("%s: %d libraries, %d supported by tibbo_new.py" % (out, len(libs), sum(1 for v in libs.values() if v["supported"])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
