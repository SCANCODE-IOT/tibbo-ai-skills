# tibbo-firmware

**English** · [Русский](README.ru.md) · [← All skills](../../README.md)

An agent skill (Claude, Codex, Gemini CLI, Kimi Code, Deep Code and others) for **Tibbo firmware and hardware configuration**: TiOS applications in Tibbo BASIC and Tibbo C,
Tibbo libraries, Tibbit selection, TPS socket layout and power supply checks.

<img src="../../docs/images/tps-board-tpp3.svg" alt="TPS board check" width="720" />

## What it does

| Task | How the skill handles it |
|---|---|
| **Write firmware** | States the assumptions (platform, Tibbits, power, language, library version), checks every object, constant and library procedure name against the reference data, produces a TIDE project as files (`global.tbh`, `main.tbs`, `device.tbs`, `settings.txt`, `.tpr`) plus a resource table (sockets, UARTs, I/O lines, buffer pages). |
| **Review firmware** | Runs a 34-item checklist - language and memory, event model, resources, network, libraries, hardware, power, storage and reliability - and reports findings as *critical / important / note* with file, procedure and a corrected fragment. |
| **Debug by symptom** | Device hangs, library does nothing, socket refuses connections, data is cut, board resets when a relay switches, ADC reads zero, TLS fails - each with the usual causes. |
| **Choose Tibbits** | Searches the 84-Tibbit catalog, follows a placement procedure (tiles and M/C/H shapes, UART/INT/ADC/PoE sockets) and validates the result with `tps_check.py`. |
| **Check power** | Supply Tibbits #09/#10/#25/#33/#23/#12, input ranges, ±15 V, PoE, board consumption, load limits with a modem and at temperature. Numbers in answers come from the script, not from memory. |
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
| `references/project-and-libs.md` | `.tpr` format, project skeleton, "library → event" hook table, `settings.txt`, Wi-Fi and TLS patterns. |
| `references/tibbits.md` | Catalog of 84 Tibbits (checked against docs.tibbo.com, Oct 2026): purpose, lines used, serial/interrupt requirements, power, mating connectors. |
| `references/docs-map.md` | Topic → docs.tibbo.com page and its Russian translation on tibbo.ru/kb. |
| `references/tibbit-selection.md` | Tibbit selection procedure, tiles and shapes, socket capabilities, placement order. |
| `references/power.md` | Power supply rules and common mistakes. |
| `references/github-map.md` | Which `tibbotech` repository to look at for a task (CA-* examples, Modbus, MQTT, TLS, Linux LTPP3). |
| `data/tibbits.json`, `data/boards.json` | Machine-readable Tibbit catalog and TPP2/TPP3 board definitions used by the scripts. |
| `scripts/tps_check.py` | TPS configuration checker and catalog tool (see below). |
| `scripts/tps_render.py` | Board renderer used by `tps_check.py --svg`. |
| `scripts/state_diagram.py` | State diagram from a short JSON description. |
| `scripts/tibbo_lint.py` | Checks API names in Tibbo BASIC / C code against the TiOS reference (see below). |
| `data/tios_api.json`, `scripts/build_lint_data.py` | Objects, members, `PL_*` constants and platforms for the linter, and the script that rebuilds them. |
| `scripts/build_data.py` | Rebuilds `data/tibbits.json` from `data/tibbits.src.json`. |
| `tests/` | Sample configurations (good and deliberately broken) and `run.sh`. |

## Tools

All scripts use only the Python standard library.

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

### `tibbo_lint.py`

```bash
python3 scripts/tibbo_lint.py my_project/ --platform "TPP3W(G2)"   # .tbs .tbh .tc .th, folders recursively
python3 scripts/tibbo_lint.py main.tbs --json
```

Catches invented or misspelled API names before TIDE does - the most common mistake of AI models:

- unknown property, method or event of a TiOS object (`sock.conect` → "did you mean `sock.connect`");
- unknown `PL_*` constant (`PL_SSTS_CONECTED`, `PL_IO_NUM_99`);
- with `--platform`: an object or constant the platform does not have (`adc` on TPP2W(G2)); branches
  `#if PLATFORM_ID=…` for other platforms are skipped;
- `elseif` (Tibbo BASIC only has `else if`).

Internal members (declared with `!` in the `.tph` files) give a warning. Exit codes: `0` - no errors, `1` - errors,
`2` - bad input. Checked on 1382 files of Tibbo's own libraries and examples without a single false error.
Library procedures (`dhcp_start`, `mqtt_publish`…) are not checked - compare them with `references/libraries.md`.

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

- **TiOS only.** Linux devices (LTPP3, LTPP3G2, NTIOS) use Linux, C/Node.js and different objects; the skill points this out instead of mixing the two.
- **No compiler.** TIDE is not available to the AI; code is checked statically. The skill never claims that code "compiles".
- **TPS boards only for `tps_check.py`.** DS/EM/WM modules are checked by hand against `power.md` and the module datasheet, and the answer says so.
- **Snapshot of October 2026.** For anything missing, the agent reads the page on docs.tibbo.com or the source on github.com/tibbotech.

## Tests

```bash
sh tests/run.sh
```

Configurations with expected exit codes, AppBlocks editor rules, the state diagram, board SVG, `board`/`find`/`tibbit`
commands, and `tibbo_lint.py` on clean code and on code with seeded mistakes (`tests/lint/`).
