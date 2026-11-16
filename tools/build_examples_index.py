#!/usr/bin/env python3
"""Build skills/appblocks/references/examples-index.md - every published appblocks.io project with its board, runtime,
Tibbits, services in use and the result of `ab_tool.py check` and of a cloud build.

  python3 tools/build_examples_index.py DIR [--sitemap sitemap.xml] [--builds results.txt] [--date "16 ноября 2026"]

DIR holds <name>.json downloaded from https://appblocks.io/projects/<name>.json (names from the /tutorials/ and
/examples/ pages of the sitemap); files that are not projects are skipped. results.txt has lines
"OK <name>", "FAIL <name> | <compiler output>", "SKIP <name> <reason>" (from `ab_api.py build`); without it the build
column says "не собирали". Needs no network and no API key.
"""
import collections, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills", "appblocks")
OUT = os.path.join(SK, "references", "examples-index.md")
# services worth naming in the index (present in nearly every export, so only the ones switched on count)
SERVICES = {"mqtt": "MQTT", "modbus_master": "Modbus master", "modbus_slave": "Modbus slave", "web_dashboard": "веб-панель",
            "httpserver": "HTTP-сервер", "http": "HTTP-клиент", "cgg": "AppBlocks Cloud", "lcd": "LCD", "luis": "LUIS",
            "wifi": "Wi-Fi", "cell": "сотовая связь", "bt": "Bluetooth", "unowiresensors": "1-Wire",
            "cron": "расписание", "tbl": "таблицы", "firmware_upgrade": "OTA", "smtp_client": "SMTP", "snmp_agent": "SNMP",
            "azure": "Azure", "kp": "клавиатура", "beep": "зуммер", "mbedtls": "TLS", "flash_devices": "флеш"}


def args():
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    opt = lambda k, d=None: a[a.index(k) + 1] if k in a else d
    return a[0], opt("--sitemap"), opt("--builds"), opt("--date", "")


def kinds(sitemap):
    if not sitemap:
        return {}
    locs = re.findall(r"<loc>https://appblocks\.io/(tutorials|examples)/([^<]+)</loc>", open(sitemap, encoding="utf-8").read())
    return {n: ("урок" if k == "tutorials" else "пример") for k, n in locs}


def builds(path):
    res = {}
    if not path:
        return res
    for line in open(path, encoding="utf-8", errors="replace"):
        m = re.match(r"(OK|FAIL|SKIP) (\S+)(.*)", line)
        if not m:
            continue
        st, name, rest = m.groups()
        if st == "FAIL":
            ids = re.findall(r"undeclared identifier '(\w+)'", rest)
            if ids:
                res[name] = "не собирается: '" + ids[0] + "'"
            else:                              # line cut by parallel writes: keep a fuller verdict from another line
                res.setdefault(name, "не собирается")
        elif st == "SKIP":
            res.setdefault(name, "Zephyr - через API не собрать" if "zephyr" in rest else "не собирали")
        else:
            res[name] = "собирается"
    return res


sys.path.insert(0, os.path.join(SK, "scripts"))
import ab_tool  # noqa: E402  (enabled_state: a missing ENABLED takes the editor default, as the generator does)
REG = ab_tool.load_registry() or {}


def used(f, node_feats):
    """A service counts when the project uses it: switched on (ENABLED or the editor default) and, for services that are
    on by default or have no ENABLED field, also used by a block or holding items (Modbus devices, 1-Wire sensors...)."""
    fid = f["id"]
    freg = next((REG[k][fid] for k in ("features", "libraries") if fid in (REG.get(k) or {})), None)
    en = ((freg or {}).get("set") or {}).get("ENABLED")
    if en is not None and not ab_tool.enabled_state(f["settings"], freg)[0]:
        return False
    if en is not None and str(en.get("d")) == "0":
        return True
    return fid in node_feats or any(isinstance(v, list) and v for v in f["settings"].values())


