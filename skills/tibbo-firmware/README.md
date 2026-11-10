# tibbo-firmware

**English** · [Русский](README.ru.md) · [← All skills](../../README.md)

An agent skill (Claude, Codex, Gemini CLI, Kimi Code, Deep Code and others) for **Tibbo firmware and hardware configuration**: TiOS applications in Tibbo BASIC and Tibbo C,
Tibbo libraries, Tibbit selection, TPS socket layout and power supply checks.

<img src="../../docs/images/tps-board-tpp3.svg" alt="TPS board check" width="720" />

## What it does

| Task | How the skill handles it |
|---|---|
| **Write firmware** | States the assumptions (platform, Tibbits, power, language), starts from one of 13 ready programs or from the project generator (`tibbo_new.py`: libraries with their dependencies, event hooks and callbacks), checks the code against the exact API of the platform (`tibbo_lint.py`) and **compiles it with Tibbo's compiler** (`tibbo_build.py`) until there are no errors. The result is a TIDE project (`.tpr`, `global.tbh`, `main.tbs`, `device.tbs`, `settings.txt`) plus a resource table (sockets, UARTs, I/O lines, buffer pages). |
| **Build and upload** | Compiles with Tibbo's compiler on Node.js (any OS), with your TIDE or - with your consent - in Tibbo's cloud; explains every compiler and linker error; finds devices on the network, uploads and runs the firmware through Tibbo's tide-proxy (experimental). Tells you what to set up for your own case. |
| **Review firmware** | Runs a 34-item checklist - language and memory, event model, resources, network, libraries, hardware, power, storage and reliability - and reports findings as *critical / important / note* with file, procedure and a corrected fragment. |
| **Debug by symptom** | Device hangs, library does nothing, socket refuses connections, data is cut, board resets when a relay switches, ADC reads zero, TLS fails - each with the usual causes. |
| **Choose Tibbits** | Searches the 84-Tibbit catalog, follows a placement procedure (tiles and M/C/H shapes, UART/INT/ADC/PoE sockets) and validates the result with `tps_check.py`. |
| **Check power** | Supply Tibbits #09/#10/#25/#33/#23/#12, input ranges, ±15 V, PoE, board consumption, load limits with a modem and at temperature. Numbers in answers come from the script, not from memory. |
| **Linux boards** | LTPP3(G2): Tibbits, sockets and power are checked like on a TPS; the program is a Linux application (Python, C, Node.js), not Tibbo BASIC - the skill says so and gives the first steps from Tibbo's documentation. |
| **Draw** | The TPS board as in the Tibbo configurator, and state diagrams of firmware built as a state machine. |

AppBlocks-generated TIDE projects are recognised (`APP_ID`, `'****boot****'` markers, `var_<X>_update`):
the skill reviews them like any other project but recommends making changes in AppBlocks itself,
so they survive the next generation.

## Contents

