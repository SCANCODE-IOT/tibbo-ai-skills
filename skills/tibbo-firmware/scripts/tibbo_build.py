#!/usr/bin/env python3
"""Build a TIDE project (Tibbo BASIC / Tibbo C) with Tibbo's real compiler and show its errors.
Сборка проекта TIDE настоящим компилятором Tibbo: ошибки компилятора и готовый .tpc.

Three ways, chosen automatically:
  checking code (plain build)       - node, then local TIDE, then cloud
  firmware for a device (--firmware, --release or --out) - local TIDE (same platforms as the user's TIDE), then node, then cloud
  Tibbo C projects                  - local TIDE, then cloud (node builds Tibbo BASIC only)
  local  - TIDE is installed on this Windows computer: runs TIDE's command-line builder tmake.exe.
           The code stays on the computer. Also from WSL (TIDE on /mnt/c, experimental).
  node   - any OS with Node.js, no TIDE: Tibbo's compiler ported to Node.js (github.com/tibbotech/tibbo-basic,
           branch feature/compiler), byte-identical .tpc; Tibbo BASIC only. Set up once: --setup-node --yes.
  cloud  - any OS, no TIDE: Tibbo's compiler behind AppBlocks (api.appblocks.io). The project files are sent to
           Tibbo's server, so it needs the user's consent: --cloud-ok or TIBBO_CLOUD_BUILD=yes.

Usage:
  python3 scripts/tibbo_build.py <project folder or .tpr> [--local | --cloud] [--release | --debug]
                                 [--out app.tpc] [--firmware] [--json] [--cloud-ok]   (or --node)
  python3 scripts/tibbo_build.py --setup-node [--yes] [--latest-platforms]   # download and build Tibbo's Node.js
                                 # compiler (asks first); --latest-platforms: newest platform files (TiOS) from GitHub
  python3 scripts/tibbo_build.py --doctor [<project>] [--json]   # what is available here, what the USER must do
                                                     # and, with a project, TIDE advice for THIS project
                                                     # (relay "Что сделать пользователю" to the user as is)
  python3 scripts/tibbo_build.py --upload app.tpc --target <MAC or COM port> [--serial] --yes
                                 # Windows + TIDE: upload to a device with TIDE's tupload.exe (asks first)

Environment: TIBBO_BASIC_HOME (Node.js compiler folder, default ~/.tibbo/tibbo-basic), TIBBO_BASIC_COMPILER, TIDE_DIR (TIDE folder, default C:\\Program Files (x86)\\Tibbo\\TIDE), TIBBO_CLOUD_BUILD=yes (consent for
cloud builds), APPBLOCKS_BASE (default https://api.appblocks.io), APPBLOCKS_API_KEY (optional), SSL_CERT_FILE.
Exit codes: 0 - built, 1 - compiler errors, 2 - bad input, 3 - no way to build here or no consent, 4 - network/tool error.
Python 3.9+, standard library only.
"""
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = os.environ.get("APPBLOCKS_BASE", "https://api.appblocks.io").rstrip("/")
TEXT_EXT = (".tbs", ".tbh", ".tc", ".th", ".txt", ".xtxt", ".html", ".htm", ".js", ".css", ".json", ".xml", ".csv", ".ini")
MAX_CLOUD_BYTES = 8 * 1024 * 1024
NOISE = re.compile(r"warning C1006: preprocessor redefinition of 'DEBUG'")


# ---------- project ----------

def read_text(p):
    """Text of a project file. UTF-16 only with a BOM (any even-length byte string 'decodes' as UTF-16);
    old files in a legacy code page (cp1251, cp1252, Big5 comments) come back as latin-1, byte for byte."""
    raw = Path(p).read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("latin-1")


def decode_output(raw):
    """Console output of TIDE tools: UTF-16 if it has zero bytes, else UTF-8, else the Windows code page."""
    if b"\x00" in raw:
        return raw.decode("utf-16", "replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        import locale
        return raw.decode(locale.getpreferredencoding(False) or "cp1251", "replace")


def find_tpr(arg):
    p = Path(arg)
    if p.is_file() and p.suffix.lower() == ".tpr":
        return p
    if p.is_dir():
        tprs = sorted(p.glob("*.tpr"))
        if len(tprs) == 1:
            return tprs[0]
        if len(tprs) > 1:
            raise ValueError("в папке несколько .tpr - укажите нужный файл: " + ", ".join(t.name for t in tprs))
    raise ValueError("не найден проект .tpr: %s" % arg)


def tpr_addresses(text):
    """[addressN] sections: devices TIDE remembers for this project (platform, transport, address)."""
    out, cur = [], None
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"\[(.+)\]$", line)
        if m:
            cur = {} if m.group(1).lower().startswith("address") else None
            if cur is not None:
                out.append(cur)
        elif cur is not None and "=" in line:
            k, v = [x.strip() for x in line.split("=", 1)]
            cur[k.lower()] = v
    return out


def parse_tpr(text):
    """[project] keys and the list of files ([fileN] path/type) of a TIDE project."""
    project, files, section, cur = {}, [], None, None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        m = re.match(r"\[(.+)\]$", line)
        if m:
            section = m.group(1).lower()
            cur = {} if section.startswith("file") else None
            if cur is not None:
                files.append(cur)
            continue
        if "=" in line:
            k, v = [x.strip() for x in line.split("=", 1)]
            if section == "project":
                project[k.lower()] = v
            elif cur is not None:
                cur[k.lower()] = v
    return project, files