def check(path):
    r = subprocess.run([sys.executable, os.path.join(SK, "scripts", "ab_tool.py"), "check", path],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    errs = [l[len("[ОШИБКА] "):] for l in r.stdout.splitlines() if l.startswith("[ОШИБКА]")]
    warns = sum(l.startswith("[ВНИМАНИЕ]") for l in r.stdout.splitlines())
    return errs, warns


def short(err):
    for pat, txt in ((r"AppBlocks Cloud \(cgg\) включён", "Cloud без OTA/HTTP"), (r"нужна .*\((\w+)\), а она выключена", None),
                     (r"нет авто-переменной порта", "нет переменной порта #05"), (r"Name conflict", "конфликт имён"),
                     (r"только в среде", "блок не той среды"), (r"BT_NAME", "LUIS без Bluetooth")):
        m = re.search(pat, err)
        if m:
            return txt or f"{m.group(1)} выключена"
    return err[:60].rstrip() + "…"


def main():
    d_in, sitemap, bfile, date = args()
    kind, bres = kinds(sitemap), builds(bfile)
    rows, stats = [], collections.Counter()
    for fn in sorted(os.listdir(d_in)):
        if not fn.endswith(".json"):
            continue
        p = os.path.join(d_in, fn)
        try:
            d = json.load(open(p, encoding="utf-8"))
        except (ValueError, UnicodeDecodeError):
            continue
        if not isinstance(d, dict) or "features" not in d:
            continue
        name = fn[:-5]
        F = d["features"]
        tb = sorted({(int(re.sub(r"\D", "", str(f["settings"].get("SOCKET", "0"))) or 0), f["id"][7:].replace("_", "-"))
                     for f in F if f["id"].startswith("tibbit_")})
        nf = {(REG.get("nodes") or {}).get(f["id"], {}).get("feat") for f in F if f["id"].startswith("node_")}
        svc = [SERVICES[f["id"]] for f in F if f["id"] in SERVICES and used(f, nf)]
        svc = list(dict.fromkeys(svc))
        nodes = sum(f["id"].startswith("node_") and f["id"] != "node_link" for f in F)
        errs, warns = check(p)
        rt = d.get("runtime") or "tios"
        stats[(d.get("device"), rt)] += 1
        stats["err"] += bool(errs)
        st = "0 ошибок" if not errs else "; ".join(dict.fromkeys(short(e) for e in errs))
        rows.append((name, kind.get(name, ""), d.get("name") or name, d.get("device") or "", rt,
                     " ".join(f"S{s}:#{m}" for s, m in tb), ", ".join(svc), nodes, st, warns,
                     bres.get(name, "Zephyr - через API не собрать" if rt != "tios" else "не собирали")))
    boards = collections.Counter(r[3] for r in rows)
    rts = collections.Counter(r[4] for r in rows)
    built = collections.Counter(r[10].split(":")[0] for r in rows)
    L = [f"# Опубликованные проекты appblocks.io: что в них и в каком они состоянии",
         "",
         f"Все {len(rows)} проектов уроков и примеров appblocks.io (`https://appblocks.io/projects/<имя>.json`, имя - последний",
         "сегмент страницы `appblocks.io/tutorials/*` или `appblocks.io/examples/*`)" + (f", снято {date}." if date else "."),
         "Читай, когда пользователь просит пример под задачу («есть готовый проект с Modbus и MQTT?»), берёт проект Tibbo за",
         "основу или спрашивает, почему пример не собирается. Сгенерировано `tools/build_examples_index.py`.",
         "",
         "Платы: " + ", ".join(f"{k} - {v}" for k, v in boards.most_common()) + ". Среды: "
         + ", ".join(f"{k} - {v}" for k, v in rts.most_common()) + ".",
         f"`ab_tool.py check`: без ошибок {len(rows) - stats['err']}, с ошибками {stats['err']}. Сборка компилятором Tibbo через"
         " API: " + ", ".join(f"{k} - {v}" for k, v in built.most_common()) + ".",
         "",
         "**Как пользоваться.** Пример с ошибками не бери как есть: сначала исправь то, что пишет `check` (частые причины ниже).",
         "Сокеты Tibbit смотри в столбце «Tibbit»: в проектах Tibbo источник питания почти всегда в S11 + #18 в S12 на TPP2 и",
         "S25 + #18 в S26 на TPP3 (power.md §2a скилла tibbo-firmware). В публичных примерах встречаются логин и пароль",
         "облака в открытом виде - в свой проект не переноси, задай свои через настройки.",
         "",
         "Частые причины «не собирается»:",
         "- **Cloud без OTA/HTTP** - включён AppBlocks Cloud (`cgg`), а `firmware_upgrade` и `http` выключены (в старых",
         "  экспортах поля ENABLED нет, редактор берёт 0): «undeclared identifier 'upload_started'». Поставь обоим ENABLED = 1.",
         "- **http выключена** - есть блок HTTP Request, а библиотека `http` выключена: «undeclared identifier 'http_request'».",
         "- **нет переменной порта #05** - у Tibbit RS232/422/485 нет авто-переменной порта: ошибка компилятора.",
         "- **Zephyr** - через API собрать нельзя (zephyr.md §4), собирай в редакторе.",
         "",
         "| Проект | Вид | Название | Плата | Среда | Tibbit (сокет:модель) | Сервисы | Блоков | check | Сборка |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| `{r[0]}` | {r[1]} | {r[2]} | {r[3]} | {r[4]} | {r[5] or '—'} | {r[6] or '—'} | {r[7]} | {r[8]}"
                 + (f", предупр. {r[9]}" if r[9] else "") + f" | {r[10]} |")
    open(OUT, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print(f"{OUT}: {len(rows)} projects")


if __name__ == "__main__":
    main()
