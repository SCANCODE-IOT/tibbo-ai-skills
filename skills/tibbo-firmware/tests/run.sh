#!/bin/sh
# Regression: expected exit codes of tps_check.py on sample configs
cd "$(dirname "$0")/.." || exit 2
# python3 on Linux/macOS, python on Windows (Git Bash); override with PY=...
if [ -z "$PY" ]; then if python3 -c "" >/dev/null 2>&1; then PY=python3; else PY=python; fi; fi
fail=0
for pair in "autowater 0" "bad_poe_m2_in_s11 1" "gallery_tpp3 0" "gallery_tpp2 0" "good_tpp2 0" "adc_lte 0" "bad_24v 1" "bad_terminal 1" "greenhouse_tpp3 0" "onewire_62_21 0"; do
  set -- $pair
  "$PY" scripts/tps_check.py check "tests/$1.json" >/dev/null; rc=$?
  if [ "$rc" != "$2" ]; then echo "FAIL $1: exit $rc, expected $2"; fail=1; else echo "ok   $1"; fi
done
T=$(mktemp -d)
"$PY" scripts/state_diagram.py tests/autowater.fsm.json "$T/fsm.svg" && grep -q "<svg" "$T/fsm.svg" && echo "ok   state_diagram" || { echo "FAIL state_diagram"; fail=1; }
"$PY" scripts/tps_check.py check tests/gallery_tpp3.json --svg "$T/b.svg" >/dev/null && grep -q "Подключение к CPU" "$T/b.svg" && echo "ok   board svg" || { echo "FAIL board svg"; fail=1; }
"$PY" scripts/tps_check.py board "TPP2W(G2)" | grep -q "PL_IO_NUM_9_TX0" && echo "ok   board cmd" || { echo "FAIL board cmd"; fail=1; }
"$PY" scripts/tps_check.py find rs485 | grep -q "#05" && echo "ok   find cmd" || { echo "FAIL find cmd"; fail=1; }
"$PY" scripts/tps_check.py tibbit 12 | grep -q '"model": "12"' && echo "ok   tibbit cmd" || { echo "FAIL tibbit cmd"; fail=1; }
out=$("$PY" scripts/tps_check.py check tests/editor_rules.json)
echo "$out" | grep -q "RF-разъём #37 в S13" && echo "$out" | grep -q "два #21 в S2 и S4" && echo "$out" | grep -q "#02 занимает два M-сокета" \
  && echo "ok   editor socket rules" || { echo "FAIL editor socket rules"; fail=1; }
# AppBlocks canvas warnings (yellow triangles): docs-allowed but editor-rejected pairs, C sensors without #00-3
out=$("$PY" scripts/tps_check.py check tests/ab_incorrect_pair.json)
echo "$out" | grep -q "Incorrect pair" && echo "$out" | grep -q "разрешено: #18" && echo "ok   appblocks incorrect pair" || { echo "FAIL appblocks incorrect pair"; fail=1; }
out=$("$PY" scripts/tps_check.py check tests/ab_approved.json)
echo "$out" | grep -q "AppBlocks отметит" && { echo "FAIL appblocks approved layout flagged"; fail=1; } || echo "ok   appblocks approved layout"
out=$("$PY" scripts/tps_check.py check tests/ab_c_sensor.json)
echo "$out" | grep -q "без #00-3 в S11" && echo "ok   appblocks C sensor" || { echo "FAIL appblocks C sensor"; fail=1; }
"$PY" scripts/ab_pairs.py "TPP2W(G2)" S1=13 S2=20 S3=12 S11=09 S12=18 | grep -q "S3: Incorrect pair" && echo "ok   ab_pairs cli" || { echo "FAIL ab_pairs cli"; fail=1; }
# a cp1251 console (Windows) must not break the output: run without PYTHONUTF8
encfail=0
for cmd in "check tests/gallery_tpp3.json" "board TPP3W(G2)" "find реле" "tibbit 12"; do
  env -u PYTHONUTF8 PYTHONIOENCODING=cp1251 "$PY" scripts/tps_check.py $cmd >/dev/null 2>"$T/err" || { echo "FAIL cp1251 console: tps_check.py $cmd"; cat "$T/err"; encfail=1; }
