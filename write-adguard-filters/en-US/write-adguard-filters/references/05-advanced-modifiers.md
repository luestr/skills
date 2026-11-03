# Advanced Modifiers

> These modifiers completely change basic rule behavior for response modification, redirection, cookie control, and other advanced features.

## Compatibility Overview

| Modifier | CoreLibs | Chromium | MV3 | Firefox | iOS | Safari | Content Blocker |
|---|---|---|---|---|---|---|---|
| `$all` | ✅ | ✅ | ✅*[1]* | ✅ | ✅ | ✅ | ❌ |
| `$badfilter` | ✅ | ✅ | ✅*[2]* | ✅ | ✅ | ✅ | ❌ |
| `$cookie` | ✅ | ✅ | ✅*[3]* | ✅ | ❌ | ❌ | ❌ |
| `$csp` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `$hls` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$inline-font` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `$inline-script` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `$jsonprune` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$xmlprune` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$network` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$permissions` | ✅*[4]* | ✅ | ✅ | ✅*[4]* | ❌ | ❌ | ❌ |
| `$redirect` | ✅ | ✅ | ✅*[5]* | ✅ | ❌ | ❌ | ❌ |
| `$redirect-rule` | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `$referrerpolicy` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$removeheader` | ✅ | ✅*[7]* | ✅*[7]* | ✅*[7]* | ❌ | ❌ | ❌ |
| `$removeparam` | ✅ | ✅ | ✅*[6]* | ✅ | ❌ | ❌ | ❌ |
| `$replace` | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| `$urltransform` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$reason` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `noop` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `$empty` 👎 | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| `$mp4` 👎 | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## `$all` — Match All Content Types

Equivalent to all content-type modifiers + `$popup`. Cannot be used with `@@`.

```adblock
||example.org^$all
```
Equivalent to: `||example.org^$document,subdocument,font,image,media,object,other,ping,script,stylesheet,websocket,xmlhttprequest,popup`

**Restrictions:** Contains `$popup`, so not supported by MV3. Not supported by Content Blocker.

---

## `$badfilter` — Disable Other Rules

Disables the basic rules it references. The text of the disabled rule must match the `$badfilter` rule (without `$badfilter`).

```adblock
||example.com$badfilter                    -- Disables ||example.com
||example.com$image,badfilter              -- Disables ||example.com$image
@@||example.com$badfilter                  -- Disables @@||example.com
||example.com$domain=domain.com,badfilter  -- Disables ||example.com$domain=domain.com
```

**Partial domain disable:** When a rule has `$domain` modifier without negated domains, `$badfilter` can disable only specific domains:
```adblock
/some$domain=example.com|example.org|example.io
/some$domain=example.com,badfilter  -- Only disables for example.com
```

**Restrictions:** MV3 only supports fully canceling rules. Not supported by Content Blocker.

---

## `$cookie` — Control Cookies

Does not block requests, but suppresses or modifies `Cookie` and `Set-Cookie` headers.

**Syntax:**
```
$cookie [= name[; maxAge = seconds[; sameSite = strategy]]]
```

**Examples:**
```adblock
||example.org^$cookie                              -- Block all cookies
$cookie=__cfduid                                   -- Block CloudFlare cookie
$cookie=/__utm[a-z]/                               -- Block GA cookies
||facebook.com^$third-party,cookie=c_user          -- Block Facebook tracking
||example.org^$cookie=NAME;maxAge=3600;sameSite=lax -- Modify cookie attributes
```

**Exceptions:**
```adblock
@@||example.org^$cookie                -- Allow all cookies
@@||example.org^$cookie=concept        -- Allow specific cookie
@@||example.org^$cookie=/^_ga_/        -- Allow regex-matched cookies
```

**Compatible modifiers:** `$domain`, `$~domain`, `$important`, `$third-party`, `$~third-party`, `$strict-third-party`, `$strict-first-party`. **Trusted filter rule.** Not supported by Content Blocker/iOS/Safari.

---

## `$csp` — Content Security Policy

Does not block requests, but modifies response headers to strengthen CSP.

**Syntax:** Value follows CSP header syntax. Exception rule value can be empty.

```adblock
||example.org^$csp=frame-src 'none'
||example.org^$csp=script-src 'self' 'unsafe-eval' http: https:
@@||example.org/page/*$csp=frame-src 'none'
@@||example.org/page/*$csp                           -- Disable all $csp rules
```

