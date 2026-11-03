# Manifest Field Reference

Source: the wiki page [App-Manifests](https://github.com/ScoopInstaller/Scoop/wiki/App-Manifests), the field-order and style rules in CONTRIBUTING, and the actual behavior of `lib/manifest.ps1`.

## Contents

- [Minimal usable manifest](#minimal-usable-manifest)
- [Required fields](#required-fields)
- [Optional fields](#optional-fields)
- [architecture block](#architecture-block)
- [url and the # fragment](#url-and-the--fragment)
- [hash](#hash)
- [installer / uninstaller](#installer--uninstaller)
- [persist](#persist)
- [bin and shim aliases](#bin-and-shim-aliases)
- [shortcuts](#shortcuts)
- [psmodule](#psmodule)
- [checkver / autoupdate](#checkver--autoupdate)
- [depends / suggest](#depends--suggest)
- [Deprecated and undocumented fields](#deprecated-and-undocumented-fields)
- [Hard style rules](#hard-style-rules)

---

## Minimal usable manifest

```json
{
    "version": "1.0",
    "url": "https://github.com/lukesampson/cowsay-psh/archive/master.zip",
    "extract_dir": "cowsay-psh-master",
    "bin": "cowsay.ps1"
}
```

`version` + `url` + `bin` is enough to install. But a manifest that actually goes into a bucket also needs `description`, `homepage`, `license`, and `hash`.

---

## Required fields

### `version`
The version number to install, as a string. When the tag carries a `v` prefix, strip it (`v1.2.3` → `"1.2.3"`).

### `description`
A short one-line description. **If it is the same as the file name, do not repeat the program name in the description.** Technically not required, but every new/updated manifest must have it.

### `homepage`
The program's home page. With `"checkver": "github"` it **must be a GitHub repository URL** (otherwise checkver reports "expects the homepage to be a github repository"); when the home page is not GitHub, use `"checkver": { "github": "<repo url>" }` or an explicit `url` instead.

### `license`
A string or an object.

- Known licenses use [SPDX identifiers](https://spdx.org/licenses): `"MIT"`, `"Apache-2.0"`, `"GPL-3.0-or-later"`.
- When it is not SPDX, use one of these words: `Freeware` (free forever), `Proprietary` (paid), `Public Domain`, `Shareware` (try before you pay), `Unknown` (cannot be determined).
- Different files carry different licenses: separate with commas. Overall dual license: separate with a pipe. When open-source and closed-source are mixed, **list the non-open-source license first**.
- When the set cannot be enumerated exhaustively, you may append `,...` at the end.
- The object form `{ "identifier": "Apache-2.0", "url": "https://.../LICENSE" }` links to the upstream LICENSE file from the bucket page.

```json
"license": "MIT"
"license": { "identifier": "Proprietary", "url": "https://example.com/eula" }
"license": { "identifier": "Freeware" }
```

---

## Optional fields

| Field | Type | Notes |
|---|---|---|
| `##` | string / array | Comment. Used to record judgments such as "why there is no checkver", so anomalies can be explained during an audit |
| `architecture` | object | See the next section |
| `autoupdate` | object | See `autoupdate-reference.md` |
| `bin` | string / array | See below |
| `checkver` | string / object | See `autoupdate-reference.md` |
| `depends` | string / array | Runtime dependencies, installed automatically |
| `suggest` | object | Suggested optional dependencies, see below |
| `env_add_path` | string / array | Added to the user PATH (system PATH with `--global`). **Must be a relative path inside the install directory** |
| `env_set` | object | Sets environment variables (system level with `--global`) |
| `extract_dir` | string | Extract only this subdirectory from the archive |
| `extract_to` | string | Extract the contents into the given subdirectory |
| `hash` | string / array | One-to-one with `url` |
| `innosetup` | `true` | Declares that this is an InnoSetup installer; Scoop unpacks it with innounp |
| `installer` | object | See below |
| `notes` | string / array | Message displayed after installation completes |
| `persist` | string / array | See below |
| `post_install` / `pre_install` / `pre_uninstall` / `post_uninstall` | string / array | PowerShell snippets, see "Script hooks" |
| `psmodule` | object | Installed as a PowerShell module |
| `shortcuts` | array of arrays | Start menu shortcuts |
| `uninstaller` | object | Same as `installer`, executed on uninstall |

### Script hooks

`pre_install` / `post_install` / `pre_uninstall` / `post_uninstall` / `installer.script` / `uninstaller.script` share one set of variables. The table below is the **measured** result (Scoop v0.6.0, obtained by dumping every variable from a `pre_install` script), not copied from the wiki:

| Variable | Measured value example | Notes |
|---|---|---|
| `$app` | `probe2` | App name (the manifest file name) |
| `$version` | `2.0.0` | The version being installed |
| `$cmd` | `install` / `update` / `uninstall` | The current subcommand |
| `$architecture` | `64bit` / `32bit` / `arm64` | Target architecture |
| `$global` | `$false` / `$true` | Whether global |
| `$manifest` | deserialized object | The full manifest |
| `$scoopConfig` | `@{root_path=...; scoop_branch=master; ...}` | Scoop configuration object |
| `$dir` | `...\apps\probe2\2.0.0` | Install directory (see scope differences below) |
| `$original_dir` | `...\apps\probe2\2.0.0` | Real version directory |
| `$persist_dir` | `...\persist\probe2` | Persist directory |
| `$bucketsdir` | `...\scoop\buckets` | |
| `$cachedir` | `...\scoop\cache` | |
| `$globaldir` | `...\ScoopGlobal` (i.e. `%ProgramData%\scoop` or its override value) | |
| `$scoopdir` | `...\ScoopUser` (i.e. `%USERPROFILE%\scoop` or its override value) | |
| `$fname` | `probe2.zip` | The last downloaded file name |
| `$url` | the manifest source used for this run | |
| `$bucket` | **undefined** (for a local manifest) | Only has a value when installing from a bucket |

**The three variables the wiki has but you cannot get** (all measured as `$null`):

| wiki spelling | reality |
|---|---|
| `$cfg` | does not exist; the configuration object is called **`$scoopConfig`** |
| `$cfgpath` | does not exist |
| `$modulesdir`, `$oldscoopdir` | do not exist |

To get a configuration value, use `$scoopConfig.root_path` or call `get_config <KEY>` directly (`get_config` is available inside hooks). To get the modules directory, use `modulesdir $global` (it is a **function**, not a variable).

**The `$dir` scope differences (confirmed by measurement)**:

- `pre_install`, `installer.script`, `pre_uninstall`, `uninstaller.script`, `post_uninstall` → `$dir` is the **real versioned directory** (`...\apps\<app>\2.0.0`).
- `post_install` → `$dir` has already been swapped by `link_current` for the **`current` junction** (`...\apps\<app>\current`).

Measured output: in `post_install`, `$dir = ...\postdir\current`, while `$original_dir = ...\postdir\1.0.0`. So use `$original_dir` when you need the real path; do not do path comparisons against `$dir` inside `post_install`.

`appdir` is a **function** (`appdir <app> [<global>]`) used to get the directory of another Scoop app:

```powershell
"post_install": "if (Test-Path \"$(appdir otherapp)\\current\\otherapp.exe\") { ... }"
```

A `pre_install` array is joined into a single scriptblock with `\r\n` and then executed with `Invoke-Command`; the variables reach it from `install_app` through PowerShell dynamic scoping. So when simulating locally for a test you must first define `$dir` / `$fname` in the outer function, otherwise you get empty values — see `installers-and-extraction.md` for details.

---

## architecture block

Under `architecture` you can place `64bit` / `arm64` / `32bit`, and each sub-object may contain: `bin`, `checkver`, `extract_dir`, `hash`, `installer`, `pre_install`, `post_install`, `shortcuts`, `uninstaller`, `url`, `msi` (deprecated).

**Rule**: only apps that provide "32bit downloads only" may omit `architecture`; in every other case `architecture` is required (this is mandatory bucket style). Only when there is a single architecture-agnostic binary do you use top-level `url`/`hash`.

```json
{
    "architecture": {
        "64bit": { "url": "...x64.zip", "hash": "..." },
        "arm64": { "url": "...arm64.zip", "hash": "..." },
        "32bit": { "url": "...x86.zip", "hash": "..." }
    }
}
```

---

## url and the # fragment

`url` can be a string or an array (when it is an array, `hash` must be an array of the same length). HTTP / HTTPS / FTP are supported.

The **`#` fragment** changes the local file name after download and must be written starting with `#/`:

| Fragment | Effect | Use |
|---|---|---|
| `#/name.exe` | Rename to `name.exe` after download | Unstable file name |
| `#/dl.7z` | Save as 7z and extract automatically | **Bypasses installers that write to the registry / require elevation** |
| `#/dl.exe` | Rename to exe, then hand over to `installer.script` | Multi-layer nested packages |

```json
"url": "https://example.org/program.exe#/dl.7z"
```

Scoop downloads `program.exe` but stores it as `dl.7z` and then extracts it — this is the standard trick for skipping an EXE installer's side effects.

---

## hash

A string or an array, one-to-one with `url`. SHA256 by default; other algorithms take a prefix: `sha512:`, `sha1:`, `md5:`. Lowercase, no backslashes.

```json
"hash": "54fabf3778685680cf97ba9fd4e84ea54f5c3ac72c54e740f9e9a12fd7dce480"
"hash": [ "<hash-of-url1>", "<hash-of-url2>" ]
```

**An empty hash is a trap**: at install time it only warns `No hash in manifest` and then continues **without verifying**; `checkver -u` cannot fill it in either (an empty hash falls into the branch that requires an `architecture` block). A new manifest must be seeded with a real hash.

The reverse trap is subtler: **if `autoupdate` contains a `hash` but no `url`, `checkver -u` will overwrite the existing correct hash with `""`**. Measured; the exit code was still 0. So if `hash` appears in `autoupdate`, `url` must be there as well.

The right tool for computing hashes is this skill's `scripts/hashurl.ps1` — it strips the `#/...` fragment (that is a Scoop directive, not part of the HTTP URL), uses Scoop's UA, and outputs a lowercase SHA256.

---

## installer / uninstaller

```json
"installer": {
    "file": "setup.exe",
    "script": "…PowerShell snippet…",
    "args": ["/S", "/D=$dir"],
    "keep": "true"
}
```

| Key | Notes |
|---|---|
| `file` | Installer file name. Defaults to the last downloaded file. **Must** be specified explicitly in `uninstaller` |
| `script` | Use a PowerShell snippet instead of `file` to perform the installation |
| `args` | Array of arguments passed to the installer |
| `keep` | When `"true"`, keep the installer (for example because it is needed at uninstall time). Ignored in `uninstaller` |

**The ordering of `file`/`args` versus `script` is a trap**: as soon as `file` or `args` is present, Scoop's `Invoke-Installer` will **first** launch that binary (`/S` for silent; without arguments it shows the GUI), and **then** run the `script` hook. To do a pure extraction install, keep only `script` and remove both `file`/`args` — with no `file`/`args` it skips execution but still calls `Invoke-HookScript`.

`uninstaller` runs on both `scoop uninstall` and `scoop update`.

---

## persist

Redirects files/directories into `~/scoop/persist/<app>/`, preserved across updates. Implemented with directory junctions or hard links.

```json
"persist": "config.ini"
"persist": ["conf", "data"]
"persist": [
    "keeps_its_name",
    ["original_name", "new_name_inside_the_data_dir"]
]
```

- Persisted data that already exists at install time is copied into the data directory and links are created.
- Uninstall **keeps** the data by default; only `scoop uninstall -p <app>` clears it.
- Portability first: if you can use `persist`, do not let the program write its configuration into `%APPDATA%`.

---

## bin and shim aliases

```json
"bin": "app.exe"
"bin": ["app.exe", "helper.exe"]
"bin": ["busybox.exe", "sh", "bash"]          // alias + no args
"bin": [["program.exe", "alias", "--args"]]   // alias + args
```

**A single aliased shim must be wrapped in one more array**: `"bin": [["program.exe", "alias"]]`. Otherwise it is treated as two independent shims.

---

## shortcuts

An array, each item being a 2~4 tuple:

1. Target file path (required, relative to the install directory)
2. Shortcut name (required, supports subdirectories `<AppsSubDir>\\<AppShortcut>`)
3. Launch arguments (optional)
4. Icon path (optional)

```json
"shortcuts": [
    ["HanaAgent.exe", "HanaAgent", "--fast", "assets\\icon.ico"]
]
```

CLI programs do not need shortcuts; when a GUI program does not accept command-line arguments, it does not need to go into `bin`.

---

## psmodule

```json
"psmodule": { "name": "NameOfTheModule" }
```

`name` is required, and it must match the name of the `.psd1` inside the extracted directory for PowerShell to recognize it automatically. Once installed it is linked into `~/scoop/modules` (that directory is added to `$env:PSModulePath` automatically); it is actually two layers of junction: `modules\Name` → `apps\name\current` → `apps\name\<version>`.

---

## checkver / autoupdate

See `autoupdate-reference.md`. In one sentence: `checkver` finds the version, and `autoupdate` uses variables such as `$version` / `$match*` / `$majorVersion` to rebuild `url`, `hash`, `extract_dir`, and so on.

---

## depends / suggest

```json
"depends": ["7zip", "innounp"]
"suggest": { "JDK": ["extras/oraclejdk", "openjdk"] }
```

- `depends` are **runtime** dependencies, installed automatically at the latest version; `scoop status` only warns about missing runtime dependencies.
- Install-time dependencies (such as the 7zip/innounp needed for extraction) are inferred from the `url` file extension and do not need to be written into `depends`.
- `suggest` is a hint, not a dependency. If any one app in that group is already installed, the whole group counts as satisfied and is no longer suggested.
- On update, dependencies are installed only when they are **completely missing**; outdated versions are left alone.

**Do not add a VC++ runtime `depends` to modern NSIS packages** — they bundle it themselves, and adding it actually prevents installation on trimmed-down systems.

---

## Deprecated and undocumented fields

| Field | Status |
|---|---|
| `msi` | **Deprecated**. Do not write it anymore. The new approach is to treat the `.msi` as a zip (just omit this field). Old field structure: `code` (product GUID, required), `silent` |
| `_comment` | Deprecated, use `##` |
| `cookie` | Undocumented, appears only in a few third-party buckets |

---

## Hard style rules

From CONTRIBUTING; PRs are checked automatically:

1. **Fields in this order** (only write the ones that are present):
   `version` → `description` → `homepage` → `license` → `notes` → `depends` → `suggest` → `architecture` (containing `url`, `hash`) → `extract_dir` → `extract_to` → `pre_install` → `installer` → `post_install` → `env_add_path` → `env_set` → `bin` → `shortcuts` → `persist` → `pre_uninstall` → `uninstaller` → `post_uninstall` → `checkver` → `autoupdate`
2. **4-space indentation** (tab width 4).
3. `license` must be a valid SPDX identifier (or one of the non-SPDX words listed above).
4. **Prefer portability** (use `persist`).
5. CLI programs do not need `shortcuts`; GUI programs without command-line arguments do not need `bin`.
6. **When an array has only one element, write it as a string**.
7. `architecture` may be omitted when only 32bit downloads are provided; it is required in every other case.
8. After an update, confirm that autoupdate actually runs through.
9. One PR changes only one manifest and its related files (variants, `.reg`, `.ps1`, etc.).

For ready-made examples see: [main bucket](https://github.com/ScoopInstaller/Main/tree/master/bucket), the official template [app-name.json.template](https://github.com/ScoopInstaller/BucketTemplate/blob/master/bucket/app-name.json.template) (this skill's `assets/app-name.json.template` is an equivalent copy of it).
