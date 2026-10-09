---
name: WriteAdGuardFilters
description: "Complete AdGuard filtering rules syntax reference. Use this skill when writing AdGuard custom filters. Covers basic rule syntax, all modifiers ($domain/$third-party/$important/$redirect/$replace/$removeparam/$cookie/$csp etc.), cosmetic rules (element hiding/CSS/Extended CSS selectors), HTML filtering, JavaScript/scriptlet rules, non-basic rule modifiers, preprocessor directives, and debugging. Trigger when user mentions AdGuard filtering rules, ad blocking rule syntax, filter list authoring, ABP syntax compatibility, element hiding rules, Extended CSS selectors (:has/:contains/:matches-css etc.). Use this skill even when the user is just writing or debugging any type of ad filtering rules."
---

# AdGuard Filtering Rules Syntax Reference

> Source: https://adguard.com/kb/general/ad-filtering/create-own-filters/

This skill is a complete reference index for AdGuard filtering rule syntax. **Do not load all reference files at once** — load only the relevant file based on the user's question to save tokens.

## Quick Routing: Which File to Load

| User Need | Load File |
|---|---|
| Basic rule syntax, special chars (`*`, `\|\|`, `^`, `\|`), regex, TLD wildcards | `references/01-basic-rules-syntax.md` |
| `$domain`, `$third-party`, `$important`, `$match-case`, `$app`, `$denyallow`, `$header`, `$method`, `$popup`, `$strict-first-party`, `$strict-third-party`, `$to` | `references/02-basic-modifiers.md` |
| `$document`, `$image`, `$script`, `$stylesheet`, `$font`, `$media`, `$subdocument`, `$websocket`, `$xmlhttprequest`, `$ping`, `$object`, `$other` | `references/03-content-type-modifiers.md` |
| Exception rule (`@@`) modifiers: `$elemhide`, `$content`, `$urlblock`, `$jsinject`, `$stealth`, `$extension`; Generic rules: `$genericblock`, `$generichide`, `$specifichide` | `references/04-exception-modifiers.md` |
| `$all`, `$badfilter`, `$cookie`, `$csp`, `$hls`, `$inline-script`, `$inline-font`, `$jsonprune`, `$xmlprune`, `$network`, `$permissions`, `$redirect`, `$redirect-rule`, `$referrerpolicy`, `$removeheader`, `$removeparam`, `$replace`, `$urltransform`, `$reason`, `noop`, `$empty`(deprecated), `$mp4`(deprecated) | `references/05-advanced-modifiers.md` |
| Rule priority calculation, priority conflict resolution | `references/06-rule-priorities.md` |
| Cosmetic rules (element hiding `##`, CSS rules `#$#`), Extended CSS selectors (`:has()`, `:contains()`, `:matches-css()`, `:matches-attr()`, `:matches-property()`, `:xpath()`, `:nth-ancestor()`, `:upward()`, `:remove()`, `:is()`, `:not()`) | `references/07-cosmetic-rules.md` |
| HTML filtering rules (`$$`), special attributes (`tag-content`, `wildcard`, `max-length`, `min-length`), `:contains()` pseudo-class | `references/08-html-filtering.md` |
| JavaScript rules (`#%#`), scriptlet rules (`//scriptlet()`), trusted scriptlets | `references/09-javascript-scriptlet.md` |
| Non-basic rule modifiers: `[$domain=...]`, `[$app=...]`, `[$path=...]`, `[$url=...]` syntax | `references/10-non-basic-modifiers.md` |
| Preprocessor directives (`!#include`, `!#if`/`!#else`/`!#endif`, `!#safari_cb_affinity`), hints (`NOT_OPTIMIZED`, `PLATFORM`/`NOT_PLATFORM`, `NOT_VALIDATE`), debugging (filtering log, selector debugging, scriptlet debugging), compatibility legend | `references/11-preprocessor-debugging.md` |
| **Safari/iOS limitations**, SafariConverterLib compatibility details, Content Blocker limitations, trusted filter definitions, removed/deprecated modifier list | `references/12-restrictions-safari.md` |

## Rule Types Quick Reference

### 1. Basic Rules — Block/Allow URL Requests

```
rule = ["@@"] pattern ["$" modifiers]
```

- `||example.com^` — Block all requests to example.com and subdomains
- `|https://example.com|` — Exact URL match
- `@@||example.com^` — Allow example.com
- `||example.com^$important` — Force rule (overrides exceptions)

### 2. Cosmetic Rules — Hide/Modify Page Elements

- `example.com##.ad-banner` — Hide element
- `example.com#$#body { background: #fff; }` — Inject CSS
- `example.com#?#div:has(> .ad)` — Extended CSS selector
- `example.com#@#.ad-banner` — Exception (unhide)

### 3. HTML Filtering Rules — Modify HTML Before Page Load

- `example.com$$script[data-src="banner"]` — Remove HTML element
- `example.com$@$script[data-src="banner"]` — Exception

### 4. JavaScript Rules — Inject JS Code

- `example.com#%#window.__gaq = undefined;` — Execute JS

### 5. Scriptlet Rules — Declarative JS Functions

- `example.com#%#//scriptlet('abort-on-property-read', 'alert')` — Use scriptlet

## Key Concepts

- **Comments**: Lines starting with `!` are comments
- **Exception rules**: Rules starting with `@@` allow requests
- **Modifiers**: Parameters after `$` that limit/change rule behavior
- **Domain restriction**: `$domain=` or domain prefix in cosmetic rules
- **Third-party**: `$third-party` (`$3p`) restricts to cross-site requests
- **Minimum rule length**: 4 characters, otherwise treated as invalid
- **URL truncation**: AdGuard truncates URLs to 4096 characters for faster matching
- **Trusted filters**: `$replace`, `$hls`, JavaScript rules, scriptlet rules etc. can only be used in trusted filters

## Compatibility Quick Reference

| Abbreviation | Meaning |
|---|---|
| CoreLibs apps | AdGuard for Windows/Mac/Android/Linux |
| AdGuard for Chromium | Chrome/Edge/Opera extension |
| AdGuard for Chrome MV3 | Chrome MV3 extension |
| AdGuard for Firefox | Firefox extension |
| AdGuard for iOS | iOS Safari |
| AdGuard for Safari | Desktop Safari |
| AdGuard Content Blocker | Android Samsung/Yandex browsers |

| Symbol | Meaning |
|---|---|
| ✅ | Fully supported |
| ✅ * | Supported with limitations |
| ❌ | Not supported |
| 👎 | Deprecated |
| 🚫 | Removed |
