# Что генерирует AppBlocks (runtime `tios`)

Проверено на проекте пользователя (TPP2W(G2), #13 в S9, #17 в S7, #10+#18, DHCP) через `POST /api/projects/code`
(`ab_api.py code p.json --outdir gen`). Результат — **обычный проект TIDE на Tibbo BASIC**, его можно открыть в TIDE,
собрать и проверять скиллом tibbo-firmware.

## Файлы
| Файл | Что внутри |
|---|---|
| `project.tpr` | `name=<проект>_dbg___<версия>`, `platform=TPP2W(G2)`, `debug=on`, `src_lib_ver=0_00`, список файлов |
| `global.tbh` | `#define` (INTERFACE_SWITCHING, SUPPORTS_TLS, DHCP_*, TBT_CLK_SOURCE…), `const` (FIRMWARE_VERSION, APP_ID = id проекта, линии Tibbit: `T13_S9_CLK=PL_IO_NUM_32`), include библиотек, `declare` переменных и процедур |
| `main.tbs` | `'****BOARD_CONFIG****'` (комментарий: какой Tibbit в каком сокете), `dim` переменных, `on_sys_init` → `boot()`, обработчики событий TiOS |
| `boot.tbs` | `sub boot()`: часовой пояс, `sys.onsystimerperiod=1`, сторожевой таймер, сеть (статический IP или `dhcp_start`), инициализация Tibbit (`tbt13_init(...)`, `tbt_pic_gra_init(...)`), `pat.play("B-B-B-")` |
| `device.tbs` | Интерфейсы и сокеты, колбэки библиотек (`callback_dhcp_ok`…), для каждой переменной — `var_<имя>_update / _update_completed / _set` |
| `libraries/…` | Копии библиотек Tibbo: time, datetime, sock, utils, dhcp, super_i2c, ssi, pic, tibbits/tbtNN |
| `cody.json` | Служебный файл ассистента (пустой) |

## Как устроено
- **Переменные** → глобальные `dim` + три процедуры. Аппаратные опрашиваются в `on_sys_timer` по `var_poll_timer`
  (период из Update Interval, по умолчанию 1000 мс): `var_X_update()` читает железо → `var_X_update_completed(value)`
  записывает и при изменении печатает `VAR> X changed…` (если `VARIABLES_DEBUG_PRINT`). `var_X_set(value)` — запись из логики.
- **Блоки** превращаются в код, вставленный в эти процедуры и обработчики. Поток On Variable Changed → в `'****var_X_changed****'`.
- **Маркеры вставки** `'****имя****'` — те же «Code Location» для своих плагинов: `GLOBAL_DEFINES`, `GLOBAL_CONSTS`,
  `GLOBAL_FILES`, `GLOBAL_INCLUDES`, `GLOBAL_DECLARATIONS`, `GLOBAL_DIMS`, `BOOT_DIMS`, `boot`, `boot_complete`,
  `EVENTS`, `on_sys_timer`, `var_poll_timer_elapsed`, `on_sock_data_arrival`, `on_net_link_change`,
  `callback_net_disconnected`, `interface_set`, `services_start`, `services_stop`, `callback_system_error`,
  `callback_dhcp_ok|failure|pre_clear_ip|pre_buffrq|buff_released`, `DEVICE_TBS_DIMS`, `DEVICE_TBS`,
  на каждую переменную `var_<X>_update|update_completed|updated|set|changed`, `var_poll_timer_<X>_elapsed`.
- Линии Tibbit в коде совпадают с `tps_check.py board <плата>` (S9 TPP2: A=32, B=33; S7: 15_TX3, 14_RX3, 3, 19_INT3).

## Блоки и настройки, проверенные генерацией (октябрь 2026)
Метки: **[генерация]** - проверено кодом от `POST /api/projects/code` (22.10.2026, TPP3W(G2) и TPP2W(G2), tios);
**[не проверено]** - ни импорт в редактор (Problems), ни компиляция в TIDE, ни железо не проверялись.
`ab_api.py code` работает без API-ключа [генерация].

- **Digital Line Set** (`node_digital_line_set`) [генерация]: `LINE_NUMBER="48", VALUE="0"` -> `io.lineset("48", "0")` - оба
  значения в кавычках. При `LINE_NUMBER="PL_IO_NUM_48"` будет `io.lineset("PL_IO_NUM_48", "0")`: строка неявно
  переводится в число (`val`) и даёт 0, то есть запись, скорее всего, уйдёт на линию 0 [не проверено в TIDE]. Как TIDE
  принимает `"48"` в аргументе типа `pl_io_num`, тоже [не проверено]. Блок **не генерирует `io.enabled`**: на линии,
  которую не сделал выходом фреймворк или Tibbit проекта, запись не подействует (tibbo-firmware SKILL.md §2).
  `ab_tool.py check`: ошибка, если `LINE_NUMBER` не число и не `{{$…}}`; предупреждение для линий вне 46-48 на TPP.
- **IF Condition** (`node_comparison`) [генерация]: аргумент `operator` уходит в Tibbo BASIC как есть: `"=="` -> `if a == b then`,
  `"<>"` -> `if a <> b then`. Редактор знает `=`, `<>`, `<`, `<=`, `>`, `>=` (для zephyr/micropython сам переводит `=` в `==`,
  `<>` в `!=`). `==` и `!=` для tios - ошибка `check` (компиляция в TIDE [не проверена]).
- **Custom Function** (`node_math_compound`) [генерация]: CODE становится телом `function <FUNCNAME>() as string` в device.tbs,
  объявление - в global.tbh, вызов - в месте блока. Внутри доступны процедуры фреймворка, например
  `signal_strength_set(&h1F)` [компиляция не проверена].
- **On Time Period** (`node_time_interval`) [генерация]: `sys.onsystimerperiod=1` (10 мс), в boot -
  `timer = INTERVAL*1000/sys.onsystimerperiod/10`, срабатывание при `count > timer`, то есть раз в N+1 тиков:
  0,5 с -> 51 тик = 0,51 с (+2 %), 5 с -> 5,01 с. Для точных интервалов учитывай.
- **`general.LEDPAT`** [генерация на 4gswitchover, water_level_control_cloud, wifiswitchover, tbt22]: при `"1"` в boot() добавляется
  `pat.play("R-R-~",PL_PAT_CANINT)` (мигание красным) перед `sys.halt` на трёх ошибках инициализации библиотеки Settings
  (stg_start, stg_check_all, stg_restore_multiple). В проекте без этих вызовов (tbt22) LEDPAT код не меняет. Стартовый
  `pat.play("B-B-B-",PL_PAT_CANINT)` в конце boot() есть при любом LEDPAT; свой `pat.play` из логики его перебивает.
- **Шкала уровня сигнала (5 синих LED) на TPP2/TPP3** [генерация на TPP3W(G2) и TPP2W(G2)]: global.tbh -
  `#define SIGNAL_STRENGTH_INDICATION 1`, `declare sub signal_strength_set(strength as byte)`,
  `declare sub signal_strength_indication_init()`; boot.tbs - `signal_strength_indication_init()` (линии `PL_IO_NUM_46/47/48` =
  reset/clock/data становятся выходами) и `signal_strength_set(0)` (шкала гаснет); device.tbs - `signal_strength_set`: 5 тактов
  по линии 47, данные на 48 активным LOW, биты 0..4 = LED 1..5. Вариант `SIGNAL_STRENGTH_INDICATION=2` - линии
  `PL_IO_NUM_19_SB1…23_SB5` (DS110x). Во время работы фреймворк вызывает `signal_strength_set(0)` только под
  `#IF CELLULAR_AVAILABLE`. Рецепт управления шкалой - editor.md §8.

## Что замечено (проверяй при ревью)
- Генератор **не останавливает** проект с #13 без #12: код инициализирует АЦП, но без ±15 В он будет читать мусор.
  Железо проверяй `tps_check.py`, а не полагайся на сборку.
- Комментарий «Set the timezone to UTC-12:00» стоит при `APP_TIMEZONE="0"` — комментарий шаблонный, верь значению.
- Debug-сборка (`debug=on`, `_dbg_` в имени); релиз — Run › Deploy Release Version / Download Release Binary (.tpc).
- Задача сборки (`/api/tasks`) живёт 3 минуты; для просмотра кода сборка не нужна — хватает `/api/projects/code`.

## Компиляция и что показал компилятор TIDE (проект «Умная теплица», TPP3W(G2), октябрь 2026)
Проверять сгенерированный код компилятором: `ab_api.py build p.json [--out fw]` (POST `/api/projects/code`, затем
`/api/projects/build` без ключа - тот же компилятор TIDE, что у Tibbo; вывод `output`, при успехе `tpc`). Ошибки ниже
`check` теперь ловит сам (`check_compile_pitfalls`), но новые случаи находит только компилятор.
- **Настройка STG в выражении** через `{{$ID stg_setting}}` → генератор оставляет `$<ID>` → `undeclared identifier '$…'`.
  Нужна авто-переменная настройки (format.md §4 п.12).
- **Удалены авто-переменные шаблона** (WIFAP/WSEC/WIFPW из примера wifiswitchover) → колбэк STG вызывает
  `var_WIFAP_update_completed` → `undeclared identifier`. Чистишь AUTOVARS - оставь те, что ссылаются на настройки.
- **#05 без авто-переменной порта** (byte, FEATURE_SETTING=NAME, DEFAULT 1) → в boot.tbs строка `<NAME>=0` →
  `undeclared identifier '<NAME>'`. Редактор создаёт её сам при добавлении Tibbit; при генерации JSON - добавляй.
- **1-Wire (#62, unowiresensors)** без Data Tables → `undeclared identifier 'tbl_select'`: нужны tbl ENABLED=1 и таблица
  `OWSENS` (структуру копируй из примера `tbt62`).
- **Custom Function** (`node_math_compound`) - функция объявляется с типом своей переменной (`function f() as float`),
  встроенный АЦП TPP3(G2) из неё компилируется: `adc.num = PL_ADC_NUM_0 : adc.enabled = YES : v = adc.getdata()`.

## Поведение сгенерированного кода (проверено по коду)
- **Реле и SSR (#03, #06, #07)**: в boot.tbs `io.enabled=YES`, затем `io.state` = значение по умолчанию переменной
  (DEFAULT 1 → HIGH, 0 → LOW). Эти Tibbit активны по LOW, поэтому DEFAULT 0 = нагрузка включается при подаче питания.
  Запись из логики - `io.lineset(<линия>, value)`: 0 = включить, 1 = выключить.
- **#17 / #16 (ШИМ на PIC)**: `tbt_pic_gra_pwm_config_simple(<tibbit>, PIC_PWMn, <FREQUENCY>, duty)`, duty 0..100,
  переменная word. Частота берётся из поля FREQUENCY Tibbit.
- **#61-1/#61-2**: `tbt61_init("…", TBT61_VOLTAGE_FOUR_SINGLE | …, <6 линий>, …)`, чтение
  `tbt61_read_adc(ch, VIN1P_SINGLE_ENDED, flags)` - переменная float. Режим MODE=SINGLE даёт 4 входа 0–10 В.
- **Регистры Modbus Master** опрашиваются сами: `var_X_update` ставит запрос в очередь (`modbus_master_enqueue_request`,
  если такого ещё нет). При таймауте значение **не сбрасывается** - в переменной остаётся последнее.
  Variable Set на переменную регистра отправляет запись в устройство (PresetMultipleRegisters).
- **MQTT**: `mqtt_start(current_interface, <host>, "<port>", "<user>", "<password>", "<client id>", MQTT_TLS)`;
  подписки - в `callback_mqtt_connect_ok`; `MQTT_LARGE_PACKETS 1`; публикация без связи отбрасывается (mqtt.md §4).
- `sys.onsystimerperiod=50` (0,5 с) при обычных On Time Period: `*_proc_timer` библиотек вызываются с нужным периодом.

## Найдено на TOTAL SMART SCHOOL GREENHOUSE 2 (ноябрь 2026, проверено по сгенерированному коду и компиляции)
- **Строка Tibbo BASIC - 255 байт, и MQTT это касается.** `mqtt_publish(topic, data, …)` собирает пакет одной строкой
  `chr(0)+chr(len(topic))+topic+data`: всё, что длиннее 255 байт вместе с топиком, обрезается **без ошибки** (компиляция
  проходит). float в шаблоне выводится как `ftofixed(x,4)` (до 12 символов), word - до 5, byte - до 3, boolean - 1.
  Телеметрию дели на несколько сообщений по топикам (`…/tele/env`, `…/tele/io` …). `ab_tool.py check` считает худший случай.
- **Delay с выражением.** `node_time_delay` генерирует `sys.timercountms + <DURATION> * 1000`: в `{{$a}} - 2` на 1000
  умножится только 2. Длительность считай в переменную (Variable Set) и указывай её одну.
- **Настройка STG как энергонезависимая переменная.** Variable Set на авто-переменную настройки вызывает
  `stg_set(...)` - значение пишется в EEPROM и переживает перезагрузку. Так хранят суточные счётчики, режим «авто»,
  флаги аварий. Пиши только по событию (порция полива, полночь), не по таймеру раз в секунду: EEPROM изнашивается.
- **On Modbus Response / On Modbus Timeout** (`node_modbus_response`, `node_modbus_timeout`) отдают `{{$device_id}}`
  (адрес на шине) и `{{$register_address}}`; ответ приходит на каждый успешный опрос любого устройства. Схема контроля
  связи: от события два и более IF `{{$device_id}} = N` (параметр виден только блоку, связанному с событием напрямую) →
  счётчик тайм-аутов +1 / сброс в 0; связь потеряна при 3 подряд (опрос 2 с + backoff 10 с). Сама переменная регистра
  при потере связи хранит последнее значение.
- **Все On Time Period стартуют от загрузки и идут в фазе**: таймеры 60, 30 и 600 с срабатывают в одну секунду. Если
  что-то должно происходить не одновременно (замер тока насоса и переключение ламп), делай один общий такт и сдвигай
  действия блоками Delay от него (насос 2 через 30 с, вентилятор через 45 с).
- **Время.** `node_datetime` → `node_datetime_format` (`datetime_timestamp_to_string`, коды `Y` (4 знака), `M`, `D`,
  `H`, `h`, `m`, `s`, `t`) → IF `{{$time_str}} >= 2025` - проверка, что часы синхронизированы (строки сравниваются
  как строки, генератор берёт `"2025"` в кавычки). Адрес SNTP - `linked_setting` на `SNTP_SERVER` (поле - IP, 15 символов).
- **Пароль веб-консоли**: `linked_setting` SETTINGID `PASSWORD` → настройка STG (строка) → в boot
  `http_server_password = <настройка>`; применяется после перезагрузки. `USER_PASSWORD` (роль user) генератор для tios
  не использует - роли есть только в zephyr (пример web-console-roles).
- **Виджеты веб-консоли** генератор берёт только из `web_dashboard.WIDGET_GROUPS` (`widget_group` → `WIDGETS`); старое
  поле `WIDGETS` (так в примерах appblocks.io) он игнорирует - в `dashboard_setup.json` группа пустая. Редактор при
  открытии переносит виджеты в группу сам; при загрузке через API - нет. Кнопка (`button_widget`) ссылается на ID
  команды (`commands` → `command`), её событие - `node_command_triggered`; ту же цепочку можно вызывать и из MQTT,
  связав оба события с первым блоком.