**Compatible modifiers:** `$domain`, `$important`, `$subdocument`. Not supported by Content Blocker/iOS/Safari.

---

## `$hls` — HLS Playlist Filtering

Modifies HLS playlist (RFC 8216) responses, removing matching segments. **Trusted filter rule.**

**Syntax:**
```adblock
||example.org^$hls=urlpattern        -- URL pattern match
||example.org^$hls=/regexp/options    -- Regex match (t=tag match, i=case-insensitive)
```

```adblock
||example.org^$hls=\/videoplayback^?*&source=dclk_video_ads
||example.org^$hls=/#UPLYNK-SEGMENT:.*\,ad/t
```

**Restrictions:** Trusted filter rule. Compatible with `$domain`, `$third-party`, `$strict-third-party`, `$strict-first-party`, `$app`, `$important`, `$match-case`, `$xmlhttprequest`. Only applies to UTF-8 encoded HLS playlists starting with `#EXTM3U`, max 10MB. CoreLibs apps only.

---

## `$inline-script` — Block Inline Scripts

Uses CSP to block inline JavaScript in pages.

```adblock
||example.org^$inline-script
```
Equivalent to: `||example.org^$csp=script-src 'self' 'unsafe-eval' http: https: data: blob: mediastream: filesystem:`

---

## `$inline-font` — Block Inline Fonts

Uses CSP to block inline fonts in pages.

```adblock
||example.org^$inline-font
```

---

## `$jsonprune` — JSON Response Modification

Removes items from JSON responses using modified JSONPath expressions. **Trusted filter rule.** CoreLibs apps only.

**Syntax:**
```adblock
||example.org^$jsonprune=expression
```

