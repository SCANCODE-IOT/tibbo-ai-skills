# github.com/tibbotech — what to use for what (≈180 public repos, surveyed Oct 2026)

Raw files: `https://raw.githubusercontent.com/tibbotech/<repo>/master/<path>` (some repos use `main`).
Clone works with `git clone --depth 1 https://github.com/tibbotech/<repo>`.

## Core references (authoritative for names/signatures)
| Repo | Content |
|---|---|
| `platforms` | TIDE platform files: `Platforms/<PLATFORM>/<PLATFORM>.tph` (I/O, enums, feature defines), `Platforms/*.tph` (object declarations: sock, ser, sys, io, net, wln, bt, fd, stor, romfile, tls, i2c, ssi, adc, pwm, kp, lcd, beep, pat, button, rtc, ppp, pppoe, dhcp), `Platforms/src/<ver>/<lib>/trunk/` library sets per `src_lib_ver`, `Platforms/<P>/firmware/tios-*.bin` TiOS firmware, `Platforms/<P>/templates/` empty projects. → tios-api.md, platforms.md |
| `libraries` | Latest Tibbo BASIC libraries: aggregate, azure, cell/cellular, cgg, dhcp, dns, dsman, filenum, gprs, http, http_server, lcd, luis, modbus, mqtt, pic, pppoe, scap, settings (STG), smtp, snmp, sntp, sock, ssi, stgcmd, super_i2c, super_spi, tables, tibbits/tbtNN, time, ui, upgrade, utils, wln. → libraries.md |
| `TibbitDefinitions` | tibbits.json — catalog of Tibbit modules, lines, mates, power. → tibbits.md |
| `tibbo-basic` | Tibbo BASIC language server: ANTLR grammar (`server/language/TibboBasic/*.g4`), TextMate syntax. Ground truth for syntax. Branch `feature/compiler`: Tibbo's `tmake`/`tbc`/`tlink` ported to Node.js (`server/out/compiler/compile-project.js <folder> -o x.tpc`), byte-identical `.tpc`, Tibbo BASIC only, platforms from the `platforms` submodule - used by `tibbo_build.py` (`--setup-node`). |
| `tibbo-basic-vscode`, `tibbo-development-vscode` | VS Code extension for Tibbo BASIC projects. |
| `tide-proxy` | Node proxy between IDE and devices (UDP broadcast port 65535, Socket.IO `/tide` on 3535): discovery (`_?`), `.tpc` upload (`Q`/`QF` → 128-byte `D` blocks → `T`, TiOS prepended if needed), run/pause/step/breakpoints, memory and properties, `debug_print`, buzz, reboot, serial bridge, GDB server for Zephyr boards. README documents the device protocol. `sim/` - Renode simulator of TPP2/TPP3 G2/G3 boards (LCD, LEDs, buttons, Tibbits, Modbus/Wiegand field devices, web UI and HTTP API, Docker with NET_ADMIN); runs Zephyr firmware, classic TiOS + `.tpc` not confirmed. |
| `tide-desktop-extension-publish` | Releases of "Tibbo Desktop Extension" for Windows/macOS/Linux (exe/dmg/AppImage), purpose not documented - likely the local bridge (tide-proxy) for Tibbo web tools. |
| Cody (cody.tibbo.tech, not on GitHub) | Tibbo's online project configurator (board, Tibbits in sockets, settings) saving a project `.json`; the tide-proxy simulator creates devices from it. |
| `web-serial-library` | JS API for web apps to reach USB devices through Tibbo Web232/Web485 boards. |

