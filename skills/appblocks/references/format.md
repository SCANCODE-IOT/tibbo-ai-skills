# Формат проекта AppBlocks (экспорт JSON)

Источник: два проекта, которые Tibbo выложила на GitHub вместе с PDF-распечатками из редактора
(`tibbotech/modbus-mqtt-gateway-appblocks`, `tibbotech/modbus-gateway-appblocks`; копии в `examples/`).
Официальной спецификации формата нет — всё ниже выведено из этих файлов. Поля и типы, которых нет в примерах,
бери из свежего экспорта пользователя, а не придумывай.

## 1. Верхний уровень

```json
{
  "id": "6a7027cef9549288e8b5f72b",      // id проекта в AppBlocks (24 hex, как ObjectId MongoDB)
  "name": "ModbusMQTTGateway",
  "device": "TPP2W(G2)",                  // платформа = имя папки Platforms в TIDE
  "description": "...", "shortDescription": "",
  "version": "0.1.19",                    // версия формата/редактора — не меняй
  "runtime": "zephyr",                    // "tios" (Tibbo BASIC, TiOS) | "zephyr" | "micropython"; через API device может быть объектом {platform, name}
  "featureFlags": [{"id": "<ID>", "name": "MQTT Enabled", "enabled": true}],
  "featureFlagMap": {"<flag ID>": ["<ID элемента>", ...]},   // какие feature/узлы включает флаг
  "features": [ {"id": "<тип>", "settings": {"ID": "<ID>", ...}}, ... ]
}
```

**Всё содержимое — плоский список `features`.** Тип — поле `id`, уникальный идентификатор — `settings.ID`.
Вложенные списки (переменные, таймеры, таблицы, настройки STG, кейсы switch, аргументы узлов) имеют ту же
форму `{"id": "<тип>", "settings": {"ID": ...}}`.

**ID**: `Date.now()` в base36 + случайный base36-хвост, 16–20 символов, напр. `mruc2f3etssfz14s8m`.
Новые ID — `python3 scripts/ab_tool.py ids 10`. ID должны быть уникальны во всём файле.

## 2. Группы feature

