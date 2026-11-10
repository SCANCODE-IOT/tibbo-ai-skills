#!/usr/bin/env python3
"""Work with Tibbo devices on the LAN without TIDE, on any OS: find, upload a .tpc, run/stop, state, buzz, reboot.
Работа с устройствами Tibbo в сети без TIDE, на любой ОС: поиск, загрузка .tpc, запуск/остановка, состояние.

Uses Tibbo's own tide-proxy (github.com/tibbotech/tide-proxy, Node.js) through scripts/tibbo_device.js.
EXPERIMENTAL: built from tide-proxy's code and documented protocol, checked against a protocol stand-in,
not yet on a real device.

Usage:
  python3 scripts/tibbo_device.py --setup [--yes]          # download tide-proxy + npm packages (asks first)
  python3 scripts/tibbo_device.py --doctor                 # Node.js, tide-proxy, network interfaces
  python3 scripts/tibbo_device.py list [--timeout 5] [--json]
  python3 scripts/tibbo_device.py state  --mac 0.36.119.87.32.2
  python3 scripts/tibbo_device.py buzz   --mac 0.36.119.87.32.2            # beeps: "which device is it?"
  python3 scripts/tibbo_device.py upload app.tpc --mac <MAC> --yes [--run] [--allow-tios <tios-*.bin>]
  python3 scripts/tibbo_device.py run|stop --mac <MAC> --yes               # debug builds wait for "run"
  python3 scripts/tibbo_device.py reboot --mac <MAC> --yes

--yes is required for everything that changes what the device does (upload, run, stop, reboot): ask the user first.
TiOS is never reflashed unless --allow-tios <file> is given (tide-proxy would do it when the device refuses
programming mode). The computer must be in the same LAN segment as the device (UDP broadcast, port 65535).
Environment: TIDE_PROXY_HOME (default ~/.tibbo/tide-proxy), TIDE_PROXY_BRANCH (default: repository default).
Exit codes: 0 - done, 1 - device refused / upload failed, 2 - bad input, 3 - not set up / no consent / no device,
4 - tool or network error. Python 3.9+, standard library only.
"""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = "https://github.com/tibbotech/tide-proxy.git"
HERE = Path(__file__).resolve().parent
DRIVER = HERE / "tibbo_device.js"
MAC_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){5}$")


def home():
    return Path(os.environ.get("TIDE_PROXY_HOME") or Path.home() / ".tibbo" / "tide-proxy")


def installed():
    h = home()
    return h if (h / "lib" / "tide-proxy.js").is_file() and (h / "node_modules" / "socket.io-client").is_dir() else None


def setup(yes):
    missing = [x for x in ("git", "node", "npm") if not shutil.which(x)]
    if missing:
        print("Нужны: %s (не найдено). Node.js: nodejs.org (LTS), git: git-scm.com." % ", ".join(missing))
        return 3
    h = home()
    if not yes:
        print("Будет скачан tide-proxy с GitHub Tibbo (%s) и его пакеты npm в %s (около 30 МБ, несколько секунд).\n"
              "Спросите пользователя и повторите с --yes." % (REPO, h))
        return 3
    steps = []
    if (h / ".git").is_dir():
        steps.append(["git", "-C", str(h), "pull", "--ff-only"])
    else:
        h.parent.mkdir(parents=True, exist_ok=True)
        br = os.environ.get("TIDE_PROXY_BRANCH")
        steps.append(["git", "clone", "--depth", "1"] + (["-b", br] if br else []) + [REPO, str(h)])
    # lib/ is committed prebuilt: runtime packages only, no build scripts
    steps.append([shutil.which("npm"), "install", "--omit=dev", "--ignore-scripts", "--no-audit", "--no-fund"])
    for cmd in steps:
        print("> " + " ".join(str(c) for c in cmd))
        r = subprocess.run(cmd, cwd=str(h) if cmd[0] != "git" else None)
        if r.returncode != 0:
            print("Не получилось (код %d). Нужен доступ к github.com и registry.npmjs.org." % r.returncode)
            return 4
    if not installed():
        print("tide-proxy не установился полностью: нет lib/tide-proxy.js или socket.io-client")
        return 4
    print("Готово: tide-proxy в %s" % h)
    return 0


def interfaces():
    """IPv4 addresses of this computer (the proxy broadcasts on every non-loopback one)."""
    try:
        r = subprocess.run([shutil.which("node"), "-e",
                            "const o=require('os').networkInterfaces();console.log(JSON.stringify(Object.entries(o)"
                            ".flatMap(([n,a])=>a.filter(x=>x.family==='IPv4'&&!x.internal).map(x=>[n,x.address,x.netmask]))))"],
                           stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=20)
        return json.loads(r.stdout.decode() or "[]")
    except Exception:
        return []


def doctor():
    node = shutil.which("node")
    h = installed()
    print("Node.js: %s" % (subprocess.run([node, "--version"], stdout=subprocess.PIPE).stdout.decode().strip()
                           if node else "НЕТ (nodejs.org, LTS)"))
    print("tide-proxy: %s" % (h or "не установлен (python3 scripts/tibbo_device.py --setup --yes, с согласия)"))
    ifs = interfaces() if node else []
    print("Сетевые интерфейсы: %s" % (", ".join("%s %s/%s" % tuple(i) for i in ifs) or "не найдено"))
    print("Что сделать пользователю:")
    acts = []
    if not node:
        acts.append("Поставить Node.js LTS с nodejs.org.")
    if not h:
        acts.append("Разрешить установку tide-proxy (около 30 МБ с GitHub Tibbo).")
    acts.append("Компьютер и устройство - в одном сегменте сети (через коммутатор, не через роутер).")
    acts.append("Брандмауэр: разрешить node обмен по UDP (порт 65535). Windows спросит при первом запуске - "
                "разрешить для частной сети; Linux (ufw): sudo ufw allow proto udp from any to any port 65535.")
    acts.append("Облачная песочница агента сеть пользователя не видит: работает только агент на компьютере в той же сети.")
    for a in acts:
        print("  - " + a)
    return 0


