# Modifier Filters (Response Modification)

> Options that modify the response rather than simply blocking or allowing it. These transform, strip, or redirect content.

## `$csp` (Content Security Policy)

Inject a Content Security Policy header into matching responses. This doesn't block the request — it adds/modifies the CSP header.

```
||example.com^$csp=script-src 'self' *
```
Adds a CSP that only allows scripts from the same origin and specified sources.

```
||example.com^$csp=frame-src 'none'
```
Prevents framing on example.com.

**Important:** 
- CSP filters are applied regardless of whether the request is blocked
- CSP filters with `$important` override exception filters
- Using `$csp` on an exception filter removes CSP injection for that site

## `$redirect` / `$redirect-rule`

Redirect a blocked request to a local resource from uBO's resources library instead of blocking it outright.

### `$redirect`

```
||tracker.com/analytics.js$3p,redirect=google-analytics_analytics.js
```
When tracker.com/analytics.js is blocked, serve the sanitized Google Analytics surrogate instead.

### `$redirect-rule`

Same as `$redirect`, but only activates when the filter would otherwise block. It doesn't create a new blocking filter on its own — it only specifies the redirect resource for an already-blocking filter.

```
||ads.example.com^$redirect-rule=noop.js
```

**Common redirect resources:**
- `noop.js` — Empty JavaScript
- `noop.css` — Empty stylesheet
- `noop.html` / `noopframe` — Empty HTML page
- `1x1.gif`, `2x2.png`, `3x2.png` — Tiny transparent images
- `none` — Disable a redirect filter
- `click2load.html` — Interactive placeholder for iframes

**URL-specific surrogates:**
- `google-analytics_analytics.js` — GA surrogate
- `google-analytics_ga.js` — ga.js surrogate
- `googletagservices_gpt.js` — GPT surrogate
- `googletagmanager_gtm.js` — GTM surrogate
- `googlesyndication_adsbygoogle.js` — AdSense surrogate
- `amazon_apstag.js` — Amazon APS surrogate
- `nobab.js` — BlockAdblock defuser
- `nofab.js` — FuckAdBlock defuser

```
||google-analytics.com/analytics.js$redirect=google-analytics_analytics.js
```

## `$removeparam`

Strip query string parameters from URLs. Supports plain text and regex.

**Plain text:**
```
||example.com^$removeparam=utm_source
```
Removes `utm_source=xxx` from the query string.

**Regex:**
```
||example.com^$removeparam=/^utm_/
```
Removes all parameters starting with `utm_`.

**Wildcard to remove all parameters:**
```
||example.com^$removeparam=*
```

**Important:** If the regex parameter starts with `/` and ends with `$/`, use the `_` noop option to disambiguate from plain regex filters:
```
/ad-$removeparam=/^foo=bar\d$/,_
```

## `$replace`

Replace text content in network responses using regex. **Trusted sources only** (uBO's own lists or user's filters with trust enabled).

```
||example.com^$replace=/bad_ad_code/good_code/
```

**Multiple replacements:**
```
||example.com^$replace=/pattern1/replacement1//pattern2/replacement2/
```

**Important restrictions:**
- Only works from trusted sources
- Can only be applied to text responses (not binary)
- Replacement is performed on the response body before it reaches the browser

## `$uritransform`

Apply regex-based transformations to request URLs. **Trusted sources only.**

```
||old.example.com^$uritransform=/old/new/
```

This is different from `$redirect` — it transforms the URL itself before the request is made, rather than serving different content.

## `$urlskip`

Skip (bypass) URL redirects by extracting the real destination from the URL pattern. **Trusted sources only.**

```
||tracker.example.com/redirect?url=$urlskip=url
```

Extracts the value of the `url` parameter and directly navigates to that destination, bypassing the tracking redirect.

## `$empty`

Alias for `$redirect=empty`. Returns an empty response for the matched request.

```
||tracker.example.com/collect^$empty
```
The request succeeds but receives an empty response body.

**Note:** `$empty` is a convenience alias. Prefer `$redirect=noop.js` or other specific redirect resources for clarity.

## `$mp4`

Alias for `$redirect=noopmp4-1s`. Redirects media requests to a 1-second silent MP4 file.

```
||cdn.example.com/videos^$mp4
```

Commonly used for sites that serve video ads — the ad "plays" but shows nothing.

## Filter Examples

```adblock
||example.com^$csp=script-src 'self' 'unsafe-inline'
```
Inject CSP on example.com allowing only self-hosted inline scripts

```adblock
||google-analytics.com/analytics.js$redirect=google-analytics_analytics.js
```
Redirect GA script to sanitized surrogate

```adblock
||example.com^$removeparam=/^utm_/
```
Strip all UTM tracking parameters from example.com URLs

```adblock
||example.com/page$removeparam=ref
```
Remove the `ref` parameter from example.com/page URLs

```adblock
||tracking.example.com^$3p,redirect=noop.js
```
Redirect tracking script to empty JS on third-party contexts

```adblock
@@||cdn.example.com^$removeparam
```
Disable parameter stripping for cdn.example.com
