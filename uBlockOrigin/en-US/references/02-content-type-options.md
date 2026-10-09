# Content Type Options

> Options that restrict network filters to specific types of content/resources.

## Overview

Content type options narrow a filter to match only specific types of network requests. Multiple types can be combined with commas. When no type is specified, the filter matches all types.

## Available Content Type Options

### `$script` / `$1p-script` / `$3p-script`

Match requests for JavaScript resources.

```
||example.com^$script
```
Blocks all script requests to example.com.

- `$1p-script` — First-party scripts only (uBO 1.20.0+)
- `$3p-script` — Third-party scripts only (uBO 1.20.0+)

### `$image` / `$1p-image` / `$3p-image`

Match requests for image resources (jpg, png, gif, webp, svg, etc.).

```
||ads.example.com^$image
```

- `$1p-image` — First-party images only
- `$3p-image` — Third-party images only

### `$stylesheet` / `$css`

Match requests for CSS stylesheet resources. `$css` is a shorthand alias.

```
||example.com^$stylesheet
```

### `$font`

Match requests for web font resources.

```
||fonts.example.com^$font
```

### `$media`

Match requests for media resources (audio, video files).

```
||cdn.example.com^$media
```

### `$subdocument` / `$frame`

Match requests for embedded documents (iframes, frames). `$frame` is the uBO-preferred alias.

```
||ads.example.com^$frame
```

### `$object`

Match requests for resources loaded by plugins (e.g., Flash, Java applets).

```
||example.com^$object
```

### `$other`

Match requests that don't fall into any of the standard content type categories.

### `$ping`

Match requests sent by the `Navigator.sendBeacon()` API or the `<a ping="">` attribute.

```
||tracking.example.com^$ping
```

### `$websocket`

Match WebSocket connections (`ws://` and `wss://` protocols).

```
||ws.example.com^$websocket
```

### `$xhr` / `$xmlhttprequest`

Match requests made by `XMLHttpRequest` or the `fetch()` API. `$xhr` is the shorthand alias.

```
||api.example.com/track^$xhr
```

### `$popup`

Match popup windows opened by the page. Works as both a blocking type and a standalone option.

```
||example.com^$popup
```
Blocks popups opened from example.com.

### `$document` / `$doc`

Match the main document (the top-level page load). This is a powerful option — using it on a blocking filter will cause strict blocking of the entire site.

```
||example.com^$document
```
Strict-blocks example.com entirely.

**Exception filter with `$document`:**
```
@@||example.com^$document
```
Allowlists example.com (disables all filtering on the site).

**Important:** uBO does NOT support `$document` on exception filters for "acceptable ads" purposes. Users must explicitly trust sites through the Trusted Sites feature.

### `$top`

Match only top-level document requests (main frame only, not subdocuments/iframes). New in uBO 1.20.0.

```
||example.com^$top
```

### `$all`

Equivalent to specifying ALL network-based types + `$popup` + `$document` + `$inline-font` + `$inline-script`. New in uBO 1.20.0.

```
||bet365.com^$all
```
Blocks all network requests, popups, inline fonts and scripts from bet365.com. The EasyList-compatible syntax doesn't allow this with just `||bet365.com^`.

## Combining Content Types

Multiple types can be combined with commas:

```
||example.com^$script,image
```
Blocks both script and image requests from example.com.

## 1p/3p Variants

Starting from uBO 1.20.0, many content types have first-party and third-party variants:

| Base Type | First-Party | Third-Party |
|---|---|---|
| `$script` | `$1p-script` | `$3p-script` |
| `$image` | `$1p-image` | `$3p-image` |
| `$stylesheet` | `$1p-css` | `$3p-css` |
| `$font` | `$1p-font` | `$3p-font` |
| `$media` | `$1p-media` | `$3p-media` |
| `$frame` | `$1p-frame` | `$3p-frame` |
| `$xhr` | `$1p-xhr` | `$3p-xhr` |

These are more efficient than combining e.g. `$script,$third-party` because they allow uBO to optimize internally.

## Examples

```adblock
||tracker.example.com^$script,xhr
```
Block script and XHR requests to tracker.example.com

```adblock
||cdn.example.com^$3p-image
```
Block third-party image requests from cdn.example.com

```adblock
@@||analytics.example.com^$1p-script
```
Allowlist first-party script from analytics.example.com

```adblock
||popads.net^$popup,important
```
Force-block all popups from popads.net
