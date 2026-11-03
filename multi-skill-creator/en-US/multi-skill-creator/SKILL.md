---
name: multi-skill-creator
description: Create new skills, modify and improve existing skills, and measure skill performance with reproducible evals. Use when users want to build a skill from scratch, edit or optimize an existing skill, run evals to verify a skill actually works, benchmark a skill's value with variance analysis, or optimize a skill description for better triggering accuracy. Defaults to writing every skill in both Chinese (zh-CN) and English (en-US) unless the user asks for a specific language. Reach for it even when the user never says the word "skill" — if the conversation is about packaging a repeatable procedure, script, or reference material into a reusable capability, this skill applies.
metadata:
  language: en-US
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

One premise up front: **this skill is not tied to any single vendor, IDE, or CLI.** Anything that can run Python and invoke an agent CLI non-interactively can use it — Claude Code, Codex, Gemini CLI, Cursor, OpenCode, Finch, or an agent you wrote yourself. The scripts pick an agent through one adapter layer, `scripts/agent_cli.py`, so switching tools never requires rewriting the skill. Users whose main tool is Claude will find notes for those environments below, but those are "special cases for one tool", not the main path.

At a high level, creating a skill goes like this:

- Decide what you want the skill to do and roughly how it should do it
- Write a draft (bilingual by default: Chinese first, then sync English once verified; only one language when the user asked for one)
- Create a few test prompts and run an agent-with-access-to-the-skill on them
- Help the user evaluate the results, both qualitatively and quantitatively
  - While the runs happen in the background, draft some quantitative evals if there aren't any (if there are some, use them as-is or modify what needs changing). Then explain them to the user — or, if they already existed, explain the ones that already exist
  - Use `eval-viewer/generate_review.py` to show the user the results, and let them look at the quantitative metrics too
- Rewrite the skill based on the user's evaluation of the results (and fix any glaring flaws the quantitative benchmarks make obvious)
- Repeat until you're satisfied
- Expand the test set and try again at larger scale

Your job when using this skill is to figure out where the user is in this process, then jump in and help them move forward. If they say "I want to make a skill for X", you can help narrow down what they mean, write a draft, write the test cases, figure out how they want to evaluate, run all the prompts, and iterate. If they already have a draft, go straight to the eval/iterate loop.

Always stay flexible: if the user says "I don't need a pile of evals, just think it through with me", do that instead.

Once the skill is basically done (order stays flexible), you can also run the description improver — a separate script whose only job is improving triggering accuracy.

## Language: Bilingual by Default, User Overrides

**Produce bilingual skills by default**: `zh-CN/<skill-name>/` and `en-US/<skill-name>/`, each independently usable, structured as described in the Bilingual Versions section. Don't stop to ask "Chinese or English?" before starting — unless the user has stated a language preference, go straight to bilingual.

Switch to a single language only when:

- The user names a language ("Chinese only", "English is fine", "do Chinese now, English later"). Do what they said; don't helpfully add a second version they didn't ask for.
- The user says explicitly that this is internal, throwaway, or not worth maintaining twice.

For a single-language skill, pick the language the same way: the user's choice wins, otherwise follow the language of the conversation — and mention in one line at delivery that only the <language> version exists and the other can be added on request.

Either way, **finish the implementation before translating**. Simplified Chinese is the primary development language: implement, verify, and revise in the Chinese version, then produce the English version from it. Never introduce functionality or behavioral changes independently in the English version.

## Capture Intent

Start by understanding what the user actually wants. The conversation may already contain a workflow they want to capture (e.g. "turn this into a skill"). In that case, extract answers from the conversation first — the tools used, the sequence of steps, the corrections the user made, the input/output formats you observed. Fill the remaining gaps with questions, and get confirmation before moving on.

1. What should this skill enable the agent to do?
2. When should it trigger? (what phrases, what contexts)
3. What's the expected output format?
4. Should we set up test cases to verify the skill works? Skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't. Suggest the appropriate default for the skill type, but let the user decide.

## Interview and Research

Proactively ask about edge cases, input/output formats, example files, success criteria, and dependencies. Get this ironed out before writing test prompts.

