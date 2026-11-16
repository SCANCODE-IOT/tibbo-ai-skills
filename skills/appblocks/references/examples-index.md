# Опубликованные проекты appblocks.io: что в них и в каком они состоянии

Все 79 проектов уроков и примеров appblocks.io (`https://appblocks.io/projects/<имя>.json`, имя - последний
сегмент страницы `appblocks.io/tutorials/*` или `appblocks.io/examples/*`), снято 16 ноября 2026.
Читай, когда пользователь просит пример под задачу («есть готовый проект с Modbus и MQTT?»), берёт проект Tibbo за
основу или спрашивает, почему пример не собирается. Сгенерировано `tools/build_examples_index.py`.

Платы: TPP2W(G2) - 76, TPP3W(G2) - 3. Среды: tios - 73, zephyr - 6.
Сборка компилятором Tibbo (проект сначала прошёл проверку редактора с её автоисправлениями - как при открытии в
редакторе): собирается - 68, Zephyr - через API не собрать - 6, не собирается - 5.

**Как читать столбцы.**
- **check** - `ab_tool.py check` по файлу как он опубликован. Предупреждения «Редактор ... включит сам» (облако без
  OTA/HTTP, выключенная библиотека блока, нет переменной порта #05) - не поломка: редактор исправляет это сам при
  открытии (format.md §4). Но если собираешь файл через API (`ab_api.py build`), внеси исправления в файл.
- **Редактор** - ошибки, которые остаются после проверки редактора (их он не исправит; вкладка Problems). Проверку
  запускали кодом самого редактора вне его окна - в редакторе список может немного отличаться.
- **Сборка** - компилятор Tibbo после проверки редактора. Zephyr через API не собрать (zephyr.md §4) - собирай в редакторе.

Сокеты Tibbit смотри в столбце «Tibbit»: в проектах Tibbo источник питания почти всегда в S11 + #18 в S12 на TPP2 и
S25 + #18 в S26 на TPP3 (power.md §2a скилла tibbo-firmware). В публичных примерах встречаются логин и пароль
облака в открытом виде - в свой проект не переноси, задай свои через настройки.

| Проект | Вид | Название | Плата | Среда | Tibbit (сокет:модель) | Сервисы | Блоков | check | Редактор | Сборка |
|---|---|---|---|---|---|---|---|---|---|---|
| `4gswitchover` | урок | 4G Switchover | TPP2W(G2) | tios | S1:#05 S2:#21 S5:#45-2 S11:#10 S12:#18 | Wi-Fi, сотовая связь, Bluetooth, HTTP-сервер, Modbus master, MQTT, веб-панель, LUIS, LCD | 7 | 0 ошибок, предупр. 2 | 0 ошибок | собирается |
| `accesscontrol1` | урок | Access Control 1 | TPP2W(G2) | tios | S2:#20 S3:#08 S5:#03-1 S6:#20 S11:#10 S12:#18 | LCD, HTTP-сервер, веб-панель | 15 | 0 ошибок, предупр. 2 | Invalid Variable: id_code. | собирается |
| `accesscontrol2` | урок | Access Control 2 | TPP2W(G2) | tios | S2:#20 S3:#08 S5:#03-1 S6:#20 S11:#10 S12:#18 | LCD, HTTP-сервер, веб-панель | 20 | 0 ошибок, предупр. 2 | Invalid Variable: id_code. | собирается |
| `accesscontrol3` | урок | Access Control 3 | TPP2W(G2) | tios | S2:#20 S3:#08 S5:#03-1 S6:#20 S11:#10 S12:#18 | LCD, HTTP-сервер, веб-панель | 33 | 0 ошибок, предупр. 3 | Invalid Variable: id_code. | собирается |
| `accesscontrol4` | урок | Access Control 4 | TPP2W(G2) | tios | S2:#20 S3:#08 S5:#03-1 S6:#20 S11:#10 S12:#18 | LCD, HTTP-сервер, веб-панель | 37 | 0 ошибок, предупр. 3 | Invalid Variable: id_code. | собирается |
| `accesscontrol5` | урок | Access Control 5 | TPP2W(G2) | tios | S2:#20 S3:#08 S5:#03-1 S6:#20 S11:#10 S12:#18 | таблицы, LCD, HTTP-сервер, веб-панель | 47 | 0 ошибок, предупр. 3 | Invalid Variable: id_code. | собирается |
| `accesscontrol6` | урок | Elements - Access Control 6 | TPP2W(G2) | tios | S2:#20 S3:#08 S5:#03-1 S6:#20 S7:#00-1 S11:#10 S12:#18 | таблицы, LCD, HTTP-сервер, веб-панель | 49 | 0 ошибок, предупр. 3 | Invalid Variable: id_code.; Interrupt line is not set | собирается |
| `blockstacking` | урок | Block Stacking | TPP2W(G2) | tios | S11:#10 S12:#18 | — | 9 | 0 ошибок, предупр. 2 | 0 ошибок | собирается |
| `bp01` | пример | bp01 | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | Modbus master | 4 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `bp05` | пример | BP05 | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | Modbus master | 11 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `bpsensorstoabc` | урок | BP sensor to AppBlocks Cloud | TPP2W(G2) | tios | S1:#05 S2:#20 S11:#10 S12:#18 | таблицы, LCD, Modbus master, AppBlocks Cloud | 2 | 0 ошибок, предупр. 2 | Widget is not set | собирается |
| `bpsensorstoconsole` | урок | BP Sensors to Console | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | Modbus master, LCD | 8 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `bpsensorstodashboard` | урок | BP Sensors to Dashboard | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | HTTP-сервер, Modbus master, веб-панель | 8 | 0 ошибок, предупр. 3 | 0 ошибок | собирается |
| `bpsensorstolog` | урок | BP Sensors to Log | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | таблицы, HTTP-сервер, Modbus master, веб-панель | 9 | 0 ошибок, предупр. 2 | 0 ошибок | собирается |
| `bpsensorstomqtt` | урок | BP Sensors to MQTT | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | Modbus master, MQTT | 11 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `bpsensortolcdgraph` | урок | BP sensor to LCD graph | TPP2W(G2) | tios | S1:#05 S2:#20 S11:#10 S12:#18 | LCD, Modbus master | 2 | 0 ошибок | Widget is not set | собирается |
| `cold_chain_logger` | пример | cold_chain_logger | TPP2W(G2) | zephyr | S1:#00-3 S2:#30 S11:#10 S12:#18 | таблицы, LCD, HTTP-сервер, веб-панель | 67 | 0 ошибок, предупр. 2 | — | Zephyr - через API не собрать |
| `conditions` | урок | Conditions and Math | TPP2W(G2) | tios | S11:#10 S12:#18 | LCD | 5 | 0 ошибок | 0 ошибок | собирается |
| `cp01` | пример | cp01 | TPP2W(G2) | tios | S1:#00-3 S2:#29 | — | 2 | 0 ошибок | 0 ошибок | собирается |
| `cp02` | пример | cp02 | TPP2W(G2) | tios | S1:#00-3 S2:#30 | — | 3 | 0 ошибок | 0 ошибок | собирается |
| `cp03` | пример | cp03 | TPP2W(G2) | tios | S1:#00-3 S2:#28 S11:#10 S12:#18 | — | 2 | 0 ошибок | 0 ошибок | собирается |
| `dashboard-command` | пример | dashboard-command | TPP2W(G2) | tios | S11:#09 S12:#18 | HTTP-сервер, веб-панель | 5 | 0 ошибок, предупр. 3 | 0 ошибок | собирается |
| `datetimeformatting` | урок | Date & Time Formatting | TPP2W(G2) | tios | S11:#10 S12:#18 | расписание | 4 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `distance-meter` | пример | distance_meter | TPP2W(G2) | tios | S1:#01 S2:#20 S3:#00-3 S11:#10 S12:#18 | таблицы, LCD | 4 | 0 ошибок, предупр. 1 | Widget is not set | собирается |
| `helloworld` | урок | Hello World | TPP2W(G2) | tios | S11:#10 S12:#18 | LCD | 2 | 0 ошибок | 0 ошибок | собирается |
| `http-post-tls` | пример | HTTP Post TLS | TPP2W(G2) | zephyr | S11:#33 S12:#18 | флеш, HTTP-клиент, TLS | 5 | 0 ошибок, предупр. 1 | — | Zephyr - через API не собрать |
| `http-request` | пример | http-request | TPP2W(G2) | tios | S11:#09 S12:#18 | — | 5 | 0 ошибок, предупр. 2 | 0 ошибок | собирается |
| `http-server-tls` | пример | HTTP Server TLS | TPP2W(G2) | zephyr | — | флеш, HTTP-сервер, TLS, веб-панель | 5 | 0 ошибок, предупр. 2 | — | Zephyr - через API не собрать |
| `hydroponics` | пример | hydroponics-controller | TPP3W(G2) | tios | S1:#02 S2:#19 S5:#05 S6:#20 S7:#00-3 S9:#01 S10:#20 S11:#03-1 S13:#05 S14:#20 S15:#03-1 S17:#06 S18:#20 S21:#61-1 S25:#33 S26:#18 | расписание, таблицы, HTTP-сервер, Modbus master, Modbus slave, веб-панель | 212 | 0 ошибок, предупр. 5 | проверку редактора вне редактора запустить не удалось | собирается |
| `lcd-menu` | пример | Settings (and LCD menu) | TPP2W(G2) | tios | S11:#10 S12:#18 | HTTP-сервер, веб-панель, LCD | 10 | 0 ошибок, предупр. 1 | Enter LCD Menu needs a display with a menu: add a display peripheral. | не собирается: 'entering_menu' |
| `lcd-widgets` | пример | LCD Widgets | TPP2W(G2) | tios | S11:#09 S12:#21 | LCD | 19 | 0 ошибок, предупр. 2 | Enter LCD Menu needs a display with a menu: add a display peripheral.; Widget is not set | не собирается: 'entering_menu' |
| `luis` | урок | LUIS Interface | TPP2W(G2) | tios | S11:#10 S12:#18 | Bluetooth, HTTP-сервер, LUIS, веб-панель, LCD | 8 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `modbusgateway` | пример | bp_modbus_gateway_lcd_v11 | TPP2W(G2) | zephyr | S1:#05 S2:#20 S3:#05 S5:#05 S6:#20 S7:#05 S11:#33 S12:#18 | Wi-Fi, Modbus master, HTTP-сервер, веб-панель, таблицы, LCD | 59 | 0 ошибок, предупр. 2 | — | Zephyr - через API не собрать |
| `modbusmqtt` | пример | ModbusMQTTGateway | TPP2W(G2) | zephyr | S1:#05 S2:#20 S11:#33 S12:#18 | флеш, MQTT, HTTP-сервер, TLS, Modbus master, веб-панель | 64 | 0 ошибок, предупр. 1 | — | Zephyr - через API не собрать |
| `modbuspump` | пример | modbuspump | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | HTTP-сервер, Modbus master, веб-панель | 26 | 0 ошибок, предупр. 4 | проверку редактора вне редактора запустить не удалось | не собирается: 'T05_S1' |
| `modbusscan` | пример | modbusscan | TPP2W(G2) | tios | S1:#05 S2:#21 | Modbus master | 5 | 0 ошибок, предупр. 3 | 0 ошибок | собирается |
| `modbustcpmaster` | пример | modbustcpmaster | TPP2W(G2) | tios | S11:#10 S12:#18 | Modbus master | 2 | 0 ошибок | 0 ошибок | собирается |
| `modbustcpslave` | пример | modbustcpslave | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | Modbus master, Modbus slave | 4 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `mqtt-bp01` | пример | mqtt-bp01 | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | Modbus master, MQTT | 7 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `mqtt-pub-sub` | пример | mqttpubsub | TPP2W(G2) | tios | S11:#10 S12:#18 | MQTT | 4 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `periodictimers` | урок | Periodic Timers | TPP2W(G2) | tios | S11:#10 S12:#18 | — | 4 | 0 ошибок | 0 ошибок | собирается |
| `pwm_cycle` | пример | pwm_tbt_17 | TPP2W(G2) | tios | S2:#20 S3:#17 S11:#10 S12:#18 | — | 4 | 0 ошибок | 0 ошибок | собирается |
| `pwmlights1` | урок | PWM Light Control 1 | TPP2W(G2) | tios | S9:#16 S10:#21 S11:#10 S12:#18 | HTTP-сервер, веб-панель, LCD | 25 | 0 ошибок, предупр. 2 | 0 ошибок | собирается |
| `pwmlights2` | урок | PWM Light Control 2 | TPP2W(G2) | tios | S9:#16 S10:#21 S11:#10 S12:#18 | HTTP-сервер, веб-панель, LCD | 12 | 0 ошибок, предупр. 2 | 0 ошибок | собирается |
| `remote-reboot` | пример | ABC-enabled Relay with Tibbit 03-1 | TPP2W(G2) | tios | S1:#03-1 S2:#21 S9:#10 S10:#18 | таблицы, HTTP-сервер, AppBlocks Cloud, Azure | 5 | 0 ошибок, предупр. 2 | 0 ошибок | собирается |
| `rs232_dispatcher` | пример | RS232Dispatcher | TPP3W(G2) | tios | S1:#01 S2:#19 S5:#01 S6:#19 S9:#01 S10:#19 S13:#01 S14:#19 S27:#10 S28:#18 | HTTP-сервер, веб-панель | 33 | 0 ошибок, предупр. 2 | 0 ошибок | собирается |
| `scheduler` | урок | Scheduler | TPP2W(G2) | tios | S11:#10 S12:#18 | расписание | 3 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `schedulersunrisesunset` | урок | Scheduler, Sunrise and Sunset | TPP2W(G2) | tios | S5:#03-1 S6:#20 S11:#09 S12:#18 | расписание | 6 | 0 ошибок | 0 ошибок | собирается |
| `settings` | урок | Settings (and Web Interface) | TPP2W(G2) | tios | S11:#10 S12:#18 | HTTP-сервер, веб-панель, LCD | 8 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `settingsinit` | урок | Setting Initialization | TPP2W(G2) | tios | S11:#10 S12:#18 | — | 15 | 0 ошибок | 0 ошибок | собирается |
| `smart_plants` | пример | Smart Plants | TPP2W(G2) | tios | S1:#10 S2:#18 S3:#03-1 S4:#21 S5:#17 S6:#20 S7:#16 S11:#10 S12:#18 | расписание, HTTP-сервер, веб-панель, LCD | 37 | 0 ошибок, предупр. 2 | 0 ошибок | собирается |
| `sprinkler1` | урок | Sprinkler Control 1 | TPP2W(G2) | tios | S5:#03-1 S6:#20 S11:#10 S12:#18 | расписание | 8 | luis/luis/GROUPS/luis_group/SETTINGS: SETTINGID=la51hwbvdid6… | 0 ошибок | собирается |
| `sprinkler2` | урок | Sprinkler Control 2 | TPP2W(G2) | tios | S5:#03-1 S6:#20 S11:#10 S12:#18 | расписание, таблицы, Bluetooth, HTTP-сервер, LUIS, веб-панель | 9 | 0 ошибок, предупр. 2 | 0 ошибок | собирается |
| `sprinkler3` | урок | Sprinkler Control 3 | TPP2W(G2) | tios | S5:#03-1 S6:#20 S11:#10 S12:#18 | расписание, таблицы, Bluetooth, HTTP-сервер, LUIS, веб-панель, LCD | 13 | 0 ошибок, предупр. 2 | Widget is not set | собирается |
| `sprinkler4` | урок | Sprinkler Control 4 | TPP2W(G2) | tios | S5:#03-1 S11:#10 S12:#18 | расписание, таблицы, Bluetooth, HTTP-сервер, LUIS, веб-панель, LCD | 25 | 0 ошибок, предупр. 3 | Widget is not set | собирается |
| `sprinkler5` | урок | Tutorial- Sprinkler Control 5 | TPP2W(G2) | tios | S5:#03-1 S6:#20 S11:#10 S12:#18 | расписание, таблицы, Bluetooth, HTTP-сервер, LUIS, веб-панель, LCD | 27 | 0 ошибок, предупр. 3 | проверку редактора вне редактора запустить не удалось | собирается |
| `sprinkler6` | урок | Sprinkler Control 6 | TPP2W(G2) | tios | S5:#03-1 S6:#20 S11:#10 S12:#18 | расписание, таблицы, Bluetooth, HTTP-сервер, LUIS, веб-панель, LCD | 39 | 0 ошибок, предупр. 3 | проверку редактора вне редактора запустить не удалось | собирается |
| `tbt01` | пример | liquid_level_sensing | TPP3W(G2) | tios | S3:#00-3 S4:#21 S5:#01 S6:#21 S23:#10 S24:#18 | расписание, HTTP-сервер, веб-панель | 10 | 0 ошибок, предупр. 3 | 0 ошибок | собирается |
| `tbt08` | пример | Access Control Example | TPP2W(G2) | tios | S2:#20 S3:#08 S5:#03-1 S6:#20 S11:#10 S12:#18 | таблицы, LCD, HTTP-сервер, веб-панель, AppBlocks Cloud | 23 | 0 ошибок, предупр. 4 | Invalid Variable: id_code. | собирается |
| `tbt22` | пример | RTD Sensor | TPP2W(G2) | tios | S1:#22 S2:#21 S11:#10 S12:#18 | — | 7 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `tbt26_temp_control` | пример | irtibbit_advb | TPP2W(G2) | tios | S1:#26 S2:#20 S3:#05 S11:#10 S12:#18 | таблицы, LCD, HTTP-сервер, Modbus master, Modbus slave, AppBlocks Cloud, веб-панель | 159 | конфликт имён, предупр. 5 | Name conflict: t1; Name conflict: bp01; Name conflict: bp03 (No duplicate names allowed); Widget is not set; Screen is not set | не собирается: 'lcd_display_widgets' |
| `tbt28` | пример | Tibbit28 | TPP2W(G2) | tios | S1:#00-3 S2:#28 S11:#10 S12:#18 | — | 2 | 0 ошибок | 0 ошибок | собирается |
| `tbt29` | пример | tbt29 | TPP2W(G2) | tios | S1:#00-3 S2:#29 S11:#10 S12:#18 | — | 2 | 0 ошибок | 0 ошибок | собирается |
| `tbt30` | пример | tbt30 | TPP2W(G2) | tios | S1:#00-3 S2:#30 | — | 3 | 0 ошибок | 0 ошибок | собирается |
| `tbt54` | пример | Cycle Counting | TPP2W(G2) | tios | S1:#54 S2:#20 S9:#10 S10:#18 | таблицы, HTTP-сервер | 4 | 0 ошибок | 0 ошибок | собирается |
| `tbt54_adv` | пример | cycle_counter | TPP2W(G2) | tios | S1:#54 S2:#20 S9:#12 S11:#10 S12:#18 | таблицы, HTTP-сервер, AppBlocks Cloud, веб-панель | 6 | 0 ошибок, предупр. 3 | 0 ошибок | собирается |
| `tbt61` | пример | tibbit61_CO2 | TPP2W(G2) | tios | S5:#61-1 S9:#10 S10:#18 | — | 3 | 0 ошибок | 0 ошибок | собирается |
| `tbt62` | пример | T62_test | TPP2W(G2) | tios | S1:#62 S2:#21 S11:#10 S12:#18 | таблицы, 1-Wire, HTTP-сервер, веб-панель | 6 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `tbt63` | пример | AC Voltage Detector with Tibbit 63 | TPP2W(G2) | tios | S1:#63-1 S11:#10 S12:#18 | — | 5 | 0 ошибок | 0 ошибок | собирается |
| `timers` | урок | Timers | TPP2W(G2) | tios | S11:#10 S12:#18 | LCD | 7 | 0 ошибок | 0 ошибок | собирается |
| `timerscontinued` | урок | Timers (Continued) | TPP2W(G2) | tios | S11:#10 S12:#18 | LCD | 14 | 0 ошибок | 0 ошибок | собирается |
| `timersstartstop2` | урок | Tutorial- Timers, Starting and Stopping 2 | TPP2W(G2) | tios | S11:#10 S12:#18 | LCD | 14 | 0 ошибок | 0 ошибок | собирается |
| `tripwire` | пример | golf_counter | TPP2W(G2) | tios | S1:#00-1 S2:#20 S3:#00-3 S5:#10 S6:#20 | таблицы, AppBlocks Cloud, LCD | 67 | 0 ошибок, предупр. 3 | Widget is not set | собирается |
| `variables` | урок | Variables and Arithmetic | TPP2W(G2) | tios | S11:#10 S12:#18 | — | 3 | 0 ошибок | 0 ошибок | собирается |
| `water_level_control_cloud` | пример | modbus_dosing_abc | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | таблицы, HTTP-сервер, Modbus master, веб-панель, LCD, AppBlocks Cloud | 85 | 0 ошибок, предупр. 6 | проверку редактора вне редактора запустить не удалось | не собирается: 'upload_started' |
| `web-console-roles` | пример | WebConsoleUserRoles | TPP2W(G2) | zephyr | — | флеш, HTTP-сервер, веб-панель | 0 | 0 ошибок | — | Zephyr - через API не собрать |
| `wifiswitchover` | урок | Wi-Fi Switchover | TPP2W(G2) | tios | S1:#05 S2:#21 S11:#10 S12:#18 | Wi-Fi, Bluetooth, HTTP-сервер, Modbus master, MQTT, веб-панель, LUIS, LCD | 7 | 0 ошибок, предупр. 1 | 0 ошибок | собирается |
| `workflow-line` | пример | workflow-line | TPP2W(G2) | tios | S11:#09 | таблицы, HTTP-сервер, AppBlocks Cloud | 3 | 0 ошибок, предупр. 3 | 0 ошибок | собирается |
| `workflow-whatsapp` | пример | workflow-whatsapp | TPP2W(G2) | tios | S11:#09 | таблицы, HTTP-сервер, AppBlocks Cloud | 3 | 0 ошибок, предупр. 3 | 0 ошибок | собирается |
