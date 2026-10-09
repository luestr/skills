# Preprocessor Directives, Hints & Debugging

## Preprocessor Directives

Directives used by filter maintainers to improve compatibility. Any mistake causes filter update failure.

Directives can be used in user rules and custom filters.

---

### `!#include` — Include File

Includes the contents of a specified file into the filter. Only same-origin files are supported.

**Syntax:**
```adblock
!#include file_path
```

- Supports absolute and relative paths
- Included files can contain nested `!#include` (recursive protection required)
- File not found causes the entire filter update to fail
- Local custom filters are not subject to same-origin restrictions

**Examples:**
```adblock
Filter URL: https://example.org/path/filter.txt

!#include https://example.org/path/includedfile.txt    -- Same-origin absolute path
!#include /includedfile.txt                             -- Relative path
!#include ../path2/includedfile.txt                     -- Relative path
!#include https://domain.com/path/includedfile.txt      -- ❌ Different origin
```

---

### `!#if` / `!#else` / `!#endif` — Conditional Directives

Conditionally apply rules based on ad blocker type. Supports basic logical operators.

**Syntax:**
```adblock
!#if (conditions)
rules_list
!#endif
```

```adblock
!#if (conditions)
true_conditions_rules_list
!#else
false_conditions_rules_list
!#endif
```

**Available constants:**
- `adguard` — always declared, sufficient for 95% of cases
- **Product-specific constants:**
  - `adguard_app_windows` — AdGuard for Windows
  - `adguard_app_mac` — AdGuard for Mac
  - `adguard_app_cli` — AdGuard for Linux
  - `adguard_app_android` — AdGuard for Android
  - `adguard_app_ios` — AdGuard for iOS
  - `adguard_ext_safari` — AdGuard for Safari
  - `adguard_ext_chromium` — AdGuard Browser Extension for Chrome
  - `adguard_ext_chromium_mv3` — AdGuard for Chrome MV3
  - `adguard_ext_firefox` — AdGuard Browser Extension for Firefox
  - `adguard_ext_edge` — AdGuard Browser Extension for Edge Legacy
  - `adguard_ext_opera` — AdGuard Browser Extension for Opera
  - `adguard_ext_android_cb` — AdGuard Content Blocker
  - `ext_ublock` — uBlock Origin (when compiled by FiltersRegistry)
  - `cap_html_filtering` — Products that support HTML filtering

**Examples:**
```adblock
!#if (adguard && !adguard_ext_safari)
||example.org^$third-party
domain.com##div.ad
!#endif

!#if (adguard_app_android)
!#include /androidspecific.txt
!#endif

!#if (adguard && !adguard_ext_safari)
||example.org^$third-party
!#else
||subdomain.example.org^$third-party
!#endif
```

**`!#else` compatibility:** FiltersDownloader v1.1.20+, CoreLibs v1.13+, Browser Extension v4.2.208+, Safari v1.11.16+.

---

### `!#safari_cb_affinity` — Safari Content Blocker Affinity

Safari limits each content blocker to 150,000 active rules. AdGuard splits rules into 6 content blockers, total limit 900,000.

**Content blocker composition:**
- `general` — Ad blocking, language-specific
- `privacy` — Privacy
- `social` — Social widgets, annoyances
- `security` — Security
- `other` — Other
- `custom` — Custom
- `all` — All content blockers

**Issue:** Rules in different blockers are applied independently. If a blocking rule is in one blocker and an exception is in another, the exception won't work.

**Syntax:**
```adblock
!#safari_cb_affinity(content_blockers)
rules_list
!#safari_cb_affinity
```

**Examples:**
```adblock
!#safari_cb_affinity(general)
example.org#@#.adBanner
!#safari_cb_affinity

!#safari_cb_affinity(privacy)
@@||example.org^
!#safari_cb_affinity
```

---

## Hints

Special comment directives for the server-side filter compiler.

