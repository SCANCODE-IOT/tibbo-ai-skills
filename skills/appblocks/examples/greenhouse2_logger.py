#!/usr/bin/env python3
"""Приёмник MQTT для проекта TOTAL SMART SCHOOL GREENHOUSE 2: телеметрия -> SQLite -> графики, тревоги, команды.

Установка на компьютер:
    1) брокер Mosquitto (mosquitto.org/download), в mosquitto.conf:
           listener 1883
           allow_anonymous true          (учебный стенд в закрытой сети; для рабочей установки - пароли)
    2) pip install paho-mqtt matplotlib

Запуск:
    python greenhouse2_logger.py log              слушать MQTT и писать в greenhouse2.db
    python greenhouse2_logger.py status           последнее состояние теплицы и последние тревоги
    python greenhouse2_logger.py events [N]       последние N событий и тревог (по умолчанию 30)
    python greenhouse2_logger.py plot [часы]      графики за N часов (по умолчанию 24) -> greenhouse2.png
    python greenhouse2_logger.py water1|water2|stop|unlock|auto_on    команда контроллеру

Что публикует контроллер (раз в 10 с, пять сообщений - каждое короче 255 символов, это предел строки Tibbo BASIC):
    greenhouse/tele/env    soil1, soil2, light1, light2, air_t, air_h
    greenhouse/tele/power  bus_v, current_a, power_w, energy_wh, water_ml
    greenhouse/tele/io     tank_empty, tank_low, no_leak, pump1, pump2, lamp1, lamp2, fan, auto_on, time_ok, air_fail
    greenhouse/tele/bed1   water1_today, cs1_active, cs1_cycles, cs1_wait, soil1_fail, bed1_fault
    greenhouse/tele/bed2   то же для грядки 2
    greenhouse/event       online, bed1_start, bed1_done, day_reset, stopped, unlocked, auto_on ...
    greenhouse/alarm       no_water, tank_low, leak, bed1_max_cycles, pump1_no_current, pump1_overcurrent,
                           soil1_offline, air_offline, time_not_synced ...
Формат значений: "ключ=значение;ключ=значение".

База: таблица tele - одна строка на пакет (пишется по приходу bed2, последнего сообщения пакета) с последними
известными значениями; events - события и тревоги. Старая база greenhouse.db от первой версии логгера не нужна;
если указать её в DB, недостающие столбцы добавятся сами.
"""
import sqlite3, sys
from datetime import datetime, timedelta

BROKER = "localhost"
DB = "greenhouse2.db"
TELE = {
    "env": ["soil1", "soil2", "light1", "light2", "air_t", "air_h"],
    "power": ["bus_v", "current_a", "power_w", "energy_wh", "water_ml"],
    "io": ["tank_empty", "tank_low", "no_leak", "pump1", "pump2", "lamp1", "lamp2", "fan", "auto_on", "time_ok", "air_fail"],
    "bed1": ["water1_today", "cs1_active", "cs1_cycles", "cs1_wait", "soil1_fail", "bed1_fault"],
    "bed2": ["water2_today", "cs2_active", "cs2_cycles", "cs2_wait", "soil2_fail", "bed2_fault"],
}
FIELDS = [f for keys in TELE.values() for f in keys]
# Реле #06 активны по LOW: pump1/pump2 приходят как уровень линии (0 = насос работает). В базу - 1 = работает.
INVERTED = {"pump1", "pump2"}
LAST_PART = "bed2"


def db():
    con = sqlite3.connect(DB)
    con.execute("create table if not exists tele (ts text)")
    have = {r[1] for r in con.execute("pragma table_info(tele)")}
    for f in FIELDS:                       # миграция: добавить недостающие столбцы, данные не теряются
        if f not in have:
            con.execute("alter table tele add column %s real" % f)
    con.execute("create table if not exists events (ts text, topic text, payload text)")
    con.execute("create index if not exists tele_ts on tele(ts)")
    con.commit()
    return con


def parse(payload: str) -> dict:
    out = {}
    for part in payload.split(";"):
        if "=" not in part:
            continue
        k, v = (x.strip() for x in part.split("=", 1))
        if k in FIELDS:
            try:
                out[k] = float(v)
                if k in INVERTED:
                    out[k] = 1.0 - out[k]
            except ValueError:
                pass
    return out


SNAP = {}


def save(con, topic: str, payload: str):
    ts = datetime.now().isoformat(timespec="seconds")
    parts = topic.split("/")
    if len(parts) >= 3 and parts[-2] == "tele":
        SNAP.update(parse(payload))
        if parts[-1] == LAST_PART:
            con.execute("insert into tele (ts, %s) values (?, %s)" % (",".join(FIELDS), ",".join("?" * len(FIELDS))),
                        [ts] + [SNAP.get(f) for f in FIELDS])
    else:
        con.execute("insert into events values (?,?,?)", (ts, topic, payload))
        if topic.endswith("/alarm"):
            print("!!! ТРЕВОГА:", payload)
    con.commit()


