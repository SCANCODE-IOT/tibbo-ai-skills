#!/usr/bin/env python3
"""Create a new TIDE project (Tibbo BASIC) that compiles from the first try.
Создаёт новый проект TIDE, который собирается с первого раза: плата + библиотеки -> .tpr, global.tbh,
main.tbs с обработчиками событий и вызовами библиотек, device.tbs со всеми callback_* библиотек.

Usage:
  python3 scripts/tibbo_new.py <folder> --platform "TPP3W(G2)" [--libs dhcp,settings,sntp] [--name myapp]
                               [--release] [--force]
  python3 scripts/tibbo_new.py --list                 # libraries the generator knows, with what each one is for
  python3 scripts/tibbo_new.py --list-platforms

What it knows that is easy to get wrong:
  - library files go into the .tpr with location = commonlib and need src_lib_ver;
  - libraries depend on each other (dhcp needs sock; on Wi-Fi platforms dhcp also needs wln);
  - every callback_* a library declares must exist in the project, with the exact arguments;
  - every *_proc_* of a library must be called from the right event handler.
Then: write your code in main.tbs and build with  python3 scripts/tibbo_build.py <folder>.
Data: data/libraries.json (scripts/build_lib_data.py), data/tios_api.json. Python 3.9+, standard library only.
Exit codes: 0 - created, 2 - bad input.
"""
import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

EVENT_SIGNATURE = {
    "on_sys_init": "",
    "on_sys_timer": "",
    "on_sock_data_arrival": "",
    "on_sock_data_sent": "",
    "on_sock_event": "newstate as pl_sock_state, newstatesimple as pl_sock_state_simple",
    "on_ser_data_arrival": "",
    "on_wln_event": "wln_event as pl_wln_events",
    "on_wln_task_complete": "completed_task as pl_wln_tasks",
}
EVENT_ORDER = list(EVENT_SIGNATURE)

# #define lines a library needs in global.tbh BEFORE its include (None -> library defaults are fine)
DEFINES = {
    "wln": ["#define WLN_AVAILABLE 1", "#define WLN_WPA 1               'WPA/WPA2 support"],
    "settings": ['#define STG_DESCRIPTOR_FILE "settings.txt"', "#define STG_MAX_NUM_SETTINGS 2", "#define STG_MAX_SETTING_NAME_LEN 2",
                 "#define STG_MAX_SETTING_VALUE_LEN 15"],
    "tables": ['#define TBL_DESCRIPTOR_FILE "tables.txt"', "#define TBL_MAX_NUM_TABLES 1", "#define TBL_MAX_TABLE_NAME_LEN 3",
               "#define TBL_MAX_FIELD_NAME_LEN 3", "#define TBL_MAX_TOTAL_NUM_FIELDS 2", "#define TBL_MAX_RECORD_SIZE 32   'power of two"],
}
# code for on_sys_init (kept minimal and safe; real use - references/recipes.md)
INIT = {
    "settings": ["if stg_start() <> EN_STG_STATUS_OK then",
                 "\t'settings are damaged or the descriptor changed: write the defaults",
                 "\tstg_restore_multiple(EN_STG_INIT_MODE_OVERRIDE)", "end if"],
    "sntp": ["sntp_init()"],
    "dhcp": ["dhcp_start(PL_SOCK_INTERFACE_NET, \"\", \"\")    'answer comes to callback_dhcp_ok"],
}
# resource files: name -> (type in .tpr, content)
RESOURCES = {
    "settings": ("settings.txt", "text",
                 ">>DN\tE\tS\t1\t0\t15\tI\t^\tDevice name\r\n>>IP\tE\tD\t1\t4\t4\tI\t192.168.1.40\tIP address\r\n"),
    "tables": ("tables.txt", "text", "==LOG\t100\tT\t0\r\n>>VAL\tW\t0\t65535\t0\r\n"),
}
# bodies of callbacks that must do something for the library to work (the rest stay empty)
def callback_body(name, objects, wifi, order=()):
    """Bodies of the callbacks that must do something for the library to work (the rest stay empty)."""
    if name.lower() == "callback_dns_answer_acquired" and "mqtt" in order:
        return ["mqtt_dns_answer_acquired(return_type, return_string)    'the mqtt library resolves the broker name through dns"]
    if name.lower() != "callback_dhcp_ok":
        return []
    b = ["'the library does NOT apply the address itself"]
    if "net" in objects:
        b += ["if interface = PL_SOCK_INTERFACE_NET then", "\tif renew = YES and net.ip = ip then exit sub",
              "\tnet.ip = ip", "\tnet.netmask = netmask", "\tnet.gatewayip = gateway_ip", "end if"]
    if wifi:
        b += ["if interface = PL_SOCK_INTERFACE_WLN then", "\tif renew = YES and wln.ip = ip then exit sub",
              "\twln.ip = ip", "\twln.netmask = netmask", "\twln.gatewayip = gateway_ip", "end if"]
    return b


