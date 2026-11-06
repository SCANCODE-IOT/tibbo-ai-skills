#!/usr/bin/env python3
"""Build the chat pack for web chats without skill support (ChatGPT, Gemini, Kimi, DeepSeek, GLM / Z.ai).

Output: dist/chat-pack/ and dist/tibbo-chat-pack.zip
  PROMPT.md                         - instructions (fits the 8000-character limit of a custom GPT)
  01-...07-*.md                     - knowledge files grouped by topic from both skills
  tibbo-tools.zip                   - both skills with their scripts, for chats that can run Python
  README.md                         - how to use the pack (for people; not uploaded to the chat)
Limits checked on every build: PROMPT <= 8000 characters, <= 10 files to upload (Gemini Gem limit),
each knowledge file <= 350 KB, every uploaded file named in PROMPT.md.
Usage: python3 tools/build_chat_pack.py
"""
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills")
FW = os.path.join(SK, "tibbo-firmware")
AB = os.path.join(SK, "appblocks")
OUT = os.path.join(ROOT, "dist", "chat-pack")

GROUPS = [
    ("01-firmware-rules-tibbits-power.md", "Tibbo firmware: rules, checklist, Tibbits, selection, power",
     [(FW, "SKILL.md"), (FW, "references/tibbit-selection.md"), (FW, "references/tibbits.md"), (FW, "references/power.md")]),
    ("02-appblocks-rules.md", "AppBlocks: rules, editor, JSON format, generated code, MQTT, Cloud API",
     [(AB, "SKILL.md"), (AB, "references/editor.md"), (AB, "references/format.md"), (AB, "references/generated-code.md"),
      (AB, "references/mqtt.md"), (AB, "references/api.md")]),
    ("03-appblocks-blocks.md", "AppBlocks: all blocks, features, Tibbit fields, real usage",
     [(AB, "references/blocks.md"), (AB, "references/features.md"), (AB, "references/catalog.md"),
      (AB, "references/catalog-examples.md")]),
    ("04-tios-api.md", "TiOS API: objects, properties, methods, events, enums", [(FW, "references/tios-api.md")]),
    ("05-platforms.md", "Tibbo platforms: objects, memory, PL_IO_NUM_*, PLATFORM_ID", [(FW, "references/platforms.md")]),
    ("06-libraries-and-projects.md", "Tibbo libraries, project format, event hooks, TIDE build and compiler errors, GitHub map",
     [(FW, "references/libraries.md"), (FW, "references/project-and-libs.md"), (FW, "references/tide.md"),
      (FW, "references/github-map.md")]),
    ("07-docs-map.md", "Where to read more: docs.tibbo.com and tibbo.ru/kb", [(FW, "references/docs-map.md")]),
]
MAX_PROMPT, MAX_FILES, MAX_KB = 8000, 10, 350


def strip_frontmatter(text):
    return re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)


def version():
    m = re.search(r'version:\s*"([^"]+)"', open(os.path.join(FW, "SKILL.md"), encoding="utf-8").read())
    return m.group(1) if m else "dev"


def build():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    ver = version()
    shutil.copy(os.path.join(ROOT, "chat-pack", "PROMPT.md"), OUT)
    shutil.copy(os.path.join(ROOT, "chat-pack", "README.md"), OUT)
    for name, title, parts in GROUPS:
        chunks = ["# %s\n\nTibbo Skills %s by Scancode - knowledge file for chats. Sections below keep their original "
                  "file names (skill/file) so the rules can refer to them.\n" % (title, ver)]
        for base, rel in parts:
            skill = os.path.basename(base)
            body = strip_frontmatter(open(os.path.join(base, rel), encoding="utf-8").read()).strip()
            chunks.append("\n\n<!-- ===== %s/%s ===== -->\n\n# [%s/%s]\n\n%s\n" % (skill, rel, skill, rel, body))
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write("".join(chunks))
    with zipfile.ZipFile(os.path.join(OUT, "tibbo-tools.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        for skill in ("tibbo-firmware", "appblocks"):
            for dirpath, dirs, files in os.walk(os.path.join(SK, skill)):
                dirs[:] = [d for d in dirs if d != "__pycache__"]
                for fn in sorted(files):
                    if fn.endswith(".pyc") or fn == ".DS_Store":
                        continue
                    full = os.path.join(dirpath, fn)
                    z.write(full, os.path.relpath(full, SK))
    check()
    zpath = os.path.join(ROOT, "dist", "tibbo-chat-pack.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for fn in sorted(os.listdir(OUT)):
            z.write(os.path.join(OUT, fn), os.path.join("tibbo-chat-pack", fn))
    print("dist/tibbo-chat-pack.zip  %d KB" % (os.path.getsize(zpath) // 1024))


def check():
    prompt = open(os.path.join(OUT, "PROMPT.md"), encoding="utf-8").read()
    upload = [fn for fn in sorted(os.listdir(OUT)) if fn not in ("PROMPT.md", "README.md")]
    errors = []
    if len(prompt) > MAX_PROMPT:
        errors.append("PROMPT.md: %d characters > %d" % (len(prompt), MAX_PROMPT))
    if len(upload) > MAX_FILES:
        errors.append("%d files to upload > %d" % (len(upload), MAX_FILES))
    for fn in upload:
        kb = os.path.getsize(os.path.join(OUT, fn)) / 1024
        if fn.endswith(".md") and kb > MAX_KB:
            errors.append("%s: %.0f KB > %d KB" % (fn, kb, MAX_KB))
        if fn not in prompt:
            errors.append("%s is not named in PROMPT.md" % fn)
        print("  %-38s %5.0f KB" % (fn, kb))
    print("  PROMPT.md: %d characters (limit %d), files to upload: %d (limit %d)" % (len(prompt), MAX_PROMPT, len(upload), MAX_FILES))
    if errors:
        sys.exit("chat pack check failed:\n  " + "\n  ".join(errors))


if __name__ == "__main__":
    build()
