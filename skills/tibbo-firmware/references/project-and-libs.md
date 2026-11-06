# Project structure, library wiring, settings descriptor

Everything here was taken from real projects in github.com/tibbotech (CA-TCP-Server, CA-Test-STG-lib,
CA-Test-WLN-lib, HTTPS_GET, CA-Test-Tibbits-13-14) and from the library sources.

## 1. TIDE project files

Build, upload and compiler errors: see `tide.md` (`scripts/tibbo_build.py`).

| File | Role |
|---|---|
| `<name>.tpr` | Project file (INI). Platform, library version, defines, file list. |
| `<name>.tprusr` | Per-user TIDE state. Not needed in a deliverable. |
| `global.tbh` | Project-wide header: config `#define`s, `include`s of libraries, `declare`s. |
| `main.tbs` | Event handlers (`on_sys_init`, `on_sys_timer`, …). |
| `device.tbs` (convention) | Library callbacks (`callback_*`) and device-specific glue. |
| `*.tbs` / `*.tbh` | BASIC source / BASIC header. Tibbo C uses `.tc` / `.th`. |
| `settings.txt` or `settings.xtxt` | STG library descriptor (see §4). Added with type `text`. |
| `*.der`, `*.bin`, `*.html` | Resource files (romfile): certificates, Wi-Fi firmware (`ga1000fw.bin`), web pages. |
| `supported_platforms.json` | `{ "platforms": [ "TPP3W(G2)", ... ] }` — which targets the sample was tested on. |

### .tpr format (real example)

```ini
[project]
version = 3.06.00
platform = TPP3W(G2)          ; folder name from Platforms/ — see platforms.md
src_lib_ver = 2_01_04         ; which Platforms/src/<ver>/ library set to use
name = test_stg_lib_1
output = test_stg_lib_1.tpc   ; compiled binary (TPC) uploaded to the device
debug = on                    ; on = debug build (sys.debugprint works, breakpoints), off = release
defines = /dOBJECT_FD=FD_ENABLED /dOBJECT_KP=KP_ENABLED /dOBJECT_WLN=WLN_ENABLED
transport = udp_winpcap       ; udp_winpcap | udp_broadcast | serial

[address1]                    ; target device(s) for upload/debug
platform = EM1000W
transport = udp_winpcap
address = 0.9.5.2.7.6         ; device MAC in Tibbo dotted-decimal form

[file1]
path = main.tbs
type = basic                  ; basic | header | text | binary ...
format =
condition =
locked = no
location =

[file2]
path = global.tbh
type = header

[file3]
path = settings\trunk\settings.tbs   ; library files referenced by relative path
type = basic
```

Every source/header/resource must be listed as a `[fileN]` section, otherwise TIDE does not compile it or
does not embed it as a resource (romfile.open fails).

New projects: TIDE templates per platform ("1 - Empty BASIC Project", "2 - Empty C Project",
"3 - Empty BASIC and C Project") or Tibbo's CODY web tool (cody.tibbo.com) that generates a configured
project. VS Code: extension `tibbo-development-vscode` (+ `tide-proxy` for device discovery/upload over UDP 65535).

## 2. Program skeleton (pattern used across Tibbo samples)

```basic
'global.tbh
'DEFINES-------------------------------------------------------------
#define DHCP_DEBUG_PRINT 0          'library config BEFORE the include
'INCLUDES------------------------------------------------------------
include "sock\trunk\sock.tbh"
include "dhcp\trunk\dhcp.tbh"
'DECLARATIONS--------------------------------------------------------
declare sub boot()
declare app_sock as byte           'variable defined (dim) in some .tbs
```

