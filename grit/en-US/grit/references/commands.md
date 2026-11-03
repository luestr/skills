# Grit command reference (v0.5.x)

A quick lookup for every `grit` command: syntax, behaviour boundaries, JSON output.
Field-level details come from your local `grit <command> --help` and the per-command pages at <https://grit-scm.com/docs/>; entries marked "main" are not in v0.5.2.

## Invocation and global options

```text
grit [OPTIONS] [COMMAND]
```

| Item | Notes |
| --- | --- |
| Bare `grit` | Same as `grit status`; `--json` works here too |
| `--json` | stdout carries exactly one JSON value; failures are `{"error": "..."}` with a non-zero exit code |
| `--filter <EXPR>` | jq-like expression, requires `--json`; multiple results become one array; an invalid expression emits `{"error": ...}` |
| `-h` / `--help`, `-V` / `--version` | Help and version; `--version` prints a version line (e.g. `grit 0.5.2`) even with `--json`, producing no JSON |
| `--markdown` | **main only, absent in v0.5.2** |

Aliases: `st` = `status`; `sl` = `shortlog`; `co` / `checkout` = `switch`.
Repository discovery matches Git (supports `GIT_DIR`, `GIT_WORK_TREE`, `GIT_CEILING_DIRECTORIES`, and more).

## Repositories and configuration

### grit init

```text
grit init [--bare] [<path>]
```

- Creates the target directory if needed; without a path it initializes the current directory; the first branch is always `main`.
- The only option is `--bare`. The documented `--ref-format <files|reftable>` (reftable ref backend) belongs to main; passing it to v0.5.2 yields `unexpected argument` (exit 2).
- JSON (v0.5.2): `initialized`, `path`, `bare`, `branch` (**no** `ref_format`).

### grit clone

```text
grit clone <url> [<dir>]
```

- Accepts `https://`, `http://`, `ssh://`, `user@host:path`, `git://`, `file://` and local paths; a local path is stored as an absolute path.
- The remote is always saved as `origin`; the remote's default branch is checked out; the destination must not exist or must be empty.
- Cloning *from* a shallow source fails on v0.5.2 (`object not found`); use git for the shallow clone and let grit take over the result. Private GitHub over HTTPS needs `grit auth` first.
- JSON: `url`, `path`, `branch`. **No** `--depth` / `--branch` / `--bare` etc. (use git when you need depth control).

### grit config

```text
grit config [--global] <key>            # read
grit config [--global] <key> <value>    # write
grit config [--global] --unset <key>    # remove
grit config [--global] --list           # list
```

- Reads and writes the exact same files as Git: `<repo>/.git/config` and the per-user `~/.gitconfig`; settings made with either tool apply to both.
- Reads cascade (repository over global); writes default to the repository level, `--global` writes the user level; reading or removing an unset key is an error (exit 1).
- Scopes beyond these two (`--system`, multi-value `--add`, etc.) do not exist — use git.
- Keys grit uses (as documented): `user.name`, `user.email`, `target.branch`, `branch.<name>.remote`, `branch.<name>.merge`, `credential.helper`, `grit.githubClientId`, `receive.denyNonFastForwards`, `receive.denyDeletes`, `receive.denyCurrentBranch`; the signing keys `commit.gpgsign`/`gpg.*`/`user.signingkey` are **not effective on v0.5.2** (see the commit section).
- JSON: `action` (`get`/`set`/`unset`/`list`); `get`/`set` carry `key`, `value`; `list` carries `entries[]`.

### grit status (default command; alias st)

```text
grit
grit status
grit st
```

Top to bottom: where you are (branch + how far ahead of the target and those commits, up to 10; `no commits yet` on an unborn branch; the commit when HEAD is detached) → **Staged** → **Changed (not staged)** → **Untracked** → a next-step hint.
Change labels (documented values): `new`, `modified`, `deleted`, `renamed`, `copied`, `type changed`, `conflict`; in practice a file rename (including `git mv`) shows as `added` + `deleted`, with `renamed` never observed.

**Target resolution order**: `target.branch` setting → `origin/master` → `origin/main` → `master` → `main`.

No options at all. JSON fields: `branch` (null when detached), `detached`, `head`, `target`, `ahead`, `commits[]` (`oid`/`subject`, up to 10), `staged[]`, `unstaged[]` (each with `path`/`status`), `untracked[]`, `clean`.

