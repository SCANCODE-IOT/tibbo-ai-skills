<div align="center">

# Скиллы Tibbo для ИИ-агентов

**Навыки, которые превращают вашу нейросеть в инженера по прошивкам Tibbo и проектам AppBlocks.**

Писать и проверять прошивки на Tibbo BASIC, подбирать Tibbit и считать бюджет питания TPS,
разбирать, исправлять и создавать проекты AppBlocks - на точных данных Tibbo API, а не по догадкам.

Claude · ChatGPT / Codex · Gemini · Kimi · DeepSeek · GLM

[![Tests](https://github.com/scancode-iot/tibbo-ai-skills/actions/workflows/tests.yml/badge.svg)](https://github.com/scancode-iot/tibbo-ai-skills/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-2-6f42c1)](#скиллы)
[![Python](https://img.shields.io/badge/python-3.9%2B%20·%20stdlib%20only-3776ab)](#требования)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-open%20standard-2ea44f)](https://agentskills.io)

[English](README.md) · **Русский**

</div>

---

## Зачем это нужно

Устройства Tibbo работают на TiOS - событийной ОС со своим диалектом BASIC, статической памятью, «курсорами» каналов
(`sock.num`, `ser.num`) и более чем 60 библиотеками, которые молча не работают, если не реализованы все колбэки
и не проброшены хуки `*_proc_*`. У подбора Tibbit свои ловушки: формы сокетов, линии UART и прерываний,
вход 9–18 В у части источников питания, шина ±15 В.

Универсальные модели знают об этом мало и выдумывают имена API. Скиллы дают модели точные справочные данные,
правила работы и офлайн-инструменты проверки, поэтому её ответы можно проверить, а не принимать на веру.
Скиллы сделаны в открытом формате [Agent Skills](https://agentskills.io): одни и те же папки работают в Claude,
Codex, Gemini CLI, Kimi Code, Deep Code и других агентах, а для веб-чатов есть чат-пакет.

> Скиллы протестированы инженерами Tibbo Technology на Тайване.

## Скиллы

| Скилл | Что умеет ваша нейросеть с ним |
|---|---|
| [**tibbo-firmware**](skills/tibbo-firmware/README.ru.md) | Писать, проверять и отлаживать прошивки на Tibbo BASIC / Tibbo C для TiOS (TPP2/TPP3, DS, EM, WM, WS); начинать проект с генератора или с одной из 20 готовых программ (`tibbo_new.py`, `recipes/`); проверять код по точному API вашей платформы (`tibbo_lint.py`) и **собирать его компилятором самой Tibbo** (`tibbo_build.py`); находить устройства в сети и загружать прошивку, не открывая TIDE (`tibbo_device.py`, экспериментально); подбирать Tibbit под задачу, раскладывать их по сокетам TPS и проверять линии, UART/INT, разъёмы, PoE и бюджет питания +5 В; рисовать плату и диаграммы состояний прошивки. Linux-платы LTPP3(G2): Tibbit, питание, слоты и первые шаги. |
| [**appblocks**](skills/appblocks/README.ru.md) | Объяснять, проверять, править и создавать проекты [AppBlocks](https://appblocks.io) (экспорт JSON); рисовать схему логики; проверять железо через `tibbo-firmware`; начинать с одного из 6 готовых проектов для TiOS; компилировать сгенерированную прошивку компилятором TIDE у Tibbo; настраивать MQTT со своим брокером; работать с AppBlocks Cloud API (проекты, устройства, OTA, workflow) с подтверждением перед любой записью. |

Скиллы работают в паре: железо проекта AppBlocks проверяется скриптом TPS из `tibbo-firmware`,
а прошивку, которую AppBlocks генерирует для TiOS, проверяют по чек-листу `tibbo-firmware`.

```mermaid
flowchart LR
    U([Ваш запрос]) --> C{Ваш ИИ-агент}
    C -->|прошивка, Tibbit, питание| F[tibbo-firmware]
    C -->|проект или облако AppBlocks| A[appblocks]
    A -->|железо проекта| T[tps_check.py]
    F --> T
    F --> G[tibbo_new.py + 20 рецептов:<br/>проект, который собирается]
    G --> N[tibbo_lint.py: точное API платформы]
    N --> B[tibbo_build.py: компилятор Tibbo]
    B --> D[tibbo_device.py: загрузка, запуск]
    F --> R[(TiOS API · 46 платформ<br/>библиотеки · 84 Tibbit)]
    A --> K[(177 блоков редактора · 78 проектов<br/>справочник Cloud API)]
    T --> S[SVG платы + бюджет питания]
    A --> L[SVG схемы логики]
```

## Как это выглядит

<table>
<tr>
<td width="50%" valign="top">

**Проверка платы TPS** - сокеты, Tibbit, линии `PL_IO_NUM_*`, `ser.num`, бюджет +5 В в стиле конфигуратора Tibbo.

<img src="docs/images/tps-board-tpp3.svg" alt="Плата TPP3 с Tibbit и бюджетом питания" />

</td>
<td width="50%" valign="top">

**Ошибки пронумерованы прямо на плате** - неверный сокет, 24 В на источник 9–18 В, нет разъёма.

<img src="docs/images/tps-board-error.svg" alt="Конфигурация TPS с пронумерованными ошибками" />

</td>
</tr>
<tr>
<td colspan="2">

**Схема логики AppBlocks** - группы, узлы на своих местах в редакторе, цвет по роли, подписи портов на связях.

<img src="docs/images/appblocks-flow.svg" alt="Схема логики проекта AppBlocks" />

</td>
</tr>
<tr>
<td colspan="2">

**Конечный автомат прошивки** - состояния, выходы, переходы и аварийные пути, взятые из кода.

<img src="docs/images/state-diagram.svg" alt="Диаграмма состояний прошивки" />

</td>
</tr>
</table>

## С какими нейросетями работает

| Нейросеть | Как подключить | Сама запускает проверки |
|---|---|---|
| **Claude** - приложения, Claude Code, API | скиллы (загрузка zip, плагин, папка) | да |
| **ChatGPT / Codex** - Codex CLI, расширение Codex для IDE | папка скиллов `~/.agents/skills` | да |
| **Gemini** - Gemini CLI | папка скиллов | да |
| **Kimi** - Kimi Code | папка скиллов | да |
| **Приложение Kimi (K3, K3.1 Pro)** - на компьютере и kimi.com, режим Agent | скилл из документов Word: [комплект для Kimi](docs/kimi/tibbo-skills-kimi-app.zip) | даёт вам команды |
| **DeepSeek** - Deep Code, OpenCode, Claude Code | папка скиллов | да |
| **GLM (Z.ai)** - Z Code, Claude Code, OpenCode, Codex | папка скиллов агента | да |
| **Веб-чаты** - ChatGPT, Gemini, Kimi, DeepSeek, GLM | чат-пакет | ChatGPT с анализом данных - да; остальные дают вам команды |

Качество всё равно зависит от модели: небольшие модели чаще пропускают шаги, поэтому их работу проверяют скрипты.

## Установка

Скачайте файлы из [последнего релиза](https://github.com/SCANCODE-IOT/tibbo-ai-skills/releases/latest).
Ставьте **оба** скилла: `appblocks` проверяет плату скриптом из `tibbo-firmware`.
**Пошаговая инструкция для каждой нейросети: [docs/INSTALL.ru.md](docs/INSTALL.ru.md).**

| Чем пользуетесь | Быстрый старт |
|---|---|
| Приложения Claude | Customize → Skills → + → Upload a skill: `tibbo-firmware.zip`, затем `appblocks.zip` |
| Claude Code | `/plugin marketplace add SCANCODE-IOT/tibbo-ai-skills`, затем `/plugin install tibbo-skills@scancode` |
| Codex, Gemini CLI, Kimi Code, Deep Code и другие агенты | распакуйте *Source code (zip)* и запустите `python tools/install.py` |
| Приложение Kimi (K3, K3.1 Pro) | [tibbo-skills-kimi-app.zip](docs/kimi/tibbo-skills-kimi-app.zip): режим Agent → Skills → «Convert Office Documents into a Skill» ([инструкция в Word](docs/kimi/tibbo-skills-kimi-guide.ru.docx)) |
| ChatGPT, Gemini, Kimi, DeepSeek, GLM в браузере | `tibbo-chat-pack.zip`: инструкция + файлы знаний + скрипты |

Установщик кладёт оба скилла в `~/.agents/skills/` (её читают Codex, Gemini CLI, Kimi Code, Deep Code, Cline, Zed)
и в `~/.claude/skills/`, если стоит Claude Code, затем запускает самопроверку. Есть ключи
`--agent opencode|cursor|copilot|all`, `--project <папка>` и `--uninstall`.

### Как обновить

Скажите агенту **«Обнови скиллы Tibbo»** - он запустит скрипт обновления, который входит в скилл
(`skills/tibbo-firmware/scripts/skills_update.py`, ключ `--check` показывает установленную и последнюю версию).
Или запустите `python tools/install.py --update` из распакованного репозитория: он обновит скиллы во всех агентах,
где они стоят. Плагин Claude Code: `/plugin marketplace update scancode`, затем `/plugin update tibbo-skills@scancode`.
Приложения Claude, приложение Kimi и веб-чаты: замените файлы на новые.
**Пошагово для каждой платформы: [docs/INSTALL.ru.md → Как обновить](docs/INSTALL.ru.md#как-обновить).**
Чтобы узнавать о новых версиях: **Watch → Custom → Releases** на этой странице.

## Примеры запросов

Просто опишите задачу - агент сам выберет скилл.

```text
Нужен контроллер на TPP3: опрашивает 4 счётчика по Modbus RTU через RS485 и отправляет
данные в MQTT по Wi-Fi. Питание 24 В в шкафу, до 50 °C. Подбери Tibbit и проверь питание.
```

```text
Проверь проект на Tibbo BASIC для TPP2W(G3): main.tbs, device.tbs, global.tbh (во вложении).
Особое внимание - работе с сокетами и DHCP.
```

```text
Вот экспорт проекта AppBlocks (во вложении). Объясни, что делает устройство,
нарисуй логику и плату, перечисли проблемы.
```

```text
Добавь в этот проект AppBlocks переменную «наработка насоса» и обнуляй её каждый день в полночь.
```

Что помогает получить точный ответ:

- **Точное имя платформы** - `TPP3W(G2)`, `TPP2W(G3)`, `DS1102W`, `EM2000W`.
- **Какие Tibbit в каких сокетах** и **от чего питание** (12/24/48 В через какой Tibbit, PoE).
- Для кода с библиотеками - `src_lib_ver` из `.tpr`.

Агент проверяет код по справочным данным и - там, где может запускать скрипты, - собирает его компилятором самой
Tibbo: версией на Node.js (нужны Node.js 18+ и git; ставится один раз с вашего согласия, код не покидает компьютер),
вашей TIDE, если она установлена, или - только с вашего согласия - облачным сборщиком Tibbo. Он пишет, что проверено,
а что нет; в веб-чате ничего не собирается, и ответ прямо об этом говорит. Сборка без ошибок - ещё не проверка:
всегда пробуйте прошивку на реальном устройстве. Что доступно агенту в вашем случае: [docs/INSTALL.ru.md](docs/INSTALL.ru.md#сборка-и-загрузка-прошивки).

## Измерено

В репозитории есть [14 контрольных задач с автоматической проверкой](evals/RESULTS.md): результат собирается
компилятором Tibbo и проверяется инструментами скиллов. Первый прогон, 10 ноября 2026:

| | Задач решено | Проверок пройдено |
|---|---|---|
| Claude Sonnet 5.5 со скиллами | 14 из 14 | 64 из 64 |
| Claude Haiku 5.5 (маленькая модель) со скиллами | 14 из 14 | 64 из 64 |
| Claude Sonnet 5.5 без скиллов | 4 из 14 | 39 из 64 |

Без скиллов не собрался ни один проект прошивки. Проверки узкие («собирается и содержит нужное», а не «работает на
устройстве»), другие агенты пока не прогонялись: это одна команда, см. `evals/README.md`.

## Структура репозитория

```text
tibbo-ai-skills/
├── skills/
│   ├── tibbo-firmware/        # SKILL.md, references/, data/, scripts/, tests/
│   └── appblocks/             # SKILL.md, references/, scripts/, examples/, tests/
├── evals/                     # контрольные задачи с автоматической проверкой, результаты первого прогона
├── chat-pack/                 # PROMPT.md и README для веб-чатов (файлы знаний собираются из скиллов)
├── .claude-plugin/
│   └── marketplace.json       # каталог плагинов Claude Code
├── docs/                      # INSTALL.md / INSTALL.ru.md, картинки (нарисованы скриптами самих скиллов)
├── tools/install.py           # ставит оба скилла в Codex, Gemini CLI, Kimi Code, Claude Code и другие агенты
├── tools/package.sh           # собирает dist/*.zip: два скилла + tibbo-chat-pack.zip (tools/build_chat_pack.py)
├── tools/recipes_src/         # исходники рецептов прошивок (tools/build_recipes.py, tools/check_recipes.py)
└── .github/workflows/         # тесты при каждом коммите, пакеты релиза по тегам
```

## Требования

Скриптам нужен **только Python 3.9+** - используется лишь стандартная библиотека. Для сборки компилятором Tibbo и
работы с устройствами дополнительно нужны **Node.js 18+ и git** (или TIDE на Windows) - см.
[Сборка и загрузка прошивки](docs/INSTALL.ru.md#сборка-и-загрузка-прошивки)
(по желанию `truststore` или `certifi` для `ab_api.py` на Windows, см. [docs/INSTALL.ru.md](docs/INSTALL.ru.md#если-что-то-не-так)).
Агент запускает их сам, но их можно запускать и самостоятельно:

```bash
cd skills/tibbo-firmware
python3 scripts/tps_check.py find "rs485 modbus"
python3 scripts/tps_check.py check tests/gallery_tpp3.json --svg board.svg
python3 scripts/tibbo_lint.py tests/lint/bad.tbs --platform "TPP3W(G2)"
python3 scripts/tibbo_new.py my_app --platform "TPP3W(G2)" --libs dhcp,settings   # проект, который собирается
python3 scripts/tibbo_build.py --doctor            # какой способ сборки работает на этом компьютере
python3 scripts/tibbo_build.py my_app              # сборка компилятором Tibbo
```

Клиент AppBlocks Cloud API берёт ключ только из переменной окружения `APPBLOCKS_API_KEY`.
Если агент работает в облачной песочнице со списком разрешённых сайтов (например, claude.ai, **Settings → Capabilities**),
сначала добавьте туда `api.appblocks.io` и `appblocks.io`.

## Тесты

```bash
sh skills/tibbo-firmware/tests/run.sh
sh skills/appblocks/tests/run.sh
```

Оба набора работают без сети и запускаются при каждом коммите вместе с проверкой установщика, валидатором
Agent Skills и лимитами чат-пакета; отдельное задание ставит компилятор Tibbo и собирает все рецепты на Tibbo BASIC на их платформах (см. [Actions](https://github.com/scancode-iot/tibbo-ai-skills/actions)).

## Источники данных

Справочники собраны в октябре-ноябре 2026 года из:

- [github.com/tibbotech](https://github.com/tibbotech) - API TiOS, платформы, библиотеки, каталог Tibbit, примеры (извлечены автоматически, имена и сигнатуры точные); API по платформам снято с самого компилятора Tibbo;
- [docs.tibbo.com](https://docs.tibbo.com) - питание, сокеты и тайлы, PoE (выписаны вручную);
- [appblocks.io](https://appblocks.io) - проекты-примеры и каталог узлов редактора.

Tibbo периодически выпускает новые библиотеки и Tibbit. Если что-то устарело,
[создайте issue](https://github.com/scancode-iot/tibbo-ai-skills/issues).

## Участие

Самое ценное - сообщения об ошибках с реальным проектом или реальной ошибкой редактора.
См. [CONTRIBUTING.md](CONTRIBUTING.md).

## Лицензия

Код и инструкции скиллов: [MIT](LICENSE) © 2026 Scancode.
Справочные данные и проекты-примеры, полученные из материалов Tibbo Technology, остаются собственностью
правообладателей - см. [NOTICE](NOTICE).

Tibbo, Tibbit, TiOS, TIDE и AppBlocks - товарные знаки Tibbo Technology Inc. Проект не является официальным
продуктом Tibbo. Claude - продукт Anthropic; ChatGPT и Codex - OpenAI; Gemini - Google; Kimi - Moonshot AI;
DeepSeek - DeepSeek; GLM и Z.ai - Zhipu AI.

<div align="center">

Сделано **[Сканкод (Scancode)](https://github.com/scancode-iot)** - дистрибьютором Tibbo Technology в России и СНГ.

</div>
