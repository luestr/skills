# Bucket Audit and Template Sync

Source: the operating rules from the `scoop-audit` and `scoop-bucket-sync` versions, the actual structure of ScoopInstaller/BucketTemplate, and the real contents of the `bin/` wrappers.

## Contents

- [Audit (read-only)](#audit-read-only)
- [Report format](#report-format)
- [Repair matrix](#repair-matrix)
- [Wrapping up after the audit](#wrapping-up-after-the-audit)
- [Template drift detection](#template-drift-detection)
- [Which differences are not drift](#which-differences-are-not-drift)
- [Classifying and handling drift](#classifying-and-handling-drift)
- [Verification after syncing](#verification-after-syncing)

---

## Audit (read-only)

One command runs every check and prints a single table:

```powershell
pwsh -NoProfile -File tools/audit.ps1                 # full (downloads, slow)
pwsh -NoProfile -File tools/audit.ps1 -Offline        # lint + checkautoupdate only
pwsh -NoProfile -File tools/audit.ps1 <app>           # a single app (for re-verifying after a fix)
```

Internally it combines:

| Check | Command | Notes |
|---|---|---|
| Outdated | `checkver * -s` | Lists outdated only, writes nothing back |
| Hash mismatch | `checkhashes` | **Downloads every url**, on the order of minutes |
| schema + rules | `tools/lint.ps1` | Fields, hash shape, style |
| autoupdate consistency | `tools/checkautoupdate.ps1` | Whether autoupdate.url can reproduce the static url |
| Source reachability | `tools/checksources.ps1` | Whether upstream still exists |

Without this set of scripts, use the equivalent combination: `checkver * -s` + `checkhashes` + this skill's `scripts/manifest-lint.ps1` (offline field/hash/autoupdate checks).

**Do not** run the underlying scripts one at a time and then add your own analysis on top — the report is authoritative as a single unified table; otherwise you will miss items or do the work twice.

**You must use `pwsh`, not `powershell`**: Windows PowerShell launched from a pwsh session inherits PS7's `PSModulePath`, and PS7's `Microsoft.PowerShell.Utility` shadows the 5.1 module of the same name, so `Get-FileHash` simply does not exist.

An app without checkver (because upstream has no trackable version, with the reason written in `##`) is that way by design and is not a problem; the only update signal for such an app is a change in hash.

---

## Report format

Group by check, keep the scripts' original wording, and omit empty sections.

```markdown
## Bucket Health Report

### Outdated
| App | Change |
|-----|--------|
| feishu | 7.20.0 -> 7.21.5 |

### Hash mismatches
| App | Detail |
|-----|--------|
| uu | Mismatch found |

### Lint / autoupdate / sources
| App | Check | Level | Detail |
|-----|-------|-------|--------|
| adobe-creative-cloud-cleaner-tool | lint:hash-missing | error | top level: a url has no hash |
```

`warn` / `autoupdate:skip` are informational and go after the errors. When the script outputs `audit: no problems found`, just say "no problems found" and stop — do not hunt for problems that are not there.

---

## Repair matrix

**The fixes are not interchangeable**; getting them wrong decides whether the manifest ends up repaired or quietly destroyed.

| Check | Fix | Notes |
|---|---|---|
| `outdated` | `bin/checkver.ps1 <app> -u` | Rewrites version / url / hash |
| `hash` mismatch | `bin/checkhashes.ps1 <app> -Update`, or `checkver <app> -u -f` | The latter is more thorough |
| `lint:hash-missing` / empty hash | `scripts/hashurl.ps1 <url>`, then write it in by hand | See the next section |
| other `lint:*` | Fix per the rules in `manifest-reference.md` | Field order, indentation, SPDX, single-element arrays written as a string, etc. |
| `autoupdate:mismatch` | Edit `autoupdate` so the template can reproduce the static `url` | Most often a `$version` snuck into the static url, or the version number is wrong |
| `source:*` / checkver no longer matches | Report it to the user; a human has to judge the upstream redesign | Do not guess at a new regex |

### Three boundaries you must remember

1. **A hash error at the same version cannot be fixed by `checkver -u`.**
   When `checkver.ps1` sees the version has not changed, it prints the version and then `continue`s; it never reaches the autoupdate step at all.

2. **An empty hash takes a different code path and is easy to fall through.**
   The branch condition in `checkhashes.ps1 -Update` is `if ($current.manifest.url -and $current.manifest.hash)` — an empty string is falsy, so it drops into the `architecture` branch, whose first line is:

   ```powershell
   $platforms = ($current.manifest.architecture | Get-Member -MemberType NoteProperty).Name
   ```

   If the manifest has no `architecture` block at all (very common for single-architecture packages with a top-level `url`/`hash`), calling `Get-Member` on `$null` throws immediately and the hash stays exactly as it was. So under the combination "empty hash + no architecture block", `checkhashes -Update` cannot help; you have to compute the hash with `hashurl.ps1` and write it in by hand.

   With an `architecture` block, an empty hash does reach the write-back logic, but the number of entries to write per section is inferred from the old hash's `.Count` (an empty string has a `.Count` of 1), so multi-architecture manifests easily end up misaligned and you still have to check the result by hand.

   `URLS and hashes count mismatch` is a different error: the `url` array and the `hash` array have different lengths. Fix the lengths.

3. **When an app is both outdated and mismatched, the order is**: `checkver -u` first, then `checkhashes -Update` for whatever is still wrong.

---

## Wrapping up after the audit

1. Fix items one by one, **pasting the output of each step as you go**.
2. After fixing an app, re-run that app's checks: `pwsh -NoProfile -File tools/audit.ps1 <app>`.
3. When `checkver -u` fails (the regex no longer matches, say), **stop and report**, stating clearly that human intervention is needed — do not work around it.
4. Once everything is fixed, ask the user: run `.\bin\formatjson.ps1` to normalize formatting? Stage + commit the changed files?
5. When committing, stage only the paths actually changed this time — do not casually `git add .`; the working tree usually holds unrelated work in progress.

---

## Template drift detection

```powershell
pwsh -NoProfile -File .claude/skills/scoop-bucket-sync/scripts/template-drift.ps1
# or use the version shipped with this skill (parameterized, no dependency on an in-repo path)
pwsh -NoProfile -File <skill>/scripts/template-drift.ps1 -RepoRoot 'C:\path\to\bucket'
```

Behavior:

1. Refresh a shallow clone of `ScoopInstaller/BucketTemplate` in a temp directory (default `%TEMP%\opencode\scoop-template`);
2. Print the template HEAD's `git log --oneline -1`;
3. List the files the template has that this repo is **missing** or has **different contents** for;
4. List the files this repo has that the template **lacks** (`Extra`);
5. Print a unified diff for each differing file.

Only **git-tracked** files are compared, so untracked build artifacts like `repomix-output.xml` never enter the report. `bucket/` and `deprecated/` are excluded — they are this repo's manifests and are never supposed to match the template.

**Read the commit subject of the template HEAD**: it usually states upstream's current policy outright (for example `ci: use pinned actions`), which explains why a given diff appeared. Skip that line and you will read a policy change as noise.

Write tooling scripts in PowerShell. Scoop's Pester-style tests require **every non-YAML file to be CRLF**, while a bash script with CRLF fails silently (drift filters stop matching, `bucket/` lines leak), so a single `.sh` helper cannot satisfy both sides.

---

## Which differences are not drift

These are deliberate customizations in this repo. **Do not "fix" them**:

| Difference | Why it belongs to this repo |
|---|---|
| `bin/auto-pr.ps1` hardcodes `<owner>/<bucket>` (instead of a placeholder) | The default branch may not be `main`; this is the only place that needs a repo-specific value filled in |
| `Scoop-Bucket.Tests.ps1` passes `-BucketPath $PSScriptRoot` | scoop core's `test/Import-Bucket-Tests.ps1` declares that parameter with the same name and the same default, so they are compatible |
| `.gitignore`, `README.md` | Bucket-specific content |
| No `bucket/app-name.json.template` | Manifest creation is covered by the authoring track of the `create-scoop-manifest` skill |
| No `deprecated/.gitkeep` | That directory holds real manifests |
| Extra `docs/`, `CLAUDE.md`, `.claude/`, `tools/` | Repo-local assets; `tools/` holds this repo's own maintenance scripts, while `bin/` stays a pure copy of the template |
| Extra `repomix-output.xml` | Already gitignored; untracked files do not participate in the comparison |
| `deprecated/scripts/` never appears | Excluded together with `deprecated/` |

The test: a difference earns its own row only when it **carries repo-specific value** or **guards against a failure the template cannot catch for this repo**. Otherwise, take the template's version.

Counterexample: a guard against `"hash": ""` was once considered for Excavator and rejected — the schema test in `bin/test.ps1` already fails on an empty hash, so that drift buys nothing.

Never add files to `bin/`; new helpers always go in `tools/`.

---

## Classifying and handling drift

Classify before touching anything, because the cheap items will bury the one that actually matters.

### 1. Pinned vs floating action refs

A digest or tag (with a `# vX.Y.Z` comment) is upstream policy. `@main` works today and breaks silently later. **Follow upstream: go back to pinning.**

### 2. Stale action versions

Bump only the `uses:` line, and keep the trailing version comment accurate. A comment saying v7.0.1 while the digest belongs to v6.0.2 is the classic copy-paste accident — `gh api repos/<o>/<r>/commits/<tag> --jq .sha` exposes it on the spot.

### 3. Workflow structure

An `if:` that decides **whether the entire job runs** must go on the job, not on a step: a step-level condition still spins up a `windows-latest` runner for every event matching `on:`. This is exactly why upstream merged the `issue_comment` handler into `pull_request.yml`; a separate workflow file plus a step-level guard looks like the same behavior, but it is drift.

### 4. Scaffolding

Issue template config, `.yaml` schema hints, template JSON, and the like. Cheap — copy the whole thing.

### Handling principles

- **Prefer copying whole files**; do not merge by hand:
  ```powershell
  Copy-Item <template>\.github\workflows\x.yml .github\workflows\x.yml -Force
  ```
- After copying, **backfill the repo-specific values** (currently only `bin/auto-pr.ps1`).
- Workflow files that upstream deleted because their contents were merged elsewhere: delete them outright.
- When a wrapper (`checkver.ps1`, `checkhashes.ps1`, `checkurls.ps1`, `formatjson.ps1`, `missing-checkver.ps1`) differs, **copy the template file** instead of editing it.

---

## Verification after syncing

```bash
actionlint .github/workflows/*.yml
for f in .github/workflows/*.yml .github/ISSUE_TEMPLATE/config.yml; do
  yq eval '.' "$f" >/dev/null || echo "BAD $f"
done
gh api repos/<owner>/<repo>/commits/<tag> --jq .sha   # must equal the digest you pinned
```

Then run `template-drift.ps1` again and confirm only the items in the "which differences are not drift" list above remain.

### Commit

```text
ci: Sync workflows and tooling with BucketTemplate
```

The body lists each behavior change and its reason, one per line. Stage the tooling paths by name (`git add -- .github/... bin/auto-pr.ps1`) — this tree frequently holds unrelated work in progress on `CLAUDE.md`, `.claude/skills/*`, and `bucket/*.json`, and none of that may ever be staged or reverted.

**Commit only, do not push.**

### Responsibility boundaries

- Manifest health → the audit track (the first half of this document)
- Creating a manifest → §B of this skill (the authoring track)
- Tooling and workflows → this section