### grit auth

```text
grit auth          # GitHub device-flow sign-in, stores a token
grit auth logout   # remove the stored token
```

- Prints a URL and a short code; after you approve in the browser it stores the token through `credential.helper`; on Windows with no helper it uses the built-in `grit manager` (Windows Credential Manager).
- Elsewhere configure one first: `grit config --global credential.helper osxkeychain|libsecret|store`.
- Custom OAuth app: env var `GRIT_GITHUB_CLIENT_ID` or the `grit.githubClientId` setting.
- JSON: `authenticated`/`logged_out`, `host`; `logged_out` is false when there is no helper to store into.

## Committing

### grit add

```text
grit add [<path>...]
```

- No paths = stage everything (modified, deleted, untracked); with paths, stage only those files/directories.
- Paths are relative to the current directory; `../` and repo-absolute paths work; a path matching nothing is an error (exit 1).
- **Note**: `grit commit` re-stages everything, so `add` does not determine what gets committed — it is for pre-staging and inspection.
- **There is no unstage/reverse patch** (no `git reset`, `git restore --staged`, or `add -p`).
- JSON: `staged` (number of paths staged by this invocation).

### grit commit

```text
grit commit [-a] <message>
grit commit [-a] -m <message>
```

- **Always commits every working-tree change** (modified, deleted, untracked); `-a` exists only so git habits like `-am` keep working.
- The message is required (positional or `-m`, not both); a multi-line message's first line is the subject; **no editor is opened and there is no `$GIT_EDITOR` path**.
- Author/committer come from `user.name`/`user.email`; `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` fix the recorded time.
- **Signing is not effective on v0.5.2**: the docs describe `commit.gpgsign` (OpenPGP/X.509 via `gpg`/`gpgsm`, SSH via `ssh-keygen -Y sign`), but with it set to true a commit still succeeds and the object carries no `gpgsig` header. Use git when you need signed commits.
- Fails when: nothing to commit; HEAD is detached; no message.
- **No** `--amend`, no `--no-verify`, no partial/path-limited commits.
- JSON: `oid`, `branch`, `subject`, `changes`.

### grit diff

```text
grit diff [<commit>]
```

- No argument: every uncommitted change in the working tree (staged and unstaged are shown **together**; there is no staged-only view). With an argument: the change that commit introduced, against its first parent.
- `<commit>` can be a full/short oid, a branch, a tag, or an expression like `HEAD~2`.
- Each file starts with its path, each hunk with its position; two line-number columns (before/after); colour on a TTY with intra-line emphasis, `-`/`+` marks when output is not a terminal or `NO_COLOR` is set; three lines of context; binaries listed but not shown.
- **No** `--staged`/`--cached` (both exit 2), no path filter, no two-commit/range diff (use git for those).
- JSON: `files[]`, each with `path`, `status`, `binary`, `hunks[]` (`old_start`/`new_start`, `lines[]` with `kind` (`context`/`add`/`del`) and line numbers, `segments[]` with optional `emphasis`).

## Reading history

### grit log

```text
grit log [--before <commit>]
```

- Commits reachable from HEAD, newest first, **10 per page**; each line shows the short oid, the author (the part before `@`, or the name when there is no email), the time, and the subject; when more history exists the last line gives `→ more: grit log --before=<oid>`.
- Only `--before` for paging; no `--all`/`--graph`/`--author`/`--grep`/`-p`/path filter/range (use git).
- An empty repository (no commits) errors with `could not list commits from HEAD` (exit 1); works on a detached HEAD.
- JSON: `commits[]` (`oid`/`subject`, ≤10), `next` (full oid for the next page, or null).

### grit shortlog (alias sl)

```text
grit shortlog
```

- Lists **all** commits on the current branch that the target does not have (not limited to 10), plus the target name.
- Target resolution is the same as `status`.
- Note this is **semantically different** from git's `shortlog`: git summarises commits per author; grit lists what is ahead of the target.
- JSON: `branch`, `target`, `ahead`, `commits[]` (`oid`/`subject`).

### grit show

```text
grit show [<object>]
```

