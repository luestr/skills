# Scriptlet Injection

> Inject JavaScript code into web pages using uBO's scriptlet injection syntax and resources library.

## Syntax

```
[hostname(s)]##+js(scriptlet-name[, param1[, param2[, ...]]])
```

- The `##+js(...)` syntax injects JavaScript from uBO's [resources library](https://github.com/gorhill/uBlock/wiki/Resources-Library)
- Scriptlet filters **must be specific** (hostname prefix required) — generic `+js` filters are ignored
- Commas in parameters must be escaped: `foo\,bar` (or `/foo\x2cbar/` for regex literals)

## Exception Syntax (1.22.0+)

Disable scriptlet injection for a specific site:
```
example.com#@#+js()
```

Disable ALL scriptlet injection everywhere:
```
#@#+js()
```

The empty form `example.com##+js()` is meaningless and ignored.

## Commonly Used Scriptlets

### `abort-on-property-read` / `aopr`

Abort script execution when a property is READ.

```
example.com##+js(aopr, adBlockDetected)
```

### `abort-on-property-write` / `aopw`

Abort script execution when a property is WRITTEN.

```
example.com##+js(aopw, Fingerprint2)
```

### `abort-current-script` / `acs`

Abort execution of inline script when it attempts to access a property (throws `ReferenceError`).

```
example.com##+js(acis, Math.random)
```

### `abort-on-stack-trace` / `aost`

Abort script when property access occurs with a matching stack trace.

```
example.com##+js(aost, Math.random, /ads\.example\.com/)
```

### `set-constant` / `set`

Set a property to a specified value, preventing the page from changing it.

```
example.com##+js(set, adBlockDetected, false)
example.com##+js(set, isAdFree, true)
```

### `addEventListener-defuser` / `aeld`

Prevent matching event listeners from being added.

```
example.com##+js(aeld, load, /adblock/)
```

### `prevent-setTimeout` / `nostif`

Prevent `setTimeout` calls matching a pattern.

```
example.com##+js(nostif, /adblock/)
```

### `prevent-setInterval` / `nosiif`

Prevent `setInterval` calls matching a pattern.

```
example.com##+js(nosiif, detectAd)
```

### `prevent-xhr` / `no-xhr-if`

Prevent XHR requests matching specified patterns.

```
example.com##+js(no-xhr-if, /\/ads\//)
```

### `prevent-fetch` / `no-fetch-if`

Prevent fetch requests matching specified patterns.

```
example.com##+js(no-fetch-if, /\/tracking\//)
```

### `prevent-window-open` / `nowoif`

Prevent or redirect `window.open()` calls.

```
example.com##+js(nowoif)
```
Blocks all window.open calls.

### `set-cookie`

Set a cookie value.

```
example.com##+js(set-cookie, consent, accepted)
```

### `remove-cookie` / `cookie-remover`

Remove a cookie.

```
example.com##+js(remove-cookie, tracking_id)
```

### `set-local-storage-item` / `set-session-storage-item`

Set a value in localStorage or sessionStorage.

```
example.com##+js(set-local-storage-item, adFree, true)
```

### `remove-attr` / `ra`

Remove attributes from DOM elements. (Consider using `:remove-attr()` cosmetic filter instead.)

### `remove-class` / `rc`

Remove classes from DOM elements. (Consider using `:remove-class()` cosmetic filter instead.)

### `remove-node-text` / `rmnt`

Remove text content from matching nodes. Useful in HTML filtering context.

### `json-prune`

Remove properties from JSON data parsed by the page.

```
example.com##+js(json-prune, ads, )
```

### `object-prune`

Remove properties from objects using JSONPath queries.

### `noeval` / `noeval-if`

Prevent `eval()` calls (optionally matching a pattern).

### `nowebrtc`

Prevent WebRTC connections (replacement for the deprecated `$webrtc` network option).

```
example.com##+js(nowebrtc)
```

### `spoof-css`

Spoof CSS property values returned by `getComputedStyle`.

### `prevent-canvas`

Prevent canvas fingerprinting.

### `close-window` / `window-close-if`

Close the window when conditions are met.

### `overlay-buster`

Remove overlay dialogs that block page interaction.

### `alert-buster`

Suppress `alert()` dialog boxes by redirecting to console.

### `href-sanitizer`

Sanitize links by removing tracking parameters.

### `disable-newtab-links`

Prevent links from opening in new tabs.

## Trusted Scriptlets

Some scriptlets are marked `[Trusted]` and only work from trusted sources (uBO's own filter lists or user's "My filters" with trust enabled):

- `trusted-click-element` — Programmatically click elements
- `trusted-set-constant` — Extended set-constant with more value types
- `trusted-set-cookie` — Set cookies with expiration and path
- `trusted-set-local-storage-item` / `trusted-set-session-storage-item`
- `trusted-set-attr` — Set attributes on elements
- `trusted-create-HTML` — Create HTML elements
- `trusted-replace-xhr-response` / `trusted-replace-fetch-response`
- `trusted-replace-node-text` / `trusted-replace-outbound-text`
- `trusted-replace-argument`
- `trusted-prevent-xhr` / `trusted-prevent-fetch`
- `trusted-prune-inbound-object` / `trusted-prune-outbound-object`
- `trusted-suppress-native-method`
- `trusted-override-element-method`
- `trusted-prevent-dom-bypass`

## `edit`-Suite Scriptlets

A family of scriptlets for editing objects using uBO-flavored JSONPath queries:

- `edit-outbound-object` — Prune properties from objects returned by methods
- `edit-inbound-object` — Prune properties from objects passed as arguments
- `edit-this-object` — Prune properties through an object's own method
- `edit-element-object` — Prune properties from DOM elements
- `json-edit` — Edit objects from `JSON.parse()`
- `json-edit-xhr-response` / `json-edit-fetch-response` — Edit fetched JSON
- `json-edit-xhr-request` / `json-edit-fetch-request` — Edit request body JSON
- `jsonl-edit-xhr-response` / `jsonl-edit-fetch-response` — Edit JSONL responses

## Defuser Scriptlets

Specialized scriptlets that neutralize specific ad-block detection scripts:

- `nobab` — Defuses BlockAdblock
- `nobab2` — Defuses BAB 4.2b
- `nofab` — Defuses FuckAdBlock/BlockAdBlock/SniffAdBlock
- `popads-dummy` / `popads` — Neutralize PopAds
- `prebid-ads` — Prebid-ads shim
- `fingerprint2` / `fingerprint3` — FingerprintJS shims
- `ampproject_v0` — Removes AMP animation delay

## Empty Redirect Resources

Use with `$redirect=` option to serve empty/minimal responses:

**Images:** `1x1.gif`, `2x2.png`, `3x2.png`, `32x32.png`
**Code:** `noop.js`, `noop.css`, `noop.html`, `noop.json`, `noop.txt`
**Media:** `noop-0.1s.mp3`, `noop-0.5s.mp3`, `noop-1s.mp4`
**XML:** `noop-vast2.xml`, `noop-vast3.xml`, `noop-vast4.xml`, `noop-vmap1.xml`
**Special:** `none` (disable redirect), `click2load.html` (interactive iframe placeholder)

## URL-Specific Surrogates

Sanitized redirect resources for specific domains:
- `google-analytics_analytics.js` / `google-analytics_ga.js`
- `googletagservices_gpt.js` / `googletagmanager_gtm.js`
- `googlesyndication_adsbygoogle.js`
- `amazon_ads.js` / `amazon_apstag.js`
- `scorecardresearch_beacon.js`
- `google-ima.js`
- `outbrain-widget.js`
- `hd-main.js`
