#!/usr/bin/env python3
"""Dev tool: build docs/kimi/tibbo-skills-kimi-app.zip - the two skills as Word documents for the Kimi app
(Agent mode -> Skills -> "Convert Office Documents into a Skill"; the app takes up to three files per skill).

The documents are the chat pack knowledge files (tools/build_chat_pack.py), grouped three per skill and converted
with pandoc. Texts of the kit: tools/kimi_kit_src/. Needs pandoc. Run after tools/package.sh:

    sh tools/package.sh && python3 tools/build_kimi_kit.py
"""
import os, shutil, subprocess, sys, tempfile, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "dist", "chat-pack")
SRC = os.path.join(ROOT, "tools", "kimi_kit_src")
OUT = os.path.join(ROOT, "docs", "kimi", "tibbo-skills-kimi-app.zip")
TOP = "Скиллы Tibbo для приложения Kimi"
KIT = [
    ("1 - tibbo-firmware", "tibbo-firmware.txt", [
        ("tibbo-1-правила-tibbit-питание.docx", ["01-firmware-rules-tibbits-power.md", "08-recipes-and-linux.md"]),
        ("tibbo-2-tios-api-платформы.docx", ["04-tios-api.md", "05-platforms.md"]),
        ("tibbo-3-библиотеки-документация.docx", ["06-libraries-and-projects.md", "07-docs-map.md"]),
    ]),
    ("2 - appblocks", "appblocks.txt", [
        ("appblocks-1-правила-редактор.docx", ["02-appblocks-rules.md"]),
        ("appblocks-2-блоки.docx", ["03-appblocks-blocks.md"]),
        ("appblocks-3-железо-tibbit-питание.docx", ["01-firmware-rules-tibbits-power.md"]),
    ]),
]


def main():
    if not shutil.which("pandoc"):
        sys.exit("pandoc is not installed")
    if not os.path.isdir(PACK):
        sys.exit("no dist/chat-pack: run sh tools/package.sh first")
    work = tempfile.mkdtemp()
    top = os.path.join(work, TOP)
    os.makedirs(top)
    shutil.copy(os.path.join(SRC, "how-to.txt"), os.path.join(top, "КАК ЗАВЕСТИ.txt"))
    for folder, about, docs in KIT:
        d = os.path.join(top, folder)
        os.makedirs(d)
        shutil.copy(os.path.join(SRC, about), os.path.join(d, "описание скилла.txt"))
        for name, parts in docs:
            md = os.path.join(work, "in.md")
            with open(md, "w", encoding="utf-8") as f:
                f.write("\n\n".join(open(os.path.join(PACK, p), encoding="utf-8").read() for p in parts))
            subprocess.run(["pandoc", md, "-f", "gfm", "-o", os.path.join(d, name)], check=True)
            if os.path.getsize(os.path.join(d, name)) < 10000:
                sys.exit("%s: suspiciously small" % name)
    if os.path.exists(OUT):
        os.remove(OUT)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(top):
            for fn in sorted(files):
                full = os.path.join(base, fn)
                z.write(full, os.path.relpath(full, work))
    shutil.rmtree(work)
    print("%s  %d KB" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT) // 1024))


if __name__ == "__main__":
    main()
