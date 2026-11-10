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
# lint: 17 habits of other languages and platform mistakes, one per line of the fixture
n=$("$PY" scripts/tibbo_lint.py tests/lint/habits --json | "$PY" -c "import json,sys; print(json.load(sys.stdin)['errors'])")
[ "$n" = 17 ] && echo "ok   lint catches 17 of 17 seeded mistakes (platform from the .tpr)" || { echo "FAIL lint habits: $n of 17"; "$PY" scripts/tibbo_lint.py tests/lint/habits; fail=1; }
# tibbo_new.py: a generated project is clean for the linter and the .tpr preflight; refusals are explained
G="$T/gen"; rm -rf "$G"
"$PY" scripts/tibbo_new.py "$G/a" --platform "TPP3W(G2)" --libs dhcp,settings,mqtt >"$T/out" 2>&1 && "$PY" scripts/tibbo_lint.py "$G/a" >"$T/out2" 2>&1 \
  && grep -q "wln" "$T/out" && grep -q "location=commonlib" "$G/a/a.tpr" && grep -q "callback_wln_ok" "$G/a/device.tbs" \
  && echo "ok   new project: libraries, dependencies, callbacks; linter clean" || { echo "FAIL new project"; cat "$T/out" "$T/out2"; fail=1; }
"$PY" scripts/tibbo_new.py "$G/b" --platform "EM1000" --libs tables >"$T/out" 2>&1 && grep -q "OBJECT_FD=FD_ENABLED" "$G/b/b.tpr" && echo "ok   new project switches on optional objects (defines=)" || { echo "FAIL new project defines"; cat "$T/out"; fail=1; }
"$PY" scripts/tibbo_new.py "$G/c" --platform "LTPP3(G2)" >"$T/out" 2>&1; [ $? = 2 ] && grep -q "linux.md" "$T/out" && echo "ok   new project refuses the Linux board" || { echo "FAIL new project LTPP3"; cat "$T/out"; fail=1; }
"$PY" scripts/tibbo_new.py "$G/d" --platform "EM1000" --libs mqtt >"$T/out" 2>&1; [ $? = 2 ] && grep -q "timercountms" "$T/out" && echo "ok   new project refuses a library that does not compile on the platform" || { echo "FAIL new project broken lib"; cat "$T/out"; fail=1; }
sed '/callback_wln_ok/,/^end sub/d' "$G/a/device.tbs" > "$T/dev" && cp "$T/dev" "$G/a/device.tbs"
"$PY" scripts/tibbo_lint.py "$G/a" | grep -q "нет callback_wln_ok" && echo "ok   lint reports a missing library callback" || { echo "FAIL lint missing callback"; fail=1; }
# recipes: every one is clean for the linter; compiled when Tibbo's Node.js compiler is installed
rfail=0; rn=0
for d in recipes/*/; do
  rn=$((rn+1))
  "$PY" scripts/tibbo_lint.py "$d" >"$T/out" 2>&1 || { echo "FAIL recipe lint $d"; cat "$T/out"; rfail=1; }
  grep -q "предупреждений: 0" "$T/out" || { echo "FAIL recipe lint warnings $d"; cat "$T/out"; rfail=1; }
done
[ "$rfail" = 0 ] && [ "$rn" -ge 13 ] && echo "ok   $rn recipes clean for the linter" || fail=1
NH="${TIBBO_BASIC_HOME:-$HOME/.tibbo/tibbo-basic}"
if [ -f "$NH/server/out/compiler/compile-project.js" ] && command -v node >/dev/null 2>&1; then
  rfail=0
  for d in recipes/*/; do
    env TIDE_DIR=/nonexistent "$PY" scripts/tibbo_build.py "$d" --node --out "$T/r.tpc" >"$T/out" 2>&1 || { echo "FAIL recipe build $d"; tail -5 "$T/out"; rfail=1; }
  done
  [ "$rfail" = 0 ] && echo "ok   $rn recipes compile with Tibbo's compiler" || fail=1
