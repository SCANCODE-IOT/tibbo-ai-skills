#!/bin/sh
# Build upload-ready skill packages: dist/<skill>.zip, each holding one <skill>/ folder with SKILL.md,
# and dist/tibbo-chat-pack.zip for web chats.
# Usage: sh tools/package.sh
set -eu
cd "$(dirname "$0")/.."
rm -rf dist && mkdir -p dist
for dir in skills/*/; do
  name=$(basename "$dir")
  [ -f "$dir/SKILL.md" ] || { echo "skip $name: no SKILL.md"; continue; }
  # the folder name must match the skill name in SKILL.md
  fm=$(sed -n 's/^name:[[:space:]]*//p' "$dir/SKILL.md" | head -1)
  [ "$fm" = "$name" ] || { echo "error: $dir has name '$fm' in SKILL.md" >&2; exit 1; }
  # only text sources of a skill go into the package
  stray=$(cd skills && find "$name" -type f ! -path '*/__pycache__/*' ! -name '*.pyc' ! -name '.DS_Store' \
          ! -name '*.md' ! -name '*.py' ! -name '*.json' ! -name '*.sh' ! -name '*.js' ! -name '*.svg' ! -name '*.png' ! -name '*.tbs')
  [ -z "$stray" ] || { echo "error: unexpected files in $dir: $stray" >&2; exit 1; }
  (cd skills && zip -qr "../dist/$name.zip" "$name" -x '*/__pycache__/*' '*.pyc' '*/.DS_Store')
  echo "dist/$name.zip  $(du -h "dist/$name.zip" | cut -f1)"
done
# chat pack for web chats without skills (ChatGPT, Gemini, Kimi, DeepSeek, GLM); checks its own limits
"${PYTHON:-python3}" tools/build_chat_pack.py
