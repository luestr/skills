# Git capabilities Grit lacks (v0.5.x)

Basis: the command index at <https://grit-scm.com/docs/>, the Grit repository's `AGENTS.md` (including its "What we drop" list), and hands-on testing of the v0.5.2 binary.
Bottom line first: **grit is a deliberately minimal subset of Git.** What it guarantees is compatibility of *on-disk formats and wire protocols*, not of argv;
each common action keeps one path and everything else is left to `git`. For everything in this list, falling back to `git` is by design, not a workaround.

## The three rules that decide "should I use git?"

1. **Need to touch only part of the work?** Partial commits, partial staging, unstaging, picking through the index — grit has no staging-area workflow. Use git.
2. **Need to rewrite existing history?** amend, rebase, revert, force push, filtering — grit never does any of it. Use git.
3. **Need finer control?** Filtering and ranges for diff/log, options for merge/pull/push, clone depth, remote management — grit's commands take almost no options. Use git.

Conversely, the everyday loop — see status → commit everything → create/switch branches → merge → fetch/pull/push → tag — is fully covered, with friendlier output for both humans and machines.

## 1. Staging and restoring the working tree

| Git capability | grit | Fallback |
| --- | --- | --- |
| `git reset` (unstage; `--soft/--mixed/--hard` to move history back) | Absent | `git reset` / `git reset --hard <commit>` |
| `git restore [--staged] [--source]` | Absent | `git restore --staged <file>`, `git restore <file>` |
| `git clean -fd` (delete untracked files) | Absent | `git clean -nd` to preview, then `git clean -fd` |
| `git rm --cached` (stop tracking, keep the file) | Absent | `git rm --cached <file>`; note a plain file deletion is recorded as a deletion by the next `grit commit` |
| `git mv` (rename) | Absent | Rename on disk; `grit status` shows `added` + `deleted` (no rename detection observed on v0.5.2) and `grit commit` records it as usual; detecting the rename in history is git's job (`-M`/`--follow`) at display time |
| `git add -p/-i` (interactive staging) | Absent | `git add -p` |
| **Partial commits** (`git commit <paths>`, committing only some changes) | **Absent**: `grit commit` always commits everything | `git add <paths> && git commit -m "…"`, or `git commit -m "…" -- <paths>` |
| `git stash push/pop/list/apply/-u` | Absent | `git stash`; to switch branches with uncommitted changes grit's switch/merge/pull/pick refuse, so the safe path is `git stash` → switch → `git stash pop` (when the changes do not conflict, `git checkout`/`git switch` can also switch directly) |
| `git checkout -- <file>` / `git checkout <commit> -- <file>` (file-level checkout) | Absent | `git checkout <commit> -- <file>` / `git restore` |
| `git update-index` / `read-tree` / `symbolic-ref` and other index plumbing | Absent | Use git (grit exposes no index-level operations) |

## 2. History rewriting

| Git capability | grit | Fallback |
| --- | --- | --- |
| `git commit --amend` | Absent | `git commit --amend` (safe while unpushed) |
| `git rebase` (incl. `-i`, `--onto`, `--autosquash`, `--continue/--abort`) | Absent | All of it goes to git; after rewriting, syncing needs a force push, also git |
| `git revert` | Absent | `git revert <commit>` |
| `git cherry-pick` for multiple commits / ranges / `-n` / `--continue` | **Partial**: `grit pick` handles one non-merge commit with no options | Use `git cherry-pick` for multiples or control; prefer `grit pick` for the everyday single commit |
| `git commit --fixup/--squash` | Absent | git |
| `git filter-repo` / `filter-branch` / `replace` (bulk rewriting) | Absent | git |
| Syncing after a rewrite (requires force push) | **Absent**: grit push never overwrites | `git push --force-with-lease` (safer than `--force`) |

## 3. Merging, conflicts and integration

| Git capability | grit | Fallback |
| --- | --- | --- |
| **Resolving merge conflicts** | **Absent** — the official path is to use git: on conflict, merge/pull/pick error out with exit 1 and leave the working tree untouched | `git merge <branch>` → edit conflict files → `git add` → `git commit`; then carry on with grit |
| `git merge --squash/--no-ff/--ff-only/--no-commit/-m/-s/-X` | No options at all | git |
| `git merge --abort/--continue` | Not needed: a failed grit merge leaves no half-finished state | If a git merge is left mid-flight: `git merge --abort` |
| `git mergetool` / `git rerere` | Absent | git |
| `git pull --rebase/--ff-only/--no-rebase` | No options at all (always ff or a merge commit) | git |
| Integrating via rebase instead of merge | Absent | git |

## 4. Remotes and pushing

