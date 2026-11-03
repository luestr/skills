# checkver and autoupdate

Sources: the wiki page [App-Manifest-Autoupdate](https://github.com/ScoopInstaller/Scoop/wiki/App-Manifest-Autoupdate), and the implementation in `lib/autoupdate.ps1` (variable case conversion, hash modes, built-in regexes).

## Table of Contents

- [Division of labor](#division-of-labor)
- [checkver.ps1 parameters](#checkverps1-parameters)
- [checkver strategies](#checkver-strategies)
- [The four source patterns and templates](#the-four-source-patterns-and-templates)
- [autoupdate fields](#autoupdate-fields)
- [The modes of autoupdate.hash](#the-modes-of-autoupdatehash)
- [The complete set of substitutable variables](#the-complete-set-of-substitutable-variables)
- [The case trap in named capture groups](#the-case-trap-in-named-capture-groups)
- [Testing autoupdate](#testing-autoupdate)

---

## Division of labor

- `checkver`: find the upstream's current version number.
- `autoupdate`: once you have the version number, rebuild fields such as `url`, `hash`, and `extract_dir`.
- `bin/checkver.ps1 -u`: write the results of the two steps above back into the manifest.

With only `checkver` and no `autoupdate`, `scoop update <app>` can still discover a new version, but the manifest is not rewritten automatically. **Always configure both**, otherwise every release means hand-editing the three fields `version`, `url`, and `hash`.

---

## checkver.ps1 parameters

```powershell
# Run from the scoop root directory (apps\scoop\current) or the bucket repo root
.\bin\checkver.ps1 <app>
.\bin\checkver.ps1 *                 # all
.\bin\checkver.ps1 <app> -u          # write back when a new version is found
.\bin\checkver.ps1 <app> <dir> -u    # specify a directory (e.g. .\TODO)
```

| Parameter | Short | Description |
|---|---|---|
| `-App` | `-a` | manifest name, wildcard `*` supported |
| `-Dir` | `-d` | search directory |
| `-Update` | `-u` | write back to the manifest |
| `-ForceUpdate` | `-f` | check and update even if the version is unchanged (mandatory for verifying autoupdate) |
| `-SkipUpdated` | `-s` | only list out-of-date manifests |
| `-Version` | `-v` | check with the specified version, usually paired with `-u` |

When troubleshooting, run `scoop config debug $true` first so you can see the actual URL being fetched and the matching process.

---

## checkver strategies

### 1. Pure regex (match on the homepage)

```json
"homepage": "https://www.rust-lang.org",
"checkver": "Version ([\\d.]+)"
```

### 2. Fetch the version from a different URL

```json
"homepage": "https://www.7-zip.org/",
"checkver": {
    "url": "https://www.7-zip.org/download.html",
    "regex": "Download 7-Zip ([\\d.]+)"
}
```

### 3. JSONPath

```json
"checkver": {
    "url": "https://example.com/app.config.json",
    "jsonpath": "$.latestVersion"
}
```

`jsonpath` is equivalent to `jp`. JSONPath can include filter expressions:

```json
"checkver": {
    "url": "https://dist.nuget.org/index.json",
    "jp": "$..versions[?(@.displayName == 'nuget.exe - recommended latest')].version"
}
```

### 4. JSONPath + regex (extract the string first, then match)

When both are present, JSONPath pulls out the string **first**, and **then** the regex is applied to it:

```json
"checkver": {
    "url": "https://nwjs.io/versions.json",
    "jsonpath": "$.stable",
    "regex": "v([\\d.]+)"
}
```

### 5. XPath

```json
"checkver": { "url": "https://example.com/versions.xml", "xpath": "/versions/stable/text()" }
```

### 6. GitHub release

```json
"homepage": "https://github.com/coreybutler/nvm-windows",
"checkver": "github"
```

Internally it matches with `\/releases\/tag\/(?:v|V)?([\d.]+)`. This requires that upstream actually uses the GitHub Releases feature; **prereleases are ignored**.

When the homepage is not the repository, give the repository URL explicitly:

```json
"homepage": "http://cmder.net",
"checkver": { "github": "https://github.com/cmderdev/cmder" }
```

### 7. reverse

By default the **first** occurrence is matched; `reverse: true` matches the **last**:

```json
"checkver": {
    "url": "https://download.videolan.org/pub/videolan/x264/binaries/win64/",
    "regex": "x264-r(?<version>[\\d]+)-(?<commit>[a-fA-F0-9]{7}).exe",
    "reverse": true
}
```

### 8. replace (recompute the version number)

`checkver.replace` can assemble a version from capture groups: `${1}`, `${2}` are unnamed groups, `${name}` is a named group.

```json
"checkver": {
    "url": "https://github.com/lukesampson/pshazz/commits/master.atom",
    "regex": "(\\d+)-(\\d+)-(\\d+)[\\S\\s]*?(?<sha>[0-9a-f]{40})",
    "replace": "0.${1}.${2}.${3}"
}
```

### 9. script (complex fetching)

```json
"checkver": {
    "script": [
        "$page = Invoke-WebRequest 'https://example.com/download' -UseBasicParsing",
        "$page.Links.href | Where-Object { $_ -match 'Setup-([\\d.]+)\\.exe' } | Select-Object -First 1"
    ]
}
```

Suited to cases that require following several links, or where upstream's structure is completely non-standard (UltraVNC, Spotify and the like). The output of `script` is then passed through `regex` (if one is written).

### 10. useragent

A few sites return different content depending on the UA:

```json
"checkver": {
    "url": "https://www.telerik.com/download/fiddler",
    "useragent": "Mozilla/5.0 ..."
}
```

### Keys supported by checkver

| Key | Type | Description |
|---|---|---|
| `github` | URI | repository URL |
| `url` | URI | page to fetch; supports version variables |
| `regex` / `re` | regex | find the version |
| `jsonpath` / `jp` | JSONPath | find the version |
| `xpath` | XPath | find the version |
| `reverse` | bool | take the last match |
| `replace` | string | recompute the version from capture groups; capture variables supported |
| `useragent` | string | custom UA |
| `script` | string / array | PowerShell fetching logic |

---

## The four source patterns and templates

### Pattern A: standard GitHub release (the most common)

Stable version, predictable URL.

```json
{
    "version": "1.2.3",
    "description": "...",
    "homepage": "https://github.com/owner/repo",
    "license": "MIT",
    "architecture": {
        "64bit": {
            "url": "https://github.com/owner/repo/releases/download/v1.2.3/app-x64.exe#/app.exe",
            "hash": ""
        },
        "arm64": {
            "url": "https://github.com/owner/repo/releases/download/v1.2.3/app-arm64.exe#/app.exe",
            "hash": ""
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

zip variant (no renaming):

```json
"url": "https://github.com/owner/repo/releases/download/v1.2.3/app-1.2.3-windows-x64.zip",
"autoupdate": { "url": "https://github.com/owner/repo/releases/download/v$version/app-$version-windows-x64.zip" }
```

Single exe, no architecture split:

```json
"url": "https://github.com/owner/repo/releases/download/v1.2.3/app.exe#/app.exe",
"bin": "app.exe",
"checkver": "github",
"autoupdate": { "url": "https://github.com/owner/repo/releases/download/v$version/app.exe#/app.exe" }
```

### Pattern B: CDN, where the URL carries a token that changes with the version

You need `checkver` to dig the token out with a named capture group, and then `autoupdate.url` fills it back in with `$matchXxx`.

```json
{
    "version": "7.65.8",
    "homepage": "https://example.com/",
    "license": { "identifier": "Freeware" },
    "url": "https://cdn.example.com/9f3a/App-win_64-7.65.8.exe#/dl.7z",
    "hash": "<sha256>",
    "checkver": {
        "url": "https://example.com/api/versions",
        "jp": "$.versions.Windows.download_link",
        "regex": "/(?<id>[\\w]+)/App-(?<arch>[\\w_]+)-([\\d\\.]+)\\.exe"
    },
    "autoupdate": {
        "url": "https://cdn.example.com/$matchId/App-$matchArch-$version.exe#/dl.7z",
        "hash": {
            "url": "https://example.com/api/versions",
            "jp": "$.versions.Windows.hash"
        }
    }
}
```

The key point: **the version must be the only unnamed group** (here `([\d\.]+)`), otherwise checkver takes group 1 as the version number.

### Pattern C: mirror / derived URL

The version is probed from the upstream origin site, while downloads go through a mirror; paths are commonly assembled from `$majorVersion.$minorVersion`.

```json
"checkver": { "url": "https://upstream.example.org/download/", "regex": "blender-([\\d.]+)-windows-x64.zip" },
"autoupdate": {
    "url": "https://mirror.example.cn/blender/$majorVersion.$minorVersion/blender-$version-windows-x64.zip"
}
```

### Pattern D: fetching artifacts behind signed / rotating links

The landing page or API hands out a tokenized link that changes on every request. Here **the page itself cannot serve as the `url`** (its content changes every time, so the hash is not reproducible); you have to locate the real public CDN object.

Decision procedure:

1. Fetch once with the URL stripped of its query, and once more with a garbage key in it.
2. Compare `ETag` / `x-goog-generation` with the signed response to see whether they agree.
3. If they agree, the token is only decoration, so use it directly: `https://.../App-$version.exe#/dl.7z`, while `checkver` still watches the official page.
4. Turn the changing path segments into named groups, but **keep the version as the first unnamed group**.

```json
"url": "https://dl.example.com/obj/app-$version.exe#/dl.7z",
"checkver": {
    "url": "https://example.com/download",
    "regex": "app-([\\d.]+)\\.exe"
}
```

---

## autoupdate fields

```json
"autoupdate": {
    "note": "Thanks for using autoupdate, please test your updates!",
    "architecture": {
        "64bit": { "url": "https://example.org/dl/example-v$version-x64.msi" },
        "32bit": { "url": "https://example.org/dl/example-v$version-x86.msi" }
    },
    "hash": { "url": "$baseurl/SHASUMS256.txt.asc" }
}
```

Fields that may go inside `autoupdate`: `bin`, `extract_dir`, `extract_to`, `env_add_path`, `env_set`, `installer`, `license`, `note`, `persist`, `post_install`, `psmodule`, `shortcuts`, and — most importantly — `url` and `hash`.

- Except for `note`, every field can be written **globally** or under `architecture.<arch>`. A global value is used to update the field for the corresponding architecture — so a single global `autoupdate.url` updates both `architecture.64bit.url` and `architecture.32bit.url`.
- Except for `hash`, every field supports capture variables and version variables.

**`autoupdate.url` must be a template that holds for any future version**. A static `url` must never contain `$version` — that is the number one cause of 404s.

### Architecture examples (nodejs / php / nginx / imagemagick)

```json
"autoupdate": {
    "architecture": {
        "64bit": { "url": "https://nodejs.org/dist/v$version/node-v$version-win-x64.7z", "extract_dir": "node-v$version-win-x64" },
        "32bit": { "url": "https://nodejs.org/dist/v$version/node-v$version-win-x86.7z", "extract_dir": "node-v$version-win-x86" }
    },
    "hash": { "url": "$baseurl/SHASUMS256.txt.asc" }
}
```

```json
"autoupdate": { "url": "https://nginx.org/download/nginx-$version.zip", "extract_dir": "nginx-$version" }
```

```json
"autoupdate": {
    "architecture": {
        "64bit": { "url": "https://www.imagemagick.org/download/binaries/ImageMagick-$version-portable-Q16-x64.zip" },
        "32bit": { "url": "https://www.imagemagick.org/download/binaries/ImageMagick-$version-portable-Q16-x86.zip" }
    },
    "hash": { "mode": "rdf", "url": "https://www.imagemagick.org/download/binaries/digest.rdf" }
}
```

---

## The modes of autoupdate.hash

The **values actually accepted** by `autoupdate.hash.mode` (checked against the `switch ($hashmode)` in `lib/autoupdate.ps1`):

| mode | Where it reads from | Key options | How it gets selected |
|---|---|---|---|
| `extract` | a plain-text file or web page | `url` + `regex`/`find` | the default; also applies when `hash.url` is written without any other hint |
| `json` | a JSON file | `url` + `jsonpath`/`jp` | switches here automatically when `jp` or `jsonpath` is written |
| `xpath` | an XML file | `url` + `xpath` | switches here automatically when `xpath` is written |
| `rdf` | an RDF file | `url` | must be written explicitly as `"mode": "rdf"` |
| `metalink` | the download response headers, or `<url>.meta4` | `url` may be omitted | must be written explicitly as `"mode": "metalink"` |

**`mode: "download"` is not a legal value** — there is no such branch in the switch, so writing it is the same as not writing it (it falls back to `extract`). "Download, then compute locally" is a **fallback behavior**, not a mode: when no mode obtained a hash, Scoop prints `Downloading ... to compute hashes!` and actually downloads.

This distinction matters: you cannot use `mode: download` to **force** it to stop parsing web pages. If you want it to download and compute directly, write only `"hash": {}` or simply omit `hash` altogether.

There are two more predefined modes that are selected **automatically**, with no `hash` written:

- `fosshub`: becomes active when `autoupdate.url` matches `^(?:.*fosshub.com\/).*(?:\/|\?dwl=)(?<filename>.*)$`, with the internal regex `$basename.*?"sha256":"([a-fA-F0-9]{64})"`.
- `sourceforge`: becomes active when `autoupdate.url` matches `(?:downloads\.)?sourceforge.net\/projects?\/(?<project>[^\/]+)\/(?:files\/)?(?<file>.*)`, with the internal regex `"$basename":.*?"sha1":\s*"([a-fA-F0-9]{40})"`. Note that it redirects the request to `https://sourceforge.net/projects/<project>/files/<file>`, because `downloads.sourceforge.net` does not provide checksums.

**And there is a third one that the wiki never documents** — the `github` automatic mode:

- When `autoupdate.url` matches `https://github.com/<owner>/<repo>/releases/download/<tag>/<file>`, `hashmode` automatically becomes `github`.
- It queries `https://api.github.com/repos/<owner>/<repo>/releases` and pulls out that asset's digest with `$..assets[?(@.browser_download_url == '<your url>')].digest`.

This explains a common phenomenon: **a standard GitHub release manifest updates its hash even with nothing at all written in `autoupdate.hash`**. Conversely, if your `autoupdate.url` looks like a GitHub release but is not actually there (a mirror, a private CDN), this automatic mode queries for an asset that does not exist and then falls back to "download, then compute locally". To avoid that silent downgrade, write `hash.url` + `find`/`jp` explicitly.

### extract (default)

When `find` is left empty, two built-in regexes are tried **in order** (`find_hash_in_textfile` in `lib/autoupdate.ps1`):

```text
1)  ^\s*([a-fA-F0-9]+)\s*$                     # the whole file holds just one hash (leading/trailing whitespace allowed)
2)  ([a-fA-F0-9]{32,128})[\x20\t]+.*$basename(?:\s|$)|$basename[\x20\t]+.*?([a-fA-F0-9]{32,128})
```

The second one is a **two-directional match**: both `hash<space>filename` and `filename<space>hash` hit. That means both checksum-file layouts work out of the box:

```text
abcdef01... *example.zip           ← hash first
example.zip  abcdef01...           ← filename first
```

The first one has `\s*` on both sides, so a single-line hash file ending in a newline or spaces works directly too (the original wiki wrote `^([a-fA-F0-9]+)$`, which fails to match a file with a trailing newline).

If neither built-in regex hits, one more attempt is made with the metalink regex for the `<hash...>` form, `'<hash[^>]+>([a-fA-F0-9]{64})'`.

When that is not enough, customize it:

```json
"hash": {
    "url": "$baseurl/hashes.txt",
    "find": "SHA256\\($basename\\)=\\s+([a-fA-F\\d]{64})"
}
```

```json
"hash": {
    "url": "https://www.python.org/downloads/release/python-$cleanVersion/",
    "find": "$basename[\\S\\s]+?$md5"
}
```

### json

```json
"hash": {
    "mode": "json",
    "jp": "$.files.['$basename'].sha512",
    "url": "$baseurl/win32_openssl_hashes.json"
}
```

Filter expressions work in JSONPath here as well:

```json
"hash": { "mode": "json", "jsonpath": "$..versions[?(@.downloadText == '$basename')].sha256", "url": "..." }
```

### xpath / rdf

```json
"hash": { "url": "https://example.com/chrome.xml", "xpath": "/chromechecker/stable64[version=\"$version\"]/sha256" }
"hash": { "mode": "rdf", "url": "https://www.imagemagick.org/download/binaries/digest.rdf" }
```

### metalink

```json
"hash": { "mode": "metalink" }
```

Read from the response headers of the download URL, or from a `.meta4` file in the same directory.

### Building hash.url from capture / version / URL variables

```json
"checkver": { "regex": "<strong>(?<year>\\d{4})-(?<month>\\d{2})-(?<day>\\d{2})</strong>...(?<version>[\\d.a-z\\-]+)" },
"autoupdate": {
    "architecture": {
        "64bit": {
            "url": "https://example.org/w64/qemu-w64-setup-$matchYear$matchMonth$matchDay.exe#/dl.7z",
            "hash": { "url": "https://example.org/w64/qemu-w64-setup-$matchYear$matchMonth$matchDay.sha512" }
        }
    }
}
```

```json
"hash": { "url": "https://julialang-s3.julialang.org/bin/checksums/julia-$version.sha256" }
"hash": { "url": "$url_fossies.sha256" }
```

### What happens when hash extraction fails

Results of the three cases, **verified by experiment** (calling `Invoke-AutoUpdate` directly, bypassing the network version probe):

| The manifest's autoupdate | Result |
|---|---|
| `{ "hash": { "url": ... } }` (hash present, no url) | **`version` is changed to the new version and `hash` is written as the empty string `""`**, exit code 0, and the log only says `Writing updated ... manifest`. The manifest is silently destroyed. |
| `{ "url": ... }` (url present, no hash) | Prints `Downloading <file> to compute hashes!` → actually downloads → `Computed hash: ...` → writes the correct hash. |
| `{ "url": ..., "hash": { "url": ... } }` (both present but no match on the vendor page) | `Searching hash for ... in ...` → `Could not find hash in ...` → falls back to local download and computation → writes the correct hash. |

So:

- **If `autoupdate` has a `hash`, it must also have a `url`**, otherwise every `checkver -u` blanks the hash once more. This is more dangerous than "an empty hash will not be updated automatically", because it actively destroys a correct hash that already exists.
- The local-download fallback is itself reliable (given a network and a reachable `autoupdate.url`), just slow.
- Once an empty hash has been written into the manifest, **later `checkver -u` runs cannot repair it either** — in `Update-ManifestProperty`, an empty `$Manifest.hash` falls into the `architecture` branch, and that step also requires `$Manifest.architecture` to exist, otherwise calling `Get-Member` on `$null` errors out. At that point the only way out is to fix it by hand with `hashurl.ps1`.

### Vendor checksums vs. computing them yourself

When the vendor publishes a checksum file (such as `SHA256SUMS`):

1. Use it for cross-validation;
2. Point `autoupdate.hash` at it (`url` + `regex`/`jp`), and **do not** let it drift into the local-download fallback.

The reason: the vendor's checksum proves "what the vendor published", whereas a locally computed one only proves "what the CDN gave me".

---

## The complete set of substitutable variables

### Capture variables

**Inside `checkver.replace`**:

- `${1}`, `${2}`, `${3}`…: unnamed groups
- `${name1}`, `${Name2}`: named groups (`(?<name1>...)`)

**Inside `autoupdate`**:

- `$match1`, `$match2`…: unnamed groups
- `$matchName1`, `$matchName2`…: named groups

### Version variables

These come from `Get-VersionVariables` in `lib/autoupdate.ps1` (checked against the implementation). `$Version` is first split on `-` into `$firstPart` (the first segment) and `$lastPart` (the last segment):

| Variable | Implementation | Result for `3.7.1.2-rc.1` |
|---|---|---|
| `$version` | as-is | `3.7.1.2-rc.1` |
| `$dotVersion` | `[._-]` → `.` | `3.7.1.2.rc.1` |
| `$underscoreVersion` | `[._-]` → `_` | `3_7_1_2_rc_1` |
| `$dashVersion` | `[._-]` → `-` | `3-7-1-2-rc-1` |
| `$cleanVersion` | delete `[._-]` | `3712rc1` |
| `$majorVersion` | segment 1 of `$firstPart` | `3` |
| `$minorVersion` | segment 2 of `$firstPart` | `7` |
| `$patchVersion` | segment 3 of `$firstPart` | `1` |
| `$buildVersion` | segment 4 of `$firstPart` | `2` |
| `$preReleaseVersion` | `$lastPart` | `rc.1` |
| `$matchHead` | the head of the regex `(?<head>\d+\.\d+(?:\.\d+)?)(?<tail>.*)` | `3.7.1` |
| `$matchTail` | the tail of the same regex | `.2-rc.1` |

Four easy mistakes:

1. **The `$majorVersion` family splits `$firstPart` (the part before `-`)**, not the whole version string. `1.0-beta.5` is only split over `1.0`, and `$patchVersion` is empty.
2. **`$preReleaseVersion` is literally the last segment of `Split('-')`**, not "a general parse of everything after the last `-`"; when the version contains no `-`, it equals the whole version string.
3. **`$dotVersion` exists and is useful**: `1.2.3_4` → `1.2.3.4`, more reliable than writing your own replace.
4. **`$matchHead` / `$matchTail` are only added to the variable table when the version number looks like `<number>.<number>[.<number>]`**; otherwise these two keys simply do not exist, and using them in a template leaves them verbatim in the generated url.

Note: the original wiki table lists `$underscoreVersion` as `3_7_1_2-rc_1` (replacing dots only), which is wrong — the implementation replaces all three classes in `[._-]`.

### URL variables

Injected by `get_hash_for_app`, five in total (`$urlNoExt` / `$basenameNoExt` are not documented in the wiki):

| Variable | Meaning | Example (url = `https://e.com/a/b/app-1.2.3.exe#/dl.7z`) |
|---|---|---|
| `$url` | the autoupdate URL with the `#` fragment stripped | `https://e.com/a/b/app-1.2.3.exe` |
| `$baseurl` | `$url` with the filename removed and the trailing slash removed | `https://e.com/a/b` |
| `$basename` | the filename (after URL decoding, fragment ignored) | `app-1.2.3.exe` |
| `$urlNoExt` | `$url` with the extension removed | `https://e.com/a/b/app-1.2.3` |
| `$basenameNoExt` | `$basename` with the extension removed | `app-1.2.3` |

`$basename` goes through `UrlDecode`, so when the filename contains encodings such as `%20` you get the decoded real name; `$baseurl` runs `TrimEnd('/')`, so concatenating `$baseurl/x.sha256` never produces a double slash.

### Hash variables (for simplifying regexes inside `hash.find`)

| Variable | Equivalent regex |
|---|---|
| `$md5` | `([a-fA-F0-9]{32})` |
| `$sha1` | `([a-fA-F0-9]{40})` |
| `$sha256` | `([a-fA-F0-9]{64})` |
| `$sha512` | `([a-fA-F0-9]{128})` |
| `$checksum` | `([a-fA-F0-9]{32,128})` |
| `$base64` | `([a-zA-Z0-9+\/=]{24,88})` |

---

## The case trap in named capture groups

The name of a named-group variable inside `autoupdate` is generated by this code (`lib/autoupdate.ps1`):

```powershell
$versionVariables.Add('$match' + (Get-Culture).TextInfo.ToTitleCase($_.Name), $_.Value)
```

`ToTitleCase` is **not "capitalize the first letter"**; it capitalizes the first letter of every word and **lowercases the remaining letters**. The consequences:

| Group name | Generated variable | What you assumed |
|---|---|---|
| `(?<build>...)` | `$matchBuild` | ✅ |
| `(?<buildId>...)` | `$matchBuildid` | ❌ `$matchBuildId` |
| `(?<build_id>...)` | `$matchBuild_Id` | ❌ `$matchBuild_id` |

**Rule: use only single lowercase words as named group names.** When you need several words, switch to shorter single words (`id`, `arch`, `file`, `path`, `sha`, `type`).

There are two real counterexamples in the main bucket worth remembering:

- `camunda-operate`: the group is named `(?<genVer>...)`, and autoupdate writes `$matchGenver` — the names line up, **but the other way round**: what the program generates is `$matchGenver`, and what the manifest writes is `$matchGenVer`. This is the most insidious kind, because when reading the code "genVer with a capital first letter" looks entirely natural.
- `ngrok`: the group named `hashArm64` generates `$matchHasharm64`, and the manifest writes `$matchHasharm64` **correctly**. So when you see such "abnormal" casing, do not change it first — compute the ToTitleCase result first.

Fully lowercase group names (`date`, `arch`, `vs`, `version`) have no problem at all — after ToTitleCase they are identical to simple first-letter capitalization.

### Another related pitfall: the first unnamed group steals the version number

checkver treats the **first unnamed capture group** as the version number. Therefore:

```json
"regex": "/(?<id>[\\w]+)/App-(?<arch>[\\w_]+)-([\\d\\.]+)\\.exe"   // ✅ the version is the only unnamed group
"regex": "/([\\w]+)/App-(?<arch>[\\w_]+)-([\\d\\.]+)\\.exe"        // ❌ the version has become id
```

Either make the version the only unnamed group, or name the version `version` and write no unnamed groups at all (named groups only serve as a fallback when group 1 is empty).

---

## Testing autoupdate

```powershell
cd <bucket repo>
scoop config debug $true
.\bin\checkver.ps1 <app> -u
```

Alternatively, lower the `version` and run it again (or use `-f`) to confirm that `url`, `hash`, and `extract_dir` are all rewritten correctly. Then `scoop install bucket\<app>.json` to install, run, and uninstall.

**Note that `checkver -f` only proves "the flow runs through", not "the hash was actually computed"** — when the hash is already correct, it writes the same value back. To verify the hash-computation path:

1. Temporarily change the hash to 64 `0`s (not the empty string — an empty hash goes down the `architecture` branch and stays empty);
2. Clear `SCOOP_CACHE`;
3. Run `checkver -f`;
4. See whether it comes back to the real value you committed.

Do this on a temporary copy (that is exactly how the `scripts/provehash` logic in this skill is designed), and do not pollute `bucket/`.

Manifests in the known buckets are patrolled automatically by [ScoopInstaller/GithubActions](https://github.com/ScoopInstaller/GithubActions) (commonly known as Excavator): `main` / `extras` hourly, `versions` / `java` / `php` / `games` daily.

### Daily workflow

```powershell
cd <bucket repo>
.\bin\checkver * -u        # update everything
git commit -m "Updated apps"
git push
scoop update
scoop status               # now you see the real version difference
scoop update <app>
```
