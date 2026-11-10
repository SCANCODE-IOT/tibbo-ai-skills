#!/usr/bin/env python3
"""AppBlocks Cloud API client (docs: appblocks.io/docs/cloud/api, notes in references/api.md).

Key: environment APPBLOCKS_API_KEY (or file in APPBLOCKS_API_KEY_FILE). Never pass it on the command line.
Base: APPBLOCKS_BASE (default https://api.appblocks.io).

Read-only (safe):
  me                                   GET /api/me            -> account + key scopes
  projects [--workspace W] [--search S] [--all]   list projects (node_* stripped by the server)
  project  <id> --out p.json           full project JSON (for ab_tool.py)
  versions <id>                        project versions
  examples                             example projects (API; if it fails — the 78 tutorial/example projects of appblocks.io)
  example  <id|name> --out p.json      one example (API id, or appblocks.io name such as sprinkler5)
  workspaces                           workspaces of the account
  devices  [--workspace W]             devices (name, connected, app, fw)
  device   <deviceId>                  one device (state, variables, changes)
  get <path>                           any GET path
  tls                                  which CA store is used for HTTPS and whether api.appblocks.io verifies
Generate (sends the project to AppBlocks, changes nothing in the account):
  code <project.json> --outdir DIR     POST /api/projects/code -> generated firmware sources
  build <project.json> [--release] [--out prefix]  code + POST /api/projects/build: Tibbo's TIDE compiler (tios),
                                       prints errors/warnings, exit 1 if it does not compile; --out saves prefix.tpc
Write (needs the user's explicit yes for this exact call; add --yes):
  create <project.json> [--workspace W] --yes      POST /api/projects
  update <id> <project.json> --yes                 PUT  /api/projects/:id
"""
import json, os, re, ssl, sys, urllib.request, urllib.error, urllib.parse


