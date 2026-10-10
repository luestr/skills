# Workflow recipes (v0.5.x)

Every recipe is a runnable command sequence with expected output and failure branches.
Shared preconditions: `grit --version` is available; an author identity is set (`grit config --global user.name/user.email`, shared with git).

## 1. Brand-new project → first push

```console
$ grit init project && cd project
$ grit config --global user.name "Ada Lovelace"     # once; git shares it
$ grit config --global user.email ada@example.com
$ echo "# Notes" > README.md
$ grit commit "Start the project"                   # everything, untracked files included
$ grit remote add origin https://github.com/<user>/<repo>.git
$ grit push                                         # creates the remote branch and pushes
```

For a private HTTPS repo run `grit auth` first; for SSH use `git@github.com:<user>/<repo>.git` and let ssh handle auth.

## 2. The daily loop (inside an existing repo)

```console
$ grit st                            # 1. status: branch, ahead count, changes, next-step hint
$ grit switch -c feature/login       # 2. create + switch (refused if you have uncommitted changes — commit first)
$ ...edit files...
$ grit diff                          # 3. review the full uncommitted change
$ grit commit "Add login form"       # 4. commit everything
$ grit push                          # 5. push to the same name on origin
$ grit show                          # 6. re-read the last commit's message and change summary
```

## 3. Syncing with a remote (the standard rejected-push flow)

```console
$ grit push
  rejected origin refs/heads/main: not a fast-forward — run `grit pull` first
$ grit pull                          # fast-forward, or a Merge commit
$ grit push
```

Notes:

- To see the difference first: `grit fetch`, then `grit status --json --filter '{branch, ahead, target}'` and `grit diff origin/main`.
- If `pull` reports a conflict, **it changed nothing**. Finish it with recipe 7.
- Pushing a branch somewhere else (not origin / not the same name): `grit config branch.main.remote upstream` and `grit config branch.main.merge refs/heads/main`.

## 4. Merging a branch (and cleaning up)

```console
$ grit switch main
$ grit merge feature                 # one of: Fast-forwarded feature → <oid> / Merged feature into the current branch (<oid>) / Already up to date
$ grit branch -d feature             # deletes when merged; (was <oid>) is printed
$ grit shortlog                      # confirm what the branch is now ahead by
```

If `-d` says `not fully merged` but you are sure: `grit branch -D feature` (recover a mistaken delete via `git reflog` / `git fsck`).

## 5. Copying a single commit (cherry-pick)

```console
$ grit log --json --filter '.commits[].subject'      # find the target first
$ grit pick 9a1c2e0                                  # or grit pick feature (its tip commit)
$ grit show --json --filter '{subject: .commit.subject, author: .commit.author}'
```

`grit pick` keeps the original author and message. It refuses — changing nothing — when the target is a merge commit, the change already exists, or there is a conflict; handle the last two with recipe 7.

## 6. Releasing and tagging

```console
$ grit tag v0.2                      # lightweight tag at the current HEAD
$ grit push --tags                   # publishes ALL local tags (not just v0.2)
$ grit tag                           # verify the list
```

For annotated tags (`-a -m`) or tagging a historical commit, use `git tag`; `grit push --tags` will still publish them.

## 7. Conflicts: grit refuses → git finishes → back to grit

```console
$ grit merge topic
error: merge has conflicts in:
  README.md

Nothing was changed. grit can't resolve conflicts yet — run `git merge topic` to resolve them.

$ git merge topic                    # redo it on the untouched tree
$ ...edit the conflict files...
$ git add README.md
$ git commit                         # or git merge --continue
$ grit st                            # back to normal; keep using grit
```

Why it is safe: on conflict grit leaves the branch **and working tree exactly as they were**, so `git merge` never runs into a half-finished state. `pull` and `pick` behave the same way.

## 8. Partial commits / unstaging / switching with WIP (git fallbacks)

grit commits everything, so these need git — and grit sees the results immediately:

```console
# Commit only some files
$ git add src/login.rs && git commit -m "login only"

# Unstage a file you staged by mistake
$ git restore --staged src/other.rs

# Discard working-tree changes to a file
$ git restore src/scratch.rs

# Switch branches with uncommitted changes (grit switch refuses)
$ git stash push -u -m wip
$ grit switch main                   # or git switch
$ git stash pop
```

## 9. Force push or history rewriting (git fallbacks)

```console
$ git commit --amend                 # amend the last commit
$ git rebase -i origin/main          # or any rebase / revert / filter-repo work
$ git push --force-with-lease        # grit push never overwrites; this must be git
```

`--force-with-lease` beats `--force`: it refuses when the remote has new commits from someone else, so you cannot silently clobber their work.

## 10. The agent automation loop (non-interactive, decidable)

```console
# 0. One-time setup, done in an interactive session: grit auth; confirm credential.helper
# 1. Self-check
$ grit --version
$ grit status --json --filter '{branch, clean, detached}'

# 2. Commit if there is anything to commit (message required; for deterministic timestamps set GIT_AUTHOR_DATE/GIT_COMMITTER_DATE)
$ grit status --json --filter .clean
$ grit commit "Automated change: <what>" --json --filter .oid

# 3. Push and handle rejection (exit 1 + rejected=true)
$ grit push --json --filter '{rejected, results}'
$ grit pull                                   # on rejection, pull; a conflict means hand off to a human/git
$ grit push

# 4. Unattended hardening (SSH remotes; PowerShell shown, use export in Bash)
PS> $env:GIT_SSH_COMMAND = "ssh -o BatchMode=yes"
```

Judge by JSON fields, never by human text; do not treat `grit manager`/`upload-pack`/`receive-pack` as JSON commands.
Details (blocking flows, exit codes, credentials) are in [automation.md](automation.md).

## 11. The quick inspection combo

```console
$ grit                                  # where am I, how far ahead, what changed
$ grit shortlog                         # the full list of commits ahead of the target
$ grit diff                             # the full uncommitted change
$ grit diff HEAD~1                      # what the previous commit changed
$ grit log                              # last 10; follow the hint to page with --before
$ grit log --json --filter '.commits[].subject'
$ grit show v0.1                        # the commit a tag points at
$ grit diff v0.1 --json --filter '.files[].path'   # that commit's file list
```

On long histories remember: `grit log` is fixed at 10 per page — loop with `--before` for bulk history, or switch to `git log`.
