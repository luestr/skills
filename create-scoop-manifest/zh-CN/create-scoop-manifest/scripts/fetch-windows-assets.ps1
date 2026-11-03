<#
.SYNOPSIS
    Print the version, download URLs and sha256 of a project's Windows release assets,
    without downloading the artifacts.
.DESCRIPTION
    GitHub computes sha256 at upload time and exposes it as an asset's `digest`, so there is
    never a reason to fetch a 500 MB installer just to hash it. This is the PowerShell twin of
    fetch-windows-assets.mjs and exists because node is not installed everywhere.

    Windows assets are identified loosely (windows / win64 / x64 / arm64 / x86, plus common
    archive extensions); anything not matched is listed separately so nothing is silently
    dropped from view.
.PARAMETER Repo
    'owner/repo'.
.PARAMETER Tag
    Release tag, e.g. 'v0.450.0'. Defaults to the latest release.
.PARAMETER Token
    GitHub token. Falls back to $env:GITHUB_TOKEN / $env:GH_TOKEN, then to
    `scoop config gh_token`. Needed for private repos and to avoid rate limits.
.EXAMPLE
    pwsh -NoProfile -File fetch-windows-assets.ps1 liliMozi/openhanako
.EXAMPLE
    pwsh -NoProfile -File fetch-windows-assets.ps1 liliMozi/openhanako v0.450.0
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $Repo,

    [Parameter(Position = 1)]
    [string] $Tag = 'latest',

    [string] $Token
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($Repo -notmatch '^[^/\s]+/[^/\s]+$') {
    Write-Error "Expected 'owner/repo', got '$Repo'"
    exit 1
}

if (-not $Token) {
    $Token = $env:GITHUB_TOKEN
    if (-not $Token) { $Token = $env:GH_TOKEN }
    if (-not $Token) {
        # Read Scoop's config file directly: `scoop config gh_token` writes to the host, so
        # shelling out would leak its output into this script's report.
        $cfgPath = Join-Path $HOME '.config/scoop/config.json'
        if (Test-Path -LiteralPath $cfgPath) {
            try {
                $cfg = Get-Content -LiteralPath $cfgPath -Raw | ConvertFrom-Json
                if ($cfg.PSObject.Properties.Name -contains 'gh_token') { $Token = [string]$cfg.gh_token }
            }
            catch { $Token = $null }
        }
    }
}

$apiUrl = if ($Tag -eq 'latest') {
    "https://api.github.com/repos/$Repo/releases/latest"
} else {
    "https://api.github.com/repos/$Repo/releases/tags/$([uri]::EscapeDataString($Tag))"
}

$headers = @{
    'User-Agent' = 'finch-scoop-skill'
    'Accept'     = 'application/vnd.github+json'
}
if ($Token) { $headers['Authorization'] = "Bearer $Token" }

function Get-JsonViaCurl {
    # Fallback for hosts where .NET TLS fails (corporate cert stores, MITM proxies): curl.exe
    # ships with Windows 10 1803+ and uses its own trust chain.
    param([string] $Uri, [hashtable] $Header)
    $curlArgs = @('-sS', '-L', '--max-time', '60')
    foreach ($k in $Header.Keys) { $curlArgs += @('-H', "$k`: $($Header[$k])") }
    $curlArgs += $Uri
    $text = & curl.exe @curlArgs 2>&1
    if ($LASTEXITCODE -ne 0) { throw "curl.exe failed ($LASTEXITCODE): $text" }
    return ($text | Out-String)
}

$raw = $null
try {
    $release = Invoke-RestMethod -Uri $apiUrl -Headers $headers -ErrorAction Stop
}
catch {
    $status = $null
    foreach ($candidate in @($_.Exception.PSObject.Properties['Response'], $_.Exception.PSObject.Properties['StatusCode'])) {
        if ($candidate -and $null -ne $candidate.Value) { $status = $candidate.Value; break }
    }
    if ("$status" -match '40[13]|429') {
        Write-Error "Request to $apiUrl was rejected ($status). Pass -Token, set GITHUB_TOKEN, or run: scoop config gh_token <token>"
        exit 1
    }
    Write-Verbose "Invoke-RestMethod failed ($($_.Exception.Message)); retrying with curl.exe"
    if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
        Write-Error "Request to $apiUrl failed and curl.exe is unavailable.`n$($_.Exception.Message)"
        exit 1
    }
    try {
        $raw = Get-JsonViaCurl -Uri $apiUrl -Header $headers
        $release = $raw | ConvertFrom-Json
    }
    catch {
        Write-Error "Request to $apiUrl failed.`n$($_.Exception.Message)"
        exit 1
    }
}

$tagName = $release.tag_name
$version = $tagName -replace '^v', ''

Write-Host "Tag:         $tagName"
Write-Host "Version:     $version"
Write-Host "Pre-release: $(if ($release.prerelease) { 'yes' } else { 'no' })"
Write-Host "Published:   $($release.published_at)"
Write-Host ''

$assets = @($release.assets)
if ($assets.Count -eq 0) {
    Write-Warning 'This release has no assets.'
    exit 2
}

function Test-WindowsAsset {
    param([string] $Name)
    # Releases usually ship every platform side by side, so "has x64 in the name" is not
    # enough - an AppImage and a .dmg both match it. Require a Windows marker, and reject
    # explicitly non-Windows platforms unless a Windows marker is also present.
    $isWin = $Name -match '(?i)(windows|win32|win64|win-x64|win-x86|win-arm64|win_x64)'
    $isOtherOs = $Name -match '(?i)(linux|darwin|macos|osx|freebsd|\.dmg$|\.deb$|\.rpm$|\.appimage$|\.pkg$)'
    if ($isOtherOs -and -not ($Name -match '(?i)windows')) { return $false }
    return $isWin
}

function Test-PackageAsset {
    param([string] $Name)
    # Loose files like latest.yml / *.json are release metadata, never a Scoop payload.
    return $Name -match '(?i)\.(exe|zip|msi|7z|tar\.gz|tgz|msix|appx)$'
}

$windows = @($assets | Where-Object { (Test-WindowsAsset $_.name) -and (Test-PackageAsset $_.name) })
$others = @($assets | Where-Object { $windows -notcontains $_ })

if ($windows.Count -eq 0) {
    Write-Warning 'No Windows-looking assets matched. All assets:'
    $assets | ForEach-Object { Write-Host "  - $($_.name) ($($_.size) bytes)" }
    exit 2
}

foreach ($a in $windows) {
    $digest = if ($a.PSObject.Properties.Name -contains 'digest') { [string]$a.digest } else { '' }
    $sha = $digest -replace '^sha256:', ''

    Write-Host "Asset:  $($a.name)"
    Write-Host "  url:    $($a.browser_download_url)"
    Write-Host "  size:   $('{0:N0}' -f $a.size) bytes"
    if ($sha) {
        Write-Host "  sha256: $sha" -ForegroundColor Green
    } else {
        Write-Host "  sha256: <absent - compute with scripts/hashurl.ps1>" -ForegroundColor Yellow
    }
    if ($digest -and $digest -notmatch '^sha256:') {
        Write-Host "  note:   GitHub reports '$digest'; Scoop needs sha256, compute it yourself" -ForegroundColor Yellow
    }
    Write-Host ''
}

if ($others.Count -gt 0) {
    Write-Host 'Other assets (probably not what a Scoop manifest wants):'
    $others | ForEach-Object { Write-Host "  - $($_.name)" }
    Write-Host ''
}

Write-Host 'Reminder: `url` uses the literal version; only `autoupdate.url` uses $version.'
exit 0
