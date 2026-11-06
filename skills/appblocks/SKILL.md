---
name: appblocks
description: Use when working with Tibbo AppBlocks (app.appblocks.io, AppBlocks Cloud) - reading, explaining, reviewing, changing or generating an AppBlocks project (exported JSON), visualising its logic and Tibbit hardware, using the AppBlocks Cloud API (projects, devices, OTA, workflows), or working in the AppBlocks editor in the browser.
license: MIT (Tibbo examples and reference data - see NOTICE)
compatibility: Any agent that reads SKILL.md (Claude, Codex, Gemini CLI, Kimi Code, Deep Code, OpenCode and others). Install next to the tibbo-firmware skill. Scripts need Python 3.9+ (standard library only); cloud commands need network access to api.appblocks.io.
metadata:
  author: Scancode (SCANCODE-IOT)
  version: "2.0.0"
  repository: https://github.com/SCANCODE-IOT/tibbo-claude-skills
---

# Tibbo AppBlocks: проекты, логика, железо, облако

AppBlocks — визуальный конструктор прошивок Tibbo: проект = плата + Tibbit/периферия + сервисы (features) +
логика из блоков. Из проекта генерируется прошивка: **`runtime: tios`** — Tibbo BASIC для TiOS (TPP2, TPP3, DS1101,
DS1102, EM510), **`zephyr`** — Zephyr C (сотни плат и TPP2/TPP3), `micropython`. AppBlocks Cloud — устройства,
OTA, переменные/таблицы/команды, облачные workflow, дашборды, HTTP API.
Ручной код на Tibbo BASIC — скилл tibbo-firmware; им же проверяй железо и код, сгенерированный для `tios`.

| Файл | Когда открывать |
|---|---|
| `references/editor.md` | Как устроен редактор и проект: шаги Hardware/Features/Application, Import/Export, Run/Debug/Release, runtime, **правила потоков** (поток с события, нет циклов, параметры видны только следующему блоку, ASYNC теряет параметры), переменные, плагины, частые ошибки. **Читать перед объяснением, ревью или проектированием логики.** |
| `references/format.md` | Формат экспорта JSON: верх, группы feature, узлы, связи, `{{$…}}`, правила правки, формат плагинов (§5). **Читать перед любой правкой JSON.** |
| `references/blocks.md` | **Все 168 блоков редактора** по категориям палитры: порты (`portId`) с параметрами, настройки с вариантами и значениями по умолчанию, нужная feature, ASYNC; скрытые/устаревшие отдельно. Снято из реестра app.appblocks.io. **Основной справочник портов и полей.** |
| `references/features.md` | Feature, сервисы-библиотеки, вложенные элементы (variable, timer, tbl_table…), поля `tibbit_NN`, периферия, виджеты LCD и веб-консоли - поля, варианты, ограничения по платам. |
| `references/catalog.md` | Поля feature и узлов в экспортах Tibbo (ModbusMQTTGateway, bp_modbus_gateway_lcd) с примерами значений, поля Tibbit, структуры Modbus/LUIS. Полный список блоков и полей - blocks.md и features.md. |
| `references/generated-code.md` | Что генерирует AppBlocks для `tios`: файлы TIDE-проекта, переменные → процедуры `var_X_*`, маркеры вставки кода, замеченные особенности. |
| `references/catalog-examples.md` | Как блоки и Tibbit реально используются в **78 проектах appblocks.io** (59 типов узлов, 28 Tibbit): типичные связки, аргументы, сокеты. |
| `references/mqtt.md` | **MQTT**: feature `mqtt` и блоки, IP брокера через настройку, поведение библиотеки (публикация без связи теряется, переподключение), свой брокер Mosquitto (конфиг, проверка `mosquitto_sub/pub`, частые проблемы), приёмник на компьютере. |
| `references/api.md` | AppBlocks Cloud API: авторизация, проекты (код, сборка, версии, OTA, бандлы), устройства, группы, workspaces, workflow, дашборды. |
| `scripts/ab_pairs.py`, `data/appblocks_pairs.json` | Правила жёлтых треугольников на холсте Hardware (снято из кода редактора); вызывается из `ab_tool.py check`. |
| `scripts/ab_tool.py` | Офлайн-разбор проекта: `summary`, `check` (связи, ссылки, порты и значения по реестру редактора), `lookup <блок\|feature\|слово>`, `flow` (схема логики SVG), `tps` (железо → tps_check), `nodes`, `ids`. |
| `data/registry.json`, `scripts/build_registry.py`, `scripts/extract_registry.js` | Реестр редактора (блоки, feature, элементы, Tibbit, периферия, виджеты) и как его обновить: JS в браузере на app.appblocks.io → `build_registry.py` пересобирает registry.json, blocks.md, features.md. |
| `scripts/ab_api.py` | Клиент API: `me`, `projects`, `project <id> --out`, `versions`, `workspaces`, `devices`, `device`, `get`, `code`, `build` (компилятор TIDE Tibbo, без ключа), `examples`/`example <имя>` (с запасным путём через appblocks.io), запись — только `create`/`update … --yes`. |
| `tests/run.sh` | Офлайн-тесты инструментов на примерах (и мост в tps_check, если tibbo-firmware лежит рядом). |
| `examples/*.json` | 6 проектов Tibbo: Modbus-шлюз с LCD на 4×RS485 и Modbus→MQTT (`ModbusMQTTGateway`, он же пример modbusmqtt; zephyr, GitHub), sprinkler5, accesscontrol6, hydroponics (TPP3), water_level_control_cloud (с appblocks.io, в т.ч. tios); `greenhouse2_tpp3.json` - TOTAL SMART SCHOOL GREENHOUSE 2 (TPP3W(G2): полив «цикл и замачивание» с блокировками, контроль связи Modbus и тока насосов, настройки в EEPROM, веб-панель с кнопками, телеметрия до 255 байт на сообщение; 0 ошибок в редакторе, компилируется), `greenhouse2_logger.py` - приёмник MQTT → SQLite → графики и `greenhouse2_instruction.md` - инструкция для пользователей (пусконаладка, насосы, бак, тревоги). |

