#!/bin/sh
# Offline regression for ab_tool.py on bundled example projects (no network, no key)
cd "$(dirname "$0")/.." || exit 2
# python3 on Linux/macOS, python on Windows (Git Bash); override with PY=...
if [ -z "$PY" ]; then if python3 -c "" >/dev/null 2>&1; then PY=python3; else PY=python; fi; fi
fail=0; T=$(mktemp -d)
for f in examples/*.json; do
  "$PY" scripts/ab_tool.py check "$f" >/dev/null || { echo "FAIL check $f"; fail=1; }
  "$PY" scripts/ab_tool.py summary "$f" | grep -q "Плата:" || { echo "FAIL summary $f"; fail=1; }
  "$PY" scripts/ab_tool.py flow "$f" "$T/f.svg" && grep -q "<svg" "$T/f.svg" || { echo "FAIL flow $f"; fail=1; }
  "$PY" scripts/ab_tool.py tps "$f" --vin 24 --out "$T/c.json" && grep -q '"board"' "$T/c.json" || { echo "FAIL tps $f"; fail=1; }
done
[ "$fail" = 0 ] && echo "ok   ab_tool on $(ls examples/*.json | wc -l) examples"
n=$("$PY" scripts/ab_tool.py ids 3 | sort -u | wc -l); [ "$n" = 3 ] && echo "ok   ids unique" || { echo "FAIL ids"; fail=1; }
# regression (Oct 2026): references inside Web Console and the Update Interval minimum must be caught
"$PY" - "$T" <<'PY' || fail=1
import json, sys, subprocess
T = sys.argv[1]
p = json.load(open("examples/accesscontrol6.json", encoding="utf-8"))
for f in p["features"]:
    if f["id"] == "stg":
        f["settings"]["SETTINGS"] = [x for x in f["settings"]["SETTINGS"] if x["settings"]["SETTINGID"] != "lock_activation_duration"]
    if f["id"] == "commands":
        f["settings"]["COMMANDS"] = []
    if f["id"] == "global_vars":
        f["settings"]["INTERVAL"] = "0.1"
json.dump(p, open(T + "/bad.json", "w"))
out = subprocess.run([sys.executable, "scripts/ab_tool.py", "check", T + "/bad.json"], capture_output=True, text=True, encoding="utf-8").stdout
need = ["SETTINGID=lh8ofi29e1ipb5hcn9n", "VARIABLE=lh8r5ppokuuzhvk8hbh", "INTERVAL=0.1"]
miss = [n for n in need if n not in out]
print("ok   panel/interval regression" if not miss else "FAIL panel/interval regression: " + ", ".join(miss))
sys.exit(1 if miss else 0)
PY
# editor registry (data/registry.json): unknown block, missing port, bad option, missing feature must be caught
"$PY" - "$T" <<'PY' || fail=1
import json, sys, subprocess
T = sys.argv[1]
p = json.load(open("examples/accesscontrol6.json", encoding="utf-8"))
F = p["features"]
F[:] = [f for f in F if f["id"] != "timers"]
for f in F:
    if f["id"] == "node_beep":
        f["settings"]["CANINT"] = "maybe"
link = next(f for f in F if f["id"] == "node_link")
link["settings"]["SOURCE_PORT"] = "no_such_port"
F.append({"id": "node_bogus", "settings": {"ID": "lzz00000000000bogus", "X": 0, "Y": 0}})
json.dump(p, open(T + "/reg.json", "w"))
out = subprocess.run([sys.executable, "scripts/ab_tool.py", "check", T + "/reg.json"], capture_output=True, text=True, encoding="utf-8").stdout
need = ["неизвестный тип блока node_bogus", "'no_such_port'", "CANINT='maybe'", "нужна feature timers"]
miss = [n for n in need if n not in out]
print("ok   registry checks" if not miss else "FAIL registry checks: " + ", ".join(miss))
lk = subprocess.run([sys.executable, "scripts/ab_tool.py", "lookup", "node_pid"], capture_output=True, text=True, encoding="utf-8").stdout
ok = "setpoint:float" in lk
print("ok   lookup" if ok else "FAIL lookup")
sys.exit(1 if miss or not ok else 0)
PY
# generated-code pitfalls: LINE_NUMBER must be a number, comparison operators of Tibbo BASIC only
"$PY" - "$T" <<'PY' || fail=1
import json, sys, subprocess
T = sys.argv[1]
base = json.load(open("examples/accesscontrol6.json", encoding="utf-8"))
base["device"] = "TPP3W(G2)"
def run(line, op):
    p = json.loads(json.dumps(base))
    F = p["features"]
    cmp_ = next(f for f in F if f["id"] == "node_comparison")
    for a in cmp_["settings"]["ARGUMENTS"]:
        if a["settings"]["TARGETPARAM"] == "operator":
            a["settings"]["ARGVALUE"] = op
    dl = {"id": "node_digital_line_set", "settings": {"ID": "lzz00000000000line1", "DISPLAY_NAME": "", "FEATURE": "", "X": 0, "Y": 0,
          "INPUTS": [], "OUTPUTS": [], "GROUP": "", "ARGUMENTS": [], "LINE_NUMBER": line, "VALUE": "0"}}
    F.append(dl)
    F.append({"id": "node_link", "settings": {"ID": "lzz00000000000link1", "SOURCE": "", "SOURCE_FEATURE": cmp_["settings"]["ID"],
              "SOURCE_PORT": "true_output", "TARGET": "", "TARGET_FEATURE": dl["settings"]["ID"], "TARGET_PORT": "digital_line_set", "ARGUMENTS": []}})
    json.dump(p, open(T + "/cg.json", "w", encoding="utf-8"))
    r = subprocess.run([sys.executable, "scripts/ab_tool.py", "check", T + "/cg.json"], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout
rc_bad, out_bad = run("PL_IO_NUM_48", "==")
rc_ok, out_ok = run("48", "=")
_, out_warn = run("5", "<>")
ok = (rc_bad == 1 and "LINE_NUMBER='PL_IO_NUM_48'" in out_bad and "оператор '=='" in out_bad
      and rc_ok == 0 and "LINE_NUMBER" not in out_ok and "оператор" not in out_ok
      and "линия 5 - блок не переводит линию в выход" in out_warn)
print("ok   codegen checks (LINE_NUMBER, operator)" if ok else "FAIL codegen checks\n" + out_bad + out_ok + out_warn)
sys.exit(0 if ok else 1)
PY
# a cp1251 console (Windows) must not break the output: run without PYTHONUTF8
encfail=0
for cmd in "lookup node_math_compound" "check examples/sprinkler5.json" "summary examples/sprinkler5.json"; do
  env -u PYTHONUTF8 PYTHONIOENCODING=cp1251 "$PY" scripts/ab_tool.py $cmd >/dev/null 2>"$T/err" || { echo "FAIL cp1251 console: ab_tool.py $cmd"; cat "$T/err"; encfail=1; }
done
env -u PYTHONUTF8 PYTHONIOENCODING=cp1251 "$PY" scripts/ab_api.py >/dev/null 2>"$T/err"; [ $? = 2 ] || { echo "FAIL cp1251 console: ab_api.py"; cat "$T/err"; encfail=1; }
grep -q UnicodeEncodeError "$T/err" && { echo "FAIL cp1251 console: ab_api.py"; encfail=1; }
[ "$encfail" = 0 ] && echo "ok   non-UTF-8 console" || fail=1
TPS=$(ls ../tibbo-firmware/scripts/tps_check.py 2>/dev/null)
if [ -n "$TPS" ]; then
  "$PY" scripts/ab_tool.py tps examples/ModbusMQTTGateway.json --vin 24 --out "$T/m.json"
  "$PY" "$TPS" check "$T/m.json" >/dev/null && echo "ok   bridge to tps_check" || { echo "FAIL bridge"; fail=1; }
fi
# AppBlocks canvas warnings (yellow triangles, not in Problems): #10 with #20 is "Incorrect pair", #29 needs #00-3
"$PY" - "$T" <<'PY' || fail=1
import json, sys, subprocess
T = sys.argv[1]
def run(mod):
    p = json.load(open("examples/accesscontrol6.json", encoding="utf-8"))
    mod(p)
    json.dump(p, open(T + "/hw.json", "w"))
    return subprocess.run([sys.executable, "scripts/ab_tool.py", "check", T + "/hw.json"], capture_output=True, text=True, encoding="utf-8").stdout
def pair20(p):
    p["features"] = [f for f in p["features"] if f["id"] != "tibbit_18"]
    p["features"].append({"id": "tibbit_20", "settings": {"ID": "hwtest20", "SOCKET": "10", "TIBBIT": "20", "PLATFORM": ""}})
def sensor29(p):
    p["features"].append({"id": "tibbit_29", "settings": {"ID": "hwtest29", "SOCKET": "10", "TIBBIT": "29", "PLATFORM": ""}})
out = run(pair20) + run(sensor29) + run(lambda p: None)
ok = "#20 рядом с #10" in out and "нужен #00_3" in out and out.count("плата:") == 2
print("ok   hardware canvas warnings" if ok else "FAIL hardware canvas warnings\n" + out)
sys.exit(0 if ok else 1)
PY
# compile pitfalls (Smart Greenhouse, Oct 2026) and runtime limits (Greenhouse 2, Nov 2026): STG setting ref, Modbus name conflict,
# #05 port autovar, 1-Wire tables, relay boot level, MQTT payload > 255, Delay with an expression, legacy WIDGETS, open web console
"$PY" - "$T" <<'PY' || fail=1
import json, sys, subprocess
T = sys.argv[1]
base = json.load(open("examples/greenhouse2_tpp3.json", encoding="utf-8"))
def run(mod):
    p = json.loads(json.dumps(base)); mod(p)
    json.dump(p, open(T + "/gh.json", "w", encoding="utf-8"))
    r = subprocess.run([sys.executable, "scripts/ab_tool.py", "check", T + "/gh.json"], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout
F = lambda p, k: next(f for f in p["features"] if f["id"] == k)
gv = lambda p: F(p, "global_vars")["settings"]
def stg_ref(p):
    st = next(x["settings"] for x in F(p, "stg")["settings"]["SETTINGS"] if x["settings"]["SETTINGID"] == "pump_sec")
    av = next(v["settings"]["ID"] for v in gv(p)["AUTOVARS"] if v["settings"]["FEATURE"] == st["ID"])
    for f in p["features"]:
        if f["id"] == "node_time_delay" and f["settings"].get("DURATION") == "{{$" + av + "}}":
            f["settings"]["DURATION"] = "{{$" + st["ID"] + "}}"
def name_conflict(p):
    F(p, "modbus_master")["settings"]["MODBUSDEVICES"][0]["settings"]["NAME"] = "SOIL1"
def no_port_var(p):
    t = F(p, "tibbit_05")["settings"]["ID"]
    gv(p)["AUTOVARS"] = [v for v in gv(p)["AUTOVARS"] if v["settings"]["FEATURE"] != t]
def onewire(p):
    F(p, "unowiresensors")["settings"]["SENSORS"] = [{"id": "unowiresensor", "settings": {"ID": "ghtestow1", "NAME": "probe",
        "SENSORTYPE": "DS18B20", "TIBBIT": "", "CHANNEL": "1", "VALUES": []}}]
def relay0(p):
    t = F(p, "tibbit_06")["settings"]["ID"]
    for v in gv(p)["AUTOVARS"]:
        if v["settings"]["FEATURE"] == t:
            v["settings"]["DEFAULT"] = "0"
def long_mqtt(p):
    for f in p["features"]:
        if f["id"] == "node_mqtt_pub":
            for a in f["settings"]["ARGUMENTS"]:
                if a["settings"]["TARGETPARAM"] == "publish_data" and "soil1=" in a["settings"]["ARGVALUE"]:
                    a["settings"]["ARGVALUE"] += ";" + a["settings"]["ARGVALUE"] + ";comment=" + "x" * 60
def delay_expr(p):
    st = next(x["settings"] for x in F(p, "stg")["settings"]["SETTINGS"] if x["settings"]["SETTINGID"] == "pump_sec")
    av = next(v["settings"]["ID"] for v in gv(p)["AUTOVARS"] if v["settings"]["FEATURE"] == st["ID"])
    next(f for f in p["features"] if f["id"] == "node_time_delay")["settings"]["DURATION"] = "{{$" + av + "}} - 2"
def legacy_widgets(p):
    wd = F(p, "web_dashboard")["settings"]
    wd["WIDGETS"] = wd["WIDGET_GROUPS"][0]["settings"]["WIDGETS"]; wd["WIDGET_GROUPS"] = []
def open_console(p):
    w = F(p, "web_dashboard")["settings"]["ID"]
    p["features"] = [f for f in p["features"] if not (f["id"] == "linked_setting" and f["settings"].get("FEATURE") == w)]
rc0, out0 = run(lambda p: None)
cases = [(stg_ref, "это ID настройки STG"), (name_conflict, "Name conflict: soil1"), (no_port_var, "нет авто-переменной порта"),
         (onewire, "OWSENS"), (relay0, "реле активно по LOW"), (long_mqtt, "строка Tibbo BASIC вмещает 255"),
         (delay_expr, "умножится только последнее слагаемое"), (legacy_widgets, "старом поле WIDGETS"), (open_console, "веб-консоль открыта")]
bad = [m for f, m in cases if m not in run(f)[1]]
ok = rc0 == 0 and not bad and "ОШИБКА" not in out0
print("ok   compile pitfalls and runtime limits (greenhouse2)" if ok else "FAIL compile pitfalls: " + ", ".join(bad) + "\n" + out0)
sys.exit(0 if ok else 1)
PY
"$PY" - "$T" <<'PY' || fail=1
import json, subprocess, sys
T = sys.argv[1]
reg = json.load(open("data/registry.json", encoding="utf-8"))
def probe(example, src_type):
    d = json.load(open("examples/" + example, encoding="utf-8"))
    src = [f for f in d["features"] if f["id"] == src_type][0]
    port = list(reg["nodes"][src_type]["out"])[0]
    d["features"].append({"id": "node_sqrt", "settings": {"ID": "probe01", "DISPLAY_NAME": "", "FEATURE": "", "X": 0, "Y": 900,
                          "INPUTS": [], "OUTPUTS": [], "GROUP": "", "ARGUMENTS": [], "VARIABLE": ""}})
    d["features"].append({"id": "node_link", "settings": {"ID": "probe02", "SOURCE": "", "SOURCE_FEATURE": src["settings"]["ID"],
                          "SOURCE_PORT": port, "TARGET": "", "TARGET_FEATURE": "probe01", "TARGET_PORT": "exec", "ARGUMENTS": []}})
    json.dump(d, open(T + "/rt.json", "w", encoding="utf-8"), ensure_ascii=False)
    r = subprocess.run([sys.executable, "scripts/ab_tool.py", "check", T + "/rt.json"], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout
rc_t, out_t = probe("sprinkler5.json", "node_cron_event")          # TiOS project
rc_z, out_z = probe("ModbusMQTTGateway.json", "node_system")       # Zephyr project
ok = rc_t == 1 and "только в среде Zephyr" in out_t and "только в среде" not in out_z
print("ok   Zephyr-only block in a TiOS project is an error" if ok else "FAIL runtime of blocks: rc=%s\n%s\n%s" % (rc_t, out_t[-600:], out_z[-400:]))
sys.exit(0 if ok else 1)
PY
rm -rf "$T"; exit $fail
