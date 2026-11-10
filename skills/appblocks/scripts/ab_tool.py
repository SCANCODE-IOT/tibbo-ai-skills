#!/usr/bin/env python3
"""AppBlocks project (exported JSON) tool.

  python3 ab_tool.py summary  project.json            # what is in the project: board, Tibbits, services, data, flows
  python3 ab_tool.py check    project.json            # structural + editor-registry checks (links, ports, refs, options, features) -> exit 1 on errors
  python3 ab_tool.py tps      project.json [--vin 24] [--out cfg.json]  # hardware -> cfg for tibbo-firmware tps_check.py
  python3 ab_tool.py flow     project.json out.svg    # flow (logic) diagram from node_* positions, links and groups
  python3 ab_tool.py ids      [N]                     # new IDs in AppBlocks style
  python3 ab_tool.py nodes    project.json            # catalogue of node types/ports used in this project
  python3 ab_tool.py lookup   <block|feature|text>    # ports and settings of a block / feature from the editor registry

The format is documented in references/format.md (derived from projects exported by AppBlocks).
"""
import json, re, sys, time, random, string, collections, os


def utf8_stdio():
    """Print UTF-8 whatever the console code page is (Windows cp1251/cp1252, pipes in Git Bash)."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

REF = re.compile(r"\{\{\$([A-Za-z0-9_]+)\}\}")
NODE_PREFIX = "node_"
SERVICE_TOGGLES = ["net", "wifi", "dhcp", "dns", "sntp", "http", "httpserver", "mqtt", "cgg", "cell", "bt",
                   "modbus_master", "modbus_slave", "snmp_agent", "smtp_client", "web_dashboard", "luis", "lcd",
                   "lcd_graph", "tbl", "stg", "fd", "log", "ds_man", "mbedtls"]


def load(path):
    d = json.load(open(path, encoding="utf-8"))
    if isinstance(d, dict) and "data" in d and isinstance(d["data"], list) and d["data"]:
        d = d["data"][0]          # API envelope {count, data:[project]}
    if isinstance(d, dict) and "project" in d and "features" not in d:
        d = d["project"]          # example envelope
    if not isinstance(d, dict) or "features" not in d:
        raise SystemExit(f"{path}: not an AppBlocks project export (no 'features')")
    if isinstance(d.get("device"), dict):   # API form {platform, name}
        d["device"] = d["device"].get("platform") or d["device"].get("name")
    return d


def new_id(n=1):
    """List of n AppBlocks-style IDs (always a list, also for n=1): Date.now() in base36 + random base36 tail
    (observed 16-20 chars). For a single ID use one_id()."""
    out = []
    for _ in range(n):
        ts = int(time.time() * 1000)
        b36 = ""
        while ts:
            ts, r = divmod(ts, 36)
            b36 = (string.digits + string.ascii_lowercase)[r] + b36
        tail = "".join(random.choice(string.digits + string.ascii_lowercase) for _ in range(10))
        out.append(b36 + tail)
        time.sleep(0.002)
    return out


def one_id():
    """One AppBlocks-style ID as a string."""
    return new_id(1)[0]


def all_ids(obj, acc=None, parent=None):
    """Every nested {"id": kind, "settings": {"ID": ...}} -> {ID: (kind, settings)}."""
    if acc is None:
        acc = {}
    if isinstance(obj, dict):
        if "settings" in obj and isinstance(obj["settings"], dict) and "ID" in obj["settings"]:
            acc.setdefault(obj["settings"]["ID"], (obj.get("id"), obj["settings"]))
        for v in obj.values():
            all_ids(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            all_ids(v, acc)
    return acc


def label(f, ids):
    s = f["settings"]
    kind = f["id"]
    name = s.get("DISPLAY_NAME") or ""
    k = kind[len(NODE_PREFIX):] if kind.startswith(NODE_PREFIX) else kind
    extra = ""
    for key, src in (("VARIABLE", "VARNAME"), ("TIMER", "TIMER_NAME"), ("COMMAND", "NAME"), ("TABLE", "NAME"),
                     ("SOCKET", "NAME"), ("WIDGET", "NAME")):
        if s.get(key) and s[key] in ids:
            extra = ids[s[key]][1].get(src) or ""
    if kind == "node_modbus_write":
        extra = f"{s.get('PROTOCOL', '')} {s.get('FUNCTIONCODE', '')}"
    if kind == "node_comparison":
        a = {x["settings"]["TARGETPARAM"]: x["settings"]["ARGVALUE"] for x in s.get("ARGUMENTS", [])}
        extra = f"{a.get('operand1', '')} {a.get('operator', '')} {a.get('operand2', '')}"
    if kind == "node_time_delay":
        extra = f"{s.get('DURATION')} s"
    if kind == "node_network_changed":
        extra = f"type {s.get('NETWORK_TYPE')} event {s.get('NETWORK_EVENT')}"
    if kind == "node_socket_event":
        extra = (extra + " " + s.get("EVENT_TYPE", "")).strip()
    return (name or k), extra


def port_name(p, ids):
    x = ids.get(p)
    if x and x[0] == "node_switch_case":
        return f"case {x[1].get('VALUE')}"
    return p


def pretty_ref(text, ids):
    def rep(m):
        x = ids.get(m.group(1))
        if not x:
            return "{" + m.group(1) + "}"
        s = x[1]
        return "{" + (s.get("VARNAME") or s.get("SETTINGID") or s.get("NAME") or s.get("TIMER_NAME") or m.group(1)) + "}"
    return REF.sub(rep, str(text))


# ------------------------------------------------------------------ summary
def summary(d):
    F = d["features"]
    ids = all_ids(d)
    by = collections.defaultdict(list)
    for f in F:
        by[f["id"]].append(f["settings"])
    print(f"Проект: {d.get('name')}  (id {d.get('id')})")
    print(f"Плата: {d.get('device')}   runtime: {d.get('runtime')}   версия формата/проекта: {d.get('version')}")
    if d.get("description"):
        print("Описание:", d["description"][:300])
    bs = (by.get("boardsetting") or [{}])[0]
    if bs:
        print(f"Сборка: PoE={bs.get('POE')} 5VDIRECT={bs.get('5VDIRECT')} TPB={bs.get('TPB')} DIN={bs.get('DIN')} "
              f"адаптер={bs.get('POWERADAPTER')} ASM={bs.get('ASM')}")
    tib = sorted([s for k, v in by.items() if k.startswith("tibbit_") for s in v], key=lambda s: int(s.get("SOCKET") or 0))
    print("\nTibbit:")
    for s in tib:
        extra = {k: v for k, v in s.items() if k not in ("ID", "SOCKET", "TIBBIT", "PLATFORM", "GENERAL")}
        print(f"  S{s.get('SOCKET'):<3} #{s.get('TIBBIT'):<5} {json.dumps(extra, ensure_ascii=False) if extra else ''}")
    wm = by.get("wireless_module")
    if wm:
        print(f"  Wi-Fi модуль: {wm[0].get('MODULE')} (enabled={wm[0].get('ENABLED')})")
    print("\nСервисы (ENABLED=1):", ", ".join(k for k in SERVICE_TOGGLES if by.get(k) and str(by[k][0].get("ENABLED", "1")) == "1"))
    print("Выключены:", ", ".join(k for k in SERVICE_TOGGLES if by.get(k) and str(by[k][0].get("ENABLED", "1")) == "0"))
    net = (by.get("net") or [{}])[0]
    if net:
        print(f"Ethernet: DHCP={net.get('DHCP')} IP={net.get('IP')} NM={net.get('NM')} GW={net.get('GI')}")
    gv = (by.get("global_vars") or [{}])[0].get("VARS", [])
    print(f"\nПеременные ({len(gv)}): " + ", ".join(f"{v['settings']['VARNAME']}:{v['settings']['DATATYPE']}" for v in gv))
    tm = (by.get("timers") or [{}])[0].get("TIMERS", [])
    print(f"Таймеры ({len(tm)}): " + ", ".join(t["settings"]["TIMER_NAME"] for t in tm))
    cm = (by.get("commands") or [{}])[0].get("COMMANDS", [])
    print(f"Команды ({len(cm)}): " + ", ".join(c["settings"]["NAME"] for c in cm))
    st = (by.get("stg") or [{}])[0].get("SETTINGS", [])
    print(f"Настройки STG ({len(st)}): " + ", ".join(f"{x['settings']['SETTINGID']}={x['settings'].get('DEFAULT')}" for x in st))
    tb = (by.get("tbl") or [{}])[0].get("TABLES", [])
    for t in tb:
        s = t["settings"]
        print(f"Таблица {s['NAME']} (max {s.get('MAXRECORDS')}): " + ", ".join(f["settings"]["NAME"] for f in s.get("FIELDS", [])))
    cf = (by.get("custom_features") or [{}])[0].get("FEATURES", [])
    for c in cf:
        s = c["settings"]
        print(f"Custom feature «{s.get('NAME')}» ({s.get('TYPE')}, {s.get('RUNTIMES')}): блоков кода {len(s.get('CODE_BLOCKS', []))} → "
              + ", ".join(b["settings"].get("LOCATION", "") for b in s.get("CODE_BLOCKS", [])))
    nodes = [f for f in F if f["id"].startswith(NODE_PREFIX) and f["id"] not in ("node_link", "node_group")]
    links = [f["settings"] for f in F if f["id"] == "node_link"]
    groups = {f["settings"]["ID"]: f["settings"].get("DISPLAY_NAME") for f in F if f["id"] == "node_group"}
    print(f"\nЛогика: узлов {len(nodes)}, связей {len(links)}, групп {len(groups)}: {', '.join(groups.values())}")
    print("Типы узлов:", dict(collections.Counter(f["id"][5:] for f in nodes)))
    if d.get("featureFlags"):
        for fl in d["featureFlags"]:
            print(f"Флаг «{fl['name']}» ({'вкл' if fl.get('enabled') else 'выкл'}): управляет {len(d.get('featureFlagMap', {}).get(fl['id'], []))} элементами")
    # event chains
    print("\nЦепочки (от событий):")
    for line in chains(d, ids)[:40]:
        print("  " + line)


def chains(d, ids):
    F = d["features"]
    feats = {f["settings"]["ID"]: f for f in F if "ID" in f["settings"]}
    out = collections.defaultdict(list)
    has_in = set()
    for f in F:
        if f["id"] == "node_link":
            s = f["settings"]
            out[s["SOURCE_FEATURE"]].append((s["SOURCE_PORT"], s["TARGET_FEATURE"], s["TARGET_PORT"]))
            has_in.add(s["TARGET_FEATURE"])
    roots = [i for i in out if i not in has_in]
    lines = []

    def name(i):
        f = feats.get(i)
        if not f:
            return f"?{i}"
        a, b = label(f, ids)
        return a + (f"[{pretty_ref(b, ids)}]" if b else "")

    def walk(i, depth, seen, prefix):
        if depth > 12 or i in seen:
            lines.append(prefix + " …")
            return
        nexts = out.get(i, [])
        if not nexts:
            lines.append(prefix)
            return
        for sp, t, tp in nexts:
            walk(t, depth + 1, seen | {i}, f"{prefix} —{port_name(sp, ids)}→ {name(t)}")
    for r in roots:
        walk(r, 0, set(), name(r))
    return lines


# ------------------------------------------------------------------ check
# fields that hold the ID of another element anywhere in the project (services and panels included)
REF_KEYS = {"SETTINGID", "VARIABLE", "TIMER", "COMMAND", "TABLE", "LINKEDSETTING", "FEATURE", "INTLINE", "TIBBIT",
            "SOCKET", "SERIAL_PORT", "WIDGET", "GROUP", "SCREEN", "DEVICE", "SOURCE_FEATURE", "TARGET_FEATURE"}
IDLIKE = re.compile(r"^(?=.*[0-9])(?=.*[a-z])[0-9a-z]{14,24}$")
# panels whose items expose settings / commands / tables by ID
PANELS = ("web_dashboard", "luis", "ds_man", "lcd_menu", "cgg")


def deep_refs(obj, path, out):
    """Yield (path, key, value, kind) for every REF_KEYS field holding an ID-like value, at any depth."""
    if isinstance(obj, dict):
        kind = obj.get("id") if isinstance(obj.get("id"), str) else None
        st = obj.get("settings") if isinstance(obj.get("settings"), dict) else None
        if st is not None:
            for k, v in st.items():
                if k in REF_KEYS and isinstance(v, str) and IDLIKE.match(v):
                    out.append((path, k, v, kind, st))
        for k, v in obj.items():
            deep_refs(v, f"{path}/{kind or k}", out)
    elif isinstance(obj, list):
        for v in obj:
            deep_refs(v, path, out)
    return out


def check_panels_and_refs(d, ids, errs, warns):
    """Errors AppBlocks shows in Problems but node-level checks miss (found on a real import, Oct 2026)."""
    seen = set()
    for f in d["features"]:
        for path, k, v, kind, st in deep_refs(f, f["id"], []):
            if v not in ids and (path, k, v) not in seen:
                seen.add((path, k, v))
                errs.append(f"{path}: {k}={v} не найден (в редакторе: «Setting is not defined» / "
                             f"«Connected Setting is not set» / «Command is not set»)")
    for f in d["features"]:
        if f["id"] not in PANELS:
            continue
        st = f["settings"]
        if st.get("ENABLED", "1") != "1":
            continue
        used = collections.Counter()
        for g in st.get("GROUPS", []) or []:
            for it in g.get("settings", {}).get("SETTINGS", []) or []:
                sid = it.get("settings", {}).get("SETTINGID", "")
                if not sid:
                    errs.append(f"{f['id']}: пункт «{it['settings'].get('NAME', '')}» без настройки (Connected Setting is not set)")
                used[sid] += 1
        for sid, c in used.items():
            if sid and c > 1:
                errs.append(f"{f['id']}: настройка {sid} выведена {c} раз (Same setting cannot be exposed more than once)")
        for w in st.get("WIDGETS", []) or []:
            ws = w.get("settings", {})
            if w.get("id") == "button_widget" and not ws.get("VARIABLE"):
                errs.append(f"{f['id']}: кнопка «{ws.get('LABEL', '')}» без команды (Command is not set)")
    gv = next((f["settings"] for f in d["features"] if f["id"] == "global_vars"), None)
    if gv is not None:
        try:
            if float(gv.get("INTERVAL", "1")) < 1:
                errs.append(f"global_vars INTERVAL={gv['INTERVAL']}: редактор требует ≥ 1 с "
                            "(«Value for Update Interval (seconds) must be at least 1»)")
        except ValueError:
            errs.append(f"global_vars INTERVAL={gv.get('INTERVAL')!r} не число")


# ------------------------------------------------------------------ registry checks (data/registry.json, from the editor)
REGISTRY = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "registry.json")
LEGIT_HIDDEN = {"node_group", "node_group_input", "node_group_output", "node_label", "node_link"}


def load_registry():
    try:
        return json.load(open(REGISTRY, encoding="utf-8"))
    except (OSError, ValueError):
        return None


def check_registry(d, errs, warns, reg=None):
    """Node types, ports, option values, linked features, hidden blocks, board limits - against the editor registry."""
    reg = reg or load_registry()
    if not reg:
        warns.append("data/registry.json не найден - проверка по реестру редактора пропущена")
        return
    N = reg["nodes"]
    F = d["features"]
    feats = {f["settings"].get("ID"): f for f in F}
    present = {f["id"]: f for f in F}
    device = str(d.get("device") or "")
    runtime = d.get("runtime") or "tios"
    rt_name = {"tios": "TiOS", "zephyr": "Zephyr", "micropython": "MicroPython"}
    only = lambda v: ", ".join(rt_name.get(r, r) for r in v["runtimes"]) or "ни в одной среде"
    for f in F:
        k, s = f["id"], f["settings"]
        if not k.startswith(NODE_PREFIX) or k == "node_link":
            if device and s.get("ENABLED", "1") != "0":
                for kind in ("features", "peripherals", "libraries"):
                    v = (reg.get(kind) or {}).get(k)
                    if v and v.get("devices") and device not in v["devices"]:
                        warns.append(f"{k}: в редакторе доступен только для {', '.join(v['devices'])}, а плата проекта {device}")
            if str(s.get("ENABLED", "1")) != "0":
                for kind in ("features", "peripherals", "libraries", "items", "widgets"):
                    v = (reg.get(kind) or {}).get(k)
                    if v and v.get("runtimes") is not None and runtime not in v["runtimes"]:
                        warns.append(f"{k} ({v.get('name')}): по реестру редактора есть только в среде {only(v)}, "
                                     f"а проект на {rt_name.get(runtime, runtime)} - проверь вкладку Problems в редакторе")
                        break
            continue
        v = N.get(k)
        if v is None:
            errs.append(f"узел {s.get('ID')}: неизвестный тип блока {k} (нет в реестре редактора, см. blocks.md)")
            continue
        if v.get("cat") == "Hidden" and k not in LEGIT_HIDDEN:
            warns.append(f"узел {k} {s.get('ID')} ({v.get('name')}): блока нет в палитре редактора (устаревший/служебный) - "
                         "в новых проектах замени блоком из blocks.md")
        if device and (v.get("unsupportedDevices") and device in v["unsupportedDevices"]
                       or v.get("devices") and device not in v["devices"]):
            errs.append(f"узел {k} {s.get('ID')}: блок недоступен на плате {device}")
        if v.get("runtimes") is not None and runtime not in v["runtimes"]:
            # checked with the code generator: such a block in a TiOS project gives HTTP 500 with no explanation
            errs.append(f"узел {k} {s.get('ID')} ({v.get('name')}): блок есть только в среде {only(v)}, а проект на "
                        f"{rt_name.get(runtime, runtime)}. Генератор кода AppBlocks на таком проекте отвечает ошибкой 500 без "
                        "объяснений. Убери блок или собери то же из блоков этой среды (blocks.md, столбец «Особенности»)")
        ft = v.get("feat")
        if ft and ft != "general" and ft in reg.get("features", {}):
            if ft not in present:
                errs.append(f"узел {k} {s.get('ID')}: нужна feature {ft}, её нет в проекте")
            elif present[ft]["settings"].get("ENABLED", "1") == "0":
                warns.append(f"узел {k} {s.get('ID')}: feature {ft} выключена (ENABLED=0) - блок не заработает")
        for sk, sv in s.items():
            st = v["set"].get(sk)
            if not st or not st.get("o") or not isinstance(sv, (str, int)) or str(sv) == "" or REF.search(str(sv)):
                continue
            opts = {str(o) for o in st["o"]}
            for x in (str(sv).split(",") if st.get("t") == "multi_option" else [str(sv)]):
                if x not in opts:
                    errs.append(f"узел {k} {s.get('ID')}: {sk}={x!r} - недопустимое значение "
                                f"(варианты: {', '.join(sorted(opts)[:12])})")
    for f in F:
        if f["id"] != "node_link":
            continue
        s = f["settings"]
        for side, port_side, fld in (("SOURCE", "out", "SOURCE_PORT"), ("TARGET", "in", "TARGET_PORT")):
            node = feats.get(s.get(f"{side}_FEATURE"))
            if not node or node["id"] not in N or N[node["id"]].get("dynamic_ports"):
                continue
            ports = N[node["id"]].get(port_side) or {}
            if s.get(fld) not in ports:
                errs.append(f"link {s.get('ID')}: у {node['id']} нет {'выхода' if port_side == 'out' else 'входа'} "
                            f"{s.get(fld)!r} (есть: {', '.join(ports) or '-'})")


# ------------------------------------------------------------------ generated-code pitfalls (checked by generation, 2026-10-22)
CMP_OPERATORS = {"=", "<>", "<", "<=", ">", ">="}   # editor's operators; the tios generator copies the text into BASIC as is
FRAMEWORK_OUTPUTS = {"TPP": {46, 47, 48}}           # TPP2/TPP3: signal strength bar (reset, clock, data) made outputs at boot


def check_codegen(d, errs, warns):
    runtime = d.get("runtime") or "tios"
    board = str(d.get("device") or "")
    fw_out = next((v for k, v in FRAMEWORK_OUTPUTS.items() if board.upper().startswith(k)), set())
    for f in d["features"]:
        k, s = f["id"], f["settings"]
        if k == "node_digital_line_set":
            ln = str(s.get("LINE_NUMBER", "")).strip()
            if REF.search(ln):
                continue
            if not ln.isdigit():
                errs.append(f"узел {k} {s.get('ID')}: LINE_NUMBER={ln!r} - нужен номер линии числом (48, а не PL_IO_NUM_48): "
                            f"генератор пишет io.lineset(\"{ln}\", …); неявное преобразование строки в число (val) даст 0, "
                            "то есть запись, скорее всего, уйдёт на линию 0 (в TIDE не проверено)")
            elif int(ln) not in fw_out:
                warns.append(f"узел {k} {s.get('ID')}: линия {ln} - блок не переводит линию в выход (io.enabled не генерируется); "
                             "запись подействует, только если линию сделал выходом фреймворк или Tibbit проекта - "
                             "проверь в коде `ab_api.py code` (generated-code.md §Digital Line Set)")
        elif k == "node_comparison":
            for a in s.get("ARGUMENTS", []) or []:
                st = a.get("settings", {})
                if st.get("TARGETPARAM") != "operator":
                    continue
                op = str(st.get("ARGVALUE", "")).strip()
                if op in CMP_OPERATORS or REF.search(op):
                    continue
                msg = (f"узел {k} {s.get('ID')}: оператор {op!r} - в редакторе есть только = <> < <= > >= "
                       f"(для tios текст уходит в Tibbo BASIC как есть: {op!r} там нет)")
                (errs if runtime == "tios" else warns).append(msg)


ACTIVE_LOW_RELAYS = {"03_1", "03_2", "06", "07"}   # LOW = load on (docs.tibbo.com); boot level = variable DEFAULT
SERIAL_PORT_TIBBITS = {"05"}                      # checked by compilation (Oct 2026); #01/#02 likely the same, not verified


def check_compile_pitfalls(d, errs, warns):
    """Mistakes that pass the structural checks but fail in the editor (Problems) or in the TIDE compiler.
    Found while building the 'Smart Greenhouse' project (TPP3W(G2), tios, Oct 2026) and checked with POST /api/projects/build."""
    F = d["features"]
    ids = all_ids(d)
    gv = next((f["settings"] for f in F if f["id"] == "global_vars"), {}) or {}
    allvars = [v.get("settings", {}) for k in ("VARS", "AUTOVARS") for v in (gv.get(k) or [])]
    by_feature = collections.defaultdict(list)
    for v in allvars:
        by_feature[(v.get("FEATURE"), v.get("FEATURE_SETTING"))].append(v)
    # 1. {{$ID}} of an STG setting: only its autovariable is visible to the logic
    stg_ids = {i for i, (k, _) in ids.items() if k == "stg_setting"}
    for f in F:
        if not f["id"].startswith(NODE_PREFIX):
            continue
        for m in REF.findall(json.dumps(f["settings"])):
            if m in stg_ids:
                av = by_feature.get((m, "SETTINGID"))
                hint = f"используй {{{{${av[0]['ID']}}}}} (авто-переменная {av[0].get('VARNAME')})" if av else \
                    "заведи авто-переменную настройки (FEATURE = ID настройки, FEATURE_SETTING = SETTINGID) и ссылайся на неё"
                errs.append(f"узел {f['id']} {f['settings'].get('ID')}: {{{{${m}}}}} - это ID настройки STG, генератор оставит "
                            f"`${m}` и TIDE выдаст «undeclared identifier»; {hint}")
    for s in (x["settings"] for f in F if f["id"] == "stg" for x in (f["settings"].get("SETTINGS") or [])):
        if not by_feature.get((s.get("ID"), "SETTINGID")):
            warns.append(f"настройка STG {s.get('SETTINGID')}: нет авто-переменной - логика её не видит, а колбэки STG шаблона "
                         f"(var_{s.get('SETTINGID')}_update_completed) могут не скомпилироваться")
    # 2. duplicate identifiers (Tibbo BASIC is case-insensitive): variables vs Modbus devices
    names = collections.defaultdict(list)
    for v in allvars:
        if v.get("VARNAME"):
            names[v["VARNAME"].lower()].append("переменная")
    for f in F:
        if f["id"] == "modbus_master":
            for dv in f["settings"].get("MODBUSDEVICES") or []:
                n = dv.get("settings", {}).get("NAME", "")
                if n:
                    names[n.lower()].append("устройство Modbus")
    for n, kinds in names.items():
        if len(kinds) > 1:
            errs.append(f"имя {n!r} занято {len(kinds)} раз ({', '.join(sorted(set(kinds)))}): редактор - «Name conflict: {n}. "
                        "No duplicate names allowed. Tibbo Basic identifiers are case-insensitive» (устройству Modbus дай префикс, например mb_)")
    # 3. serial-port Tibbit needs the port autovariable (generator writes `<NAME>=0`)
    for f in F:
        t = f["id"][7:] if f["id"].startswith("tibbit_") else None
        if t in SERIAL_PORT_TIBBITS and not by_feature.get((f["settings"].get("ID"), "NAME")):
            errs.append(f"{f['id']} S{f['settings'].get('SOCKET')}: нет авто-переменной порта (byte, FEATURE_SETTING = NAME, DEFAULT 1) - "
                        f"генератор пишет `{f['settings'].get('NAME')}=0` и TIDE выдаст «undeclared identifier»")
    # 4. 1-Wire sensors need Data Tables with the OWSENS table
    ow = next((f["settings"] for f in F if f["id"] == "unowiresensors"), {}) or {}
    if ow.get("SENSORS"):
        tbl = next((f["settings"] for f in F if f["id"] == "tbl"), {}) or {}
        tables = {t.get("settings", {}).get("NAME") for t in tbl.get("TABLES") or []}
        if tbl.get("ENABLED") != "1" or "OWSENS" not in tables:
            errs.append("1-Wire (unowiresensors) без Data Tables: нужны tbl ENABLED=1 и таблица OWSENS (как в примере tbt62), "
                        "иначе TIDE: «undeclared identifier 'tbl_select'»")
    # 5. active-low relays: the variable DEFAULT is the line level at boot
    for f in F:
        t = f["id"][7:] if f["id"].startswith("tibbit_") else None
        if t not in ACTIVE_LOW_RELAYS:
            continue
        for key in ("L1NAME", "L2NAME"):
            for v in by_feature.get((f["settings"].get("ID"), key), []):
                if str(v.get("DEFAULT", "")).strip() not in ("1", "true", "True"):
                    warns.append(f"#{t} S{f['settings'].get('SOCKET')} {v.get('VARNAME')}: DEFAULT={v.get('DEFAULT')!r} - реле активно по LOW, "
                                 "генератор ставит линию при старте в значение по умолчанию: нагрузка включится при подаче питания. "
                                 "Ставь DEFAULT 1 (выключено) и включай значением 0")
    # 6. Variable Set on a Modbus register variable writes to the device; input registers / discrete inputs are read-only
    ro = {i for i, (k, st) in ids.items() if k == "modbus_device_register"
          and st.get("DATATYPE") in ("ReadInputRegisters", "ReadInputStatus")}
    ro_vars = {v["ID"]: v.get("VARNAME") for v in allvars if v.get("FEATURE") in ro}
    for f in F:
        if f["id"] == "node_variable_set" and f["settings"].get("VARIABLE") in ro_vars:
            warns.append(f"узел node_variable_set {f['settings'].get('ID')}: {ro_vars[f['settings']['VARIABLE']]} - регистр Modbus только для чтения "
                         "(Input Register / Discrete Input), а Variable Set на переменную регистра отправляет запись в устройство. "
                         "Расчёт веди в отдельной переменной")


# Widths of {{$var}} in generated tios strings: float -> ftofixed(x,4), integers -> str(), boolean -> str()
TIOS_WIDTH = {"float": 12, "real": 12, "dword": 10, "long": 11, "word": 5, "short": 6, "integer": 6, "char": 4,
              "byte": 3, "boolean": 1}
OPS = re.compile(r"[-+*/]")


def check_runtime_limits(d, errs, warns):
    """Runtime limits found on TOTAL SMART SCHOOL GREENHOUSE 2 (Nov 2026), checked in the generated Tibbo BASIC."""
    F = d["features"]
    gv = next((f["settings"] for f in F if f["id"] == "global_vars"), {}) or {}
    vtype = {v.get("settings", {}).get("ID"): v.get("settings", {}).get("DATATYPE", "float")
             for k in ("VARS", "AUTOVARS") for v in (gv.get(k) or [])}
    tios = (d.get("runtime") or "tios") == "tios"
    for f in F:
        st = f["settings"]
        args = {a["settings"].get("TARGETPARAM"): a["settings"].get("ARGVALUE", "")
                for a in st.get("ARGUMENTS") or [] if isinstance(a, dict) and "settings" in a}
        # 7. MQTT payload: mqtt_publish(topic, data) builds chr(0)+chr(len)+topic+data in ONE string -> 255 bytes on tios
        if tios and f["id"] == "node_mqtt_pub":
            topic, data = str(args.get("topic", "")), str(args.get("publish_data", ""))
            unknown = []
            n = len(topic) + 2 + len(REF.sub("", data))
            for m in REF.findall(data):
                t = vtype.get(m)
                if t is None or t == "string":
                    unknown.append(m)
                else:
                    n += TIOS_WIDTH.get(t, 12)
            where = f"узел node_mqtt_pub {st.get('ID')} ({topic})"
            if n > 255:
                errs.append(f"{where}: сообщение до {n} байт вместе с топиком - строка Tibbo BASIC вмещает 255, "
                            "mqtt_publish соберёт пакет в одну строку и хвост пропадёт без ошибки. Раздели на несколько "
                            "сообщений (по топикам) или сократи ключи; float выводится как ftofixed(x,4)")
            elif n > 230 or (unknown and n > 120):
                warns.append(f"{where}: сообщение до {n} байт" + (f" плюс строковые переменные {len(unknown)} шт." if unknown else "")
                             + " - близко к пределу строки Tibbo BASIC 255 байт вместе с топиком")
        # 8. Delay with an expression: generator writes sys.timercountms + <DURATION> * 1000
        if f["id"] == "node_time_delay":
            dur = str(st.get("DURATION", ""))
            if OPS.search(REF.sub("v", dur).lstrip("-")) and not (dur.startswith("(") and dur.endswith(")")):
                errs.append(f"узел node_time_delay {st.get('ID')}: DURATION={dur!r} - генератор пишет "
                            f"`sys.timercountms + {dur} * 1000`, умножится только последнее слагаемое. Посчитай длительность "
                            "в переменную блоком Variable Set и укажи её")
    # 9. web console: widgets and password
    wd = next((f["settings"] for f in F if f["id"] == "web_dashboard"), None)
    if wd and wd.get("ENABLED") == "1":
        if wd.get("WIDGETS") and not any((g.get("settings") or {}).get("WIDGETS") for g in wd.get("WIDGET_GROUPS") or []):
            warns.append("web_dashboard: виджеты лежат в старом поле WIDGETS - генератор берёт только WIDGET_GROUPS "
                         "(widget_group с GROUPID/NAME/WIDGETS). Без открытия в редакторе панель на устройстве будет пустой")
        linked = {f["settings"].get("SETTINGID") for f in F if f["id"] == "linked_setting"
                  and f["settings"].get("FEATURE") == wd.get("ID")}
        if not wd.get("PASSWORD") and "PASSWORD" not in linked:
            warns.append("web_dashboard: пароль администратора пуст и не связан с настройкой - веб-консоль открыта любому в сети. "
                         "Свяжи PASSWORD с настройкой STG (linked_setting, как WBPWD в web-console-roles) и задай пароль на устройстве")


def check_event_params(d, ids, warns, reg=None):
    """{{$param}} in a block must come from a port of a block linked straight into it (editor rule: parameters are seen
    only by the next block; after an ASYNC block or one block further they are empty)."""
    reg = reg or load_registry()
    if not reg:
        return
    nodes_reg = reg.get("nodes", {})
    F = d["features"]
    nodes = {f["settings"]["ID"]: f for f in F if f["id"].startswith(NODE_PREFIX) and f["id"] not in ("node_link", "node_group")}
    inc = collections.defaultdict(list)
    for f in F:
        if f["id"] == "node_link":
            inc[f["settings"]["TARGET_FEATURE"]].append(f["settings"])
    for nid, n in nodes.items():
        params = {m for m in REF.findall(json.dumps(n["settings"])) if m not in ids}
        if not params:
            continue
        avail, srcs = set(), []
        for l in inc.get(nid, []):
            src = nodes.get(l["SOURCE_FEATURE"])
            if not src:
                continue
            srcs.append(f"{src['id']}.{l['SOURCE_PORT']}")
            outs = nodes_reg.get(src["id"], {}).get("out", {}).get(l["SOURCE_PORT"])
            if not outs:          # the registry does not list this port's parameters - cannot judge
                avail.add("*")
            for o in outs or []:
                avail.add("*" if o.startswith("<") else o.split(":")[0])
        miss = sorted(p for p in params if p not in avail and "*" not in avail)
        if miss:
            warns.append(f"узел {n['id']} {nid}: параметр(ы) {', '.join('{{$' + m + '}}' for m in miss)} не придут - "
                         f"входящие связи {', '.join(srcs) or 'нет'} их не дают (параметр виден только следующему блоку, после ASYNC - пусто)")


def check_hardware(d, warns):
    """Yellow triangles on the Hardware canvas (Incorrect pair / Connector required / Tibbit required). Not in Problems."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import ab_pairs
        data = ab_pairs.load_pairs()
    except (ImportError, OSError, ValueError):
        return
    slots = {f["settings"].get("SOCKET"): f["settings"].get("TIBBIT") for f in d["features"]
             if f["id"].startswith("tibbit_") and f["settings"].get("SOCKET")}
    res = ab_pairs.socket_warnings(d.get("device", ""), slots, None, data)
    if not res:
        return
    t = data["tibbits"]
    occ = ab_pairs.occupancy(d["device"], slots, data)
    for M, C in data["boards"][d["device"]]["mateSockets"]:
        m_mod, c_mod = occ.get(M), occ.get(C)
        msgs = set(res.get(M, [])) | set(res.get(C, []))
        if ab_pairs.INCORRECT in msgs:
            warns.append(f"плата: S{M}+S{C} - редактор нарисует жёлтый треугольник «Incorrect pair» (#{c_mod} рядом с #{m_mod}; "
                         f"для #{m_mod} разрешено: #{', #'.join(t.get(m_mod, {}).get('mates', [])) or 'ничего'}). В Problems этого нет")
        if "Tibbit required" in res.get(M, []):
            need = t.get(c_mod, {}).get("mates", [])
            warns.append(f"плата: S{M} пуст, а в S{C} #{c_mod} - «Tibbit required»" + (f" (нужен #{' или #'.join(need)})" if need else ""))
        if "Connector required" in res.get(C, []):
            warns.append(f"плата: у #{m_mod} в S{M} нет разъёма в S{C} - «Connector required»")