Check which MCP tools are available. If they help with research (searching docs, finding similar skills, looking up best practices), research in parallel — via subagents if you have them, inline otherwise. Come prepared with context to reduce the burden on the user.

## Write the SKILL.md

From the interview, fill in these parts:

- **name**: the identifier, kebab-case, 64 characters max
- **description**: when to trigger, what it does. This is the entire triggering mechanism — include both what the skill does AND specific contexts for when to use it. All "when to use" information goes here, not in the body. Note that agents have a general tendency to *undertrigger* — to skip a skill that would have helped. To counter that, descriptions can be a little **pushy**. Instead of "How to build a simple dashboard to display company data", write "How to build a simple dashboard to display company data. Use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a 'dashboard.'"
- **metadata.language**: the language tag for this copy (see the Bilingual section)
- **compatibility**: required tools and dependencies (optional, rarely needed)
- **the body, and everything else**

### Skill Writing Guide

#### Anatomy of a Skill

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description required)
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - executable code for deterministic/repetitive tasks
    ├── references/ - docs loaded into context as needed
    └── assets/     - files used in output (templates, icons, fonts)
```

Skills are bilingual by default, so the real deliverable wraps one of these in a language directory — `zh-CN/skill-name/` and `en-US/skill-name/`, each containing the full structure above. See "Bilingual Versions → 1. Language Structure".

#### Progressive Disclosure

Skills load in three levels:
1. **Metadata** (name + description) — always in context (~100 words)
2. **SKILL.md body** — in context whenever the skill triggers (<500 lines ideal)
3. **Bundled resources** — as needed (unlimited; scripts can execute without loading)

These counts are rules of thumb; go longer if the content genuinely needs it.

**Key patterns:**
- Keep SKILL.md under 500 lines. As you approach that limit, add another layer of hierarchy and clear pointers telling the agent where to go next
- Reference files clearly from SKILL.md, with guidance on when to read them
- For reference files over 300 lines, include a table of contents

**Domain organization**: when a skill covers multiple domains or frameworks, split by variant:

```
cloud-deploy/
├── SKILL.md (workflow + selection logic)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

The agent reads only the relevant reference file.

#### Principle of Lack of Surprise

Skills must not contain malware, exploit code, or anything that could compromise system security. Once a skill is adopted, its contents should not surprise the user in intent. Don't go along with requests to build misleading skills, or skills designed for unauthorized access or data exfiltration — and don't pretend not to notice a problem just to keep the user happy. "Roleplay as an XYZ" is fine.

#### Writing Patterns

Prefer the imperative form in instructions.

**Defining output formats** — like this:

```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

**Examples pattern** — examples are valuable. You can format them like this (if "Input"/"Output" labels don't fit the domain, rename them):

```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

#### Writing Style

Explain **why** something matters rather than piling on heavy-handed MUSTs. Today's models are smart, with good theory of mind: give them a good harness and they'll go beyond rote instructions. So write a draft, then read it again with fresh eyes and improve it.

Keep the skill **general** rather than over-fitted to the handful of examples in front of you.

### Test Cases