**Syntax:**
```adblock
!+ HINT_NAME1(PARAMS) HINT_NAME2(PARAMS)
```

---

### `NOT_OPTIMIZED` — Do Not Optimize

Prevents rules from being removed in optimized versions.

```adblock
!+ NOT_OPTIMIZED
||example.org^

!+ NOT_OPTIMIZED PLATFORM(android)
||example.org^
```

---

### `PLATFORM` / `NOT_PLATFORM` — Platform Restriction

Specifies which platforms a rule applies to.

**Platform list:**
`windows`, `mac`, `cli` (Linux), `android`, `ios`, `ext_chromium`, `ext_chromium_mv3`, `ext_ff`, `ext_edge`, `ext_opera`, `ext_safari`, `ext_android_cb`, `ext_ublock`

```adblock
!+ PLATFORM(windows,mac,android)
||example.org^

!+ NOT_PLATFORM(ext_safari, ext_android_cb, ios)
||example.org^
```

---

### `NOT_VALIDATE` — Skip Validation

Skips rule validation, useful for rules whose support has not yet been added or rules incorrectly discarded.

```adblock
!+ NOT_VALIDATE
||example.org^$newmodifier
```

---

## Debugging Methods

### Filtering Log

Detailed tool listing all web requests passing through AdGuard.

**Location by product:**
- **Windows:** Ad Blocker tab or tray menu
- **Mac:** Settings → Advanced → Filtering log
- **Android:** Statistics → Recent activity
- **Browser Extension:** Miscellaneous settings tab or right-click extension icon

**Filtering log does not exist on iOS/Safari** (Safari content blocker implementation limitation).

---

### Selectors Debugging Mode

Use the `debug` style property to check selector performance.

**Single selector debugging:**
```adblock
#$?#.banner { display: none; debug: true; }
```

**Global debugging:**
```adblock
#$?#.banner { display: none; debug: global; }
```

**Testing ExtendedCss without AdGuard:**
```js
!function(e,t,d){C=e.createElement(t),C.src=d,C.onload=function(){alert("ExtendedCss loaded")},s=e.getElementsByTagName(t)[0],s?s.parentNode.insertBefore(C,s):(h=e.getElementsByTagName("head")[0],h.appendChild(C))}(document,"script","https://AdguardTeam.github.io/ExtendedCss/extended-css.min.js");

// Usage
const selector = 'div.block:has=(.header:matches-css(after, content: Ads))';
ExtendedCss.query(selector);
```

---

### Debugging Scriptlets

In Browser Extension, open the Filtering log — scriptlets switch to debug mode.

**Dedicated debug scriptlets:**
- `debug-current-inline-script`
- `debug-on-property-read`
- `debug-on-property-write`
- `log-addEventListener`
- `log-on-stack-trace`
- `log-eval`
- `log`

**Scriptlets usable for debugging:**
- `json-prune`, `prevent-fetch`, `prevent-requestAnimationFrame`, `prevent-setInterval`, `prevent-setTimeout`, `prevent-window-open`, `prevent-xhr`, `trusted-replace-fetch-response`, `trusted-replace-xhr-response`

---

## Compatibility Legend

| Symbol | Meaning |
|---|---|
| ✅ | Fully supported |
| ✅ * | Supported with limitations |
| 🧩 | May be available in nightly/beta |
| ⏳ | Planned but not yet available |
| ❌ | Not supported |
| 👎 | Deprecated |
| 🚫 | Removed |

**Product abbreviations:**
- **CoreLibs apps** — Windows/Mac/Android/Linux
- **AdGuard for Chromium** — Chrome/Edge/Opera extension
- **AdGuard for Chrome MV3** — Chrome MV3 extension
- **AdGuard for Firefox** — Firefox extension
- **AdGuard for iOS** — iOS Safari
- **AdGuard for Safari** — Desktop Safari
- **AdGuard Content Blocker** — Android Samsung/Yandex browsers