- Shows a commit's id, author, date and full message, then a summary of the files it changed with insertion/deletion counts; no argument means HEAD.
- `<object>` accepts an oid, an expression, a branch or a tag; when you name a branch/tag the first line shows the name; for an **annotated tag** the tag's own author, date and message come first.
- For the full change a commit made, use `grit diff <commit>`.
- JSON: `kind` (`commit`/`branch`/`tag`/`annotated_tag`), `ref_name` (omitted when you passed a raw id), `tag` (annotated tags), `commit` (`oid`/`parents`/`author`/`committer`/`subject`/`message`), `stat` (`files[]`/`files_changed`/`insertions`/`deletions`).

## Branches and merging

### grit branch

```text
grit branch
grit branch <name>
grit branch -d <name>
grit branch -D <name>
```

- No arguments lists local branches, marking the current one with `*`.
- `<name>` creates a branch at the current commit (**without switching**; use `grit switch -c` to create and switch in one step).
- `-d` deletes, refusing when the branch has commits not merged into the current one (it tells you to use `-D`); you cannot delete the branch you are on.
- **Name validation is only partial (measured on v0.5.2)**: structurally broken names (e.g. a trailing `/`) are refused (`invalid ref: refusing to update ref with bad name`), but names git considers invalid — containing spaces or `..`, ending in `.lock`, or the reserved `HEAD` — were created successfully in testing. To keep refs git-compatible, validate names yourself against `git check-ref-format --branch`, or create the branch with git.
- **File/directory conflicts**: a branch `feature` and a branch `feature/login` cannot coexist (whichever is created second fails with `cannot lock ref … non-empty directory … blocking reference`), exactly like git's files backend.
- **No** rename (`-m`), no upstream, no remote-branch listing, no `-v` details.
- JSON: `action` (`list`/`create`/`delete`); `list` carries `current`, `branches[]` (`name`/`current`); `create` carries `name`; `delete` carries `name`, `oid`, `short_oid`.

### grit switch (aliases co / checkout)

```text
grit switch <branch>
grit switch -c <branch>
```

- Switches to a local branch and updates the working tree to match; `-c` creates the branch at the current commit first (fails if it already exists).
- **Refuses to run with uncommitted changes** (staged or not; exit 1, tells you to commit first); untracked files stay put, unless the target branch has a file at the same path, in which case grit stops rather than overwrite it.
- From a detached HEAD, `grit switch <branch>` gets you back onto a branch.
- **No** `--detach`, no forced switch, no file-level checkout (use git for `git checkout -- <file>`).
- JSON: `branch`, `created`.

### grit merge

```text
grit merge <branch>
```

- Three outcomes: already contains everything (`up_to_date`, nothing changes) → fast-forward (`fast_forward`, no new commit) → a real merge (records a commit whose message is `Merge <branch>`, with CLI output `Merged <branch> into the current branch (<oid>)`).
- `<branch>` may be a local branch or a remote-tracking branch such as `origin/main`; local branches are looked up first.
- **On conflict**: lists the conflicting files, exits 1, and leaves the branch and working tree exactly as they were; grit does not resolve conflicts — redo the merge with `git merge <branch>` (the official instruction).
- Refuses to run: with uncommitted changes, on a branch with no commits, on a detached HEAD, or when an untracked file would be overwritten.
- **No options at all** (no `--squash`/`--no-ff`/`--abort`/`-m`).
- JSON: `result` (`up_to_date`/`fast_forward`/`merged`/`set_upstream`), `branch`, `oid`, `upstream`.

### grit pick

```text
grit pick <commit>
```

- Applies the change `<commit>` made onto the current branch as a new commit (single-commit cherry-pick); **keeps the original author and message**.
- `<commit>` accepts an oid, a branch name (picks the commit at its tip), or an expression like `feature~2`.
- Refuses (changing nothing): uncommitted changes / branch with no commits / detached HEAD; the target is a merge commit; the change is empty or already on the current branch; a conflict; an untracked file would be overwritten.
- **No** multi-commit or ranges, no `-n`, no continue/abort (use git).
- JSON: `source`, `oid`, `subject`.

## Remotes and publishing

### grit remote

```text
grit remote
grit remote add <name> <url>
```

- No arguments lists remotes and their URLs; `add` creates one (fails if the name exists).
- URLs accept everything `clone` accepts (https/ssh/git/file/local path).
- `clone` adds `origin` for you.
- **No** `remove`/`rename`/`set-url`/`get-url`/`show`/`prune` (use git).
- JSON: `action` (`list`/`add`); `list` carries `remotes[]` (`name`/`url`); `add` carries `name`/`url`.

### grit fetch

