# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), versions follow [Semantic Versioning](https://semver.org/).

## [2.0.0] - 2026-11-06

**Major update: the skills now work beyond Claude** - in ChatGPT / Codex, Gemini, Kimi, DeepSeek and GLM, in coding
agents and in web chats. Nothing changes for Claude users: the technical rules are the same, the install is the same.

### Any agent, any model
- **Agent-neutral instructions.** `SKILL.md` of both skills no longer depends on Claude-only tools or menus (WebFetch,
  Glob, artifacts, claude.ai settings): agents use their own search, web and preview tools, Claude stays one of the
  examples. Frontmatter follows the open [Agent Skills](https://agentskills.io) specification (`license`,
  `compatibility`, `metadata`) and passes the reference validator `skills-ref`.
- **"Order for any agent"** at the top of both `SKILL.md` files: the seven rules that matter most, short enough for
  smaller models - no invented API names, scripts before answers, assumptions first, no "it compiles" claims, and what
  to do when scripts cannot be run (say so and give the user the files and commands).
- **`tools/install.py`** - one installer for Windows, macOS and Linux: both skills into `~/.agents/skills/`
  (Codex CLI / IDE extension, Gemini CLI, Kimi Code, Deep Code, Cline, Zed) and `~/.claude/skills/`, or
  `--agent opencode|cursor|copilot|gemini|kimi|all`, `--project <folder>`, `--uninstall`; self-test from the
  installed copy.
- **Chat pack `tibbo-chat-pack.zip`** for web chats without skills (ChatGPT custom GPT or Project, Gemini Gem, Kimi,
  DeepSeek, GLM / chat.z.ai): `PROMPT.md` (5000 characters, fits the custom GPT limit), seven knowledge files grouped
  by task, `tibbo-tools.zip` with all scripts for ChatGPT's code interpreter or your own computer. Built by
  `tools/build_chat_pack.py`, which checks the limits on every build (prompt <= 8000 characters, <= 10 files for a Gem,
  every file <= 350 KB).
- **Docs:** `docs/INSTALL.md` and `docs/INSTALL.ru.md` - step by step for every AI; READMEs speak of "your AI agent".

### tibbo-firmware
- **New `scripts/tibbo_lint.py`** - checks API names in Tibbo BASIC / C code (`.tbs .tbh .tc .th`): unknown properties,
  methods and events of TiOS objects with "did you mean", invented `PL_*` constants, objects and constants the
  platform does not have (`--platform`, aware of `#if PLATFORM_ID=…` branches), `elseif`; internal `!` members give a
  warning. Data: `data/tios_api.json`, rebuilt by `scripts/build_lint_data.py` from the references (optionally from
  clones of `tibbotech/platforms` and `tibbotech/libraries`). Zero false errors on 1382 files of Tibbo's libraries
  and examples; tests with seeded mistakes in `tests/lint/`.
- **Fixed:** `references/tios-api.md` listed the SSI baud constants cut at the first lowercase letter
  (`PL_SSI_BAUD_100`, `PL_SSI_BAUD_1MH`); the real names are `PL_SSI_BAUD_100kHz` … `PL_SSI_BAUD_1MHz`. Found by the
  new linter.
- The checklist and the writing / review procedure run `tibbo_lint.py` before `tps_check.py`.

### Repository
- CI: installer test on Linux and Windows (Python 3.9-3.14), `skills-ref validate`, chat pack limits.
- Releases carry three files: `tibbo-firmware.zip`, `appblocks.zip`, `tibbo-chat-pack.zip`.

## [1.4.0] - 2026-11-02

Lessons from TOTAL SMART SCHOOL GREENHOUSE 2 (TPP3W(G2), rebuilt from a review of the first greenhouse): limits of the
generated Tibbo BASIC that compile fine but break at run time, the editor's current web console format, and a fresh
snapshot of the AppBlocks editor and its public examples and plugins.

### Both skills
- **A Tibbo BASIC string holds 255 bytes, and MQTT is no exception.** `mqtt_publish` builds the packet as one string
  (topic + data), so a longer message is cut without an error - the first greenhouse lost the tail of its telemetry this
  way. Split telemetry by topic; `MQTT_LARGE_PACKETS` does not help.
- Relay and PWM notes: #06 is rated 16 A / 48 V for resistive loads - put a flyback diode and a fuse on every DC motor;
  #17 documents no protection diodes; #54 inputs are not galvanically isolated; two floats (empty / low) and a leak sensor
  on one #54.

