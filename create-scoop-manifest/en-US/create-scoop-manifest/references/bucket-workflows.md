# Bucket Workflows: Creation, CI, PRs

Sources: wiki [Buckets](https://github.com/ScoopInstaller/Scoop/wiki/Buckets), [Criteria for including apps in the main bucket](https://github.com/ScoopInstaller/Scoop/wiki/Criteria-for-including-apps-in-the-main-bucket), [CONTRIBUTING](https://github.com/ScoopInstaller/.github/blob/main/.github/CONTRIBUTING.md), and the BucketTemplate repository.

## Contents

- [What a bucket is](#what-a-bucket-is)
- [Creating your own bucket](#creating-your-own-bucket)
- [The automation BucketTemplate gives you](#the-automation-buckettemplate-gives-you)
- [Criteria for including apps in the main bucket](#criteria-for-including-apps-in-the-main-bucket)
- [The full PR submission flow](#the-full-pr-submission-flow)
- [PR title format](#pr-title-format)
- [Excavator and "no version-only PRs"](#excavator-and-no-version-only-prs)
- [The scripts directory and auxiliary files](#the-scripts-directory-and-auxiliary-files)
- [Publishing and listing](#publishing-and-listing)

---

## What a bucket is

A bucket is a Git repository containing JSON manifests. It can be a GitHub repository, or a bare Git repository on a local or network drive.

- `main` ships with Scoop and is always the default search source.
- `extras` holds GUI / non-developer tools that do not belong in main.
- `versions` holds old versions of well-known packages.
- Anyone can create their own bucket; you just have to tell people the repository URL.

`ScoopDirectory` (<https://rasa.github.io/scoop-directory/>) indexes community buckets; add the GitHub topic `scoop-bucket` to your repository and it will be picked up by the scan.

---

## Creating your own bucket

### Option 1: Use the template (recommended)

1. Open [ScoopInstaller/BucketTemplate](https://github.com/ScoopInstaller/BucketTemplate) and click **Use this template**.
2. Name it, then change the two placeholders (`<username>/<bucketname>`) as described at the bottom of the README.
3. CI, automatic updates, and issue/PR handling work out of the box.

What the template gives you is covered in the next section.

### Option 2: By hand

```powershell
git clone https://github.com/<your-username>/my-bucket
cd my-bucket
# write your first manifest
'{ "version": "1.0", "url": "https://gist.githubusercontent.com/lukesampson/6446238/raw/hello.ps1", "bin": "hello.ps1", "description": "Hello world example", "homepage": "https://example.com", "license": "MIT" }' > bucket/hello.json
# compute the hash and fill it into the hash field
git add .
git commit -m "Add hello"
git push
```

Directory convention: manifests go under `bucket/` at the repository root (when `Find-BucketDirectory` detects that `<bucket>\bucket` exists, it automatically descends one level).

### Add it and verify

```powershell
scoop bucket add my-bucket https://github.com/<your-username>/my-bucket
scoop bucket list                    # should show my-bucket
scoop search hello                   # should be listed under 'my-bucket bucket:'
scoop install hello
hello
```

### Share it

Just tell people the one line `scoop bucket add my-bucket <url>`. If you want ScoopDirectory to index it, add the topic.

---

## The automation BucketTemplate gives you

| Capability | What it does |
|---|---|
| **Continuous integration** | Runs Scoop's official tests on every commit, enforcing formatting and readability (CRLF is required for non-YAML files) |
| **Continuous delivery** | Automatically updates every manifest to its latest version every 4 hours (runs checkver -u) |
| **Issue handlers** | Automatically handles common reports such as 404s and hash verification failures |
| **Pull Request handlers** | Automatic PR validation: required fields, hash verification, CI tests |
| **`bin/` wrappers** | `checkver.ps1` / `checkhashes.ps1` / `checkurls.ps1` / `formatjson.ps1` / `missing-checkver.ps1` are 4-line forwarders to `$SCOOP_HOME/bin/`; `auto-pr.ps1` and `test.ps1` (the Pester runner) are slightly longer |

**Do not add your own files to `bin/`**. If you need a new tool, put it in `tools/` and keep `bin/` a pure copy of the template — otherwise template sync will keep reporting drift. See `bucket-audit-and-sync.md` for details.

---

## Criteria for including apps in the main bucket

An app that goes into `main` must:

- Be a **well-known developer tool** (roughly ≥500 stars and ≥150 forks for a GitHub project)
- Be the latest stable version
- Be the **full version**, not a trial
- Have a relatively standard installation method (versioned download URL, no complex pre/post scripts needed)
- **Not be a GUI**

Anything that does not qualify goes to `extras`. 32-bit-only old packages, and packages that require registration / payment, go to `nonportable` or `versions`.

---

## The full PR submission flow

### 0. Open an issue first

Apart from claiming an existing issue directly, any new change (including a new package) must start with an issue in the corresponding repository, describing the implementation details and the rationale.

> "We are very reluctant to accept random PRs that have no issue created first."

Wait until a maintainer confirms you can submit a PR, then start writing.

### 1. Claim it

Comment on the issue that you are working on it, so you do not collide with someone else. If there is already an active discussion (within 7 days) and someone is working on it, pick something else.

### 2. Branch

- Scoop core: branch from **`develop`**.
- Bucket: branch from the default branch (usually `master`).

### 3. Write the manifest and verify it locally

Read [App Manifests](https://github.com/ScoopInstaller/Scoop/wiki/App-Manifests) and [Creating an App Manifest](https://github.com/ScoopInstaller/Scoop/wiki/Creating-an-app-manifest), and write it following the rules on field order, 4-space indentation, SPDX license, and so on. Then:

1. `scoop install bucket\<app>.json` → install, run it, verify functionality and persistence, uninstall
2. Confirm autoupdate actually works: `.\bin\checkver.ps1 <app> -u`
3. One PR changes only one manifest plus its related files (variants, `.reg`, `.ps1`)

### 4. Submit the PR

Title follows the rules in the next section. The body describes what changed and why.

### 5. `/verify`

Add a comment under the PR whose content starts with `/verify`, which triggers the automatic manifest verifier. It checks required properties, hashes, CI tests, and so on.

### 6. Wait for review

Respond to the questions raised as quickly as you can. Reviewing each other's PRs is encouraged, as long as you stay friendly and constructive.

### Extra requirements for Scoop core

- Branch from `develop`
- Run the tests and confirm there are no regressions
- Update tests and docs when needed
- PR titles follow [Conventional Commits](https://www.conventionalcommits.org/)

---

## PR title format

The validation regex is [regex101.com/r/cn45r4/1](https://regex101.com/r/cn45r4/1).

| Scenario | Format | Example |
|---|---|---|
| New manifest | `<app-name>: Add version <version>` | `tailcat: Add version 0.6.0` |
| Update an existing manifest | `<app-name>(@<version>): <small description>` | `wget@1.21.4: Fix moved urls`<br>`wget: Update to version 1.25.0, remove arm64 version` |
| Change several related manifests at once | `<app-name(*)>: <small description>` | `uutils-(*): Update homepage`<br>`uutils-coreutils(-lean): Fix shims` |
| Maintenance change | `(chore): <small description>` | `(chore): Resolve redirected GitHub repository URLs in bulk` |

---

## Excavator and "no version-only PRs"

Public buckets have an automatic update mechanism (`checkver` + `autoupdate`) plus a scheduled job (commonly called the **Excavator**, usually running every 4 hours).

Therefore:

- **PRs that only bump the version number will be rejected**. Exceptions are extremely rare (for example, GitHub Runner IPs being blocked by something like Cloudflare).
- If the logs show that autoupdate itself is broken, then fix autoupdate at the same time as you bump the version.
- **If upstream has a new version but the manifest has no autoupdate configuration, please add autoupdate along with the update.**

Known bucket auto-update cadence:

| bucket | Frequency |
|---|---|
| `main` | Every hour |
| `extras` | Every hour |
| `versions` | Daily |
| `java` | Daily |
| `php` | Daily |
| `games` | Daily |

To get the packages in your own bucket updated automatically: move them to one of the buckets above, or run your own copy of the Excavator.

---

## The scripts directory and auxiliary files

When you need auxiliary scripts such as `.reg` or `.ps1` files, put them under `scripts/<app-name>/` in the bucket repository, then have `pre_install` / `post_install` copy them into the install directory and execute them.

Examples: the Extras bucket's [vscode scripts](https://github.com/ScoopInstaller/Extras/tree/master/scripts/vscode) (file icons, program associations, with both an install and a removal set) and [windows-terminal](https://github.com/ScoopInstaller/Extras/tree/master/scripts/windows-terminal).

Caveats for file associations and icons (they must point at the `current` directory, never at the shim) are in `troubleshooting.md`.

---

## Publishing and listing

- Your own bucket: one line, `scoop bucket add <name> <url>`, is enough to distribute it.
- To get into ScoopDirectory: add the GitHub topic `scoop-bucket` to the repository.
- To get into the official main / extras: follow the main inclusion criteria above and go through the PR process (open an issue first).
- Old packages: the `versions` bucket; packages that need admin / system-level installation: `nonportable`.
