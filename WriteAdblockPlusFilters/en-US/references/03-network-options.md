# Network Filter Options

Filter options modify the behavior of blocking and exception rules. They are appended after a `$` at the end of the filter pattern, separated by commas.

```
/pattern/$option1,option2
```

## Type Options

Restrict which types of network requests a filter applies to. Multiple types can be combined.

| Option | Description |
|---|---|
| `script` | External scripts loaded via `<script>` tags |
| `image` | Images, typically from `<img>` tags |
| `stylesheet` | External CSS stylesheets |
| `object` | Content handled by browser plugins (Flash, Java) |
| `xmlhttprequest` | Requests via `XMLHttpRequest` or `fetch()` API |
| `subdocument` | Embedded pages (iframes) |
| `ping` | Requests from `<a ping>` or `navigator.sendBeacon()` |
| `websocket` | WebSocket connections |
| `webrtc` | WebRTC ICE server connections |
| `popup` | Pages opened in new tabs/windows (**must** be explicitly specified to block popups) |
| `font` | External font files |
| `media` | Media files (audio, video) |
| `other` | Request types not covered above |
| `match-case` | Makes the filter pattern case-sensitive (default is case-insensitive) |

**Exception-only type options** (only meaningful in `@@` rules):

| Option | Description |
|---|---|
| `document` | Allowlists the page itself — disables all ABP on the page |
| `elemhide` | Disables element hiding rules on the page |
| `generichide` | Disables only generic element hiding rules |
| `genericblock` | Disables only generic blocking rules |

**Examples:**

```
||example.com/ads/*$script,stylesheet
```
Blocks only script and stylesheet requests from `/ads/` on `example.com`.

```
*/BannerAd.gif$match-case
```
Blocks `BannerAd.gif` (capital B and A) but not `bannerad.gif`.

## Inverse Type Options (`~`)

Prefix a type with `~` to *exclude* that type. This is the opposite of specifying types.

```
||example.com/ads/*$~script,~image
```
Blocks requests from `/ads/` for everything *except* scripts and images.

Available inverse types: `~script`, `~image`, `~stylesheet`, `~object`, `~xmlhttprequest`, `~subdocument`, `~ping`, `~websocket`, `~webrtc`, `~document`, `~elemhide`, `~other`.

## Third-Party / First-Party Restriction

```
||ads.example.com^$third-party
```
Blocks requests to `ads.example.com` only when they originate from a **different** domain than the page you're viewing.

```
||example.com/analytics.js$~third-party
```
Blocks `analytics.js` only when loaded from the **same** origin as the page (first-party).

## Domain Restriction (`$domain`)

Limit a filter to specific domains:

```
||ads.example.com^$domain=example.com
```
Only blocks ads requests when you're on `example.com` (or its subdomains/iframes).

Multiple domains (pipe-separated):
```
||ads.example.com^$domain=example.com|example.net
```

Exclude a domain (tilde prefix):
```
||ads.example.com^$domain=~example.com
```
Blocks ads on every site *except* `example.com`.

Combine inclusion and exclusion:
```
||ads.example.com^$domain=example.com|~foo.example.com
```
Blocks ads on `example.com` but not on the `foo.example.com` subdomain.

**Note:** For blocking rules, the domain must be specified under `$domain` for the filter to be considered site-specific (relevant for `$genericblock`/`$generichide`).

## Sitekey Restriction (`$sitekey`)

```
||ads.example.com^$sitekey=abcdsitekeydcba
```
Only applies on pages that provide a matching public key and verifiable signature. Multiple sitekeys: `sitekey=key1|key2`.

Sitekeys allow a single filter to apply across many domains without listing them all, but require server-side implementation (see the sitekey implementation section in the main docs).

## Content Security Policy (`$csp`)

Injects a Content Security Policy header into matching responses:

```
||example.com^$csp=script-src: 'none'
```
Injects `script-src: 'none'` CSP header, blocking all scripts (including inline) on pages matching the filter.

**Use sparingly** — this is a last resort for advanced circumvention. Prefer specific blocking filters when possible. (Requires ABP 3.1+)

## Redirect to Internal Resource (`$rewrite`)

Redirect matching requests to an internal placeholder resource instead of blocking:

```
||example.com/ads/analytics.js$rewrite=abp-resource:blank-js
```
The browser receives an empty JavaScript file instead of the real one — no error is thrown.

**Available internal resources:**

| Resource | Content |
|---|---|
| `blank-text` | Empty text |
| `blank-css` | Empty stylesheet |
| `blank-js` | Empty JavaScript |
| `blank-html` | Empty HTML document |
| `blank-mp3` | 0.1s silent MP3 |
| `blank-mp4` | Blank MP4 video |
| `1x1-transparent-gif` | 1×1 transparent GIF |
| `2x2-transparent-png` | 2×2 transparent PNG |
| `3x2-transparent-png` | 3×2 transparent PNG |
| `32x32-transparent-png` | 32×32 transparent PNG |

**Restrictions:**
- Must be combined with `$domain=` (cannot be used without domain restriction).
- Cannot be used with `$third-party`, but can be used with `$~third-party`.
- The filter pattern must be `*` or start with `||`.
- (Requires ABP 3.5+)

## Header Matching (`$header`)

Block requests/responses based on HTTP headers:

```
||example.com^$header=x-tracking-id=some-value
```
Blocks the request if the HTTP response contains header `x-tracking-id` whose value includes `some-value`.

**Check for header presence only** (omit content and `=`):
```
||example.com^$header=x-tracking-id
```

**Escape comma** in content with `\x2c`:
```
||example.com^$header=x-custom=val1\x2c val2
```

**Escape `\x2c` literally** with `\\`:
```
||example.com^$header=x-custom=text\\x2c still literal
```

**Notes:**
- Header names are matched case-insensitively.
- Only supported in Firefox.
- Can only be added to user custom filters or ABP Anti-Circumvention list.
- Regex for content is **not yet supported** (syntax `header=/content/` is reserved).
- (Requires ABP 3.11+)

## Add Header (`$addheader`)

Inject HTTP headers into requests or responses instead of blocking:

```
||example.com^$addheader=request:X-Custom-Header: value
```
Adds header `X-Custom-Header: value` to the **request** sent to the server.

```
||example.com^$addheader=response:X-Frame-Options: DENY
```
Adds header `X-Frame-Options: DENY` to the **response** received by the browser.

**Prefixes:** `request:` for request headers, `response:` for response headers.

**Notes:**
- Only supported in Firefox.
- (Requires ABP 4.32.0+)

## Regular Expressions

Wrap the filter pattern in `/` to use a regular expression:

```
/ad-[0-9]+\.example\.com/
```
Matches any URL containing `ad-` followed by one or more digits and `.example.com`.

```
/^https?:\/\/[a-z]{8}\.example\.com\/[a-z]{3}\.js/
```
Matches URLs from `example.com` with an 8-letter subdomain and a 3-letter `.js` file.

Regular expressions follow the same syntax as JavaScript `RegExp`. They can be combined with filter options:

```
/ad[-_]?banner/$image,third-party
```

**Performance note:** Regex filters are slower than plain-text or wildcard filters. Use them only when simpler patterns can't express the match.

## Option Precedence

When multiple filters match the same request, more specific filters take priority. A filter with domain restriction is more specific than a generic one. Exception rules (`@@`) always take priority over blocking rules for the same match.