def utf8_stdio():
    """Print UTF-8 whatever the console code page is (Windows cp1251/cp1252, pipes in Git Bash)."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

BASE = os.environ.get("APPBLOCKS_BASE", "https://api.appblocks.io").rstrip("/")


def ssl_context():
    """Verified TLS context. Certificate checks are never disabled.

    Order: SSL_CERT_FILE / SSL_CERT_DIR (only that bundle) -> truststore (the OS store, if installed)
    -> certifi (Mozilla bundle, if installed) -> Python's default context.
    """
    cafile, capath = os.environ.get("SSL_CERT_FILE"), os.environ.get("SSL_CERT_DIR")
    if cafile or capath:
        return ssl.create_default_context(cafile=cafile or None, capath=capath or None), \
            f"SSL_CERT_FILE/SSL_CERT_DIR ({cafile or capath})"
    try:
        import truststore
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT), "truststore (хранилище сертификатов ОС)"
    except ImportError:
        pass
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where()), f"certifi ({certifi.where()})"
    except ImportError:
        pass
    return ssl.create_default_context(), "стандартный контекст Python"


CTX, CTX_SOURCE = ssl_context()


def tls_hint(e):
    """Explain CERTIFICATE_VERIFY_FAILED; other connection errors keep the sandbox hint."""
    reason = getattr(e, "reason", e)
    if isinstance(reason, ssl.SSLCertVerificationError) or "CERTIFICATE_VERIFY_FAILED" in str(reason):
        return (f"сертификат сервера не прошёл проверку: {reason}\n"
                f"Хранилище сертификатов: {CTX_SOURCE}. Проверка сертификата не отключается.\n"
                "Если тот же адрес открывается в браузере или curl, у Python не то хранилище корневых сертификатов "
                "(часто на Windows). Варианты:\n"
                "  pip install truststore   - брать сертификаты из хранилища ОС\n"
                "  pip install certifi      - брать актуальный набор Mozilla\n"
                "  SSL_CERT_FILE=<бандл>    - например, C:/Program Files/Git/mingw64/etc/ssl/certs/ca-bundle.crt из Git для Windows\n"
                "Если в сети есть прокси с подменой сертификатов, добавь его корневой сертификат в бандл.\n"
                "Диагностика: python ab_api.py tls")
    return (f"нет соединения: {reason}\n(в облачной песочнице хост может быть закрыт: добавь api.appblocks.io в разрешённые хосты "
            f"или запусти скрипт на компьютере пользователя)")


def key(required=True):
    k = os.environ.get("APPBLOCKS_API_KEY")
    if not k and os.environ.get("APPBLOCKS_API_KEY_FILE"):
        k = open(os.environ["APPBLOCKS_API_KEY_FILE"], encoding="utf-8").read().strip()
    if not k and required:
        sys.exit("нет ключа: задай APPBLOCKS_API_KEY или APPBLOCKS_API_KEY_FILE")
    return k


def call(method, path, body=None, auth=True, raw=False):
    headers = {"Accept": "application/json"}
    if auth:
        headers["x-api-key"] = key()
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120, context=CTX) as r:
            b = r.read()
            st = r.status
    except urllib.error.HTTPError as e:
        b, st = e.read(), e.code
    except urllib.error.URLError as e:
        sys.exit(f"{BASE}: " + tls_hint(e))
    if not (200 <= st < 300):
        sys.exit(f"HTTP {st} {method} {path}: {b[:500].decode('utf-8', 'replace')}")
    if raw:
        return b
    try:
        return json.loads(b) if b else None
    except ValueError:
        return b.decode("utf-8", "replace")


def post_raw(path, body, auth=True):
    """POST that returns (status, bytes) instead of exiting on HTTP errors: the build endpoint answers 500 with the compiler output."""
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if auth:
        headers["x-api-key"] = key()
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(), method="POST", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=300, context=CTX) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except urllib.error.URLError as e:
        sys.exit(f"{BASE}: " + tls_hint(e))


SITE = "https://appblocks.io"


def fetch(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"Accept": "*/*"}), timeout=60, context=CTX) as r:
            return r.read().decode("utf-8")
    except urllib.error.URLError as e:
        sys.exit(f"{url}: " + tls_hint(e))


def site_examples():
    import re
    xml = fetch(f"{SITE}/sitemap.xml")
    names = {u.rstrip("/").split("/")[-1] for u in re.findall(r"<loc>https://appblocks.io/(?:tutorials|examples)/([^<]+)</loc>", xml)
             if "tags" not in u and "page/" not in u}
    return sorted(n for n in names if n not in ("archive", "introduction"))


def call_soft(method, path):
    """like call() but raises RuntimeError instead of exiting (for fallbacks)"""
    headers = {"Accept": "application/json"}
    k = key(False)
    if k:
        headers["x-api-key"] = k
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + path, method=method, headers=headers), timeout=60, context=CTX) as r:
            return json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}")
    except urllib.error.URLError as e:
        raise RuntimeError(tls_hint(e))


def opt(a, name, default=None):
    return a[a.index(name) + 1] if name in a else default


def qs(**kw):
    kw = {k: v for k, v in kw.items() if v not in (None, "")}
    return ("?" + urllib.parse.urlencode(kw)) if kw else ""


def dump(obj, out=None):
    txt = json.dumps(obj, ensure_ascii=False, indent=1)
    if out:
        open(out, "w", encoding="utf-8").write(txt)
        print(f"сохранено: {out}")
    else:
        print(txt[:20000])


def unwrap_project(r):
    if isinstance(r, dict) and "data" in r and isinstance(r["data"], list) and r["data"]:
        return r["data"][0]
    return r


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(2)
    c = a[0]
    if c == "tls":
        print(f"Python {sys.version.split()[0]}, {ssl.OPENSSL_VERSION}")
        print(f"хранилище сертификатов: {CTX_SOURCE}")
        try:
            with urllib.request.urlopen(urllib.request.Request(BASE + "/", method="HEAD"), timeout=30, context=CTX) as r:
                st = r.status
        except urllib.error.HTTPError as e:
            st = e.code
        except urllib.error.URLError as e:
            sys.exit(tls_hint(e))
        print(f"{BASE}: TLS ок (сертификат проверен), HTTP {st}")
        return
    if c == "me":
        dump(call("GET", "/api/me"))
    elif c == "projects":
        start, rows = 0, []
        while True:
            r = call("GET", "/api/projects" + qs(start=start, count=50, workspace=opt(a, "--workspace"), search=opt(a, "--search")))
            rows += r.get("data", [])
            start += 50
            if "--all" not in a or start >= r.get("count", 0):
                break
        print(f"всего: {r.get('count')}")
        for p in rows:
            dev = p.get("device")
            dev = dev.get("name") or dev.get("platform") if isinstance(dev, dict) else dev
            print(f"{p.get('_id')}  {p.get('name')!r:40} {dev}  runtime={p.get('runtime')}  {p.get('updatedAt', '')[:19]}")
    elif c == "project":
        dump(unwrap_project(call("GET", f"/api/projects/{a[1]}")), opt(a, "--out"))
    elif c == "versions":
        r = call("GET", f"/api/projects/{a[1]}/versions")
        if not r.get("data"):
            print("версий нет")
        for v in r.get("data", []):
            print(f"{v.get('_id')}  code={v.get('versionCode')}  {v.get('versionDescription', '')!r}  {v.get('createdAt', '')[:19]}  {v.get('url', '')}")
    elif c == "examples":
        try:
            r = call_soft("GET", "/api/projects/examples" + qs(count=200))
            for e in r.get("data", []):
                print(f"{e.get('id')}  {e.get('name')!r}  {e.get('device')}")
        except RuntimeError as e:
            print(f"API примеров недоступно ({e}); список с appblocks.io:")
            for n in site_examples():
                print(n)
    elif c == "example":
        name = a[1]
        try:
            r = call_soft("GET", f"/api/projects/examples/{name}")
            proj = r.get("project", r) if isinstance(r, dict) else r
        except RuntimeError:
            proj = json.loads(fetch(f"{SITE}/projects/{name}.json"))
        dump(proj, opt(a, "--out"))
    elif c == "workspaces":
        ws = call("GET", "/api/workspaces") or []
        if not ws:
            print("workspaces нет (только личные проекты и устройства)")
        for w in ws:
            print(f"{w.get('_id')}  {w.get('name')}")
    elif c == "devices":
        r = call("GET", "/cgg/devices" + qs(count=100, workspace=opt(a, "--workspace")))
        print(f"всего: {r.get('count')}")
        for d in r.get("data", []):
            s = d.get("state", {})
            print(f"{d.get('deviceId')}  {d.get('name')!r:30} {'онлайн' if s.get('connected') else 'офлайн':7} app={s.get('appName')} v{s.get('appVersion')} fw={s.get('firmwareVersion')}")
    elif c == "device":
        d = call("GET", f"/cgg/devices/{a[1]}")
        if isinstance(d, dict):
            d.pop("key", None)  # MQTT credential: never print
        dump(d)
    elif c == "get":
        r = call("GET", a[1])
        if isinstance(r, dict):
            r.pop("key", None)
        dump(r, opt(a, "--out"))
    elif c == "build":
        proj = json.load(open(a[1], encoding="utf-8"))
        files = call("POST", "/api/projects/code", {"params": {"project": proj, "debug": "--release" not in a}}, auth=bool(key(False)))
        # the build service wants "on"/"off": a JSON boolean (even false) gives a DEBUG build
        body = {"command": "build", "files": files, "debug": "off" if "--release" in a else "on",
                "project": {"runtime": proj.get("runtime") or "tios", "device": proj.get("device")}}
        st, b = post_raw("/api/projects/build", body, auth=bool(key(False)))
        try:
            r = json.loads(b)
        except ValueError:
            sys.exit(f"HTTP {st}: {b[:500].decode('utf-8', 'replace')}")
        out = (r.get("output") or "").replace("\r", "")
        lines = [l for l in out.split("\n") if ("error" in l or "warning" in l) and "C1006" not in l]
        for l in lines:
            print(re.sub(r"^.*?TIDEProjects[\\/]temp[\\/][^\\/]+[\\/]", "", l))
        ok = 200 <= st < 300 and r.get("status") == "completed"
        tpc = r.get("tpc") or r.get("binary")
        if ok and tpc and opt(a, "--out"):
            data = bytes(tpc["data"]) if isinstance(tpc, dict) else tpc.encode("latin-1")
            open(opt(a, "--out") + ".tpc", "wb").write(data)
            print("сохранено:", opt(a, "--out") + ".tpc")
        size = len(tpc["data"]) if isinstance(tpc, dict) and "data" in tpc else None
        print(("компиляция: OK" + (f", {size} байт" if size else "")) if ok else "компиляция: ОШИБКА")
        sys.exit(0 if ok else 1)
    elif c == "code":
        proj = json.load(open(a[1], encoding="utf-8"))
        files = call("POST", "/api/projects/code", {"params": {"project": proj, "debug": True}}, auth=bool(key(False)))
        outdir = opt(a, "--outdir", "generated")
        os.makedirs(outdir, exist_ok=True)
        for f in files:
            p = os.path.join(outdir, f["name"].lstrip("/"))
            os.makedirs(os.path.dirname(p) or outdir, exist_ok=True)
            c = f["contents"]
            if not isinstance(c, str):          # some files (e.g. project.tpr metadata) come back as JSON objects
                c = json.dumps(c, ensure_ascii=False, indent=1)
            open(p, "w", encoding="utf-8").write(c)
            print(p)
    elif c in ("create", "update"):
        if "--yes" not in a:
            sys.exit("запись в аккаунт: сначала покажи пользователю что и куда, получи явное «да», потом повтори с --yes")
        proj = json.load(open(a[1] if c == "create" else a[2], encoding="utf-8"))
        body = {k: proj[k] for k in ("name", "description", "shortDescription", "device", "features", "featureFlags",
                                     "featureFlagMap", "version", "runtime") if k in proj}
        if c == "create":
            if opt(a, "--workspace"):
                body["workspace"] = opt(a, "--workspace")
            r = call("POST", "/api/projects", body)
        else:
            r = call("PUT", f"/api/projects/{a[1]}", body)
        r = unwrap_project(r)
        print("ok:", r.get("_id") if isinstance(r, dict) else r)
    else:
        print(__doc__); sys.exit(2)


if __name__ == "__main__":
    utf8_stdio()
    try:
        main()
    except IndexError:
        print("не хватает аргумента команды\n" + __doc__)
        sys.exit(2)
    except BrokenPipeError:
        pass