| Path | What is inside |
|---|---|
| `SKILL.md` | Instructions the agent follows: context questions, Tibbo BASIC facts, TiOS execution model, library rules, workflow, review checklist, debugging, visualisation. |
| `references/tios-api.md` | Every property, method, event and enum of TiOS objects: `sys io net sock ser romfile stor fd wln bt tls i2c ssi adc pwm kp lcd beep pat button rtc ppp pppoe`, with G3/WM2000/WS110x differences. |
| `references/platforms.md` | 46 platforms: available objects, ROM/RAM, TiOS version, exact `PL_IO_NUM_*` and line-to-socket mapping, `PLATFORM_ID` symbols. |
| `references/libraries.md` | Tibbo libraries (STG, sock, DHCP, DNS, Wi-Fi, MQTT, HTTP, Modbus, SNTP, cellular, `tbtNN` Tibbit drivers…): `#define` options, API, required `callback_*`. |
| `references/project-and-libs.md` | `.tpr` format, what the generated project looks like, "library → event" hook table, `settings.txt`, Wi-Fi and TLS patterns. |
| `references/recipes.md`, `recipes/` | **13 complete projects** compiled by Tibbo's compiler: TCP server and client, DHCP, Wi-Fi, RS232-to-TCP, Modbus RTU master, MQTT, web server, settings, relays and inputs, SNTP, flash disk log, buttons and LEDs. |
| `references/tide.md` | Building and uploading without the TIDE window: what the user needs depending on where the agent runs, `tmake`/`tupload`, debug and release, **catalog of compiler and linker errors**, TIDE menus. |
| `references/linux.md` | Linux boards LTPP3(G2) and LTPP3: what applies, sockets and lines, logins, system update, PinMux. |
| `references/tibbits.md` | Catalog of 84 Tibbits (checked against docs.tibbo.com, Oct 2026): purpose, lines used, serial/interrupt requirements, power, mating connectors. |
| `references/docs-map.md` | Topic → docs.tibbo.com page and its Russian translation on tibbo.ru/kb. |
| `references/tibbit-selection.md` | Tibbit selection procedure, tiles and shapes, socket capabilities, placement order. |
| `references/power.md` | Power supply rules and common mistakes. |
| `references/github-map.md` | Which `tibbotech` repository to look at for a task (CA-* examples, Modbus, MQTT, TLS, Linux LTPP3). |
| `data/tibbits.json`, `data/boards.json` | Machine-readable Tibbit catalog and board definitions (TPP2, TPP3, LTPP3(G2)) used by the scripts. |
| `data/platform_api.json` | Exact API of 28 platforms dumped from Tibbo's compiler: objects, properties (read/write), methods (argument count), events, enums, optional objects. |
| `data/libraries.json` | 17 libraries bundled with TIDE: files, hooks, callbacks (which are required), dependencies, platforms a library does not build on. |
| `scripts/tibbo_new.py` | Project generator (see below). |
| `scripts/tibbo_build.py` | Build with Tibbo's compiler (see below). |
| `scripts/tibbo_device.py`, `tibbo_device.js` | Devices on the network through tide-proxy (see below). |
| `scripts/tps_check.py` | TPS configuration checker and catalog tool (see below). |
| `scripts/tps_render.py` | Board renderer used by `tps_check.py --svg`. |
| `scripts/state_diagram.py` | State diagram from a short JSON description. |
| `scripts/tibbo_lint.py` | Checks a project against the exact API of its platform and against Tibbo BASIC rules (see below). |
| `data/tios_api.json`, `scripts/build_lint_data.py`, `build_platform_api.py`, `build_lib_data.py` | Data for the linter and the generator, and the scripts that rebuild them. |
| `scripts/skills_update.py` | Updates both skills to the latest release. |
| `scripts/build_data.py` | Rebuilds `data/tibbits.json` from `data/tibbits.src.json`. |
| `tests/` | Sample configurations and code (good and deliberately broken), stand-ins for TIDE, the compiler and a device, and `run.sh`. |

## Tools

All scripts use only the Python standard library. Building and working with devices additionally need Node.js 18+
and git (or TIDE on Windows); the agent installs Tibbo's compiler and tide-proxy only after your "yes".

### `tps_check.py`

```bash
python3 scripts/tps_check.py check cfg.json [--json] [--svg board.svg]   # validate a TPS configuration
python3 scripts/tps_check.py find "rs485 modbus"                         # search the Tibbit catalog
python3 scripts/tps_check.py board "TPP3W(G2)"                           # sockets and PL_IO_NUM_* of a board
python3 scripts/tps_check.py tibbit 25                                   # everything about one Tibbit
```

Exit codes: `0` - no errors, `1` - errors found, `2` - bad input.

Configuration format:

```jsonc
{
  "board": "TPP3W(G2)",          // TPP2W, TPP2W(G2), TPP2W(G3), TPP2N, TPP3W, TPP3W(G2), TPP3W(G3), TPP3N
  "slots": {"S1": "05", "S2": "21", "S9": "25", "S10": "18", "S25": "23"},
                                 // a wide Tibbit is listed once, at its first socket;
                                 // per-slot override: "S9": {"model": "25", "vin": 24}
  "power": {"vin": 24,           // voltage fed to power Tibbits, V
            "ext5v_ma": 0},      // external regulated 5 V supply on the terminal, mA (0 = none)
  "poe_jumpers": "2-3",          // "1-2" = RJ45 power routed to the PoE socket
  "wifi": null,                  // "WA2000" if the Wi-Fi add-on is fitted
  "buzzer": true,
  "ambient_c": 40,               // max temperature inside the enclosure, °C
  "extra_5v_ma": 0               // anything else on the 5 V rail
}
```

What is checked: socket shape and occupancy, line conflicts, UART and interrupt requirements, connectors
next to Tibbits that need them, PoE socket and jumpers, input voltage of each supply, ±15 V for #13/#14,
+5 V budget with derating for modems and temperature.
The SVG shows the board, a "connection to CPU" table, the budget bar and numbered errors.

### `state_diagram.py`

```bash
python3 scripts/state_diagram.py fsm.json fsm.svg
```

```json
{
  "title": "Auto-watering - state machine (0.5 s tick)",
  "states": [
    {"id": "START", "note": "8 samples", "outputs": "pump off", "kind": "init"},
    {"id": "IDLE",  "note": "wait for dry soil", "outputs": "pump off"},
    {"id": "WATER", "outputs": "pump on", "kind": "active"},
    {"id": "FAULT", "note": "pump locked", "kind": "fault"}
  ],
  "transitions": [
    {"from": "START", "to": "IDLE", "label": "8 valid samples"},
    {"from": "IDLE", "to": "WATER", "label": "moisture < threshold"},
    {"from": "*", "to": "FAULT", "label": "sensor out of range"}
  ]
}
```

`kind`: `init` (blue), `normal` (green, default), `active` (orange), `fault` (red). `"from": "*"` means "from any state".

### `tibbo_new.py`

```bash
python3 scripts/tibbo_new.py my_app --platform "TPP3W(G2)" --libs dhcp,settings,mqtt
python3 scripts/tibbo_new.py --list              # libraries and what each one pulls in
python3 scripts/tibbo_new.py --list-platforms
```

Writes a project that compiles as is: `.tpr` (library files with `location = commonlib`, `src_lib_ver`, `defines=` for
objects that are off by default), `global.tbh`, `main.tbs` with every library hook in its event handler and
`device.tbs` with every required callback. Dependencies are resolved (dhcp → wln where the platform has Wi-Fi,
mqtt → sock + dns, tables → filenum + time). Checked by compiling on all 28 platforms with 13 libraries. Refuses
what does not build (a Linux board, mqtt on older platforms) and says why.

### `tibbo_lint.py`

```bash
python3 scripts/tibbo_lint.py my_project/          # platform and file list are read from the .tpr
python3 scripts/tibbo_lint.py main.tbs --platform "TPP3W(G2)" [--json]
```

Catches the usual mistakes of AI models before the compiler does:

