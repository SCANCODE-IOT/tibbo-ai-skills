# appblocks

[English](README.md) · **Русский** · [← Все скиллы](../../README.ru.md)

Скилл для ИИ-агентов (Claude, Codex, Gemini CLI, Kimi Code, Deep Code и других) - **[Tibbo AppBlocks](https://appblocks.io)** - визуального конструктора прошивок для устройств Tibbo
и Zephyr и его облака. Агент читает, объясняет, проверяет, правит и создаёт проекты AppBlocks, рисует их логику
и железо, работает с AppBlocks Cloud API.

<img src="../../docs/images/appblocks-flow.svg" alt="Схема логики AppBlocks" width="900" />

> Ставьте вместе с [tibbo-firmware](../tibbo-firmware/README.ru.md): через него идут проверка железа и ревью сгенерированного кода Tibbo BASIC.

## Что умеет

| Задача | Как скилл её решает |
|---|---|
| **Объяснить проект** | `ab_tool.py summary` - плата, Tibbit, сервисы, переменные, таблицы и цепочки событий, затем описание человеческим языком: что делает устройство. |
| **Проверить логику** | Применяет правила потоков AppBlocks: поток должен начинаться с события, параметры видны только следующему блоку, ASYNC-блоки теряют параметры, рекурсия `On Variable Changed`, циклы через команды без выхода, необработанные `modbus_timeout` / `tbl_record_not_found`, пароли открытым текстом, выключенные сервисы, которые нужны узлам. |
| **Проверить железо** | Переводит Tibbit проекта в конфигурацию TPS (`ab_tool.py tps`) и запускает `tps_check.py` из `tibbo-firmware`: сокеты, линии, бюджет питания, картинка платы. |
| **Править и создавать** | Правит *копию* экспорта скриптом, а не вручную; сохраняет ID переиспользуемых элементов, а ненужные удаляет вместе со всеми ссылками (включая дашборды, LUIS, меню LCD); новые ID - из `ab_tool.py ids`; перед выдачей файла для **Import** `check` должен показать 0 ошибок. |
| **Работать с облаком** | Список проектов и устройств, загрузка проектов, генерация кода прошивки, версии и рабочие пространства. Любая запись - создание и изменение проектов, переменные устройств, команды, **OTA**, workflow - только после вашего явного «да» на конкретный вызов. |
| **Работать в редакторе** | В вашем браузере, под вашим входом, сначала только чтение; Run, Deploy, OTA, сохранение и удаление - после подтверждения. |

Поддерживаемые runtime: **`tios`** (Tibbo BASIC для TPP2, TPP3, DS1101, DS1102, EM510), **`zephyr`** (Zephyr C), `micropython`.

## Состав

| Путь | Что внутри |
|---|---|
| `SKILL.md` | Инструкции для агента: откуда взять проект, ревью, правка, правила записи в облако, браузер, визуализация. |
| `references/editor.md` | Устройство редактора (Hardware / Features / Application), Import/Export, Run/Debug/Release, runtime, **правила потоков**, переменные, плагины, частые ошибки. |
| `references/format.md` | Формат экспорта JSON: верхний уровень, группы feature, узлы, связи, ссылки `{{$…}}`, правила правки, формат плагинов (`custom_feature`). |
| `references/blocks.md` | **Все 177 блоков редактора** по категориям палитры: порты с параметрами, настройки с допустимыми значениями и значениями по умолчанию, нужная feature, ASYNC; скрытые и устаревшие блоки отдельно. Снято из реестра app.appblocks.io. |
| `references/features.md` | Feature, сервисы-библиотеки, вложенные элементы, поля `tibbit_NN`, периферия, виджеты LCD и веб-консоли. |
| `references/catalog.md` | Поля feature и узлов в экспортах Tibbo с примерами значений, поля Tibbit, структуры Modbus и LUIS. |
| `references/catalog-examples.md` | Как блоки и Tibbit используются в **78 проектах appblocks.io** (59 типов узлов, 28 Tibbit): типичные связки, аргументы, сокеты. |
| `references/generated-code.md` | Что генерирует AppBlocks для `tios`: файлы проекта TIDE, процедуры `var_X_*`, маркеры вставки кода. |
| `references/mqtt.md` | MQTT: feature `mqtt` и блоки, IP брокера как настройка устройства, поведение библиотеки (без связи публикации теряются, переподключение), свой брокер Mosquitto, приёмник на компьютере. |
| `references/api.md` | AppBlocks Cloud API: авторизация, проекты (код, сборка, версии, OTA, бандлы), устройства, группы, рабочие пространства, workflow, дашборды. |
| `scripts/ab_tool.py` | Офлайн-инструмент для проектов (см. ниже). |
| `data/registry.json` | Реестр редактора в компактном виде; обновление - `scripts/extract_registry.js` (в браузере на app.appblocks.io, только чтение) и `scripts/build_registry.py`. |
| `scripts/ab_api.py` | Клиент облачного API (см. ниже). |
| `examples/` | 6 проектов Tibbo: Modbus-шлюз с LCD на 4×RS485 и шлюз Modbus→MQTT (Zephyr), полив, контроль доступа, гидропоника (TPP3), контроль уровня воды с облаком; а также `greenhouse2_tpp3.json` (TOTAL SMART SCHOOL GREENHOUSE 2: полив «цикл и замачивание» с блокировками, контроль связи Modbus и тока насосов, настройки в EEPROM, веб-панель устройства с кнопками; 0 ошибок в редакторе, компилируется в TIDE), `greenhouse2_logger.py` (MQTT → SQLite → графики на компьютере; нужны paho-mqtt и matplotlib) и `greenhouse2_instruction.md` (инструкция для пользователей: пусконаладка, насосы, бак, тревоги). |
| `tests/run.sh` | Офлайн-тесты на примерах, включая связку с `tps_check.py`. |

## Инструменты

Оба скрипта используют только стандартную библиотеку Python.

### `ab_tool.py` - офлайн, аккаунт не нужен

```bash
python3 scripts/ab_tool.py summary project.json              # что есть в проекте
python3 scripts/ab_tool.py check   project.json              # связи, ссылки, ID, сокеты + порты, значения настроек, feature по реестру редактора, ловушки компиляции, размер MQTT-сообщений, Delay с выражением, веб-консоль (код 1 при ошибках)
python3 scripts/ab_tool.py lookup  node_table                # порты и настройки блока / feature из реестра
python3 scripts/ab_tool.py flow    project.json flow.svg     # схема логики
python3 scripts/ab_tool.py tps     project.json --vin 24 --out cfg.json   # железо → конфигурация tps_check.py
python3 scripts/ab_tool.py nodes   project.json              # использованные типы узлов и порты
python3 scripts/ab_tool.py ids     5                         # новые ID в стиле AppBlocks
```

Полная проверка железа с картинкой платы:

```bash
python3 scripts/ab_tool.py tps project.json --vin 24 --out cfg.json
python3 ../tibbo-firmware/scripts/tps_check.py check cfg.json --svg board.svg
```

Напряжение питания в проекте AppBlocks не хранится, передайте его через `--vin`. Если вы его не укажете,
он примет 24 В и напишет об этом в ответе.

### `ab_api.py` - AppBlocks Cloud

```bash
export APPBLOCKS_API_KEY=abk_...        # Settings → API Keys в веб-приложении AppBlocks
python3 scripts/ab_api.py me                           # аккаунт и права ключа
python3 scripts/ab_api.py projects                     # список проектов
python3 scripts/ab_api.py project <id> --out p.json    # скачать проект
python3 scripts/ab_api.py code p.json --outdir gen     # сгенерированные исходники прошивки
python3 scripts/ab_api.py build p.json --out fw         # компиляция компилятором TIDE у Tibbo (ключ не нужен)
python3 scripts/ab_api.py devices                      # устройства, связь, прошивка
python3 scripts/ab_api.py example sprinkler5 --out p.json
```

| Группа команд | Команды | Меняет ваш аккаунт? |
|---|---|---|
| Чтение | `me`, `projects`, `project`, `versions`, `examples`, `example`, `workspaces`, `devices`, `device`, `get` | Нет |
| Генерация | `code`, `build` | Нет - проект только отправляется в генератор кода и компилятор |
| Запись | `create … --yes`, `update … --yes` | **Да** - агент каждый раз спрашивает разрешения |

Безопасность:

- Ключ берётся **только** из `APPBLOCKS_API_KEY` или файла, указанного в `APPBLOCKS_API_KEY_FILE`, но не из командной строки. Агент не выводит его и не сохраняет в файлы, память или артефакты; MQTT-ключ устройства (`key`) тоже скрывается.
- В облачной песочнице (например, claude.ai) сеть может быть закрыта по умолчанию: добавьте `api.appblocks.io` и `appblocks.io` в разрешённые домены в **Settings → Capabilities** (в Team/Enterprise - через администратора). Без этого работайте с экспортированным `.json`.

## Примеры запросов

```text
Вот экспорт моего проекта AppBlocks. Что делает это устройство? Нарисуй логику и плату.
```

```text
Проверь проект на ошибки, прежде чем я разверну его на 30 контроллерах.
```

```text
Возьми пример sprinkler5 и сделай 6 зон, у каждой своя таблица расписания.
```

```text
Покажи мои устройства AppBlocks, которые не в сети, и какая на них версия прошивки.
```

## Ограничения

- Формат JSON и каталог узлов восстановлены по экспортированным проектам (октябрь 2026). Нового типа узла может не быть; тогда агент берёт структуру с похожего узла в ваших проектах и просит проверить вкладку **Problems** в редакторе.
- Успешный `ab_api.py code` не гарантирует, что список Problems в редакторе пуст: скилл просит открыть проект и прислать новые ошибки, а потом добавляет их в `check`.
- Устройство в режиме **Debug** останавливается без связи с редактором - скилл предупреждает не оставлять его так на объекте.

## Тесты

```bash
sh tests/run.sh
```

`check`, `summary`, `flow` и `tps` на каждом примере, уникальность ID, регрессии для ссылок из дашбордов
и интервала обновления, связка с `tps_check.py`, если `tibbo-firmware` лежит рядом.