**Windows:** скрипты запускай через `python` (или `python3`), вывод всегда UTF-8; при `CERTIFICATE_VERIFY_FAILED` в `ab_api.py` проверку не отключай - `pip install truststore` (или `certifi`, или `SSL_CERT_FILE` с бандлом Git), диагностика `ab_api.py tls`.

Железо проверяет `tps_check.py` из скилла tibbo-firmware (обычно `../tibbo-firmware/scripts/tps_check.py` рядом с папкой этого скилла; если нет - найди файл поиском): он же
рисует плату в стиле редактора AppBlocks (сокеты с номерами линий, SERn(k)/INTn(k), Tibbit, PoE, +5V, бюджет питания).

## Порядок для любого агента (коротко)

1. Проект правь только скриптом Python по копии экспорта, не руками. Перед выдачей: `python3 scripts/ab_tool.py check p.json` - 0 ошибок.
2. Порты, поля и значения блоков бери из `references/blocks.md` или `ab_tool.py lookup <блок>`. Не выдумывай блоки и поля.
3. Железо (Tibbit, сокеты, питание) - через `ab_tool.py tps` и `tps_check.py` из скилла tibbo-firmware.
4. Любая запись в облако AppBlocks (create, update, OTA, команды устройствам) - только после явного «да» пользователя на конкретный вызов.
5. Ключ API не печатай и не сохраняй. Пароли - через настройки, не открытым текстом в проекте.
6. **Скрипты запустить нельзя** (веб-чат): скажи «скриптами не проверено», дай файл и команды проверки, чтобы пользователь запустил их у себя, и попроси прислать вкладку Problems из редактора.
7. Скрипты лежат в папке скилла: запускай их с путём от неё или перейди в неё. На Windows - `python` вместо `python3`.

## 1. Откуда взять проект
1. **API** (лучший путь): `ab_api.py projects` → `ab_api.py project <id> --out p.json`. Ключ `abk_…` из Settings →
   API Keys в веб-приложении; передаётся `x-api-key`. Первым делом `ab_api.py me` (аккаунт и скоупы read/write).
2. **Экспорт**: в редакторе кнопка **Export** скачивает `.json`; пользователь прикладывает файл.
3. **Браузер** (§5) — смотреть проект в редакторе под входом пользователя.
4. **Примеры**: `https://appblocks.io/projects/<имя>.json`, где имя — последний сегмент страниц
   `appblocks.io/tutorials/*` и `appblocks.io/examples/*` (78 проектов: sprinkler1–6, accesscontrol1–6, modbusgateway,
   modbusmqtt, tbt22, hydroponics, http-server-tls…). `GET /api/projects/examples` в октябре 2026 отвечал 500.

**Сеть.** Если агент работает в облачной песочнице со списком разрешённых сайтов, хосты AppBlocks доступны только после
того, как пользователь добавит `api.appblocks.io` и `appblocks.io` в разрешённые (в Claude: claude.ai → Settings →
Capabilities, в Team/Enterprise - администратор; в других сервисах - их настройка доступа к сети); до этого прокси
отвечает 403. Проверка: `ab_api.py me`. Если сеть закрыта: скрипт на компьютере пользователя, браузер или файл экспорта.
Документацию appblocks.io читай веб-инструментом агента, если он есть (карта: `https://appblocks.io/sitemap.xml`).

