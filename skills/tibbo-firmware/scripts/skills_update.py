#!/usr/bin/env python3
"""Update the Tibbo skills (tibbo-firmware + appblocks) in place to the latest release.
Обновление скиллов Tibbo (tibbo-firmware + appblocks) до последнего релиза - прямо в папке, где они стоят.

Works for any agent that keeps skills in a folder: Codex, Gemini CLI, Kimi Code, Deep Code, OpenCode, Cursor,
Claude Code (manual install). Ask your agent "update the Tibbo skills" or run it yourself:

  python3 <skills folder>/tibbo-firmware/scripts/skills_update.py --check   # installed vs latest version
  python3 <skills folder>/tibbo-firmware/scripts/skills_update.py           # update both skills
  python3 .../skills_update.py --from <folder with tibbo-firmware.zip and appblocks.zip>   # without internet access to GitHub
  python3 .../skills_update.py --force                                      # reinstall even if up to date

Not for: Claude apps (upload the new zips in Customize -> Skills), the Claude Code plugin
(/plugin marketplace update scancode, then /plugin update tibbo-skills@scancode), the Kimi app (Word kit).
Exit codes: 0 - done or already up to date, 1 - error, 2 - this install cannot be updated in place.
Python 3.9+, standard library only (optional: truststore or certifi for certificates on Windows).
"""
import io
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

REPO = "SCANCODE-IOT/tibbo-ai-skills"
SKILLS = ["tibbo-firmware", "appblocks"]
API = "https://api.github.com/repos/%s/releases/latest" % REPO
UA = {"User-Agent": "tibbo-skills-updater", "Accept": "application/vnd.github+json"}


def ssl_context():
    cafile, capath = os.environ.get("SSL_CERT_FILE"), os.environ.get("SSL_CERT_DIR")
    if cafile or capath:
        return ssl.create_default_context(cafile=cafile or None, capath=capath or None)
    try:
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    except Exception:
        pass
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def fetch(url, accept=None):
    headers = dict(UA)
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ssl_context(), timeout=60) as r:
        return r.read()


def version_of(skill_dir):
    try:
        text = (Path(skill_dir) / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return None
    m = re.search(r'^\s*version:\s*"?([0-9][0-9.]*)"?', text, re.M)
    return m.group(1) if m else "1.x"


def vtuple(v):
    try:
        return tuple(int(x) for x in v.split("."))
    except Exception:
        return (0,)


def skills_root():
    return Path(__file__).resolve().parents[2]


def where_installed(root):
    """Say why an in-place update is not possible here, or None if it is."""
    p = str(root).replace("\\", "/")
    if "/.claude/plugins/" in p:
        return ("Скиллы стоят как плагин Claude Code. Обновите их там:\n"
                "  /plugin marketplace update scancode\n  /plugin update tibbo-skills@scancode\n"
                "и перезапустите Claude Code.")
    if not os.access(str(root), os.W_OK):
        return ("Папка скиллов только для чтения (так бывает в приложениях Claude: claude.ai, desktop).\n"
                "Скачайте tibbo-firmware.zip и appblocks.zip из последнего релиза\n"
                "https://github.com/%s/releases/latest и загрузите их заново: Customize -> Skills." % REPO)
    return None


def latest_release():
    data = json.loads(fetch(API).decode("utf-8"))
    assets = {a["name"]: a["browser_download_url"] for a in data.get("assets", [])}
    missing = [s for s in SKILLS if s + ".zip" not in assets]
    if missing:
        raise RuntimeError("в релизе %s нет файлов: %s" % (data.get("tag_name"), ", ".join(m + ".zip" for m in missing)))
    return data["tag_name"].lstrip("v"), {s: assets[s + ".zip"] for s in SKILLS}


def unpack(blob, dest):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for n in z.namelist():
            if n.startswith("/") or ".." in Path(n).parts:
                raise RuntimeError("подозрительный путь в архиве: %s" % n)
        z.extractall(dest)


def install(root, staged):
    """Swap the staged skill folders in; roll back on any error."""
    backups = {}
    try:
        for s in SKILLS:
            target = root / s
            if target.exists():
                bak = root / (".%s.old-%d" % (s, int(time.time())))
                target.rename(bak)
                backups[s] = bak
            shutil.move(str(staged / s), str(target))
    except Exception:
        for s, bak in backups.items():
            if (root / s).exists():
                shutil.rmtree(root / s, ignore_errors=True)
            bak.rename(root / s)
        raise
    for bak in backups.values():
        shutil.rmtree(bak, ignore_errors=True)


def self_test(root):
    py = sys.executable or "python3"
    fw = root / "tibbo-firmware"
    r1 = subprocess.run([py, str(fw / "scripts" / "tps_check.py"), "find", "rs485"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    lint = fw / "scripts" / "tibbo_lint.py"
    r2 = subprocess.run([py, str(lint), str(fw / "tests" / "lint" / "good.tbs")], stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE) if lint.exists() else r1
    return r1.returncode == 0 and r2.returncode == 0


def main(argv):
    check = "--check" in argv
    force = "--force" in argv
    src = argv[argv.index("--from") + 1] if "--from" in argv else None
    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    root = skills_root()
    installed = {s: version_of(root / s) for s in SKILLS}
    print("Папка скиллов: %s" % root)
    for s in SKILLS:
        print("  %-15s установлена версия %s" % (s, installed[s] or "- (нет)"))

    reason = where_installed(root)
    if reason and not check:
        print("\n" + reason)
        return 2

    if src:
        latest, urls = None, None
    else:
        try:
            latest, urls = latest_release()
        except Exception as e:
            print("\nНе удалось узнать последнюю версию на GitHub: %s" % e)
            print("Нет доступа к github.com? Скачайте tibbo-firmware.zip и appblocks.zip из\n"
                  "https://github.com/%s/releases/latest вручную и запустите с --from <папка с архивами>.\n"
                  "Ошибка сертификата на Windows: pip install truststore" % REPO)
            return 1
        print("Последняя версия на GitHub: %s" % latest)
        current = min((vtuple(v) for v in installed.values() if v), default=(0,))
        if all(installed.values()) and vtuple(latest) <= current and not force:
            print("Обновление не нужно: стоит последняя версия.")
            return 0
        if check:
            print("Есть новая версия %s. Обновить: запустите этот скрипт без --check." % latest)
            if reason:
                print(reason)
            return 0
    if check:
        return 0

    with tempfile.TemporaryDirectory(dir=str(root)) as tmp:
        staged = Path(tmp)
        for s in SKILLS:
            if src:
                blob = (Path(src) / (s + ".zip")).read_bytes()
            else:
                print("Скачиваю %s.zip ..." % s)
                blob = fetch(urls[s], accept="application/octet-stream")
            unpack(blob, staged)
            if not (staged / s / "SKILL.md").is_file():
                print("В архиве %s.zip нет %s/SKILL.md - обновление отменено, ничего не изменено." % (s, s))
                return 1
        new = version_of(staged / "tibbo-firmware")
        install(root, staged)
    ok = self_test(root)
    print("Готово: скиллы обновлены до версии %s. Самопроверка: %s" % (new, "ok" if ok else "ОШИБКА"))
    print("Перезапустите агента (или начните новую сессию), чтобы он перечитал скиллы.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
