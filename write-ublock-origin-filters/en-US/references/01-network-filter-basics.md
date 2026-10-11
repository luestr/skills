# Network Filter Basics

> URL pattern matching fundamentals for uBlock Origin network filters.

## Filter Syntax Overview

```
pattern [$options]
@@pattern [$options]    (exception/allowlist)
```

- **pattern** — URL address mask; every request URL is matched against this
- **`@@`** — Exception marker; rules starting with `@@` allowlist requests
- **options** — Parameters after `$` that limit/change rule behavior

## Special Characters

### `*` — Wildcard

Matches any set of characters (empty string or any length). Used to fill gaps in URL patterns.

```
||example.com/ads/*
```
Matches: `https://example.com/ads/banner.jpg`, `https://example.com/ads/video.mp4`

### `||` — Domain Anchor

Matches the beginning of a URL, covering the scheme and domain. Equivalent to matching `https://*.`, `http://*.`, `ws://*.`, `wss://*.` simultaneously. This is the most commonly used pattern anchor.

```
||example.com^
```
Blocks:
- `https://example.com/ad1.gif`
- `https://subdomain.example.com/ad1.gif`
- `https://ads.example.com:8000/`

Does NOT block:
- `https://example.org/`
- `https://example.com.us/ad1.gif`

### `^` — Separator Character

A separator is any character **except** letters, digits, `_`, `-`, `.`, `%`. The end of the URL is also treated as a separator.

```
||example.com^
```
This is the standard way to match a domain and all its paths/queries while ensuring the domain boundary is respected.

### `|` — URL Start/End Marker

Depending on placement, matches the beginning or end of the URL.

**End marker:**
```
.swf|
```
Matches: `https://example.com/annoyingflash.swf`
Does NOT match: `https://example.com/swf/index.html`

**Start marker:**
```
|https://example.org
```
Matches: `https://example.org`
Does NOT match: `https://domain.com?url=https://example.org`

**Exact match (both markers):**
```
|https://example.org/|
```
Matches only `https://example.org/` exactly.

### Important Limitation

`|`, `||`, `^` can only be used in network filter patterns (URL matching). They cannot be used in cosmetic filter selectors (e.g., `||example.com##.advert` is invalid).

## Regular Expression Filters

For more flexible matching, use regular expressions enclosed in `/`:

```
/banner\d+/$third-party
```
Applies regex `banner\d+` to all third-party requests.

```
@@/banner\d+/
```
Exception rule for the above regex pattern.

**Performance note:** Regex filters are slower to evaluate — prefer plain patterns with `||`, `^`, `*` when possible, and limit regex scope to specific domains via `$domain=`.

## HOSTS File Parsing

uBO can parse HOSTS file-like resources. All hostname entries are interpreted as equivalent to `||hostname^` filters.

**Ambiguity resolution:** A bare entry like `example.com` is interpreted by uBO as `||example.com^` (block the site and all subdomains), NOT as "block URLs containing `example.com`" (which is the ABP interpretation).

To force ABP-style interpretation (contains match), add a wildcard:
```
example.com*
```

To ensure a filename is not parsed as a hostname, prepend with a slash:
```
/example.js
```

**Important:** uBO's HOSTS interpretation includes blocking the main document itself (strict blocking). See the `document` option for details.

## `_` aka "noop"

A placeholder option that does nothing. Used to resolve parsing ambiguity, especially with `$removeparam` filters that use regex parameters (which could be misinterpreted as plain regex filters):

```
/ad-$removeparam=/^foo=bar\d$/,_
```

Starting from 1.50.1b11, multiple `_` options are supported for readability:
```
||example.com$_,removeparam=/^ss\\$/,_,image
||example.com$replace=/bad/good/,___,~third-party
```

## `*` aka "all URLs" Pattern

The wildcard `*` as the entire pattern applies a filter to **all** URLs. Always narrow with options:

- `*$third-party` — Block all 3rd-party network requests
- `*$script,domain=example.com` — Block all script requests on example.com
- `*$image,important` — Force-block all images

Usually, dynamic filtering rules are more convenient for broad blocking.

## Filter Examples

```adblock
||example.com/ads/*
```
Matches: `https://example.com/ads/banner.jpg`, `https://subdomain.example.com/ads/otherbanner.jpg`

```adblock
||example.org^$third-party
```
Blocks third-party requests to example.org and its subdomains

```adblock
@@||example.com$document
```
Completely allowlists example.com and all subdomains

```adblock
||tracker.example.com^$important
```
Force-blocks tracker.example.com even if there's an exception rule

```adblock
/ad[-_]?banner/
```
Regex filter matching ad-banner, ad_banner, or adbanner patterns