def check(d):
    F = d["features"]
    ids = all_ids(d)
    errs, warns = [], []
    top_ids = collections.Counter(f["settings"].get("ID") for f in F)
    for i, c in top_ids.items():
        if c > 1:
            errs.append(f"дублируется ID {i} ({c} раз)")
    feats = {f["settings"]["ID"]: f for f in F if f["settings"].get("ID")}
    port_out = collections.defaultdict(set)
    for f in F:
        if f["id"] == "node_link":
            s = f["settings"]
            for side in ("SOURCE", "TARGET"):
                fid = s.get(f"{side}_FEATURE")
                if fid not in feats:
                    errs.append(f"link {s['ID']}: {side.lower()} {fid} не существует")
            if s.get("SOURCE_FEATURE") == s.get("TARGET_FEATURE"):
                warns.append(f"link {s['ID']}: узел соединён сам с собой")
            src = feats.get(s.get("SOURCE_FEATURE"))
            if src and src["id"] == "node_switch":
                cases = {c["settings"]["ID"] for c in src["settings"].get("CASES", [])}
                if s["SOURCE_PORT"] not in cases and s["SOURCE_PORT"] not in ("default", "switch_default"):
                    warns.append(f"link {s['ID']}: у switch нет case {s['SOURCE_PORT']}")
    linked = set()
    for f in F:
        if f["id"] == "node_link":
            linked.add(f["settings"]["SOURCE_FEATURE"]); linked.add(f["settings"]["TARGET_FEATURE"])
    for f in F:
        k = f["id"]; s = f["settings"]
        if k.startswith(NODE_PREFIX) and k not in ("node_link", "node_group", "node_system", "node_label") and s["ID"] not in linked:
            warns.append(f"узел {k} {s['ID']} ни с чем не соединён")
        if k.startswith(NODE_PREFIX) and s.get("GROUP") and s["GROUP"] not in feats:
            errs.append(f"узел {k} {s['ID']}: группа {s['GROUP']} не существует")
        for key in ("VARIABLE", "TIMER", "COMMAND", "TABLE", "SOCKET", "WIDGET", "SERIAL_PORT"):
            if k.startswith(NODE_PREFIX) and s.get(key) and s[key] not in ids:
                errs.append(f"узел {k} {s['ID']}: {key}={s[key]} не найден")
    for f in F:
        if f["id"] == "linked_setting":
            s = f["settings"]
            if s.get("LINKEDSETTING") not in ids:
                errs.append(f"linked_setting {s['ID']}: настройка {s.get('LINKEDSETTING')} не найдена")
            if s.get("FEATURE") not in ids:
                errs.append(f"linked_setting {s['ID']}: feature {s.get('FEATURE')} не найдена")
    # references inside text values: unresolved ones are either event parameters or typos
    unresolved = collections.Counter()
    for m in REF.findall(json.dumps(d)):
        if m not in ids:
            unresolved[m] += 1
    if unresolved:
        warns.append("ссылки {{$…}} не на ID (это параметры события/записи или опечатка): " + ", ".join(f"{k}×{v}" for k, v in unresolved.most_common()))
    # sockets
    socks = collections.Counter()
    for f in F:
        if f["id"].startswith("tibbit_"):
            socks[f["settings"].get("SOCKET")] += 1
            if f["id"][7:] != f["settings"].get("TIBBIT"):
                errs.append(f"{f['id']}: TIBBIT={f['settings'].get('TIBBIT')} не совпадает с типом feature")
    for sck, c in socks.items():
        if c > 1:
            errs.append(f"в сокет S{sck} поставлено {c} Tibbit")
    check_panels_and_refs(d, ids, errs, warns)
    check_registry(d, errs, warns)
    check_codegen(d, errs, warns)
    check_compile_pitfalls(d, errs, warns)
    check_runtime_limits(d, errs, warns)
    check_event_params(d, ids, warns)
    check_hardware(d, warns)
    for fl in d.get("featureFlags", []):
        for x in d.get("featureFlagMap", {}).get(fl["id"], []):
            if x not in ids:
                errs.append(f"флаг «{fl['name']}»: элемент {x} не найден")
    for e in errs:
        print("[ОШИБКА]", e)
    for w in warns:
        print("[ВНИМАНИЕ]", w)
    print(f"Итог: ошибок {len(errs)}, предупреждений {len(warns)}")
    return 1 if errs else 0