| Группа | Типы | Что важно |
|---|---|---|
| Плата и сборка | `boardsetting` (POE, 5VDIRECT, TPB, DIN, POWERADAPTER, ASM, WIFIANTENNA, GPRSANTENNA), `general` (DEVICE_NAME, FIRMWAREVERSION, TIMEZONE, LOGGING) | POE="1" ↔ перемычки PoE; 5VDIRECT="1" ↔ питание 5 В на клеммы платы |
| Tibbit | `tibbit_NN` с `SOCKET` (номер сокета без «S»), `TIBBIT` ("05", "33"…), `PLATFORM`, + свои поля (у #05: NAME, MODE, BAUD, FLOWCONTROL, PARITY, BITS, TXBUF, RXBUF; у #33: PF) | Широкие (C2/M2/H2) записываются по первому сокету: #20 в SOCKET "2" = S2+S4 |
| Беспроводное | `wireless_module` (MODULE: "WA2000C"), `wifi` (MODE, DHCP, WAP, WSEC, WPW…), `wln`, `bt`, `cell` | |
| Сеть и сервисы | `net`, `dhcp`, `dns`, `sntp`, `http`, `httpserver`, `socket` (SOCKETS), `mqtt`, `cgg` (облако AggreGate), `modbus`, `modbus_master`, `modbus_slave`, `snmp_agent`, `smtp_client`, `mbedtls` | У сервисов `ENABLED` "0"/"1" |
| Интерфейсы | `web_dashboard`, `luis` (настройка через BLE/веб), `lcd`, `lcd_graph`, `display_lib`, `ds_man` | |
| Данные | `global_vars` (VARS → `variable`: VARNAME, DATATYPE float/string/datetime…, DEFAULT), `stg` (SETTINGS → `stg_setting`: SETTINGID, STORAGE E/R, DATATYPE, DEFAULT), `tbl` (TABLES → `tbl_table` → FIELDS `tbl_field`), `timers` (TIMERS → `timer`), `commands` (COMMANDS → `command`), `cron`, `fd`, `files`, `flash_devices` | |
| Связки | `linked_setting` (FEATURE = ID Tibbit/сервиса, SETTINGID = его поле, LINKEDSETTING = ID `stg_setting`) | Поле feature берётся из настройки STG (меняется с веба/BLE) |
| Расширения | `custom_features` → `custom_feature` (плагин: SETTINGS, CODE_BLOCKS, VARIABLES), узел-плагин `node_custom_*` | Свой код внутри проекта, §5 |
| Служебные | `filenum`, `sock`, `time`, `datetime`, `stgcmd_lib`, `mqtt_lib`, `peripheral_wiring` (LAYOUT_DATA), `datasheet_pages` (PAGES — markdown страниц datasheet) | Не трогай без нужды |

## 3. Логика: узлы и связи

Узел — feature `node_<тип>` с общими полями:
`ID, DISPLAY_NAME, FEATURE, X, Y (позиция в редакторе), GROUP (ID node_group или ""), INPUTS, OUTPUTS, ARGUMENTS`
плюс свои поля (TIMER, VARIABLE, TABLE, COMMAND… — это **ID** соответствующих элементов).

`ARGUMENTS` — список `node_argument {ID, TARGETPARAM, ARGVALUE}`. В `ARGVALUE` можно подставлять:
- `{{$<ID>}}` — значение переменной/настройки STG по её ID (`{{$mruc3avst0no8wlazw}}`);
- `{{$<ИМЯ>}}` — параметр события или поле найденной записи: `{{$response_data}}`, `{{$rows}}`,
  `{{$time_now}}`, `{{$pressed_time}}`, `{{$boot_reason}}`, `{{$ipaddress}}`, поля таблицы `{{$DEVICE_ID}}`, `{{$VALUE}}`;
- выражения: `{{$id}}+1`, `{{$a}} * {{$b}}`, конкатенация `{{$x}}/{{$y}}`.

Связь — feature `node_link`:
```json
{"id": "node_link", "settings": {"ID": "...", "SOURCE": "", "SOURCE_FEATURE": "<ID узла-источника>",
 "SOURCE_PORT": "boot", "TARGET": "", "TARGET_FEATURE": "<ID узла-приёмника>", "TARGET_PORT": "timer_start", "ARGUMENTS": []}}
```
Порты каждого типа - `references/blocks.md` (или `ab_tool.py lookup <тип>`). У `node_switch` выходной порт = **ID кейса** из CASES.
`node_system` (один на проект) объявляет порты в INPUTS/OUTPUTS: выходы `boot`, `on_sys_timer`; входы `sys.halt`, `sys.reboot`.

Типичный приём из примеров — «команды» как подпрограммы: `node_command_trigger(COMMAND=X)` вызывает,
`node_command_triggered(COMMAND=X)` — точка входа. Так строятся циклы опроса (POLL_NEXT → … → POLL_END → POLL_NEXT).

## 4. Правила правки и генерации

1. Начинай с экспорта пользователя (или примера) и меняй его, а не пиши проект с нуля: так сохраняются
   служебные feature, версия формата и runtime.
2. Каждый новый элемент — новый ID (`ab_tool.py ids`). Не копируй ID из другого проекта.
3. Ссылки (`GROUP`, `TIMER`, `VARIABLE`, `TABLE`, `COMMAND`, `SOCKET`, `SERIAL_PORT`, `{{$ID}}`, `LINKEDSETTING`)
   должны указывать на существующие ID.
4. Порты и поля бери из `blocks.md` / `ab_tool.py lookup <блок>` (реестр редактора), catalog-examples.md или из того же типа узла в экспорте пользователя.
5. Новый Tibbit = `tibbit_NN` с SOCKET/TIBBIT/PLATFORM:"" и полями по образцу того же Tibbit в любом экспорте;
   если образца нет — добавь Tibbit в редакторе AppBlocks, а не угадывай поля.
6. Позиции X/Y: новые узлы ставь правее источника (+300…350 по X), в той же GROUP.
7. После правки: `ab_tool.py check` (0 ошибок) → `ab_tool.py tps … --out cfg.json` + `tps_check.py check cfg.json --svg board.svg` для железа →
   `ab_tool.py flow` для картинки → импорт в AppBlocks и проверка в редакторе.
8. **Ссылки по ID есть не только в узлах.** Панели и сервисы хранят ID других элементов во вложенных списках:
   `web_dashboard` → GROUPS → `luis_item.SETTINGID` (ID `stg_setting`), WIDGETS → `button_widget.VARIABLE`
   (ID **команды**), TABLES → `console_table_item.TABLE` (ID `tbl_table`); то же бывает в `luis`, `ds_man`, `lcd_menu`, `cgg`.
   Если при переделке проекта удаляешь или пересоздаёшь настройку, команду или таблицу — **сохрани её старый ID**
   (или пройди по всему дереву и замени старый ID новым), иначе редактор покажет «Setting is not defined»,
   «Connected Setting is not set», «Same setting cannot be exposed more than once» (несколько пунктов с одинаковой
   битой ссылкой), «Command is not set». `ab_tool.py check` ищет такие ссылки по всему файлу.
9. **Числовые поля имеют минимумы редактора**: `global_vars.INTERVAL` (Update Interval) ≥ 1. Значения вне пределов
   редактор показывает в Problems, хотя сервер генерации кода их принимает — успешный `ab_api.py code` не доказывает,
   что проект чистый.
10. **Импорт сгенерированного файла в AppBlocks проверен** в октябре 2026 на проекте СКУД; ошибки, которые показал
   редактор, вошли в `check` (п. 8–9). Для нового типа правки всё равно попроси пользователя открыть проект и прислать Problems.
11. **Значения настроек с вариантами** (Format, Operator, CANINT…) - только из списка в blocks.md; `check` сверяет их
   с реестром редактора. Значения feature, которые зависят от runtime (BAUD у zephyr - `PL_SER_BAUD_*`), реестр
   tios не описывает: бери по образцу проекта того же runtime.
12. **Настройка в логике - по ID её автопеременной.** У каждой `stg_setting` есть переменная в `global_vars.AUTOVARS`
   (поля FEATURE/FEATURE_SETTING указывают на настройку). В `{{$ID}}` и `VARIABLE` блоков ставь **ID автопеременной**,
   а не ID `stg_setting`: иначе Problems «Invalid Variable» / ошибка var_undefined при генерации. То же с линиями Tibbit:
   у `tibbit_54` с `L1NAME='door'` есть автопеременная `door` (её ID - в AUTOVARS).
13. **Входы #54 и прерывания.** `L*MODE`: 0 - Standard Input (переменная), 1 - Button Input (событие On Button Pressed,
   `node_keypad` с `BUTTON = "<имя линии>_kp"`). Режима прерывания у #54 нет, `node_interrupt` к нему не подключить:
   короткие сигналы ловят On Variable Changed по переменной линии или Button Input.
