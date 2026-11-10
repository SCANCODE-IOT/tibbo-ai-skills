# Control tasks for the Tibbo skills

**English** · [Результаты на русском](RESULTS.md)

14 requests a real user would type - firmware, hardware, traps, AppBlocks - each with automatic checks of the
result. The set answers two questions: *do the skills help* (the same model with and without them) and *does a new
agent or model handle them* (Codex, Gemini CLI, Kimi Code and others).

```bash
python3 evals/run.py --agent claude --model sonnet              # with the skills
python3 evals/run.py --agent claude --model sonnet --no-skills  # the same model alone
python3 evals/run.py --agent codex                              # preset, not run by the authors: check with --dry
python3 evals/run.py --agent gemini
python3 evals/run.py --cmd 'kimi --prompt-file {prompt_file}'   # any agent: your own command line
python3 evals/run.py --report evals/runs/A evals/runs/B         # one table for several runs
python3 evals/run.py --grade evals/runs/A                       # check again without running the agent
```

For the "compiles" checks install Tibbo's compiler once:
`python3 skills/tibbo-firmware/scripts/tibbo_build.py --setup-node --yes` (Node.js 18+, git).

## What a run does

For every task: an empty folder, the task's input files, both skills in `.agents/skills` and `.claude/skills`
(unless `--no-skills`), the agent started in that folder with the task text. What the agent printed is saved as
`answer.md`. Then the folder is checked with the tools of this repository, whatever the agent used itself:

| Check | Meaning |
|---|---|
| `compiles` | the project builds with Tibbo's compiler |
| `lint_clean` | `tibbo_lint.py` finds no errors: exact API of the platform, invented events, missing callbacks |
| `tps_check_ok`, `cfg` | the hardware configuration passes `tps_check.py` and has the Tibbits the task needs |
| `ab_check_ok`, `ab_variable`, `ab_no_node`, `ab_same_nodes` | the AppBlocks project passes `ab_tool.py check`, has what was asked and nothing else changed |
| `regex`, `regex_all`, `regex_absent`, `no_file` | a required fact is in the answer or in the code; a forbidden one is not |

A task is solved when all its critical checks pass. Tasks and checks: `tasks.json`; input files: `fixtures/`.

| Group | Tasks |
|---|---|
| Firmware | TCP relay server, DHCP on a Wi-Fi board, RS232-TCP bridge, MQTT publisher, fix a project that does not build (one mistake the compiler does not report), review of code that builds but does not work |
| Hardware | 24 V on a 9-18 V supply, choose Tibbits and check power, ADC without the ±15 V supply |
| Knowledge | exact event names, a Linux board asked for Tibbo BASIC |
| AppBlocks | add a variable, a Zephyr-only block in a TiOS project, relays that switch on at boot |

## Reading the results honestly

- The checks are automatic and narrow: they prove that a project builds and contains what was asked, not that the
  device works. Nothing here runs on hardware.
- "Without skills" means the model's own knowledge: in these runs the agent had no web search.
- The `claude` preset limits the shell to Python scripts and read-only commands and says so in a system note
  (`CLAUDE_NOTE` in `run.py`); files are written with the agent's file tools.
- Several tasks ask for a file in the format of the skills' tools (`cfg.json`). A model without the skills cannot know
  it: that part of the difference is the tool, not the knowledge.
- Both Claude models solve every task with the skills, so this set does not tell a strong model from a small one yet.
  It needs harder tasks (several libraries in one project, larger AppBlocks changes).
