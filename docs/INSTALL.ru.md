# Установка скиллов Tibbo

[English](INSTALL.md) · **Русский** · [← README](../README.ru.md)

Скиллы работают двумя способами:

- **В агенте со скиллами** (лучший вариант): Claude, Codex, Gemini CLI, Kimi Code, Deep Code (DeepSeek), OpenCode
  и другие агенты для программирования читают скиллы из папки и сами запускают скрипты проверки.
- **В веб-чате с чат-пакетом**: ChatGPT, Gemini, Kimi, DeepSeek, GLM (chat.z.ai) в браузере получают инструкцию
  и файлы знаний. ChatGPT с анализом данных тоже умеет запускать проверки, остальные чаты дают вам команды.

## Какой способ ваш

| Чем пользуетесь | Способ | Раздел |
|---|---|---|
| Claude (claude.ai, приложение для компьютера и телефона) | загрузить два zip-файла | [Приложения Claude](#приложения-claude) |
| Claude Code | плагин или папка | [Claude Code](#claude-code) |
| Codex: CLI, расширение для IDE | папка скиллов | [Codex](#codex) |
| Gemini CLI | папка скиллов | [Gemini CLI](#gemini-cli) |
| Kimi Code | папка скиллов | [Kimi Code](#kimi-code) |
| Приложение Kimi (K3, K3.1 Pro), режим Agent | скилл из документов Word | [Kimi Code](#kimi-code) |
| DeepSeek в Deep Code, OpenCode или Claude Code | папка скиллов | [DeepSeek](#deepseek) |
| GLM (Z.ai) в Z Code, Claude Code, OpenCode или Codex | папка скиллов этого агента | [GLM](#glm-zai) |
| ChatGPT, Gemini, Kimi, DeepSeek, GLM в браузере | чат-пакет | [Веб-чаты](#веб-чаты) |

Скиллы уже стоят? Как обновить их на любой платформе - в разделе [Как обновить](#как-обновить).

## Перед началом

1. **Python 3.9 или новее.** Он нужен скриптам проверки. Проверьте: `python --version` (Windows) или
   `python3 --version` (macOS, Linux). Если на Windows его нет, установите с [python.org](https://www.python.org/downloads/)
   и отметьте *Add python.exe to PATH*. Больше ничего не нужно: скрипты используют только стандартную библиотеку.
2. **Скачайте файлы** из [последнего релиза](https://github.com/SCANCODE-IOT/tibbo-ai-skills/releases/latest):
   - `tibbo-firmware.zip` и `appblocks.zip` - два скилла (ставьте всегда оба: `appblocks` проверяет плату
     скриптом из `tibbo-firmware`);
   - `tibbo-chat-pack.zip` - только для веб-чатов;
   - *Source code (zip)* - весь репозиторий с установщиком `tools/install.py`.

## Установщик для всех агентов

Распакуйте *Source code (zip)*, откройте терминал в распакованной папке и выполните:

```bash
python tools/install.py            # Windows
python3 tools/install.py           # macOS, Linux
```

Установщик копирует оба скилла в `~/.agents/skills/` - общую папку, которую читают Codex, Gemini CLI, Kimi Code,
Deep Code, Cline и Zed, - и в `~/.claude/skills/`, если стоит Claude Code. Затем запускает самопроверку
из установленной копии и пишет `самопроверка: ok`.

Другие папки: `--agent claude`, `--agent opencode`, `--agent cursor`, `--agent copilot`, `--agent gemini`
(`~/.gemini/skills`), `--agent all`. `--list` показывает папки, `--project <папка>` ставит в один проект
(`<папка>/.agents/skills`), `--uninstall` удаляет скиллы. Повторный запуск заменяет старую версию.

**Без установщика:** создайте папку `~/.agents/skills/` (на Windows - `C:\Users\<имя>\.agents\skills\`)
и распакуйте в неё `tibbo-firmware.zip` и `appblocks.zip`, чтобы получились
`~/.agents/skills/tibbo-firmware/SKILL.md` и `~/.agents/skills/appblocks/SKILL.md`.

## Приложения Claude

1. Включите выполнение кода: **Settings → Capabilities** (в тарифах Team и Enterprise скиллы включает владелец).
2. **Customize → Skills** → **+** → **Create skill** → **Upload a skill**.
3. Загрузите `tibbo-firmware.zip`, затем `appblocks.zip`. Проверьте, что оба включены.

Если меню выглядит иначе, см. [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

## Claude Code

```text
/plugin marketplace add SCANCODE-IOT/tibbo-ai-skills
/plugin install tibbo-skills@scancode
```

Обновление: `/plugin marketplace update scancode`, затем `/plugin update tibbo-skills@scancode`. Или установка в папку: `python tools/install.py --agent claude`.
**Claude API:** загрузите каждую папку скилла через [Skills API](https://platform.claude.com/docs/en/build-with-claude/skills-guide).

## Codex

Codex CLI и расширение Codex для IDE читают скиллы из `~/.agents/skills/`.

1. Запустите [установщик](#установщик-для-всех-агентов) (или распакуйте два zip в `~/.agents/skills/`).
2. Перезапустите Codex. В Codex CLI команда `/skills` показывает скиллы, `$tibbo-firmware` вызывает скилл напрямую.
3. Обычно вызывать не нужно: опишите задачу про Tibbo, и Codex сам выберет скилл по его описанию.

## Gemini CLI

Gemini CLI читает `~/.gemini/skills/` и `~/.agents/skills/`, поэтому хватит [установщика](#установщик-для-всех-агентов).
Можно и так - Gemini CLI сам скачает скиллы с GitHub:

```bash
gemini skills install https://github.com/SCANCODE-IOT/tibbo-ai-skills.git --path skills/tibbo-firmware
gemini skills install https://github.com/SCANCODE-IOT/tibbo-ai-skills.git --path skills/appblocks
```

Проверка в сессии: `/skills list`.

## Kimi Code

Kimi Code читает `~/.agents/skills/` (и `~/.kimi-code/skills/`). Запустите [установщик](#установщик-для-всех-агентов),
перезапустите Kimi Code (в приложении Kimi Code для компьютера - команда `/reload`) и задайте вопрос или наберите `/`
и выберите скилл. Если скиллы уже стоят в Claude Code или Codex, их переносит команда `/import-from-cc-codex`.

**Приложение Kimi (K3, K3.1 Pro), веб и компьютер, режим Agent.** Папку скилла туда загрузить нельзя - Kimi создаёт
скилл из офисных документов. Готовый комплект: [tibbo-skills-kimi-app.zip](kimi/tibbo-skills-kimi-app.zip) - две
папки, в каждой три документа Word и текст описания. В Kimi: режим Agent → панель Skills → «Convert Office Documents
into a Skill» → загрузите три .docx из папки → вставьте описание → «Create Skill». Скрипты проверки там не
запускаются: Kimi даст команды для проверки у себя.

Подробная инструкция для Kimi в Word: [tibbo-skills-kimi-guide.ru.docx](kimi/tibbo-skills-kimi-guide.ru.docx).

## DeepSeek

- **Deep Code** - терминальный агент для моделей DeepSeek (`npm install -g @vegamo/deepcode-cli`), читает
  `~/.agents/skills/`: запустите [установщик](#установщик-для-всех-агентов) и перезапустите агента. `/` открывает выбор скиллов.
- **OpenCode** или **Claude Code** с ключом DeepSeek API: ставьте в папку этого агента (`--agent opencode` или `--agent claude`).

## GLM (Z.ai)

Модели GLM работают по тарифу GLM Coding Plan в Z Code, Claude Code, OpenCode, Codex, Cline и других агентах.
Ставьте скиллы в того агента, которым пользуетесь: Claude Code или Z Code - `--agent claude`; OpenCode -
`--agent opencode`; Codex или Cline - папка по умолчанию `~/.agents/skills/`.

## Другие агенты

Большинство агентов с поддержкой Agent Skills читают `.agents/skills/` в папке проекта (`--project <папка>`).
[Vercel skills CLI](https://github.com/vercel-labs/skills) ставит скиллы в 80+ агентов (нужен Node.js 22.20+):
`npx skills add SCANCODE-IOT/tibbo-ai-skills -g`.

## Веб-чаты

Распакуйте `tibbo-chat-pack.zip`. Внутри: `PROMPT.md` (инструкция), семь файлов знаний `01`-`07`,
`tibbo-tools.zip` (скрипты) и короткий `README.md`.

- **ChatGPT, свой GPT** (платные тарифы): Обзор GPT → Создать → Настроить. Текст `PROMPT.md` - в поле «Инструкции»,
  `01`-`07` и `tibbo-tools.zip` - в «Знания», включите «Интерпретатор кода и анализ данных». GPT сам запускает проверки.
- **ChatGPT, Проект:** создайте проект, вставьте `PROMPT.md` в инструкции проекта, добавьте файлы.
- **Gemini, Gem:** Gems → Новый Gem. `PROMPT.md` - в «Инструкции», `01`-`07` - в «Знания» (до 10 файлов).
- **Kimi (kimi.com), DeepSeek (chat.deepseek.com), GLM (chat.z.ai):** в новом чате приложите `PROMPT.md` и 1-3 файла
  под задачу, напишите «Следуй PROMPT.md». В каждом новом чате - заново.

| Задача | Файлы |
|---|---|
| Подобрать Tibbit, проверить сокеты и питание | 01, 05 |
| Написать или проверить прошивку на Tibbo BASIC | 01, 04, 06 (+ 05 для платформы) |
| Библиотеки: DHCP, MQTT, Modbus, Wi-Fi, TLS | 06, 04 |
| Проект AppBlocks | 02, 03 (+ 01 для железа) |

Чат, который не запускает код, выдаёт файлы и команды. Выполните их у себя: распакуйте `tibbo-tools.zip`
и в этой папке запустите

```bash
python tibbo-firmware/scripts/tps_check.py check cfg.json --svg board.svg
python tibbo-firmware/scripts/tibbo_lint.py my_project --platform "TPP3W(G2)"
python appblocks/scripts/ab_tool.py check project.json
```

`[ОШИБКА]` в выводе - это ошибка. Отправьте вывод обратно в чат.

## Как обновить

**Как узнать о новой версии.** На странице репозитория нажмите **Watch → Custom → Releases** - GitHub пришлёт письмо
о каждом релизе. Или спросите агента «какая версия скиллов Tibbo и есть ли новее?». Номер установленной версии
записан в начале файла `SKILL.md` (строка `version:`).

Обновляются всегда **оба** скилла сразу.

| Где стоят скиллы | Как обновить |
|---|---|
| **Codex, Gemini CLI, Kimi Code, Deep Code, OpenCode, Cursor, Copilot, Cline** (папка скиллов) | Скажите агенту: **«Обнови скиллы Tibbo»**. Он запустит скрипт обновления из самого скилла. Или сами: `python tools/install.py --update` из распакованного репозитория - обновит скиллы во всех агентах, где они стоят. Затем перезапустите агента. |
| **Claude Code, плагин** | `/plugin marketplace update scancode`, затем `/plugin update tibbo-skills@scancode`, перезапустите Claude Code. |
| **Claude Code, папка** `~/.claude/skills` | Как для других агентов: «Обнови скиллы Tibbo» или `python tools/install.py --update`. |
| **Приложения Claude** (claude.ai, компьютер, телефон) | Скачайте новые `tibbo-firmware.zip` и `appblocks.zip` из релиза. **Customize → Skills**: удалите старые версии скиллов и загрузите новые zip. |
| **Gemini CLI**, если ставили через `gemini skills install` | Повторите обе команды `gemini skills install …` из раздела [Gemini CLI](#gemini-cli), затем `/skills reload`. |
| **Kimi Code**, если переносили через `/import-from-cc-codex` | Обновите скиллы в Claude Code или Codex и снова выполните `/import-from-cc-codex`. |
| **Приложение Kimi** (K3, K3.1 Pro) | Скачайте новый [комплект для Kimi](kimi/tibbo-skills-kimi-app.zip). Skills → вкладка **Custom Skills**: у каждого скилла замените документы на новые (или удалите скилл и создайте заново по инструкции). |
| **ChatGPT, свой GPT или Проект** | Скачайте новый `tibbo-chat-pack.zip`. В настройках GPT (или проекта) замените текст инструкций на новый `PROMPT.md`, удалите старые файлы знаний и загрузите новые `01`-`07` и `tibbo-tools.zip`. |
| **Gemini, Gem** | То же: новый `PROMPT.md` в «Инструкции», новые файлы `01`-`07` вместо старых в «Знаниях». |
| **Чаты Kimi, DeepSeek, GLM** | Просто прикладывайте файлы из нового `tibbo-chat-pack.zip` - в каждом новом чате они и так прикладываются заново. |

**Нет доступа к GitHub из терминала?** Скачайте `tibbo-firmware.zip` и `appblocks.zip` из релиза в браузере, положите
в одну папку и запустите `python <папка скиллов>/tibbo-firmware/scripts/skills_update.py --from <эта папка>`.
Скрипт обновления сам откатывает изменения, если архив повреждён, и проверяет новую версию после установки.

## Проверьте, что работает

Спросите: *«TPP3W(G2): источник питания #10 в S1 с разъёмом #18 в S2, в шкафу 24 В. Всё правильно?»*
Рабочий скилл пишет допущения, запускает `tps_check.py` (или даёт команду) и отвечает, что #10 принимает
только 9-18 В, а для 24 В нужен #25 или #33. Если этих шагов нет, скилл не загрузился: перезапустите агента
и проверьте папку.

## Насколько хорошо справляются разные модели

Скиллы дают правила и данные, но качество всё равно зависит от модели. Сильные модели проходят процедуру сами.
Небольшие и быстрые чаще пропускают шаги: требуйте проверки (`tps_check.py`, `tibbo_lint.py`, `ab_tool.py check`)
и собирайте каждую прошивку в TIDE, прежде чем загружать в устройство.

## Если что-то не так

- **`python` не найден.** Windows: переустановите Python с *Add to PATH* или пишите `py` вместо `python`.
- **Агент не видит скилл.** Перезапустите его и проверьте, что `SKILL.md` лежит на один уровень глубже папки скиллов:
  `.../skills/tibbo-firmware/SKILL.md`, а не `.../skills/tibbo-firmware/tibbo-firmware/SKILL.md`.
- **Кракозябры вместо русского** в старой консоли Windows: `chcp 65001` или Windows Terminal.
- **`CERTIFICATE_VERIFY_FAILED` в `ab_api.py`** на Windows: `pip install truststore`; `python scripts/ab_api.py tls`
  покажет, какое хранилище сертификатов используется. Проверку сертификатов не отключаем.
- **Обновление:** см. раздел [Как обновить](#как-обновить) - таблица для каждой платформы.
