---
name: create-scoop-manifest
description: >
  Create and maintain Scoop bucket manifests (appname.json inside a bucket directory) for Windows apps, plus the
  install, verification, health-check and troubleshooting work that surrounds them.
  Use this skill whenever the user says "create a scoop manifest", "write a manifest for that app",
  "add this to my bucket", "submit a PR to scoop-extras / main / versions", "write checkver /
  autoupdate", "is this app packaged yet / how do I install it", "the packages in my bucket are
  outdated / the hash is wrong / audit this bucket", "sync with BucketTemplate / bump GitHub
  Actions", or "scoop errors out / won't install / extraction fails / missing hash / package not
  found / downloads are slow" - even if they never say the word "scoop".
  Trigger on anything involving Windows app manifests (NSIS .exe / MSI / portable .zip), bucket
  repositories, portable software installation, or Scoop's own configuration and troubleshooting.
  Projects that only ship macOS/Linux artifacts are out of scope.
metadata:
  language: en-US
---

# Scoop Manifest

Scoop is the command-line package manager for Windows: it installs into your user directory, needs
no admin rights, leaves no registry debris, keeps PATH clean, and resolves dependencies. Scoop
itself is a pile of PowerShell scripts - **what gets installed and how is entirely described by the
JSON manifest in a bucket**, which is why manifest authoring and maintenance are this skill's centre
of gravity.

**Core mental model:** Linux-style package management (the `apt-get` / `brew` equivalent), except the
package definition is plain JSON that you can write, host and maintain yourself.

## Three tracks - decide which one you're on first

| What the user wants | Track | Entry point |
|---|---|---|
| **Write a manifest for an app, add it to a bucket, submit a PR** | **B - authoring (primary)** | §B below |
| **Audit, repair, or template-sync an existing bucket** | **C - maintenance (primary)** | §C below |
| Install software, set up an environment, update, uninstall, switch versions, proxy, global install | A - using Scoop (supporting) | §A below |

§B and §C are the body of this skill. §A carries only the usage knowledge you need while authoring
and maintaining manifests - you cannot verify a manifest you wrote without being able to
`scoop install` it, `scoop update`, and read what `scoop info` prints.

Decide by asking whether the user has a bucket repository. Yes → B or C. No, they just want software
installed → A.

---

# §A Using Scoop: install and daily management

## A1 Prerequisites (fix these before installing anything)

- PowerShell 5.1+ (`$PSVersionTable.PSVersion` at least 5.1). PowerShell 7 is better and also works
  around the antivirus false positive on `get.scoop.sh` under 5.1.
- Language Mode must be `FullLanguage`; ExecutionPolicy must be `RemoteSigned`, `Unrestricted` or
  `ByPass`.
