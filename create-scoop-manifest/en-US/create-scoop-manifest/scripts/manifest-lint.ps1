<#
.SYNOPSIS
    Offline static lint for a Scoop app manifest. No network, no install.
.DESCRIPTION
    Catches the mistakes that otherwise only surface at `scoop install` time or after a
    broken autoupdate silently writes an empty hash:

      - required fields missing / wrong type
      - hash shape (algorithm prefix, length, lowercase) and url/hash pairing
      - architecture block sanity (32bit-only apps may omit it, everything else may not)
      - autoupdate.url reproducing the static url for the current version
      - $version leaking into a static url (a guaranteed 404)
      - named capture groups whose name will not survive Scoop's ToTitleCase transform
      - an unnamed capture group before the version in checkver.regex
      - array-of-one style, deprecated fields, field ordering

    Exit code: 0 when there are no errors, 1 when at least one error was reported.
    Warn-level rows are informational and never change the exit code.
.PARAMETER Path
    One or more manifest paths, or a directory (its bucket/*.json and *.json are linted).
.PARAMETER Strict
    Also report field-ordering deviations as errors instead of warnings.
.EXAMPLE
    pwsh -NoProfile -File manifest-lint.ps1 bucket\myapp.json
.EXAMPLE
    pwsh -NoProfile -File manifest-lint.ps1 .\bucket -Quiet
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]] $Path,

    [switch] $Strict,

    [switch] $Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Official field order from CONTRIBUTING.md.
$fieldOrder = @(
    'version', 'description', 'homepage', 'license', 'notes', 'depends', 'suggest',
    'architecture', 'extract_dir', 'extract_to', 'pre_install', 'installer', 'post_install',
    'env_add_path', 'env_set', 'bin', 'shortcuts', 'persist', 'pre_uninstall', 'uninstaller',
    'post_uninstall', 'checkver', 'autoupdate'
)

$findings = [System.Collections.Generic.List[object]]::new()

function Add-Finding {
    param(
        [string] $App,
        [string] $Check,
        [ValidateSet('error', 'warn', 'info')] [string] $Level,
        [string] $Detail,
        [string] $Fix
    )
    $findings.Add([pscustomobject]@{ App = $App; Check = $Check; Level = $Level; Detail = $Detail; Fix = $Fix })
}

function Get-Prop {
    param($Object, [string] $Name)
    if ($null -eq $Object) { return $null }
    if ($Object -is [System.Collections.IDictionary]) {
        if ($Object.Contains($Name)) { return $Object[$Name] }
        return $null
    }
    $p = $Object.PSObject.Properties[$Name]
    if ($p) { return $p.Value }
    return $null
}

function Test-HasProp {
    param($Object, [string] $Name)
    if ($null -eq $Object) { return $false }
    if ($Object -is [System.Collections.IDictionary]) { return $Object.Contains($Name) }
    return $null -ne $Object.PSObject.Properties[$Name]
}

# Scoop picks the FIRST unnamed capture group as the version, unless a group is literally
# named 'version'. Emulate that so a regex whose version is group 2 gets flagged.
function Get-VersionGroupInfo {
    param([string] $Regex)
    $named = @([regex]::Matches($Regex, '\(\?<([A-Za-z_][A-Za-z0-9_]*)>'))
    # Unnamed groups only: `(?!\?)` already excludes (?: (?= (?! (?< (?'
    $allGroups = @([regex]::Matches($Regex, '\((?!\?)'))
    $unnamedCount = $allGroups.Count
    $names = @($named | ForEach-Object { $_.Groups[1].Value })
    return [pscustomobject]@{
        Named        = $names
        UnnamedCount = $unnamedCount
        # The `$matchXxx` keys Scoop will actually create for these names.
        MatchKeys    = @($names | ForEach-Object { '$match' + (Get-Culture).TextInfo.ToTitleCase($_) })
    }
}

function Get-ExpectedUrl {
    # Substitute the documented variable set into an autoupdate url template so it can be
    # compared with the manifest's static url.
    #
    # Mirrors Scoop's own `substitute` in lib/core.ps1: keys sorted by length descending and
    # replaced with a literal .Replace() - NO word boundary. That is why `$version_windows_amd64`
    # expands to `3.5.0_windows_amd64` in real manifests; a \b-anchored regex would miss it and
    # report a false mismatch.
    param([string] $Template, [string] $Version)

    $parts = $Version -split '\.'
    $first = ($Version -split '-')[0]
    $firstParts = $first -split '\.'
    $matchHeadMatch = [regex]::Match($Version, '^(?<head>\d+\.\d+(?:\.\d+)?)(?<tail>.*)$')

    $vars = [ordered]@{
        '$version'           = $Version
        '$dotVersion'        = ($Version -replace '[._-]', '.')
        '$underscoreVersion' = ($Version -replace '[._-]', '_')
        '$dashVersion'       = ($Version -replace '[._-]', '-')
        '$cleanVersion'      = ($Version -replace '[._-]', '')
        '$majorVersion'      = if ($firstParts.Count -gt 0) { $firstParts[0] } else { '' }
        '$minorVersion'      = if ($firstParts.Count -gt 1) { $firstParts[1] } else { '' }
        '$patchVersion'      = if ($firstParts.Count -gt 2) { $firstParts[2] } else { '' }
        '$buildVersion'      = if ($firstParts.Count -gt 3) { $firstParts[3] } else { '' }
        '$preReleaseVersion' = (($Version -split '-')[-1])
    }
    if ($matchHeadMatch.Success) {
        $vars['$matchHead'] = $matchHeadMatch.Groups['head'].Value
        $vars['$matchTail'] = $matchHeadMatch.Groups['tail'].Value
    }

    foreach ($k in ($vars.Keys | Sort-Object { $_.Length } -Descending)) {
        $Template = $Template.Replace($k, [string]$vars[$k])
    }
    return $Template
}

function Resolve-Targets {
    param([string[]] $Paths)
    $out = @()
    foreach ($p in $Paths) {
        if (Test-Path -LiteralPath $p -PathType Container) {
            $sub = Join-Path $p 'bucket'
            if (Test-Path -LiteralPath $sub -PathType Container) {
                $out += @(Get-ChildItem -LiteralPath $sub -Filter '*.json' -File | ForEach-Object { $_.FullName })
            }
            $out += @(Get-ChildItem -LiteralPath $p -Filter '*.json' -File | ForEach-Object { $_.FullName })
        }
        elseif (Test-Path -LiteralPath $p) {
            $out += (Resolve-Path -LiteralPath $p).Path
        }
        else {
            Add-Finding -App $p -Check 'lint:path' -Level 'error' -Detail 'Path does not exist' -Fix 'Check the path'
        }
    }
    # Always return an array: a single path would otherwise come back as a bare string and
    # .Count would fail under Set-StrictMode. The unary comma stops PowerShell from
    # unwrapping a one-element array on return.
    return ,@($out | Select-Object -Unique)
}

function Test-Manifest {
    param([string] $File)

    $app = [System.IO.Path]::GetFileNameWithoutExtension($File)

    try {
        $raw = Get-Content -LiteralPath $File -Raw
        $m = $raw | ConvertFrom-Json -ErrorAction Stop
    }
    catch {
        Add-Finding -App $app -Check 'lint:json' -Level 'error' -Detail $_.Exception.Message -Fix 'Fix the JSON syntax'
        return
    }

    if ($m -isnot [pscustomobject]) {
        Add-Finding -App $app -Check 'lint:json' -Level 'error' -Detail 'Manifest is not a JSON object' -Fix 'Rewrite the manifest'
        return
    }

    # ---- required fields -------------------------------------------------
    foreach ($f in @('version', 'description', 'homepage', 'license')) {
        if (-not (Test-HasProp $m $f) -or [string]::IsNullOrWhiteSpace([string](Get-Prop $m $f))) {
            Add-Finding -App $app -Check "lint:missing-$f" -Level 'error' `
                -Detail "'$f' is missing or empty" -Fix "Add a valid '$f'"
        }
    }

    $version = [string](Get-Prop $m 'version')

    if (Test-HasProp $m 'description') {
        $desc = [string](Get-Prop $m 'description')
        $descWords = $desc.ToLower()
        if ($descWords.StartsWith($app.Replace('-', ' ').ToLower() + ' ') -or $descWords.StartsWith($app.ToLower() + ' ')) {
            Add-Finding -App $app -Check 'lint:description' -Level 'warn' `
                -Detail 'Description starts with the app name' -Fix 'Drop the app name from the description'
        }
        if ($desc.Length -gt 256) {
            Add-Finding -App $app -Check 'lint:description' -Level 'warn' -Detail 'Description is longer than 256 chars' -Fix 'Keep it to one line'
        }
    }

    if (Test-HasProp $m 'homepage') {
        $hp = [string](Get-Prop $m 'homepage')
        if ($hp -notmatch '^(?i)https?://') {
            Add-Finding -App $app -Check 'lint:homepage' -Level 'error' -Detail "homepage is not http(s): $hp" -Fix 'Use a full URL'
        }
    }

    # ---- license ---------------------------------------------------------
    $license = Get-Prop $m 'license'
    $licenseId = $null
    if ($license -is [string]) { $licenseId = $license }
    elseif ($license -is [pscustomobject]) {
        $licenseId = [string](Get-Prop $license 'identifier')
        if (-not $licenseId) {
            Add-Finding -App $app -Check 'lint:license' -Level 'error' `
                -Detail 'license object has no identifier' -Fix 'Add identifier (SPDX id or Freeware/Proprietary/...)'
        }
        $licenseUrl = Get-Prop $license 'url'
        if ($licenseUrl -and ([string]$licenseUrl -notmatch '^(?i)https?://')) {
            Add-Finding -App $app -Check 'lint:license' -Level 'warn' -Detail "license.url is not http(s): $licenseUrl" -Fix 'Use a full URL'
        }
    }
    elseif ($null -ne $license) {
        Add-Finding -App $app -Check 'lint:license' -Level 'error' -Detail 'license must be a string or an object' -Fix 'See manifest-reference.md'
    }

    if ($licenseId) {
        $known = @('Freeware', 'Proprietary', 'Public Domain', 'Shareware', 'Unknown')
        $single = ($licenseId -split '[|,]' | ForEach-Object { $_.Trim() })
        $unknown = @($single | Where-Object { $_ -and ($_ -notin $known) })
        if ($unknown.Count -gt 0) {
            # A plain SPDX id is also fine; only flag things that look like prose.
            foreach ($u in $unknown) {
                if ($u -match '\s' -or $u -match '^(?i)(apache|mit|bsd|gpl|lgpl|agpl|mpl|isc|unlicense|zlib|wtfpl)\b' -eq $false -and $u -match ' ') {
                    Add-Finding -App $app -Check 'lint:license' -Level 'warn' -Detail "Unrecognized license token: '$u'" -Fix 'Use an SPDX id or Freeware/Proprietary/Public Domain/Shareware/Unknown'
                }
            }
        }
    }

    # ---- deprecated / stray fields --------------------------------------
    foreach ($dep in @('msi', '_comment')) {
        if (Test-HasProp $m $dep) {
            Add-Finding -App $app -Check "lint:deprecated-$dep" -Level 'error' `
                -Detail "'$dep' is deprecated" -Fix $(if ($dep -eq 'msi') { 'Remove it; .msi is extracted like a zip' } else { 'Use "##" for comments' })
        }
    }
    if (Test-HasProp $m 'cookie') {
        Add-Finding -App $app -Check 'lint:cookie' -Level 'warn' -Detail "'cookie' is undocumented" -Fix 'Avoid unless the bucket requires it'
    }

    # ---- url / hash ------------------------------------------------------
    $urlTop = Get-Prop $m 'url'
    $hashTop = Get-Prop $m 'hash'
    $arch = Get-Prop $m 'architecture'
    $archKeys = @()
    if ($arch -is [pscustomobject]) { $archKeys = @($arch.PSObject.Properties.Name) }

    if ($archKeys.Count -eq 0) {
        if (-not $urlTop) {
            Add-Finding -App $app -Check 'lint:url-missing' -Level 'error' -Detail 'No url and no architecture block' -Fix 'Add a url'
        }
        if (-not $hashTop -and $null -eq $hashTop) {
            Add-Finding -App $app -Check 'lint:hash-missing' -Level 'error' -Detail 'No hash' -Fix 'Compute with scripts/hashurl.ps1'
        }
        elseif ([string]::IsNullOrWhiteSpace([string]$hashTop)) {
            Add-Finding -App $app -Check 'lint:hash-missing' -Level 'error' `
                -Detail 'hash is an empty string' -Fix 'Seed a real hash; Scoop only autoupdates a non-empty hash'
        }
    }
    elseif (-not ($archKeys.Count -eq 1 -and $archKeys[0] -eq '32bit')) {
        # Only a 32bit-only app may skip architecture; having the block is required otherwise.
        foreach ($k in $archKeys) {
            if ($k -notin @('64bit', '32bit', 'arm64')) {
                Add-Finding -App $app -Check 'lint:architecture' -Level 'error' -Detail "Unknown architecture key '$k'" -Fix 'Use 64bit / arm64 / 32bit'
            }
        }
    }

    # Gather url/hash pairs from the top level and from every architecture branch.
    $pairs = @()
    if ($urlTop) {
        $urls = @($urlTop)
        $hashes = @()
        if ($null -ne $hashTop) { $hashes = @($hashTop) }
        if ($hashes.Count -ne $urls.Count) {
            Add-Finding -App $app -Check 'lint:url-hash-count' -Level 'error' `
                -Detail "url has $($urls.Count) entries, hash has $($hashes.Count)" -Fix 'URLS and hashes count mismatch'
        }
        for ($i = 0; $i -lt $urls.Count; $i++) {
            $pairs += [pscustomobject]@{ Scope = 'top level'; Url = [string]$urls[$i]; Hash = if ($i -lt $hashes.Count) { [string]$hashes[$i] } else { '' } }
        }
    }
    if ($arch -is [pscustomobject]) {
        foreach ($k in $archKeys) {
            $branch = $arch.$k
            $bs = Get-Prop $branch 'url'
            $hs = Get-Prop $branch 'hash'
            if (-not $bs) { continue }
            $branches = @($bs)
            # An if-expression unwraps a one-element array, so build the array explicitly.
            $bh = @()
            if ($null -ne $hs) { $bh = @($hs) }
            if ($bh.Count -ne $branches.Count) {
                Add-Finding -App $app -Check 'lint:url-hash-count' -Level 'error' `
                    -Detail "architecture.$k url has $($branches.Count) entries, hash has $($bh.Count)" -Fix 'URLS and hashes count mismatch'
            }
            for ($i = 0; $i -lt $branches.Count; $i++) {
                $pairs += [pscustomobject]@{ Scope = "architecture.$k"; Url = [string]$branches[$i]; Hash = if ($i -lt $bh.Count) { [string]$bh[$i] } else { '' } }
            }
        }
    }

    foreach ($p in $pairs) {
        # URL-shape checks run regardless of the hash, so one bad manifest reports everything
        # that is wrong with it in a single pass instead of one issue per run.
        if ($p.Url -match '\$version') {
            Add-Finding -App $app -Check 'lint:version-in-url' -Level 'error' `
                -Detail "$($p.Scope): static url contains `$version" -Fix 'Use the literal version in url; only autoupdate.url uses $version'
        }
        if ($p.Url -match '#(?!/)') {
            Add-Finding -App $app -Check 'lint:url-fragment' -Level 'warn' `
                -Detail "$($p.Scope): fragment should start with '#/'" -Fix 'Write #/name.ext'
        }

        if ([string]::IsNullOrWhiteSpace($p.Hash)) {
            Add-Finding -App $app -Check 'lint:hash-missing' -Level 'error' `
                -Detail "$($p.Scope): a url has no hash" -Fix 'Compute with scripts/hashurl.ps1'
            continue
        }
        $h = $p.Hash
        $algo = 'sha256'
        if ($h -match '^([A-Za-z0-9]+):(.*)$') {
            $algo = $Matches[1].ToLower()
            $h = $Matches[2]
            if ($algo -notin @('sha256', 'sha512', 'sha1', 'md5')) {
                Add-Finding -App $app -Check 'lint:hash-format' -Level 'error' -Detail "$($p.Scope): unknown hash algorithm '$algo'" -Fix 'Use sha256/sha512/sha1/md5 or no prefix'
            }
        }
        $expectedLen = switch ($algo) { 'md5' { 32 } 'sha1' { 40 } 'sha256' { 64 } 'sha512' { 128 } default { 64 } }
        if ($h -notmatch '^[a-fA-F0-9]+$') {
            Add-Finding -App $app -Check 'lint:hash-format' -Level 'error' -Detail "$($p.Scope): hash is not hex" -Fix 'Paste the raw hex digest'
        }
        elseif ($h.Length -ne $expectedLen) {
            Add-Finding -App $app -Check 'lint:hash-format' -Level 'error' `
                -Detail "$($p.Scope): $algo hash is $($h.Length) chars, expected $expectedLen" -Fix 'Recompute the hash'
        }
        elseif ($h -cne $h.ToLower()) {
            Add-Finding -App $app -Check 'lint:hash-format' -Level 'warn' -Detail "$($p.Scope): hash contains uppercase" -Fix 'Scoop lowercases it; store lowercase'
        }
    }

    # ---- hint: -1 style or single-element arrays ------------------------
    foreach ($arrField in @('bin', 'shortcuts', 'persist', 'depends', 'env_add_path', 'notes', '##')) {
        $val = Get-Prop $m $arrField
        if ($val -is [array] -and $val.Count -eq 1 -and $val[0] -is [string]) {
            Add-Finding -App $app -Check 'lint:style' -Level 'info' `
                -Detail "'$arrField' is a single-element array" -Fix 'Write it as a plain string'
        }
    }

    # ---- duplicates with no effect --------------------------------------
    if ($urlTop -and $archKeys.Count -gt 0) {
        $archHasUrl = @($archKeys | Where-Object { Test-HasProp $arch.$_ 'url' }).Count -gt 0
        if ($archHasUrl) {
            Add-Finding -App $app -Check 'lint:url-scope' -Level 'warn' `
                -Detail 'Both a top-level url and per-architecture urls exist' -Fix 'Keep only the per-architecture urls'
        }
    }

    # ---- installer traps -------------------------------------------------
    $installer = Get-Prop $m 'installer'
    if ($installer -is [pscustomobject]) {
        $hasFile = Test-HasProp $installer 'file'
        $hasArgs = Test-HasProp $installer 'args'
        $hasScript = Test-HasProp $installer 'script'
        if ($hasScript -and ($hasFile -or $hasArgs)) {
            Add-Finding -App $app -Check 'lint:installer-order' -Level 'warn' `
                -Detail 'installer has both script and file/args: the binary runs FIRST, then the script' `
                -Fix 'For a pure unpack, keep only installer.script'
        }
    }

    # ---- autoupdate vs static url ---------------------------------------
    $checkver = Get-Prop $m 'checkver'
    $autoupdate = Get-Prop $m 'autoupdate'

    if (-not $checkver) {
        Add-Finding -App $app -Check 'lint:checkver-missing' -Level 'warn' `
            -Detail 'No checkver' -Fix 'Add one, or explain in "##" why the upstream has no trackable version'
    }
    if (-not $autoupdate) {
        if ($checkver) {
            Add-Finding -App $app -Check 'lint:autoupdate-missing' -Level 'error' `
                -Detail 'checkver without autoupdate: version bumps must be done by hand' -Fix 'Add autoupdate'
        }
    }
    else {
        # Keep arrays intact: [string] on a string[] joins with spaces, which then gets
        # compared as one giant url and produces nonsense diffs for multi-url manifests.
        $auUrlValue = Get-Prop $autoupdate 'url'
        $auArch = Get-Prop $autoupdate 'architecture'
        $auArchUrl = $null
        if ($auArch -is [pscustomobject]) {
            # An empty architecture object makes .Name return $null, and @($null) would be a
            # one-element array holding nothing - filter it out before indexing.
            $auArchKeys = @($auArch.PSObject.Properties | ForEach-Object { $_.Name } | Where-Object { $_ })
            foreach ($k in $auArchKeys) {
                $candidate = Get-Prop $auArch.$k 'url'
                if ($candidate) { $auArchUrl = $candidate; break }
            }
        }
        $template = if ($auUrlValue) { $auUrlValue } elseif ($auArchUrl) { $auArchUrl } else { $null }

        if (-not $template) {
            # An autoupdate with nothing in it cannot rewrite anything.
            $auHash = Get-Prop $autoupdate 'hash'
            if ($auHash) {
                Add-Finding -App $app -Check 'lint:autoupdate-no-url' -Level 'error' `
                    -Detail 'autoupdate has a hash but no url: checkver -u writes "hash": "" and exits 0' `
                    -Fix 'Add a version-less autoupdate.url'
            }
        }
        else {
            if ($template -notmatch '\$version|\$match|\$majorVersion|\$minorVersion|\$cleanVersion|\$underscoreVersion|\$dashVersion') {
                # A constant autoupdate.url is legitimate: some upstreams serve a stable
                # filename (autoit's autoit-v3.zip) or a rolling snapshot (cc65), so only the
                # version/checksum change. Worth noting, not an error.
                Add-Finding -App $app -Check 'lint:autoupdate-static' -Level 'info' `
                    -Detail 'autoupdate.url has no substitution variable: the url never changes' -Fix 'Fine if upstream uses a stable filename; otherwise use $version or $matchXxx'
            }
            # Compare every static url against the template for its own scope, one url at a
            # time. Comparing only the first pair missed multi-url manifests, and comparing
            # joined arrays produced nonsense diffs (bun, lua, gawk all served multiple urls).
            $scopes = @($pairs | Where-Object { $_.Url } | ForEach-Object { $_.Scope } | Select-Object -Unique)

            foreach ($scope in $scopes) {
                $scopePairs = @($pairs | Where-Object { $_.Url -and $_.Scope -eq $scope })
                if ($scopePairs.Count -eq 0) { continue }

                # Pick the autoupdate template that matches this url's scope, so a per-arch
                # static url is compared against its own per-arch template.
                $cmpTemplate = $template
                if ($scope -ne 'top level' -and $auArch -is [pscustomobject]) {
                    $archName = ($scope -split '\.')[1]
                    if (Test-HasProp $auArch $archName) {
                        $t = Get-Prop $auArch.$archName 'url'
                        if ($t) { $cmpTemplate = $t }
                    }
                }

                # An array template has one entry per static url; keep them as separate
                # entries so each url is compared with its own template.
                $cmpTemplates = @()
                foreach ($entry in @($cmpTemplate)) { if ($null -ne $entry) { $cmpTemplates += [string]$entry } }
                if ($cmpTemplates.Count -eq 0) { continue }

                $joined = $cmpTemplates -join ' '
                if ($joined -match '\$match') {
                    # `$matchXxx` values come from whatever the checkver regex captured off the
                    # upstream page - they cannot be derived offline from the static url, so any
                    # comparison here would be a guess. Report it as info, never as an error.
                    Add-Finding -App $app -Check 'lint:autoupdate-verify-online' -Level 'info' `
                        -Detail "$scope`: autoupdate.url uses `$match variables; only checkver -u can confirm it reproduces the static url" `
                        -Fix 'Run: bin\checkver.ps1 <app> -u, then review the diff'
                    continue
                }

                if ($cmpTemplates.Count -ne $scopePairs.Count) {
                    Add-Finding -App $app -Check 'lint:autoupdate-url-count' -Level 'error' `
                        -Detail "$scope`: manifest declares $($scopePairs.Count) url(s) but autoupdate has $($cmpTemplates.Count)" `
                        -Fix 'Keep autoupdate urls one-to-one with the static urls'
                    continue
                }

                for ($i = 0; $i -lt $scopePairs.Count; $i++) {
                    $actual = ($scopePairs[$i].Url -split '#', 2)[0]
                    $raw = $cmpTemplates[$i]
                    $expected = (Get-ExpectedUrl -Template $raw -Version $version) -split '#', 2
                    $expected = $expected[0]
                    if ($expected -ne $actual) {
                        Add-Finding -App $app -Check 'lint:autoupdate-mismatch' -Level 'error' `
                            -Detail "$scope`: autoupdate.url expands to '$expected' but the static url is '$actual'" `
                            -Fix 'Make the template reproduce today''s url exactly'
                    }
                }
            }
        }

        # Hash handling. Two rules that come from lib/autoupdate.ps1 rather than the wiki:
        #   - `mode: download` is not a real switch branch; it silently falls back to extract.
        #   - a GitHub release url gets hashmode 'github' automatically (digest via the API),
        #     so a missing autoupdate.hash there is fine.
        $auHash = Get-Prop $autoupdate 'hash'
        if ($auHash -is [pscustomobject]) {
            $mode = [string](Get-Prop $auHash 'mode')
            if ($mode -eq 'download') {
                Add-Finding -App $app -Check 'lint:autoupdate-hash' -Level 'warn' `
                    -Detail "'mode: download' is not a supported hash mode; it falls back to extract" `
                    -Fix 'Drop the mode (download-compute is the automatic fallback) or use extract/json/xpath/rdf/metalink'
            }
            if (-not $template -and $mode -and $mode -notin @('metalink')) {
                Add-Finding -App $app -Check 'lint:autoupdate-hash' -Level 'error' `
                    -Detail "hash.mode '$mode' without autoupdate.url: nothing can be fetched" -Fix 'Add autoupdate.url'
            }
        }

        if ($template -and -not $auHash) {
            $isGithubRelease = $template -match '^https://github\.com/[^/]+/[^/]+/releases/download/[^/]+/[^/]+'
            if (-not $isGithubRelease) {
                Add-Finding -App $app -Check 'lint:autoupdate-hash' -Level 'info' `
                    -Detail 'no autoupdate.hash: every update downloads the artifact to hash it locally' `
                    -Fix 'Point hash.url at the vendor checksum file when one exists'
            }
        }
    }

    # ---- checkver regex capture-group rules -----------------------------
    $regex = $null
    $cvGithub = $false
    # Only the bare string `"checkver": "github"` derives the repo from homepage. The object
    # form `{ "github": "<repo>" }` states the repo explicitly, so homepage is free to be a
    # product site - that is the documented workaround, not a defect. Conflating the two
    # produced ~770 false errors across the main bucket.
    $cvGithubExplicit = $false
    if ($checkver -is [string]) {
        if ($checkver -ne 'github') { $regex = $checkver } else { $cvGithub = $true }
    }
    elseif ($checkver -is [pscustomobject]) {
        $r = Get-Prop $checkver 'regex'
        if (-not $r) { $r = Get-Prop $checkver 're' }
        if ($r) { $regex = [string]$r }
        $g = Get-Prop $checkver 'github'
        if ($g) {
            $cvGithub = $true
            $cvGithubExplicit = $true
            # The repo host is github.com, but the API host (api.github.com/.../releases,
            # /tags, /releases/latest) is idiomatic for jsonpath/regex-based checkver and
            # appears throughout the official buckets. Accept both.
            if ([string]$g -notmatch '^(?i)https?://(www\.|api\.)?github\.com/') {
                Add-Finding -App $app -Check 'lint:checkver-github' -Level 'error' `
                    -Detail "checkver.github is not a github url: $g" -Fix 'Use https://github.com/<owner>/<repo> (or the api.github.com equivalent)'
            }
        }
    }

    if ($cvGithub -and -not $cvGithubExplicit) {
        $homepage = [string](Get-Prop $m 'homepage')
        if ($homepage -notmatch '^(?i)https?://(www\.)?github\.com/[^/]+/[^/]+/?$') {
            Add-Finding -App $app -Check 'lint:checkver-github' -Level 'error' `
                -Detail "``checkver: github`` reads the repo from homepage, but homepage is not a repo url: $homepage" `
                -Fix 'Point homepage at the repo, or use { "github": "<repo url>" } explicitly'
        }
    }

    if ($regex) {
        try { [void][regex]::new($regex) }
        catch {
            Add-Finding -App $app -Check 'lint:checkver-regex' -Level 'error' -Detail "regex does not compile: $($_.Exception.Message)" -Fix 'Fix the regex'
            $regex = $null
        }
    }

    if ($regex) {
        $info = Get-VersionGroupInfo -Regex $regex
        # Where the match variables actually get consumed. Only groups referenced there can
        # break an update; a mixed-case group nobody references (neovim's `patchVersion` is
        # used only by the checkver regex itself) is harmless.
        $autoupdateText = if ($autoupdate) { $autoupdate | ConvertTo-Json -Depth 12 -Compress } else { '' }
        foreach ($name in $info.Named) {
            $title = (Get-Culture).TextInfo.ToTitleCase($name)
            $documented = '$match' + $name.Substring(0, 1).ToUpper() + $name.Substring(1)
            # The bug is an inner capital in the ORIGINAL name: ToTitleCase lowercases the rest
            # of each word, so `buildId` silently becomes `$matchBuildid`. A name that is already
            # all-lowercase (date/arch/vs/version) title-cases to exactly the documented variable
            # and is perfectly fine - comparing $title -cne $name flagged those too.
            if ($name -cnotmatch '[a-z][A-Z]') { continue }

            $referenced = ($autoupdateText -match [regex]::Escape($documented))
            if ($referenced) {
                Add-Finding -App $app -Check 'lint:matchvar-case' -Level 'error' `
                    -Detail "autoupdate uses $documented, but group '$name' produces `$match$title - the variable resolves empty" `
                    -Fix "Rename the group to a single lowercase word, or use `$match$title"
            }
            else {
                Add-Finding -App $app -Check 'lint:matchvar-case' -Level 'warn' `
                    -Detail "group '$name' would produce `$match$title (not $documented); harmless unless you reference it in autoupdate" `
                    -Fix 'Prefer a single lowercase word for group names'
            }
        }
        if ($info.UnnamedCount -gt 1 -and ('version' -notin $info.Named)) {
            Add-Finding -App $app -Check 'lint:checkver-groups' -Level 'warn' `
                -Detail "$($info.UnnamedCount) unnamed groups and no group named 'version'" `
                -Fix 'Keep the version as the only unnamed group, or name it version'
        }
        if ($info.UnnamedCount -gt 1) {
            $firstUnnamed = [regex]::Match($regex, '\((?!\?)([^)]*)\)')
            if ($firstUnnamed.Success) {
                $body = $firstUnnamed.Groups[1].Value
                if ($body -notmatch 'version' -and $body -notmatch '\\d') {
                    Add-Finding -App $app -Check 'lint:checkver-groups' -Level 'warn' `
                        -Detail "First unnamed group '($body)' does not look like a version and will be used as one" `
                        -Fix 'Move the version to the first unnamed group'
                }
            }
        }
    }

    # ---- field ordering --------------------------------------------------
    $props = @($m.PSObject.Properties.Name)
    $lastIdx = -1
    $lastName = $null
    foreach ($p in $props) {
        if ($p -in @('##', '$schema')) { continue }
        $idx = [array]::IndexOf($fieldOrder, $p)
        if ($idx -lt 0) { continue }
        if ($idx -lt $lastIdx) {
            Add-Finding -App $app -Check 'lint:field-order' -Level $(if ($Strict) { 'error' } else { 'warn' }) `
                -Detail "'$p' appears after '$lastName' but belongs earlier" -Fix 'Follow the official field order'
        }
        $lastIdx = $idx
        $lastName = $p
    }

    # ---- time to report --------------------------------------------------
    $mine = @($findings | Where-Object App -eq $app)
    if ($mine.Count -eq 0 -and -not $Quiet) {
        Write-Host "$app : ok" -ForegroundColor Green
    }
}

$targets = Resolve-Targets -Paths $Path
if ($targets.Count -eq 0) {
    Write-Host 'No manifests found.' -ForegroundColor Yellow
    exit 1
}

foreach ($t in $targets) { Test-Manifest -File $t }

if ($findings.Count -eq 0) {
    Write-Host "lint: no problems found in $($targets.Count) manifest(s)" -ForegroundColor Green
    exit 0
}

$findings |
    Sort-Object @{ Expression = { switch ($_.Level) { 'error' { 0 } 'warn' { 1 } default { 2 } } } }, App, Check |
    Format-Table -AutoSize -Wrap App, Check, Level, Detail |
    Out-String -Width 200 |
    Write-Host

$errors = @($findings | Where-Object Level -eq 'error').Count
$warns = @($findings | Where-Object Level -eq 'warn').Count
Write-Host "$errors error(s), $warns warning(s) across $($targets.Count) manifest(s)" -ForegroundColor $(if ($errors) { 'Red' } else { 'Yellow' })

if ($errors -gt 0) { exit 1 }
exit 0