done
[ "$encfail" = 0 ] && echo "ok   non-UTF-8 console" || fail=1
out=$("$PY" scripts/tps_check.py check tests/onewire_62_21.json)
echo "$out" | grep -q "обслуживает модуль" && { echo "FAIL #62+#21 pairing"; fail=1; } || echo "ok   #62+#21 pairing"
out=$("$PY" scripts/tps_check.py check tests/greenhouse_tpp3.json)
echo "$out" | grep -q "предупреждений 0" && echo "ok   greenhouse clean" || { echo "FAIL greenhouse"; echo "$out"; fail=1; }
# tibbo_lint.py: API names checked against the TiOS reference
"$PY" scripts/tibbo_lint.py tests/lint/good.tbs --platform "TPP3W(G2)" >/dev/null && echo "ok   lint clean code" || { echo "FAIL lint clean code"; fail=1; }
out=$("$PY" scripts/tibbo_lint.py tests/lint/bad.tbs --platform "TPP3W(G2)"); rc=$?
for want in "sock.conect" "ser.speed" "PL_SSTS_CONECTED" "PL_IO_NUM_99" "elseif" "PL_IO_PORT_NUM_1" "ошибок: 6"; do
  echo "$out" | grep -q "$want" || { echo "FAIL lint missed: $want"; fail=1; }
done
[ "$rc" = 1 ] && echo "ok   lint seeded errors" || { echo "FAIL lint exit code $rc"; fail=1; }
"$PY" scripts/tibbo_lint.py tests/lint/tpp2_adc.tbs --platform "TPP2W(G2)" | grep -q "объекта adc нет на платформе" && echo "ok   lint platform objects" || { echo "FAIL lint platform objects"; fail=1; }
"$PY" scripts/tibbo_lint.py tests/lint/tpp2_adc.tbs >/dev/null && echo "ok   lint without platform" || { echo "FAIL lint without platform"; fail=1; }
env -u PYTHONUTF8 PYTHONIOENCODING=cp1251 "$PY" scripts/tibbo_lint.py tests/lint/bad.tbs >/dev/null 2>"$T/err"; [ $? = 1 ] && echo "ok   lint non-UTF-8 console" || { echo "FAIL lint cp1251"; cat "$T/err"; fail=1; }
# skills_update.py: in-place update from local zips, refusal for plugin installs, broken archive keeps the install
U=$(mktemp -d); mkdir -p "$U/skills" "$U/zips" "$U/bad"
cp -r . "$U/skills/tibbo-firmware"; cp -r ../appblocks "$U/skills/appblocks" 2>/dev/null || mkdir -p "$U/skills/appblocks"
(cd .. && "$PY" -c "import shutil,sys; [shutil.make_archive(sys.argv[1]+'/'+n, 'zip', '.', n) for n in ('tibbo-firmware','appblocks')]" "$U/zips") 2>/dev/null
if [ -f "$U/zips/appblocks.zip" ]; then
  "$PY" "$U/skills/tibbo-firmware/scripts/skills_update.py" --from "$U/zips" >"$U/out" 2>&1 && grep -q "Самопроверка: ok" "$U/out" \
    && echo "ok   skills_update from local zips" || { echo "FAIL skills_update from local zips"; cat "$U/out"; fail=1; }
  (cd "$U/bad" && mkdir x && echo hi > x/a.txt && "$PY" -c "import shutil; shutil.make_archive('tibbo-firmware','zip','.','x'); shutil.copy('tibbo-firmware.zip','appblocks.zip')")
  "$PY" "$U/skills/tibbo-firmware/scripts/skills_update.py" --from "$U/bad" >"$U/out" 2>&1
  [ $? = 1 ] && [ -f "$U/skills/tibbo-firmware/SKILL.md" ] && echo "ok   skills_update keeps install on a bad archive" || { echo "FAIL skills_update bad archive"; cat "$U/out"; fail=1; }