```basic
'main.tbs
include "global.tbh"
dim app_sock as byte

sub on_sys_init()
    boot()
end sub

sub boot()
    app_sock = sock_get("APP")      'sock library hands out sockets by signature
    sock.num = app_sock
    sock.rxbuffrq(2)
    sock.txbuffrq(2)
    sys.buffalloc()                 'ONE call after ALL buffrq requests
    sock.protocol  = PL_SOCK_PROTOCOL_TCP
    sock.inconmode = PL_SOCK_INCONMODE_ANY_IP_ANY_PORT
    sock.localportlist = "1001"
    dhcp_start(PL_SOCK_INTERFACE_NET, "", "")
end sub

sub on_sys_timer()                  'every 0.5 s by default (sys.onsystimerperiod, 10 ms units)
    dhcp_proc_timer()
end sub

sub on_sock_data_arrival()          'sock.num is already switched to the socket that has data
    if sock.num = app_sock then
        sock.setdata(sock.getdata(sock.txfree))   'echo, never more than fits
        sock.send
    else
        dhcp_proc_data()
    end if
end sub
```

```basic
'device.tbs — every callback the included libraries declare must exist (empty body is fine)
include "global.tbh"
sub callback_dhcp_ok(renew as no_yes, interface as pl_sock_interfaces, byref ip as string, byref gateway_ip as string, byref netmask as string, lease_time as dword)
    if renew = YES and net.ip = ip then exit sub
    'the library does NOT apply the IP itself
    net.ip = ip
    net.netmask = netmask
    net.gatewayip = gateway_ip
end sub
sub callback_dhcp_failure(interface as pl_sock_interfaces, failure_code as en_dhcp_status_codes)
end sub
sub callback_dhcp_pre_clear_ip(interface as pl_sock_interfaces)
end sub
sub callback_dhcp_pre_buffrq(required_buff_pages as byte)
end sub
sub callback_dhcp_buff_released()
end sub
```

## 3. Library event hooks — call them from YOUR handlers

Libraries never own the event handlers; you forward events to them. Missing a forward = library silently
does nothing (DHCP never completes, Wi-Fi never associates, MQTT never connects).