def collect(tpr):
    """Files to send to the cloud: every project file that exists in the folder (+ headers/sources lying next to them).
    Paths that do not exist here are TIDE library files (e.g. sock\\trunk\\sock.tbs): the compiler resolves them."""
    root = tpr.parent
    text = read_text(tpr)
    project, entries = parse_tpr(text)
    out, seen, library, size = [{"name": "/" + tpr.name, "contents": text}], {tpr.name.lower()}, [], len(text)

    def add(rel, kind=None):
        nonlocal size
        rel = rel.replace("\\", "/")
        fp = root / rel
        if rel.lower() in seen:
            return True
        if not fp.is_file():
            return False
        data = fp.read_bytes()
        size += len(data)
        contents = None
        if kind != "binary" and rel.lower().endswith(TEXT_EXT):
            try:
                contents = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                pass  # legacy code page: send the bytes as they are, as TIDE would read them
        if contents is None:
            contents = {"type": "Buffer", "data": list(data)}
        out.append({"name": "/" + rel, "contents": contents})
        seen.add(rel.lower())
        return True

    for e in entries:
        path = e.get("path", "")
        if path and not add(path, e.get("type")):
            library.append(path)
    for fp in sorted(root.rglob("*")):
        if fp.is_file() and fp.suffix.lower() in (".tbs", ".tbh", ".tc", ".th") and len(fp.relative_to(root).parts) <= 4:
            add(str(fp.relative_to(root)))
    if size > MAX_CLOUD_BYTES:
        raise ValueError("проект слишком большой для облачной сборки (%d КБ)" % (size // 1024))
    return project, out, library


def parse_messages(output, root_hint=None):
    msgs = []
    for line in output.replace("\r", "").split("\n"):
        if NOISE.search(line):
            continue
        m = re.search(r"([^\\/:]*?[\\/]?[\w .()\-]+\.\w+)\((\d+)\):\s*(error|warning)\s+(C\d+):\s*(.*)", line)
        if m:
            f = re.sub(r"^.*?TIDEProjects[\\/]temp[\\/][^\\/]+[\\/]", "", line[:m.start(2) - 1])
            f = re.sub(r"^.*?[\\/](Platforms[\\/])", r"\1", f)
            if root_hint:
                f = f.replace(str(root_hint) + os.sep, "")
            msgs.append({"file": f.strip(), "line": int(m.group(2)), "level": m.group(3), "code": m.group(4),
                         "message": m.group(5).strip()})
        elif re.search(r"\berror\s*(C\d+)?\s*:|Unable to (open|find)|too large to fit|requires more variable memory", line, re.I):
            msgs.append({"file": "", "line": 0, "level": "error", "code": "", "message": line.strip()})
    return msgs


# ---------- what an error means and what to do (shown under every error; full catalog: references/tide.md §5) ----------

HINTS = [
    (r"unresolved address '\?F:(\w+)'",
     "процедура {0} объявлена (declare), но не написана. Добавьте её тело. Для callback_* библиотеки - пустая "
     "заготовка: sub {0}(...) / end sub с аргументами как в .tbh библиотеки (python3 scripts/tibbo_new.py делает их сам)"),
    (r"address '\?[VF]:(\w+)' is already defined",
     "имя {0} уже занято - так называется переменная или процедура подключённой библиотеки (или оно объявлено "
     "через dim в двух файлах). Переименуйте своё; общую переменную объявляют dim в одном .tbs и declare в global.tbh"),
    (r"undeclared identifier 'wln_check_association'",
     "на платформах с Wi-Fi библиотека dhcp требует библиотеку wln: добавьте wln\\trunk\\wln.tbs и wln.tbh в проект "
     "(location = commonlib), include \"wln\\trunk\\wln.tbh\" перед dhcp.tbh и её callback_wln_* (tibbo_new.py --libs dhcp)"),
    (r"unable to find include file '.*?([\w]+)[\\/]trunk[\\/]",
     "файл библиотеки {0} не найден: в секции [fileN] проекта у файлов библиотек Tibbo должно быть location = commonlib, "
     "а src_lib_ver - установленная версия (например 2_01_05)"),
    (r"unable to find include file '(.*?)'", "нет файла {0}: добавьте его в папку проекта и секцией [fileN] в .tpr"),
    (r"invalid platform|referes to invalid platform",
     "в .tpr нет строки platform=<точное имя> или такой платформы нет: имена - в references/platforms.md"),
    (r"'(\w+)' is not member of '(\w+)' object",
     "у объекта {1} нет {0} на этой платформе: python3 scripts/tibbo_lint.py --platform подскажет похожее имя; "
     "список - references/tios-api.md"),
    (r"undeclared identifier 'elseif'", "в Tibbo BASIC пишут раздельно: else if ... then ... end if end if, либо select case"),
    (r"undeclared identifier 'return'", "return нет: значение функции присваивают её имени (f = 5), выход - exit function"),
    (r"undeclared identifier '(print|sleep|delay|wait|cstr|cint|int|integer_|printf)'",
     "{0} в Tibbo BASIC нет: вывод - sys.debugprint, пауза - таймер on_sys_timer (не цикл), преобразования - str/val/lval/hex"),
    (r"undeclared identifier '(PL_\w+)'", "константы {0} нет на этой платформе: точные имена - references/platforms.md"),
    (r"undeclared identifier '(\w+)'",
     "{0} не объявлен: нет dim/declare, не подключён .tbh библиотеки (include) или её .tbs не добавлен в проект"),
    (r"string capacity must not exceed 255", "строка не длиннее 255 символов: string(N), N <= 255; длинные данные - по частям"),
    (r"event handlers cannot be called", "обработчик события нельзя вызывать: вынесите код в свою sub и зовите её из обоих мест"),
    (r"recursive calls are not supported", "рекурсии нет (в том числе через цепочку вызовов): перепишите циклом"),
    (r"'(\w+)' already has body", "{0} написан дважды: обработчик события один на проект - объедините код"),
    (r"property '(\w+)' is read-only", "{0} только для чтения: состояние меняют методом (sock.connect, sock.close ...)"),
    (r"expects (\d+) arguments \((\d+) passed\)|argument count mismatch for function '(\w+)'",
     "не то число аргументов: сверить с references/tios-api.md (для on_* событий - точная сигнатура там же)"),
    (r"unknown base", "возможно, строки склеены через &: в Tibbo BASIC это +, а &h1F и &b1010 - числа"),
    (r"'Then' expected|'If' expected|invalid expression",
     "синтаксис: сравнения = <> < >, логика and/or/not (не != && ||), каждый if закрыт end if"),
    (r"too large to fit", "программа больше памяти платформы: уберите лишние библиотеки и ресурсы или возьмите плату с большей памятью"),
    (r"requires more variable memory", "не хватает RAM под переменные: уменьшите массивы и строки (string(32) вместо string)"),
]


def hint_for(message):
    for pat, text in HINTS:
        m = re.search(pat, message or "", re.I)
        if m:
            return text.format(*[g or "" for g in m.groups()])
    return None


def preflight(tpr):
    """Project mistakes no compiler explains well: checked before any build."""
    text = read_text(tpr)
    project, entries = parse_tpr(text)
    msgs = []
    err = lambda t: msgs.append({"file": tpr.name, "line": 0, "level": "error", "code": None, "message": t})
    if not project.get("platform"):
        err("в [project] нет platform=<имя платформы> (точные имена - references/platforms.md)")
    for e in entries:
        path = (e.get("path") or "").strip()
        if not path:
            continue
        local = (tpr.parent / path.replace("\\", "/")).is_file()
        lib = (e.get("location") or "").strip().lower() in ("commonlib", "library")
        if local or lib:
            continue
        if re.search(r"[\\/]trunk[\\/]", path):
            err("%s - файл библиотеки Tibbo, но у него нет location = commonlib: добавьте эту строку в его секцию "
                "[fileN] (и src_lib_ver в [project])" % path)
        else:
            err("%s указан в проекте, но такого файла в папке проекта нет" % path)
    if any((e.get("location") or "").strip().lower() == "commonlib" for e in entries) and not project.get("src_lib_ver"):
        err("в [project] нет src_lib_ver=<версия библиотек>, например 2_01_05")
    return msgs


# ---------- environment ----------

def environment():
    """Where this script (= the agent's shell) runs: windows | wsl | mac | linux, plus sandbox hints."""
    kind = "windows" if os.name == "nt" else "mac" if sys.platform == "darwin" else "linux"
    if kind == "linux":
        try:
            if "microsoft" in open("/proc/sys/kernel/osrelease").read().lower():
                kind = "wsl"
        except OSError:
            pass
    hints = []
    if os.environ.get("SANDBOX"):
        hints.append("gemini-sandbox")          # Gemini CLI started with --sandbox
    if os.environ.get("CODEX_SANDBOX_NETWORK_DISABLED") == "1":
        hints.append("codex-no-network")        # Codex sandbox without network
    if kind in ("linux", "mac") and (Path("/.dockerenv").exists() or os.environ.get("container")):
        hints.append("container")
    return kind, hints


def tide_dir():
    cands = [os.environ.get("TIDE_DIR")]
    for var in ("ProgramFiles(x86)", "ProgramFiles"):
        if os.environ.get(var):
            cands.append(os.path.join(os.environ[var], "Tibbo", "TIDE"))
    cands.append(r"C:\Program Files (x86)\Tibbo\TIDE")
    if environment()[0] == "wsl":
        cands += ["/mnt/c/Program Files (x86)/Tibbo/TIDE", "/mnt/c/Program Files/Tibbo/TIDE"]
    for c in cands:
        if c and Path(c, "Bin", "tmake.exe").is_file():
            return Path(c)
    return None


def platforms_dir(tpr, tide, platform):
    """TIDE 5.04.32+ uses per-project platforms by default: <project>/Platforms/<platform> wins over TIDE's own."""
    own = tpr.parent / "Platforms"
    if platform and (own / platform).is_dir():
        return own, True
    return (tide / "Platforms") if tide else None, False


def tide_info(tide):
    """Version, installed platforms (with bundled TiOS), library versions, WinPcap/Npcap."""
    info = {"version": None, "platforms": {}, "lib_versions": [], "pcap": None, "winpcap_installers": []}
    if not tide:
        return info
    try:
        m = re.search(r"\b(5\.\d+\.\d+)\b", (tide / "whatsnew.html").read_text("utf-8", "replace"))
        info["version"] = m.group(1) if m else None
    except OSError:
        pass
    plat = tide / "Platforms"
    if plat.is_dir():
        for d in sorted(plat.iterdir()):
            if d.is_dir() and (d / (d.name + ".tph")).is_file():
                fw = sorted(x.name for x in (d / "firmware").glob("*.bin")) if (d / "firmware").is_dir() else []
                info["platforms"][d.name] = fw
        if (plat / "src").is_dir():
            info["lib_versions"] = sorted(x.name for x in (plat / "src").iterdir() if x.is_dir())
    info["winpcap_installers"] = sorted(x.name for x in (tide / "Bin").glob("WinPcap*.exe"))
    sysroot = os.environ.get("SystemRoot") or ("/mnt/c/Windows" if environment()[0] == "wsl" else r"C:\Windows")
    for cand in (Path(sysroot, "System32", "Npcap", "wpcap.dll"), Path(sysroot, "System32", "wpcap.dll")):
        if cand.is_file():
            info["pcap"] = "Npcap" if "Npcap" in str(cand) else "WinPcap"
            break
    return info


def known_platforms():
    """Latest platforms and TiOS files from github.com/tibbotech/platforms, as listed in references/platforms.md."""
    out = {}
    try:
        text = (Path(__file__).resolve().parent.parent / "references" / "platforms.md").read_text("utf-8")
    except OSError:
        return out
    for m in re.finditer(r"(?m)^\| ([A-Za-z0-9_]+(?:\([A-Za-z0-9]+\))?) \| [^|]+ \| \d+ \| \d+ \| \d+ \| [^|]* \| ([^|]*?) \|$", text):
        out[m.group(1).lower()] = (m.group(1), sorted(re.findall(r"tios-[^\s,;]+?\.bin", m.group(2))))
    return out


def vtuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


def tios_version(fw_name):
    m = re.search(r"(\d+_\d+_\d+)", fw_name or "")
    return m.group(1).replace("_", ".") if m else None


def project_advice(tpr, tide, info):
    """Facts about THIS project on THIS TIDE and concrete steps for the user."""
    text = read_text(tpr)
    project, _ = parse_tpr(text)
    plat, libv = project.get("platform"), project.get("src_lib_ver")
    debug = project.get("debug", "on").lower() == "on"
    transport = project.get("transport", "udp_broadcast").lower()
    devices = [a for a in tpr_addresses(text) if a.get("platform", "").lower() == (plat or "").lower() and a.get("address")]
    pdir, own = platforms_dir(tpr, tide, plat)
    facts, steps = [], []
    facts.append("Проект: %s, платформа %s, библиотеки %s, сборка %s, связь %s"
                 % (tpr.name, plat or "?", libv or "-", "debug" if debug else "release", transport))
    if own:
        facts.append("У проекта свои платформы: %s (TIDE берёт их, а не системные)" % pdir)
    if tide:
        known = {k.lower(): k for k in info["platforms"]}
        fresh = known_platforms().get((plat or "").lower())
        if plat and plat.lower() not in known and not own:
            steps.append("Платформы %s нет в вашем TIDE%s. %sОбновите TIDE с tibbo.com (Downloads → TIDE) "
                         "или выберите платформу своего устройства: File > Project Settings → Platform."
                         % (plat, (" " + info["version"]) if info["version"] else "",
                            "Она есть в свежих платформах Tibbo (github.com/tibbotech/platforms): можно положить папку "
                            "Platforms оттуда в проект - TIDE 5.04.32+ берёт платформы проекта. " if fresh else ""))
        elif plat and plat.lower() in known:
            fw = info["platforms"][known[plat.lower()]]
            if fw:
                facts.append("TiOS для %s в этом TIDE: %s (%s)" % (plat, tios_version(fw[-1]), fw[-1]))
                newest = max((f for f in (fresh[1] if fresh else [])), key=lambda f: vtuple(tios_version(f)), default=None)
                if newest and vtuple(tios_version(newest)) > vtuple(tios_version(fw[-1])):
                    steps.append("У Tibbo есть TiOS новее, чем в вашем TIDE: %s (в TIDE %s). Обновите TIDE с tibbo.com "
                                 "или возьмите файл из github.com/tibbotech/platforms (Platforms\\%s\\firmware); "
                                 "обновлять TiOS устройства стоит, если нужны исправления новой версии."
                                 % (tios_version(newest), tios_version(fw[-1]), known[plat.lower()]))
                steps.append("На устройстве должна стоять TiOS, подходящая к платформе TIDE (.tpc её не содержит). "
                             "Если TIDE при загрузке пишет о несовпадении версий: Device Explorer → устройство → "
                             "Upload... → Load Firmware Through the Network → файл %s из TIDE\\Platforms\\%s\\firmware."
                             % (fw[-1], known[plat.lower()]))
        plain = [v for v in info["lib_versions"] if re.fullmatch(r"\d+(_\d+)+", v)] or info["lib_versions"]
        if libv and plain and libv not in info["lib_versions"]:
            steps.append("Библиотек версии %s в TIDE нет (есть: %s). File > Project Settings → Source library set: "
                         "выберите установленную, например %s, и пересоберите; при ошибках - сверить вызовы библиотек."
                         % (libv, ", ".join(plain[-4:]), plain[-1]))
        if transport == "udp_winpcap" and not info["pcap"]:
            steps.append("Проект связывается с устройством через WinPcap (так советует Tibbo), а он не установлен. "
                         "Установите %s из TIDE\\Bin (или Npcap с режимом совместимости WinPcap) и перезапустите TIDE; "
                         "либо File > Project Settings → Transport → UDP broadcast." % (info["winpcap_installers"][-1] if info["winpcap_installers"] else "WinPcap"))
    js = node_compiler()
    if js and plat and not own:
        try:   # which TiOS line the Node.js compiler builds this platform for
            real = next(p for p in (js.parents[3] / "platforms" / "Platforms").iterdir() if p.name.lower() == plat.lower())
            tp = (real / (real.name + ".tp")).read_text("latin-1")
            ver = re.search(r"(?mi)^version\s*=\s*(\S+)", tp).group(1)
            facts.append("Компилятор на Node.js собирает эту платформу как %s" % ver)
            fresh = known_platforms().get(plat.lower())
            newest = max((f for f in (fresh[1] if fresh else [])), key=lambda f: vtuple(tios_version(f)), default=None)
            if newest and vtuple(tios_version(newest))[:2] > vtuple(ver.split("-")[-1])[:2]:
                steps.append("У Tibbo уже есть TiOS %s для %s, а компилятор на Node.js (и облачный) собирает для %s. "
                             "Если на устройстве TiOS %s.x - поставьте свежие платформы: python3 scripts/tibbo_build.py "
                             "--setup-node --yes --latest-platforms. Версию на устройстве покажет tibbo_device.py state."
                             % (tios_version(newest), plat, ver.split("-")[-1], tios_version(newest).split(".")[0]))
        except (StopIteration, OSError, AttributeError):
            pass
    if not devices:
        steps.append("Устройство для этого проекта не выбрано: Debug > Select/Manage Target → щёлкнуть устройство → "
                     "Select. Не видно - Refresh; устройство должно быть в том же сегменте сети (через роутер TIDE его "
                     "не найдёт, через коммутатор - найдёт), проверить питание, кабель и брандмауэр Windows для "
                     "tide.exe и tdevexplore.exe.")
    else:
        facts.append("Устройство в проекте: %s (%s)" % (devices[0]["address"], devices[0].get("transport", transport)))
    if debug:
        steps.append("Сборка debug: после загрузки программа ждёт команды из TIDE - Debug > Run (F5). "
                     "Для работы без компьютера: Build mode = Release (панель Debug или File > Project Settings), "
                     "затем Build > Rebuild All and Upload.")
    else:
        steps.append("Сборка release: программа запустится сама после загрузки и при каждом включении; "
                     "sys.debugprint и точки останова не работают. Для отладки - Build mode = Debug.")
    return {"project": tpr.name, "platform": plat, "src_lib_ver": libv, "debug": debug, "transport": transport,
            "device": devices[0]["address"] if devices else None, "own_platforms": own, "facts": facts, "steps": steps}


def winpath(p):
    """Path as the Windows tools of TIDE see it (WSL: /mnt/c/... -> C:\\...)."""
    if environment()[0] != "wsl":
        return str(p)
    r = subprocess.run(["wslpath", "-w", str(p)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return r.stdout.decode("utf-8", "replace").strip() or str(p)


def cloud_consent():
    return os.environ.get("TIBBO_CLOUD_BUILD", "").lower() in ("1", "yes", "true", "on")


def ssl_context():
    cafile, capath = os.environ.get("SSL_CERT_FILE"), os.environ.get("SSL_CERT_DIR")
    if cafile or capath:
        return ssl.create_default_context(cafile=cafile or None, capath=capath or None)
    for mod in ("truststore", "certifi"):
        try:
            if mod == "truststore":
                import truststore
                return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            import certifi
            return ssl.create_default_context(cafile=certifi.where())
        except Exception:
            continue
    return ssl.create_default_context()


def post(path, body, timeout=300):
    headers = {"Accept": "application/json", "Content-Type": "application/json", "User-Agent": "tibbo-skills"}
    if os.environ.get("APPBLOCKS_API_KEY"):
        headers["x-api-key"] = os.environ["APPBLOCKS_API_KEY"]
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_context()) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


# ---------- build ----------

def build_cloud(tpr, debug):
    project, files, library = collect(tpr)
    platform = project.get("platform")
    if not platform:
        raise ValueError("в .tpr нет строки platform=")
    if debug is None:
        debug = project.get("debug", "on").lower() == "on"
    # the build service wants "on"/"off": a JSON boolean (even false) gives a DEBUG build
    st, b = post("/api/projects/build", {"command": "build", "files": files, "debug": "on" if debug else "off",
                                         "project": {"runtime": "tios", "device": platform}})
    try:
        r = json.loads(b)
    except ValueError:
        raise RuntimeError("HTTP %s: %s" % (st, b[:300].decode("utf-8", "replace")))
    msgs = parse_messages(r.get("output") or "")
    ok = 200 <= st < 300 and r.get("status") == "completed"
    tpc = r.get("tpc") or r.get("binary")
    data = bytes(tpc["data"]) if isinstance(tpc, dict) and "data" in tpc else None
    return {"ok": ok, "messages": msgs, "tpc": data, "platform": platform, "debug": debug, "library_files": library,
            "files_sent": len(files)}


def prepared(tpr, project, want, near=False):
    """The .tpr to build: the user's own, or a temporary copy with debug=on/off changed (the project is not touched)."""
    if not want or project.get("debug", "on").lower() == want:
        return tpr, None
    cleanup = Path(tempfile.mkdtemp(prefix=".tibbo_build_", dir=str(tpr.parent) if near else None))
    shutil.copytree(str(tpr.parent), str(cleanup / "p"), ignore=shutil.ignore_patterns(".tibbo_build_*"))
    tpr_used = cleanup / "p" / tpr.name
    raw = re.sub(rb"(?mi)^([ \t]*debug[ \t]*=[ \t]*)\w+", rb"\g<1>" + want.encode(), tpr_used.read_bytes())
    tpr_used.write_bytes(raw)  # bytes: keep the project's own encoding
    return tpr_used, cleanup


# --- Tibbo's own compiler ported to Node.js (github.com/tibbotech/tibbo-basic, branch feature/compiler) ---
NODE_REPO = "https://github.com/tibbotech/tibbo-basic.git"
NODE_BRANCH = os.environ.get("TIBBO_BASIC_BRANCH", "feature/compiler")
NODE_CLI = Path("server", "out", "compiler", "compile-project.js")


def node_home():
    return Path(os.environ.get("TIBBO_BASIC_HOME") or Path.home() / ".tibbo" / "tibbo-basic")


def node_compiler():
    """compile-project.js of tibbo-basic if it is set up and Node.js is installed, else None."""
    if not shutil.which("node"):
        return None
    c = os.environ.get("TIBBO_BASIC_COMPILER")
    for p in ([Path(c), Path(c) / NODE_CLI] if c else []) + [node_home() / NODE_CLI]:
        if p.is_file():
            return p
    return None


def node_version():
    exe = shutil.which("node")
    if not exe:
        return None
    r = subprocess.run([exe, "--version"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return r.stdout.decode("utf-8", "replace").strip() or None


def has_c_sources(entries):
    return any(e.get("type", "").lower() in ("c", "htmlc") or e.get("path", "").lower().endswith(".tc") for e in entries)


def setup_node(yes, latest_platforms=False):
    """Download Tibbo's Node.js compiler from GitHub and build it (git, Node.js 18+ and npm needed)."""
    home = node_home()
    missing = [x for x in ("git", "node", "npm") if not shutil.which(x)]
    if missing:
        print("Для компилятора Tibbo на Node.js нужны: %s (не найдено). Node.js: nodejs.org (LTS), git: git-scm.com."
              % ", ".join(missing))
        return 3
    if not yes:
        print("Будет скачан компилятор Tibbo BASIC с GitHub (%s, ветка %s) с платформами Tibbo\n"
              "и его зависимости из npm, в папку %s (около 200 МБ), затем он будет собран.\n"
              "Спросите пользователя и повторите с --yes." % (NODE_REPO, NODE_BRANCH, home))
        return 3
    npm = shutil.which("npm")
    steps = []
    if (home / ".git").is_dir():
        steps.append((["git", "-C", str(home), "pull", "--ff-only"], None))
    else:
        home.parent.mkdir(parents=True, exist_ok=True)
        steps.append((["git", "clone", "--depth", "1", "-b", NODE_BRANCH, NODE_REPO, str(home)], None))
    steps.append((["git", "-C", str(home), "submodule", "update", "--init", "--depth", "1", "platforms"], None))
    if latest_platforms:   # newest platform files from github.com/tibbotech/platforms instead of the ones the compiler pins
        steps.append((["git", "-C", str(home / "platforms"), "fetch", "--depth", "1", "origin", "HEAD"], None))
        steps.append((["git", "-C", str(home / "platforms"), "checkout", "-q", "FETCH_HEAD"], None))
    steps.append(([npm, "install", "--no-audit", "--no-fund", "--ignore-scripts"], home / "server"))
    steps.append(([npm, "run", "build"], home / "server"))
    for cmd, cwd in steps:
        print("> " + " ".join(cmd[:1] + [str(c) for c in cmd[1:]]))
        r = subprocess.run(cmd, cwd=str(cwd) if cwd else None)
        if r.returncode != 0:
            print("Не получилось (код %d). Проверьте интернет до github.com и registry.npmjs.org." % r.returncode)
            return 4
    if not (home / NODE_CLI).is_file():
        print("Сборка компилятора не дала %s" % (home / NODE_CLI))
        return 4
    print("Готово: компилятор Tibbo на Node.js в %s" % home)
    return 0


NODE_MSG = re.compile(r"^(?P<file>.*?):(?P<line>\d+):(?P<col>\d+): (?P<level>error|warning): (?P<text>.*)$")


def build_node(tpr, debug, js):
    project, entries = parse_tpr(read_text(tpr))
    if has_c_sources(entries):
        raise ValueError("в проекте есть файлы Tibbo C: компилятор на Node.js собирает только Tibbo BASIC "
                         "(соберите через TIDE или облако: --local / --cloud)")
    want = None if debug is None else ("on" if debug else "off")
    tpr_used, cleanup = prepared(tpr, project, want)
    root = tpr_used.parent
    fd, out = tempfile.mkstemp(suffix=".tpc")
    os.close(fd)
    try:
        r = subprocess.run([shutil.which("node"), str(js), str(root), "-o", out],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        text = decode_output(r.stdout)
        msgs = []
        for line in text.splitlines():
            m = NODE_MSG.match(line.strip())
            if not m:
                continue
            f = m.group("file")
            try:
                f = os.path.relpath(f, str(root))
            except ValueError:
                pass
            parts = Path(f).parts if f else ()
            if not f:
                f = None   # linker and project errors come without a file
            elif parts and parts[0] == "..":  # outside the project: platform or library file
                f = "\\".join(parts[parts.index("Platforms"):]) if "Platforms" in parts else parts[-1]
            inner = re.match(r"^.*?\((\d+)\):\s*(error|warning)\s+(C\d+):\s*(.*)$", m.group("text"))
            code, msg = (inner.group(3), inner.group(4)) if inner else (None, m.group("text"))
            msgs.append({"file": f.replace("/", "\\") if f else None, "line": int(m.group("line")),
                         "level": m.group("level"), "code": code, "message": msg})
        if r.returncode != 0 and not any(x["level"] == "error" for x in msgs):
            msgs.append({"file": None, "line": 0, "level": "error", "code": None,
                         "message": (text.strip().splitlines() or ["компилятор завершился с кодом %d" % r.returncode])[-1]})
        data = Path(out).read_bytes() if r.returncode == 0 and os.path.getsize(out) else None
    finally:
        os.unlink(out)
        if cleanup:
            shutil.rmtree(str(cleanup), ignore_errors=True)
    ok = data is not None and not any(m["level"] == "error" for m in msgs)
    return {"ok": ok, "messages": msgs, "tpc": data, "platform": project.get("platform"),
            "debug": (want or project.get("debug", "on")) == "on", "raw_tail": text.strip().splitlines()[-5:]}


def tpc_platform(tpc):
    """Platform and TiOS line written into a .tpc by the linker, e.g. 'TPP3W(G2)-4.02'."""
    m = re.search(rb"\x00([A-Za-z0-9_]+(?:\([A-Za-z0-9]+\))?-\d+\.\d+)\x00", tpc or b"")
    return m.group(1).decode("ascii") if m else None


def build_local(tpr, debug, tide):
    project, entries = parse_tpr(read_text(tpr))
    want = None if debug is None else ("on" if debug else "off")
    # WSL: keep the copy on the Windows disk next to the project, so tmake.exe can open it
    tpr_used, cleanup = prepared(tpr, project, want, near=environment()[0] == "wsl")
    workdir = tpr_used.parent
    pdir, _ = platforms_dir(tpr_used, tide, project.get("platform"))
    # -b: folder with tbc.exe/tlink.exe (tmake looks in the current dir otherwise) - per tibbotech/tibbo-basic AGENTS.md
    cmd = [str(tide / "Bin" / "tmake.exe"), winpath(tpr_used), "-p" + winpath(pdir), "-b" + winpath(tide / "Bin"), "-r"]
    r = subprocess.run(cmd, cwd=str(workdir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = decode_output(r.stdout)
    msgs = parse_messages(out, workdir)
    name = project.get("output") or tpr.stem + ".tpc"
    tpc_path = workdir / name
    data = tpc_path.read_bytes() if tpc_path.is_file() else None
    ok = r.returncode == 0 and data is not None and not any(m["level"] == "error" for m in msgs)
    if cleanup:
        shutil.rmtree(str(cleanup), ignore_errors=True)
    return {"ok": ok, "messages": msgs, "tpc": data, "platform": project.get("platform"),
            "debug": (want or project.get("debug", "on")) == "on", "raw_tail": out.strip().splitlines()[-5:]}


def doctor_report(tpr=None):
    """What can build here and, if something is missing, what exactly the USER has to do."""
    kind, hints = environment()
    tide = tide_dir()
    try:
        post("/api/projects/build", {"command": "ping"}, timeout=20)
        net = None
    except Exception as e:
        net = str(getattr(e, "reason", e))
    consent = cloud_consent()
    js, nver = node_compiler(), node_version()
    actions = []
    if tide:
        missing = [x for x in ("tmake.exe", "tupload.exe") if not (tide / "Bin" / x).is_file()]
        if missing:
            actions.append("В TIDE нет %s: переустановите TIDE с tibbo.com." % ", ".join(missing))
        actions.append("Агент попросит разрешение запустить python (а он - tmake.exe из TIDE): разрешите. "
                       "Чтобы не спрашивал каждый раз - добавьте эту команду в разрешённые в настройках агента.")
        if kind == "wsl":
            actions.append("Агент работает в WSL: TIDE вызывается через Windows (экспериментально). "
                           "Проект держите на диске Windows (/mnt/c/...), не в домашней папке Linux.")
    elif kind == "windows":
        actions.append("TIDE не найден. Установите TIDE (tibbo.com → Downloads) или, если он стоит не в "
                       "C:\\Program Files (x86)\\Tibbo\\TIDE, задайте переменную TIDE_DIR с путём к нему "
                       "и перезапустите агента.")
    elif kind == "wsl":
        actions.append("TIDE не найден на диске C:. Задайте TIDE_DIR=/mnt/<диск>/<путь к TIDE> и перезапустите агента.")
    elif not js:
        where = "в контейнере или облачной песочнице" if "container" in hints else "не на Windows"
        actions.append("Агент работает %s: TIDE этого пользователя отсюда недоступен. Варианты: "
                       "(1) компилятор Tibbo на Node.js прямо здесь (Tibbo BASIC, код никуда не уходит); "
                       "(2) облачный компилятор Tibbo - с согласия; (3) запустить агента на Windows-компьютере "
                       "с TIDE; (4) пользователь сам собирает в TIDE и присылает вывод Output." % where)
    if "gemini-sandbox" in hints:
        actions.append("Gemini CLI запущен в песочнице (--sandbox): папки Windows и TIDE ему не видны. "
                       "Для локальной сборки запустите gemini без --sandbox.")
    if not tide and not js:
        if nver and shutil.which("git"):
            actions.append("Быстрая сборка без TIDE и без отправки кода: компилятор Tibbo на Node.js (только Tibbo "
                           "BASIC). Установить с согласия пользователя: python3 scripts/tibbo_build.py --setup-node "
                           "--yes (скачает с GitHub около 200 МБ, около минуты).")
        else:
            actions.append("Для сборки без TIDE и без отправки кода можно поставить компилятор Tibbo на Node.js "
                           "(только Tibbo BASIC): нужны Node.js 18+ (nodejs.org, LTS) и git (git-scm.com), затем "
                           "python3 scripts/tibbo_build.py --setup-node --yes.")
    if not tide and not js:
        if net:
            if "codex-no-network" in hints:
                actions.append("Песочница Codex без сети: для облачной сборки разрешите сеть "
                               "(config.toml: [sandbox_workspace_write] network_access = true) или одобрите команду вне песочницы.")
            else:
                actions.append("Нет связи с %s (%s). Для облачной сборки нужен доступ к этому адресу: "
                               "в облачной песочнице агента - добавить домен api.appblocks.io в разрешённые "
                               "(в организации это делает администратор), на компьютере - проверить прокси и сертификаты "
                               "(pip install truststore)." % (BASE, net))
        elif not consent:
            actions.append("Для облачной сборки нужно согласие пользователя: файлы проекта уйдут на сервер Tibbo "
                           "(api.appblocks.io). Спросить один раз; на все проекты - переменная TIBBO_CLOUD_BUILD=yes.")
    cloud_mode = "cloud" if not net and consent else "cloud-after-consent" if not net else "none"
    mode = "node" if js else "local" if tide else cloud_mode            # checking code
    firmware_mode = "local" if tide else "node" if js else cloud_mode   # .tpc for a device
    info = tide_info(tide)
    advice = project_advice(tpr, tide, info) if tpr else None
    return {"tide_version": info["version"], "tide_platforms": len(info["platforms"]),
            "tide_lib_versions": info["lib_versions"], "pcap": info["pcap"], "project_advice": advice,
            "python": sys.version.split()[0], "os": kind, "hints": hints, "tide": str(tide) if tide else None,
            "cloud_reachable": net is None, "cloud_error": net, "cloud_consent": consent,
            "upload_possible": bool(tide and (tide / "Bin" / "tupload.exe").is_file()) or tide_proxy_ready(), "mode": mode,
            "firmware_mode": firmware_mode,
            "node": nver, "node_compiler": str(js) if js else None,
            "user_actions": actions}


def doctor(as_json=False, tpr=None):
    r = doctor_report(tpr)
    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    print("Python %s, %s%s" % (r["python"], r["os"], (" (" + ", ".join(r["hints"]) + ")") if r["hints"] else ""))
    print("TIDE на этом компьютере: %s%s" % (r["tide"] or "не найден (локальная сборка недоступна)",
                                           (", версия " + r["tide_version"]) if r["tide_version"] else ""))
    if r["tide"]:
        for exe in ("tmake.exe", "tupload.exe"):
            print("  %-12s %s" % (exe, "есть" if Path(r["tide"], "Bin", exe).is_file() else "НЕТ"))
        print("  Платформы: %d, версии библиотек: %s" % (r["tide_platforms"], ", ".join([v for v in r["tide_lib_versions"] if re.fullmatch(r"\d+(_\d+)+", v)][-4:]) or "-"))
        print("  WinPcap/Npcap: %s" % (r["pcap"] or "не установлен (нужен только для связи udp_winpcap)"))
    print("Компилятор Tibbo на Node.js: %s" % (r["node_compiler"] or ("не установлен (Node.js %s есть)" % r["node"]
                                                                     if r["node"] else "не установлен, Node.js нет")))
    print("Согласие на облачную сборку (TIBBO_CLOUD_BUILD=yes): %s" % ("дано" if r["cloud_consent"] else "нет"))
    print("Облачный компилятор %s: %s" % (BASE, "доступен" if r["cloud_reachable"] else "НЕДОСТУПЕН: " + r["cloud_error"]))
    names = {"local": "локально (TIDE)", "node": "компилятором Tibbo на Node.js", "cloud": "в облаке",
             "cloud-after-consent": "в облаке - после согласия пользователя", "none": "НЕВОЗМОЖНА отсюда"}
    print("Сборка будет: проверка кода - %s; прошивка для устройства - %s%s" % (
        names[r["mode"]], names[r["firmware_mode"]],
        "; Tibbo C - %s" % names["local" if r["tide"] else ("cloud" if r["cloud_consent"] and r["cloud_reachable"]
                                                              else "cloud-after-consent" if r["cloud_reachable"] else "none")]
        if r["node_compiler"] else ""))
    print("Загрузка в устройство: %s" % (("возможна (tupload)" if r["tide"] else "возможна (tide-proxy, экспериментально)")
                                          if r["upload_possible"] else "отсюда невозможна (TIDE или tide-proxy: "
                                          "python3 scripts/tibbo_device.py --setup --yes)"))
    if r["user_actions"]:
        print("Что сделать пользователю:")
        for a in r["user_actions"]:
            print("  - " + a)
    a = r["project_advice"]
    if a:
        print("Ваш проект:")
        for f in a["facts"]:
            print("  " + f)
        print("Рекомендации по TIDE для этого проекта:")
        for i, st in enumerate(a["steps"], 1):
            print("  %d. %s" % (i, st))
    return 0


def tide_proxy_ready():
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import tibbo_device
        return tibbo_device.installed() is not None and bool(shutil.which("node"))
    except Exception:
        return False


def upload(tpc, target, serial, yes):
    tide = tide_dir()
    if not tide or not (tide / "Bin" / "tupload.exe").is_file():
        if not serial and tide_proxy_ready():  # any OS: Tibbo's tide-proxy (experimental)
            import tibbo_device
            print("TIDE не найден: загрузка через tide-proxy Tibbo (экспериментально).")
            return tibbo_device.main(["upload", str(tpc), "--mac", target] + (["--yes"] if yes else []))
        print("Загрузка в устройство: нужен TIDE на Windows (tupload.exe) или tide-proxy Tibbo на любой ОС\n"
              "(с согласия пользователя: python3 scripts/tibbo_device.py --setup --yes).")
        return 3
    if not yes:
        print("Загрузка меняет прошивку устройства %s. Спросите пользователя и повторите с --yes." % target)
        return 3
    loader = "taiko.serialdevice" if serial else "taiko.udpdevice"
    cmd = [str(tide / "Bin" / "tupload.exe"), "--loader", loader, "--target", target, "--app", winpath(tpc)]
    print("Команда: " + " ".join('"%s"' % c if " " in c else c for c in cmd))
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(decode_output(r.stdout).strip())
    return 0 if r.returncode == 0 else 4


def main(argv):
    if not argv or "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0 if argv else 2
    opt = lambda k: argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else None
    if "--doctor" in argv:
        pos = [a for a in argv if not a.startswith("--")]
        try:
            tpr = find_tpr(pos[0]) if pos else None
        except ValueError as e:
            print(e)
            return 2
        return doctor("--json" in argv, tpr)
    if "--upload" in argv:
        if not opt("--upload") or not opt("--target"):
            print("нужно: --upload <файл.tpc> --target <адрес>")
            return 2
        return upload(opt("--upload"), opt("--target"), "--serial" in argv, "--yes" in argv)

    if "--setup-node" in argv:
        return setup_node("--yes" in argv, "--latest-platforms" in argv)
    flags = {"--local", "--node", "--cloud", "--release", "--debug", "--json", "--cloud-ok", "--out", "--firmware"}
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--out")]
    try:
        tpr = find_tpr(pos[0] if pos else ".")
    except ValueError as e:
        print(e)
        return 2
    debug = False if "--release" in argv else (True if "--debug" in argv else None)
    tide = tide_dir()
    js = node_compiler()
    firmware = "--firmware" in argv or "--release" in argv or bool(opt("--out"))
    if "--local" in argv:
        mode = "local"
    elif "--node" in argv:
        mode = "node"
    elif "--cloud" in argv:
        mode = "cloud"
    else:
        c_proj = has_c_sources(parse_tpr(read_text(tpr))[1])
        node_ok = bool(js) and not c_proj
        if firmware:   # a .tpc for a device: the user's own TIDE platforms match what TIDE uploads
            mode = "local" if tide else "node" if node_ok else "cloud"
        else:          # checking code: Node.js compiler is the fastest and the same everywhere
            mode = "node" if node_ok else "local" if tide else "cloud"
    if mode == "node" and not js:
        print("Компилятор Tibbo на Node.js не установлен. Установка (с согласия пользователя):\n"
              "  python3 scripts/tibbo_build.py --setup-node --yes\n"
              "Нужны Node.js 18+ и git. Подробнее: python3 scripts/tibbo_build.py --doctor")
        return 3
    if mode == "local" and not tide:
        print("TIDE не найден. Установите TIDE (Windows) или задайте TIDE_DIR; иначе - облачная сборка (--cloud).\n"
              "Что именно сделать пользователю: python3 scripts/tibbo_build.py --doctor")
        return 3
    if mode == "cloud" and not ("--cloud-ok" in argv or cloud_consent()):
        print("Облачная сборка отправит файлы проекта на сервер Tibbo (%s).\n"
              "Спросите согласие пользователя, затем повторите с --cloud-ok (или TIBBO_CLOUD_BUILD=yes)." % BASE)
        return 3
    pre = preflight(tpr)
    try:
        if pre:
            p0 = parse_tpr(read_text(tpr))[0]
            res = {"ok": False, "messages": pre, "tpc": None, "platform": p0.get("platform"),
                   "debug": p0.get("debug", "on").lower() == "on"}
            mode = "preflight"
        else:
          res = (build_local(tpr, debug, tide) if mode == "local" else build_node(tpr, debug, js) if mode == "node"
               else build_cloud(tpr, debug))
    except ValueError as e:
        print(e)
        return 2
    except (OSError, RuntimeError, urllib.error.URLError) as e:
        print("Сборка не выполнена: %s\nПодсказка: python3 scripts/tibbo_build.py --doctor" % getattr(e, "reason", e))
        return 4

    name = parse_tpr(read_text(tpr))[0].get("output") or tpr.stem + ".tpc"
    out = opt("--out") or str(tpr.parent / name)
    if res["ok"] and res["tpc"]:
        Path(out).write_bytes(res["tpc"])
    for m in res["messages"]:
        if m["level"] == "error":
            m["hint"] = hint_for(m["message"])
    errors = [m for m in res["messages"] if m["level"] == "error"]
    built_for = tpc_platform(res["tpc"]) if res["ok"] else None
    warnings = [m for m in res["messages"] if m["level"] == "warning"]
    if "--json" in argv:
        print(json.dumps({"mode": mode, "ok": res["ok"], "platform": res["platform"], "debug": res["debug"],
                          "errors": errors, "warnings": warnings, "tpc": out if res["ok"] else None,
                          "tpc_bytes": len(res["tpc"] or b""), "built_for": built_for, "firmware": firmware,
                          "library_files": res.get("library_files", [])},
                         ensure_ascii=False, indent=1))
    else:
        print("Сборка: %s, %s, %s" % ({"local": "TIDE на этом компьютере", "node": "компилятор Tibbo на Node.js (без TIDE, "
                                       "код не покидает компьютер)", "cloud": "облачный компилятор Tibbo",
                                       "preflight": "не начата - ошибки в файле проекта"}[mode],
                                      res["platform"], "debug" if res["debug"] else "release"))
        for m in res["messages"]:
            tag = "[ОШИБКА]" if m["level"] == "error" else "[ВНИМАНИЕ]"
            where = "%s(%d): " % (m["file"], m["line"]) if m["file"] else ""
            print("%s%s %s%s" % (where, tag, (m["code"] + " ") if m.get("code") else "", m["message"]))
            if m.get("hint"):
                print("    что делать: " + m["hint"])
        if res.get("library_files"):
            print("Библиотеки TIDE (берёт компилятор): " + ", ".join(res["library_files"][:6]) +
                  (" ..." if len(res["library_files"]) > 6 else ""))
        if res["ok"]:
            print("Компиляция: OK, ошибок 0, предупреждений %d, .tpc %d байт%s" % (
                len(warnings), len(res["tpc"] or b""), " -> " + out))
            if built_for:
                print("Собрано для: %s (платформа и старшая версия TiOS)" % built_for)
            if res["debug"]:
                print("Это debug-сборка: в устройстве она ждёт команд TIDE. Для работы без TIDE - --release.")
            if firmware and mode != "local":
                print("Прошивка собрана без TIDE пользователя (платформы %s). Перед загрузкой сверьте TiOS устройства "
                      "(Device Explorer) с версией выше; не совпадает - соберите в TIDE или обновите TiOS."
                      % ("с GitHub Tibbo" if mode == "node" else "облака Tibbo"))
        else:
            print("Компиляция: ОШИБКА (ошибок: %d)" % len(errors))
            if not errors and res.get("raw_tail"):
                print("\n".join(res["raw_tail"]))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
