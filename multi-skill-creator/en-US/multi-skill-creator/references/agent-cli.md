# The Agent CLI Adapter

`scripts/agent_cli.py` is the only part of this skill that talks to an external agent. It reduces two operations to data:

- **Completion**: hand it a long prompt, get text back. Used to rewrite a skill description from eval failures.
- **Trigger probe**: run a user query in a project where a skill is installed, and report whether the agent actually loaded that skill.

The upstream version hard-wired both to `claude -p`. This version makes them configurable, so switching CLIs never requires editing the skill.

## Choosing the agent

Resolution order:

1. `--agent-cmd "<command template>"`, or the `SKILL_CREATOR_AGENT_CMD` environment variable
2. `--agent <preset>`
3. With no flags, the first preset whose executable is on PATH (same as `--agent auto`)

If nothing resolves, the adapter raises `AgentUnavailable` with an actionable message instead of a confusing subprocess error.

A command template may contain two placeholders:

| Placeholder | Meaning |
|---|---|
| `{prompt}` | Where the prompt goes. With no placeholder, the prompt is appended as the final argument |
| `{model}` | The model name. When `--model` is not passed, a standalone `{model}` argument is dropped entirely |

```bash
# template with a placeholder
--agent-cmd "my-agent --print {prompt}"
# prompt via stdin
--agent-cmd "my-agent --print" --agent-transport stdin
# with a model
--agent-cmd "my-agent --print {prompt} --model {model}" --model fast-1
```

Paths with spaces need no special handling on Windows; the adapter strips the quoting itself:

```powershell
--agent-cmd 'python "C:\tools\my agent.py"'
```

## Built-in presets

| Preset | Executable | Probe event stream | Skill install locations |
|---|---|---|---|
| `claude` | `claude` | JSON stream events | `.claude/skills/`, `.claude/commands/` |
| `codex` | `codex` | plain text | `.agents/skills/` |
| `gemini` | `gemini` | plain text | `.gemini/skills/` |
| `cursor-agent` | `cursor-agent` | plain text | `.cursor/skills/`, `.agents/skills/` |
| `opencode` | `opencode` | plain text | `.opencode/skills/` |
| `finch` | `finch` | plain text | `.finch/skills/`, `.claude/skills/` |

Presets are starting points, not gospel: CLI flags change between releases. When one drifts, override with `--install-root` or `--agent-cmd`, or edit the entry in `PRESETS`. Each preset carries a comment in the code stating its assumptions.

## How the probe works

1. In the project root, write a tiny skill body into the directories that CLI scans:
   - `skill_md` style: `<dir>/<skill-name>-probe-<random>/SKILL.md`
   - `command_md` style: `<dir>/<skill-name>-probe-<random>.md`
   - The body contains a random token `PROBE-TOKEN-<hex>`. The important detail: that token does **not** appear in the skill's name, only in the file's body. The name is visible in the agent's skill list; the body has to actually be read. An earlier version searched for the name prefix, so an answer that merely mentioned the skill name counted as triggered — and plenty of CLIs list a skill's name while declining to use it, which systematically overstates trigger rates
2. Hand the user's query to the agent
3. Decide whether it triggered
4. Delete the probe files (and any directory the probe created)

**The decision differs per CLI, and that needs to be stated plainly:**

- **Structured output** (`claude`, and any CLI emitting JSON event lines): inspect the first tool call. If it reads a skill and the payload contains that token, it counts as triggered; if the first tool call is something else, it does not. This is the reliable path, and it is evaluated line by line as the stream arrives, so a trigger returns immediately instead of waiting for the process to exit
- **Plain text output** (every other preset): a text heuristic — the answer must contain the random token. The token exists only inside the probe skill's body, so its presence is reasonable evidence the skill was read, and echoing the name cannot fool it. That evidence is still weaker than an event stream: a CLI that dumps skill directory contents into context wholesale could cause a false positive

So for plain-text CLIs, treat the trigger score as an **upper bound**. It is more trustworthy for relative comparisons (this description beats that one) than for absolute judgments. For precise trigger measurement, use a CLI with event streams.

If the probe cannot be installed anywhere (read-only project, sandbox restrictions), the script fails loudly rather than silently reporting "not triggered" — a silent failure would mark every query as untriggered and corrupt every score.

## Determining the project root

The probe has to land in whatever directory the CLI treats as this project's root. `find_project_root()` walks up from the current directory and stops at any of: `.claude`, `.finch`, `.agents`, `.gemini`, `.cursor`, `.opencode`, `.git`. If none is found, it uses the current directory.

When the guess is wrong, pass `--project-root` explicitly.

## When the known directories are wrong

Your CLI's skill directory isn't in the table, or you're driving a custom agent:

```bash
python -m scripts.run_eval ... --install-root .myagent/skills
```

`--install-root` is repeatable and overrides the preset's guesses. Paths are relative to the project root.

## Nested invocation

Running a CLI non-interactively from inside that same CLI's session trips a few tools' nesting guards. The adapter strips these variables before starting a child process: `CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`, `CODEX_SANDBOX`, `GEMINI_CLI`. Stripping a variable that isn't set is a no-op.

## Which script uses what

| Script | How it uses the adapter |
|---|---|
| `run_eval.py` | Trigger probe |
| `improve_description.py` | Completion (description rewrite) |
| `run_loop.py` | Both |
| `aggregate_benchmark.py` / `generate_report.py` / `package_skill.py` | No use; pure local computation and packaging |

`run_eval.py`, `improve_description.py`, and `run_loop.py` share one set of flags (`--agent`, `--agent-cmd`, `--agent-transport`, `--install-root`, `--agent-model-flag`), defined in `run_eval.add_agent_arguments()` so the three scripts cannot drift apart.

## How a model reaches a custom CLI

A custom template does **not** get `--model` appended by default: an unknown CLI probably has no such switch, and guessing wrong turns a working command into an argument-error crash. Two supported routes:

```bash
# 1) place it yourself in the template (recommended)
--agent-cmd "my-agent --print {prompt} --model {model}" --model fast-1

# 2) declare the switch and let the script append it
--agent-cmd "my-agent --print {prompt}" --agent-model-flag --model --model fast-1
```

Neither route duplicates: when the template already contains `{model}`, `build_command()` does not append it again.
