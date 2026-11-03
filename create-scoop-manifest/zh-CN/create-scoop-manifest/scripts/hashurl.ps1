<#
.SYNOPSIS
    Compute the SHA256 of one or more URLs, ready to paste into a Scoop manifest.
.DESCRIPTION
    Strips the Scoop '#' fragment (a Scoop directive, not part of the HTTP URL), sends Scoop's
    user agent, and prints lowercase SHA256 - Scoop's default hash type, so no prefix is needed.
    Pass every architecture URL for a multi-arch manifest.

    Use pwsh, not powershell: a powershell started from a pwsh session inherits PS7's
    PSModulePath, which shadows the 5.1 Utility module and breaks Get-FileHash.
.PARAMETER Url
    One or more URLs, with or without a '#/name.ext' fragment.
.PARAMETER Algorithm
    SHA256 (default), SHA512, SHA1 or MD5. Non-SHA256 results get the Scoop prefix automatically.
.PARAMETER OutFile
    Optional path to write 'url<TAB>hash' lines, handy for multi-arch manifests.
.EXAMPLE
    pwsh -NoProfile -File hashurl.ps1 'https://example.com/app-x64.exe#/app.exe'
.EXAMPLE
    pwsh -NoProfile -File hashurl.ps1 'https://e.com/a.exe#/dl.7z' 'https://e.com/b.exe#/dl.7z' -OutFile hashes.txt
.NOTES
    Ground truth for the fragment rule: lib/download.ps1 in Scoop core uses the fragment only for
    the local filename; the HTTP request never includes it.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]] $Url,

    [ValidateSet('SHA256', 'SHA512', 'SHA1', 'MD5')]
    [string] $Algorithm = 'SHA256',

    [string] $OutFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Scoop sends this UA when it downloads manifests and artifacts.
$userAgent = 'Scoop/1.0 (+http://scoop.sh/) (PowerShell Core)'

function Get-HashWithAlgorithm {
    param([Parameter(Mandatory)] [string] $Path, [Parameter(Mandatory)] [string] $Algo)
    # Use the static Create() API: Get-FileHash is unavailable in some shadows of the 5.1 module
    # and the static API works identically in 5.1 and 7+.
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $hashAlgo = [System.Security.Cryptography.HashAlgorithm]::Create($Algo)
        try {
            $bytes = $hashAlgo.ComputeHash($stream)
            return (($bytes | ForEach-Object { $_.ToString('x2') }) -join '')
        }
        finally { $hashAlgo.Dispose() }
    }
    finally { $stream.Dispose() }
}

function Format-ScoopHash {
    param([string] $Hash, [string] $Algo)
    switch ($Algo) {
        'SHA256' { return $Hash }
        'SHA512' { return "sha512:$Hash" }
        'SHA1'   { return "sha1:$Hash" }
        'MD5'    { return "md5:$Hash" }
    }
}

$results = @()
$failed = 0

foreach ($raw in $Url) {
    # Strip the fragment: '#/dl.7z' only tells Scoop what to name the file locally.
    $httpUrl = ($raw -split '#', 2)[0]
    if ($httpUrl -notmatch '^(?i)https?://') {
        Write-Error "Not an http(s) URL: $raw"
        $failed++
        continue
    }

    $tmp = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "hashurl-$([guid]::NewGuid().ToString('n')).tmp")
    try {
        Write-Host "Downloading $httpUrl ... " -NoNewline
        Invoke-WebRequest -Uri $httpUrl -OutFile $tmp -UserAgent $userAgent -MaximumRedirection 10 -ErrorAction Stop
        $size = (Get-Item -LiteralPath $tmp).Length
        $hash = Get-HashWithAlgorithm -Path $tmp -Algo $Algorithm
        $formatted = Format-ScoopHash -Hash $hash -Algo $Algorithm
        Write-Host ("{0:N0} bytes" -f $size) -ForegroundColor Green

        Write-Host "  url:  $raw"
        Write-Host "  hash: $formatted"
        Write-Host ''

        $results += [pscustomobject]@{ Url = $raw; Hash = $formatted }
    }
    catch {
        Write-Host 'FAILED' -ForegroundColor Red
        Write-Error "  $raw`n  $($_.Exception.Message)"
        $failed++
    }
    finally {
        if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction Ignore }
    }
}

if ($results.Count -gt 1) {
    Write-Host 'JSON array, ready to paste as "hash":'
    $json = '[' + (($results | ForEach-Object { '"' + $_.Hash + '"' }) -join ', ') + ']'
    Write-Host "  $json"
    Write-Host ''
}

if ($OutFile) {
    $results | ForEach-Object { "$($_.Url)`t$($_.Hash)" } | Set-Content -LiteralPath $OutFile -Encoding utf8
    Write-Host "Written to $OutFile"
}

if ($failed -gt 0) { exit 1 }
exit 0
