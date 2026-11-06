# Tibbo chat pack - for web chats without skills

**English** · [Русский](#русский)

Use this pack in web chats that cannot install skills: ChatGPT (custom GPT or Project), Gemini (Gem),
Kimi, DeepSeek, GLM (chat.z.ai). If you use a coding agent (Codex, Claude, Gemini CLI, Kimi Code, Deep Code,
OpenCode), install the skills instead - they are more capable (see the main README).

| File | What it is |
|---|---|
| `PROMPT.md` | Instructions for the chat. Paste into the instructions field, or send as the first message. |
| `01`-`07` `.md` | Knowledge files. Upload all where possible, or only those your task needs (table below). |
| `tibbo-tools.zip` | Checking scripts. Upload to ChatGPT with code interpreter, or run on your computer (Python 3.9+). |
| `README.md` | This file. Do not upload. |

**ChatGPT, custom GPT:** Explore GPTs → Create → Configure. Paste `PROMPT.md` into Instructions, upload `01`-`07` and
`tibbo-tools.zip` to Knowledge, turn on Code Interpreter & Data Analysis. The GPT can then run the checks itself.
**ChatGPT, Project:** create a project, paste `PROMPT.md` into the project instructions, add the files to the project.
**Gemini, Gem:** Gems → New Gem. Paste `PROMPT.md` into Instructions, add `01`-`07` to Knowledge (the limit is 10 files).
A Gem cannot run the scripts: it gives you the files and commands to check them on your computer.
**Kimi, DeepSeek, GLM (chat.z.ai):** start a new chat, attach `PROMPT.md` and the 1-3 files your task needs, and write
"Follow PROMPT.md". Attach the files again in every new chat.

| Task | Files |
|---|---|
| Choose Tibbits, check sockets and power | 01, 05 |
| Write or review Tibbo BASIC firmware | 01, 04, 06 (+ 05 for the platform) |
| Libraries: DHCP, MQTT, Modbus, Wi-Fi, TLS | 06, 04 |
| AppBlocks project: explain, review, edit | 02, 03 (+ 01 for hardware) |
| Where to read more | 07 |

Check the result on your computer (unzip `tibbo-tools.zip`, then in that folder; on Windows `python`, on macOS/Linux `python3`):
```
python tibbo-firmware/scripts/tps_check.py check cfg.json --svg board.svg
python tibbo-firmware/scripts/tibbo_lint.py my_project --platform "TPP3W(G2)"
python appblocks/scripts/ab_tool.py check project.json
```
`[ОШИБКА]` in the output means an error. Smaller models make more mistakes: always run the checks and build in TIDE.

---

## Русский

Пакет для веб-чатов, где скиллы установить нельзя: ChatGPT (свой GPT или Проект), Gemini (Gem), Kimi, DeepSeek,
GLM (chat.z.ai). Если вы пользуетесь агентом для программирования (Codex, Claude, Gemini CLI, Kimi Code, Deep Code,
OpenCode), лучше установите скиллы: они умеют больше (см. главный README).

| Файл | Что это |
|---|---|
| `PROMPT.md` | Инструкция для чата. Вставьте в поле инструкций или отправьте первым сообщением. |
| `01`-`07` `.md` | Файлы знаний. Загрузите все, если можно, или только нужные для задачи (таблица ниже). |
| `tibbo-tools.zip` | Скрипты проверки. Загрузите в ChatGPT с анализом данных или запустите у себя (Python 3.9+). |
| `README.md` | Этот файл. Загружать не нужно. |

**ChatGPT, свой GPT:** Обзор GPT → Создать → Настроить. `PROMPT.md` - в поле «Инструкции», `01`-`07` и
`tibbo-tools.zip` - в «Знания», включите «Интерпретатор кода и анализ данных». Тогда GPT сам запускает проверки.
**ChatGPT, Проект:** создайте проект, вставьте `PROMPT.md` в инструкции проекта, добавьте файлы в проект.
**Gemini, Gem:** Gems → Новый Gem. `PROMPT.md` - в «Инструкции», `01`-`07` - в «Знания» (лимит - 10 файлов).
Gem не запускает скрипты: он отдаёт файлы и команды, чтобы вы проверили их у себя.
**Kimi, DeepSeek, GLM (chat.z.ai):** откройте новый чат, приложите `PROMPT.md` и 1-3 файла под задачу, напишите
«Следуй PROMPT.md». В каждом новом чате файлы нужно приложить заново.

| Задача | Файлы |
|---|---|
| Подобрать Tibbit, проверить сокеты и питание | 01, 05 |
| Написать или проверить прошивку на Tibbo BASIC | 01, 04, 06 (+ 05 для платформы) |
| Библиотеки: DHCP, MQTT, Modbus, Wi-Fi, TLS | 06, 04 |
| Проект AppBlocks: объяснить, проверить, изменить | 02, 03 (+ 01 для железа) |
| Где почитать подробнее | 07 |

Проверка у себя на компьютере (распакуйте `tibbo-tools.zip` и в этой папке; на Windows `python`, на macOS/Linux `python3`):
```
python tibbo-firmware/scripts/tps_check.py check cfg.json --svg board.svg
python tibbo-firmware/scripts/tibbo_lint.py my_project --platform "TPP3W(G2)"
python appblocks/scripts/ab_tool.py check project.json
```
`[ОШИБКА]` в выводе - ошибка. Чем слабее модель, тем больше ошибок: всегда запускайте проверки и собирайте проект в TIDE.
