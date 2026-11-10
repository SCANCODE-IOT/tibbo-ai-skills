#!/usr/bin/env python3
"""Rebuild data/tibbits.json and data/boards.json.

Inputs:
  - tibbits.json from github.com/tibbotech/TibbitDefinitions (path as argv[1])
  - references/platforms.md (socket/line map extracted from TIDE .tph files)
  - facts from docs.tibbo.com, kept in this file (DOCS_* dicts) with their source page

Usage: python3 scripts/build_data.py /path/to/TibbitDefinitions/tibbits.json
"""
import json, re, sys, os


def utf8_stdio():
    """Print UTF-8 whatever the console code page is (Windows cp1251/cp1252, pipes in Git Bash)."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---- facts from docs.tibbo.com (Oct 2026) -------------------------------------------------
# Status from docs.tibbo.com/tibbit_list
DOCS_STATUS = {
    "48": "deprecated", "49": "deprecated", "50": "deprecated", "51": "deprecated", "56": "deprecated",
    "52": "deprecated", "53": "not_recommended",
}
# Form-factor corrections from docs.tibbo.com/tibbit_list (catalog JSON says H2)
DOCS_FORM = {"61_1": "H2T", "61_2": "H2T"}

# Power supply Tibbits: docs.tibbo.com/tibbit_09, _10, _12, _23, _25, _33
DOCS_SUPPLY = {
    "09": {"out_rail": "+5V", "vin": [9, 18], "max_ma": 700, "isolated": False,
           "doc": "https://docs.tibbo.com/tibbit_09",
           "notes": "Catalog name says '12V input'; real range 9-18V. 24V will damage it."},
    "10": {"out_rail": "+5V", "vin": [9, 18], "max_ma": 1100, "isolated": False,
           "doc": "https://docs.tibbo.com/tibbit_10",
           "notes": "Catalog name says '12V input'; real range 9-18V. 24V will damage it."},
    "25": {"out_rail": "+5V", "vin": [8, 60], "max_ma": 1500, "isolated": False,
           "doc": "https://docs.tibbo.com/tibbit_25",
           # (vin, max_ma, max_ambient_C) derating points from the page
           "derating": [[12, 1000, 70], [24, 1500, 60], [24, 1000, 80], [48, 1000, 60],
                        [48, 500, 80], [60, 1000, 50], [60, 500, 70]],
           "notes": "Meant for 24/48V; at 12V only ~1A. Derate by ambient temperature."},
    "33": {"out_rail": "+5V", "vin": [8, 60], "max_ma": 1500, "peak_ma": 2000, "isolated": False,
           "doc": "https://docs.tibbo.com/tibbit_33",
           "above_48v_max_ma": 1300,
           "notes": "Dips to 6V / spikes to 100V tolerated. -PF line = power-fail flag (watch with interrupt). "
                    "Sustained >48V input: max 1.3A. Protected (reverse input, short, overheat). -40..+85C."},
    "23": {"out_rail": "+5V", "vin": [35, 60], "max_ma": 1300, "isolated": True, "poe": True,
           "doc": "https://docs.tibbo.com/tibbit_23",
           "derating_ambient": [[1300, 50], [1000, 60], [500, 80]],
           "notes": "Must sit in the PoE socket (TPP2: S9+S11, TPP3: S25+S27) with the 4 jumpers by RJ45 in 1-2. "
                    "Non-PoE use: 35-60V any polarity on IO5/IO6 or IO7/IO8."},
    "12": {"out_rail": "+-15V", "vin_rail": "+5V", "max_ma": 15, "isolated": False,
           "base_5v_ma": 230, "per_ma_5v": 4.5,
           "doc": "https://docs.tibbo.com/tibbit_12",
           "notes": "Only source of +15/-15V. Draws 230mA + 4.5 x (load on +-15V) from +5V. Required by #13, #14."},
}
DOCS_REQUIRES_TIBBIT = {"13": ["12"], "14": ["12"]}

# Selection tags (EN + RU) for quick search; complements name/description
TAGS = {
    "00_1": "gpio direct io прямые линии", "00_2": "gpio direct io ground", "00_3": "gpio +5v sensor adapter питание датчика c1",
    "01": "rs232 serial uart com-port последовательный", "02": "rs232 rs422 rs485 serial uart universal modbus",
    "03_1": "relay реле low power слаботочное", "03_2": "relay реле low power",
    "04_1": "digital input дискретный вход isolated опто", "04_2": "digital input isolated common minus",
    "04_3": "digital input isolated common plus", "04_4": "digital input opto 4ch",
    "04_5": "digital input 24v дискретный вход 24в isolated", "04_6": "digital input 24v common minus",
    "04_7": "digital input 24v common plus", "04_8": "digital input 24v 4ch",
    "05": "rs485 modbus rtu serial uart", "06": "relay реле high power силовое 2ch", "07": "ssr solid state relay твердотельное реле dc",
    "08": "wiegand clock data reader считыватель rfid скуд access control", "09": "power supply питание 12v 5v",
    "10": "power supply питание 12v 5v", "11": "open collector output выход ок", "12": "power +15v -15v питание аналог",
    "13": "adc ацп analog input 0-10v аналоговый вход", "14": "dac цап analog output аналоговый выход",
    "15": "ac ssr 220v solid state relay сетевое реле", "16": "pwm шим open collector", "17": "pwm шим power output",
    "18": "power input jack разъем питания", "19": "db9 connector разъем", "20": "terminal blocks клеммы 9",
    "21": "terminal blocks клеммы 4", "22": "rtd pt100 pt1000 temperature температура термосопротивление",
    "23": "poe power over ethernet питание", "25": "power supply питание 24v 48v 12v high power",
    "26": "ir infrared ик пульт", "27": "ir infrared ик", "28": "light sensor освещенность", "29": "temperature температура",
    "30": "humidity temperature влажность температура", "31": "pic coprocessor сопроцессор", "33": "power supply wide input 8-60v 24v 48v 12v питание power fail",
    "35": "pressure давление барометр", "36": "accelerometer акселерометр", "37": "rf antenna антенна wifi lte",
    "38": "button кнопка", "39_1": "led индикатор", "39_2": "led индикатор", "39_3": "led индикатор", "39_4": "led индикатор",
    "40_1": "digital potentiometer потенциометр", "40_2": "digital potentiometer", "40_3": "digital potentiometer", "40_4": "digital potentiometer",
    "41": "8-bit port", "42": "rtc clock часы nvram", "43_1": "streaming adc ±10v ацп быстрый", "43_2": "streaming adc ±100v ацп",
    "44_1": "isolated rs232 rs422 rs485 serial гальваноразвязка db9", "44_2": "isolated rs232 rs422 rs485 serial terminal",
    "45_1": "lte 4g modem модем cellular", "45_2": "lte 4g modem europe", "45_3": "lte 4g modem americas",
    "46": "nb-iot cat-m1 modem модем", "48": "audio", "49": "microsd card", "50": "usb", "52": "isolated adc ±10v",
    "53": "isolated 4-20ma adc токовая петля", "54": "dry contact сухой контакт digital input",
    "57": "fpga", "58": "24v npn output выход isolated", "59": "24v pnp output выход isolated",
    "61_1": "isolated adc ±10v 4-20ma токовая петля 24v output питание датчиков", "61_2": "isolated adc ±10v 4-20ma токовая петля",
    "62": "1-wire onewire ds18b20 dht11 dht22 temperature humidity", "63_1": "ac voltage detector 110v наличие напряжения",
    "63_2": "ac voltage detector 220v наличие напряжения сети",
    "WA2000C": "wifi bluetooth add-on", "WA2000U": "wifi bluetooth add-on", "WM6256": "wifi add-on",
}

# Board facts. Socket line maps come from platforms.md; the rest from docs.tibbo.com:
# tpp2g2_tiles_sockets, tpp3_tiles_sockets, tps_common_power, tpp2g3, tpp3g2, ltpp3g2_tiles_sockets
BOARD_FAMILY = {
    "TPP2": {"m_sockets": [1, 3, 5, 7, 9, 11], "c_sockets": [2, 4, 6, 8, 10, 12], "rf_socket": 13,
             "tiles": [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]],
             "poe": {"m1": 11, "m2": [9, 11], "jumpers": "1-2"}, "enclosures": ["TPB2", "TPB2L"]},
    "TPP3": {"m_sockets": list(range(1, 28, 2)), "c_sockets": list(range(2, 29, 2)), "rf_socket": 29,
             "tiles": [[i, i + 1, i + 2, i + 3] for i in range(1, 28, 4)],
             "poe": {"m1": 27, "m2": [25, 27], "jumpers": "1-2"}, "enclosures": ["TPB3"]},
    # Linux board. docs.tibbo.com/ltpp3g2, ltpp3g2_tiles_sockets: 4 tiles, UART on S1/S5/S9/S13, no PoE socket, no RF socket
    "LTPP3": {"m_sockets": list(range(1, 16, 2)), "c_sockets": list(range(2, 17, 2)), "rf_socket": None,
              "tiles": [[i, i + 1, i + 2, i + 3] for i in range(1, 16, 4)], "poe": None, "enclosures": ["LTPB3"]},
}
# LTPP3(G2) lines by socket, docs.tibbo.com/ltpp3g2_platform_pl_io_num (not in the TIDE platform files)
LTPP3G2_LINES = {1: (9, 8, 0, 16), 3: (32, 33, 4, 20), 5: (11, 10, 1, 17), 7: (34, 35, 5, 21),
                 9: (13, 12, 2, 18), 11: (36, 37, 6, 22), 13: (15, 14, 3, 19), 15: (38, 39, 7, 23)}
BOARDS = {
    # name: family, gen, base current at 5V (mA), onboard supply
    "TPP2W": ("TPP2", 1, 300, None), "TPP2N": ("TPP2", 1, 300, None),
    "TPP2W(G2)": ("TPP2", 2, 140, None), "TPP2W(G3)": ("TPP2", 3, 140, None),
    "TPP3W": ("TPP3", 1, 300, None), "TPP3N": ("TPP3", 1, 300, None),
    "TPP3W(G2)": ("TPP3", 2, 140, None), "TPP3W(G3)": ("TPP3", 3, 140, None),
    # Linux. Own 8-60 V supply rated 2.5 A, so no power Tibbits (docs.tibbo.com/ltpp3g2). The board itself draws
    # 400 mA at 12 V with both Ethernet ports on = 4.8 W, taken here as 960 mA of the 5 V budget (estimate).
    "LTPP3(G2)": ("LTPP3", 2, 960, {"ma": 2500, "vin": "8-60 В", "note": "оценка: Tibbo даёт 2,5 А источника и 400 мА при 12 В у платы"}),
}


def parse_platform_sockets(md):
    sections = re.split(r"\n## ", md)
    out = {}
    for s in sections:
        name = s.split(" — ")[0].strip()
        if name not in BOARDS:
            continue
        socks = {}
        for pl, sock, line in re.findall(r"- (PL_IO_NUM_\w+) — Socket (\d+), control line ([A-H])", s):
            # Known comment typo in TPP3 .tph files: PL_IO_NUM_38/39 are labelled "Socket 13" although
            # S13 A/B are TX3/RX3; docs.tibbo.com/tpp3_tiles_sockets says every M socket except
            # S23/S25/S27 has all 4 lines, and S15 A/B are otherwise missing -> they belong to S15.
            if name.startswith("TPP3") and pl in ("PL_IO_NUM_38", "PL_IO_NUM_39") and sock == "13":
                sock = "15"
            d = socks.setdefault(int(sock), {})
            info = {"pl": pl}
            m = re.search(r"_(RX|TX)(\d+)$", pl)
            if m:
                info["uart"] = int(m.group(2)); info["uart_role"] = m.group(1)
            m = re.search(r"_INT(\d+)$", pl)
            if m:
                info["int"] = int(m.group(1))
            d[line] = info
        adc = re.findall(r"PL_ADC_NUM_(\d+) — ADC channel \d+ \(mapped to I/O line (\d+)\)", s)
        if adc:
            io_lines = {int(x[1]) for x in adc}
            for sock, lines in socks.items():
                for ln, info in lines.items():
                    n = int(re.match(r"PL_IO_NUM_(\d+)", info["pl"]).group(1))
                    if n in io_lines:
                        info["adc"] = True
        out[name] = socks
    return out


def build_tibbits(src):
    raw = json.load(open(src, encoding="utf-8"))
    out = []
    for x in raw:
        m, g = x["main"], x["good"]
        model = g["model"]
        form = DOCS_FORM.get(model, m.get("form", ""))
        kind = form[0] if form and form[0] in "MCH" else form
        width = int(form[1]) if len(form) > 1 and form[1].isdigit() else None
        height = form[2] if len(form) > 2 and form[2] in "ST" else None
        lines = []
        for l in m.get("lines", []):
            lines.append({"id": l.get("id", "?"), "need": l.get("requirement", 0), "if_missing": (l.get("message") or "").strip()})
        consume, supply = {}, {}
        for p in m.get("power", []):
            v = p["voltage"].replace("5V", "+5V") if p["voltage"] == "5V" else p["voltage"]
            (supply if p.get("supply") else consume)[v] = int(p["value"])
        base = model.split("_")[0]
        t = {
            "model": model, "name": g["name"], "description": (g.get("description") or "").strip(),
            "category": m.get("category"), "form": form, "kind": kind, "width": width, "height": height,
            "lines": lines, "requires": m.get("requires", []), "requires_tibbit": DOCS_REQUIRES_TIBBIT.get(model, []),
            "mates": m.get("mates", []), "consumes_ma": consume, "supplies_ma": supply,
            "tags": TAGS.get(model, ""), "status": DOCS_STATUS.get(base, "active" if g.get("for_sale", 1) else "not_for_sale"),
            "doc": f"https://docs.tibbo.com/tibbit_{base}" if base[0].isdigit() else None,
        }
        if base in DOCS_SUPPLY and model == base:
            t["supply_spec"] = DOCS_SUPPLY[base]
        if kind == "WIFI":
            t["consumes_ma"] = {"+5V": 300}
            t["note"] = "Catalog says 200mA; docs.tibbo.com/tps_common_power says WA2000 adds 300mA. 300 used."
        if model in ("45_1", "45_2", "45_3", "46"):
            t["note"] = "Average current from catalog. Cellular modems draw short transmit peaks well above average: keep >=30% supply margin."
        out.append(t)
    return out


def build_boards(platform_sockets):
    out = {}
    for name, (fam, gen, base_ma, onboard) in BOARDS.items():
        f = BOARD_FAMILY[fam]
        b = {"family": fam, "gen": gen, "board_5v_ma": base_ma, "buzzer_ma": 50, "wa2000_ma": 300,
             "onboard_supply": onboard, **f, "sockets": {}}
        socks = platform_sockets.get(name, {})
        if fam == "LTPP3":
            b.update({"buzzer_ma": 0, "wa2000_ma": 0, "os": "linux"})   # buzzer is part of the board figure
            socks = {}
            for n, (s, (la, lb, lc, ld)) in enumerate(LTPP3G2_LINES.items()):
                socks[s] = {k: {"pl": "PL_IO_NUM_%d" % v} for k, v in zip("ABCD", (la, lb, lc, ld))}
                socks[s]["D"]["int"] = n            # any M socket can be an interrupt source (PinMux), 8 at most
                if s in (1, 5, 9, 13):
                    socks[s]["A"]["uart"] = (1, 5, 9, 13).index(s)
        for s in f["m_sockets"]:
            lines = socks.get(s, {})
            b["sockets"][f"S{s}"] = {
                "type": "M", "lines": {k: v["pl"] for k, v in sorted(lines.items())},
                "uart": next((v["uart"] for v in lines.values() if "uart" in v), None),
                "int": next((v["int"] for v in lines.values() if "int" in v), None),
                "adc": any(v.get("adc") for v in lines.values()),
                "c_pair": f"S{s + 1}",
            }
        for s in f["c_sockets"]:
            b["sockets"][f"S{s}"] = {"type": "C", "m_pair": f"S{s - 1}"}
        if f["rf_socket"]:
            b["sockets"][f"S{f['rf_socket']}"] = {"type": "C", "only": ["37"]}
        out[name] = b
    return out


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "tibbits.src.json")
    md = open(os.path.join(ROOT, "references", "platforms.md"), encoding="utf-8").read()
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    tib = build_tibbits(src)
    boards = build_boards(parse_platform_sockets(md))
    json.dump(tib, open(os.path.join(ROOT, "data", "tibbits.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(boards, open(os.path.join(ROOT, "data", "boards.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"tibbits: {len(tib)}, boards: {', '.join(boards)}")


if __name__ == "__main__":
    try:
        utf8_stdio()
        main()
    except BrokenPipeError:      # the reader (head, grep -q) closed the pipe: not an error
        try:
            sys.stdout.close()
        except OSError:
            pass
        os._exit(0)
