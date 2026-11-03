# multi-skill-creator (American English)

Create agent skills, then iteratively improve them with reproducible evals. **Not tied to any single CLI.**

For the full picture — why it's built this way, how it differs from upstream, and the complete list of supported agents — see the [repository README](../../README.md). This page covers installation and the essentials.

## Install

Drop this whole directory (`multi-skill-creator/`) into your agent's skills directory:

| Tool | Install location |
|---|---|
| Claude Code | `.claude/skills/multi-skill-creator/` (project) or `~/.claude/skills/` (global) |
| Finch | `.finch/skills/multi-skill-creator/` |
| Common convention | `.agents/skills/multi-skill-creator/` |
| Other CLIs | wherever that tool documents its skill or command directory |

This one directory is all you need. Don't install both language versions side by side — they share the same skill name and will shadow each other.

## Requirements

- Python 3.10+
- A non-interactively invocable agent CLI (`claude`, `codex`, `gemini`, `cursor-agent`, `opencode`, or `finch`), or any command you can drive with a template
- No third-party Python dependencies; `quick_validate.py` uses PyYAML when present and falls back to a built-in parser otherwise

## What it walks you through

Once installed, "I want to make a skill for X" is enough to start. The skill first works out where you are (idea / draft / optimize the description), then moves you forward:

1. Narrow the intent and interview for edge cases
2. Draft `SKILL.md` and test cases (`evals/evals.json`)
3. Run each case twice — with the skill and as a baseline
4. Grade and aggregate into `benchmark.json` (pass rate, time, tokens, mean ± stddev)
5. Generate a local review page for clicking through outputs and leaving feedback
6. Rewrite from the feedback, then run another iteration
7. Optimize the description against ~20 queries to reduce undertriggering

## Language

**Bilingual (Chinese + English) by default**: `zh-CN/<skill-name>/` and `en-US/<skill-name>/`, each independently usable. The Chinese version is built and verified first, then the English version follows from it. Want a single language? Just say so ("Chinese only", "English is fine") and the skill will honor it without adding a second version.

## Running the scripts by hand

All commands run from **this directory**:

```bash
# trigger evaluation
python -m scripts.run_eval --eval-set triggers.json --skill-path ../my-skill --agent auto --verbose

# eval + improve loop
python -m scripts.run_loop --eval-set triggers.json --skill-path ../my-skill --agent auto --max-iterations 5 --verbose

# aggregate a benchmark
python -m scripts.aggregate_benchmark <workspace>/iteration-1 --skill-name my-skill

# review page (add --static out.html on a headless host)
python eval-viewer/generate_review.py <workspace>/iteration-1 --skill-name my-skill --benchmark <workspace>/iteration-1/benchmark.json

# validate and package
python scripts/quick_validate.py ../my-skill
python -m scripts.package_skill ../my-skill
```

## Using a different agent

```bash
# a specific preset
--agent codex

# any CLI, prompt appended as the last argument
--agent-cmd "my-agent --print {prompt}"

# any CLI, prompt over stdin
--agent-cmd "my-agent --print" --agent-transport stdin

# skill directory not in the preset table
--install-root .myagent/skills
```

For per-CLI differences, where the probe skill gets installed, and why plain-text CLIs only give you an upper bound on trigger rates, see [`references/agent-cli.md`](references/agent-cli.md).

## License

Apache License 2.0. Derived from `skill-creator` in anthropics/skills.