| Git capability | grit | Fallback |
| --- | --- | --- |
| **Force push** (`-f`, `--force-with-lease`) | **Absent**: grit push never overwrites remote commits | `git push --force-with-lease` (confirm nobody else pushed first) |
| Push refspecs, `--all`, `--mirror`, `--delete`, pushing a single tag, pushing under a different name | Absent: `grit push` takes no arguments and only pushes "current branch → same name on the configured remote", or `--tags` (all tags) | git; you can redirect the destination with `grit config branch.<name>.remote/merge`, but renames and multi-branch pushes need git |
| `git push -u/--set-upstream` | No upstream concept: grit uses `branch.<name>.remote`/`branch.<name>.merge`; pulling/merging a remote-tracking branch adopts it as upstream (JSON `result: "set_upstream"`) | `grit config` or `git push -u` |
| `--dry-run`, `--atomic`, `--no-verify`, `-o/--push-option` | Absent | git |
| `git fetch --all/--prune/refspec/--depth` | Absent: `grit fetch [<remote>]` takes one remote, defaults to origin, and **never cleans up** remote branches deleted upstream | `git fetch --prune` to drop stale remote-tracking branches |
| `git remote remove/rename/set-url/get-url/show/prune/update` | Absent: only list and add | git |
| `git ls-remote` (inspect remote refs without downloading) | No CLI (grit-lib has ls-remote in its network layer) | `git ls-remote <url>` |
| `git submodule`, submodule clone/update | Absent | git |
| `git credential fill/approve/reject` | Absent | git (grit only stores/looks up through `credential.helper`) |

## 5. Inspection, search and debugging

| Git capability | grit | Fallback |
| --- | --- | --- |
| `git blame` | Absent | git |
| `git grep` | Absent | `git grep` / `rg` |
| `git bisect` | Absent | git |
| `git reflog` (recovering from mistakes) | No CLI (grit-lib has reflog read/write) | `git reflog` — **check it first after a mistaken delete/reset**, with `git fsck` if needed; restore with `git branch <name> <oid>` |
| `git describe` | Absent | git |
| `git log` filtering and formats: `--all`, `--graph`, `-p/--stat`, `--author/--grep`, `--since/-n`, ranges `A..B`, path filters, `--follow` | **Absent**: `grit log` is fixed at 10 per page with only `--before` to advance | git (even `--json` gives you only `commits[]` + `next`, no ranges or filters) |
| `git diff --staged/--cached`, two-commit/range diffs, `--stat/--name-only`, path filters | **Absent**: `grit diff` offers only "all uncommitted changes (staged and unstaged merged)" or "one commit vs its first parent" | `git diff --cached`, `git diff A..B -- <path>`; for just the file list use `grit diff <commit> --json --filter '.files[].path'` |
| `git show` with `-p/--stat/--name-only`, viewing blob/tree contents | **Partial**: `grit show` gives the message plus a per-file insertion/deletion summary | Use `grit diff <commit>` for the content; `git cat-file` for raw objects |
| `git rev-parse` / `rev-list` / `merge-base` / `name-rev` | No CLI (grit-lib has revparse/revwalk/merge base) | git |
| `git cat-file` / `hash-object` / `ls-files` / `ls-tree` / `show-ref` / `for-each-ref` / `count-objects` / `verify-pack` | No CLI | git |
| `git range-diff` | Absent | git |
| `git shortlog` (commits summarised per author) | **Different semantics**: `grit shortlog` lists the commits ahead of the target | `git shortlog -sn` for the per-author summary |
| `git check-ignore` / `check-attr` | Absent | git |

## 6. Branch and tag details

| Git capability | grit | Fallback |
| --- | --- | --- |
| `git branch -m/-M` (rename), `-c/-C` (copy) | Absent | git |
| `git branch -u/--set-upstream-to`, `--unset-upstream` | Absent | `grit config branch.<name>.remote/merge`, or git |
| `git branch -a/-r` (remote branches), `-v` (details), `--merged/--contains`, `--sort/--format` | Absent: `grit branch` lists local branches only | git |
| `git switch --detach`, `git checkout <commit>` (detached checkout) | Absent: grit only switches between branches | git; note `grit commit` then fails on the detached HEAD, while `grit log/diff/status` still work |
| `git switch -f/--discard-changes`, `--merge`, `--orphan` | Absent | git |
| `git tag -a -m` (annotated), tagging an arbitrary commit, `-f`, `-l` patterns, `-v` verification, pushing one tag | Absent: `grit tag` creates **lightweight** tags at HEAD only, and can list/delete | git creates annotated tags; `grit push --tags` will publish them along with everything else |
| Deleting a remote branch/tag | Absent (no `--delete` on push) | `git push origin --delete <branch>` |

## 7. Repository maintenance and worktree management

| Git capability | grit | Fallback |
| --- | --- | --- |
| `git gc` / `prune` / `repack` / `pack-refs` / `maintenance` | No CLI | git (grit-lib reads/writes packs, midx and commit-graph, but exposes no command) |
| `git fsck`, `verify-pack` | No CLI (grit-lib has fsck) | git |
| `git worktree add/list/remove/lock` | No CLI (grit-lib supports worktrees) | git |
| `git submodule` | Absent | git |
| `git sparse-checkout`, partial clone (`--filter`) | Absent | git |
| Git LFS | Unsupported (no LFS in the command surface or capability list) | Use `git` + git-lfs for anything involving LFS (pulling/pushing large files) |
| `git notes` | No CLI (grit-lib has notes) | git |
| `git bundle create/verify/unbundle` | No CLI (grit-lib has bundles) | git |
| `git apply`, `git am` (applying patches) | Absent | git |
| Hook management, `--no-verify`, `core.hooksPath` | No CLI options (grit-lib has a hooks layer) | git |
| `SHA-256` object-format repositories (`init --object-format=sha256`) | No such option (`grit init` targets SHA-1 repositories) | git |
| `git replace` / object namespaces / alternates management | No CLI | git (reading alternates via env vars is supported) |