else echo "skip recipe compilation (Tibbo's Node.js compiler is not installed)"; fi
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
env -u TIBBO_BASIC_COMPILER TIBBO_BASIC_HOME=/nonexistent TIDE_DIR="$PWD/tests/build/fake_tide" "$PY" scripts/tibbo_build.py "$B/proj" >"$B/out" 2>&1; rc=$?
[ "$rc" = 0 ] && grep -q "TIDE на этом компьютере" "$B/out" && [ -f "$B/proj/test.tpc" ] && echo "ok   build local (tmake)" || { echo "FAIL build local (rc=$rc)"; cat "$B/out"; fail=1; }
env -u TIBBO_BASIC_COMPILER TIBBO_BASIC_HOME=/nonexistent TIDE_DIR="$PWD/tests/build/fake_tide" "$PY" scripts/tibbo_build.py "$B/proj/test.tpr" --release >"$B/out" 2>&1
grep -q "release" "$B/out" && grep -q "debug = on" "$B/proj/test.tpr" && echo "ok   build release keeps the project unchanged" || { echo "FAIL build release"; cat "$B/out"; fail=1; }
sed -i.bak 's/sock.num/sock.nmu/' "$B/proj/main.tbs"
env -u TIBBO_BASIC_COMPILER TIBBO_BASIC_HOME=/nonexistent TIDE_DIR="$PWD/tests/build/fake_tide" "$PY" scripts/tibbo_build.py "$B/proj" --json >"$B/out" 2>&1; rc=$?
[ "$rc" = 1 ] && grep -q '"line": 2' "$B/out" && grep -q '"code": "C1013"' "$B/out" && echo "ok   build reports compiler errors" || { echo "FAIL build errors (rc=$rc)"; cat "$B/out"; fail=1; }
;; esac
# --doctor: says what the USER must do; offline cloud (closed port) must not hang
env -u TIBBO_CLOUD_BUILD -u TIBBO_BASIC_COMPILER TIBBO_BASIC_HOME=/nonexistent TIDE_DIR=/nonexistent APPBLOCKS_BASE=http://127.0.0.1:9 "$PY" scripts/tibbo_build.py --doctor --json >"$B/doc" 2>&1
"$PY" -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); assert d['mode']=='none' and not d['tide'] and d['user_actions'] and any('api.appblocks.io' in a or 'связи' in a for a in d['user_actions']), d" "$B/doc" && echo "ok   doctor tells the user what to do (no TIDE, no network)" || { echo "FAIL doctor no TIDE"; cat "$B/doc"; fail=1; }
env -u TIBBO_BASIC_COMPILER TIBBO_BASIC_HOME=/nonexistent TIDE_DIR="$PWD/tests/build/fake_tide" APPBLOCKS_BASE=http://127.0.0.1:9 "$PY" scripts/tibbo_build.py --doctor >"$B/doc" 2>&1
grep -q "проверка кода - локально (TIDE)" "$B/doc" && grep -q "возможна (tupload)" "$B/doc" && echo "ok   doctor finds TIDE" || { echo "FAIL doctor TIDE"; cat "$B/doc"; fail=1; }
env -u TIBBO_BASIC_COMPILER TIBBO_BASIC_HOME=/nonexistent TIDE_DIR="$PWD/tests/build/fake_tide" APPBLOCKS_BASE=http://127.0.0.1:9 "$PY" scripts/tibbo_build.py --doctor "$B/proj" --json >"$B/doc" 2>&1
"$PY" -c "import json,sys; d=json.load(open(sys.argv[1],encoding='utf-8')); a=d['project_advice']; assert d['tide_version']=='5.04.50' and a['platform']=='TPP3W(G2)' and any('4.02.00' in f for f in a['facts']) and any('Select/Manage Target' in x for x in a['steps']) and any('Debug > Run' in x for x in a['steps']) and any('4.02.02' in x for x in a['steps']), d" "$B/doc" && echo "ok   doctor gives TIDE advice for the project" || { echo "FAIL doctor project advice"; cat "$B/doc"; fail=1; }
# Node.js compiler (tibbotech/tibbo-basic) through a stand-in with the same CLI: errors, release flag, no TIDE needed
if command -v node >/dev/null 2>&1; then
NB="env -u TIBBO_BASIC_COMPILER TIBBO_BASIC_HOME=$PWD/tests/build/fake_node TIDE_DIR=/nonexistent"
$NB "$PY" scripts/tibbo_build.py "$B/proj" --json >"$B/out" 2>&1; rc=$?
[ "$rc" = 1 ] && grep -q '"mode": "node"' "$B/out" && grep -q '"line": 2' "$B/out" && echo "ok   build with the Node.js compiler reports errors" || { echo "FAIL node errors (rc=$rc)"; cat "$B/out"; fail=1; }
cp -r "$B/proj" "$B/ok"; sed 's/sock\.nmu/sock.num/' "$B/proj/main.tbs" > "$B/ok/main.tbs"
$NB "$PY" scripts/tibbo_build.py "$B/ok" --release --out "$B/n.tpc" >"$B/out" 2>&1; rc=$?
[ "$rc" = 0 ] && "$PY" -c "import sys; d=open(sys.argv[1],'rb').read(); assert d[28]==0xe" "$B/n.tpc" && grep -q "debug = on" "$B/ok/test.tpr" && echo "ok   Node.js build --release (project unchanged)" || { echo "FAIL node release (rc=$rc)"; cat "$B/out"; fail=1; }
BOTH="env -u TIBBO_BASIC_COMPILER TIBBO_BASIC_HOME=$PWD/tests/build/fake_node TIDE_DIR=$PWD/tests/build/fake_tide"
$BOTH "$PY" scripts/tibbo_build.py "$B/ok" --json >"$B/out" 2>&1
grep -q '"mode": "node"' "$B/out" && echo "ok   checking code prefers the Node.js compiler over TIDE" || { echo "FAIL check mode"; cat "$B/out"; fail=1; }
$BOTH "$PY" scripts/tibbo_build.py "$B/ok" --release --json >"$B/out" 2>&1
grep -q '"mode": "local"' "$B/out" && echo "ok   firmware for a device prefers the user's TIDE" || { echo "FAIL firmware mode"; cat "$B/out"; fail=1; }
else echo "skip node compiler tests (no Node.js)"; fi
"$PY" scripts/tibbo_build.py --setup-node >"$B/out" 2>&1; [ $? = 3 ] && echo "ok   setup-node needs --yes" || { echo "FAIL setup-node guard"; cat "$B/out"; fail=1; }
# tibbo_device.py: guards (no tide-proxy needed); end-to-end with tide-proxy + a protocol stand-in if installed
D="env TIDE_PROXY_HOME=/nonexistent"
$D "$PY" scripts/tibbo_device.py upload "$B/n.tpc" --mac 0.36.119.87.32.2 >"$B/out" 2>&1; [ $? = 3 ] && grep -q -- "--yes" "$B/out" && echo "ok   device upload needs --yes" || { echo "FAIL device upload guard"; cat "$B/out"; fail=1; }
$D "$PY" scripts/tibbo_device.py state --mac 00:24:77 >"$B/out" 2>&1; [ $? = 2 ] && echo "ok   device checks the MAC format" || { echo "FAIL device mac"; fail=1; }
printf 'x' > "$B/bad.tpc"; $D "$PY" scripts/tibbo_device.py upload "$B/bad.tpc" --mac 0.36.119.87.32.2 --yes >"$B/out" 2>&1; [ $? = 2 ] && echo "ok   device refuses a non-.tpc" || { echo "FAIL device non-tpc"; cat "$B/out"; fail=1; }
$D "$PY" scripts/tibbo_device.py list >"$B/out" 2>&1; [ $? = 3 ] && grep -q -- "--setup --yes" "$B/out" && echo "ok   device without tide-proxy says how to set it up" || { echo "FAIL device setup hint"; cat "$B/out"; fail=1; }
TPH="${TIDE_PROXY_HOME:-$HOME/.tibbo/tide-proxy}"
if [ -f "$TPH/lib/tide-proxy.js" ] && command -v node >/dev/null 2>&1; then
  (cd "$B" && "$PY" "$OLDPWD/tests/build/fake_device.py" --seconds 40 &) ; sleep 1
  "$PY" scripts/tibbo_device.py list --timeout 3 >"$B/out" 2>&1
  grep -q "0.36.119.87.32.2" "$B/out" && echo "ok   device list finds the stand-in" || { echo "FAIL device list"; cat "$B/out"; fail=1; }
  printf 'TBIN\0\0\0\0guid 3e308cda-de34-49d5-8f3c-86e789061779 payload TBIN' > "$B/up.tpc"
  "$PY" scripts/tibbo_device.py upload "$B/up.tpc" --mac 0.36.119.87.32.2 --yes --run >"$B/out" 2>&1; rc=$?
  [ "$rc" = 0 ] && grep -q "Запуск: OK" "$B/out" && "$PY" -c "import sys; a=open(sys.argv[1],'rb').read(); b=open(sys.argv[2],'rb').read(); sys.exit(0 if b[:len(a)] == a else 1)" "$B/up.tpc" "$B/fake_device.tpc" && echo "ok   device upload + run (stand-in got the same bytes)" || { echo "FAIL device upload (rc=$rc)"; cat "$B/out"; fail=1; }
else echo "skip device end-to-end (tide-proxy not installed)"; fi
printf "' resolution +0.25\242C\n" > "$B/proj/legacy.tbs"   # legacy code page byte, even length: must go as raw bytes
"$PY" -c "import sys; sys.path.insert(0,'scripts'); import tibbo_build as t; from pathlib import Path
f={x['name']: x['contents'] for x in t.collect(Path(sys.argv[1]))[1]}
assert isinstance(f['/legacy.tbs'], dict) and 0xa2 in f['/legacy.tbs']['data'], f['/legacy.tbs']
assert isinstance(f['/main.tbs'], str)" "$B/proj/test.tpr" && echo "ok   build sends legacy-encoded sources byte for byte" || { echo "FAIL build legacy encoding"; fail=1; }
"$PY" scripts/tibbo_build.py --upload x.tpc --target 0.1.2.3.4.5 >"$B/out" 2>&1; [ $? = 3 ] && echo "ok   upload needs TIDE and --yes" || { echo "FAIL upload guard"; fail=1; }
rm -rf "$B"
rm -rf "$T"
exit $fail
