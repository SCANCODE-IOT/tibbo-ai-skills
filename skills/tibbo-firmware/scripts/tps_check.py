#!/usr/bin/env python3
"""TPS configuration checker: Tibbit placement, lines, UART/INT, connectors, PoE and power budget.

  python3 scripts/tps_check.py check config.json [--json] [--svg out.svg]
  python3 scripts/tps_check.py find "rs485 modbus"          # search the Tibbit catalog
  python3 scripts/tps_check.py board "TPP3W(G2)"             # socket capabilities of a board
  python3 scripts/tps_check.py tibbit 25                     # one Tibbit in full

config.json:
{
  "board": "TPP3W(G2)",                 // folder name in Platforms (TPP2W, TPP2W(G2), TPP2W(G3), TPP3W, TPP3W(G2), TPP3W(G3), TPP2N, TPP3N)
  "slots": {"S1": "05", "S2": "21", "S9": "25", "S10": "18", "S25": "23"},
                                        // a wide Tibbit (M2/C2/H1/H2) is listed once, at its first socket
                                        // per-slot override: "S9": {"model": "25", "vin": 24}
  "power": {"vin": 24,                  // voltage fed to power Tibbits (V)
            "ext5v_ma": 0},             // rating of an external regulated 5V PSU on the board terminal (mA), 0 = none
  "poe_jumpers": "2-3",                 // "1-2" = RJ45 power lines routed to the PoE socket
  "wifi": null,                         // "WA2000" etc. if the Wi-Fi add-on is fitted
  "buzzer": true,                       // count buzzer current (50 mA)
  "ambient_c": 40,                      // max ambient temperature inside the box, C
  "extra_5v_ma": 0                      // anything else powered from the 5V rail (sensors, LEDs...)
}
Exit code: 0 = no errors, 1 = errors found, 2 = bad input.
"""
import json, os, sys, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import ab_pairs
except ImportError:      # the module ships with the skill; keep the checker usable without it
    ab_pairs = None