def run_logger():
    import paho.mqtt.client as mqtt
    con = db()

    def on_connect(c, userdata, flags, rc, *args):
        c.subscribe("greenhouse/#")
        print("подключено к брокеру, жду данные...")

    def on_message(c, userdata, msg):
        if msg.topic.endswith("/cmd"):
            return
        payload = msg.payload.decode("utf-8", "replace")
        save(con, msg.topic, payload)
        if not msg.topic.split("/")[-2:-1] == ["tele"]:
            print(msg.topic, payload)

    try:
        c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="greenhouse2-logger")
    except AttributeError:  # paho-mqtt 1.x
        c = mqtt.Client(client_id="greenhouse2-logger")
    c.on_connect, c.on_message = on_connect, on_message
    c.connect(BROKER, 1883, 60)
    c.loop_forever()


def send(cmd: str):
    import paho.mqtt.publish as publish
    publish.single("greenhouse/cmd", cmd, hostname=BROKER)
    print("отправлено:", cmd)


def status():
    con = db()
    row = con.execute("select ts, %s from tele order by ts desc limit 1" % ",".join(FIELDS)).fetchone()
    if not row:
        print("данных ещё нет")
        return
    v = dict(zip(["ts"] + FIELDS, row))
    yn = lambda x: "да" if x == 1 else ("нет" if x == 0 else "?")
    print("Данные на", v["ts"])
    print("  Почва: грядка 1 %.1f %%, грядка 2 %.1f %%;  воздух %.1f °C, %.0f %%" % (v["soil1"] or 0, v["soil2"] or 0, v["air_t"] or 0, v["air_h"] or 0))
    print("  Бак: пуст - %s, мало воды - %s; протечки нет - %s" % (yn(v["tank_empty"]), yn(v["tank_low"]), yn(v["no_leak"])))
    print("  Автоматика: %s; время синхронизировано: %s" % (yn(v["auto_on"]), {1: "да", 0: "нет", 2: "ещё не проверено"}.get(v["time_ok"], "?")))
    for n in (1, 2):
        print("  Грядка %d: вода сегодня %.0f мл, сеанс %s, циклов %d, ждать %d мин, авария насоса %s, датчик почвы %s" % (
            n, v["water%d_today" % n] or 0, yn(v["cs%d_active" % n]), v["cs%d_cycles" % n] or 0, v["cs%d_wait" % n] or 0,
            yn(v["bed%d_fault" % n]), "нет связи" if (v["soil%d_fail" % n] or 0) >= 3 else "на связи"))
    print("Последние тревоги:")
    for ts, t, p in con.execute("select * from events where topic like '%alarm' order by ts desc limit 5"):
        print("  ", ts, p)


def events(n=30):
    for ts, t, p in db().execute("select * from events order by ts desc limit ?", (n,)):
        print(ts, t.split("/")[-1].ljust(6), p)


def plot(hours: float = 24):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    con = db()
    since = (datetime.now() - timedelta(hours=hours)).isoformat(timespec="seconds")
    rows = con.execute("select ts, %s from tele where ts >= ? order by ts" % ",".join(FIELDS), (since,)).fetchall()
    if not rows:
        print("нет данных за период")
        return
    t = [datetime.fromisoformat(r[0]) for r in rows]
    col = {f: [r[i + 1] for r in rows] for i, f in enumerate(FIELDS)}
    fig, ax = plt.subplots(5, 1, figsize=(11, 13), sharex=True)
    ax[0].plot(t, col["soil1"], label="почва, грядка 1, %")
    ax[0].plot(t, col["soil2"], label="почва, грядка 2, %")
    ax[1].plot(t, col["water1_today"], label="вода грядке 1 за сутки, мл")
    ax[1].plot(t, col["water2_today"], label="вода грядке 2 за сутки, мл")
    ax[2].step(t, col["pump1"], where="post", label="насос 1 (1 = работает)")
    ax[2].step(t, [(x or 0) + 1.2 for x in col["pump2"]], where="post", label="насос 2 (смещён на 1,2)")
    ax[3].plot(t, col["air_t"], label="воздух, °C", color="tab:red")
    a3 = ax[3].twinx()
    a3.plot(t, col["light1"], label="свет 1, лк", color="tab:olive", alpha=.6)
    a3.plot(t, col["light2"], label="свет 2, лк", color="tab:green", alpha=.6)
    ax[4].plot(t, col["current_a"], label="ток нагрузок, А", color="tab:purple")
    for a in list(ax) + [a3]:
        a.legend(loc="upper left", fontsize=8)
    for a in ax:
        a.grid(alpha=.3)
    for ts, tp, p in con.execute("select * from events where ts >= ? and topic like '%alarm'", (since,)):
        for a in ax:
            a.axvline(datetime.fromisoformat(ts), color="red", alpha=.3, lw=1)
    fig.suptitle("TOTAL SMART SCHOOL GREENHOUSE 2: последние %g ч (красные линии - тревоги)" % hours)
    fig.tight_layout()
    fig.savefig("greenhouse2.png", dpi=110)
    print("сохранено greenhouse2.png,", len(rows), "точек")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "log"
    if cmd == "log":
        run_logger()
    elif cmd == "status":
        status()
    elif cmd == "events":
        events(int(sys.argv[2]) if len(sys.argv) > 2 else 30)
    elif cmd == "plot":
        plot(float(sys.argv[2]) if len(sys.argv) > 2 else 24)
    elif cmd in ("water1", "water2", "stop", "unlock", "auto_on"):
        send(cmd)
    else:
        print(__doc__)
