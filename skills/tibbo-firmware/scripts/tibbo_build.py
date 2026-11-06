#!/usr/bin/env python3
"""Build a TIDE project (Tibbo BASIC / Tibbo C) with Tibbo's real compiler and show its errors.
Сборка проекта TIDE настоящим компилятором Tibbo: ошибки компилятора и готовый .tpc.

Two ways, chosen automatically:
  local  - TIDE is installed on this Windows computer: runs TIDE's command-line builder tmake.exe.
           The code stays on the computer. Also from WSL (TIDE on /mnt/c, experimental).
  cloud  - any OS, no TIDE: Tibbo's compiler behind AppBlocks (api.appblocks.io). The project files are sent to
           Tibbo's server, so it needs the user's consent: --cloud-ok or TIBBO_CLOUD_BUILD=yes.

Usage:
  python3 scripts/tibbo_build.py <project folder or .tpr> [--local | --cloud] [--release | --debug]
                                 [--out app.tpc] [--json] [--cloud-ok]
  python3 scripts/tibbo_build.py --doctor [--json]   # what is available here and what the USER must do
                                                     # (relay "Что сделать пользователю" to the user as is)
  python3 scripts/tibbo_build.py --upload app.tpc --target <MAC or COM port> [--serial] --yes
                                 # Windows + TIDE: upload to a device with TIDE's tupload.exe (asks first)

Environment: TIDE_DIR (TIDE folder, default C:\\Program Files (x86)\\Tibbo\\TIDE), TIBBO_CLOUD_BUILD=yes (consent for
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
    st, b = post("/api/projects/build", {"command": "build", "files": files, "debug": debug,
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


def build_local(tpr, debug, tide):
    project, entries = parse_tpr(read_text(tpr))
    workdir, cleanup = tpr.parent, None
    want = None if debug is None else ("on" if debug else "off")
    tpr_used = tpr
    if want and project.get("debug", "on").lower() != want:
        # WSL: keep the copy on the Windows disk next to the project, so tmake.exe can open it
        base = tpr.parent if environment()[0] == "wsl" else None
        cleanup = Path(tempfile.mkdtemp(prefix=".tibbo_build_", dir=str(base) if base else None))
        shutil.copytree(str(tpr.parent), str(cleanup / "p"), ignore=shutil.ignore_patterns(".tibbo_build_*"))
        tpr_used = cleanup / "p" / tpr.name
        raw = re.sub(rb"(?mi)^([ \t]*debug[ \t]*=[ \t]*)\w+", rb"\g<1>" + want.encode(), tpr_used.read_bytes())
        tpr_used.write_bytes(raw)  # bytes: keep the project's own encoding
        workdir = tpr_used.parent
    cmd = [str(tide / "Bin" / "tmake.exe"), winpath(tpr_used), "-p" + winpath(tide / "Platforms"), "-r"]
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


def doctor_report():
    """What can build here and, if something is missing, what exactly the USER has to do."""
    kind, hints = environment()
    tide = tide_dir()
    try:
        post("/api/projects/build", {"command": "ping"}, timeout=20)
        net = None
    except Exception as e:
        net = str(getattr(e, "reason", e))
    consent = cloud_consent()
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
    else:
        where = "в контейнере или облачной песочнице" if "container" in hints else "не на Windows"
        actions.append("Агент работает %s: TIDE этого пользователя отсюда недоступен. Варианты: "
                       "(1) запустить агента прямо на Windows-компьютере с TIDE (Claude Code, Codex, Gemini CLI, "
                       "Kimi Code в терминале или VS Code); (2) облачный компилятор Tibbo - с согласия; "
                       "(3) пользователь сам запускает tibbo_build.py или Build в TIDE и присылает вывод." % where)
    if "gemini-sandbox" in hints:
        actions.append("Gemini CLI запущен в песочнице (--sandbox): папки Windows и TIDE ему не видны. "
                       "Для локальной сборки запустите gemini без --sandbox.")
    if not tide:
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
    mode = "local" if tide else ("cloud" if not net and consent else "cloud-after-consent" if not net else "none")
    return {"python": sys.version.split()[0], "os": kind, "hints": hints, "tide": str(tide) if tide else None,
            "cloud_reachable": net is None, "cloud_error": net, "cloud_consent": consent,
            "upload_possible": bool(tide and (tide / "Bin" / "tupload.exe").is_file()), "mode": mode,
            "user_actions": actions}


def doctor(as_json=False):
    r = doctor_report()
    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return 0
    print("Python %s, %s%s" % (r["python"], r["os"], (" (" + ", ".join(r["hints"]) + ")") if r["hints"] else ""))
    print("TIDE на этом компьютере: %s" % (r["tide"] or "не найден (локальная сборка недоступна)"))
    if r["tide"]:
        for exe in ("tmake.exe", "tupload.exe"):
            print("  %-12s %s" % (exe, "есть" if Path(r["tide"], "Bin", exe).is_file() else "НЕТ"))
        print("  Платформы и библиотеки: %s" % Path(r["tide"], "Platforms"))
    print("Согласие на облачную сборку (TIBBO_CLOUD_BUILD=yes): %s" % ("дано" if r["cloud_consent"] else "нет"))
    print("Облачный компилятор %s: %s" % (BASE, "доступен" if r["cloud_reachable"] else "НЕДОСТУПЕН: " + r["cloud_error"]))
    print("Сборка будет: %s" % {"local": "локально (TIDE)", "cloud": "в облаке",
                                "cloud-after-consent": "в облаке - после согласия пользователя",
                                "none": "НЕВОЗМОЖНА отсюда"}[r["mode"]])
    print("Загрузка в устройство: %s" % ("возможна (tupload)" if r["upload_possible"] else "отсюда невозможна"))
    if r["user_actions"]:
        print("Что сделать пользователю:")
        for a in r["user_actions"]:
            print("  - " + a)
    return 0


def upload(tpc, target, serial, yes):
    tide = tide_dir()
    if not tide or not (tide / "Bin" / "tupload.exe").is_file():
        print("Загрузка в устройство возможна только на Windows с установленным TIDE (tupload.exe).")
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
        return doctor("--json" in argv)
    if "--upload" in argv:
        if not opt("--upload") or not opt("--target"):
            print("нужно: --upload <файл.tpc> --target <адрес>")
            return 2
        return upload(opt("--upload"), opt("--target"), "--serial" in argv, "--yes" in argv)

    flags = {"--local", "--cloud", "--release", "--debug", "--json", "--cloud-ok", "--out"}
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--out")]
    try:
        tpr = find_tpr(pos[0] if pos else ".")
    except ValueError as e:
        print(e)
        return 2
    debug = False if "--release" in argv else (True if "--debug" in argv else None)
    tide = tide_dir()
    mode = "local" if "--local" in argv else "cloud" if "--cloud" in argv else ("local" if tide else "cloud")
    if mode == "local" and not tide:
        print("TIDE не найден. Установите TIDE (Windows) или задайте TIDE_DIR; иначе - облачная сборка (--cloud).\n"
              "Что именно сделать пользователю: python3 scripts/tibbo_build.py --doctor")
        return 3
    if mode == "cloud" and not ("--cloud-ok" in argv or cloud_consent()):
        print("Облачная сборка отправит файлы проекта на сервер Tibbo (%s).\n"
              "Спросите согласие пользователя, затем повторите с --cloud-ok (или TIBBO_CLOUD_BUILD=yes)." % BASE)
        return 3
    try:
        res = build_local(tpr, debug, tide) if mode == "local" else build_cloud(tpr, debug)
    except ValueError as e:
        print(e)
        return 2
    except (OSError, RuntimeError, urllib.error.URLError) as e:
        print("Сборка не выполнена: %s\nПодсказка: python3 scripts/tibbo_build.py --doctor" % getattr(e, "reason", e))
        return 4

    out = opt("--out") or str(tpr.with_suffix(".tpc") if mode == "cloud" else "")
    if res["ok"] and res["tpc"] and mode == "cloud" and out:
        Path(out).write_bytes(res["tpc"])
    errors = [m for m in res["messages"] if m["level"] == "error"]
    warnings = [m for m in res["messages"] if m["level"] == "warning"]
    if "--json" in argv:
        print(json.dumps({"mode": mode, "ok": res["ok"], "platform": res["platform"], "debug": res["debug"],
                          "errors": errors, "warnings": warnings, "tpc": out if res["ok"] else None,
                          "tpc_bytes": len(res["tpc"] or b""), "library_files": res.get("library_files", [])},
                         ensure_ascii=False, indent=1))
    else:
        print("Сборка: %s, %s, %s" % ("TIDE на этом компьютере" if mode == "local" else "облачный компилятор Tibbo",
                                      res["platform"], "debug" if res["debug"] else "release"))
        for m in res["messages"]:
            tag = "[ОШИБКА]" if m["level"] == "error" else "[ВНИМАНИЕ]"
            where = "%s(%d): " % (m["file"], m["line"]) if m["file"] else ""
            print("%s%s %s %s" % (where, tag, m["code"], m["message"]))
        if res.get("library_files"):
            print("Библиотеки TIDE (берёт компилятор): " + ", ".join(res["library_files"][:6]) +
                  (" ..." if len(res["library_files"]) > 6 else ""))
        if res["ok"]:
            print("Компиляция: OK, ошибок 0, предупреждений %d, .tpc %d байт%s" % (
                len(warnings), len(res["tpc"] or b""), (" -> " + out) if out and mode == "cloud" else ""))
            if res["debug"]:
                print("Это debug-сборка: в устройстве она ждёт команд TIDE. Для работы без TIDE - --release.")
        else:
            print("Компиляция: ОШИБКА (ошибок: %d)" % len(errors))
            if not errors and res.get("raw_tail"):
                print("\n".join(res["raw_tail"]))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
