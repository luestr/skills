# Automation and scripting (v0.5.x)

The shared contract for programs and autonomous agents driving `grit`: JSON output, exit codes, non-interactive requirements, credentials, and documentation resources.
Per-command JSON fields are in [commands.md](commands.md) and each command's `--help`.

## The JSON contract

Always pass `--json` when something other than a human reads the result:

- **stdout**: exactly **one** JSON value — the command's outcome object on success, or `{"error": "…"}` on failure.
- **stderr**: progress lines, auth prompts, human-style `error: …` diagnostics. Parsers read stdout only.
- The process still exits non-zero on failure, so you can branch on the exit code or on the presence of an `error` key.

```console
$ grit commit --json
{"error":"provide a commit message, e.g. grit commit \"what changed\""}
```

`--filter <EXPR>` narrows the JSON in place with a jq-like expression (requires `--json`). Expressions follow jq rules: bare-name shorthand works for top-level fields only; nested values need explicit keys:

```console
$ grit status --json --filter '{branch, clean}'
$ grit status --json --filter '{b: .branch, c: .clean}'    # explicit keys work too
$ grit log --json --filter '.commits[].subject'            # several results → one JSON array
$ grit log --json --filter '.commits | length'
```

- On failure the filter runs on `{"error": "…"}`, so **the error text is replaced by the filtered result**: `grit commit --json --filter .oid` with no message prints `null` (exit 1), not the error object. With `--filter`, judge success by the **exit code**; drop `--filter` when you need the error string.
- An **invalid expression** still emits `{"error": "invalid filter …"}` (exit 1) — one of the few failure cases where an `error` key stays visible under `--filter`.
- A missing path can evaluate to `null` (still exit 0).

When any ref is rejected, `grit push` prints its full JSON result yet exits **1** (`rejected: true`) — rely on the `rejected` field when you do not use `--filter`, and on the exit code when you do.

## Exit codes

| Code | Meaning |
| --- | --- |
| 0 | Success (including jq filters that evaluate to `null` when a path is missing) |
| 1 | Command failed (missing repo, rejected push, validation error, …); with `--json`, stdout still carries `{"error": "…"}` |
| 2 | Usage error (unknown option/subcommand). clap prints help to stderr and **there is no JSON on stdout** |

```console
$ grit status --filter '.branch'   # forgot --json
error: --filter requires --json    # exit 1
```

## Colour and terminal detection

Human output is coloured only when stdout is a TTY, the environment supports ANSI, and `NO_COLOR` is unset; piping or redirecting yields plain text.
Set `NO_COLOR=1` to force plain text on a TTY. JSON mode never depends on colour — always use `--json` for machines.

## Staying non-interactive

`grit` **never opens an external editor**: `grit commit` requires a message (positional or `-m`) and there is no `$GIT_EDITOR` path. There is also no global `--yes`.

Flows that can **block on a person**, and how to avoid them:

| Area | Behaviour | How to avoid blocking |
| --- | --- | --- |
| `grit auth` | OAuth device flow: URL and code on stderr, then polls until you authorise in a browser | Run `grit auth` once in an interactive session before automating; the token goes into `credential.helper` |
| `grit fetch`/`push`/`pull` (HTTPS GitHub) | On auth failure with **stdin a TTY**, grit may ask `Sign in to GitHub now? [Y/n]` and start the device flow | Use a stored token; or ensure stdin is not a TTY so it prints a hint and exits without prompting |
| `clone`/`fetch`/`pull`/`push` over SSH | grit pipes the protocol stdin/stdout but **inherits stderr**, so the ssh child can still talk to `/dev/tty` (host-key confirmation, passphrases, ssh-askpass); `--json` does not disable this | Preconfigure keys and known_hosts; for unattended jobs set `GIT_SSH_COMMAND='ssh -o BatchMode=yes'` so SSH fails fast instead of prompting. grit resolves SSH as `GIT_SSH_COMMAND` → `GIT_SSH` → `ssh` on `PATH` (**not** `core.sshCommand`) |
| `grit update` | Runs the release installer (`curl \| sh` on Unix) | Do not call in unattended jobs unless you intend to upgrade the binary |