- **Install from a non-admin PowerShell.** Installation from an elevated console is disabled by
  default for security; you must opt in with `-RunAsAdmin`.

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
```

Default location is `C:\Users\<username>\scoop`. Custom directories, global directory, cache
directory, proxy, CI, silent install and admin install are all covered in
`references/install-and-setup.md`.

## A2 First thing after installing

```powershell
scoop install git 7zip
scoop bucket add extras
```

`git` is a hard dependency for adding buckets (without it `scoop bucket add` fails outright); `7zip`
unpacks the vast majority of packages; `innounp` and `dark` handle InnoSetup and WiX installers.
`scoop checkup` verifies these plus NTFS, long paths and Developer Mode for you.

## A3 Everyday commands (full option list in `references/cli-reference.md`)

| Task | Command |
|---|---|
| Install | `scoop install <app>` (`-g` global, `-i` skip dependencies, `-k` bypass cache, `-s` skip hash check, `-a <arch>` pick architecture) |
| Install a specific version | `scoop install <app>@<version>` |
| Install from a URL or local file | `scoop install <url-or-path>.json` |
| Uninstall | `scoop uninstall <app>` (`-p` also removes persisted data) |
| Update Scoop itself + manifests | `scoop update` |
| Update one / all apps | `scoop update <app>` / `scoop update *` |
| List installed | `scoop list [query]` |
| Search | `scoop search <keyword>` (no argument lists everything; the query is a regex unless the sqlite cache is on) |
| Show details | `scoop info <app>` (`-v` shows full paths and URLs) |
| See what's outdated | `scoop status` (`-l` local only, no network) |
| Remove old versions | `scoop cleanup *` (`-k` also clears stale downloads) |
| Clear the download cache | `scoop cache rm *` |
| Pin a version | `scoop hold <app>` / `scoop unhold <app>` |
| Switch versions | `scoop reset <app>@<version>` (only between **already installed** versions) |
| Backup / restore | `scoop export > scoopfile.json` (`-c` includes config) / `scoop import scoopfile.json` |
| Find a shim's real path | `scoop which <cmd>` |
| Open the homepage | `scoop home <app>` |
| Show dependency order | `scoop depends <app>` |

Also available: `alias` (custom subcommands), `cat` (print a manifest), `create` (interactive manifest
generation), `download` (download into the cache and verify hashes without installing), `prefix`
(print the install path), `shim` (add/rm/list/info/alter), `virustotal` (look up a hash or URL),
`cache show|rm`, `checkup`.

## A4 Three user-level rules that keep biting people

1. **`scoop status` is only as fresh as your local buckets.** It compares the installed version
   against the *local* manifest, so without `scoop update` it reports stale information. `scoop
   update` is also auto-triggered every 3 hours during install/update/download/virustotal.
2. **Multiple versions coexist via `reset`, not reinstall.** `scoop install python python27` then
   `scoop reset python27` switches; `scoop reset python` returns to the newest installed version.
   `scoop list` only shows the newest version - `scoop info <app>` is what lists them all.
3. **`current` is a directory junction, not a real directory.** Every external tool (file
   associations, IDEs, shortcuts) must point at `apps\<app>\current\...` - never at a version
   directory, and never at a shim (see the Open With section of `references/troubleshooting.md`).

## A5 Common configuration (`scoop config`, stored in `~/.config/scoop/config.json`)

```powershell
scoop config proxy currentuser@default          # system proxy with the current Windows credentials
scoop config proxy 127.0.0.1:7890               # anonymous, explicit proxy
scoop config rm proxy                           # bypass the system proxy
scoop install aria2; scoop config aria2-enabled true
scoop config aria2-warning-enabled false        # silence the aria2 nag
scoop config use_sqlite_cache true              # speeds up search/shim
scoop config use_external_7zip true             # use the 7z on PATH
scoop config no_junction true                   # stop using the current alias
scoop config default_architecture 64bit
scoop config gh_token <token>                   # avoids checkver rate limits, reaches private repos
scoop config debug true                         # turn on when troubleshooting
```

Every setting (`scoop_branch`, `root_path`, `global_path`, `private_hosts`, `use_isolated_path`,
`ignore_running_processes`, and the rest) is documented in `references/cli-reference.md`.

## A6 Bucket basics

A bucket is a Git repository full of JSON manifests. `main` ships with Scoop. Known community
buckets: `extras` `versions` `nirsoft` `sysinternals` `php` `nerd-fonts` `nonportable` `java`
`games`; run `scoop bucket known` for the authoritative list.

```powershell
scoop bucket add extras                                          # known bucket, no URL needed
scoop bucket add my-bucket https://github.com/<user>/my-bucket    # custom bucket
scoop bucket list
scoop bucket rm <name>
```

---

# §B Authoring: write a manifest

Scoop installs apps from `bucket/<appname>.json`. The goal is a version-pinned manifest with working
`checkver` + `autoupdate`, so Scoop tracks new releases forever after without anyone hand-editing
`version`/`url`/`hash`.

**Decide whether this is even possible first.** The project must publish a Windows binary (NSIS
`.exe`, MSI, portable `.zip`/`.7z`) behind a stable URL (usually GitHub Releases). Projects that only
ship macOS/Linux artifacts are not a Scoop candidate - say so and stop.

Complete field reference (license forms, architecture blocks, persist, psmodule, shortcuts,
installer): `references/manifest-reference.md`. Every checkver strategy, every hash extraction mode,
every substitutable variable: `references/autoupdate-reference.md`.

## B1 Probe the source - never guess URLs

```bash
gh repo view <owner>/<repo> --json url,description,licenseInfo -q '{homepage:.url, description:.description, license:.licenseInfo.spdxId}'
gh api repos/<owner>/<repo>/releases/latest --jq '{version:.tag_name, assets:[.assets[]|{name,size,browser_download_url,digest}]}'
```

For non-GitHub sources: `curl ... | jq` for JSON endpoints, `curl ... | htmlq "a[href*='.exe']"
--attribute href` for download pages. You need the version (**strip any leading `v`**), the Windows
asset names (split by 64bit/arm64/32bit), the homepage, the description, and the license.

For Node/Electron projects also read `package.json`: `build.productName`,
`build.win.executableName`, and the `build.win.artifactName` template. Other ecosystems: look at
`Cargo.toml`, `pyproject.toml`, `*.spec`, `installer/`.

## B2 Get version / URL / sha256 - without downloading the artifact

Every GitHub release asset carries a `digest: sha256:<hex>` field, and **that is the hash Scoop
wants**. Downloading a 500 MB installer just to hash it is the single biggest waste of time in this
workflow.

```bash
node <skill>/scripts/fetch-windows-assets.mjs <owner>/<repo> [tag]
# equivalent implementation when node is not installed
pwsh -NoProfile -File <skill>/scripts/fetch-windows-assets.ps1 <owner>/<repo> [tag]
```

It prints the tag, the version with `v` stripped, and each Windows asset's URL / size / sha256.
Non-GitHub sources have no digest, so download once and hash it:
`<skill>/scripts/hashurl.ps1 <url>`.

## B3 Pick the install shape (this decides the manifest)

```text
portable .zip/.7z only        -> use it directly, add extract_dir if needed   (preferred)
both .zip and NSIS .exe       -> pick the .zip
NSIS .exe only                -> two routes:
   a) silent install works    -> set installer.file + args, let Scoop run it
   b) /S pops a GUI or fails   -> pre_install + two-stage 7z extraction (see references/installers-and-extraction.md)