| Hook name pattern | Call it from |
|---|---|
| `<lib>_proc_timer()` (dhcp, dns, http, mqtt, smtp, sntp, pppoe, gprs, wln, agg, azure, cgg, cell, http_server, modbus, ui_input_box) | `on_sys_timer` |
| `<lib>_proc_data()` / `<lib>_proc_sock_data()` (dhcp, dns, http, mqtt, smtp, sntp, pppoe, wln, agg, cell, cgg, gprs, http_server) | `on_sock_data_arrival` |
| `<lib>_proc_sock_event(newstate, newstatesimple)` (agg, cell, cgg, http_server, smtp; sntp takes only the simple state) | `on_sock_event` |
| `<lib>_proc_data_sent()` (agg, smtp, http_server) | `on_sock_data_sent` (and enable it with `sock.notifysent`) |
| `<lib>_proc_ser_data()` (gprs, cgg), `cell__proc_on_ser_data_arrival()` | `on_ser_data_arrival` |
| `modbus_proc_ser_data_sent()` | `on_ser_data_sent` |
| `wln_proc_event(wln_event)` | `on_wln_event` |
| `wln_proc_task_complete(completed_task)` | `on_wln_task_complete` |
| `tibbit_43_proc_data()` | `on_ser_data_arrival` (Tibbit #43 streams over UART) |

Exact signatures: libraries.md. Each hook ignores sockets that are not its own, so it is safe to call
several hooks in one handler — but filter your own socket first (`if sock.num = my_sock`).

## 4. Library versions — a real trap

The same library exists in several versions:
- `github.com/tibbotech/libraries` (latest),
- `Platforms/src/<src_lib_ver>/<lib>/trunk/` shipped with TIDE (selected by `src_lib_ver` in .tpr),
- copies inside sample projects (often older).

Signatures differ between versions. Example: CA-Test-Tibbits-13-14 calls `tbt13_init(YES)`, while the current
library declares `tbt13_init(signature as string, data_pin as byte, clk_pin as byte, byref tbt_channel as byte, use_ssi as no_yes) as ok_ng`
and every other tbt13 call takes `tbt_channel`. Rule: write calls against the .tbh that will actually be
compiled in the user's project; if unknown, ask which library version / take libraries.md (latest) and say so.

## 5. STG (settings) library descriptor — settings.txt

One line per setting, starting with `>>`, TAB-separated fields:

```
>>NAME  STORAGE  TYPE  MEMBERS  P1  P2  INIT  DEFAULT  [comment]
>>DN    E        S     1        0   10  I     ^        Device Name
>>IP    E        D     1        4   4   A     192.168.1.93   IP address
>>PN    E        W     1        0   65535 A   1000     Port number
>>PTN   E        S     3        0   16  A     G-~/R-~/B-~    LED patterns (3 members, defaults split by /)
>>CPTN  R        B     1        0   2   A     0        Current pattern (volatile, RAM)
```

- STORAGE: `E` = non-volatile (EEPROM via stor, or flash file if `STG_STORAGE_MEMORY 1`), `R` = volatile (RAM).
- TYPE: `B` byte, `W` word, `S` string, `D` dot-decimal (IP), `F` float, plus timestamp/time types (see en_stg_types).
- P1/P2: min/max value (B/W), min/max length (S), number of bytes (D, e.g. 4 for IPv4).
- INIT: `I` = initialize only when invalid, `A` = always initialize on `stg_restore_multiple(EN_STG_INIT_MODE_NORMAL)`.
- DEFAULT: `^` = empty/NULL; members separated by `/`.
- `#define`s for the library can sit in the same file when it is included with `includepp "settings.txt"`
  (STG_MAX_NUM_SETTINGS, STG_MAX_SETTING_NAME_LEN, STG_RAM_ARRAY_SIZE ...). With `STG_DEBUG_PRINT 1` the
  library prints exact sizes and tells you "YOU ARE WASTING MEMORY!!! Set X to N" — use it to tune.
- Start: `if stg_start() <> EN_STG_STATUS_OK then sys.halt` (or handle the error), then `stg_get("IP",0)` /
  `stg_set("IP",0,"192.168.1.5")`. Implement `callback_stg_error`, `callback_stg_pre_get`, `callback_stg_post_set`
  (+ validation / vm callbacks when enabled by defines).

## 6. Wi-Fi (WLN library) pattern (CA-Test-WLN-lib)

- global.tbh: `#define WLN_AVAILABLE 1`, `#define WLN_WPA 1`, include `sock`, `settings` (stores the PSK), `wln`.
- Older modules (EM1000/EM1206/DS1101W... with GA1000) need the SPI pin defines `WLN_CLK/CS/DI/DO/RST` per
  platform and the `ga1000fw.bin` resource; G2/G3 TPP and WM2000 have Wi-Fi built in (OBJECT_WLN in platforms.md).
- Handlers: `wln_proc_timer()` in on_sys_timer, `wln_proc_data()` in on_sock_data_arrival,
  `wln_proc_event()` in on_wln_event, `wln_proc_task_complete()` in on_wln_task_complete.
- Outgoing sockets over Wi-Fi: `sock.targetinterface = PL_SOCK_INTERFACE_WLN`.
- Reconnect logic lives in on_sys_timer: `if wln_check_association() = PL_WLN_ASSOCIATED then ... sock.connect`.

## 7. TLS / HTTPS pattern (HTTPS_GET, TPP2W(G3), src_lib_ver 2_02_00)

Flow inside `on_sock_event` for your socket:
1. `PL_SST_EST_AOPENED` → `sock.tlsdeinit`, `romfile.open(CA_CERT)`, `sock.tlsinit(romfile.offset)`,
   `sock.tlshandshake(SERVER_HOST)` (host must match the certificate name). Check each `pl_tls_result`.
2. `PL_SST_EST_TLS` → handshake done: `sock.tlssetdata(...)`, `sock.send`.
3. `PL_SST_EST_TLS_FAILED` → `sock.rxclear`, `sock.reset`.
4. `newstatesimple = PL_SSTS_CLOSED` → `sock.rxclear`, `sock.txclear`, `sock.tlsdeinit`.
Data: `sock.tlsgetdata(255)` in a loop until empty (in on_sock_data_arrival).
Buffers: 1 page = 256 bytes; ~6 RX/6 TX pages for ECDSA P-256, raise to 8 for RSA-2048.
CA certificate: DER file added to the project as a resource. TLS exists only on platforms that include
`tls.tph` (G2/G3 TPP, EM2000W, EM3000W, WM2000, WS110x, KLM*_32 — see platforms.md).

## 8. Tibbit on a TPS board — pin binding

Tibbit libraries take the I/O lines as `#define`s or init arguments. Lines depend on the socket (slot) number
and the board: look up `enum pl_io_num` for the board in platforms.md — comments say "Socket N, control line A/B/C/D"
and which lines double as UART RX/TX or interrupts (e.g. on TPP3W(G2): `PL_IO_NUM_8_RX0` = socket 1 line B).
Tibbit line roles (SCL/SDA, TX/RX, CS/CLK…) are in tibbits.md. Serial Tibbits (#01, #02, #05, #08, #43, #45…)
must sit in a socket whose lines are a UART (`requires: serial`); interrupt-using Tibbits need an INT line.
Use per-platform `#if PLATFORM_ID=TPP3WG2 ... #elif ... #else XXXX 'Unsupported platform #endif` blocks as the
samples do so a wrong target fails at compile time.

## 9. Факты из docs.tibbo.com, важные для кода и ревью (сверка октябрь 2026)

Ссылки - slug страницы `https://docs.tibbo.com/<slug>`; полный указатель тем - docs-map.md.

**Язык и компилятор** (guide_basic_c_*)
- 16-битные платформы считают выражения в 16 битах: `(50000+60000)/10` даст 4446. Добавь в выражение хотя бы одну 32-битную переменную (`dword`/`long`) - расчёт станет 32-битным. На 32-битных платформах всё 32-битное (guide_basic_c_variables_simple_differences; тип платформы - таблица в platforms.md).
- Память статическая: глобальные + аргументы + стек по самой длинной цепочке вызовов от обработчика события + (в debug) буфер отладки. Нет рекурсии, повторного входа и указателей на функции (guide_basic_c_procedures_allocation).
- Процедура с `doevents` и все процедуры, ведущие к ней, получают отдельную память и **не могут вызываться из других цепочек событий**; событие того же типа, что стоит на `doevents`, не выполнится, пока исходное не завершится; новые события, пришедшие во время `doevents`, ждут следующего раунда (guide_basic_c_doevents*).
- В BASIC массивы нельзя передавать в процедуры и возвращать - оборачивай в `type` и передавай `byref` (guide_basic_c_procedures). `sizeof()` в BASIC - только для типов; `countof()` - число элементов массива или ёмкость строки.
- Строка: 1 байт длины + 1 байт ёмкости + данные (до 255), 257 байт по умолчанию; может содержать любые байты, включая 0. Неявные преобразования строка↔число (`dim c as word = s` вызывает `val`). В Tibbo C нельзя `char *b="123"` (константы во flash); в union нельзя строки (guide_basic_c_variables_string, _arrays_limitations).
- Глобальные переменные должны быть уникальны во всём проекте; **типы между `dim` и `declare` в разных файлах не сверяются** - расхождение не найдёт ни компилятор, ни линкер. То же при кросс-вызовах BASIC↔C (`byref x` ↔ `*x`; массивы и структуры кросс-вызовом не передаются) (guide_basic_c_variables_scopes, _procedures_cross-calling).
- Enum хранится в наименьшем подходящем типе (char → byte → short → word → long → dword).
- Константы BASIC: `&h`, `&b`, символы в обратных кавычках `` `A` `` (до 4 символов для dword), escape-последовательности `\x00 \r \n \t \e` в строках; `const` есть только в BASIC (в C - `#define`).
- Препроцессор: `#if X=Y` в BASIC и `#if X==Y` в C; `#includeb` подключает .tbh из C; `includepp` - `#define` из текстовых ресурсов (settings.xtxt); `#message`, `#error`, `#undef`. Условия на уровне файлов проекта (File Condition) пишутся в синтаксисе BASIC (`AND`, `OR`, `<>`), видят только глобальные идентификаторы платформы и проекта, для .tbh/.th не задаются (guide_basic_c_preprocessor, guide_tide_projects_conditional).
- HTML с кодом `<? ?>`: весь файл - одна виртуальная процедура (процедуры внутри определять нельзя), переменные уровня файла глобальные (едят RAM), очередь событий стоит, пока страница не отдана, - для длинных страниц `doevents` или вынос кода в процедуры (guide_basic_c_html).

**Отладка и выпуск** (guide_tide_*)
- Исключения VM: HALT (sys.halt), DIV0, OOR (выход за массив BASIC; в C массивы не проверяются), FPERR, IOC, OUM, TDLF. **В release DIV0, OOR и FPERR не останавливают программу** (неверный доступ к массиву блокируется, выполнение идёт дальше) - проверяй делители и индексы сам, для real - `cfloat()` (guide_tide_debugging_states, syscall_cfloat).
- Release-.tpc запускается сам при включении; debug-приложение ждёт запуска из TIDE. .tpc совместим только с той же платформой и той же **старшей** версией TiOS (V3.50.xx); надёжнее склеить TiOS+приложение в .bin (BinMerger, apps.tibbo.com/bin_merger) (guide_tide_releasing).
- Отладка идёт по UDP-порту 65535 в пределах сегмента сети (через роутер нельзя); приложение может само слушать 65535 - пакеты, начинающиеся с `_`, забирает отладчик (ref_platforms_debug_comm).
- Пароль устройства (EEPROM, 16 байт MD5) сбрасывается удержанием MD при действии в TIDE/Device Explorer (guide_tide_releasing, button).

**EEPROM и flash** (eeprom_life, object_fd_prolonging, ref_platforms_eeprom_conf_section)
- Служебная область EEPROM: обычно 28 байт (MAC 8 + пароль 20), `stor.base` по умолчанию 29; у DS1101/DS1102 - 8 байт. Адреса считаются с 1. MAC в EEPROM: байт 1 = 6, байты 2–7 MAC, байт 8 = 255 − (сумма байт 1–7 mod 256); первый байт MAC TiOS всегда обнуляет; при неверной записи MAC = 0.1.2.3.4.100.
- EEPROM: сектора по 16 байт (2 КБ EEPROM) или 8 байт (256 Б); запись даже одного байта изнашивает весь сектор; каждый байт `stor.setdata` - отдельный цикл; запись тех же данных тоже цикл → сначала читай и сравнивай. Ориентир ≥1 млн циклов на сектор, при нагреве меньше. Счётчики - в RAM с периодическим сбросом, ротация ячеек, две копии с контрольной суммой, или библиотека STG.
- Flash: ~100 000 циклов на сектор. Файлы fd создавай один раз нужного размера и перезаписывай (не дописывай - иначе изнашиваются FRT/FAT); журнал `fd.formatj` - 50–100 секторов; до 64 файлов (кратно 4); после форматирования диск надо смонтировать. На платформах с общей flash при отладке оставляй зазор между диском и областью приложения (object_fd_formatting).
- WM2000/WS1102: сектор fd 528 байт (раньше 264), 4 МБ; все файлы и приложения выровнены на 4 КБ.

**Monitor/Loader, светодиоды, MD** (ml, ml_update_modes, intro_led_md, status_leds, button)
- MD нажата при включении → M/L, режим обновления: XModem по первому UART (у TPS - сокет S1, Tibbit #01/#02/#44 + #19; передачу на ПК запускать **до** включения устройства - таймаут меньше секунды), затем сеть (EM500/510, EM2000/2001, TPP2/3(G2), TPP2(G3); Device Explorer, «TiOS-32 Loader»), затем BLE (при WA2000, M/L V3+). Файлы: .bin (TiOS или TiOS+приложение), для BLE - .tcu.
- SG/SR (зелёный/красный) показывают состояние TiOS, пока приложение не запущено; при работе приложения ими управляет `pat.` (канал 0). У EM500/EM510/DS1100 нет жёлтого - линк показывается яркостью SG/SR.
- MD-кнопка - ещё и обычная кнопка приложения (`button.`) и обход пароля.

**WM2000 и WS1102** (ml_dcb, ref_platforms_dual_apps, wm2000_*)
- DCB (блок конфигурации во flash): autoconnect (no), domain (0 US), ssid, password, dhcp (no), debugmode (serial), defaultapp (1). Доступ - BLE-консоль M/L, Companion App (APP0), или свойства `sys.`/`wln.` из кода; сброс к заводским - MD по схеме M/L V4. Обновление по Wi-Fi и отладка по сети возможны только при autoconnect = yes.
- Два приложения APP0/APP1 (1 688 КБ на оба), по умолчанию грузится APP1; если приложение одно и загружено в APP0 - поставь `sys.defaultapp = PL_APP_NUM_0`. Обновление APP0 стирает APP1. Device Explorer всегда пишет в активное приложение.
- `sys.sleep(дни, минуты, секунды от 1.1.2000)`: линия LP уходит в LOW и внешний ключ снимает питание; пробуждение - полная перезагрузка, без продолжения. VCCB (питание RTC, 1,8 В…VCC, ~3 мкА) подключать всегда.
- WM2000: 10 GPIO 3,3 В (до 12 мА; GPIO1 и GPIO3 только 500 мкА и это bootstrap-линии - при старте не нагружать), прерывания только GPIO2/3; CTS и W0&1 только на линиях прерывания 0/1; при последовательной отладке UART1 недоступен (`ser.num=1` не установится).

**DS/WS110x** (dsws110x_*)
- DS1102: режим порта задают PL_IO_NUM_17/18 (RS232: LOW/HIGH, RS422: HIGH/HIGH, RS485: HIGH/LOW, обе - выходы); направление RS485 - PL_IO_NUM_3_TX1_INT3 (HIGH - передача). Порт DB9 - три независимых UART (TX/RX, TX2/RX2 = RTS/CTS, TX3/RX3 = DTR/DSR).
- WS1102: режим порта и LED-бар через расширитель MCP23008 по I²C (GPIO5/6, объект `ssi.`): GP5/GP6 RS232 HIGH/LOW, RS422 HIGH/HIGH, RS485 LOW/HIGH; направление RS485 - PL_IO_NUM_3_INT1. При последовательной отладке DTR/DSR становятся TX/RX отладочного порта.
- DS1101/DS1102: синие LED-бара - PL_IO_NUM_19_SB1…23_SB5, включение = выход + LOW. DS1101: 12 В на контакт 9 DB9 - линия `PL_IO_NUM_8_PWROUT` (так в .tph; в тексте docs опечатка `PL_IO_NUM8_PWROUT`) как выход + LOW (на выходе ≈ Uвх − 0,3 В). PoE и Wi-Fi одновременно у DS110x невозможны.

**LTPP3(G2), Linux** (ltpp3g2*, linux_*)
- Это не TiOS: Ubuntu/Yocto на Plus1 (SP7021), Tibbo BASIC/C работает поверх Linux; `io.`/`pat.` отличаются (см. tios-api.md, раздел Linux), исключения возможны. 8 M-сокетов S1…S15: UART на S1, S5, S9, S13; INT и SPI/I²C - на всех. Встроенный источник 8–60 В/2,5 А - Tibbit-источники не нужны. Карта линий - platforms.md, «LTPP3(G2)».
- Прошивка: файл ISPBOOOT.BIN на USB/microSD (FAT32), перемычка CN11 (для microSD ещё CN10), консоль USB 115200 8N1, конец - «ISP all: Done». Оверлей rootfs (tb_overlay, tb_rootfs_ro) - данные в оверлее теряются при перезагрузке.

**Modbus Gateway (приложение Tibbo, открытый исходник)** (раздел tmgm на docs, tibbo.ru/kb/modbus/)
- Работает на TPP2(G2)/TPP3(G2) (до 4 портов: #01 RS232, #05 RS485, #02 универсальный - на TPP2 только порты 1 и 3) и DS1101/DS1102. До 8 TCP-мастеров и 4 TCP-слейвов, маршрутизация по Slave ID (до 8 диапазонов, сдвиг ID) и по TCP-порту (4 порта, приоритет выше). Таймаут ответа - шаги 0,5 с; межсимвольная пауза RTU - шаги 10 мс. На ARM-платформах (G2, EM2000) нет режима 7 бит без чётности. Для Modbus TCP-мастеров нужен статический IP.