def call(request, quiet=False):
    h = installed()
    if not h:
        print("tide-proxy не установлен. С согласия пользователя: python3 scripts/tibbo_device.py --setup --yes")
        return 3, None
    node = shutil.which("node")
    p = subprocess.Popen([node, str(DRIVER), str(h), json.dumps(request)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = None
    for raw in p.stdout:
        line = raw.decode("utf-8", "replace").rstrip()
        if line.startswith("@@PROGRESS "):
            if not quiet:
                print("  загрузка: %d%%" % round(float(line.split()[1]) * 100), flush=True)
        elif line.startswith("@@MESSAGE ") and not quiet:
            print("  tide-proxy: " + line[10:], flush=True)
        elif line.startswith("@@RESULT "):
            result = json.loads(line[9:])
    err = p.stderr.read().decode("utf-8", "replace").strip()
    rc = p.wait()
    if result is None:
        print("tide-proxy завершился без ответа (код %d)%s" % (rc, (": " + err[-500:]) if err else ""))
        return 4, None
    return rc, result


STATE = {0: "остановлена", 1: "на паузе", 2: "работает", -1: "?"}


def show(d):
    return "%-22s %-15s %-28s %s, программа: %s" % (
        d.get("mac", ""), d.get("ip", ""), (d.get("tios") or "")[:28], (d.get("app") or "-"),
        STATE.get(d.get("pcode"), d.get("pcode")))


def main(argv):
    if not argv or "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0 if argv else 2
    opt = lambda k: argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else None
    if "--setup" in argv:
        return setup("--yes" in argv)
    if "--doctor" in argv:
        return doctor()
    action = argv[0]
    mac = opt("--mac")
    if action != "list" and (not mac or not MAC_RE.match(mac)):
        print("нужен --mac в виде 0.36.119.87.32.2 (как в Device Explorer и в list)")
        return 2
    req = {"action": action, "mac": mac, "timeout": float(opt("--timeout") or (5 if action == "list" else 8))}
    if action in ("upload", "run", "stop", "reboot") and "--yes" not in argv:
        what = {"upload": "заменит программу", "run": "запустит программу", "stop": "остановит программу",
                "reboot": "перезагрузит"}[action]
        print("Команда %s устройство %s. Спросите пользователя (что сейчас подключено к выходам) "
              "и повторите с --yes." % (what, mac))
        return 3
    if action == "upload":
        if len(argv) < 2 or not Path(argv[1]).is_file():
            print("нужен файл: upload app.tpc --mac <MAC> --yes")
            return 2
        data = Path(argv[1]).read_bytes()
        if data[:4] != b"TBIN":
            print("%s - не .tpc (нет подписи TBIN)" % argv[1])
            return 2
        req["file"] = str(Path(argv[1]).resolve())
        if opt("--allow-tios"):
            fw = Path(opt("--allow-tios"))
            if not fw.is_file():
                print("нет файла TiOS: %s" % fw)
                return 2
            req["tiosFirmware"] = str(fw.resolve())
    if action not in ("list", "state", "buzz", "upload", "run", "stop", "reboot"):
        print("неизвестная команда: %s" % action)
        return 2

    rc, res = call(req, quiet="--json" in argv)
    if res is None:
        return rc
    if "--json" in argv:
        print(json.dumps(res, ensure_ascii=False, indent=1))
        return rc
    if action == "list":
        devs = res.get("devices", [])
        print("Найдено устройств: %d" % len(devs))
        for d in devs:
            print("  " + show(d))
        if not devs:
            print("Нет ответа. Проверьте: та же сеть (сегмент), питание, брандмауэр для UDP 65535 (--doctor).")
        return 0
    if not res.get("ok"):
        print("Не выполнено: %s" % res.get("error"))
        if res.get("error") == "no_programming_mode":
            print("Устройство не вошло в режим загрузки (возможно, оно в Loader или TiOS не подходит). "
                  "Обновить TiOS можно в TIDE (Device Explorer → Upload...) или здесь с --allow-tios <tios-*.bin> "
                  "- только с согласия пользователя.")
        return rc or 1
    if res.get("device"):
        print(show(res["device"]))
    if action == "upload":
        print("Загрузка: OK")
        if "--run" in argv:
            rc2, res2 = call({"action": "run", "mac": mac, "timeout": 8}, quiet=True)
            print("Запуск: %s" % ("OK" if res2 and res2.get("ok") else "не удалось"))
            if res2 and res2.get("device"):
                print(show(res2["device"]))
        elif len(data) > 28 and data[28] & 1:  # TBIN header flags: bit 0 = debug build
            print("Это debug-сборка: она ждёт команды run - python3 scripts/tibbo_device.py run --mac %s --yes" % mac)
        else:
            print("Release-сборка: программа запускается сама.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