MSI                           -> do not write an msi block (deprecated); extract it like a zip
InnoSetup                     -> "innosetup": true, Scoop unpacks it with innounp
WiX / dark                    -> unpacked via the dark helper
```

Inspect an NSIS payload with `7z l <file>.exe`; electron-builder output reveals
`$PLUGINSDIR\app-64.7z` (the real application lives inside). A `Type = PE` report from `7z l` does
not mean it is unextractable - the embedded 7z stream is often right there in the same listing.

The `#/dl.7z` URL suffix is the cheapest escape hatch: it makes Scoop treat the installer as a 7z
archive, skipping execution and UAC entirely. The full recovery procedure for NSIS silent-install
failures (including the `$PLUGINSDIR` quoting trap, `$dir`/`$fname` scoping, and a local reproduction
harness) is in `references/installers-and-extraction.md`.

## B4 Write the JSON

Required: `version` `description` `homepage` `license` `url` `hash`. Field order, 4-space indent and
the single-element-array style rule are in `references/manifest-reference.md`.

**The one mistake that hurts most:** the static `url` uses a **literal version**, while
`autoupdate.url` uses `$version`. Get it backwards and every install 404s.

```json
{
    "version": "1.2.3",
    "description": "One-line description without the app name",
    "homepage": "https://github.com/owner/repo",
    "license": "MIT",
    "architecture": {
        "64bit": {
            "url": "https://github.com/owner/repo/releases/download/v1.2.3/app-x64.exe#/app.exe",
            "hash": "<sha256>"
        },
        "arm64": {
            "url": "https://github.com/owner/repo/releases/download/v1.2.3/app-arm64.exe#/app.exe",
            "hash": "<sha256>"
        }
    },
    "bin": "app.exe",
    "checkver": "github",
    "autoupdate": {
        "architecture": {
            "64bit": { "url": "https://github.com/owner/repo/releases/download/v$version/app-x64.exe#/app.exe" },
            "arm64": { "url": "https://github.com/owner/repo/releases/download/v$version/app-arm64.exe#/app.exe" }
        }
    }
}
```

