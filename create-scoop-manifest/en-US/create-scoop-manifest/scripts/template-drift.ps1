<#
.SYNOPSIS
    Report how a bucket repository diverges from ScoopInstaller/BucketTemplate.
.DESCRIPTION
    Read-only. Refreshes a shallow clone of the template in a temp directory, then reports the
    template files that are missing or differ here, plus the repo files the template does not
    have. bucket/ and deprecated/ are excluded because they are this bucket's own manifests.

    Run with pwsh. A `powershell` started from a pwsh session inherits PS7's PSModulePath,
    which hides the 5.1 module that ships Get-FileHash.

    Read the printed template HEAD commit subject as well: it states upstream's current policy
    (for example `ci: use pinned actions`), which is why a given diff exists. Without it, a
    policy change looks like noise.
.PARAMETER RepoRoot
    Bucket repository root. Defaults to the git top level of the current directory.
.PARAMETER TemplateDir
    Where to keep the template clone. Reused and refreshed on each run.
.PARAMETER NoDiff
    Only list the drift, skip the per-file unified diff (useful for a quick pass).
.EXAMPLE
    pwsh -NoProfile -File template-drift.ps1 -RepoRoot C:\Users\me\my-bucket
.NOTES
    Only tracked files are compared, so untracked scratch (repomix-output.xml and friends)
    stays out of the report.
#>
[CmdletBinding()]
param(
    [string] $RepoRoot,
    [string] $TemplateDir = (Join-Path ([System.IO.Path]::GetTempPath()) 'opencode/scoop-template'),
    [switch] $NoDiff
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$templateRepo = 'https://github.com/ScoopInstaller/BucketTemplate.git'
$manifestDirs = '^(bucket|deprecated)/'

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error 'git is required. Run: scoop install git'
    exit 1
}

if (-not $RepoRoot) {
    $top = & git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $top) {
        Write-Error 'Not inside a git repository. Pass -RepoRoot <path>.'
        exit 1
    }
    $RepoRoot = $top.Trim()
}

$RepoRoot = (Resolve-Path -LiteralPath $RepoRoot).Path

if (Test-Path -LiteralPath (Join-Path $TemplateDir '.git')) {
    & git -C $TemplateDir fetch --depth 1 --quiet origin HEAD
    if ($LASTEXITCODE -ne 0) {
        Write-Warning 'fetch failed; falling back to a fresh clone'
        Remove-Item -LiteralPath $TemplateDir -Recurse -Force -ErrorAction Ignore
    }
    else {
        & git -C $TemplateDir reset --hard --quiet FETCH_HEAD
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $TemplateDir '.git'))) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $TemplateDir) | Out-Null
    & git clone --depth 1 --quiet $templateRepo $TemplateDir
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to clone $templateRepo"
        exit 1
    }
}

$templateHead = (& git -C $TemplateDir log --oneline -1 | Out-String).Trim()

Write-Host "repo:     $RepoRoot"
Write-Host "template: $templateHead"
Write-Host ''

$templateFiles = @(& git -C $TemplateDir ls-files)
$repoFiles = @(& git -C $RepoRoot ls-files)

# Compare content hashes only for files that exist on both sides.
$drift = [System.Collections.Generic.List[object]]::new()

foreach ($rel in $templateFiles) {
    $templatePath = Join-Path $TemplateDir $rel
    $repoPath = Join-Path $RepoRoot $rel
    if (-not (Test-Path -LiteralPath $repoPath)) {
        $drift.Add([pscustomobject]@{ Kind = 'Missing'; Path = $rel })
    }
    else {
        $a = (Get-FileHash -LiteralPath $templatePath -Algorithm SHA256).Hash
        $b = (Get-FileHash -LiteralPath $repoPath -Algorithm SHA256).Hash
        if ($a -ne $b) {
            $drift.Add([pscustomobject]@{ Kind = 'Differs'; Path = $rel })
        }
    }
}

$extra = @($repoFiles | Where-Object { $_ -notin $templateFiles -and $_ -notmatch $manifestDirs })

if ($drift.Count -eq 0 -and $extra.Count -eq 0) {
    Write-Host 'no drift: every template file matches' -ForegroundColor Green
    exit 0
}

foreach ($d in $drift) { Write-Host ('{0,-8} {1}' -f $d.Kind, $d.Path) }
foreach ($e in $extra) { Write-Host ('{0,-8} {1}' -f 'Extra', $e) }
Write-Host ''

if (-not $NoDiff) {
    foreach ($item in ($drift | Where-Object Kind -eq 'Differs')) {
        Write-Host "===== $($item.Path) ====="
        & git --no-pager diff --no-index --no-color -- `
            (Join-Path $TemplateDir $item.Path) (Join-Path $RepoRoot $item.Path)
        Write-Host ''
    }
}

Write-Host @"
Reminder - these are deliberate customizations, not drift:
  bin/auto-pr.ps1                 carries <owner>/<bucket> instead of the placeholder
  Scoop-Bucket.Tests.ps1          passes -BucketPath `$PSScriptRoot (compatible with scoop core)
  .gitignore, README.md           bucket-specific content
  missing bucket/app-name.json.template, deprecated/.gitkeep
  extra docs/, CLAUDE.md, .claude/, tools/, repomix-output.xml
Never add a new file to bin/ - put helpers in tools/.
"@
exit 0
