#!/usr/bin/env python3
"""Dev tool: (re)create skills/appblocks/recipes/*.json - small complete AppBlocks projects for TiOS.

Every recipe starts from the same empty project (Tibbo's "Sprinkler" tutorial with its logic, Tibbits and data removed,
board TPP2W(G2), power #10 + #18) and adds Tibbits, variables and blocks with the helpers below. IDs are derived from
the recipe name, so a rebuild gives the same files. After building run tools/check_ab_recipes.py: ab_tool.py check,
Tibbo's code generator and Tibbo's compiler.

Usage: python3 tools/build_ab_recipes.py
"""
import copy
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AB = os.path.join(ROOT, "skills", "appblocks")
OUT = os.path.join(AB, "recipes")
REG = json.load(open(os.path.join(AB, "data", "registry.json"), encoding="utf-8"))["nodes"]
B36 = "0123456789abcdefghijklmnopqrstuvwxyz"


class Project:
    def __init__(self, name, title, about):
        self.name, self.n = name, 0
        d = json.load(open(os.path.join(AB, "examples", "sprinkler5.json"), encoding="utf-8"))
        keep = []
        for f in d["features"]:
            k, s = f["id"], f["settings"]
            if k.startswith("node_") or k in ("tibbit_03_1", "tibbit_20", "variable"):
                continue
            if k == "timers":
                s["TIMERS"] = []
            elif k == "cron":
                s["SCHEDULES"] = []
            elif k == "tbl":
                s["TABLES"] = []
            elif k == "global_vars":
                s["VARS"] = []
                s["AUTOVARS"] = [v for v in s["AUTOVARS"] if v["settings"]["FEATURE_SETTING"] == "SETTINGID"]
            elif k == "lcd":           # no display in these recipes
                s["ENABLED"] = "0"
                for scr in s["SCREENS"]:
                    scr["settings"]["WIDGETS"] = []
            elif k == "web_dashboard":
                s.update({"WIDGETS": [], "TABLES": [], "WIDGET_GROUPS": [], "DASHBOARD_TITLE": title, "ENABLED": "0"})
            elif k == "bt":            # Bluetooth setup is not part of the recipes
                s["ENABLED"] = "0"
                s["DEVICENAME"] = title[:20]
            elif k == "luis":          # LUIS needs Bluetooth: with bt off and luis on the firmware does not compile
                s["ENABLED"] = "0"
                s["BTENABLED"] = "0"
            elif k == "general":
                s["DEVICE_NAME"] = name.replace("-", "_")
            keep.append(f)
        d["features"] = keep
        d.update({"name": title, "description": about, "shortDescription": about[:120]})
        d.pop("id", None)
        self.d = d
        self.x = 0

    # ---- helpers
    def id(self):
        self.n += 1
        h = int(hashlib.sha1(("%s/%d" % (self.name, self.n)).encode()).hexdigest(), 16)
        s = ""
        while len(s) < 17:
            h, r = divmod(h, 36)
            s += B36[r]
        return "r" + s

    def feat(self, k):
        return next(f["settings"] for f in self.d["features"] if f["id"] == k)

    def add(self, k, **settings):
        s = {"ID": self.id()}
        s.update(settings)
        self.d["features"].append({"id": k, "settings": s})
        return s["ID"]

    def autovar(self, name, datatype, feature, setting, label, default, lo=0, hi=1):
        vid = self.id()
        self.feat("global_vars")["AUTOVARS"].append({"id": "variable", "settings": {
            "ID": vid, "VARNAME": name, "DATATYPE": datatype, "NAME": label, "FEATURE": feature, "FEATURE_SETTING": setting,
            "MINIMUM": lo, "MAXIMUM": hi, "DEFAULT": str(default), "POLL_INTERVAL": ""}})
        return vid

    def var(self, name, datatype="float", default="0", lo="", hi=""):
        vid = self.id()
        self.feat("global_vars")["VARS"].append({"id": "variable", "settings": {
            "ID": vid, "VARNAME": name, "DATATYPE": datatype, "NAME": "", "FEATURE": "", "FEATURE_SETTING": "",
            "MINIMUM": lo, "MAXIMUM": hi, "DEFAULT": str(default), "POLL_INTERVAL": ""}})
        return vid

    def setting(self, sid, title, default, lo, hi):
        """A value kept in EEPROM (survives power-off). Returns the ID of its variable - use that one in logic."""
        st = self.id()
        self.feat("stg")["SETTINGS"].append({"id": "stg_setting", "settings": {
            "ID": st, "GENERAL": "", "ADVANCED": "", "SETTINGID": sid, "NAME": title, "STORAGE": "E", "SETTINGTYPE": "float",
            "DATATYPE": "F", "MIN": lo, "MAX": hi, "INITIALIZE": "A", "DEFAULT": str(default)}})
        return self.autovar(sid, "float", st, "SETTINGID", "", default, lo, hi)

    def text_setting(self, sid, title, default, maxlen=32):
        st = self.id()
        self.feat("stg")["SETTINGS"].append({"id": "stg_setting", "settings": {
            "ID": st, "GENERAL": "", "ADVANCED": "", "SETTINGID": sid, "NAME": title, "STORAGE": "E", "SETTINGTYPE": "string",
            "DATATYPE": "S", "MIN": "", "MAX": maxlen, "INITIALIZE": "A", "DEFAULT": default}})
        self.autovar(sid, "string", st, "SETTINGID", "Setting", default, "", maxlen)
        return st

    def tibbit(self, model, socket, connector=None, **fields):
        """connector "20" (nine terminals) is two sockets wide: one in S2 serves the modules in S1 and S3 (S6: S5 and S7)."""
        s = {"SOCKET": str(socket), "TIBBIT": model, "PLATFORM": ""}
        s.update(fields)
        tid = self.add("tibbit_" + model, **s)
        if connector:
            cs = {1: 2, 3: 2, 5: 6, 7: 6}[socket] if connector == "20" else socket + 1
            if not any(f["id"] == "tibbit_" + connector and f["settings"]["SOCKET"] == str(cs) for f in self.d["features"]):
                self.add("tibbit_" + connector, SOCKET=str(cs), TIBBIT=connector, PLATFORM="")
        return tid

    def relays(self, socket, name1, name2):
        """#03_1 with connector #20. Relays are active LOW: 1 = off (the default), 0 = on."""
        t = self.tibbit("03_1", socket, "20", NAME="T03_1_S%d" % socket, L1NAME=name1, L2NAME=name2)
        return (self.autovar(name1, "boolean", t, "L1NAME", "Tibbit 03_1", 1),
                self.autovar(name2, "boolean", t, "L2NAME", "Tibbit 03_1", 1))

    def inputs54(self, socket, names):
        """#54 (four dry contacts) with connector #20: a closed contact reads 0, an open one 1."""
        f = {"NAME": "T54_S%d" % socket, "INTEDGE": "INT_EDGE_LOW"}
        for i, n in enumerate(names, 1):
            f["L%dNAME" % i], f["L%dMODE" % i] = n, "0"
        t = self.tibbit("54", socket, "20", **f)
        return [self.autovar(n, "boolean", t, "L%dNAME" % i, "Tibbit 54", 1) for i, n in enumerate(names, 1)]

    def node(self, kind, args=None, x=None, y=0, **settings):
        if kind not in REG:
            raise SystemExit("no such block: " + kind)
        if REG[kind].get("runtimes") is not None and "tios" not in REG[kind]["runtimes"]:
            raise SystemExit("%s is not a TiOS block" % kind)
        if x is None:
            x = self.x
        self.x = x + 300
        s = {"DISPLAY_NAME": "", "FEATURE": "", "X": x, "Y": y, "INPUTS": [], "OUTPUTS": [], "GROUP": "",
             "ARGUMENTS": [{"id": "node_argument", "settings": {"ID": self.id(), "ARGVALUE": str(v), "TARGETPARAM": k}}
                           for k, v in (args or {}).items()]}
        s.update(settings)
        return self.add(kind, **s)

    def kind(self, node_id):
        return next(f["id"] for f in self.d["features"] if f["settings"].get("ID") == node_id)

    def link(self, a, b, out=None, inp=None):
        outs, ins = list(REG[self.kind(a)]["out"]), list(REG[self.kind(b)]["in"])
        out = out or (outs[0] if len(outs) == 1 else None)
        inp = inp or (ins[0] if len(ins) == 1 else None)
        if out not in outs or inp not in ins:
            raise SystemExit("%s: link %s.%s -> %s.%s: ports are %s / %s" % (self.name, self.kind(a), out, self.kind(b), inp, outs, ins))
        self.add("node_link", SOURCE="", SOURCE_FEATURE=a, SOURCE_PORT=out, TARGET="", TARGET_FEATURE=b, TARGET_PORT=inp, ARGUMENTS=[])

    def chain(self, *nodes):
        for a, b in zip(nodes, nodes[1:]):
            self.link(a, b)

    def set(self, var, value, y=0, x=None):
        return self.node("node_variable_set", {"value": value}, x=x, y=y, VARIABLE=var)

    def cmp(self, a, op, b, y=0, x=None):
        return self.node("node_comparison", {"operand1": a, "operator": op, "operand2": b}, x=x, y=y)

    def boot(self):
        s = self.node("node_system", x=0, y=-200)
        f = next(f["settings"] for f in self.d["features"] if f["settings"]["ID"] == s)
        port = lambda name, pid: {"id": "node_port", "settings": {"ID": self.id(), "NAME": name, "PORTID": pid, "PARAMS": []}}
        f["INPUTS"] = [port("Halt", "sys.halt"), port("Reboot", "sys.reboot")]
        f["OUTPUTS"] = [port("Boot Complete", "boot"), port("System tick", "on_sys_timer")]
        return s

    def save(self, meta):
        os.makedirs(OUT, exist_ok=True)
        json.dump(self.d, open(os.path.join(OUT, self.name + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        meta.update({"file": self.name + ".json", "title": self.d["name"], "about": self.d["description"],
                     "board": self.d["device"], "runtime": self.d["runtime"]})
        return meta


V = lambda vid: "{{$%s}}" % vid          # the value of a variable inside an argument


def r01_button_relay():
    p = Project("01-button-relay", "Кнопка переключает реле",
                "Кнопка MD на плате включает и выключает реле 1. Показывает: событие, условие, запись в переменную реле.")
    lamp, _ = p.relays(1, "lamp", "relay2")
    b = p.node("node_button_released", x=0, y=0)
    c = p.cmp(V(lamp), "=", "1")                 # 1 = сейчас выключено
    p.link(b, c)
    p.link(c, p.set(lamp, 0, y=-100), out="true_output")
    p.link(c, p.set(lamp, 1, y=100, x=600), out="false_output")
    return p.save({"tibbits": "#03_1 в S1 + #20 в S2, питание #10 в S11 + #18 в S12",
                   "blocks": "On Button Released, Comparison, Variable Set",
                   "try": "нажмите и отпустите кнопку MD - реле щёлкнет; ещё раз - выключится"})


def r02_blink():
    p = Project("02-blink-interval", "Мигалка: реле по интервалу",
                "Реле 1 переключается каждые 5 секунд. Показывает: периодическое действие блоком On Time Period.")
    lamp, _ = p.relays(1, "lamp", "relay2")
    t = p.node("node_time_interval", x=0, y=0, INTERVAL="5")
    c = p.cmp(V(lamp), "=", "1")
    p.link(t, c)
    p.link(c, p.set(lamp, 0, y=-100), out="true_output")
    p.link(c, p.set(lamp, 1, y=100, x=600), out="false_output")
    return p.save({"tibbits": "#03_1 в S1 + #20 в S2, питание #10 в S11 + #18 в S12",
                   "blocks": "On Time Period, Comparison, Variable Set",
                   "try": "после включения реле щёлкает каждые 5 секунд; период - поле Interval блока On Time Period"})


def r03_input_delay():
    p = Project("03-input-delay-off", "Свет по датчику с задержкой выключения",
                "Контакт датчика замкнулся - свет включается и горит ещё 30 секунд после размыкания. Время хранится в "
                "настройке и переживает выключение питания. Показывает: вход «сухой контакт», Delay, настройку STG.")
    light, _ = p.relays(1, "light", "relay2")
    sensor = p.inputs54(3, ["sensor", "in2", "in3", "in4"])[0]
    hold = p.setting("HOLD", "Задержка выключения, с", 30, 1, 3600)
    ch = p.node("node_variable_changed", x=0, y=0, VARIABLE=sensor)
    c = p.cmp(V(sensor), "=", "0")               # 0 = контакт замкнут
    p.link(ch, c)
    p.link(c, p.set(light, 0, y=-100), out="true_output")
    d = p.node("node_time_delay", x=600, y=100, DURATION=V(hold))
    p.link(c, d, out="false_output")
    c2 = p.cmp(V(sensor), "=", "1", y=100)       # за время задержки датчик мог сработать снова
    p.link(d, c2)
    p.link(c2, p.set(light, 1, y=100), out="true_output")
    return p.save({"tibbits": "#03_1 в S1, #54 в S3, один разъём #20 в S2 на оба (он занимает S2 и S4), питание #10 в S11 + #18 в S12",
                   "blocks": "On Variable Changed, Comparison, Delay, Variable Set; настройка HOLD",
                   "try": "замкните вход 1 Tibbit #54 на общий - свет включится; разомкните - погаснет через 30 с"})


def r04_modbus_thermostat():
    p = Project("04-modbus-thermostat", "Термостат по датчику Modbus RTU",
                "Раз в секунду читает температуру с датчика Modbus RTU (адрес 1, регистр 0, десятые доли градуса) и держит "
                "её между порогами: ниже нижнего - нагрев включён, выше верхнего - выключен. Нет связи с датчиком - нагрев "
                "выключается. Показывает: Modbus Master, гистерезис, безопасное состояние при потере связи.")
    heat, _ = p.relays(3, "heater", "relay2")
    port = p.tibbit("05", 1, "20", NAME="T05_S1", BAUD="9600", FLOWCONTROL="0", PARITY="0", BITS="1", TXBUF="1", RXBUF="1")
    p.autovar("T05_S1", "byte", port, "NAME", "", 1, 0, 255)
    reg = p.id()
    p.feat("modbus_master")["MODBUSDEVICES"].append({"id": "modbus_device", "settings": {
        "ID": p.id(), "NAME": "mb_sensor", "PROTOCOL": "modbus_RTU", "SERIAL_PORT": port, "DEVICEID": "1", "DEVICEIP": "1.0.0.1",
        "DEVICEPORT": "502", "POLL_FAIL_BACKOFF_THRESHOLD": "3", "POLL_FAIL_BACKOFF_MS": "10000",
        "REGISTERS": [{"id": "modbus_device_register", "settings": {
            "ID": reg, "ADDRESS": "0", "LENGTH": "1", "DATATYPE": "ReadHoldingRegisters", "VARTYPE": "INTEGER", "NAME": "temperature",
            "MULTIPLIER": "0.1", "ENDIAN": "BIG"}}]}})
    temp = p.autovar("temperature", "float", reg, "NAME", "Modbus Device Register", 0, "", "")
    low = p.setting("TLOW", "Включить нагрев ниже, °C", 20, -40, 100)
    high = p.setting("THIGH", "Выключить нагрев выше, °C", 22, -40, 100)
    ch = p.node("node_variable_changed", x=0, y=0, VARIABLE=temp)
    c1 = p.cmp(V(temp), "<", V(low))
    p.link(ch, c1)
    p.link(c1, p.set(heat, 0, y=-100), out="true_output")
    c2 = p.cmp(V(temp), ">", V(high), y=100, x=600)
    p.link(c1, c2, out="false_output")
    p.link(c2, p.set(heat, 1, y=100), out="true_output")
    to = p.node("node_modbus_timeout", x=0, y=400)
    p.link(to, p.set(heat, 1, y=400))            # нет связи - выключить
    return p.save({"tibbits": "#05 в S1, #03_1 в S3, один разъём #20 в S2 на оба (он занимает S2 и S4), питание #10 в S11 + #18 в S12",
                   "blocks": "On Variable Changed, Comparison, Variable Set, On Modbus Timeout; Modbus Master, настройки TLOW и THIGH",
                   "try": "подключите датчик с адресом 1, 9600 8N1; адрес, регистр и множитель - в Modbus Master"})


def r05_mqtt():
    p = Project("05-mqtt-relay", "MQTT: команды реле и телеметрия",
                "Подключается к брокеру MQTT, выполняет команды on и off из топика tibbo/demo/cmd и раз в 30 секунд "
                "публикует состояние реле в tibbo/demo/state. Показывает: подписку, публикацию, адрес брокера в настройках.")
    lamp, _ = p.relays(1, "lamp", "relay2")
    m = p.feat("mqtt")
    topic = p.id()
    m.update({"ENABLED": "1", "MQTT_APP_CLIENT_ID": "tibbo_demo", "MQTT_NAME": "", "MQTT_PASSWORD": "", "MQTT_SERVER_HOST": "192.168.1.100",
              "MQTT_DEBUG_PRINT": "0",
              "TOPICS": [{"id": "mqtt_topic", "settings": {"ID": topic, "TOPIC_NAME": "tibbo/demo/cmd", "NAME": "cmd", "QOS": "QOS_AT_MOST_ONCE"}}]})
    p.add("mqtt_lib")
    sub = p.node("node_mqtt_sub", x=0, y=0, TOPIC=topic)
    c_on = p.cmp("{{$data}}", "=", "on", x=300, y=0)
    c_off = p.cmp("{{$data}}", "=", "off", x=300, y=200)
    p.link(sub, c_on)
    p.link(sub, c_off)
    p.link(c_on, p.set(lamp, 0, x=600, y=0), out="true_output")
    p.link(c_off, p.set(lamp, 1, x=600, y=200), out="true_output")
    t = p.node("node_time_interval", x=0, y=500, INTERVAL="30")
    pub = p.node("node_mqtt_pub", {"topic": "tibbo/demo/state", "publish_data": "lamp=" + V(lamp), "qos": "QOS_AT_MOST_ONCE",
                                   "retain": "false"}, x=300, y=500)
    p.link(t, pub)
    return p.save({"tibbits": "#03_1 в S1 + #20 в S2, питание #10 в S11 + #18 в S12",
                   "blocks": "On MQTT Message, Comparison, Variable Set, On Time Period, MQTT Publish; сервис MQTT",
                   "try": "укажите адрес брокера в MQTT → Server Host; отправьте on или off в tibbo/demo/cmd. "
                          "В state приходит lamp=0 (включено) или lamp=1 (выключено)"})


def r06_web_panel():
    p = Project("06-web-panel", "Веб-панель: переключатель и счётчик",
                "Страница на самом устройстве: переключатель управляет реле, карточка показывает время работы в секундах. "
                "Показывает: веб-панель, переменную для интерфейса отдельно от переменной реле.")
    lamp, _ = p.relays(1, "lamp", "relay2")
    want = p.var("lamp_on", "float", 0, 0, 1)
    up = p.var("uptime_s", "float", 0, 0, 4000000000)
    w = p.feat("web_dashboard")
    w.update({"ENABLED": "1", "WIDGET_GROUPS": [{"id": "widget_group", "settings": {"ID": p.id(), "GROUPID": "group1", "NAME": "Панель", "WIDGETS": [
        {"id": "switch_widget", "settings": {"ID": p.id(), "X": 0, "Y": 0, "W": 2, "H": 3, "VISIBLE": "1", "VARIABLE": want, "LABEL": "Свет",
                                             "OFF_VALUE": "0", "ON_VALUE": "1", "OFF_LABEL": "Выкл", "ON_LABEL": "Вкл"}},
        {"id": "card_widget", "settings": {"ID": p.id(), "X": 2, "Y": 0, "W": 2, "H": 3, "VISIBLE": "1", "VARIABLE": up, "LABEL": "Работает, с",
                                           "DECIMAL_PLACES": "0", "COLOR": "#1976d2", "TEXT_COLOR": "#000000", "LABEL_FONT_SIZE": 14, "FONT_SIZE": 40}}]}}]})
    pw = p.text_setting("WBPWD", "Пароль веб-панели (пользователь admin)", "tibbo")
    p.add("linked_setting", SETTINGID="PASSWORD", LINKEDSETTING=pw, FEATURE=w["ID"])
    ch = p.node("node_variable_changed", x=0, y=0, VARIABLE=want)
    c = p.cmp(V(want), "=", "1")
    p.link(ch, c)
    p.link(c, p.set(lamp, 0, y=-100), out="true_output")
    p.link(c, p.set(lamp, 1, y=100, x=600), out="false_output")
    t = p.node("node_time_interval", x=0, y=400, INTERVAL="1")
    p.link(t, p.set(up, V(up) + "+1", x=300, y=400))
    return p.save({"tibbits": "#03_1 в S1 + #20 в S2, питание #10 в S11 + #18 в S12",
                   "blocks": "On Variable Changed, Comparison, Variable Set, On Time Period; веб-панель",
                   "try": "откройте в браузере адрес устройства (выданный DHCP), пользователь admin, пароль tibbo - "
                          "сразу смените его в настройке WBPWD"})


if __name__ == "__main__":
    index = [f() for f in (r01_button_relay, r02_blink, r03_input_delay, r04_modbus_thermostat, r05_mqtt, r06_web_panel)]
    json.dump({"recipes": index}, open(os.path.join(OUT, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    L = ["# Готовые проекты AppBlocks для TiOS", "",
         "Шесть небольших законченных проектов в папке `recipes/`. Каждый проходит `ab_tool.py check` без ошибок, проверку платы "
         "`tps_check.py`, генератор кода Tibbo и собирается компилятором Tibbo (`tools/check_ab_recipes.py` в репозитории). "
         "В редакторе AppBlocks (вкладка Problems) и на устройстве они не открывались - попроси пользователя проверить.", "",
         "**Как пользоваться.** Новый проект не пиши с нуля: возьми ближайший рецепт, скопируй файл и меняй копию скриптом "
         "(правила - format.md §4). Все рецепты - плата TPP2W(G2), среда TiOS, питание 12 В через #10 в S11 и #18 в S12; "
         "Bluetooth и LUIS выключены, веб-панель включена только в рецепте 06. Плату меняй полем `device` до добавления Tibbit. "
         "В веб-чате файлы лежат в `tibbo-tools.zip` (папка `appblocks/recipes/`).", "",
         "| Файл | Что делает | Tibbit | Блоки и сервисы | Как проверить на устройстве |", "|---|---|---|---|---|"]
    for it in index:
        L.append("| `recipes/%s` | **%s.** %s | %s | %s | %s |" % (it["file"], it["title"], it["about"], it["tibbits"], it["blocks"], it["try"]))
    L += ["", "## Что в них стоит перенять", "",
          "- **Реле активны по LOW.** У переменных реле значение по умолчанию 1 (выключено), включение - запись 0. В MQTT и на "
          "панель отдавай отдельную переменную с понятным смыслом (рецепт 06: `lamp_on`), а не переменную линии.",
          "- **Один разъём #20 на два модуля.** #20 занимает два сокета (S2 и S4): он один обслуживает модули в S1 и S3 "
          "(рецепты 03 и 04). Второй #20 в S4 - ошибка раскладки.",
          "- **Безопасное состояние.** Рецепт 04 выключает нагрев по On Modbus Timeout: без связи с датчиком выход не остаётся включённым.",
          "- **То, что должно пережить выключение питания, - в настройках STG** (HOLD, TLOW, THIGH), а в логике используется "
          "авто-переменная настройки.",
          "- **Delay принимает число или одну переменную** (рецепт 03: `{{$HOLD}}`), выражение туда писать нельзя.",
          "- **Пароль веб-панели - через настройку** (рецепт 06: `WBPWD`, по умолчанию `tibbo` - скажи пользователю сменить).",
          "- **LUIS без Bluetooth не собирается**: `luis.ENABLED = 1` при `bt.ENABLED = 0` даёт в boot.tbs ошибку "
          "`undeclared identifier 'BT_NAME'`. Выключай оба или включай оба.", ""]
    open(os.path.join(AB, "references", "recipes.md"), "w", encoding="utf-8").write("\n".join(L))
    print("AppBlocks recipes built: %d -> %s" % (len(index), OUT))
