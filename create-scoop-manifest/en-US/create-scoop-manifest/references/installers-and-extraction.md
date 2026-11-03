# Extraction, Installers, and Escaping NSIS

Sources: `lib/decompress.ps1` (the dispatch logic of `Invoke-Extraction` / `Expand-*`), `lib/install.ps1` (`Invoke-Installer` / `Invoke-HookScript`), and hands-on experience.

## Contents

- [How Scoop decides how to extract](#how-scoop-decides-how-to-extract)
- [Handling strategy by package type](#handling-strategy-by-package-type)
- [Telling what is inside an exe](#telling-what-is-inside-an-exe)
- [The #dl.7z trick](#the-dl7z-trick)
- [Escaping an NSIS silent-install failure](#escaping-an-nsis-silent-install-failure)
- [installer.script vs pre_install: which to pick](#installerscript-vs-pre_install-which-to-pick)
- [Three quoting and scoping traps](#three-quoting-and-scoping-traps)
- [Local reproduction test](#local-reproduction-test)
- [extract_dir for zip/tar](#extract_dir-for-ziptar)

---

## How Scoop decides how to extract

`Invoke-Extraction` runs a single `switch -regex` over **each downloaded file name**, looking only at the extension:

| File name matches | Which function runs | Condition |
|---|---|---|
| `\.zip$` | `Expand-7zipArchive` | the 7zip helper is installed (default), or `use_external_7zip` is set and `7z` is on PATH |
| `\.zip$` | `Expand-ZipArchive` | neither of the above holds; falls back to `Microsoft.PowerShell.Archive\Expand-Archive` |
| `\.msi$` | `Expand-MsiArchive` | lessmsi when `use_lessmsi`, otherwise `msiexec /a` |
| `\.exe$` | `Expand-InnoArchive` | **only when** `manifest.innosetup = true` |
| anything else (decided by `Test-7zipRequirement`) | `Expand-7zipArchive` | `.7z`, `.tar`, `.gz`, `.lzma`, `.lzh`, split 7z/rar, etc. |

Three key conclusions:

1. **A `.exe` is by default neither extracted nor executed.** `Invoke-Extraction` only unpacks a `.exe` when `innosetup: true`, and the very first check in `Invoke-Installer` (`lib/install.ps1`) is `if ($installer.file -or $installer.args)` - **with no `installer` block the whole section is skipped**. So a bare `.exe` URL is simply dropped into `$dir` untouched and never run - verified by experiment: with `url` pointing at `where.exe` and no `installer` written, "Running installer" never appeared in the install log, `where.exe` sat unchanged in the install directory, and Scoop went straight ahead and created a shim for it.

   This means the two common ways of writing a manifest mean completely different things:

   | How it is written | What Scoop does |
   |---|---|
   | `"url": "...setup.exe"` + only `bin` | **Download only, no execution.** Suited to artifacts that are already a single executable (Go/Rust single-file exe). |
   | `"url": "...setup.exe"` + `installer.file`/`args` | Runs the installer first, then runs `installer.script` |
   | `"url": "...setup.exe#/dl.7z"` | Stores it as `dl.7z`, then extracts it as a 7z |

   So when "the project only ships an NSIS installer and you want it installed as a portable app", **omitting the `installer` block makes extraction impossible** - the installer never runs, but you did not get the application files either, so `bin` points at a file that does not exist and the `create_shims` stage reports `Can't shim 'xxx.exe': File doesn't exist`. You **must** extract explicitly, either with `#/dl.7z` or with 7z inside `pre_install`.

2. **NSIS is not on the automatic extraction allowlist.** Even when an electron-builder NSIS package can be opened with 7z, Scoop will not go and extract it on its own.
3. **`.tar.gz` / `.tar.xz` are extracted twice.** `Expand-7zipArchive` detects the inner tar and extracts again, and `extract_dir` takes effect on the second pass.

The actual arguments to `Expand-7zipArchive`: `7z x <file> -o<dest> -xr!*.nsis -y`, plus `-ir!<dir>\*` when there is an `extract_dir`. So for 7z, `extract_dir` means "extract only this one subdirectory", not "extract everything and then move it".

---

## Handling strategy by package type

| Package type | Recommended form | Notes |
|---|---|---|
| Portable `.zip` / `.7z` | plain `url` + `extract_dir` if needed | Preferred. Use `7z l` to check whether there is a root directory |
| `.tar.gz` | plain `url` + `extract_dir` | Scoop extracts the inner tar automatically |
| `.msi` | **do not write an `msi` block**; treat it as a zip | The old `msi.code` / `msi.silent` form is deprecated |
| InnoSetup `.exe` | `"innosetup": true` | Scoop unpacks it with innounp, no installer run |
| WiX / Burn `.exe` | `scoop install dark`, then let the helper unpack it | `Expand-DarkArchive` |
| NSIS `.exe` (silent run works) | write `installer.file` + `args: ["/S"]`, hand it to Scoop | without an `installer` block it **never runs at all** |
| NSIS `.exe` (silent run does not work) | `#/dl.7z`, or `pre_install` + two-stage 7z | see below |
| Single-file `.exe` (Go/Rust artifact) | plain `url` + `#/name.exe` + `bin` | no `installer` needed, no extraction needed |
| Self-extracting SFX | `#/dl.7z` | often extractable even when `7z l` says `Type = PE` |

The benefit of extracting an MSI instead of installing it: nothing lands in "Apps & features", no registry uninstall entry is left behind, and uninstalling means deleting the directory.

---

## Telling what is inside an exe

```powershell
7z l .\setup.exe            # list contents
7z l -slt .\setup.exe       # include type information
```

How to read it:

- `$PLUGINSDIR\app-64.7z` (or `app-32.7z`) appears → an electron-builder / NSIS-3 Unicode wrapper, and the real application lives in the inner 7z.
- A pile of `.dll` files plus something like `System.dll` under `$PLUGINSDIR\` → ordinary NSIS.
- `{app}\...` paths appear → InnoSetup (you should be using `innosetup: true`).
- `Binary.*` / `AttachedContainer\` appear → WiX Burn.
- `Type = PE` but an embedded 7z stream can still be listed → `#/dl.7z` will still extract it.
- `7z l` reports `Unknown Error` / lists nothing at all → either a pure MSI wrapped in an exe shell, or a proprietary format; change your approach.

Running `7z x -y -o<dir> setup.exe` by hand once and looking at the directory structure is faster than reading documentation.

---

## The #dl.7z trick

The lowest-effort universal workaround; it needs no script at all:

```json
"url": "https://example.org/app-1.2.3-setup.exe#/dl.7z"
```

Scoop stores the exe as `dl.7z` and then routes it through `Expand-7zipArchive` as a `.7z`. The installer never runs at all, so there is no UAC prompt, nothing is written to the registry, and nothing is placed outside the install directory.

The price: if the exe really is an opaque installer (no usable 7z stream inside), what you extract is garbage or the extraction simply fails. So confirm with `7z l` first.

It applies to: NSIS wrappers, SFX archives, and any exe that "7z can list".

---

## Escaping an NSIS silent-install failure

### Symptom

The manifest says `"bin": "app.exe"`, and `scoop install` reports:

```text
Can't shim 'app.exe': File doesn't exist.
```

Or the install hangs indefinitely, or a setup wizard window pops up.

### Cause

When an electron-builder NSIS configuration uses `oneClick: false`, `perMachine: false` and `allowToChangeInstallationDirectory: true`, the installer has an interactive wizard. Scoop runs `app-1.2.3-setup.exe /S`, the installer is still waiting for GUI interaction, extraction never completes, and of course the exe that `bin` wants is not in `$dir`.

### Fix: two-stage 7z extraction

Skip the `installer` block, do the extraction in two stages with `pre_install`, and pull in `7zip` via `depends` (Scoop uses its built-in helper).

```json
{
    "version": "2.4.2",
    "description": "Oh My PPT - Local-first AI presentation workbench",
    "homepage": "https://github.com/arcsin1/oh-my-ppt",
    "license": { "identifier": "Apache-2.0", "url": "https://github.com/arcsin1/oh-my-ppt/blob/main/LICENSE" },
    "url": "https://github.com/arcsin1/oh-my-ppt/releases/download/v2.4.2/oh-my-ppt-2.4.2-win.exe",
    "hash": "bca4930d53e2d2a9c75ede781216c4efa83ba6465a579dc2998f8e397bb5c13d",
    "depends": "7zip",
    "pre_install": [
        "$nsis = Get-Item \"$dir\\$fname\"",
        "$stage = Join-Path $env:TEMP (\"ohmyppt-extract-\" + $PID)",
        "if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }",
        "New-Item -ItemType Directory -Path $stage | Out-Null",
        "Push-Location $stage",
        "& 7z x -y -o\"$stage\" \"$nsis\" '$PLUGINSDIR\\app-64.7z' | Out-Null",
        "& 7z x -y -o\"$dir\" (Join-Path $stage '$PLUGINSDIR\\app-64.7z') | Out-Null",
        "Pop-Location",
        "Remove-Item -Recurse -Force $stage",
        "Remove-Item -Force \"$nsis\""
    ],
    "bin": "ohmyppt.exe",
    "shortcuts": [
        ["ohmyppt.exe", "OhMyPPT", "Oh My PPT - Local-first AI presentation workbench"]
    ],
    "checkver": { "github": "https://github.com/arcsin1/oh-my-ppt", "regex": "v([\\d.]+)" },
    "autoupdate": {
        "url": "https://github.com/arcsin1/oh-my-ppt/releases/download/v$version/oh-my-ppt-$version-win.exe"
    }
}
```

The flow: extract the NSIS archive into a temp directory to get `$PLUGINSDIR\app-64.7z` → extract that inner 7z into `$dir` → clean up the temp directory and the original exe.

**The inner file name can change between versions.** For something more robust, search instead of hardcoding:

```powershell
"$inner = Get-ChildItem -Path $stage -Recurse -Filter 'app-64.7z' | Select-Object -First 1",
"if ($null -eq $inner) { throw 'Inner app archive (app-64.7z) not found inside NSIS payload' }",
"& 7z x -y -o\"$dir\" $inner.FullName | Out-Null"
```

### Scope of applicability

- ✅ electron-builder NSIS (inner `app-64.7z` / `app-32.7z`)
- ✅ Other NSIS toolchains, where the outer layer can have its embedded 7z pulled out by 7z (replace `$PLUGINSDIR\app-64.7z` with the real inner path)
- ❌ Non-NSIS (MFC, WinRAR SFX, InnoSetup with `innosetup: true` left out) - run `7z l` on the structure first, then decide

---

## installer.script vs pre_install: which to pick

Both can do a pure extraction install, but the semantics differ:

| | `pre_install` + 7z | `installer.script` + 7z |
|---|---|---|
| When it runs | before the extraction stage | after the extraction stage, before `bin`/shims |
| Does Scoop execute the exe | no | **as soon as `file` or `args` is present it runs first** |
| Risk of getting it wrong | low | high (`file`/`args` is the trap) |
| Use when | you need files laid down first, or you are bypassing the installer flow entirely | you need custom logic inserted in the middle of the standard install flow |

The `installer.script` version (safe only when there is no `file`/`args`):

```json
"installer": {
    "script": "7z x \"-o$dir\\.cache\" \"$dir\\$fname\" -y | Out-Null; $inner = Get-ChildItem -Path \"$dir\\.cache\" -Recurse -Filter 'app-64.7z' | Select-Object -First 1; if ($null -eq $inner) { throw 'Inner app archive not found' }; 7z x \"-o$dir\" $inner.FullName -y | Out-Null; Remove-Item -Recurse -Force \"$dir\\.cache\", \"$dir\\$fname\""
}
```

**Decision rule**: if the goal is merely "do not run that installer, just get the files out", use `pre_install`. Only use `installer.script` when you genuinely need to insert logic into Scoop's installer stage, and you **must** confirm that the `installer` block contains neither `file` nor `args`.

---

## Three quoting and scoping traps

### 1. `$PLUGINSDIR` **must** use single quotes

`$PLUGINSDIR` is an NSIS variable name, not a PowerShell variable. Double quotes make PowerShell evaluate it to an empty string, and 7z then cannot find the path.

```powershell
"& 7z x -y -o\"$stage\" \"$nsis\" '$PLUGINSDIR\\app-64.7z'                # ✅
"& 7z x -y -o\"$stage\" \"$nsis\" \"$PLUGINSDIR\\app-64.7z\"              # ❌ the path becomes \app-64.7z
"(Join-Path $stage '$PLUGINSDIR\\app-64.7z')"                             # ✅ when joining, still let only $stage be evaluated
```

### 2. `$dir` / `$fname` **must** use double quotes

These two are PowerShell variables that Scoop injects through dynamic scoping. Single quotes will not get their values.

### 3. How the `pre_install` array is joined and executed

Scoop's implementation (`Invoke-HookScript` in `lib/install.ps1`):

```powershell
Invoke-Command ([scriptblock]::Create($Script -join "`r`n"))
```

What that means:

- The array elements are joined into a single scriptblock with `\r\n`.
- It runs through `Invoke-Command`, and the variables arrive from the `install_app` function through **dynamic scoping**.

Corollary: when you simulate it locally you **must** define `$dir` / `$fname` in an enclosing function, otherwise `Invoke-Command` picks up empty values and the script silently does the wrong thing.

Also note that `$dir` inside `pre_install` is the **real versioned directory** (`apps\<app>\1.2.3`); only in `post_install` does `$dir` point at `current`.

---

## Local reproduction test

You can verify `pre_install` logic without touching a bucket and without a real `scoop install`:

```powershell
function Invoke-HookScript {
    param([string]$HookType, [string[]]$Script)
    if ($Script) {
        Invoke-Command ([scriptblock]::Create($Script -join "`r`n"))
    }
}

$dir = 'D:\tmp\apptest\2.4.2'                 # any target directory
$fname = 'oh-my-ppt-2.4.2-win.exe'            # the target file name
$manifest = Get-Content 'bucket\oh-my-ppt.json' -Raw | ConvertFrom-Json

# put the downloaded exe into $dir first
Invoke-HookScript -HookType 'pre_install' -Script $manifest.pre_install

# verify
Test-Path (Join-Path $dir 'ohmyppt.exe')      # should be True
Get-ChildItem $dir                            # the original exe should be gone, no intermediate junk left
```

Get this step passing before doing a real `scoop install`; it saves you from repeated install/uninstall cycles.

---

## extract_dir for zip/tar

Many zips extract to a single root directory (`App-1.2.3/`). Without `extract_dir` everything is flattened into `$dir` and the `bin` path ends up wrong.

```powershell
7z l .\app.zip | Select-Object -First 20      # check whether the first level is a single root directory
```

```json
"extract_dir": "App-1.2.3",
"autoupdate": { "url": "...", "extract_dir": "App-$version" }
```

`autoupdate.extract_dir` has to be written as well, otherwise the structure will not match after the next automatic update.

Likewise, if the archive has to be laid down into a subdirectory:

```json
"extract_to": "bin"
```