The four source patterns (GitHub release / CDN with tokens / mirror-derived URL / signed rotating
link) each have a template in `references/autoupdate-reference.md`.

**`checkver` is bound to `homepage`.** `"checkver": "github"` reads the repository out of `homepage`,
so homepage must be the GitHub repo URL - or, when the homepage is a product site, use
`"checkver": { "github": "<repo url>" }`. Pairing a product page with `"github"` makes checkver fail
outright.

## B5 Verify - run these in order, do not skip ahead

```bash
# 0. Offline static checks: fields, hash shape, whether autoupdate.url reproduces the static url
pwsh -NoProfile -File <skill>/scripts/manifest-lint.ps1 bucket/<appname>.json

# 1. Version detection
pwsh -NoProfile -Command "cd '<bucket>'; .\bin\checkver.ps1 <appname>"

# 2. Install test
scoop install '<bucket>\bucket\<appname>.json'
<appname> --version
scoop uninstall <appname>
```

Without Scoop installed, at minimum: `node -e "require('./bucket/<appname>.json')"` plus a `curl -I`
that returns 200 on the `url`.

`checkver -u` (forced update) proves autoupdate can write back `version`/`url`/`hash`. Whether the
**hash was actually computed** is a separate question: set the hash to 64 zeros, run `checkver -f`,
and see whether it comes back as your committed value. `checkver -f` alone proves nothing - with a
correct hash it just rewrites the same value in place.

## B6 Commit

Commit message for a new manifest: `Add <appname>`. PR title formats for the public buckets, the
`/verify` comment, field ordering, and the rule that Excavator rejects version-bump-only PRs are all
in `references/bucket-workflows.md`.

---

# §C Maintenance: audit, repair, template sync

## C1 Audit (read-only, report before touching anything)

```bash
pwsh -NoProfile -File tools/audit.ps1            # full: checkver -s + checkhashes + lint + autoupdate + sources
pwsh -NoProfile -File tools/audit.ps1 -Offline   # seconds: lint + static autoupdate checks only
```

Without a local `audit.ps1`, use the equivalent combination: `checkver * -s` (outdated),
`checkhashes` (mismatches, really downloads, slow), static lint (this skill's
`scripts/manifest-lint.ps1`), and `checkver` (is the source still alive).

**Process:** run it → group the findings by check (outdated / hash mismatch / lint / autoupdate /
source) → **list the affected apps and ask before fixing** → only change anything after explicit
approval. Omit empty sections; put `warn` level rows after the errors.

## C2 Repair (the fixes are not interchangeable)

| Check | Fix |
|---|---|
| `outdated` | `bin/checkver.ps1 <app> -u` (rewrites version/url/hash) |
| `hash` mismatch | `bin/checkhashes.ps1 <app> -Update`, or `checkver <app> -u -f` |
| hash missing / empty | compute with `<skill>/scripts/hashurl.ps1 <url>` and write it by hand |
| other lint, `autoupdate:mismatch` | edit the manifest per the rules |
| `source:*` / checkver no longer matches | upstream changed; report it and let a human decide |

Three hard rules (all confirmed by experiment):

- **A hash error at the current version cannot be fixed by `checkver -u`** - it prints the version,
  sees no change, and `continue`s before ever reaching autoupdate.