# ------------------------------------------------------------------ tps bridge
def to_tps(d, vin=None):
    by = collections.defaultdict(list)
    for f in d["features"]:
        by[f["id"]].append(f["settings"])
    slots = {}
    for k, v in by.items():
        if k.startswith("tibbit_"):
            for s in v:
                slots[f"S{s['SOCKET']}"] = s["TIBBIT"]
    bs = (by.get("boardsetting") or [{}])[0]
    wm = (by.get("wireless_module") or [{}])[0]
    cfg = {"board": d.get("device"), "slots": slots, "power": {"vin": vin},
           "poe_jumpers": "1-2" if str(bs.get("POE")) == "1" else "2-3",
           "wifi": wm.get("MODULE") if str(wm.get("ENABLED", "0")) == "1" else None,
           "buzzer": True, "ambient_c": 40,
           "_source": f"AppBlocks project {d.get('name')} ({d.get('id')}); adapter {bs.get('POWERADAPTER')}; 5VDIRECT={bs.get('5VDIRECT')}"}
    supplies = {"09", "10", "23", "25", "33"}
    if str(bs.get("5VDIRECT")) == "1":
        cfg["power"]["ext5v_ma"] = 1000
    elif not (set(slots.values()) & supplies):
        cfg["power"]["ext5v_ma"] = 1000
        cfg["_assumption"] = ("в проекте нет Tibbit-источника и 5VDIRECT=0: принято внешнее стабилизированное 5 В / 1 А "
                              "на клеммы платы — уточни у пользователя")
    return cfg