**Ключ.** Только из окружения (`APPBLOCKS_API_KEY` или файл `APPBLOCKS_API_KEY_FILE` с правами 600, удалить после).
Не печатать, не сохранять в файлы, память, артефакты. У устройства поле `key` (MQTT) тоже не показывать.

## 2. Разбор и ревью
```
python3 scripts/ab_tool.py summary p.json        # плата, Tibbit, сервисы, переменные, таблицы, цепочки событий
python3 scripts/ab_tool.py check   p.json        # битые связи и ссылки, дубли ID, сокеты; порты, варианты настроек, feature - по реестру редактора
python3 scripts/ab_tool.py lookup  node_table   # порты и настройки блока (или feature/элемента) из реестра
python3 scripts/ab_tool.py flow    p.json flow.svg
python3 scripts/ab_tool.py tps     p.json --vin 24 --out cfg.json && python3 <tps_check.py> check cfg.json --svg board.svg
python3 scripts/ab_api.py code p.json --outdir gen   # что сгенерирует AppBlocks (для tios — Tibbo BASIC)
python3 scripts/ab_api.py build p.json --out fw      # компилятор TIDE у Tibbo: ошибки компиляции, fw.tpc (ключ не нужен)
```
- Напряжение питания в проекте не хранится (только `POWERADAPTER`) — спроси или прими 24 В и напиши допущение.
- Ответ: что делает устройство (по цепочкам, человеческим языком) → картинки платы и логики → проблемы → что проверить.
- Ревью логики по правилам editor.md §4: поток без события (не попадёт в прошивку), параметр предыдущего блока после
  ASYNC-блока или через блок (пусто), рекурсия On Variable Changed, циклы через команды без условия выхода,
  `modbus_timeout`/`tbl_record_not_found` никуда не ведут, длинные потоки на tios, таблицы с большим MAXRECORDS,
  пароли открытым текстом (MQTT_PASSWORD, PASSWORD, WPW) вместо настроек, выключенные feature, нужные узлам,
  блоки, которых нет в палитре (`node_math`, `node_modbus_register` - устаревшие: предложи замену из blocks.md).
- Ревью железа — `tps_check.py` (предупреждения AppBlocks про -SDWN, ±15 В, serial-сокеты, питание он повторяет).
  **Жёлтые треугольники на холсте** («Incorrect pair», «Connector required», «Tibbit required») не видны в Problems:
  `ab_tool.py check` пишет их строками «плата: …» (editor.md §9). Таблица разъёмов редактора строже документации:
  источнику питания #09/#10/#25/#33 - только #18. Для публичных решений - пара, которую одобряет редактор; вариант
  «по документации» - отдельно, как нишевый, с пометкой о риске. Номера клемм разъёмов - вид **Wiring** (editor.md §9а).
- `ab_tool.py check` предупреждает, если `{{$param}}` не может прийти в блок: входящие связи не дают такого параметра
  (параметр виден только следующему блоку). Порты, у которых реестр не знает параметров, не проверяются.

## 3. Правка и генерация
Порядок: format.md §4 → правка **копии** экспорта скриптом Python (не строками вручную) → `check` = 0 ошибок →
`tps_check` для железа → `flow` для картинки → отдать файл (импорт кнопкой **Import**) или, с согласия, через API.
- Новые ID: `ab_tool.py ids N`. Порты и поля - из blocks.md / `ab_tool.py lookup` (реестр редактора), примеры связок - из
  catalog-examples.md или такого же узла в проектах пользователя. Нужного блока нет - плагин Block (format.md §5).
- Логику строй по правилам потоков: каждое действие достижимо из события; значения между потоками — через переменные;
  повторы — таймеры/On Time Period/команды; после ASYNC — только переменные.
