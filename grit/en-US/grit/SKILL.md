---
name: grit
description: "Whenever a task involves version control (status, committing, creating or switching branches, merging, pushing, pulling, tagging, diffing, reading history) and grit may be installed, consult this skill first — especially before doing anything Grit deliberately does not do (partial commits, unstaging, history rewriting, force push, conflict resolution): read references/git-gaps.md and pick the right tool. Use the Grit CLI (grit-scm.com, a modern Git client rewritten in Rust) for repository inspection, commits, branches, merges, cherry-picks, remote sync and tags, with the --json/--filter contract for scripts and agents — plus a complete list of Git capabilities Grit lacks and the fallback for each. Supported Grit versions: 0.5.x (calibrated against v0.5.2; the command surface can differ between patch versions, so trust your local `grit --help`)."
---

# Grit Skill

Grit is a Rust implementation of Git, made of two parts: **`grit`** (a modern, minimal CLI) and **`grit-lib`** (a linkable Rust library).
It shares on-disk formats, wire protocols and config files (`~/.gitconfig`, `.git/config`) with Git, but its command set is a **deliberately minimal subset**:
every common action gets one obvious path, and its argv and messages are *not* meant to mirror Git.

**Supported versions: 0.5.x.** This document is calibrated against **v0.5.2** by hands-on testing; the command surface can differ between patch versions, so trust your local `grit --help`.
Before you start, check the environment: `grit --version`. The online docs (grit-scm.com/docs) track the main branch and may describe commands that are not released yet (see "Version differences").

## Six rules (measured, and the most common traps)

1. **Everything gets committed; there is no partial commit.** Every `grit commit` stages and records *all* working-tree changes — modified, deleted and untracked files. `grit add <path>` only pre-stages/previews; the following `grit commit` re-stages everything anyway. To commit only some files you must use `git` (see [references/git-gaps.md](references/git-gaps.md)).
2. **A commit message is mandatory and there is no editor.** Use `grit commit "message"` or `-m "message"`; without one, it stages your changes and then errors out. On a detached HEAD, `grit commit` fails outright (`HEAD is detached; grit commit needs a branch`).
3. **Uncommitted changes block branch operations.** `switch`, `merge`, `pull` and `pick` all refuse to run with any uncommitted change (or an untracked file in the way) and exit 1. Commit before switching — including WIP, as a commit: grit has no `stash`.
4. **Conflicts are not resolved.** When `merge`/`pull`/`pick` hits a conflict it reports the files, exits 1, and leaves the branch **and working tree exactly as they were** (no half-finished state); the official path is to redo the merge with `git merge <branch>`, fix and commit. There is no `--abort` to run because nothing was changed.
5. **Machines always read `--json`.** stdout carries exactly one JSON value; failures are `{"error": "..."}` with a non-zero exit code, and stderr carries only progress and human hints. `--filter` (a jq-like expression) requires `--json`; multiple results come back as one array. Exit codes: `0` success, `1` command failed, `2` usage error (no JSON error object in that case).
6. **Falling back to `git` for missing capabilities is by design.** git and grit can freely work on the same repository (same index, object store, config and refs); whatever git changes, grit sees immediately. Do not force grit to do reset/rebase/force push — check [references/git-gaps.md](references/git-gaps.md) first.

## Version differences: docs ≠ the v0.5.2 binary

- **Actually available in v0.5.2**: `init` `clone` `remote` `log` `diff` `show` `status` `shortlog` `add` `commit` `branch` `switch` `merge` `pick` `fetch` `pull` `push` `tag` `auth` `update` `config` `manager`, plus the hidden `upload-pack` and `receive-pack`; global options `--json`, `--filter`, `-h`, `-V`.
- **Aliases**: `status`=`st`, `shortlog`=`sl`, `switch`=`co`=`checkout` (`grit checkout` switches branches only; it is not git's file checkout or detached checkout).
- **In the docs but not in v0.5.2** (they belong to unreleased main): `grit skill`, `grit completions`, the global `--markdown`, and `grit init --ref-format` (reftable). Calling them yields `unrecognized subcommand` or `unexpected argument` (exit 2). Run `grit --help` first if you need them.
- **Documented but not effective on v0.5.2** (measured): `commit.gpgsign` signing (commits still succeed, unsigned) and cloning *from* a shallow source (`grit clone` fails with `object not found`). Handle both by v0.5.2's actual behaviour.

## Task cheat sheet

| Task | Command |
| --- | --- |
| See where you are (the default command) | `grit` / `grit status` / `grit st` |
| Init / clone | `grit init [--bare] [path]`; `grit clone <url> [dir]` |
| Commit everything | `grit commit "message"` (`-am` is accepted for git habits; same effect) |
| Uncommitted diff / a commit's diff | `grit diff`; `grit diff <commit>` (no `--staged`, no pathspec) |
| History (10 per page) | `grit log`; next page `grit log --before=<oid>` |
| Commits ahead of the target | `grit shortlog` / `grit sl` |
| Inspect a commit/branch/tag | `grit show [object]` |
| Create / switch branches | `grit switch -c feature`; `grit switch main`; `grit branch <name>` (create only) |
| Merge | `grit merge <branch>` (also accepts `origin/main`) |
| Copy one commit | `grit pick <commit>` (single-commit cherry-pick) |
| Remotes | `grit remote add origin <url>`; `grit fetch [remote]`; `grit pull`; `grit push`; `grit push --tags` |
| Tags (lightweight, at HEAD) | `grit tag v0.1`; `grit tag -d v0.1` |
| Sign in to GitHub (HTTPS) | `grit auth`; sign out with `grit auth logout` |
| Config (same files as git) | `grit config [--global] <key> [value]`; `--list`; `--unset <key>` |

## Reference index (load on demand — do not read everything at once)

| File | Contents | Read when |
| --- | --- | --- |
| [references/commands.md](references/commands.md) | Per-command syntax, key options, behaviour boundaries and JSON fields | You are unsure how a command works or what it emits |
| [references/automation.md](references/automation.md) | The `--json`/`--filter` contract, exit codes, non-interactive checklist, credentials, usable env vars, JSON recipes | Writing scripts/automation, running unattended, debugging blocks or auth |
| [references/git-gaps.md](references/git-gaps.md) | The full list of Git capabilities Grit lacks (9 missing-capability categories, plus narrower-semantics, library-only and permanently-dropped sections) + fallback commands | **Mandatory** before partial commits, unstaging, history rewriting, force push, conflict resolution, blame/rebase/stash, etc. |
| [references/workflows.md](references/workflows.md) | Task recipes: first push, daily loop, sync, merge, cherry-pick, release, conflict recovery, git fallbacks, automation loop | Executing an end-to-end task — copy the commands |
| [references/grit-lib.md](references/grit-lib.md) | Embedding grit-lib in a Rust program, with a module map | The task needs programmatic Git access from Rust |

## Minimal loop (the five most-used steps)

```console
$ grit --version                      # confirm it exists; use git if it does not
$ grit                                # where you are: branch, ahead count, changes, next-step hint
$ grit commit "Add the greeting"      # commit everything (message required)
$ grit push                           # push the current branch to the same name on origin
$ grit pull                           # when push is rejected, pull first (ff or a Merge commit)
```

Detailed recipes and failure handling live in [references/workflows.md](references/workflows.md).