```text
grit fetch [<remote>]
```

- Downloads everything new from a remote, updating remote-tracking branches (e.g. `origin/main`) and new tags; **your own branches and working tree are left alone**.
- The remote defaults to `origin`; each updated ref is listed with old → new oid.
- Works inside Git-made shallow clones (measured): `grit fetch` respects the existing shallow boundary while updating remote-tracking branches and new tags.
- **No** `--prune` (stale remote-tracking branches are not cleaned)/`--all`/refspec/`--depth` (use git).
- JSON: `remote`, `updates[]` (`ref`/`old_oid`/`new_oid`; `old_oid` is null for a new ref, `new_oid` null for a removed one), `updated`.

### grit pull

```text
grit pull
```

- = fetch + integrate the remote branch for the current branch: fast-forward when you have no new commits, a merge commit when both sides do, and simply adopting the remote's on a branch with no commits yet.
- Remote: `branch.<name>.remote` (default `origin`); branch: `branch.<name>.merge` (default the same name).
- Like `merge`: refuses with uncommitted changes or a detached HEAD; on conflict it changes nothing (exit 1).
- **No options at all** (no `--rebase`/`--ff-only`, etc.).
- JSON has the same shape as `merge`.

### grit push

```text
grit push
grit push --tags
```

- **No arguments**: pushes the current branch to `origin` under the same name (creating it if needed); there is no `-u`/upstream concept and no refspec.
  - Redirect it with `grit config branch.<name>.remote <remote>` and `branch.<name>.merge <ref>`.
- **Never overwrites remote commits**: when the remote has commits you lack, the push is rejected (exit 1; JSON has `rejected: true`, `status: "rejected"` and a `reason`) and tells you to `grit pull` first; **there is no force push**.
- `-t`/`--tags`: pushes all local tags instead of the current branch.
- If a GitHub-over-HTTPS push fails because you are not signed in, grit offers to run `grit auth` and retries.
- JSON: `remote`, `branch` (or `--tags`), `results[]` (`ref`/`status`: `ok`/`up_to_date`/rejected), `rejected`.

### grit tag

```text
grit tag
grit tag <name>
grit tag -d <name>
```

- No arguments lists tags; `<name>` creates a **lightweight** tag at the **current commit** (HEAD; no message of its own); `-d` deletes.
- Name validation is partial, the same as for branches (see above): names git rejects may still be accepted; validate with `git check-ref-format refs/tags/<name>` when you need git compatibility. Deleting a missing tag is an error.
- Tags are local until published with `grit push --tags`.
- **No** annotated tags (`-a`/`-m`), no tagging another commit, no `-f` overwrite.
- JSON: `action` (`list`/`create`/`delete`); `list` carries `tags[]` (`name`/`oid`); `create` carries `name`/`oid`.

## Maintenance and internal commands

| Command | Notes |
| --- | --- |
| `grit update` | Re-runs the official install script to replace the running binary (Unix `curl \| sh`, Windows PowerShell). **Do not call from unattended jobs** unless you intend to upgrade. |
| `grit manager` | Windows credential helper (Windows Credential Manager). Plumbing; no `--json`. |
| `grit upload-pack` / `grit receive-pack` | Smart-protocol servers for fetch/push over stdin/stdout (run by ssh and grit-http-server). Plumbing; **no `--json`**; do not wrap them as JSON commands. |
| `grit skill` / `grit completions` | **main only, absent in v0.5.2**: print the built-in SKILL.md / generate completion scripts. |

## Command coverage at a glance

| Git capability | grit status |
| --- | --- |
| status / commit / log / show / branch / switch / merge / cherry-pick / tag / remote sync | Present (narrower — see the "No" notes above) |
| `reset`, `restore`, `clean`, `rm`, `mv`, `stash`, `apply` | Absent |
| `rebase`, `revert`, `commit --amend`, `filter-repo` | Absent |
| `blame`, `grep`, `bisect`, `reflog`, `describe` | Absent |
| `gc`, `prune`, `repack`, `fsck`, `worktree`, `submodule`, `notes`, `bundle`, LFS | Absent |
| force push, refspec, `push -u`, `remote set-url`, `fetch --prune` | Absent |
| annotated tags, `branch -m`/`-u`, `switch --detach`, `diff --staged` | Absent |

The complete list, grouped into categories with per-item fallbacks, is in [git-gaps.md](git-gaps.md).
