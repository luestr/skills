# Installation and Setup

Source: <https://github.com/ScoopInstaller/Install#readme>, the `install.ps1` parameter table, and the wiki pages Quick-Start / Global-Installs / Using-Scoop-behind-a-proxy / Uninstalling-Scoop.

## Contents

- [Prerequisites](#prerequisites)
- [Standard installation](#standard-installation)
- [All installer parameters](#all-installer-parameters)
- [Two ways to specify custom directories](#two-ways-to-specify-custom-directories)
- [Installing as administrator](#installing-as-administrator)
- [Installing behind a proxy](#installing-behind-a-proxy)
- [CI environments](#ci-environments)
- [Silent installation and exit codes](#silent-installation-and-exit-codes)
- [Directory layout and environment variables](#directory-layout-and-environment-variables)
- [Global installations](#global-installations)
- [Uninstalling](#uninstalling)
- [Installation-time failures](#installation-time-failures)

---

## Prerequisites

| Condition | Requirement | Check / fix |
|---|---|---|
| PowerShell | 5.1 or higher (what Win10 / Server 2016+ ship with is enough) | `$PSVersionTable.PSVersion` |
| Language Mode | Must be `FullLanguage` | `$ExecutionContext.SessionState.LanguageMode` |
| Execution Policy | One of `RemoteSigned` / `Unrestricted` / `ByPass` | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |

Win7/8 and Server 2008/2012 need [WMF 5.1](https://aka.ms/wmf5download) installed, or a supported newer PowerShell side-by-side. Older systems are not supported.

If Language Mode is `ConstrainedLanguage`, you must first allow it at the Group Policy / AppLocker layer — it cannot be changed from the script layer.

## Standard installation

In a **non-elevated** PowerShell:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
# equivalent form
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
```

The default location is `C:\Users\<username>\scoop`.

`get.scoop.sh` is a redirector that fetches `install.ps1` and executes it. When you need to pin a version / audit the contents, save it to disk first and then run it:

```powershell
irm get.scoop.sh -outfile 'install.ps1'
.\install.ps1
```

## All installer parameters

The complete param block of `install.ps1`:

```powershell
param(
    [String] $ScoopDir,                                          # User-level Scoop root directory
    [String] $ScoopGlobalDir,                                    # Global installation root directory
    [String] $ScoopCacheDir,                                     # Download cache directory
    [Switch] $NoProxy,                                           # Ignore the system proxy during installation
    [Uri] $Proxy,                                                # Proxy to use during installation
    [System.Management.Automation.PSCredential] $ProxyCredential,# Proxy credentials
    [Switch] $ProxyUseDefaultCredentials,                        # Authenticate to the proxy with the current user's Windows credentials
    [Switch] $RunAsAdmin                                         # Allow installation from an elevated console
)
```

| Parameter | Purpose | Notes |
|---|---|---|
| `-ScoopDir` | User-level root directory | Equivalent to setting `$env:SCOOP` |
| `-ScoopGlobalDir` | Global (`--global`) root directory | Equivalent to setting `$env:SCOOP_GLOBAL`; requires NTFS |
| `-ScoopCacheDir` | Download cache directory | Defaults to `<ScoopDir>\cache` |
| `-NoProxy` | Bypass the system proxy during installation | Only takes effect during installation; not written to the Scoop config |
| `-Proxy <Uri>` | Proxy for installation | E.g. `-Proxy 'http://127.0.0.1:7890'` |
| `-ProxyCredential <PSCredential>` | Username/password for the proxy | Either this or `-ProxyUseDefaultCredentials` |
| `-ProxyUseDefaultCredentials` | Authenticate to the proxy with the currently logged-on user's credentials | |
| `-RunAsAdmin` | Allow installation from an elevated console | Disabled by default; see below |

## Two ways to specify custom directories

**Option one: parameters (recommended — done in one shot)**

```powershell
.\install.ps1 -ScoopDir 'D:\Applications\Scoop' -ScoopGlobalDir 'F:\GlobalScoopApps' -NoProxy
```

**Option two: environment variables (legacy)**

```powershell
$env:SCOOP='D:\Applications\Scoop'
$env:SCOOP_GLOBAL='F:\GlobalScoopApps'
[Environment]::SetEnvironmentVariable('SCOOP_GLOBAL', $env:SCOOP_GLOBAL, 'Machine')
irm get.scoop.sh | iex
```

Note that `SCOOP_GLOBAL` must be written to the Machine scope; `SCOOP` only needs the User scope. Both must be visible in **the session that runs the installation script**.

You can still change them afterwards: `scoop config root_path <path>` / `scoop config global_path <path>` (see `cli-reference.md`). But **already-installed apps do not move with it** — changing the path only affects subsequent operations; an actual migration means moving directories and reinstalling shims by hand.

## Installing as administrator

For security reasons, an elevated console **cannot** install Scoop by default. To install in an elevated session you must explicitly pass `-RunAsAdmin`:

```powershell
irm get.scoop.sh -outfile 'install.ps1'
.\install.ps1 -RunAsAdmin [-OtherParameters ...]

# one-liner
iex "& {$(irm get.scoop.sh)} -RunAsAdmin"
```

Even so, day-to-day management should still go back to a normal user session. "Whether to be administrator" and "whether to install globally" are two separate things: installing Scoop as administrator ≠ global apps — global apps come from `scoop install <app> --global`.

## Installing behind a proxy

Three levels of granularity — pick as needed:

```powershell
# 1) Give only the installation script a proxy
iex "& {$(irm get.scoop.sh -Proxy 'http://<ip:port>')} -Proxy 'http://<ip:port>'}"

# 2) Use environment variables — every request in this session goes through the proxy
$env:HTTP_PROXY='http://<ip:port>'
$env:HTTPS_PROXY='http://<ip:port>'
irm get.scoop.sh | iex

# 3) When authentication is required, use the .NET default proxy (only valid for the current PowerShell session)
[net.webrequest]::defaultwebproxy = new-object net.webproxy "http://proxy.example.org:8080"
[net.webrequest]::defaultwebproxy.credentials = [net.credentialcache]::defaultcredentials
# or
[net.webrequest]::defaultwebproxy.credentials = new-object net.networkcredential 'username', 'password'
```

After installation, configure it permanently with `scoop config proxy` — see the proxy section of `cli-reference.md` and the `bucket add` proxy pitfall in `troubleshooting.md`.

## CI environments

GitHub Actions:

```yaml
- name: Install Scoop
  shell: pwsh
  run: irm get.scoop.sh | iex
```

When `$env:CI` is not set in CI, the `iex` form does not `exit`, so an installation failure will not fail the pipeline. Either exit with the code explicitly, or set `$env:CI`:

```yaml
- name: Install Scoop
  shell: pwsh
  run: |
    irm get.scoop.sh | iex
    exit $LASTEXITCODE
```

Common CI hardening: point `$env:SCOOP` at a workspace cache directory, `scoop config aria2-enabled false` (aria2 pays off little in CI), and `scoop install --no-update-scoop` to skip the self-update every time.

## Silent installation and exit codes

```powershell
irm get.scoop.sh | iex *> $null        # discard all output
irm get.scoop.sh | iex *> install.log  # write to a log
$LASTEXITCODE                          # 0 = success
```

`install.ps1` internally turns failures into `$Global:LASTEXITCODE` (under `iex`, `exit` would close the interactive session, so it only uses `LASTEXITCODE`). Judge success by that value alone — do not try to match output text.

## Directory layout and environment variables

```text
%USERPROFILE%\scoop                 User-level root directory (overridable via %SCOOP%)
  apps\                             Installed apps, one directory per app
    <app>\<version>\                Real version directory
    <app>\current\                  Directory junction → current version
    scoop\                          Scoop itself
  buckets\                          git clone of each bucket
  cache\                            Download cache (overridable via %SCOOP_CACHE% / cache_path)
  persist\                          Persistent data (%SCOOP%\persist\<app>)
  shims\                            Shim directory added to PATH
  modules\                          PowerShell modules (installed by psmodule, automatically added to PSModulePath)
%ProgramData%\scoop                 Global root directory (overridable via %SCOOP_GLOBAL%)
%USERPROFILE%\.config\scoop\config.json   Config file
```

Requirement: **the Scoop directory must live on an NTFS volume**. `scoop checkup` checks this with `DriveInfo.DriveFormat`; FAT32/exFAT errors out immediately.

### The three candidate config file locations (in priority order)

The actual logic in `lib/core.ps1`:

1. **Portable mode**: if Scoop is installed under `<root>\apps\scoop\current` and `<root>\config.json` exists, that file is used. This turns the whole root into a movable portable configuration.
2. **XDG**: `$env:XDG_CONFIG_HOME\scoop\config.json` (only takes effect when this environment variable is set).
3. **Default**: `%USERPROFILE%\.config\scoop\config.json`.

So when a config change "doesn't take effect", first confirm whether `$env:XDG_CONFIG_HOME` is pointing the path somewhere else, then check whether there is a `config.json` at the root.

The same priority order applies to the root directory: `$env:SCOOP` → `root_path` config → the root where Scoop itself lives → `%USERPROFILE%\scoop`; to the global directory: `$env:SCOOP_GLOBAL` → `global_path` → `%ProgramData%\scoop`; and to the cache: `$env:SCOOP_CACHE` → `cache_path` → `<root>\cache`.

Note that `SCOOP_CACHE` is officially marked **experimental and not thoroughly tested**: multiple users sharing the same cache directory may hit concurrent-write conflicts.

Historical path: very old versions installed to `%USERPROFILE%\AppData\Local\scoop`. Scripts used to have variables like `$oldscoopdir`, but **it does not exist in the hook scope of the current version** (measured: `$null`), so do not rely on it in a manifest.

## Global installations

```powershell
scoop install sudo
sudo scoop install git --global      # long form
sudo scoop install git -g            # short form
```

- Installs into `%ProgramData%\scoop`, changes system environment variables, and needs administrator rights → hence `sudo`.
- After the first global installation you must **reboot**, so that the local system account can see the new environment variables.
- Uninstalling / updating / cleaning up all need `-g`: `sudo scoop uninstall git -g`, `sudo scoop update git -g`, `sudo scoop cleanup * -g`.

## Uninstalling

```powershell
scoop uninstall scoop     # asks for confirmation; type y
```

This deletes `~/scoop/persist` (persistent data goes with it).

If the installation directory was manually damaged and you want to reinstall:

```powershell
del .\scoop -Force        # run from $HOME
irm get.scoop.sh | iex
```

To clear only one app's persistent data: `scoop uninstall -p <app>`.

## Installation-time failures

| Symptom | Cause | Fix |
|---|---|---|
| `iex` flashes and nothing gets installed | ExecutionPolicy is not an allowed value | Set `RemoteSigned` |
| `... cannot be loaded because running scripts is disabled on this system` | Same as above | Same as above |
| Errors mentioning `ConstrainedLanguage` | Wrong Language Mode | Allow `FullLanguage` in Group Policy |
| Antivirus flags `get.scoop.sh` as malicious | PowerShell 5.1 + heuristic false positive | Install with PowerShell 7; or add an exclusion path |
| A security prompt appears in an elevated session | Administrator installation is blocked by default | Add `-RunAsAdmin` |
| Installed on FAT32/exFAT, later operations error out | Not NTFS | Switch volumes, or change `SCOOP` / `root_path` |
| `irm get.scoop.sh` times out on a corporate network | Proxy | See proxy installation above |
| The `scoop` command is not found after installation | PATH not refreshed | Reopen the terminal; the shims directory must be on PATH |
| Globally installed apps are invisible to SYSTEM | Environment variables not in effect for SYSTEM | Reboot once |

`Add-MpPreference -ExclusionPath "$($env:programdata)\scoop", "$($env:scoop)"` excludes both root directories from real-time scanning (requires administrator); undo it with `Remove-MpPreference -ExclusionPath ...`.