- **An empty hash cannot be repaired automatically** - `checkver -u` falls into a branch that
  requires an `architecture` block, and `checkhashes -Update` hits `Get-Member` on `$null` when that
  block is absent. Compute it with `hashurl.ps1` instead.
- **Writing only `hash` and no `url` inside `autoupdate` makes `checkver -u` overwrite a correct
  hash with `""` and exit 0.** This actively destroys data, which makes it worse than an empty hash.

When an app is both outdated and mismatched: `checkver -u` first, then `checkhashes -Update` for
whatever is still wrong.

Re-run the checks for each app after fixing it. If `checkver -u` fails (regex no longer matches, say),
stop and report instead of working around it. Once everything passes, ask whether to normalise with
`formatjson.ps1` and whether to stage + commit.

## C3 Sync with BucketTemplate

```powershell
pwsh -NoProfile -File <skill>/scripts/template-drift.ps1 -RepoRoot <bucket>
# a repo that carries its own copy can use that instead
pwsh -NoProfile -File .claude/skills/scoop-bucket-sync/scripts/template-drift.ps1
```

It reports the template's HEAD commit (which states upstream's current policy, e.g.
`ci: use pinned actions`), the files that are missing or differ, and the files this repo has that the
template lacks. **`bucket/` and `deprecated/` belong to this repo and are not drift**; neither are
`CLAUDE.md`, `README`, `.gitignore`, `docs/`, `.claude/` or `tools/`.

Classify before touching anything: pinned vs floating action refs, stale action versions, workflow
structure (an `if:` that decides whether the whole job runs belongs on the job, not on a step), and
scaffolding files. Prefer copying whole files, then re-apply repo-specific values. Verify with
`actionlint`, a YAML parse, and `gh api repos/<o>/<r>/commits/<tag> --jq .sha` against the digest you
pinned. Commit with `ci: Sync workflows and tooling with BucketTemplate`, stage only the tooling
paths, and do not push.

Full rules and the "these differences must be preserved" list: `references/bucket-audit-and-sync.md`.

---

# Troubleshooting entry point

Run `scoop checkup` first, then consult `references/troubleshooting.md` (execution policy, package
not found, missing hash, extraction failures, NSIS stuck on a GUI, slow downloads, proxy auth, NTFS
requirement, long paths, Developer Mode, antivirus real-time scanning, install failures and version
conflicts, broken `current` links). Always diagnose in the order environment → package → upstream
source; never start by editing the manifest.

## Scripts and references

| File | Purpose |
|---|---|
| `scripts/fetch-windows-assets.ps1` | Version, URLs and sha256 from the GitHub Release API (no download); use this when node is unavailable |
| `scripts/fetch-windows-assets.mjs` | The same thing, Node implementation |
| `scripts/hashurl.ps1` | SHA256 for one or more URLs (strips the `#/...` fragment, sends Scoop's UA) |
| `scripts/manifest-lint.ps1` | Offline static checks: fields, hash shape, architecture pairing, autoupdate.url reproduction, named-group casing; `-Strict` promotes field ordering to errors |
| `scripts/template-drift.ps1` | Compare against ScoopInstaller/BucketTemplate |
| `assets/app-name.json.template` | Starting point for a new manifest (official field order) |
| `references/install-and-setup.md` | Every installer parameter, env vars, CI, silent install, admin install, mirrors, proxy |
| `references/cli-reference.md` | Full options for every command plus every config key |
| `references/manifest-reference.md` | Every manifest field, license forms, architecture, persist, psmodule, shortcuts |
| `references/autoupdate-reference.md` | checkver strategies, autoupdate, hash extraction modes, all variables, named-group trap |
| `references/installers-and-extraction.md` | Extraction and installer dispatch, NSIS recovery, two-stage 7z, local reproduction |
| `references/bucket-workflows.md` | Bucket creation, template CI/Excavator, PR and commit conventions |
| `references/bucket-audit-and-sync.md` | Audit report format, repair matrix, template sync details |
| `references/troubleshooting.md` | Every known failure and its fix |
