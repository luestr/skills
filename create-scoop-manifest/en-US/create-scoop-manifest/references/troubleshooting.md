# Troubleshooting

The diagnostic order is always: **environment → package → upstream source**. Run `scoop checkup` first, then look up the symptom in the tables. Do not start by editing the manifest.

## Contents

- [What checkup covers](#what-checkup-covers)
- [Install / launch issues](#install--launch-issues)
- [Package not found / version issues](#package-not-found--version-issues)
- [Download issues](#download-issues)
- [Extraction / installer issues](#extraction--installer-issues)
- [Hash issues](#hash-issues)
- [checkver / autoupdate issues](#checkver--autoupdate-issues)
- [Paths / links / associations](#paths--links--associations)
- [Performance and security software](#performance-and-security-software)
- [Command and environment quirks](#command-and-environment-quirks)

---

## What checkup covers

`scoop checkup` checks the following (some items require admin):

| Item | Consequence if it fails |
|---|---|
| Windows Defender exclusions | Extraction/installation is extremely slow and CPU is pegged; only detected with admin |
| The `main` bucket exists | Nothing you try to install can be found |
| Long path support | Extraction into deep directories fails |
| Windows Developer Mode | junction-related anomalies |
| 7zip helper (or `use_external_7zip`) | Most packages will not unpack |
| innounp | InnoSetup packages will not unpack |
| dark | WiX installer packages will not unpack |
| The volume holding `$globaldir` is NTFS | Global installs fail |
| The volume holding `$scoopdir` is NTFS | Scoop itself does not work properly |

Only an output of `No problems identified!` means the environment layer is fine. Look at `$issues` (problems) and `$defenderIssues` (performance issues only) separately.

---

## Install / launch issues

| Symptom | Cause | Fix |
|---|---|---|
| `File ... cannot be loaded because running scripts is disabled on this system` | ExecutionPolicy | `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `iex` flashes by and nothing gets installed | ExecutionPolicy / LanguageMode | Set the policy; check that `$ExecutionContext.SessionState.LanguageMode` is `FullLanguage` |
| The `scoop` command is not found | PATH not refreshed | Reopen the terminal; use `scoop which scoop` to locate it |
| Installing from an admin session throws a security error | Admin installs are blocked by default | `-RunAsAdmin` |
| Commands only take effect after a reboot (global) | System environment variables require a reboot for SYSTEM | Reboot once |
| `scoop install` fails partway through | Environment (missing 7zip/innounp/dark) or network | Run `scoop checkup` first, then `scoop install 7zip innounp dark` |
| Old version conflicts / two versions installed and behavior is wrong | Multiple versions coexisting requires an explicit switch | `scoop reset <app>@<version>`; `scoop list` only shows the newest version, use `scoop info <app>` to see all of them |
| Configuration lost after an upgrade | The program writes its config into the version directory | The manifest should use `persist`; as a stopgap you can copy it back from the old version directory |
| Leftovers after uninstall | `persist` data is kept by default | `scoop uninstall -p <app>` |

---

## Package not found / version issues

| Symptom | Cause | Fix |
|---|---|---|
| `Couldn't find manifest for 'x'` | The corresponding bucket is missing | `scoop bucket add extras` (or the corresponding bucket); `scoop search x` |
| `scoop search` results do not match expectations | With the sqlite cache enabled it is a partial match; with it disabled the query is a regex | Try different keywords; or `scoop config use_sqlite_cache true` |
| `scoop install x@1.2.3` says the version is not found | That version is not in the git history and autoupdate failed to generate it | Check `use_git_history`; manually confirm the manifest has `autoupdate`; if necessary look in the versions bucket |
| The outdated information shown by `scoop status` is wrong | The local bucket is not updated | Run `scoop update` first; `scoop status` compares against the local manifest |
| A manifest that was just pushed cannot be found | The bucket is not updated | `scoop update`; confirm the bucket has been added with `scoop bucket add` |

---

## Download issues

| Symptom | Cause | Fix |
|---|---|---|
| Downloads are extremely slow | Not going through a proxy / aria2 not enabled / slow CDN | `scoop install aria2`; `scoop config proxy ...` |
| aria2 causes failures | aria2 is incompatible with certain servers | `scoop config aria2-enabled false`, or use `aria2-fallback-enabled true` (already on by default) |
| aria2 warnings appear during `scoop update` | Default behavior | `scoop config aria2-warning-enabled false` |
| `scoop bucket add` cannot get through the proxy | scoop passes `currentuser@host:port` straight to git, and the format is incompatible | Temporarily switch to the git format: `scoop config proxy ':@proxy.example.org:8080'` → `scoop bucket add extras` → switch back with `scoop config proxy 'currentuser@proxy.example.org:8080'` |
| The proxy password contains `@` or `:` | Delimiter collision | Escape with `\`: `scoop config proxy 'username:p\@ssword@proxy.example.org:8080'` |
| You want to bypass the system proxy | | `scoop config rm proxy`, or `scoop config proxy none` |
| 401 on a private repository | Missing token / missing private_hosts | `scoop config gh_token <token>`; configure `private_hosts` with `match` + `headers` |
| It downloads but installs somewhere else / throws an `Invoke-WebRequest` exception | The URL carries a `#/...` fragment | The fragment is a Scoop directive, not part of HTTP; `scripts/hashurl.ps1` strips it automatically when it computes the hash |

---

## Extraction / installer issues

| Symptom | Cause | Fix |
|---|---|---|
| `Can't shim 'x.exe': File doesn't exist` | The installer never actually unpacked (an NSIS stuck on its GUI is the most common case) | See the NSIS escape plan in `installers-and-extraction.md` |
| `Failed to extract files from ...` | 7z does not support that format, or the helper is missing | Look at `7zip.log`; `scoop install 7zip`; confirm you are not treating an exe as a zip |
| An InnoSetup package extracts to nothing | `"innosetup": true` was omitted | Add it |
| A WiX / Burn package fails | dark is missing | `scoop install dark` or `wixtoolset` |
| An MSI installs with an uninstall entry and you do not want that | A deprecated `msi` block was written | Delete the `msi` block; Scoop will extract the msi like a zip |
| A zip extracts with all files flat at the root and `bin` cannot be found | `extract_dir` is missing | Use `7z l` to see the root directory name and add `extract_dir` (add it in autoupdate too) |
| `7z l` reports `Type = PE` and you assume it cannot be extracted | Misjudgment | The same listing usually contains an embedded 7z stream; try `#/dl.7z` |
| A strange `.nsis` directory appears after extraction | 7z's default exclusion rule | `Expand-7zipArchive` already carries `-xr!*.nsis`; add it yourself when extracting manually |
| A UAC prompt / install wizard appears during install | The `.exe` was treated as an installer and executed | Use `#/dl.7z`, or `pre_install` + 7z |
| `installer.script` ran but the installer also ran | `file` or `args` was written inside the `installer` block | Delete `file`/`args` and keep only `script` |

---

## Hash issues

| Symptom | Cause | Fix |
|---|---|---|
| `No hash in manifest` warning | The manifest has no hash | Compute it with `scripts/hashurl.ps1` and write it in (never leave it empty) |
| It installs but is never verified | An empty hash only warns, it does not block | Same as above; or temporarily use `-s` to skip explicitly (use with care) |
| `Hash check failed` | Wrong manifest hash / upstream swapped the package / the CDN returned an error page | `checkhashes -Update`; or `checkver -u -f`; verify the URL still points at the same artifact |
| `checkhashes -Update` cannot fill an empty hash | Known defect: `Get-Member` errors and the value is not changed | Compute it manually: `scripts/hashurl.ps1 <url>` |
| `URLS and hashes count mismatch` | The url array and the hash array have different lengths | Make the lengths match |
| `checkver -f` reports success but the hash is empty | `autoupdate.url` is missing, so Scoop has nowhere to download from | Add an `autoupdate.url` that reproduces a static url |
| Hashing a landing page gives a different value every time | The landing page itself changes | Compute/host the hash against the real artifact URL instead (source mode D) |

---

## checkver / autoupdate issues

| Symptom | Cause | Fix |
|---|---|---|
| `expects the homepage to be a github repository` | `"checkver": "github"` is set but `homepage` is not a repository | Change homepage, or write `"checkver": { "github": "<repo>" }` |
| checkver never matches | The upstream page was redesigned / the regex is stale | `scoop config debug true` to see the fetched content, then rewrite the regex |
| The version checkver picks up is the wrong token | The first unnamed group is not the version | Make the version the only unnamed group, or name it `version` |
| The `$matchXxx` variable is empty | The named group's casing was changed by `ToTitleCase` | Use only a single lowercase word for group names (`build` rather than `buildId`) |
| The url written by autoupdate 404s | `$version` was written into the static url, or the template is malformed | Use a literal version in the static url; only `autoupdate.url` should use variables |
| `checkver -u` does not fix the hash of the current version | It `continue`s when the version has not changed | Use `checkhashes -Update` or `checkver -u -f` |
| Frequent 403 / rate limit | The GitHub API is unauthenticated | `scoop config gh_token <token>` |
| Pre-releases are ignored but you want to use one | GitHub policy | Use an explicit `url` + `regex` instead of `"github"` |
| All hashes are empty during a bulk update | One or two manifests in the batch are missing `autoupdate.url` | Fill them in and run those individually; do not paper over the problem with a `mode: download` fallback |

---

## Paths / links / associations

### Broken `current`

`apps\<app>\current` is a **directory junction** that points at the current version directory. Why not a symlink: creating a symlink requires admin rights, a junction does not.

How a broken link shows up: after `scoop install`/`reset`, `current` in the app directory points at a version that does not exist. Fix: `scoop reset <app>` to rebuild it; if it is still broken, `scoop uninstall <app>` and reinstall.

Do not want to use junctions: `scoop config no_junction true` (the cost is that shims and shortcuts are bound to a specific version directory and must be regenerated after an update).

### File associations / Open With icons

There is only one rule: **point at `apps\<app>\current\<exe>` — never at shims, and never at a version directory.**

- Pointing at a version directory (`...\apps\mpv\0.32.0\mpv.exe`) → it breaks on the next update.
- Pointing at a shim (`...\scoop\shims\mpv.exe`) → the Open With menu shows an unnamed block with an unknown icon, multiple shims cannot be told apart, every associated file gets infected by the same problem, and sometimes the shim does not exit after launching the program.

How to do it: right-click → `Open With` → `Choose another app` → `Browse...` → pick the exe under `current`.

**What to do if you already added a shim by mistake**: Windows will not let you add the correct path for the same basename. You must uninstall the package that provides that shim → use any file to trigger "open with" once so Windows clears the stale entry → reinstall → then add the correct path. Alternatively edit the registry by hand.

Known limitation: programs whose executable file name is unstable (such as GIMP's `bin/gimp-2.10.exe`) cannot keep the association across updates.

### Long paths / deep directories

`checkup` checks long path support. When it is not enabled, extracting deep `node_modules` or long asset names fails. How to enable it (admin + group policy/registry `LongPathsEnabled`), or shorten the `SCOOP` root path.

---

## Performance and security software

| Symptom | Cause | Fix |
|---|---|---|
| CPU pegged during install, file access denied | The antivirus is scanning the files being extracted in real time | Add exclusion paths |
| `get.scoop.sh` is flagged as malware | PowerShell 5.1 heuristic false positive | Install with PowerShell 7 |
| The program is quarantined after installation | Same as above | Add the exclusion + report the false positive |

```powershell
# Requires admin
Add-MpPreference -ExclusionPath "$($env:programdata)\scoop", "$($env:scoop)"
# Undo
Remove-MpPreference -ExclusionPath "$($env:programdata)\scoop", "$($env:scoop)"
```

In an admin session, `checkup` detects whether these two exclusions are already set.

---

## Command and environment quirks

| Symptom | Cause | Fix |
|---|---|---|
| `Get-FileHash` does not exist | `powershell` was started from a pwsh session and inherited PS7 via `PSModulePath` | Standardize on `pwsh -NoProfile` |
| After `cd` in bash the script cannot find its files | Wrong working directory | For git use `git -C <path>`; for pwsh use `pwsh -NoProfile -Command "cd '...'; ..."` |
| You want to use scoop from bash/zsh | Scoop installs sh versions of its shims | You can use them directly; do not mix path separators across shells |
| Color codes in `scoop` output break parsing | Terminal ANSI | Judge by `$LASTEXITCODE`, do not match against output text |
| The install fails in CI but the pipeline is green | `iex` does not `exit` | `exit $LASTEXITCODE`, or set `$env:CI` |
| `scoop update` reports a conflict | The local bucket repository was modified | `scoop config autostash_on_conflict true`, or `git -C <bucket> stash` manually |
| A running target process aborts reset/uninstall/update | Default behavior | Close the program, or `scoop config ignore_running_processes true` (warn and continue only) |

---

## Troubleshooting order cheat sheet

1. `scoop checkup` — are there holes in the environment layer.
2. `scoop config debug true` — turn on verbose output and see what it actually does.
3. Verify "download" and "install" separately: `scoop download <app>` only checks the network and the hash; if it passes, the problem is in extraction/installer.
4. `scoop install <app> -k` — bypass the cache to rule out cache pollution.
5. `scoop install <app> -s` — skip the hash to separate "wrong hash" from "wrong file".
6. `7z l` / `7z x` the target package by hand — take the Scoop layer out of the picture and confirm the package itself is usable.
7. Only then suspect the manifest, and check it field by field against the field rules in `manifest-reference.md`.