14. **Жёлтые треугольники на холсте** (неподходящий разъём, нет разъёма, пустой M-сокет) - не ошибки Problems; проверяй
   `ab_tool.py check` (строки «плата: …», editor.md §9). Источнику питания #09/#10 ставь #18, а не #20/#21.

15. **Авто-переменные, которые создаёт редактор** (при генерации JSON добавляй их сами, иначе ошибки компиляции):
   | Источник | FEATURE / FEATURE_SETTING | Тип, DEFAULT |
   |---|---|---|
   | `stg_setting` | ID настройки / `SETTINGID` | float или string, значение настройки |
   | `tibbit_05` (порт) | ID Tibbit / `NAME` | byte, 1 |
   | линии #00-x, #03, #06, #07, #54 | ID Tibbit / `L1NAME`… | boolean; у реле DEFAULT 1 = выключено |
   | каналы #17/#16 | ID Tibbit / `L1NAME`… | word 0..100 |
   | каналы #13 / #61 | ID Tibbit / `CH1`… / `VIN1P`, `VIN1M`, `VIN2P`, `VIN2M`, `IIN1`, `IIN2` | float |
   | `modbus_device_register` | ID регистра / `NAME` | float (MULTIPLIER применяется) |
   | `unowiresensorval` | ID значения / `NAME` | float |
16. **Имена - идентификаторы Tibbo BASIC и не различают регистр.** Имя устройства Modbus не должно совпадать с именем
   переменной или регистра: Problems «Name conflict: soil1. No duplicate names allowed. Tibbo Basic identifiers are
   case-insensitive». Устройствам давай префикс (`mb_soil1`).

17. **Виджеты веб-консоли** - в `web_dashboard.WIDGET_GROUPS` (`{"id":"widget_group","settings":{"ID","GROUPID":"group1","NAME","WIDGETS":[…]}}`),
    поле `WIDGETS` оставляй пустым: генератор читает только группы. Поля виджетов - строки, как в редакторе (`"HAS_INPUT":"0"`).
    `button_widget.VARIABLE` = ID команды из `commands`, `switch_widget`/`card_widget.VARIABLE` = ID переменной.
