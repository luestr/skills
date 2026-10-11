---
name: archify-en
description: "Create polished, validated architecture, workflow, sequence, data-flow, and lifecycle/state diagrams as explorable standalone HTML with inline SVG, dark/light themes, optional trace motion, and PNG/JPEG/WebP/SVG/WebM export. Accept plain-language requirements or pasted Mermaid flowchart, sequenceDiagram, and stateDiagram input; inspect repository evidence when the diagram must reflect real code. Use when the user asks to visualize system architecture, infrastructure, cloud/security/network topology, technical workflows, API call sequences, request lifecycles, data pipelines, ETL/ELT, data lineage, state machines, or to convert/beautify Mermaid. Also use for everyday subjects with steps, parts, relationships, or states: a leave or travel plan, an application or approval process, a back-and-forth such as renting, where money or documents go, or where an application or order stands. Not for numeric charts or dashboards. This is the Chatlo (iOS, built-in WebKit browser) adaptation: run with bun, use only the Chatlo built-in browser, and delegate the automated browser gate to a built-in-browser review."
license: MIT
metadata:
  version: "3.0"
  author: tt-a1i
  based_on: Cocoon-AI/architecture-diagram-generator (MIT, v1.0)
  adapted_for: Chatlo (iOS, built-in WebKit browser)
  display_name: Archify (Chatlo adaptation)
  display_name_en: Archify
---

# Archify (Chatlo adaptation)

This skill is adapted from the upstream repository `tt-a1i/archify` (MIT, v3.0) for the Chatlo environment (iOS, built-in WebKit browser): always run with `bun`; use only the Chatlo built-in browser for browser work; the desktop Chrome automated browser gate, which cannot run on Chatlo, is delegated to a built-in-browser review.

Create an interactive HTML diagram from typed JSON. Static output is the default; enable motion only when requested.

## Chatlo environment adaptations (read first)

The rest of this skill matches upstream, but on Chatlo the following must be done as described here:

- **Always run with `bun`**: the CLI and renderers are zero-dependency ESM; run them with **`bun`**. Every `node bin/archify.mjs` in the commands below must be replaced with **`bun bin/archify.mjs`**. The CLI spawns its own subprocesses through `process.execPath`, so launching it with `bun` keeps the whole pipeline on `bun` with no extra setup.
- **Path to `bin/archify.mjs`**: in the commands below, `bin/archify.mjs` means the `bin/archify.mjs` in this SKILL.md's own directory. Input and output paths resolve from your working directory.
- **Browser (mandatory)**: any action that opens a page, previews a page, fetches/renders a page, automates clicks or typing on a page, takes a screenshot, reads cookies, or exports, must use **only** the Chatlo built-in browser — the `web_browser` tool (or the equivalent `chatlo-browser` command). **Do not** install, download, or run Chrome / Chromium / Firefox / Edge / Playwright / Puppeteer or any other third-party browser or engine, and do not bypass with a headless engine.
- **Automated browser evidence is unavailable on Chatlo → delegate**: the upstream `browser-check` gate launches desktop Chrome and, over the DevTools protocol, measures containment and readability at four desktop viewports. Chatlo has no Chrome, and the built-in browser viewport is fixed by the host (phone-sized). Therefore `finalize` marks the `browser-check` stage as **`delegated`** on Chatlo instead of failing: `validate → deliver → check` still all pass. You (the agent) perform the delegated browser review with the built-in browser (see "Chatlo browser review" under Delivery).
- **Temporary directory**: Chatlo mounts `/tmp` as tmpfs, which breaks the atomic-output identity checks. The CLI already switches its internal temp directory to the hostfs `/agent/tmp`. Override with `ARCHIFY_TMPDIR` or `TMPDIR` if needed.
- **Self-update checks are off by default**: upstream contacts a GitHub Pages update manifest; this skill sets `ARCHIFY_UPDATE_CHECK_DISABLED=1` by default. Do not check for or install updates. To opt in, set `ARCHIFY_UPDATE_CHECK_DISABLED=0`.
- **Do not use `preview` or `--open`**: Chatlo has no `open` / `xdg-open`, and the host `127.0.0.1` is not guaranteed reachable. After generating HTML, open the file's `chatlo:///absolute/path` with the `web_browser` tool; never display the page as plain text.
- **Output directory**: unless the user names another location, give each diagram request its own folder `.archify/<type>-<slug>-<YYYYMMDD-HHMMSS>/` (local time), or place it under `/agent/outputs/archify/<type>-<slug>-<YYYYMMDD-HHMMSS>/`. Keep `candidate.json` and `<slug>.html` in it, set `meta.output` to that relative HTML path, and reuse the folder for every repair rerun.
- **Delivering files**: to hand the HTML to the user, use `present_files`.