# ------------------------------------------------------------------ flow diagram
KIND_COLOR = {
    "event": "#2F8FE3", "logic": "#9B59B6", "data": "#16A085", "io": "#E67E22", "comm": "#C0392B", "sys": "#5B6770",
}


def kind_of(k):
    k = k[5:]
    if k in ("system", "button", "button_released", "timer_completed", "command_triggered", "socket_event",
             "socket_data_arrival", "network_changed", "time_interval", "cron_event", "variable_changed", "keypad",
             "keypad_released", "interrupt", "wiegand", "mqtt_connected", "mqtt_sub", "modbus_response", "modbus_timeout",
             "ser_data_arrival", "sms_recv", "ir_received", "button_input_pressed", "button_input_released", "http_server_endpoint"):
        return "event"
    if k in ("comparison", "compound_condition", "switch", "time_delay"):
        return "logic"
    if k.startswith("table") or k.startswith("string") or k in ("variable_set", "datetime", "datetime_format", "settings_init",
                                                                  "arithmetic", "math_compound", "bitwise", "random", "num_round",
                                                                  "number_to_fixed", "json_get_string", "log_add"):
        return "data"
    if k in ("command_trigger",):
        return "event"
    if k in ("modbus_write", "mqtt_pub") or k.startswith("socket") or k.startswith("http"):
        return "comm"
    if k in ("beep", "pat", "debug", "lcd_text_widget") or k.startswith("lcd"):
        return "io"
    return "sys"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def flow_svg(d):
    F = d["features"]
    ids = all_ids(d)
    nodes = {f["settings"]["ID"]: f for f in F if f["id"].startswith(NODE_PREFIX) and f["id"] not in ("node_link", "node_group")}
    groups = {f["settings"]["ID"]: f["settings"] for f in F if f["id"] == "node_group"}
    links = [f["settings"] for f in F if f["id"] == "node_link"]
    NW, NH = 200, 64
    # positions: editor X/Y; nodes in a group are stored relative to the canvas too, groups are only labels
    by_group = collections.defaultdict(list)
    for i, n in nodes.items():
        by_group[n["settings"].get("GROUP") or ""].append(i)
    # lay groups out as separate panels so they never overlap (editor coordinates kept inside a panel)
    panels = []
    for g, members in sorted(by_group.items(), key=lambda kv: (kv[0] != "", groups.get(kv[0], {}).get("DISPLAY_NAME", ""))):
        xs = [nodes[i]["settings"].get("X", 0) for i in members]
        ys = [nodes[i]["settings"].get("Y", 0) for i in members]
        panels.append((g, members, min(xs), min(ys), max(xs) + NW - min(xs), max(ys) + NH - min(ys)))
    pos = {}
    y0 = 70
    W = 0
    for g, members, mx, my, w, h in panels:
        for i in members:
            s = nodes[i]["settings"]
            pos[i] = (40 + s.get("X", 0) - mx, y0 + 40 + s.get("Y", 0) - my)
        panels_rect = (20, y0, w + 40, h + 60)
        W = max(W, w + 80)
        nodes_panel = (g, panels_rect)
        y0 += h + 100
        pos[("panel", g)] = panels_rect
    H = y0 + 20
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Inter,Segoe UI,Helvetica,Arial,sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#F7F8FA"/>',
         '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#555"/></marker></defs>',
         f'<text x="20" y="40" font-size="22" font-weight="800" fill="#222">{esc(d.get("name"))} — логика AppBlocks ({len(nodes)} узлов, {len(links)} связей)</text>']
    for g, members, *_ in panels:
        x, y, w, h = pos[("panel", g)]
        title = groups.get(g, {}).get("DISPLAY_NAME") or ("без группы" if not g else g)
        o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#fff" stroke="#D5D9DE"/>')
        o.append(f'<text x="{x + 14}" y="{y + 24}" font-size="15" font-weight="700" fill="#556">Группа: {esc(title)}</text>')
    for l in links:
        a, b = l["SOURCE_FEATURE"], l["TARGET_FEATURE"]
        if a not in pos or b not in pos:
            continue
        x1, y1 = pos[a][0] + NW, pos[a][1] + NH / 2
        x2, y2 = pos[b][0], pos[b][1] + NH / 2
        dx = max(40, abs(x2 - x1) / 2)
        o.append(f'<path d="M{x1},{y1} C{x1 + dx},{y1} {x2 - dx},{y2} {x2},{y2}" fill="none" stroke="#888" stroke-width="1.6" marker-end="url(#a)"/>')
        o.append(f'<text x="{x1 + 8 + (x2 - x1) * 0.12:.0f}" y="{y1 + (y2 - y1) * 0.22 - 5:.0f}" font-size="9.5" fill="#777">{esc(port_name(l["SOURCE_PORT"], ids)[:22])}</text>')
    for i, n in nodes.items():
        x, y = pos[i]
        title, extra = label(n, ids)
        col = KIND_COLOR[kind_of(n["id"])]
        args = n["settings"].get("ARGUMENTS", []) or []
        tip = "\n".join(f"{a['settings']['TARGETPARAM']} = {pretty_ref(a['settings']['ARGVALUE'], ids)}" for a in args)
        o.append(f'<g><title>{esc(n["id"])}\n{esc(tip)}</title>')
        o.append(f'<rect x="{x}" y="{y}" width="{NW}" height="{NH}" rx="8" fill="#fff" stroke="{col}" stroke-width="2"/>')
        o.append(f'<rect x="{x}" y="{y}" width="8" height="{NH}" rx="4" fill="{col}"/>')
        o.append(f'<text x="{x + 16}" y="{y + 22}" font-size="13" font-weight="700" fill="#222">{esc(title[:24])}</text>')
        if extra:
            o.append(f'<text x="{x + 16}" y="{y + 40}" font-size="11" fill="#444">{esc(pretty_ref(extra, ids)[:30])}</text>')
        if args:
            a0 = args[0]["settings"]
            o.append(f'<text x="{x + 16}" y="{y + 56}" font-size="10" fill="#777">{esc((a0["TARGETPARAM"] + "=" + pretty_ref(a0["ARGVALUE"], ids))[:32])}</text>')
        o.append("</g>")
    lx = W - 560
    for k, (name, col) in enumerate((("события", KIND_COLOR["event"]), ("логика", KIND_COLOR["logic"]), ("данные", KIND_COLOR["data"]),
                                     ("связь", KIND_COLOR["comm"]), ("индикация", KIND_COLOR["io"]), ("система", KIND_COLOR["sys"]))):
        o.append(f'<rect x="{lx + k * 92}" y="28" width="12" height="12" fill="{col}"/><text x="{lx + k * 92 + 17}" y="39" font-size="12" fill="#333">{name}</text>')
    o.append("</svg>")
    return "\n".join(o)