- a property, method, constant or object the **chosen platform** does not have (`sock.conect` → "did you mean
  `sock.connect`"), a write to a read-only property, a wrong number of arguments, an object that is switched off
  (with the `defines=` line that switches it on);
- **an invented event name** (`on_button_press`): the compiler accepts it silently and the handler never runs;
  a wrong event signature, the same handler written twice, a handler called directly;
- Tibbo BASIC rules: `elseif`, recursion, `string(300)`, `return`, `print`, `sleep`, `+=`, `!=`, `&&`, `&` for strings,
  types of other languages;
- a required callback of an included library that is missing (a linker error otherwise).

Out of 23 mistakes that Tibbo's compiler reports it finds 20 before the build, plus invented events, which the
compiler does not report at all; no false errors on 15 projects from github.com/tibbotech. Exit codes: `0` - no
errors, `1` - errors, `2` - bad input. The linter does not replace the compiler: types and expressions are checked
by `tibbo_build.py`.

### `tibbo_build.py`

```bash
python3 scripts/tibbo_build.py --doctor [my_project]      # what works on this computer, what you need to do
python3 scripts/tibbo_build.py --setup-node --yes         # install Tibbo's compiler (Node.js 18+, git; once)
python3 scripts/tibbo_build.py my_project [--json]        # check the code: errors as file(line) text + "what to do"
python3 scripts/tibbo_build.py my_project --release --out app.tpc    # firmware for a device
```

Three ways, chosen by the purpose: checking code - Tibbo's compiler ported to Node.js (any OS, Tibbo BASIC, the code
stays on the computer); firmware for a device - your TIDE (`tmake`) when it is installed; Tibbo's cloud build
service - a fallback (Tibbo C without TIDE), only with `--cloud-ok` after the user agrees, because the project is
sent to Tibbo's server. Before the build the `.tpr` is checked; under every error there is a line saying what to do.
The Node.js compiler gave byte-identical `.tpc` files and the same errors as the cloud compiler on 15 tibbotech projects.

### `tibbo_device.py` (experimental)

```bash
python3 scripts/tibbo_device.py --setup --yes     # install Tibbo's tide-proxy (Node.js; once)
python3 scripts/tibbo_device.py list              # devices in the local network
python3 scripts/tibbo_device.py upload app.tpc --mac 0.36.119.87.32.2 --yes --run
```

`list`, `state` and `buzz` are safe; `upload`, `run`, `stop`, `reboot` need `--yes`; TiOS itself is never replaced
without `--allow-tios`. Checked against a stand-in that speaks Tibbo's protocol, not on a real device yet.

## Example prompts

```text
TPP2W(G3), Tibbits: #05 in S1, #03 in S3, #09 in S9. Powered from 24 V. Is this OK?
```

```text
Write firmware for TPP3W(G2) that serves a Modbus TCP slave on port 502 and maps
4 relays (#03 ×2) and 4 inputs (#04) to coils and discrete inputs. Use the STG library for settings.
```

```text
The device stops answering on the network after a few hours. Here is main.tbs. What could it be?
```

## Limits

- **TiOS firmware only.** Linux boards (LTPP3(G2), LTPP3) get hardware checks and first steps (`references/linux.md`), not Tibbo BASIC code.
- **A clean build is not a test.** The compiler checks the language, not the logic and not the hardware: try the firmware on a device. Where the agent cannot run scripts (a web chat) nothing is compiled, and the answer says so.
- **The Node.js compiler builds Tibbo BASIC only** and uses the platform files of its own release (G3 platforms as TiOS 4.01 unless installed with `--latest-platforms`). Tibbo C needs TIDE or the cloud build. Step-by-step debugging stays in TIDE.
- **`tmake`, `tupload` and `tibbo_device.py` were not run on real hardware** - only against stand-ins that follow Tibbo's command line and protocol.
- **TPS boards only for `tps_check.py`.** DS/EM/WM modules are checked by hand against `power.md` and the module datasheet, and the answer says so.
- **Snapshot of November 2026.** For anything missing, the agent reads the page on docs.tibbo.com or the source on github.com/tibbotech.

## Tests

```bash
sh tests/run.sh
```

Configurations with expected exit codes, AppBlocks editor rules, the state diagram, board SVG, `board`/`find`/`tibbit`
commands, `tibbo_lint.py` on clean code and on code with seeded mistakes (`tests/lint/`), the generator, the build
tool with stand-ins for TIDE, the Node.js compiler and a device. When Tibbo's compiler is installed
(`TIBBO_BASIC_HOME`), the suite also compiles the generated projects and all 13 recipes.
