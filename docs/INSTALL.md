# Installing Tibbo Skills

**English** · [Русский](INSTALL.ru.md) · [← README](../README.md)

The skills work in two ways:

- **Agent with skills** (best): Claude, Codex, Gemini CLI, Kimi Code, Deep Code (DeepSeek), OpenCode and other
  coding agents read the skills from a folder and run the checking scripts themselves.
- **Web chat with the chat pack**: ChatGPT, Gemini, Kimi, DeepSeek, GLM (chat.z.ai) in the browser get instructions
  and knowledge files. ChatGPT with code interpreter can also run the checks; other chats hand you the commands.

## Which way is yours

| You use | Way | Section |
|---|---|---|
| Claude (claude.ai, desktop, mobile) | upload two zip files | [Claude apps](#claude-apps) |
| Claude Code | plugin or folder | [Claude Code](#claude-code) |
| Codex: CLI, IDE extension | skills folder | [Codex](#codex) |
| Gemini CLI | skills folder | [Gemini CLI](#gemini-cli) |
| Kimi Code | skills folder | [Kimi Code](#kimi-code) |
| DeepSeek in Deep Code, OpenCode or Claude Code | skills folder | [DeepSeek](#deepseek) |
| GLM (Z.ai) in Z Code, Claude Code, OpenCode or Codex | skills folder of that agent | [GLM](#glm-zai) |
| ChatGPT, Gemini, Kimi, DeepSeek, GLM in the browser | chat pack | [Web chats](#web-chats) |

## Before you start

1. **Python 3.9 or newer.** The checking scripts need it. Check: `python --version` (Windows) or `python3 --version`
   (macOS, Linux). No Python on Windows: install it from [python.org](https://www.python.org/downloads/) and tick
   *Add python.exe to PATH*. Nothing else is needed: the scripts use only the standard library.
2. **Download the files** from the [latest release](https://github.com/SCANCODE-IOT/tibbo-claude-skills/releases/latest):
   - `tibbo-firmware.zip` and `appblocks.zip` - the two skills (always install both: `appblocks` uses the board
     checker of `tibbo-firmware`);
   - `tibbo-chat-pack.zip` - only for web chats;
   - *Source code (zip)* - the whole repository with the installer `tools/install.py`.

## Installer for all agents

Unpack *Source code (zip)*, open a terminal in the unpacked folder and run:

```bash
python tools/install.py            # Windows
python3 tools/install.py           # macOS, Linux
```

It copies both skills to `~/.agents/skills/` - the shared folder that Codex, Gemini CLI, Kimi Code, Deep Code,
Cline and Zed read - and to `~/.claude/skills/` if Claude Code is installed. Then it runs a self-test from the
installed copy and prints `self-test: ok`.

Other folders: `--agent claude`, `--agent opencode`, `--agent cursor`, `--agent copilot`, `--agent gemini`
(`~/.gemini/skills`), `--agent all`. `--list` shows the folders, `--project <folder>` installs into one project
(`<folder>/.agents/skills`), `--uninstall` removes the skills. Running it again replaces the old version.

**Without the installer:** create the folder `~/.agents/skills/` (on Windows `C:\Users\<you>\.agents\skills\`) and
unpack `tibbo-firmware.zip` and `appblocks.zip` into it so that you get
`~/.agents/skills/tibbo-firmware/SKILL.md` and `~/.agents/skills/appblocks/SKILL.md`.

## Claude apps

1. Make sure code execution is on: **Settings → Capabilities** (on Team and Enterprise plans an owner enables skills).
2. **Customize → Skills** → **+** → **Create skill** → **Upload a skill**.
3. Upload `tibbo-firmware.zip`, then `appblocks.zip`. Check that both are switched on.

If the menu looks different, see [Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude).

## Claude Code

```text
/plugin marketplace add SCANCODE-IOT/tibbo-claude-skills
/plugin install tibbo-skills@scancode
```

Updates: `/plugin marketplace update scancode`. Or install into the folder: `python tools/install.py --agent claude`.
**Claude API:** upload each skill folder through the [Skills API](https://platform.claude.com/docs/en/build-with-claude/skills-guide).

## Codex

Codex CLI and the Codex IDE extension read skills from `~/.agents/skills/`.

1. Run the [installer](#installer-for-all-agents) (or unpack the two zips into `~/.agents/skills/`).
2. Restart Codex. In Codex CLI, `/skills` lists the skills; `$tibbo-firmware` calls one directly.
3. Usually you do not need to call them: describe a Tibbo task and Codex picks the skill by its description.

## Gemini CLI

Gemini CLI reads `~/.gemini/skills/` and `~/.agents/skills/`, so the [installer](#installer-for-all-agents) is enough.
Alternatively, Gemini CLI can install from GitHub itself:

```bash
gemini skills install https://github.com/SCANCODE-IOT/tibbo-claude-skills.git --path skills/tibbo-firmware
gemini skills install https://github.com/SCANCODE-IOT/tibbo-claude-skills.git --path skills/appblocks
```

Check in a session: `/skills list`.

## Kimi Code

Kimi Code reads `~/.agents/skills/` (and `~/.kimi-code/skills/`). Run the [installer](#installer-for-all-agents),
restart Kimi Code (in the Kimi Code desktop app, `/reload`) and ask your question, or type `/` and pick the skill.
If the skills are already in Claude Code or Codex, `/import-from-cc-codex` brings them over.

**Kimi app (K3.1 Pro), web and desktop, Agent mode.** It cannot take a skill folder: Kimi builds a skill from
Office documents. Ready set: [tibbo-skills-kimi-app.zip](kimi/tibbo-skills-kimi-app.zip) - two folders, each with three
Word documents and a description text. In Kimi: Agent mode → Skills panel → "Convert Office Documents into a Skill" →
upload the three .docx from a folder → paste the description → "Create Skill". The checking scripts do not run there:
Kimi gives you the commands to run on your computer.

Step-by-step guide for Kimi (Word, Russian): [tibbo-skills-kimi-guide.ru.docx](kimi/tibbo-skills-kimi-guide.ru.docx).

## DeepSeek

- **Deep Code**, the terminal agent for DeepSeek models (`npm install -g @vegamo/deepcode-cli`), reads
  `~/.agents/skills/`: run the [installer](#installer-for-all-agents) and restart it. `/` opens the skill picker.
- **OpenCode** or **Claude Code** with a DeepSeek API key: install into that agent's folder
  (`--agent opencode` or `--agent claude`).

## GLM (Z.ai)

GLM models work through the GLM Coding Plan in Z Code, Claude Code, OpenCode, Codex, Cline and other agents.
Install the skills into the agent you use: Claude Code or Z Code - `--agent claude`; OpenCode - `--agent opencode`;
Codex or Cline - the default `~/.agents/skills/`.

## Other agents

Most agents that support Agent Skills read `.agents/skills/` in the project folder (`--project <folder>`).
The [Vercel skills CLI](https://github.com/vercel-labs/skills) installs into 80+ agents (Node.js 22.20+):
`npx skills add SCANCODE-IOT/tibbo-claude-skills -g`.

## Web chats

Unpack `tibbo-chat-pack.zip`. Inside: `PROMPT.md` (instructions), seven knowledge files `01`-`07`, `tibbo-tools.zip`
(the scripts) and a short `README.md`.

- **ChatGPT, custom GPT** (paid plans): Explore GPTs → Create → Configure. Paste the text of `PROMPT.md` into
  *Instructions*, upload `01`-`07` and `tibbo-tools.zip` to *Knowledge*, turn on *Code Interpreter & Data Analysis*.
  The GPT runs the checks itself.
- **ChatGPT, Project:** create a project, paste `PROMPT.md` into the project instructions, add the files.
- **Gemini, Gem:** Gems → New Gem. `PROMPT.md` into *Instructions*, `01`-`07` into *Knowledge* (up to 10 files).
- **Kimi (kimi.com), DeepSeek (chat.deepseek.com), GLM (chat.z.ai):** in a new chat attach `PROMPT.md` and the 1-3
  files your task needs and write "Follow PROMPT.md". Repeat in every new chat.

| Task | Files |
|---|---|
| Choose Tibbits, check sockets and power | 01, 05 |
| Write or review Tibbo BASIC firmware | 01, 04, 06 (+ 05 for the platform) |
| Libraries: DHCP, MQTT, Modbus, Wi-Fi, TLS | 06, 04 |
| AppBlocks project | 02, 03 (+ 01 for hardware) |

A chat that cannot run code gives you the files and the commands. Run them on your computer: unpack
`tibbo-tools.zip` and, in that folder,

```bash
python tibbo-firmware/scripts/tps_check.py check cfg.json --svg board.svg
python tibbo-firmware/scripts/tibbo_lint.py my_project --platform "TPP3W(G2)"
python appblocks/scripts/ab_tool.py check project.json
```

`[ОШИБКА]` in the output means an error; send the output back to the chat.

## Check that it works

Ask: *"TPP3W(G2): power Tibbit #10 in S1 with #18 in S2, the cabinet has 24 V. Is this OK?"*
A working skill states its assumptions, runs `tps_check.py` (or gives you the command) and answers that #10 accepts
only 9-18 V, so for 24 V you need #25 or #33. An answer without these steps means the skill was not loaded:
restart the agent and check the folder.

## How well does each model do

The skills carry the rules and the data, but the quality still depends on the model. Strong models follow the
procedure on their own. Smaller and faster models skip steps more often: insist on the checks
(`tps_check.py`, `tibbo_lint.py`, `ab_tool.py check`) and build every firmware in TIDE before it goes to hardware.

## Troubleshooting

- **`python` is not found.** Windows: reinstall Python with *Add to PATH*, or use `py` instead of `python`.
- **The agent does not see the skill.** Restart it; check that `SKILL.md` lies one level deep:
  `.../skills/tibbo-firmware/SKILL.md`, not `.../skills/tibbo-firmware/tibbo-firmware/SKILL.md`.
- **Russian text is garbled** in an old Windows console: `chcp 65001` or Windows Terminal.
- **`CERTIFICATE_VERIFY_FAILED` from `ab_api.py`** on Windows: `pip install truststore`; `python scripts/ab_api.py tls`
  shows which certificate store is used. Certificate checks are never switched off.
- **Update:** download the new release and run the installer again (Claude apps: upload the new zips).