def nodes_catalog(d):
    F = d["features"]
    feats = {f["settings"]["ID"]: f for f in F if f["settings"].get("ID")}
    ports = collections.defaultdict(lambda: {"in": set(), "out": set()})
    for f in F:
        if f["id"] == "node_link":
            s = f["settings"]
            if s["SOURCE_FEATURE"] in feats:
                ports[feats[s["SOURCE_FEATURE"]]["id"]]["out"].add(s["SOURCE_PORT"])
            if s["TARGET_FEATURE"] in feats:
                ports[feats[s["TARGET_FEATURE"]]["id"]]["in"].add(s["TARGET_PORT"])
    for k in sorted({f["id"] for f in F if f["id"].startswith(NODE_PREFIX)}):
        print(f"{k:<28} in: {', '.join(sorted(ports[k]['in'])) or '—':<30} out: {', '.join(sorted(ports[k]['out'])) or '—'}")


def lookup(q):
    """Print registry entries whose id equals q, or whose id/name contains q (case-insensitive)."""
    reg = load_registry()
    if not reg:
        raise SystemExit("data/registry.json не найден")
    ql = q.lower()
    hits = []
    for kind in ("nodes", "features", "libraries", "items", "tibbits", "peripherals", "widgets"):
        for k, v in reg.get(kind, {}).items():
            if k.lower() == ql:
                hits.insert(0, (kind, k, v))
            elif ql in k.lower() or ql in str(v.get("name", "")).lower():
                hits.append((kind, k, v))
    if not hits:
        print("ничего не найдено"); return 1
    for kind, k, v in hits[:12]:
        print(f"[{kind}] {k} - {v.get('name')}" + (f"  (палитра: {v['cat']})" if v.get("cat") else ""))
        if v.get("cat") == "Hidden" and k not in LEGIT_HIDDEN:
            print("  нет в палитре редактора (устаревший/служебный): в новых проектах не использовать, замену ищи в blocks.md")
        for side in ("in", "out"):
            if side in v:
                print(f"  {'входы ' if side == 'in' else 'выходы'}: " + (", ".join(
                    p + (f"({', '.join(a)})" if a else "") for p, a in v[side].items()) or "-"))
        if v.get("runtimes") is not None:
            print("  только в среде: " + (", ".join(v["runtimes"]) or "нет"))
        extra = [x for x in ("feat", "async", "dynamic_ports", "devices", "unsupportedDevices", "requirements") if v.get(x)]
        if extra:
            print("  " + "; ".join(f"{x}={v[x]}" for x in extra))
        for sk, st in v.get("set", {}).items():
            if st.get("t") in ("hidden", "group"):
                continue
            o = f" [{' | '.join(str(x) + ('=' + str(st['on'][str(x)]) if str(x) in st.get('on', {}) else '') for x in st['o'][:30])}]" if st.get("o") else ""
            dflt = f" ={st['d']}" if "d" in st and not isinstance(st["d"], (list, dict)) else ""
            print(f"  {sk}: {st.get('t')}{' →' + st['ref'] if st.get('ref') else ''}{o}{dflt}")
    if len(hits) > 12:
        print(f"... ещё {len(hits) - 12}, уточни запрос")
    return 0


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(2)
    cmd = a[0]
    if cmd == "lookup":
        sys.exit(lookup(" ".join(a[1:])))
    if cmd == "ids":
        print("\n".join(new_id(int(a[1]) if len(a) > 1 else 1))); return
    d = load(a[1])
    if cmd == "summary":
        summary(d)
    elif cmd == "check":
        sys.exit(check(d))
    elif cmd == "tps":
        vin = float(a[a.index("--vin") + 1]) if "--vin" in a else None
        txt = json.dumps(to_tps(d, vin), ensure_ascii=False, indent=1)
        if "--out" in a:
            open(a[a.index("--out") + 1], "w", encoding="utf-8").write(txt)
        else:
            print(txt)
    elif cmd == "flow":
        open(a[2], "w", encoding="utf-8").write(flow_svg(d))
    elif cmd == "nodes":
        nodes_catalog(d)
    else:
        print(__doc__); sys.exit(2)


if __name__ == "__main__":
    utf8_stdio()
    try:
        main()
    except IndexError:
        print("не хватает аргумента команды\n" + __doc__)
        sys.exit(2)
    except BrokenPipeError:
        pass