### appblocks
- **`ab_tool.py check`, new run-time checks:** MQTT message longer than 255 bytes with its topic (worst case per
  variable type: float = `ftofixed(x,4)`), Delay with an expression (the generator writes
  `sys.timercountms + <DURATION> * 1000`), widgets in the old `WIDGETS` field (the generator reads only `WIDGET_GROUPS`,
  so the device panel would be empty), web console without a password linked to a setting.
- **`generated-code.md`, verified in generated code:** a Variable Set on a setting's autovariable writes EEPROM
  (`stg_set`) - the way to keep counters, modes and fault flags over a reboot; On Modbus Response / On Modbus Timeout
  with `{{$device_id}}` for link monitoring (the register keeps its last value); all On Time Period timers start in phase
  at boot - shift actions with Delay from one tick; time-sync check through the DateTime formatter; web console password
  through `linked_setting` (the `user` role is zephyr-only); button widgets and On Command sharing a chain with MQTT.
- `format.md` §4 items 17-20: `WIDGET_GROUPS`, `linked_setting` targets (MQTT host, SNTP server, web console and cloud
  passwords), Delay duration, and what the editor rewrites by itself when a project is opened (positions, widget IDs,
  `WIDGETS` → `WIDGET_GROUPS`, disabled LCD features, Wi-Fi autovariable defaults).
- `editor.md` §11: logic groups as tabs (links between tabs work but are not drawn), the status bar counters, the web
  console preview, PCB Designer, Plugins Marketplace (still three approved Tibbo plugins on 2 Nov 2026); `api.md`:
  `GET /cgg/extensions`.
- `mqtt.md`: the 255-byte limit replaces the wrong "400 bytes passed" note of 1.3.0; publish an `online` event from
  On MQTT Change.
- **Example `greenhouse2_tpp3.json`** replaces `greenhouse_tpp3.json`: cycle-and-soak irrigation with a lockout after
  the cycle limit, Modbus link monitoring, pump current check by the rise of the Hall sensor current, staggered pumps,
  float debounce, low-water and leak inputs, counters and faults in EEPROM, web panel buttons and an `auto_on` switch,
  telemetry in five messages under 255 bytes, SNTP server and console password as settings. 0 errors / 0 warnings in the
  editor, compiles in TIDE. `greenhouse2_logger.py` (merges the five messages, migrates an old database, `status`,
  `events`, alarms) replaces `mqtt_logger.py`; `greenhouse2_instruction.md` - the user guide (commissioning checklist,
  settings, alarms, pumps, tank, sensors, limits).
- Editor registry refreshed (2 Nov 2026): still 168 blocks; small changes in `smtp_client` (HTML template), MQTT,
  web console and LCD settings. The 78 public projects on appblocks.io are unchanged.

### tibbo-firmware
- `SKILL.md` §1 and `libraries.md` (`## mqtt/`): the 255-byte string limit for concatenations and MQTT messages.
- `tibbit-selection.md`: flyback diodes and fuses for motors on #06 and #17, #54 isolation, tank floats and leak input.

## [1.3.0] - 2026-10-30

Lessons from the "smart greenhouse" project on a TPP3 (three iterations, each compiled by Tibbo's TIDE compiler and
uploaded to AppBlocks): what breaks the generated code at compile time, how relays and Modbus behave in the generated
firmware, and how to run MQTT with your own broker.

### Both skills
- **Reliability first.** Tibbits and parts are chosen for reliability and efficiency, not for the lowest price: relays
  with margin for motor loads, isolated inputs where ground loops are possible, an adapter sized for inrush current.
- **Compile, don't just generate.** A project is ready only after the generated code compiles; a successful
  `ab_api.py code` is not enough.

### appblocks
- **New `references/mqtt.md`.** The `mqtt` feature and its blocks; the broker IP as a device setting (`linked_setting`),
  so a new laptop IP needs no reflash; `TOPICS` are subscriptions only; `{{$data}}` is seen only by the next block;
  library behaviour: publishing while offline is dropped silently (no buffer), auto-reconnect every 10 s,
  `MQTT_LARGE_PACKETS`; control logic stays on the controller. Your own Mosquitto broker: configs for a lab and for
  production, `mosquitto_sub`/`mosquitto_pub` checks, and the usual reasons a device does not connect (firewall,
  Mosquitto 2.x listening only on localhost, Wi-Fi client isolation, changed IP, duplicate client id).
