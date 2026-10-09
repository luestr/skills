---
name: Write uBlockOrigin Filters
description: "Complete uBlock Origin (uBO) static filter syntax reference. Use this skill when writing uBlock Origin custom filters for ad blocking, privacy protection, or content filtering. Covers basic network filter patterns (||, *, ^, |), all network filter options ($domain, $third-party, $important, $redirect, $removeparam, $csp, $replace, $header, $method, $denyallow, $badfilter, $all, etc.), content type options ($script, $image, $stylesheet, $font, $media, $xhr, $popup, $document, $frame, etc.), cosmetic filters (element hiding ##, CSS selectors, entity matching, hostname regex), procedural cosmetic filters (:has, :has-text, :matches-css, :upward, :xpath, :matches-path, :watch-attr, etc.), action operators (:remove, :style, :remove-attr, :remove-class), HTML filters (##^), response header filtering (##^responseheader), scriptlet injection (##+js()), and pre-parsing directives (!#include, !#if). Trigger when user mentions uBlock Origin filters, uBO filter syntax, ad blocking filter rules, element hiding rules, procedural cosmetic selectors, scriptlet injection, or wants to write/debug any type of uBO-compatible filter list. Use this skill even when the user is just writing or debugging uBlock Origin filter rules, creating custom filter lists, or migrating filters from AdBlock Plus/AdGuard to uBO."
---

# uBlock Origin Static Filter Syntax Reference

> Source: https://github.com/gorhill/uBlock/wiki/Static-filter-syntax

This skill is a complete reference index for uBlock Origin (uBO) static filter syntax. **Do not load all reference files at once** — load only the relevant file based on the user's question to save tokens.

## Quick Routing: Which File to Load

| User Need | Load File |
|---|---|
| Basic URL pattern matching (`*`, `\|\|`, `^`, `\|`), HOSTS file parsing, `_` (noop), `*` (all URLs) | `references/01-network-filter-basics.md` |
| Content type options: `$script`, `$image`, `$stylesheet`/`$css`, `$font`, `$media`, `$subdocument`/`$frame`, `$object`, `$other`, `$ping`, `$websocket`, `$xhr`, `$popup`, `$document`, `$top` | `references/02-content-type-options.md` |
| Behavior modifiers: `$third-party`/`$3p`, `$first-party`/`$1p`, `$domain`/`$from`, `$to`, `$match-case`, `$important`, `$badfilter`, `$denyallow`, `$method`, `$header`, `$strict1p`, `$strict3p`, `$all`, `$elemhide`/`$ehide`, `$generichide`/`$ghide`, `$specifichide`/`$shide`, `$popunder`, `$inline-script`, `$inline-font`, `$cname`, `$ipaddress`, `$permissions` | `references/03-behavior-modifiers.md` |
| Modifier filters (response modification): `$csp`, `$redirect`, `$redirect-rule`, `$removeparam`, `$replace`, `$uritransform`, `$urlskip`, `$empty`, `$mp4` | `references/04-modifier-filters.md` |
| Cosmetic filters (element hiding `##`/`#@#`), entity matching, hostname regex, specific-generic, procedural cosmetic filters (`:has()`, `:has-text()`, `:matches-css()`, `:upward()`, `:xpath()`, `:matches-path()`, `:watch-attr()`, etc.), action operators (`:remove()`, `:style()`, `:remove-attr()`, `:remove-class()`) | `references/05-cosmetic-filters.md` |
| HTML filters (`##^`), response header filtering (`##^responseheader()`) | `references/06-html-response-header-filters.md` |
| Scriptlet injection (`##+js()`), available scriptlets, redirect resources, resources library | `references/07-scriptlet-injection.md` |
| Pre-parsing directives (`!#include`, `!#if`/`!#else`/`!#endif`), unsupported features, compatibility notes | `references/08-preparsing-directives.md` |

## Rule Types Quick Reference

### 1. Network Filters — Block/Allow URL Requests

```
pattern [$options]
@@pattern [$options]    (exception/allowlist)
```

- `||example.com^` — Block all requests to example.com and subdomains
- `|https://example.com/ad.js|` — Exact URL match
- `@@||example.com^` — Allowlist example.com
- `||example.com^$important` — Force rule (overrides exceptions)

### 2. Cosmetic Filters — Hide/Modify Page Elements

- `example.com##.ad-banner` — Hide element
- `example.com#@#.ad-banner` — Exception (unhide)
- `example.com##h1:style(color: red !important)` — Inject CSS style
- `example.com##.ad:remove()` — Remove element from DOM

### 3. HTML Filters — Remove HTML Before Browser Parsing (Firefox only)

- `example.com##^script:has-text(adScript)` — Remove script tag from response

### 4. Response Header Filtering — Remove Response Headers

- `example.com##^responseheader(refresh)` — Remove refresh header

### 5. Scriptlet Injection — Inject JavaScript

- `example.com##+js(set-constant, adBlockDetected, false)` — Inject scriptlet

## Key Concepts

- **Comments**: Lines starting with `!` are comments
- **Exception rules**: Rules starting with `@@` allowlist requests
- **Options/Modifiers**: Parameters after `$` that limit/change rule behavior
- **Domain restriction**: `$domain=` in network filters, hostname prefix in cosmetic/extended filters
- **Third-party**: `$third-party` (`$3p`) restricts to cross-site requests
- **HOSTS file format**: uBO interprets bare hostnames like `example.com` as `||example.com^`
- **Trusted source**: Only uBO's own filter lists and user's "My filters" (if enabled) are trusted for `$replace`, scriptlet injection, etc.
- **Entity matching**: `google.*` matches all Google TLDs (google.com, google.co.uk, etc.)
- **Hostname regex**: `/regex/` as hostname in extended filters (use sparingly for performance)

## Important: uBO vs ABP/AdGuard Differences

| Feature | uBO | ABP/AdGuard |
|---|---|---|
| `document` for entire page exception | ❌ Not supported | ✅ Supported |
| `genericblock` | ❌ Not supported | ✅ Supported |
| `$webrtc` option | ❌ Use `##+js(nowebrtc)` | ✅ Supported |
| `$replace` filter | Trusted sources only | More permissive |
| HOSTS file interpretation | `example.com` → `\|\|example.com^` | `example.com` matches anywhere in URL |
| `$badfilter` | ✅ Supported | Partial |
| `$denyallow` | ✅ Supported | ❌ Not supported |
| HTML filtering (`##^`) | Firefox only | CoreLibs apps |
| Scriptlet naming | uBO native + AG compatibility | AG native |