## Existing candidate handoff

When the user supplies a frozen candidate, run `finalize` first as one CLI invocation. Its passing receipt completes the automated gates; follow any visual review recommendation under Delivery before claiming visual quality. For repair, follow step 5 below.

`finalize` includes a bounded update check in its delivery receipt; on Chatlo that check is disabled (see Update awareness).

## Fast authoring path

Use this path for ordinary generation. Read branch references only when their stated trigger applies.

1. Choose `architecture`, `workflow`, `sequence`, `dataflow`, or `lifecycle` from the question.
2. Use the exact schema and example paths in the Type router without listing their directories. Read [Authoring defaults](references/authoring-defaults.md) and the mode's example in a bounded batch separate from project documents and complete schemas so neither is truncated; recover any missing section before writing. For Architecture, use the matching showcase example. For Sequence, Dataflow, and Lifecycle, also read the mode and common schemas. Read the relevant schema definition before choosing any new field, enum, or constrained text, especially boundary kinds. Examples teach shape, not facts. Use fresh IDs, wording, and layout. Go directly to the candidate without preliminary help, doctor, starter validation, temporary diagrams, or output-path listing. Query brands only for an explicitly requested mark; read [Brand marks](references/brand-marks.md) for an unknown mark with a user-provided URL.
3. Once the requested scope and, for a real codebase, [source evidence](references/repository-authoring.md) are covered, write the complete candidate directly without planning coordinates in prose. Choose Architecture abstraction and connected placement using Authoring defaults before coordinates: show the main user journey and necessary branches, preserve control roles and behavior-changing conditions, and leave enough room for actual relationship labels. No node, relationship, source, view, card, or boundary count is a target or ceiling. Use automatic routes first; add explicit routing only for necessary branch, return, supplied geometry, or measured repair. Set `meta.quality_profile` to `"showcase"` unless the user requests dense `standard`.
4. Once the complete first candidate is written, run `finalize` directly. Its first gate is showcase validation; successful first drafts need no separate pre-validation. Keep the candidate unchanged while the command runs:

   ```bash
   bun bin/archify.mjs finalize <type> <candidate.json> <output.html> --quality showcase --json
   ```

   For a repository-backed candidate, include evidence on the first draft and use the complete first command: `bun bin/archify.mjs finalize <type> <candidate.json> <output.html> --repo-root <repo-root> --quality showcase --json`.

   A passing receipt proves the included `validate`, `deliver`, strict `check`, and `browser-check` gates passed; on Chatlo `browser-check` shows as `delegated`. Use its compact summary; run standalone commands only for a separate request or focused failure diagnosis.