fi
P="$U/.claude/plugins/cache/x/skills"; mkdir -p "$P"; cp -r "$U/skills/tibbo-firmware" "$P/"
"$PY" "$P/tibbo-firmware/scripts/skills_update.py" >"$U/out" 2>&1; rc=$?
[ "$rc" = 2 ] && grep -q "/plugin update" "$U/out" && echo "ok   skills_update refuses plugin installs" || { echo "FAIL skills_update plugin path (rc=$rc)"; cat "$U/out"; fail=1; }
rm -rf "$U"
# tibbo_build.py: offline - consent for the cloud, local build through tmake (test stand-in), errors, release copy
B=$(mktemp -d); cp -r tests/build/proj "$B/proj"
env -u TIBBO_CLOUD_BUILD TIDE_DIR=/nonexistent "$PY" scripts/tibbo_build.py "$B/proj" --cloud >"$B/out" 2>&1; rc=$?
[ "$rc" = 3 ] && grep -q "согласие" "$B/out" && echo "ok   build asks consent before cloud" || { echo "FAIL build consent (rc=$rc)"; cat "$B/out"; fail=1; }
case "$(uname -s)" in MINGW*|MSYS*|CYGWIN*) echo "skip build local (tmake stand-in is a script, Windows runs only real .exe)";; *)
TIDE_DIR="$PWD/tests/build/fake_tide" "$PY" scripts/tibbo_build.py "$B/proj" >"$B/out" 2>&1; rc=$?
[ "$rc" = 0 ] && grep -q "TIDE на этом компьютере" "$B/out" && [ -f "$B/proj/test.tpc" ] && echo "ok   build local (tmake)" || { echo "FAIL build local (rc=$rc)"; cat "$B/out"; fail=1; }
TIDE_DIR="$PWD/tests/build/fake_tide" "$PY" scripts/tibbo_build.py "$B/proj/test.tpr" --release >"$B/out" 2>&1
grep -q "release" "$B/out" && grep -q "debug = on" "$B/proj/test.tpr" && echo "ok   build release keeps the project unchanged" || { echo "FAIL build release"; cat "$B/out"; fail=1; }
sed -i.bak 's/sock.num/sock.nmu/' "$B/proj/main.tbs"
TIDE_DIR="$PWD/tests/build/fake_tide" "$PY" scripts/tibbo_build.py "$B/proj" --json >"$B/out" 2>&1; rc=$?
[ "$rc" = 1 ] && grep -q '"line": 2' "$B/out" && grep -q '"code": "C1013"' "$B/out" && echo "ok   build reports compiler errors" || { echo "FAIL build errors (rc=$rc)"; cat "$B/out"; fail=1; }
;; esac
printf "' resolution +0.25\242C\n" > "$B/proj/legacy.tbs"   # legacy code page byte, even length: must go as raw bytes
"$PY" -c "import sys; sys.path.insert(0,'scripts'); import tibbo_build as t; from pathlib import Path
f={x['name']: x['contents'] for x in t.collect(Path(sys.argv[1]))[1]}
assert isinstance(f['/legacy.tbs'], dict) and 0xa2 in f['/legacy.tbs']['data'], f['/legacy.tbs']
assert isinstance(f['/main.tbs'], str)" "$B/proj/test.tpr" && echo "ok   build sends legacy-encoded sources byte for byte" || { echo "FAIL build legacy encoding"; fail=1; }
"$PY" scripts/tibbo_build.py --upload x.tpc --target 0.1.2.3.4.5 >"$B/out" 2>&1; [ $? = 3 ] && echo "ok   upload needs TIDE and --yes" || { echo "FAIL upload guard"; fail=1; }
rm -rf "$B"
rm -rf "$T"
exit $fail