- Tibbit: сначала подбор и проверка раскладки/питания (tibbo-firmware), затем `tibbit_NN` с SOCKET и полями по образцу.
- Минимальная основа для нового tios-проекта - пример `tbt22` (`appblocks.io/projects/tbt22.json`: TPP2W(G2), 47 feature,
  датчик #22 с разъёмом #21 и источник #10 с #18, несколько блоков); плату меняй полем `device` до добавления Tibbit.
- **Проект на основе примера**: меняешь данные (настройки STG, команды, таблицы) — **оставляй ID тех, что переиспользуешь,
  а ненужные удаляй вместе со всеми ссылками на них**, включая панели (`web_dashboard`, `luis`, `ds_man`, `lcd_menu`, `cgg`:
  пункты настроек, кнопки-команды, таблицы консоли). Никогда не пересоздавай элемент с новым ID, не заменив старый
  ID по всему файлу. Так появились 9 из 11 ошибок первого СКУД-проекта (format.md §4 п.8).
- **Update Interval** (`global_vars.INTERVAL`) — не меньше 1 с. Короткие сигналы — на линию прерывания (editor.md §7а).
- `ab_tool.py check` = 0 ошибок обязателен перед записью; `ab_api.py code` без ошибок **не** означает, что Problems пуст.
- **Компиляция перед загрузкой - обязательно**: `ab_api.py build p.json` (сборщик Tibbo, тот же компилятор TIDE).
  Ошибки, которые нашёл компилятор и которые теперь ловит `check` (generated-code.md, format.md §4 п.15-16):
  настройка STG в выражении - только через её авто-переменную; у #05 нужна авто-переменная порта (NAME, byte);
  1-Wire (#62) требует Data Tables с таблицей OWSENS; не удаляй авто-переменные настроек шаблона.
- **Имена не различают регистр и не повторяются**: устройство Modbus и его регистр с одним именем - Problems
  «Name conflict». Устройствам - префикс `mb_`.
- **Реле и SSR (#03, #06, #07) активны по LOW**: уровень линии при старте = значение по умолчанию переменной.
  DEFAULT 1 (выключено), включать значением 0 - иначе насос включится при подаче питания.
- **Регистры Modbus Master** - авто-переменные, опрашиваются сами (`POLL_INTERVAL`); при потере связи значение не
  сбрасывается - ставь в логике пределы (суточный лимит полива и т.п.). Variable Set на такую переменную пишет в устройство.
- **MQTT** - mqtt.md: IP брокера через `linked_setting`, команды из MQTT проверяют условия безопасности, логика
  управления остаётся на контроллере (публикация без связи теряется). **Сообщение вместе с топиком - до 255 байт**:
  длинную телеметрию дели по топикам, иначе хвост пропадёт молча.
- **Строки и выражения в генерации** (generated-code.md, ноябрь 2026): Delay - только число или одна переменная;
  то, что должно пережить перезагрузку (счётчики, режимы, аварии), - в настройки STG (Variable Set пишет в EEPROM,
  только по событию); контроль связи Modbus - On Modbus Timeout / On Modbus Response с `{{$device_id}}`; действия,
  которые не должны совпасть по времени, - от одного такта с Delay, а не разными On Time Period.
- **Веб-консоль**: виджеты - в `WIDGET_GROUPS`, пароль - `linked_setting` на настройку STG (format.md §4 п. 17-18).
- **Надёжность важнее минимальной цены** (tibbo-firmware §0.1): реле с запасом по току, защищённые входы #54,
  отказобезопасное подключение датчиков, безопасное состояние выходов при старте; самый дешёвый вариант - отдельно, со списком рисков.
- После создания/обновления проекта через API попроси пользователя открыть его и прислать вкладку Problems;
  каждую новую ошибку оттуда добавляй в `check` и в эти правила.

## 4. Запись в облако — только с подтверждением
Без вопросов: GET (чтение), `code` (генерация кода ничего не меняет в аккаунте).
С явным «да» пользователя на **конкретный** вызов (покажи метод, путь, что изменится): создание/изменение/удаление
проектов и версий, запись переменных и таблиц устройств, команды устройствам, **OTA-прошивка** устройств и групп,
workflow (создаются выключенными; включение — отдельное подтверждение), workspaces (DELETE удаляет всё).
`ab_api.py create|update … --yes` — флаг ставь только после подтверждения. Сначала `ab_api.py me`: ключ бывает только с read
(тогда 403 на запись - попроси ключ с write). После `update` открытого в редакторе проекта попроси перезагрузить вкладку без сохранения.

## 5. Редактор в браузере
Только если у агента есть управление браузером (например, встроенный браузер Claude или расширение Chrome) - под входом пользователя. Сначала читай.
Run/Deploy Release, OTA, сохранение, удаление — только после подтверждения. Пароли и ключи в поля не вводи.
Устройство в Debug-режиме останавливается без связи с редактором — не оставляй его в Debug на объекте.
Карта экранов — editor.md §1–2; если интерфейс отличается, сообщи пользователю и предложи обновить скилл.
В редакторе есть свой ИИ-помощник (editor.md §10): мелкую правку открытого проекта пользователь может сделать им.
Реестр блоков устарел (новый блок «неизвестен» для `check`) - обнови его: `scripts/extract_registry.js` в браузере
на app.appblocks.io (только чтение) → `build_registry.py`; изменения покажи пользователю.

## 6. Визуализация
- **Плата**: `tps_check.py --svg` — вид как в AppBlocks. **Логика**: `ab_tool.py flow` — группы панелями, узлы
  по позициям редактора, цвет по роли (события синие, логика фиолетовые, данные зелёные, связь красные, индикация
  оранжевые), подписи портов, при наведении — аргументы. **Текстом**: цепочки из `summary`.
- Показывай SVG встроенным просмотром агента, если он есть, иначе файлом (PNG через cairosvg). Не перерисовывай вручную в другом стиле.