- **`ab_api.py build <project.json> [--release] [--out prefix]`** - generates the code and compiles it with Tibbo's
  TIDE compiler (`POST /api/projects/build`, no key needed), prints errors and warnings, saves the `.tpc`, exits 1 on
  failure.
- **`ab_tool.py check` catches compile errors before the build:** a `{{$…}}` reference to a setting instead of its
  autovariable, variable names that clash with Modbus device names (case-insensitive, "Name conflict" in the editor),
  #05 RS485 without a port variable, 1-Wire sensors without the `tbl` service and OWSENS table. Warnings: a relay
  variable whose DEFAULT is not 1 (relays are active LOW, so the default sets the boot state), writing to a read-only
  Modbus register.
- **Example `greenhouse_tpp3.json`** - TPP3 with Modbus RTU sensors, #06 relays for pumps and fan, #17 PWM lamps, #54
  water level float, #61 isolated ADC for a Hall current sensor, MQTT telemetry and commands. **`mqtt_logger.py`** - a
  receiver for the PC: MQTT → SQLite → charts, commands to the device (paho-mqtt 1.x and 2.x).
- `generated-code.md`: compile findings and how the generated code drives relays, PWM, the ADC, Modbus polling (a
  timed-out register keeps its old value), MQTT and the timer. `format.md`, `api.md` (build endpoint, read-only key
  gives 403, reload the editor after `update`), `editor.md` (Name conflict).

