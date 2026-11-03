# Restrictions & Compatibility: SafariConverterLib, Content Blocker, Trusted Filters

> Must-read before writing Safari/iOS filtering rules.

## Trusted Filters

The following rules can only be used in trusted filters:
- `$replace`, `$hls`, `$jsonprune`, `$xmlprune`, `$urltransform`
- `$removeheader`, `$removeparam`
- JavaScript rules (`#%#`)
- Scriptlet rules (`//scriptlet()`)

Trusted filters include:
- Filter lists created by the AdGuard team
- Custom filter lists installed as `trusted`
- User rules

---

## AdGuard Content Blocker

Extension for Samsung and Yandex browsers on Android. Very limited, only supports old ABP syntax:

- Basic blocking rules: only `$domain`, `$third-party`, content-type modifiers
- Basic exception rules: only `$document`, `$elemhide`
- Basic element hiding rules (no Extended CSS support)

**Not supported:** CSS rules, HTML filtering, JavaScript, scriptlets, and all advanced modifiers.

---

## SafariConverterLib Detailed Limitations

Safari Converter supports AdGuard syntax as much as possible, but important limitations remain.

### Basic (Network) Rules

#### Supported with Limitations

| Item | Limitation |
|---|---|
| **Regular expressions** | Limited to [Safari-supported regex subset](https://developer.apple.com/documentation/safariservices/creating-a-content-blocker#Capture-URLs-by-pattern) |
| **`$domain`** | ① Cannot mix allowed and excluded domains (e.g. `$domain=example.org\|~sub.example.org`)<br>② `domain.*` not fully supported (replaced with top 100 TLDs)<br>③ Regex not supported |
| **`$denyallow`** | Implemented by converting to a set of rules, **must have `$domain` modifier** |
| **`$popup`** | Equivalent to `$document` blocking, does not attempt to close tabs |
| **`@@` exception rules** | Exceptions without modifiers disable all filtering (including cosmetic rules) due to Safari's `ignore-previous-rules` mechanism |
| **`$urlblock`/`$genericblock`** | Equivalent to `$document`, disables all filtering |
| **`$content`** | Compatibility only, limited to `document` resource type |
| **`$specifichide`** | Must target a domain (e.g. `\|\|example.org^$specifichide`), does not cover subdomains |
| **Single modifier limit** | `urlblock`, `genericblock`, `generichide`, `elemhide`, `specifichide`, `jsinject` can only be used as the sole modifier in a rule |

#### Unsupported Modifiers

`$app`, `$header`, `$method`, `$extension`, `$stealth`, `$cookie`, `$csp`, `$hls`, `$inline-script`, `$inline-font`, `$jsonprune`, `$xmlprune`, `$network`, `$permissions`, `$redirect`, `$redirect-rule`, `$referrerpolicy`, `$removeheader`, `$removeparam`, `$replace`, `$urltransform`

**Planned support:** `$strict-first-party`, `$strict-third-party`, `$to`, `$cookie` (partial)

---

### Cosmetic Rules Limitations

- Domain restrictions subject to the same limitations as basic rules' `$domain`
- `$path` supported, but regex limited to Safari subset
- `$url` not yet supported

---

### Script/Scriptlet Rules

- **Fully supports** JS rules and scriptlet rules, but can only be interpreted by a separate extension
- **Important:** Scriptlets should run as early as possible (before page scripts); Safari always has a slight delay

---

### HTML Filtering Rules

**Not supported and will never be** — Safari does not provide the necessary technical capabilities.

---

### Safari Content Blocker Architecture

Safari limits each content blocker to **150,000** active rules. AdGuard splits into 6 blockers, total limit **900,000**:

| Blocker | Content |
|---|---|
| `general` | Ad blocking, language-specific |
| `privacy` | Privacy |
| `social` | Social widgets, annoyances |
| `security` | Security |
| `other` | Other |
| `custom` | Custom |

User rules and allowlist are added to all blockers.

**Key issue:** Rules in different blockers are applied independently. If a blocking rule is in blocker A and an exception is in blocker B, **the exception won't work**. Use `!#safari_cb_affinity` directive to put related rules in the same blocker.

```adblock
!#safari_cb_affinity(general)
example.org#@#.adBanner
!#safari_cb_affinity
```

---

## Removed Modifiers

| Modifier | Status | Replacement |
|---|---|---|
| `$object-subrequest` | 🚫 Removed | None |
| `$webrtc` | 🚫 Removed | `nowebrtc` scriptlet |
| `$empty` | 👎 Deprecated | `$redirect=nooptext` |
| `$mp4` | 👎 Deprecated | `$redirect=noopmp4-1s,media` |
| `:if-not()` | 🚫 Removed | `:not(:has())` |
| `:if()` | 🚫 Removed | `:has()` |