5. A non-zero exit is never success. Read compact stdout or `evidence.summaryReceipt`, then [repair the failed gate](references/delivery-contract.md#failed-finalize-and-candidate-repair), including its repair limit. Preserve requested meaning and source evidence. For several tangled Architecture routes, read [Architecture layout repair](references/architecture-layout-repair.md); for measured field or geometry failures, read [Authoring contract](references/authoring-contract.md). Edit the connected neighborhood and rerun the complete `finalize` command from step 4.

## Update awareness

`finalize` and standalone `deliver` include `update` in their receipts. **On Chatlo this check is off by default**: `update.status` is `unavailable` and `reason` is `disabled`, so keep **no** update line and do not check for or install updates. Only when the user explicitly sets `ARCHIFY_UPDATE_CHECK_DISABLED=0` should you follow upstream's update-notice convention (see `references/update-awareness.md`).

## Type router

| Type | Use for | Schema | Example |
|---|---|---|---|
| `architecture` | Components, services, cloud/security boundaries, infrastructure | `schemas/architecture.schema.json` | `examples/web-app.architecture.json`; `examples/production-deployment.architecture.json` |
| `workflow` | Processes, approval gates, tool calls, runbooks, CI/CD | `schemas/workflow.schema.json` | `examples/agent-tool-call.workflow.json` |
| `sequence` | API call chains, request lifecycles, async traces, returns | `schemas/sequence.schema.json` | `examples/cache-miss-request.sequence.json` |
| `dataflow` | Pipelines, ETL/ELT, lineage, governance, consumers | `schemas/dataflow.schema.json` | `examples/product-analytics.dataflow.json` |
| `lifecycle` | State/status transitions, retries, waiting and terminal states | `schemas/lifecycle.schema.json` | `examples/deployment-release.lifecycle.json` |

When ambiguous, run `bun bin/archify.mjs guide "<scenario>" --json`. Scenario proof examples are structural references, not facts to copy.

For an everyday subject, keep the same five modes and semantic types, then name them for the reader: use everyday `icon` values and `meta.legend` labels as in [Node icons](references/authoring-contract.md#node-icons). Ask for missing personal facts instead of inventing dates, amounts, or rules.

## Mermaid input

Read Mermaid for topology and meaning, then author fresh Archify JSON; do not mechanically render Mermaid styling.

- `flowchart` / `graph` → `workflow`, or `architecture` for a component map.
- `sequenceDiagram` → `sequence`; participants become semantic participants and arrows become messages.
- `stateDiagram` → `lifecycle`; states and transitions retain meaning, not Mermaid style.

## Delivery

Use the `finalize` command above for the first candidate and after a repair.

`finalize` stops at the first non-passing gate. Its compact stdout and `<output-stem>.finalize-summary.json` are ordinary evidence. A passing run creates no screenshots and reports `visualReview: "not-requested"`.

### Chatlo browser review

On Chatlo, `browser-check` shows as `delegated` and finalize's `visualReview` is `delegated-to-chatlo-web_browser`. When you need a visual/perceptual review, or the user explicitly asks to "take a look" or "visually check", do it with the **built-in browser**:

1. Open the produced HTML with the `web_browser` tool `open`: `chatlo:///absolute/path/<slug>.html` (add `?theme=light` / `?theme=dark`).
2. Use `web_browser` `screenshot` (add `--full-page` for long pages) or `snapshot`, then check: horizontal overflow, legend vs. bottom navigation overlap, text that is too small, and correct theme.
3. Optional: use `web_browser` `act --kind evaluate` to run the probe scripts in `references/chatlo-browser-evidence.md`.
4. Claim visual quality only after you have **actually** inspected a screenshot/snapshot; otherwise report automated checks only.

When a passing Architecture receipt reports `visualReviewRecommendation.signals.resolvedCrossovers`, copy the candidate aside and apply the hints in one edit that changes only node positions and sizes. Rerun the complete `finalize` once with `--out-dir <folder>/review-2`. If that run fails or reports more crossings, restore the copy and finalize it with `--out-dir <folder>/review-3`. Do not start a second placement round.

When `layoutReviewRecommendation.action` is `inspect-sequence-width`, follow [Sequence width review](references/delivery-contract.md#sequence-width-review) before handing off a newly authored Sequence.

`visualReviewRecommendation` is advisory. Read [Delivery contract](references/delivery-contract.md) for failed gates, standalone commands, provenance/recovery, repeated delivery, exports, or opening. Recovery follows `deliver` → strict provenance `check` → `browser-check` (on Chatlo the last stage's browser gate is delegated to the built-in browser).

For workflow viewport overflow, read [Workflow viewport repair](references/authoring-contract.md#workflow-viewport-repair) before the next layout edit.

Report artifact checks, browser evidence, captures, and actual perceptual review as **distinct** results. For an explicitly requested immediate preview or active desktop loop, see [Optional opening](references/delivery-contract.md#optional-opening) (on Chatlo, open with the built-in browser instead).

## Optional viewer capabilities

`meta.animation: "trace"` is opt-in.

Read `references/viewer-runtime.md` only when the user explicitly asks for Share Cards, Route/Reach cards, motion, deep links, presentation, search/focus, or another Viewer Runtime feature.

## Setup and fallback

No install is required inside the skill package. For setup diagnosis, verify with:

```bash
bun bin/archify.mjs doctor
bun bin/archify.mjs demo <output-directory>
```

When shell access is unavailable, hand-place architecture SVG into `assets/template.html`, use CSS semantic classes rather than inline colors, and follow the visual review contract in `references/delivery-contract.md`.

## Output

Return the checked HTML as an absolute path, diagram type, validation summary, specification/artifact receipt, browser-evidence status, and truthful visual-review status. Do not claim success for a non-zero command or claim visual inspection you did not perform.