18. **`linked_setting`** связывает поле feature с настройкой STG (меняется в веб-консоли без перепрошивки):
    проверено для `mqtt.MQTT_SERVER_HOST`, `sntp.SNTP_SERVER`, `web_dashboard.PASSWORD`, `cgg.PASSWORD` (пример tbt54_adv).
    Пароли - только так, а не значением в проекте; для поля пароля в группе настроек - `luis_item.CONTROL "PASSWORD"`, для IP - `"IPCTRL"`.
19. **`node_time_delay.DURATION`** - число или одна ссылка `{{$var}}`, без выражений (generated-code.md).
20. **Редактор при открытии нормализует и сохраняет проект сам**: новые координаты блоков, новые ID виджетов, перенос
    `WIDGETS` в `WIDGET_GROUPS`, удаление выключенных LCD-feature, `POLL_INTERVAL` у авто-переменных, шаблонные значения
    по умолчанию у авто-переменных Wi-Fi (`access_point`, `password` - это значения RAM до чтения настроек, сами настройки
    STG не меняются). Перед `update` через API скачай текущую версию и сравни: изменения редактора не должны пропасть
    незамеченными, а свои ты перезапишешь целиком.

## 5. Плагины (custom_feature) - формат
Плагин живёт в проекте внутри `custom_features.FEATURES` и выглядит так (сокращённо, по плагинам маркетплейса):
```json
{"id": "custom_feature", "settings": {"ID": "<ID>", "NAME": "Deadband", "FEATURE_ID": "node_custom_deadband",
 "VERSION": "1.0.0", "RUNTIMES": "tios", "TYPE": "block", "REQUIREMENTS": "", "DEPENDENCIES": "", "CAPABILITIES": "",
 "SETTINGS": [{"id": "custom_feature_setting", "settings": {"ID": "<ID>", "SETTING_ID": "threshold", "NAME": "Threshold",
    "TYPE": "value", "DATA_TYPE": "float", "REQUIRED": "1", "DEFAULT_VALUE": "", "REFID": "", "OPTIONS": [],
    "PIN_REQUIREMENT": "GPIO", "FEATURE_CAPABILITY": "", "STATE": "enabled"}}],
 "CODE_BLOCKS": [{"id": "custom_feature_code_block", "settings": {"ID": "<ID>", "TYPE": "code", "RUNTIME": "tios",
    "LOCATION": "block_trigger", "CODE_ID": "", "CONDITION": "", "CODE": "...Tibbo BASIC...\n{{block.output}}"}}],
 "VARIABLES": [{"id": "custom_feature_variable", "settings": {"ID": "<ID>", "NAME": "result", "DATA_TYPE": "string"}}]}}
```
- `TYPE`: `service` | `peripheral` | `block` | `array_item`; у block `FEATURE_ID` начинается с `node_custom_`.
  `RUNTIMES` - через запятую из tios, zephyr, micropython; `REQUIREMENTS` - tios, network.
- Настройка: `DATA_TYPE` string, byte, float, integer, boolean, dword, long; `STATE` enabled, disabled, hidden;
  `OPTIONS` - список `custom_feature_setting_option {LABEL, VALUE}` для выпадающего списка; `REFID` - ссылка на тип
  элемента (например, Tibbit для выбора сокета); `PIN_REQUIREMENT` - GPIO, INT, PWM, ADC, TX, RX, RTS, CTS, DTR, DSR.
- Код-блок: `LOCATION` - место вставки (`boot`, `block_trigger` для Block, или маркер сгенерированного кода, в т.ч.
  с подстановкой: `{{feature.settings.ID}}_done`); `TYPE` code или file; `CONDITION` - когда вставлять.
  В коде: `{{feature.settings.<SETTING_ID>}}` - значение настройки, `{{feature.settings.<Tibbit>}}_CS` и т.п. - имена,
  которые генератор даёт выбранному Tibbit; `{{block.output}}` - переход к следующему блоку.
- `VARIABLES` блока - его выходные параметры (видны следующему блоку как `{{$result}}`).
- Узел плагина на холсте - feature с `id` = FEATURE_ID; его порты задаёт плагин, поэтому `check` их не сверяет.