### tibbo-firmware
- `SKILL.md`: the reliability principle; compile through the AppBlocks build API; relay polarity in the checklist.
- `tibbit-selection.md`: relay ratings (#03 1 A/30 V, #06 16 A/48 V, #07 1 A; all active LOW), #17 PWM, #54 for float
  switches (fail-safe wiring), #61 isolation and Hall sensor wiring (the isolated ground must not be tied to board GND).
- `power.md` §6а: sizing the 230/12 V adapter (pumps' inrush, fan, lamps, controller; ≥ 8 A at 12 V in the example).
- `tps_check.py`: connector pairing is checked in both directions - no more false "#62 + #21" warning. Regression
  configs `tests/greenhouse_tpp3.json`, `tests/onewire_62_21.json`.

## [1.2.0] - 2026-10-26

Lessons from building ten turnkey recipes (github.com/SCANCODE-IOT/tibbo-recipes): the AppBlocks editor's hardware-canvas
rules, connector pinouts, and two firmware mistakes that only show on 16-bit platforms or with fast system timers.

### Both skills
- **AppBlocks canvas warnings.** The editor draws yellow triangles on Tibbit sockets ("Incorrect pair", "Connector
  required", "Tibbit required", missing-line messages). They are not listed in Problems and do not stop the build, so a
  project with "0 errors, 0 warnings" can still be flagged. The rule (`getTppProjectWarnings`) and the editor's own
  connector table were taken from app.appblocks.io into `data/appblocks_pairs.json`; `scripts/ab_pairs.py` repeats the
  check and matches the editor on 60 random TPP2/TPP3 layouts.
- **Docs vs editor.** The editor accepts only #18 next to power Tibbits #09, #10, #25, #33 (docs.tibbo.com also lists
  #19/#20/#21), has no allowed connectors for #12 and #23, and needs #00-3 next to C sensors #28-#41.

### tibbo-firmware
- `tps_check.py check` warns "AppBlocks отметит …" for such layouts, says when the documentation allows the pair, and
  recommends the editor-approved pair for public solutions (the documentation-only variant stays a niche option at the
  user's risk). The "#20 instead of two #21" hints are no longer given when the editor would reject #20. New
  `ab_pairs.py` command line. Regression configs `tests/ab_*.json`.
- `tibbit-selection.md` §4: M1/C1/C2 pinouts, terminal maps of #18, #20, #21, #54 inputs (on TPP2(G2) S10+S12: #20
  terminals 1-4 → module in S9, 5 → ground, 6-9 → module in S11); §5: the editor rules and the docs/editor differences.
  `power.md`: power input connectors per editor, #09/#18 input and ground pins.
- Checklist: UART divider `ser.div9600 * 9600 / baud` overflows a word on 16-bit platforms (wrong baud rate on DS110x) -
  divide first; `dhcp/dns/mqtt/sntp_proc_timer` must keep the 0.5 s period when `sys.onsystimerperiod` is faster.
- `libraries.md`: using latest tibbotech Tibbit drivers with TIDE libraries 2_01_05 (`super_i2c.tbh` before `ssi.tbh`,
  `fstr()` missing for `cellular`).

### appblocks
- `ab_tool.py check`: hardware-canvas warnings ("плата: …") and a check that `{{$param}}` can reach the block
  (parameters are seen only by the next block; ports whose parameters the registry does not list are skipped - no false
  positives on the bundled examples).
- `editor.md` §9 rewritten from the editor code; §9а: the **Wiring** view (Tibbit schematics with pin and terminal
  numbers). `format.md`: settings are referenced by their autovariable ID; #54 has no interrupt mode (Button Input gives
  `<line>_kp` for On Button Pressed); canvas warnings.

## [1.1.2] - 2026-10-22

### Fixed
- Removed `certifi-*.whl` that was committed by mistake into `skills/appblocks/scripts/` in 1.1.1 and got into `appblocks.zip`
  (the file was not used by the skill). `tools/package.sh` now refuses to package anything but text sources, and `*.whl` is in `.gitignore`.

## [1.1.1] - 2026-10-22

Hotfix after user reports: scripts on Windows, and AppBlocks code generation facts checked against `POST /api/projects/code`.

### Fixed
- **Windows console encoding.** Every script (`ab_tool.py`, `ab_api.py`, `build_registry.py`, `tps_check.py`, `state_diagram.py`,
  `build_data.py`) now prints UTF-8 regardless of the console code page, so cp1251/cp1252 consoles no longer stop them with
  `UnicodeEncodeError` (for example `ab_tool.py lookup node_math_compound`). All files are opened with an explicit `encoding="utf-8"`.
- **`CERTIFICATE_VERIFY_FAILED` in `ab_api.py`.** HTTPS uses `SSL_CERT_FILE` / `SSL_CERT_DIR` if set, otherwise `truststore`
  (the OS store) or `certifi` when installed, otherwise Python's default. Verification is never disabled. A failed check now
  prints what to do on Windows instead of the sandbox hint; new `ab_api.py tls` shows the store in use and tests the connection.

### Added
- `ab_tool.py check`: error when Digital Line Set `LINE_NUMBER` is not a number (`PL_IO_NUM_48` is written into the code as a string);
  warning when the line is not made an output by the framework; error for comparison operators other than `=` `<>` `<` `<=` `>` `>=`
  on `tios` (`==` and `!=` go into Tibbo BASIC as is).
- `generated-code.md`: Digital Line Set, IF Condition, Custom Function, On Time Period (fires every N+1 ticks: 0.5 s is 0.51 s),
  `LEDPAT` (adds a red error pattern on Settings library init failures, no effect without Settings), the TPP signal strength bar
  driver (`signal_strength_set`). Each fact is marked: checked by generation, not checked in the editor, TIDE or on hardware.
- `editor.md` §8: driving the TPP signal strength bar from logic; `SKILL.md`: `tbt22` as a minimal base for a new tios project.
- tibbo-firmware `tios-api.md`: `pat.playlb` exists only on LTPP3(G2); on TiOS boards the bar is driven by the application.
- `ab_tool.one_id()`; `new_id()` docstring says it always returns a list.
- README and both `SKILL.md`: running the scripts on Windows.
- Tests run without `PYTHONUTF8` on a cp1251 console; CI on `windows-latest` (Python 3.12, 3.14) and an HTTPS check from Windows
  with `truststore` and `certifi`.

## [1.1.0] - 2026-10-22

Skills retrained on the AppBlocks editor itself (app.appblocks.io) and on the full docs.tibbo.com sources (2,325 pages, received from Tibbo on 2026-10-21).

### appblocks
- **Added** `references/blocks.md`: all 168 editor blocks (was 59 seen in examples) by palette category - ports with parameters, settings with allowed values and defaults, required feature, ASYNC; 45 hidden/legacy blocks listed separately.
- **Added** `references/features.md`: 30 features, 32 service libraries, 41 nested item types, 66 `tibbit_NN` field sets, 29 peripherals, 30 LCD / web console widgets.
- **Added** `data/registry.json` with `scripts/build_registry.py` and `scripts/extract_registry.js` (read-only browser extractor) to refresh it when AppBlocks changes.
- **Added** `ab_tool.py lookup <block|feature|word>`.
- **Changed** `ab_tool.py check` now also reports: unknown block type, link to a port the block does not have, setting value outside the allowed list, block whose feature is missing (or disabled), blocks no longer in the palette, blocks/features unavailable on the project's board. No false positives on the 78 appblocks.io projects and 5 real user projects.
- **Added** plugin format (`custom_feature`: settings, code blocks with `{{feature.settings.*}}` / `{{block.output}}`, variables) to `format.md` §5, based on the three marketplace plugins.
- **Added** to `editor.md`: how the editor validates Tibbit placement (§9), the editor's built-in AI assistant and text project view (§10), the plugin marketplace.
- **Changed** `SKILL.md`: new references, review rule for legacy blocks, how to refresh the registry.

### tibbo-firmware
- **Added** `references/docs-map.md`: topic → docs.tibbo.com page and its Russian translation on tibbo.ru/kb (objects, syscalls, libraries, platforms, TPS, all Tibbits, Monitor/Loader, Linux).
- **Changed** Tibbit catalog checked against 76 `tibbit_NN` pages: 84 Tibbits (added #47, #51, #56, all deprecated); #02 and #44 need an interrupt line for RTS/CTS; mating connectors for #09/#10/#16/#17/#23/#25/#33 per docs.
- **Fixed** #13/#14 own +5V consumption is 10/20 mA; the former 66/56 mA already included the #12 share, so the power budget counted it twice.
- **Changed** `tios-api.md`: defaults and notes from docs (watchdog, `sys.timercountms`, `net.gatewayip`, `stor.base`/`stor.size`, `wln.dhcp`/`autoconnect`, `kp.repeatdelay`, `ssi.baudrate` is writable, deprecated PPPoE and WS1102 properties).
- **Added** `platforms.md`: platform parameters table (16/32-bit, clock, RAM, EEPROM, UART FIFO, debugging, dual apps), docs vs .tph constant names, LTPP3(G2) line map.
- **Added** `project-and-libs.md` §9: facts for code and review - 16-bit arithmetic, `doevents` rules, VM exceptions in release builds, EEPROM/flash wear, Monitor/Loader and MD button, WM2000/WS1102 DCB and dual apps, DS110x port modes, LTPP3(G2).
- **Changed** `power.md`, `libraries.md`, `SKILL.md` (16-bit arithmetic, release exceptions, EEPROM service area is usually 28 bytes, not 8).
- **Added** `tps_check.py` rules from the AppBlocks editor: WA2000U needs RF connector #37; hints to use one #20 instead of #21 for double-width modules or two #21 in one tile.

### Repository
- Version 1.1.0 in the plugin catalog; counts updated in README files.

## [1.0.0] - 2026-10-20

First public release.

### tibbo-firmware
- TiOS API reference, 46 platforms with `PL_IO_NUM_*` mapping, Tibbo libraries, 81-Tibbit catalog (snapshot of October 2026).
- Writing, review checklist (34 items) and symptom-based debugging for Tibbo BASIC / Tibbo C.
- `tps_check.py`: TPS socket, line, UART/INT, connector, PoE and +5 V power budget checks; board SVG in the Tibbo configurator style; `find`, `board`, `tibbit` commands.
- `state_diagram.py`: state diagrams for firmware built as a state machine.

### appblocks
- AppBlocks editor, export format, node catalog (78 projects, 59 node types, 28 Tibbits), generated code and Cloud API references.
- `ab_tool.py`: `summary`, `check`, `flow`, `tps`, `nodes`, `ids`.
- `ab_api.py`: AppBlocks Cloud client; writes only with explicit confirmation.
- 6 example projects; AppBlocks Cloud device credentials removed from the published examples.

### Repository
- Claude Code plugin catalog (`/plugin marketplace add scancode-iot/tibbo-claude-skills`).
- Upload-ready packages for Claude apps and the API (`tools/package.sh`, attached to releases).
- Offline tests on every push.

[1.4.0]: https://github.com/scancode-iot/tibbo-claude-skills/releases/tag/v1.4.0
[1.3.0]: https://github.com/scancode-iot/tibbo-claude-skills/releases/tag/v1.3.0
[1.2.0]: https://github.com/scancode-iot/tibbo-claude-skills/releases/tag/v1.2.0
[1.1.2]: https://github.com/scancode-iot/tibbo-claude-skills/releases/tag/v1.1.2
[1.1.1]: https://github.com/scancode-iot/tibbo-claude-skills/releases/tag/v1.1.1
[1.1.0]: https://github.com/scancode-iot/tibbo-claude-skills/releases/tag/v1.1.0
[1.0.0]: https://github.com/scancode-iot/tibbo-claude-skills/releases/tag/v1.0.0