def utf8_stdio():
    """Print UTF-8 whatever the console code page is (Windows cp1251/cp1252, pipes in Git Bash)."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
LETTERS = "ABCD"


def load():
    tib = {t["model"]: t for t in json.load(open(os.path.join(DATA, "tibbits.json"), encoding="utf-8"))}
    boards = json.load(open(os.path.join(DATA, "boards.json"), encoding="utf-8"))
    return tib, boards


def norm_model(m):
    m = str(m).strip().lstrip("#").replace("-", "_")
    if re.fullmatch(r"\d", m.split("_")[0]):
        m = "0" + m
    return m.upper() if m.startswith("w") or m.startswith("W") else m


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, where, msg):
        self.items.append({"level": level, "where": where, "msg": msg})

    def err(self, w, m): self.add("error", w, m)
    def warn(self, w, m): self.add("warning", w, m)
    def info(self, w, m): self.add("info", w, m)

    @property
    def errors(self):
        return [i for i in self.items if i["level"] == "error"]


def tile_of(board, n):
    for t in board["tiles"]:
        if n in t:
            return t
    return None


def occupied(board, t, start, rep):
    """Return list of socket numbers a Tibbit occupies, or None if placement is impossible."""
    kind, width = t["kind"], t["width"]
    tile = tile_of(board, start)
    s = board["sockets"].get(f"S{start}")
    if s is None:
        rep.err(f"S{start}", f"на плате {board['family']} нет сокета S{start}")
        return None
    if kind == "WIFI":
        rep.err(f"S{start}", f"#{t['model']} ставится в разъём Wi-Fi add-on, а не в сокет Tibbit (укажи \"wifi\")")
        return None
    if s.get("only") and t["model"] not in s["only"]:
        rep.err(f"S{start}", f"сокет S{start} предназначен только для #{'/#'.join(s['only'])}")
        return None
    want = {"M": "M", "C": "C", "H": "M"}[kind]
    if s["type"] != want:
        rep.err(f"S{start}", f"#{t['model']} ({t['form']}) должен стоять в {want}-сокете, S{start} — {s['type']}-сокет"
                + (" (M — нечётные, C — чётные номера)" if board["family"] in ("TPP2", "TPP3", "LTPP3") else ""))
        return None
    if tile is None:
        return [start]
    if kind == "M" and width == 1:
        return [start]
    if kind == "C" and width == 1:
        return [start]
    if kind == "M" and width == 2:
        if start != tile[0]:
            rep.err(f"S{start}", f"M2-модуль #{t['model']} занимает два M-сокета одного тайла: ставь в S{tile[0]} (займёт S{tile[0]}+S{tile[2]})")
            return None
        return [tile[0], tile[2]]
    if kind == "C" and width == 2:
        if start != tile[1]:
            rep.err(f"S{start}", f"C2-разъём #{t['model']} занимает два C-сокета тайла: ставь в S{tile[1]} (займёт S{tile[1]}+S{tile[3]})")
            return None
        return [tile[1], tile[3]]
    if kind == "H" and width == 1:
        return [start, start + 1]
    if kind == "H" and width == 2:
        if start != tile[0]:
            rep.err(f"S{start}", f"H2-модуль #{t['model']} занимает весь тайл (место M2+C2): ставь в S{tile[0]}")
            return None
        return list(tile)
    return [start]


def supply_limit(t, vin, ambient, rep, where):
    """Usable mA of a power Tibbit at given input and ambient; None if input invalid."""
    sp = t.get("supply_spec") or {}
    m = t["model"]
    if m == "12":
        return sp.get("max_ma")
    lo, hi = sp.get("vin", [None, None])
    if sp.get("poe"):
        return poe_limit(sp, ambient, rep, where)
    if vin is None:
        rep.warn(where, f"#{m}: не указано входное напряжение (power.vin) — диапазон входа проверить нельзя")
        return sp.get("max_ma")
    if not (lo <= vin <= hi):
        hint = ""
        if m in ("09", "10") and vin > hi:
            hint = " Для 24/48 В нужен #25 (8–60 В, до 1.5 А) или #33 (8–60 В, 1.5 А, есть сигнал -PF)."
        rep.err(where, f"#{m}: вход {vin} В вне допустимого диапазона {lo}–{hi} В.{hint}")
        return None
    limit = sp["max_ma"]
    if m == "25":
        pts = sp["derating"]
        vins = sorted({p[0] for p in pts})
        v_ref = next((v for v in vins if v >= vin), vins[-1])
        ok = [p[1] for p in pts if p[0] == v_ref and p[2] >= ambient]
        if ok:
            limit = max(ok)
        else:
            limit = min(p[1] for p in pts if p[0] == v_ref)
            rep.warn(where, f"#25: при {vin} В нет данных о токе для {ambient} °C (по таблице до "
                            f"{max(p[2] for p in pts if p[0] == v_ref)} °C) — считаю {limit} мА, нужен запас")
        if vin <= 12:
            rep.info(where, "#25 рассчитан на 24/48 В; при 12 В отдаёт только ~1 А")
    if m == "33" and vin > 48:
        limit = sp.get("above_48v_max_ma", limit)
        rep.info(where, "#33: при длительной работе от входа выше 48 В — не более 1.3 А")
    return limit


def poe_limit(sp, ambient, rep, where):
    ok = [ma for ma, tmax in sp["derating_ambient"] if tmax >= ambient]
    if not ok:
        rep.err(where, f"#23: при {ambient} °C внутри корпуса за пределами таблицы (до 80 °C при 0.5 А)")
        return 0
    return max(ok)


def check(cfg, tib, boards):
    rep = Report()
    bname = cfg.get("board")
    if bname not in boards:
        rep.err("board", f"неизвестная плата '{bname}'. Есть: {', '.join(boards)}")
        return rep, {}
    board = boards[bname]
    ambient = cfg.get("ambient_c", 40)
    pw = cfg.get("power", {}) or {}
    vin = pw.get("vin")
    placed = {}   # socket num -> (model, start)
    units = []    # dicts: model, start, sockets, t, vin
    for key, val in (cfg.get("slots") or {}).items():
        m = re.fullmatch(r"S?(\d+)", str(key).strip(), re.I)
        if not m:
            rep.err(key, "имя слота должно быть вида S1, S2…"); continue
        start = int(m.group(1))
        model = norm_model(val["model"] if isinstance(val, dict) else val)
        t = tib.get(model)
        if not t:
            rep.err(f"S{start}", f"нет Tibbit #{model} в каталоге (scripts/tps_check.py find …)"); continue
        socks = occupied(board, t, start, rep)
        if socks is None:
            continue
        clash = [s for s in socks if s in placed]
        if clash:
            rep.err(f"S{start}", f"#{model} пересекается с #{placed[clash[0]][0]} в S{clash[0]}"); continue
        for s in socks:
            placed[s] = (model, start)
        u_vin = val.get("vin", vin) if isinstance(val, dict) else vin
        units.append({"model": model, "start": start, "sockets": socks, "t": t, "vin": u_vin})
        if t["status"] in ("deprecated", "not_recommended"):
            rep.warn(f"S{start}", f"#{model} — {'снят с производства' if t['status']=='deprecated' else 'не рекомендуется для новых проектов'}")

    models_present = {u["model"] for u in units}
    poe = board.get("poe")
    jumpers = str(cfg.get("poe_jumpers", "2-3"))

    for u in units:
        t, start, w = u["t"], u["start"], f"S{u['start']}"
        # lines
        if t["kind"] in ("M", "H"):
            m_socks = [s for s in u["sockets"] if board["sockets"][f"S{s}"]["type"] == "M"]
            missing_needed, needed = 0, 0
            for i, ln in enumerate(t["lines"]):
                if ln["need"] == 0 or i >= 4 * len(m_socks):
                    continue
                sock = board["sockets"][f"S{m_socks[i // 4]}"]
                letter = LETTERS[i % 4]
                needed += 1
                if letter not in sock["lines"]:
                    missing_needed += 1
                    msg = f"#{t['model']}: линия {ln['id']} → S{m_socks[i // 4]}.{letter}, а у этого сокета линии {letter} нет"
                    if ln["need"] >= 2:
                        rep.err(w, msg)
                    elif not (t["model"] == "23"):
                        rep.warn(w, msg + (f" ({ln['if_missing']})" if ln["if_missing"] else ""))
            if needed and missing_needed == needed and t["model"] != "23" and t["category"] != "power":
                rep.err(w, f"#{t['model']}: у сокета S{m_socks[0]} нет ни одной нужной линии — модуль будет неуправляем, выбери другой сокет")
            first = board["sockets"][f"S{m_socks[0]}"] if m_socks else None
            if first is not None:
                if "serial" in t["requires"] and first.get("uart") is None:
                    uarts = [k for k, v in board["sockets"].items() if v.get("uart") is not None]
                    rep.err(w, f"#{t['model']} нужен UART, а S{m_socks[0]} не UART-сокет. UART на {bname}: {', '.join(uarts)}")
                elif "serial" in t["requires"]:
                    rep.info(w, f"#{t['model']} → ser.num = {first['uart']}")
                if "interrupt" in t["requires"] and first.get("int") is None:
                    ints = [k for k, v in board["sockets"].items() if v.get("int") is not None]
                    rep.err(w, f"#{t['model']} нужна линия прерывания (D), у S{m_socks[0]} её нет. INT на {bname}: {', '.join(ints)}")
        # Tibbit dependencies
        for need in t.get("requires_tibbit", []):
            if need not in models_present:
                rep.err(w, f"#{t['model']} не работает без #{need} (источник ±15 В) — добавь #{need} в любой M-сокет")
        # connector pairing
        if t["kind"] == "C" and t["width"] == 1:
            ms = board["sockets"][f"S{start}"].get("m_pair")
            mod = placed.get(int(ms[1:]), (None,))[0] if ms else None
            # compatible if either side lists the other (#62 lists #21, while #21 in tibbits.json does not list #62)
            if ms and t["mates"] and mod not in t["mates"] and t["model"] not in (tib.get(mod, {}).get("mates") or []):
                rep.warn(w, f"разъём #{t['model']} обслуживает модуль в {ms}"
                            + (f" (сейчас там #{mod})" if mod else " (он пуст)")
                            + f"; совместим с #{', #'.join(t['mates'][:10])}{' …' if len(t['mates']) > 10 else ''}")
        if t["kind"] == "M":
            cpairs = [board["sockets"][f"S{s}"]["c_pair"] for s in u["sockets"]]
            conns = [placed.get(int(c[1:]), (None,))[0] for c in cpairs]
            is_supply = bool(t.get("supply_spec")) and t["model"] not in ("12", "23")
            if is_supply and not any(c in ("18", "19", "20", "21") for c in conns):
                rep.warn(w, f"#{t['model']}: нет входного разъёма питания в {'/'.join(cpairs)} — поставь #18 (джек+клеммы): "
                            f"его одобряет AppBlocks; #20/#21 допускает документация, но редактор их не принимает")
            elif not is_supply and t["category"] in ("io", "input", "output") and all(c is None for c in conns) and t["mates"]:
                rep.info(w, f"#{t['model']}: в {'/'.join(cpairs)} нет разъёма — внешние линии не выведены (обычно #{t['mates'][0]})")
        # PoE
        if t["model"] == "23":
            if not poe:
                rep.err(w, "на этой плате нет PoE-сокета")
            elif u["sockets"][0] != poe["m2"][0]:
                rep.err(w, f"#23 ставится только в PoE-сокет: S{poe['m2'][0]}+S{poe['m2'][1]}")
            if jumpers != "1-2":
                rep.err(w, "для #23 четыре перемычки у RJ45 должны стоять в положение 1-2 (poe_jumpers)")
        if t["model"] == "18":
            rep.info(w, "#18: не подавай питание одновременно на джек и на клеммы — повредит Tibbit")
    # rules the AppBlocks editor applies to the board (Tibbit socket validator, 2026-10)
    rf = board.get("rf_socket")
    # WA2000U has a U.FL output and needs #37; WA2000C has an on-board chip antenna
    if str(cfg.get("wifi") or "").upper().endswith("U") and rf and placed.get(rf, (None,))[0] != "37":
        rep.warn(f"S{rf}", f"Wi-Fi-модулю {cfg['wifi']} нужен RF-разъём #37 в S{rf} (выход на внешнюю антенну)")
    for u in units:
        t = u["t"]
        tile = tile_of(board, u["start"])
        if not tile or len(tile) < 4:
            continue
        if t["kind"] == "M" and t["width"] == 2:
            c21 = [c for c in (tile[1], tile[3]) if placed.get(c, (None,))[0] == "21"]
            if c21 and ab_ok(t["model"], "20"):
                rep.info(f"S{u['start']}", f"#{t['model']} занимает два M-сокета: один #20 (9 клемм) в S{tile[1]} вместо #21 "
                                           f"в S{', S'.join(map(str, c21))} выведет все его линии")
    for tile in board.get("tiles", []):
        if len(tile) == 4 and all(placed.get(c) == ("21", c) for c in (tile[1], tile[3])):
            mods = [placed.get(m, (None,))[0] for m in (tile[0], tile[2])]
            if all(m and m != "21" and ab_ok(m, "20") for m in mods) and placed.get(tile[0], (None, 0))[1] != placed.get(tile[2], (None, 1))[1]:
                rep.info(f"S{tile[1]}", f"два #21 в S{tile[1]} и S{tile[3]} можно заменить одним #20 (9 клемм) в S{tile[1]} - "
                                        f"он обслужит #{mods[0]} и #{mods[1]}")
    if poe and jumpers == "1-2":
        c_after = poe["m1"] + 1
        if c_after in placed and placed[c_after][0] != "23":
            rep.warn(f"S{c_after}", f"при перемычках 1-2 сокет S{poe['m1']} отключён от S{c_after}: разъём #{placed[c_after][0]} не получит линии")
        if poe["m1"] in placed and placed[poe["m1"]][0] != "23":
            rep.warn(f"S{poe['m1']}", f"перемычки 1-2 подают линии питания RJ45 на S{poe['m1']}, а там #{placed[poe['m1']][0]} — проверь, что это допустимо")

    appblocks_rules(bname, board, units, placed, tib, rep)
    power = power_budget(cfg, board, units, ambient, rep)
    return rep, {"board": bname, "units": [{k: u[k] for k in ("model", "start", "sockets")} | {"form": u["t"]["form"], "name": u["t"]["name"], "category": u["t"]["category"]} for u in units], "power": power, "poe_jumpers": jumpers, "wifi": cfg.get("wifi"), "ext5v": bool((cfg.get("power") or {}).get("ext5v_ma"))}


_AB = None


def ab_data():
    global _AB
    if _AB is None and ab_pairs is not None:
        try:
            _AB = ab_pairs.load_pairs()
        except (OSError, ValueError):
            _AB = {}
    return _AB or {}


def ab_ok(module, connector):
    """True if the AppBlocks editor accepts connector next to module (or has no data for the module)."""
    t = ab_data().get("tibbits", {}).get(module)
    return t is None or not t["mates"] or connector in t["mates"]


def appblocks_rules(bname, board, units, placed, tib, rep):
    """Yellow triangles the AppBlocks editor would draw on the board (see ab_pairs.py). They do not show in Problems."""
    data = ab_data()
    if not data or bname not in data.get("boards", {}):
        return
    res = ab_pairs.socket_warnings(bname, {u["start"]: u["model"] for u in units}, board["sockets"], data)
    done = set()
    for M, C in data["boards"][bname]["mateSockets"]:
        m_mod, c_mod = placed.get(int(M), (None,))[0], placed.get(int(C), (None,))[0]
        for sock in (M, C):
            for msg in res.get(sock, []):
                if (sock, msg) in done:
                    continue
                done.add((sock, msg))
                if msg == ab_pairs.INCORRECT:
                    done.add((C if sock == M else M, msg))
                    docs = c_mod in (tib.get(m_mod, {}).get("mates") or []) or m_mod in (tib.get(c_mod, {}).get("mates") or [])
                    allowed = data["tibbits"].get(m_mod, {}).get("mates", [])
                    text = (f"AppBlocks отметит S{M} и S{C} жёлтым треугольником «Incorrect pair»: редактор не принимает #{c_mod} рядом с #{m_mod}"
                            + (f" (для #{m_mod} разрешено: #{', #'.join(allowed)})" if allowed else ""))
                    if docs:
                        text += (". Документация Tibbo эту пару допускает, электрически она работает, но для публичных решений "
                                 "бери пару, которую одобряет AppBlocks; вариант из документации - для тех, кто берёт риск на себя")
                    rep.warn(f"S{M}", text)
                elif msg == "Tibbit required":
                    need = data["tibbits"].get(c_mod, {}).get("mates", [])
                    if c_mod and need and set(need) <= {"00_3"}:
                        rep.warn(f"S{M}", f"#{c_mod} в S{C} без #00-3 в S{M}: C-датчик не получит +5 В, землю и линии I2C; "
                                          f"AppBlocks отметит S{M} «Tibbit required». Поставь #00-3 в S{M} (как в примере Tibbo tbt29)")
                    else:
                        rep.warn(f"S{M}", f"AppBlocks отметит S{M} «Tibbit required»: разъём #{c_mod} в S{C} без модуля")
                elif msg == "Connector required":
                    rep.warn(f"S{C}", f"AppBlocks отметит S{C} «Connector required»: у #{m_mod} в S{M} нет разъёма для внешних линий")
                elif msg.startswith("Tibbit #"):
                    rep.warn(f"S{sock}", f"AppBlocks отметит S{sock}: «{msg}»")
                else:
                    rep.info(f"S{sock}", f"AppBlocks: {msg}")
    for sock, msgs in res.items():
        if int(sock) % 2 == 1 and not any(sock in pr for pr in data["boards"][bname]["mateSockets"]):
            for msg in msgs:
                rep.info(f"S{sock}", f"AppBlocks: {msg}")


def power_budget(cfg, board, units, ambient, rep):
    pw = cfg.get("power", {}) or {}
    cons = []  # (label, mA on +5V)
    base = board["board_5v_ma"]
    cons.append((f"плата {board['family']} Gen{board['gen']}", base))
    if cfg.get("buzzer", True):
        cons.append(("зуммер", board["buzzer_ma"]))
    if cfg.get("wifi"):
        cons.append((f"Wi-Fi {cfg['wifi']}", board["wa2000_ma"]))
    if cfg.get("extra_5v_ma"):
        cons.append(("прочее на 5 В", int(cfg["extra_5v_ma"])))
    p15 = m15 = 0
    n12 = 0
    cellular = False
    for u in units:
        t = u["t"]
        c = t["consumes_ma"]
        if t["model"] == "12":
            n12 += 1
            continue
        if t.get("supplies_ma", {}).get("+5V"):
            continue
        if c.get("+5V"):
            cons.append((f"#{t['model']} S{u['start']}", c["+5V"]))
        p15 += c.get("+15V", 0)
        m15 += c.get("-15V", 0)
        if t["model"] in ("45_1", "45_2", "45_3", "46"):
            cellular = True
    rail15 = None
    if p15 or m15 or n12:
        cap = 15 * n12
        rail15 = {"plus_ma": p15, "minus_ma": m15, "capacity_ma": cap}
        if n12:
            share = (p15 + m15) / n12
            for i in range(n12):
                cons.append((f"#12 (±15 В) #{i+1}", round(230 + 4.5 * share)))
        for name, val in (("+15 В", p15), ("−15 В", m15)):
            if n12 and val > cap:
                rep.err("±15V", f"нагрузка {name} {val} мА больше {cap} мА от {n12}×#12 — добавь ещё #12")
    # supplies
    sources = []
    if pw.get("ext5v_ma"):
        sources.append(("внешний БП 5 В на клеммах платы", int(pw["ext5v_ma"])))
    onboard = board.get("onboard_supply")
    if onboard:
        sources.append((f"встроенный источник платы ({onboard['vin']})", int(onboard["ma"])))
        rep.info("питание", f"у платы свой источник {onboard['vin']}, {onboard['ma']} мА: Tibbit-ы питания не нужны. "
                            f"Потребление самой платы {board['board_5v_ma']} мА - {onboard.get('note', 'оценка')}")
        if any(u["t"].get("supply_spec") and u["t"]["model"] != "12" for u in units):
            rep.warn("питание", "на этой плате есть свой источник: Tibbit-источник 5 В лишний (docs.tibbo.com/ltpp3g2)")
        if cfg.get("wifi"):
            rep.info("питание", "потребление модуля Wi-Fi WM6256 Tibbo не публикует - в расчёт не включено, оставь запас")
    for u in units:
        t = u["t"]
        if t.get("supply_spec") and t["model"] != "12":
            lim = supply_limit(t, u["vin"], ambient, rep, f"S{u['start']}")
            if lim:
                sources.append((f"#{t['model']} S{u['start']}" + (f" ({u['vin']:g} В)" if u["vin"] and t["model"] != "23" else ""), lim))
    total = sum(v for _, v in cons)
    cap = sum(v for _, v in sources)
    if not sources:
        rep.err("питание", "нет источника 5 В: укажи power.ext5v_ma (внешний стабилизированный 5 В на клеммы платы) "
                           "или поставь Tibbit-источник (#09/#10 9–18 В, #25/#33 8–60 В, #23 PoE)")
    else:
        util = total / cap if cap else 9
        margin_need = 0.7 if cellular else 0.8
        if util > 1:
            rep.err("питание", f"потребление по 5 В {total} мА больше возможностей источников {cap} мА")
        elif util > margin_need:
            rep.warn("питание", f"загрузка источников 5 В {util:.0%} — мало запаса"
                                + (" (сотовый модем даёт пиковые токи, держи загрузку ≤70%)" if cellular else " (держи ≤80%)"))
        if len(sources) > 1:
            rep.info("питание", "несколько источников 5 В работают параллельно через диоды — токи суммируются (docs: tibbit_power)")
    return {"consumers": cons, "sources": sources, "total_5v_ma": total, "capacity_5v_ma": cap, "rail_15v": rail15}


# ------------------------------------------------------------------ output
LEVEL_RU = {"error": "ОШИБКА", "warning": "ВНИМАНИЕ", "info": "инфо"}


def print_report(rep, res):
    if res.get("power"):
        p = res["power"]
        print(f"Плата: {res['board']}")
        print("Установлено: " + ", ".join(f"S{'+S'.join(map(str, u['sockets']))} #{u['model']} ({u['form']})" for u in res["units"]))
        print("\nБюджет +5 В:")
        for n, v in p["consumers"]:
            print(f"  {v:>6} мА  {n}")
        print(f"  {p['total_5v_ma']:>6} мА  ИТОГО потребление")
        for n, v in p["sources"]:
            print(f"  {v:>6} мА  источник: {n}")
        print(f"  {p['capacity_5v_ma']:>6} мА  ИТОГО источники")
        if p["rail_15v"]:
            r = p["rail_15v"]
            print(f"  ±15 В: +{r['plus_ma']} / −{r['minus_ma']} мА из {r['capacity_ma']} мА")
    print()
    order = {"error": 0, "warning": 1, "info": 2}
    for i in sorted(rep.items, key=lambda x: order[x["level"]]):
        print(f"[{LEVEL_RU[i['level']]}] {i['where']}: {i['msg']}")
    print(f"\nИтог: ошибок {len(rep.errors)}, предупреждений {sum(1 for i in rep.items if i['level']=='warning')}")


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def cmd_find(q, tib):
    words = q.lower().split()
    rows = []
    for t in tib.values():
        hay = " ".join([t["model"], t["name"], t["description"], t["tags"], t["category"] or ""]).lower()
        score = sum(1 for w in words if w in hay)
        if score:
            rows.append((score, t))
    rows.sort(key=lambda r: (-r[0], r[1]["status"] != "active", r[1]["model"]))
    for score, t in rows[:15]:
        lines = ",".join(l["id"] for l in t["lines"] if l["need"])
        pw = "; ".join(f"{k} {v}мА" for k, v in t["consumes_ma"].items())
        sup = "; ".join(f"даёт {k} {v}мА" for k, v in t["supplies_ma"].items())
        st = "" if t["status"] == "active" else f" [{t['status']}]"
        print(f"#{t['model']:<6} {t['form']:<4} {t['name']}{st}\n        линии: {lines or '—'} | нужно: {','.join(t['requires']) or '—'} | "
              f"питание: {pw or '—'}{(' | ' + sup) if sup else ''} | разъём: {','.join(t['mates'][:4]) or '—'}")


def cmd_board(name, boards):
    b = boards.get(name)
    if not b:
        print("Платы:", ", ".join(boards)); return
    print(f"{name}: {b['family']} Gen{b['gen']}, плата {b['board_5v_ma']} мА + зуммер {b['buzzer_ma']} мА, Wi-Fi +{b['wa2000_ma']} мА")
    if b.get("os") == "linux":
        print("Linux-плата: не TiOS, программы - приложения Linux (references/linux.md). "
              f"Свой источник {b['onboard_supply']['vin']}, {b['onboard_supply']['ma']} мА.")
    print("Тайлы:", " | ".join("S" + ",S".join(map(str, t)) for t in b["tiles"]))
    if b.get("poe"):
        print(f"PoE: M1 в S{b['poe']['m1']} или M2 в S{b['poe']['m2'][0]}+S{b['poe']['m2'][1]}, перемычки {b['poe']['jumpers']}")
    for k, s in b["sockets"].items():
        if s["type"] == "M":
            print(f"  {k:<4} M  линии {''.join(s['lines']) or '—':<5} UART {s['uart'] if s['uart'] is not None else '-'}  INT {s['int'] if s['int'] is not None else '-'}"
                  f"{'  ADC' if s['adc'] else ''}  → разъём в {s['c_pair']}  ({', '.join(s['lines'].values())})")
        elif s.get("only"):
            print(f"  {k:<4} C  только #{','.join(s['only'])}")


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    tib, boards = load()
    cmd = sys.argv[1]
    if cmd == "find":
        cmd_find(" ".join(sys.argv[2:]), tib); return
    if cmd == "board":
        cmd_board(sys.argv[2], boards); return
    if cmd == "tibbit":
        print(json.dumps(tib.get(norm_model(sys.argv[2])), ensure_ascii=False, indent=1)); return
    if cmd != "check":
        print(__doc__); sys.exit(2)
    path = sys.argv[2]
    try:
        cfg = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print(f"не читается {path}: {e}"); sys.exit(2)
    rep, res = check(cfg, tib, boards)
    if "--json" in sys.argv:
        print(json.dumps({"result": res, "findings": rep.items}, ensure_ascii=False, indent=1))
    else:
        print_report(rep, res)
    if "--svg" in sys.argv and res:
        out = sys.argv[sys.argv.index("--svg") + 1]
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import tps_render
        open(out, "w", encoding="utf-8").write(tps_render.render(res, boards[res["board"]], rep, tib))
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    utf8_stdio()
    main()