`grit auth logout` is non-interactive and reports whether a helper had a token to erase:

```console
$ grit auth logout --json
{"logged_out": false, "host": "github.com"}
```

## Credentials (HTTPS GitHub)

- `grit auth` uses GitHub's device flow and stores the token through your configured `credential.helper` (the same mechanism as Git).
- Override the OAuth app with the `GRIT_GITHUB_CLIENT_ID` env var or `grit config --global grit.githubClientId …`.
- Without a helper there is nowhere to store it: Windows has the built-in `grit manager`; macOS/Linux need `grit config --global credential.helper osxkeychain|libsecret|store` first.
- SSH remotes do not use the device-flow token; authentication is entirely ssh's job (mind the blocking risks above).

## Commands that cannot be JSON

`grit manager`, `grit upload-pack` and `grit receive-pack` are protocol commands (binary or line protocols on stdin/stdout) with **no `--json`** — do not wrap them as JSON commands.
`-V`/`--version` prints a version line (e.g. `grit 0.5.2`) even with `--json`, producing no JSON value.

## Useful environment variables (excerpt)

| Variable | Effect |
| --- | --- |
| `GIT_DIR`, `GIT_WORK_TREE`, `GIT_CEILING_DIRECTORIES`, `GIT_PREFIX` | Repository discovery |
| `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES` | Index and object-store paths |
| `GIT_CONFIG`, `GIT_CONFIG_GLOBAL`, `GIT_CONFIG_SYSTEM`, `GIT_CONFIG_NOSYSTEM`, `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n`/`GIT_CONFIG_PARAMETERS` | Config cascade (e.g. `GIT_CONFIG_NOSYSTEM=1` skips a broken system config) |
| `HOME`, `XDG_CONFIG_HOME`, `USERPROFILE` | Home and identity fallbacks |
| `GIT_AUTHOR_*`, `GIT_COMMITTER_*` | Author/committer name, email and **date** overrides for new objects (enables deterministic commits) |
| `GIT_SSH`, `GIT_SSH_COMMAND` | SSH transport command |
| `GIT_HTTP_LOW_SPEED_LIMIT`, `GIT_HTTP_LOW_SPEED_TIME` | HTTP low-speed abort thresholds |
| `TZ` | Local timezone when no explicit offset is given |
| `NO_COLOR` | Force plain-text output |

## JSON recipes

```console
# Is the working tree clean?
$ grit status --json --filter .clean                          # true / false

# Current branch, ahead count, target
$ grit status --json --filter '{branch, ahead, target}'
$ grit shortlog --json --filter .ahead

# Recent commit subjects
$ grit log --json --filter '.commits[].subject'
$ grit show HEAD~1 --json --filter .commit.subject

# Files changed by a commit
$ grit diff HEAD~1 --json --filter '.files[].path'

# Branch list
$ grit branch --json --filter '{action, current, branches}'
$ grit branch --json --filter '.branches[].name'

# Remotes
$ grit remote --json --filter '.remotes[].name'

# Push verdict (remember exit may be 1 too)
$ grit push --json --filter '{rejected, results}'
```

Without `--json` you get the human forms — the status screen, ten-line `grit log` pages, `grit diff`'s `-`/`+` markers. Scripts should not parse those; use JSON.

## Documentation resources for agents

| Resource | Where | Use |
| --- | --- | --- |
| llms.txt | <https://grit-scm.com/llms.txt> | Curated index of every docs page |
| llms-full.txt | <https://grit-scm.com/llms-full.txt> | Full text of all docs Markdown |
| Markdown twin | swap `index.html` for `index.md` in any page URL | One page's source, good for close reading |
| `grit skill` | built-in SKILL.md | **main only, absent in v0.5.2**; use it after upgrading — it names its own version |
| grit-lib API | <https://docs.rs/grit-lib> | Rust library reference |

## JSON stability

Command pages document the fields as a contract. With `--json`, rely on **documented top-level fields** (such as `branch`, `clean`, `rejected`);
do not depend on the wording of human text (it changes between versions), and do not depend on nested keys that are not documented.