## Sample applications (Tibbo BASIC, "CA-" = code application)
| Task | Repos |
|---|---|
| Minimal sockets | `CA-TCP-Server`, `CA-Simple-DS`, `Serial_Ethernet_test`, `RS485_Device_Server`, `CA-PING`, `CA-DNS-Demo`, `CA-NetBIOS` |
| Serial-over-IP / device server | `CA-SOI` (full SOI firmware), `Dev_Serv-4`, `DEV_BASE`, `CA-Asynchronous-Serial-Data-Splitter`, `CA-Inband` |
| Modbus | `Modbus-Gateway`, `modbus-gateway-appblocks`, `modbus-mqtt-gateway-appblocks`, `CA-Modbus-Converter`, `CA-Modbus-Energy-Meter`, `web-modbus-library` (JS) |
| MQTT / cloud | `CA-MQTT-Publisher`, `CA-MQTT-Subscriber`, `MQTT-Library-Update` (packets up to 16383 bytes), `CA-TPSG3-Azure`, `tps-monitoring-azure-iothub`, `AggreGate-server-demo`, `CA-Test-AGG-lib` |
| HTTP / HTTPS / TLS (G3) | `HTTPS_GET`, `HTTPS_HTTP` (built-in HTTPS server), `HTTPS_MTLS`, `SSL_MULTI_CLIENT`, `SSL_MULTI_SERVER` (TLS 1.3), `HTTP-Helper`, `CA-HTML-Form`, `CA-LED-and-Webserver`, `JSON-Requests` |
| Settings / storage | `CA-Test-STG-lib`, `CA-EEPROM-and-Resource`, `CA-External-EEPROM`, `CA-Memory-Wipe`, `CA-L-Convert` |
| Network config | `CA-Test-DHCP-lib`, `CA-PPPoE`, `CA-SNTP`, `CA-IP-Authentication`, `GPRS-with-wifi-and-Ethernet`, `myNetwork` (Wi-Fi AP) |
| Wi-Fi / Bluetooth | `CA-Test-WLN-lib`, `CA-Wifi-Settings-Example` (settings over BLE), `Bluetooth-test`, `BT-WLN-Echo-Test`, `WM2000_Companion`, `wm2000ev` |
| Tibbit drivers / tests | `CA-Test-Tibbit-22/26/28/29/30/35/36/40/41/42/52/53/57/61/62`, `CA-Test-Tibbits-13-14`, `CA-Test-Tibbits-16-17-31`, `CA-One_Wire`, `CA-PCA9555`, `CA-Update-PIC-Firmware`, `Tibbit_43-1/-2` (PIC firmware) |
| UI on TPS2L (LCD/keypad) | `CA-TPS2L-LCD-Keypad`, `LCD-Set-Color`, `TPS2L_Screen_Capture`, `CA-Screen-Capture`, `ui_demo`, `CA-KP-Demo`, `CA-Segment-LED-Display-with-SSI-Object` |
| Firmware/app update | `tibbo_self_updater` (upgrade methods), `OSS_Apps` (WM2000 app0 = essential config, app1 = main app), `wm2000_recovery_tool` |
| Misc | `CA-LED-Blinker`, `Watchdog_test`, `CA-CRC`, `CA-LZO-Demo`, `Float-To-Hex`, `CA-FTP-Client`, `CA-MySQL-Client`, `CA-Aircon-Control`, `CA-Dehumidifier-Control`, `Remote-IO`, `Sentinel` |

## Linux-based Tibbo (LTPP3 / LTPP3G2, Size 3 Linux TPS) — NOT TiOS
Yocto/Buildroot (`yocto_layers`, `meta-tibbo`, `meta-sunplus`, `br2_external`, `plus1_kernel`, `plus1_uboot`),
kernel modules (`kern-mod-tpsleds`, `kern-mod-twg` Wiegand, `kern-mod-tpsid`), Node.js (`node-ltps`,
`tps-gpio-tutorials`, `gpio-indicators`, `wiegand-demo`, `ltps-capi-node`), C API (`ltps-capi`), `ntios_dev_env`
(NTIOS: TiOS-like API on Linux). Apps there are Linux programs (C/C++/Node/Python), not Tibbo BASIC —
do not mix the two worlds. In platforms.md the LTPP3/LKLM601 targets expose `lsock`/`lfd` objects instead of `sock`/`fd`.