`$` and `,` must be escaped with `\`. Supports JSONP documents (CoreLibs v1.11+).

**Modified JSONPath syntax differences:**
- Script expressions not supported
- Supported filters: `?(has <key>)`, `?(key-eq <key> <value>)`, `?(key-substr <key> <value>)`

**Examples:**
```adblock
||example.org^$jsonprune=\$..[one\, "two three"]
||example.org^$jsonprune=\$.a[?(has ad_origin)]
||example.org^$jsonprune=\$.*.*[?(key-eq 'Some key' 'Some value')]
```

---

## `$xmlprune` — XML Response Modification

Removes items from XML responses using XPath 1.0 expressions. **Trusted filter rule.** CoreLibs apps only (v1.15+).

```adblock
||example.org^$xmlprune=/bookstore/book[position() mod 2 = 1]
||example.org^$xmlprune=/bookstore/book[year = 2003]
||example.org^$xmlprune=//*/@*
```

---

## `$network` — Network Layer Firewall

Completely blocks or allows access to specified remote IP addresses. **Matches IP addresses only, not domains.** CoreLibs apps only.

```adblock
174.129.166.49:3478^$network
[2001:4860:4860::8888]:443^$network
174.129.166.49$network
@@174.129.166.49$network              -- Bypass, no filtering at all
/.+:3[0-9]{4}/$network                -- Block ports 30000-39999
```

**Compatible modifiers:** Only `$app` and `$important`.

---

## `$permissions` — Permissions Policy

Does not block requests, but modifies response headers to add Permissions-Policy.

```adblock
||example.org^$permissions=autoplay=()
$domain=example.org|example.com,permissions=storage-access=()\, camera=()
@@||example.org/page/*$permissions=autoplay=()
@@||example.org/page/*$permissions
```

**Note:** Multiple matching rules each add independent Permissions-Policy headers. `|` can replace escaped commas (CoreLibs v1.14+). Firefox ignores Permissions-Policy headers.

**Compatible modifiers:** `$domain`, `$important`, `$subdocument`, content-type modifiers.

---

## `$redirect` — Redirect to Local Resources

Redirects requests to a local "resource".

```adblock
||example.org/script.js$script,redirect=noopjs
||example.org/test.mp4$media,redirect=noopmp4-1s
@@||example.org^$redirect
@@||example.org^$redirect=nooptext
```

**Priority:** `$important` > `@@` > `$redirect` > basic rules

**Restrictions:** MV3 does not support allowlist rules with `$redirect`. Priority specification not supported (uBO's `:42` syntax). Not supported by Content Blocker/iOS/Safari.

---

## `$redirect-rule` — Conditional Redirect

Alias of `$redirect`, but **only applies when the target request is blocked by another basic rule**.

```adblock
||example.org/script.js
||example.org^$redirect-rule=noopjs
```
Only `script.js` is redirected; other `example.org` requests are unaffected.

Not supported by Content Blocker/iOS/Safari/MV3.

---

## `$referrerpolicy` — Override Referrer Policy

Overrides a page's referrer policy. Also replaces the `content` attribute of `<meta name="referrer">` in HTML.

```adblock
||example.com^$referrerpolicy=unsafe-url
@@||example.com^$referrerpolicy=unsafe-url
@@||example.com/abcd.html^$referrerpolicy
```

Without content-type modifiers, matches `$document` and `$subdocument`. CoreLibs v1.12+.

---

## `$removeheader` — Remove HTTP Headers

Removes HTTP request or response headers. **Trusted filter rule.**

```adblock
||example.org^$removeheader=refresh              -- Remove response header
||example.org^$removeheader=request:x-client-data -- Remove request header
@@||example.org/path/$removeheader
```

**Security restrictions:** Cannot remove security-related headers (e.g. `access-control-*`, `origin`, `content-security-policy`, `content-type`, etc. — see full list in docs).

**Compatible modifiers:** `$domain`, `$third-party`, `$strict-third-party`, `$strict-first-party`, `$app`, `$important`, `$match-case`, content-type modifiers.

---

## `$removeparam` — Remove Query Parameters

Strips query parameters from request URLs. Only applies to `GET`, `HEAD`, `OPTIONS`, and sometimes `POST` requests. **Trusted filter rule.**

**Alias:** `$queryprune` (deprecated)

**Syntax:**
```adblock
$removeparam=param                           -- Remove specified parameter
$removeparam=/regexp/[i]                     -- Regex match removal
$removeparam=~param                          -- Remove all params except param
$removeparam                                 -- Remove all parameters
```

**Examples:**
```adblock
$removeparam=/^(utm_source|utm_medium|utm_term)=/
$removeparam=/^(utm_content|utm_campaign|utm_referrer)=/
@@||example.com^$removeparam
```

**MV3 limitations:** No regex, negation, or allowlist rules. Each named parameter generates a separate declarative rule, removed one per redirect hop (Chrome allows up to 20 hops per navigation).

---

## `$replace` — Regex Replace Response Content

Does not block requests, but modifies response text. Requires regex knowledge. **Trusted filter rule.** CoreLibs apps + Firefox extension only.

**Syntax:**
```
$replace = "/" regexp "/" replacement "/" modifiers
```

`$` and `,` must be escaped with `\`.

```adblock
||example.org^$replace=/(<VAST[\s\S]*?>)[\s\S]*<\/VAST>/\$1<\/VAST>/i
@@||example.org^$replace
@@||example.org^$document  -- Disable all $replace rules
```

**Features:** Does not apply to binary responses; responses >10MB not modified; higher priority than other basic rules (including exceptions), but `$content` exception can override; multiple rules applied alphabetically.

---

## `$urltransform` — URL Rewrite

Modifies request URLs via regex replacement. **Trusted filter rule.** CoreLibs v1.15+.

**Syntax:** A series of transformations separated by `|`. Supports `substitute` (regex replace) and `decode` (`b64` Base64 / `pct` percent-encoding).

```adblock
||example.org^$urltransform=/(pref\/).*\/(suf)/\$1\$2/i
```

**Changing origin:** If regexp starts with `^http`, the full URL can be modified (CoreLibs v1.17+). Transformed requests are re-matched against all rules.

---

## `$reason` — Custom Block Reason

Displays a custom explanation message on the blocking page. Must be used with `$document`.

```adblock
||example.com^$document,reason="Tracker"
||tracking.example.com^$document,reason=tracker
||malware.example.com^$document,reason=disreputable
```

Predefined localizable tokens: `malicious`, `tracker`, `disreputable`. CoreLibs v1.20+.

---

## `noop` — No-Operation Modifier

Does nothing, only improves rule readability. Consists of any length of `_` characters.

```adblock
||example.com$_,removeparam=/^ss\\$/,_,image
||example.com$replace=/bad/good/,___,~third-party
```

Not supported by Content Blocker.

---

## `$empty` 👎 (Deprecated)

Replacement for `$redirect=nooptext`. Returns an empty 200 OK response.

```adblock
||example.org^$empty
```

---

## `$mp4` 👎 (Deprecated)

Replacement for `$redirect=noopmp4-1s,media`. Returns a short placeholder video.

```adblock
||example.com/videos/$mp4
```