## 8. Configuration

| Git capability | grit | Fallback |
| --- | --- | --- |
| `--system` / `--local` / `--worktree` / `--file` / `--blob` scopes | Absent: only repository (default) and `--global` | `git config --system/--file …` |
| `--add` / `--replace-all` / `--unset-all` (multi-valued keys) | Absent: one value, or `--unset` | git |
| `--get-regexp` / `--get-all` / `--show-origin` / `--show-scope` / `-z` | Absent | git |
| `--type=bool/int/…` validation, `--edit` | Absent | git |

## 9. Clone and init options

| Git capability | grit | Fallback |
| --- | --- | --- |
| `git clone --depth/--shallow-since`, `--single-branch`, `--branch`, `--bare`, `--mirror`, `--filter`, `-o`, `--no-checkout`, `--recurse-submodules` | No options: `grit clone <url> [dir]` | Use git to clone when you need these (grit works fine on the result afterwards, shallow clones included) |
| `git init --initial-branch`, `--template`, `--separate-git-dir`, `--shared`, `--object-format` | Absent: the first branch is always `main` and the only option is `--bare` (the documented `--ref-format` belongs to main, absent in v0.5.2) | git |

## 10. Present in grit but narrower or different

Easy to misuse — not "missing", but "not the same":

| Command | Difference |
| --- | --- |
| `grit checkout` / `co` | An **alias for `switch`**: branches only; not git's file checkout, and no detached checkout |
| `grit add` | Stages everything, or pre-stages by path; **cannot unstage or interactively pick** (and `commit` re-stages everything) |
| `grit commit` | Commits everything; message required; no amend, no hook options, no `--no-verify` |
| `grit diff` | No `--staged`, no path/range arguments |
| `grit log` | Fixed 10 per page + `--before`; no filters, no `-p`, no ranges |
| `grit shortlog` | "Commits ahead of the target", not git's per-author summary |
| `grit branch` | List/create/delete only; no rename, no upstream, no remote branches |
| `grit merge` / `grit pull` | No options; conflicts not resolved |
| `grit push` | No arguments, no force, no refspec; destination decided by `branch.<name>.remote/merge` |
| `grit tag` | Lightweight tags at the current HEAD only |
| `grit config` | Read/write/list/remove, repository-level and `--global` only |
| `grit status` | No options, but a complete `--json` shape (`staged`/`unstaged`/`untracked`/…) |

## 11. grit-lib only (no CLI)

These exist as library APIs but have **no** grit command. Programs can use the library (see [grit-lib.md](grit-lib.md)); otherwise use git:

stash (read/write), reflog (read/write), notes, bundles, fsck, worktrees, hooks, patch-ids, multiple packs / multi-pack-index / commit-graph, the reftable ref backend, pack and protocol internals (upload-pack/receive-pack exist as hidden commands), revparse/rev-list/merge-base, ls-remote.

## 12. Permanently dropped (never coming back — use git)

The Grit project's `AGENTS.md` ("What we drop") states these get **no CLI and no further work**:

- `archive`;
- the email workflow: `am`, `format-patch`, `send-email`, `imap-send`, `request-pull`;
- foreign-VCS bridges (`svn`, `hg`, `p4` and friends);
- `daemon`, `instaweb` and other peripheral tools;
- a second Git-compatible CLI (`grit-git` was removed) — do not expect grit to grow git-shaped subcommands.

## Notes for when you fall back to git

- **Mixing is fine**: grit and git operate on the same repository (same index, object store, config and refs); git's changes show up in grit immediately and vice versa.
- **grit is the conservative one**: with uncommitted changes, grit's `switch`/`merge`/`pull`/`pick` refuse, while git allows them — the safe way to switch with changes in flight is `git stash` → switch → `git stash pop` (when the changes do not conflict with the target branch, `git checkout`/`git switch` can also switch directly).
- **When recovering from a mistake, check `git reflog` first**: branches deleted with `grit branch -D` and work lost to `git reset --hard` may still be recoverable.
- **The canonical conflict loop**: grit reports the conflict (tree untouched) → `git merge <branch>` → resolve → `git add` + `git commit` (or `git merge --continue`) → keep using grit to push.
- **After rewriting history**: having done it with git, syncing needs `git push --force-with-lease`; nothing on the grit side needs compensating.

Sources: command coverage from the index at <https://grit-scm.com/docs/> and v0.5.2 testing; the "permanently dropped" and library-boundary claims from the repository's <https://github.com/gitbutlerapp/grit/blob/main/AGENTS.md>.
