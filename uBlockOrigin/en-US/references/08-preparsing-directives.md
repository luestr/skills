# Pre-parsing Directives, Unsupported Features & Compatibility

> Preprocessor directives for conditional compilation, features uBO does not support, and platform compatibility notes.

## Pre-parsing Directives (1.16.0+)

Pre-parsing directives are prefixed with `!#` so older uBO versions and other blockers treat them as comments and discard them. They execute **before** a list's content is parsed and influence the final filter list content.

### `!#include [file name]`

Import another filter list in place of the directive. The sub-list **must** be in the same directory as the main list.

**Correct:**
```
!#include ublock-filters.txt
!#include ublock/filters.txt
```

**Incorrect:**
```
!#include https://github.com/uBlockOrigin/uAssets/blob/master/filters/filters.txt
!#include ../filters.txt
```

Purpose: allow filter list maintainers to create uBO-specific filters while keeping compatibility with other blockers.

### `!#if [condition]`

Conditional compilation — parse a block of filters only if conditions are met.

```
!#if env_firefox
example.com##+js(nowebrtc)
!#endif
```

Negation with `!`:
```
!#if !env_firefox
example.com##^script:has-text(ad)
!#endif
```

### `!#else` (1.50.1b9+)

```
!#if cap_html_filtering
example.com##^script:has-text(fakeAd)
!#else
example.com##+js(rmnt, script, fakeAd)
!#endif
```

### Supported Condition Tokens

| Token | Value | Notes |
|---|---|---|
| `ext_abp` | **false** | Always false in uBO |
| `ext_ublock` | **true** | Always true in uBO |
| `ext_ubol` | true on uBOL | 1.44.3b12+ |
| `ext_devbuild` | true on dev build | 1.48.1b1+ |
| `env_chromium` | true on Chromium browsers | |
| `env_edge` | true on Edge (legacy) | |
| `env_firefox` | true on Firefox | |
| `env_mobile` | true on mobile | |
| `env_safari` | true on Safari (legacy ≤12) | |
| `env_mv3` | true when uBOL assembled | 1.44.5b15+ |
| `false` | **false** | 1.22.0+ |
| `cap_html_filtering` | true if HTML filtering available | |
| `cap_user_stylesheet` | true on Firefox, Chromium 66+ | |
| `adguard` | **false** | 1.29.0+ |
| `adguard_app_*` | **false** | All AdGuard app tokens |
| `adguard_ext_*` | See version notes | Browser-specific |

**Disable a block permanently (1.22.0+):**
```
!#if false
...disabled filters...
!#endif
```

## Unsupported Features

### `document` for Entire Page Exception

Not supported. The `document` option on exception filters is meant for "acceptable ads," which uBO does not support. Users must explicitly trust sites through the Trusted Sites feature.

**Note:** `$document` on a BLOCKING filter does work for strict blocking, and exceptions can negate strict blocking.

### `genericblock`

Not supported. Would silently disable large numbers of generic filters (including hosts file entries and anti-tracking lists), creating a dangerous security gap.

### `$webrtc` Option

Not supported as a network filter option. Use the `nowebrtc` scriptlet instead:
```
example.com##+js(nowebrtc)
```

### `elemhide` / `ehide`

**Supported** since uBO 1.23.0 (also aliased as `ehide`). Before 1.23.0 it was translated to `generichide` internally.

## Platform Compatibility Notes

### HTML Filtering
- Firefox only
- Requires `cap_html_filtering` token
- Does not work on Chromium-based browsers

### CNAME Uncloaking
- Firefox MV2 only (`$cname` option)
- Chromium does not support CNAME uncloaking at the extension level

### Hostname Regex
- Available since 1.46.1b15
- Works in hostname position and in `$domain=`, `$to=`, `$from=`
- Use sparingly — O(n) iteration vs O(1) lookup for plain hostnames

### Scriptlet Logging
- Works only in dev builds or with `filterAuthorMode` advanced setting
- All logging now appears in uBO's logger (1.57.3b1+)
- Old `(log, 1)` token method is deprecated

### Trusted Sources
Only these are trusted for restricted features (`$replace`, trusted scriptlets, etc.):
- uBO's own filter lists ("uBlock filters -- ...")
- User's "My filters" (only if "Allow custom filters requiring trust" is checked, or in dev build)
- Override with `trustedListPrefixes` advanced setting

## uBO vs Other Blockers: Key Differences

| Feature | uBO | ABP | AdGuard |
|---|---|---|---|
| `$document` exception | ❌ | ✅ | ✅ |
| `genericblock` | ❌ | ✅ | ✅ |
| `$webrtc` | ❌ (use scriptlet) | ✅ | ✅ |
| `$replace` | Trusted only | ❌ | Trusted only |
| `$badfilter` | ✅ | ❌ | ✅ |
| `$denyallow` | ✅ | ❌ | ❌ |
| `$cname` | Firefox MV2 | ❌ | ❌ |
| HTML filters `##^` | Firefox only | ❌ | CoreLibs |
| `$header` option | ✅ | ❌ | ✅ |
| `$method` option | ✅ | ❌ | ✅ |
| HOSTS parsing | `example.com` → `\|\|example.com^` | Pattern match | Pattern match |
| Scriptlet syntax | `##+js()` | N/A | `#%#//scriptlet()` |
| Procedural CSS | Rich set | Limited | Rich set |
| `$popunder` | ✅ | ❌ | ✅ |
| `$permissions` | ✅ | ❌ | ✅ |