def load(name):
    return json.load(open(ROOT / "data" / name, encoding="utf-8"))


def resolve(libs, known, wifi):
    """Requested libraries plus everything they need, in include order (dependencies first)."""
    order = []

    def add(n):
        if n in order:
            return
        for d in known[n].get("needs", []) + (known[n].get("needs_wifi", []) if wifi else []):
            add(d)
        order.append(n)
    for n in libs:
        add(n)
    return order


def main(argv):
    if not argv or "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0 if argv else 2
    data = load("libraries.json")
    known = {k: v for k, v in data["libraries"].items() if v.get("supported")}
    api = load("platform_api.json")
    if "--list" in argv:
        for k, v in known.items():
            extra = (" (нужны: %s)" % ", ".join(v["needs"])) if v.get("needs") else ""
            print("  %-10s %s%s" % (k, v.get("title", ""), extra))
        return 0
    if "--list-platforms" in argv:
        print(", ".join(sorted(api["platforms"])))
        return 0
    opt = lambda k: argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else None
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] not in ("--platform", "--libs", "--name"))]
    platform = opt("--platform")
    if not pos or not platform:
        print("нужно: <папка> --platform \"<платформа>\" (список: --list-platforms)")
        return 2
    by_lower = {p.lower(): p for p in api["platforms"]}
    if platform.lower() in ("ltpp3", "ltpp3(g2)", "lklm601") or platform.lower().startswith("ltpp"):
        print("%s - Linux-плата: на ней не TiOS, проект TIDE для неё не создаётся (references/linux.md)" % platform)
        return 2
    if platform.lower() not in by_lower:
        import difflib
        near = difflib.get_close_matches(platform.lower(), by_lower, n=3, cutoff=0.5)
        print("неизвестная платформа '%s'%s" % (platform, (". Похожие: " + ", ".join(by_lower[n] for n in near)) if near else ""))
        return 2
    platform = by_lower[platform.lower()]
    objects = set(api["platforms"][platform]["objects"])
    optional = api["platforms"][platform]["optional"]      # objects the project must switch on with defines=
    wifi = "wln" in objects or "wln" in optional
    libs = [x.strip().lower() for x in (opt("--libs") or "").split(",") if x.strip()]
    libs = ["settings" if x == "stg" else "tables" if x == "tbl" else x for x in libs]
    bad = [x for x in libs if x not in known]
    if bad:
        print("генератор не знает библиотеки: %s. Знает: %s" % (", ".join(bad), ", ".join(known)))
        return 2
    if "wln" in libs and not wifi:
        print("на платформе %s нет Wi-Fi (объекта wln): уберите wln или выберите плату с W в названии" % platform)
        return 2
    if "dhcp" in libs and "net" not in objects and not wifi:
        print("на платформе %s нет сети" % platform)
        return 2
    order = resolve(libs, known, wifi)
    for n in order:
        why = known[n].get("broken_on", {}).get(platform)
        if why:
            print("библиотека %s версии %s не собирается на %s (%s). Проверено компилятором Tibbo." % (n, data["src_lib_ver"], platform, why))
            return 2
    defines = []
    for n in order:
        for o in known[n].get("objects", []):
            if o in objects:
                continue
            if o not in optional:
                print("библиотеке %s нужен объект %s, а на платформе %s его нет" % (n, o, platform))
                return 2
            if optional[o]["define"] not in defines:
                defines.append(optional[o]["define"])
    folder = Path(pos[0])
    name = opt("--name") or re.sub(r"[^A-Za-z0-9_]+", "_", folder.resolve().name) or "app"
    if folder.exists() and any(folder.iterdir()) and "--force" not in argv:
        print("папка %s не пуста (перезаписать - --force)" % folder)
        return 2
    folder.mkdir(parents=True, exist_ok=True)

    # ---- global.tbh
    g = ["'" + "=" * 67, "'" + " %s - global header. Platform: %s" % (name, platform), "'" + "=" * 67, "",
         "'DEFINES: library settings must come BEFORE the include of the library"]
    for n in order:
        g += DEFINES.get(n, [])
        g += known[n].get("extra_defines", {}).get(platform, [])
    g += ["", "'INCLUDES: order matters - a library goes after the libraries it uses"]
    g += ['include "%s"' % known[n]["header"] for n in order]
    g += ["", "'DECLARATIONS: your own subs, functions and global variables (dim them in ONE .tbs file)", ""]

    # ---- main.tbs
    hooks = {}
    for n in order:
        for h in known[n]["hooks"]:
            hooks.setdefault(h["event"], []).append(h["call"])
    init = []
    for n in order:
        body = INIT.get(n, [])
        if n == "dhcp" and "net" not in objects:
            body = ["'no Ethernet here: start DHCP for Wi-Fi after association - dhcp_start(PL_SOCK_INTERFACE_WLN, \"\", \"\")"]
        init += body
    m = ['include "global.tbh"', "", "'" + "-" * 67, "sub on_sys_init()"]
    m += ["\t" + x for x in (init or ["'your initialization"])]
    m += ["\t'your initialization goes here; one sys.buffalloc() after ALL buffer requests", "end sub"]
    for ev in EVENT_ORDER[1:]:
        if ev not in hooks:
            continue
        m += ["", "'" + "-" * 67, "sub %s(%s)" % (ev, EVENT_SIGNATURE[ev])]
        m += ["\t" + c for c in hooks[ev]]
        m += ["\t'your code", "end sub"]

    # ---- device.tbs
    d = ['include "global.tbh"', "", "'Callbacks of the libraries. Every one of them must exist, even if empty:",
         "'the linker reports a missing one as \"unresolved address '?F:callback_...'\".", ""]
    ncb = 0
    only = os.environ.get("TIBBO_NEW_CALLBACKS")
    only = None if only is None else set(x for x in only.lower().split(",") if x)
    for n in order:
        cbs = known[n]["callbacks"]
        if not cbs:
            continue
        d += ["'" + "-" * 30 + " " + n]
        for cb in cbs:
            if only is not None and cb["name"].lower() not in only:
                continue   # (data build: tools/verify_libraries.py finds which callbacks the linker needs)
            if only is None and not cb.get("required"):
                continue   # needed only with non-default library settings
            ncb += 1
            d += [cb["decl"]]
            d += ["\t" + x for x in callback_body(cb["name"], objects | set(optional if defines else []), wifi, order)]
            d += ["end " + cb["kind"], ""]

    # ---- .tpr
    t = ["[project]", "name=%s" % name, "output=%s.tpc" % name, "debug=%s" % ("off" if "--release" in argv else "on"),
         "platform=%s" % platform, "src_lib_ver=%s" % data["src_lib_ver"], "transport=udp_broadcast"]
    if defines:   # optional TiOS objects of this platform (TIDE: Project Settings -> Customize)
        t.append("defines=" + "".join(" /d" + x for x in defines))
    t.append("")
    files = [("main.tbs", "basic", "project"), ("global.tbh", "header", "project"), ("device.tbs", "basic", "project")]
    res = []
    for n in order:
        if n in RESOURCES:
            fn, typ, content = RESOURCES[n]
            files.append((fn, typ, "project"))
            res.append((fn, content))
        for f in known[n]["files"]:
            files.append((f, "header" if f.lower().endswith(".tbh") else "basic", "commonlib"))
    for i, (path, typ, loc) in enumerate(files, 1):
        t += ["[file%d]" % i, "path=%s" % path, "type=%s" % typ, "location=%s" % loc, ""]

    def write(fn, lines_or_text):
        text = lines_or_text if isinstance(lines_or_text, str) else "\r\n".join(lines_or_text) + "\r\n"
        (folder / fn).write_bytes(text.encode("utf-8"))
    write("global.tbh", g)
    write("main.tbs", m)
    write("device.tbs", d)
    write(name + ".tpr", t)
    for fn, content in res:
        write(fn, content)

    print("Проект создан: %s (%s)" % (folder, platform))
    print("  библиотеки: %s" % (", ".join(order) or "нет"))
    if defines:
        print("  включены объекты платформы: %s (строка defines= в .tpr)" % ", ".join(d.split("=")[0] for d in defines))
    added = [n for n in order if n not in libs]
    if added:
        print("  добавлены сами, потому что нужны выбранным: %s" % ", ".join(added))
    print("  обработчики событий: %s; заготовки callback_*: %d" % (", ".join(["on_sys_init"] + [e for e in EVENT_ORDER[1:] if e in hooks]), ncb))
    print("Дальше: код в main.tbs, сборка - python3 scripts/tibbo_build.py %s" % folder)
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