After writing the draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user (don't feel bound to my exact wording): "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?" Then run them.

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions in the next section, while the runs are in flight.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema, including the `assertions` field you'll add later.

## Running and Evaluating Test Cases

This section is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/`, a sibling of the skill directory. The layout is a contract, because the aggregator scans for exactly this shape — miss a level and it finds nothing:

```text
<skill-name>-workspace/
└── iteration-1/
    ├── csv-column-tidy/            ← test case, descriptive name
    │   ├── eval_metadata.json
    │   ├── with_skill/
    │   │   ├── run-1/
    │   │   │   ├── outputs/        ← produced files
    │   │   │   ├── grading.json
    │   │   │   └── timing.json
    │   │   └── run-2/              ← only when repeating a config
    │   └── without_skill/
    │       └── run-1/
    │           ├── outputs/
    │           └── grading.json
    └── pdf-table-extract/
        └── …
```

The rules:
- Test-case directories may — and should — be descriptively named rather than `eval-0`
- **Every configuration needs that `run-<N>/` level**, and `grading.json` belongs inside the run directory
- One run means `run-1`; repeat runs mean `run-1`, `run-2`, which the aggregator turns into mean ± stddev
- Don't create all of it upfront — build as you go

`python -m scripts.aggregate_benchmark` scans for `<case>/<config>/run-<N>/grading.json`. If the shape is wrong it exits with an error instead of writing an all-zero benchmark.

### Step 1: Spawn every run in the same turn

Each test case gets two runs — one with the skill, one as a baseline. The important part: don't run the with-skill cases first and come back for baselines later. Launch everything at once so it all finishes around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <the eval's files, or "none">
- Save outputs to: <workspace>/iteration-<N>/<case-name>/with_skill/run-1/outputs/
- Outputs to save: <what the user actually cares about — e.g. "the .docx file", "the final CSV">
```

**Baseline run** (same prompt; what the baseline is depends on context):
- **Creating a new skill**: no skill at all. Same prompt, no skill path, saved to `without_skill/run-1/outputs/`
- **Improving an existing skill**: the old version. Snapshot it before editing (`cp -r <skill-path> <workspace>/skill-snapshot/`, or `Copy-Item -Recurse` on Windows), then point the baseline run at the snapshot, saved to `old_skill/run-1/outputs/`

Bilingual skills: `<path-to-skill>` points at a **specific language directory** (e.g. `zh-CN/<skill-name>`), one language per evaluation run, with test prompts written in that language. Each language gets its own full with-skill/baseline comparison — don't mix them, and don't use the Chinese results to draw conclusions about the English version.

Write an `eval_metadata.json` for each test case (assertions can stay empty for now). Name each eval for what it tests — not just "eval-0". Use that name for the directory too. If this iteration uses new or modified prompts, create these files for every new eval directory; don't assume they carry over from the previous iteration.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

**On "spawning" a run**: it depends on your harness. With parallel subagents, give each run its own (for example Finch's `multi_agent_run`, or a task/subagent tool in other CLIs). Without them, run the cases in series, or just work through the skill's instructions yourself in the main conversation. Either way, two things stay true: the with-skill and baseline runs must be a fair comparison, and each run's outputs must land in its own `outputs/` directory.

### Step 2: While runs are in progress, draft assertions

Don't just wait. Use the time to draft quantitative assertions for each test case and explain them to the user. If `evals/evals.json` already has assertions, review them and explain what they check.

Good assertions are objectively verifiable and have descriptive names — someone glancing at the benchmark report should immediately understand what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively; don't force assertions onto things that need human judgment.

Update `eval_metadata.json` and `evals/evals.json` once the assertions are drafted. Also explain what the user will see in the viewer — both the qualitative outputs and the quantitative benchmark.

### Step 3: As runs complete, capture timing data

Every finished run should give you a token count and a duration. Whatever your harness exposes — a task completion notification, a log line, your own timing — write it to `timing.json` in that run's directory straight away:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This is easy to skip and impossible to recover later. **If you don't have exact numbers, don't invent them**: keep the fields you do have (even if it's only your own wall-clock time) and omit the rest. A missing column in the benchmark beats a fabricated one.

### Step 4: Grade, aggregate, and launch the viewer

Once all runs are done:

1. **Grade each run** — have a grader agent (or yourself, in the main conversation) read `agents/grader.md` and evaluate each assertion against the outputs; save results to `grading.json` in each run directory. The `grading.json` expectations array must use the field names `text`, `passed`, and `evidence` (not `name`/`met`/`details` or any other variant) — the viewer depends on those exact names. For assertions that can be checked programmatically, write and run a script rather than eyeballing it: faster, more reliable, and reusable across iterations.

2. **Aggregate into a benchmark** — run the aggregator from the skill directory:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>
   ```
   This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens per configuration, including mean ± stddev and the delta. If you write benchmark.json by hand, follow `references/schemas.md` exactly. Put each with-skill version before its baseline counterpart.

3. **Do an analyst pass** — read the benchmark data and surface patterns the aggregates hide. See the "Analyzing Benchmark Results" section of `agents/analyzer.md` for what to look for: assertions that pass no matter what (non-discriminating), high-variance evals (possibly flaky), and time/token tradeoffs.

4. **Launch the viewer** with both qualitative outputs and quantitative data:
   ```bash
   python <skill-creator-path>/eval-viewer/generate_review.py \
     <workspace>/iteration-N \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-N/benchmark.json
   ```
   For iteration 2 and later, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

   **Environments with no display or browser** (remote servers, containers, sandboxes): use `--static <output_path>` to write a standalone HTML file and hand the user the path to open. When the user clicks "Submit All Reviews", `feedback.json` downloads as a file; copy it back into the workspace directory so the next iteration picks it up.

   Use `generate_review.py` to build the viewer — don't write your own HTML.

5. **Tell the user** something like: "I've opened the results in your browser. There are two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. Come back here when you're done."

### What the user sees in the viewer

The "Outputs" tab shows one test case at a time:
- **Prompt**: the task that was given
- **Output**: the files the skill produced, rendered inline where possible
- **Previous Output** (iteration 2+): last iteration's output, collapsed
- **Formal Grades** (if grading ran): assertion pass/fail, collapsed
- **Feedback**: a textbox that auto-saves as they type
- **Previous Feedback** (iteration 2+): their comments from last time, below the textbox

The "Benchmark" tab shows the stats summary: pass rates, timing, and token usage per configuration, with per-eval breakdowns and analyst observations.

Navigate with the prev/next buttons or arrow keys. When done, "Submit All Reviews" saves everything to `feedback.json`.

### Step 5: Read the feedback

When the user says they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."},
    {"run_id": "eval-2-with_skill", "feedback": "perfect, love this", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus improvements on the cases where they raised something specific.

Shut down the viewer server when you're done with it (not applicable if you used `--static`).

## Improving the Skill

This is the heart of the loop. The test cases ran, the user reviewed the results, and now you make the skill better based on their feedback.

### How to think about improvements

1. **Generalize from the feedback.** The big picture: we're building skills meant to be used a million times (maybe literally, who knows), while iterating on only a handful of examples. That's fine for speed — the user knows these examples inside out and can judge new outputs quickly. But if the skill only works for those examples, it's useless. Rather than fiddly over-fitted tweaks, or oppressively constrictive MUSTs, try branching out: different metaphors, a different way of working. Experiments are cheap and you might land on something great.

2. **Keep it lean.** Remove what isn't pulling its weight. Read the **transcripts**, not just the final outputs. If the skill is making the model waste time on unproductive work, delete the parts causing it and see what happens.

3. **Explain the why.** Try hard to explain the **reason** behind everything you ask for. If you catch yourself writing ALWAYS or NEVER in all caps, or reaching for rigid structures, that's a yellow flag — reframe and explain the reasoning instead.

4. **Look for repeated work across test cases.** Read the run transcripts and notice whether every run independently wrote a similar helper script or took the same multi-step approach. If all 3 cases produced a `create_docx.py` or a `build_chart.py`, that's a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and tell the skill to use it. That saves every future invocation from reinventing the wheel.

This matters — the goal is real economic value at scale — and thinking time is not the bottleneck. Slow down and mull it over. Draft a revision, then look at it again with fresh eyes and improve it. Really try to get inside the user's head and understand what they want and need.

### The iteration loop

After improving:

1. Apply the improvements to the skill
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. When creating a new skill, the baseline is always `without_skill` (no skill) and stays the same across iterations. When improving an existing skill, use judgment on what makes the better baseline: the version the user arrived with, or the previous iteration
3. Launch the reviewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user to review and say they're done
5. Read the new feedback, improve again, repeat

Bilingual skills: iterate in the Chinese version until it's stable, then sync the finalized text to English and **run a separate verification pass on the English version** — translation drifts, so don't let English inherit the Chinese conclusions. Usually one English pass is enough.

Stop when:
- The user says they're happy
- The feedback is all empty (everything looks good)
- You're not making meaningful progress

## Advanced: Blind Comparison

When you want a more rigorous comparison between two versions of a skill (e.g. the user asks "is the new version actually better?"), there's a blind comparison system. See `agents/comparator.md` and `agents/analyzer.md` for details. The idea: hand two outputs to an independent agent without telling it which is which, let it judge quality, then analyze why the winner won.

Optional, requires subagents, and most users won't need it. The human review loop is usually sufficient.

## Description Optimization

The `description` field in the SKILL.md frontmatter is the primary mechanism determining whether an agent loads a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

### Step 1: Generate trigger eval queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

The queries must be realistic — something a user of this agent would actually type. Not abstract requests: concrete and specific, with detail. File paths, the user's own job and situation, column names and values, company names, URLs, a bit of backstory. Some can be all lowercase, include abbreviations, typos, or casual speech. Mix the lengths, and focus on edge cases rather than clean-cut ones (the user gets a chance to sign off on them).

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

The **should-trigger** queries (8-10) need coverage: different phrasings of the same intent, some formal and some casual; cases where the user never names the skill or file type but clearly needs it; some uncommon use cases; and cases where this skill competes with another but should win.

The **should-not-trigger** queries (8-10) are most valuable as near-misses — queries that share keywords or concepts with the skill but actually need something else. Think adjacent domains, ambiguous phrasing where naive keyword matching would fire but shouldn't, and cases that touch the skill's territory where another tool is the better answer.

The key thing to avoid: should-not-trigger queries that are obviously irrelevant. "Write a fibonacci function" as a negative for a PDF skill is too easy — it tests nothing. Negatives have to be genuinely tricky.

### Step 2: Review with the user

Present the eval set to the user for review using the HTML template:

1. Read `assets/eval_review.html`
2. Replace the placeholders:
   - `__EVAL_DATA_PLACEHOLDER__` → the JSON array of eval items (no surrounding quotes — it's a JS variable assignment)
   - `__SKILL_NAME_PLACEHOLDER__` → the skill's name
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → the skill's current description
3. Write to a temp file and open it:
   - macOS: `open /tmp/eval_review_<skill-name>.html`
   - Windows: `Start-Process <path>`
   - Linux: `xdg-open <path>`
4. The user can edit queries, toggle should-trigger, add or remove entries, then click "Export Eval Set"
5. The file downloads to the Downloads folder — if there are several (e.g. `eval_set (1).json`), take the newest

This step matters: bad eval queries lead to bad descriptions.

### Step 3: Run the optimization loop

Tell the user: "This will take a while — I'll run the optimization loop in the background and check on it periodically."

Save the eval set to the workspace, then run it:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --agent auto \
  --max-iterations 5 \
  --verbose
```

`--agent auto` picks the first supported CLI found on PATH. To use something else, or pass a model:

```bash
# a specific preset
python -m scripts.run_loop ... --agent codex

# any custom CLI: tell it how to receive the prompt
python -m scripts.run_loop ... --agent-cmd "my-agent --print {prompt}"

# that CLI reads the prompt from stdin
python -m scripts.run_loop ... --agent-cmd "my-agent --print" --agent-transport stdin

# model (only when the CLI supports one)
python -m scripts.run_loop ... --model <model-id>
```

`{prompt}` is a placeholder. If your template has none, the prompt is appended as the final argument. The `SKILL_CREATOR_AGENT_CMD` environment variable works in place of `--agent-cmd`.

This handles the full loop automatically: it splits the eval set 60% train / 40% held-out test, evaluates the current description (running each query 3 times for a reliable trigger rate), then asks the agent to propose improvements based on what failed. Each new description is re-evaluated on both splits, iterating up to 5 times. When it finishes it opens an HTML report showing the results per iteration and returns JSON whose `best_description` is selected by test score rather than train score, to avoid overfitting.

While it runs, tail the output periodically and tell the user which iteration it's on and how the scores look.

### How skill triggering works

Understanding triggering helps you design better eval queries. Skills appear in the agent's skill list as name + description, and the agent decides purely from that description whether to consult the skill. Crucially, agents only consult skills for tasks they can't easily handle on their own. A simple one-step request like "read this PDF" may not trigger a skill even with a perfect description, because the agent can just do it. Complex, multi-step, or specialized requests reliably trigger skills when the description matches.

So eval queries need enough substance that the agent would actually benefit from the skill. "Read file X" is a poor test case — it won't trigger regardless of description quality.

### Step 4: Apply the result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter. Show the user the before/after and report the scores.

For a bilingual skill, **run this once per language**: the two descriptions are worded differently and trigger differently, so a Chinese `best_description` cannot be translated into the English result. Write the eval queries in the target users' language too — Chinese queries for the zh-CN copy, English for the en-US copy. Running Chinese queries against an English description measures the wrong thing.

## Package and Present

To hand the user a distributable skill package (only if your environment can give files back to the user; otherwise skip this):

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

After packaging, point the user at the resulting `.skill` file so they can install it.

A bilingual skill means **one package per language directory**, keeping the identical output filename apart by directory (e.g. `dist/zh-CN/<skill-name>.skill` and `dist/en-US/<skill-name>.skill`) so one doesn't overwrite the other. Say clearly which package is which language. If the user asked for a single language, package only that one.

## Adapting to Your Environment

The core workflow (draft → test → review → improve → repeat) is the same everywhere; only the mechanics change. Work out which environment you're in, then adjust. Three questions settle it: can you run subagents in parallel? Is there a display? Is an agent CLI available?

### Parallel subagents available

The best case. Test cases really do run in parallel, baseline comparisons are meaningful, and quantitative benchmarking is worth doing.

- Spawn two subagents per test case (with skill / baseline) in the same turn
- Have each subagent write its own `metrics.json` (tool call counts, output characters, errors encountered) for use during grading
- If you hit severe timeout problems, running cases in series is acceptable

### No subagents (single-threaded, e.g. a web chat or a single-process CLI)

- Can't parallelize, so go one at a time. For each test case, read the skill's `SKILL.md` and then follow it to complete the prompt. Less rigorous than independent subagents (you wrote the skill and you're carrying all the context), but a useful sanity check — and the human review step compensates
- **Skip baseline runs** — without independent execution, baseline comparison means nothing
- **Skip quantitative benchmarking** — same reason. Put the effort into qualitative feedback instead

### No browser or display

- Generate the viewer with `--static <output_path>` to write a standalone HTML file, and give the user the path to open themselves
- If you can't show HTML at all, present results directly in the conversation: for each test case, the prompt and the output. If the output is a file (.docx, .xlsx), save it to the filesystem and tell the user where, so they can download and inspect it. Ask inline: "How does this look? Anything you'd change?"

### No agent CLI available

The quantitative triggering features (turn the description into a template any CLI can consume) need a non-interactive agent CLI. Without one:

- Skip the description-optimization section entirely
- Test cases can still run, but only by hand in the main conversation, with scores judged by a human
- Writing the skill, designing evals, and packaging are all unaffected

### If Claude Code / Claude.ai / Cowork is your main tool

The upstream original was written for these environments. What's different here:

- **Claude Code**: the full workflow works. `--agent claude` is one of the default presets and `auto` usually selects it. Packaged `.skill` files can be shared directly
- **Claude.ai**: no subagents, and no non-interactive `claude` CLI, so follow the two reduced modes above. `package_skill.py` still works with nothing but Python and a filesystem
- **Cowork**: has subagents, so the main workflow runs; no display, so use `--static` for the viewer. Note that agents in these environments tend to skip generating the viewer after tests finish, so one more time: **in every environment, generate the viewer with `generate_review.py` before evaluating or revising the skill yourself.** Use the provided script; don't write boutique HTML. The whole point is getting examples in front of the human as fast as possible

### Updating an existing skill

The user may be asking you to update an existing skill rather than create a new one. If so:

- **Preserve the original name.** Note the skill's directory name and `name` frontmatter field and use them unchanged. If the installed skill is `research-helper`, output `research-helper.skill` (not `research-helper-v2`)
- **Copy to a writable location before editing.** The installed path may be read-only. Copy to a temp directory, edit there, and package from the copy
- **When packaging manually, stage in a temp directory first**, then copy to the output location — direct writes may fail on permissions

## Reference Files

The `agents/` directory holds instructions for specialized subagents. Read them when you need to spawn the relevant one:

- `agents/grader.md` — how to evaluate assertions against outputs
- `agents/comparator.md` — how to do a blind A/B comparison between two outputs
- `agents/analyzer.md` — how to analyze why one version beat another

The `references/` directory has additional documentation:

- `references/schemas.md` — JSON structures for evals.json, grading.json, and friends
- `references/agent-cli.md` — configuring the agent adapter: preset list, custom command templates, where the probe skill gets installed, and per-CLI differences

## Bilingual Versions

This skill follows the bilingual skill-repository rules, and **bilingual is the default output** (see "Language: Bilingual by Default, User Overrides" above); both versions are independently usable. What follows covers organization, priority, synchronization, and distribution. Where these rules conflict with the skill-authoring instructions above, **follow the authoring instructions for skill implementation** while preserving the bilingual requirements below.

### 1. Language Structure

Every skill repository MUST use the following directory structure:

```text
skill-name/
├── zh-CN/
│   └── skill-name/
│       ├── SKILL.md
│       ├── scripts/
│       ├── references/
│       └── assets/
│
├── en-US/
│   └── skill-name/
│       ├── SKILL.md
│       ├── scripts/
│       ├── references/
│       └── assets/
│
├── README.md
```

- `zh-CN/`: Simplified Chinese version.
- `en-US/`: American English version.
- Both language directories MUST contain an independently usable skill.
- Both versions MUST use the same skill name.
- Optional directories SHOULD only be created when needed.
- Do **not** generate `LICENSE` or `.gitignore` for a skill. A skill is a capability package; licensing and ignore rules belong at the repository level, and dropping them into every skill directory just pollutes the install artifact. Add them only when the user explicitly asks.

### 2. Development Priority

Simplified Chinese is the primary development language.

1. ALWAYS create and develop the Simplified Chinese version first.
2. Complete implementation, verification, and revision of the Chinese version before translating it.
3. Create or update the American English version based on the verified Chinese version.
4. NEVER independently introduce functionality or behavioral changes in the American English version.
5. Do not delay Chinese development while preparing the American English version.

### 3. Content Synchronization

The two language versions MUST maintain functional and behavioral consistency.

- Keep instructions, workflows, constraints, permissions, and safety requirements equivalent.
- Keep scripts, assets, templates, and other functional resources synchronized.
- American English wording MAY be adapted for natural readability without changing meaning.
- Any functional change to the Chinese version MUST trigger an English synchronization review.
- Bug fixes and security updates MUST be reflected in both versions.
- Never silently remove or weaken requirements during translation.

Evaluate per language as well: write test prompts in the target users' language, and treat results as valid only for that language version. A Chinese pass rate says nothing about the English version — real phrasing, terminology, and edge cases differ. Functional assertions (file structure, field names, script behavior) can usually be shared across both; qualitative feedback and trigger evals must not be.

### 4. Metadata and Versioning

Each `SKILL.md` MUST retain the standard Agent Skills metadata requirements.

Use identical skill names and version numbers across both languages.

Language metadata SHOULD be declared as follows:

Chinese:

```yaml
metadata:
  language: zh-CN
```

American English:

```yaml
metadata:
  language: en-US
```

Both versions MUST use the same version number when version metadata is maintained.

### 5. Independence and Dependencies

- Each language version MUST be independently installable and distributable.
- Never reference files across language directories.
- All resource references MUST use paths relative to the corresponding skill directory.
- Do not require users to download both language versions.
- Do not duplicate shared functional dependencies outside the individual skill directories.
- Do not put repository-level files such as `LICENSE` or `.gitignore` inside a skill directory — they play no part in running the skill and only clutter the install artifact.

### 6. README and Publishing

- The repository-level `README.md` SHOULD provide an overview and clearly identify both language versions.
- Publish each language version as an independent skill directory.
- The publishing process MUST preserve the skill directory structure.
- Do not assume that every Agent automatically discovers nested language directories.
- Verify the target Agent's skill discovery and installation behavior before publishing.

### 7. Rule Precedence

These rules govern bilingual organization, language priority, synchronization, and distribution only.

The dedicated skill-authoring instructions remain responsible for skill design, content creation, formatting, and validation.

When conflicts arise, follow the dedicated skill-authoring instructions for skill implementation, while preserving the bilingual requirements defined here.

---

Repeating the core loop once more for emphasis:

- Figure out what the skill is about
- Draft or edit the skill (bilingual by default; the language the user asked for when they asked)
- Run an agent-with-the-skill on the test prompts
- With the user, evaluate the outputs:
  - Generate `benchmark.json` and run `eval-viewer/generate_review.py` so the human can review
  - Run the quantitative evals
- Repeat until you and the user are satisfied
- Sync both language versions, package the final skill, and hand it to the user

If you have a TodoList or similar, add these steps to it so nothing gets lost.

Good luck.
