# Content-Type Modifiers

> Used to limit rules to specific types of request content (images, scripts, stylesheets, etc.). Can be combined.

## Compatibility Overview

| Modifier | CoreLibs | Chromium | MV3 | Firefox | iOS | Safari | Content Blocker |
|---|---|---|---|---|---|---|---|
| `$document` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `$font` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$image` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$media` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$object` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| `$other` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `$ping` | ✅*[1]* | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| `$script` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$stylesheet` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$subdocument` | ✅*[2]* | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `$websocket` | ✅ | ✅ | ✅ | ✅ | ✅*[3]* | ✅*[3]* | ❌ |
| `$xmlhttprequest` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$webrtc` 🚫 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$object-subrequest` 🚫 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

## Content Type Detection

- **Browser Extension**: Browser provides content type directly
- **CoreLibs apps**: First determines type via `Sec-Fetch-Dest` header or file extension; if not blocked, determines via `Content-Type` response header

## Combination Examples

```adblock
||example.org^$image
||example.org^$script,stylesheet
||example.org^$~image,~script,~stylesheet
```

---

## `$document` — Main Document Request

Matches main frame document requests (HTML documents loaded in browser tab), does not match iframes.

- By default, AdGuard does not block requests loaded in browser tabs ("main frame bypass")
- When `$document` modifier is specified explicitly, AdGuard blocks page loading and shows a "blocking page"
- As an **exception rule** (`@@...$document`), it is equivalent to using `$elemhide`, `$content`, `$urlblock`, `$jsinject`, `$extension` simultaneously

**Alias:** `$doc`

**Examples:**
```adblock
@@||example.com^$document           -- Completely disable filtering
||example.com^$document             -- Block page loading
||example.com^$document,redirect=noopframe  -- Redirect to empty page
||example.com^$document,removeparam=test    -- Remove query parameter
||example.com^$document,replace=/test1/test2/ -- Replace content
```

---

## `$font` — Font Requests

Matches font requests (e.g. `.woff` file extension).

---

## `$image` — Image Requests

Matches image requests.

---

## `$media` — Media Requests

Matches media file requests (music and video, e.g. `.mp4` files).

---

## `$object` — Plugin Resource Requests

Matches browser plugin resource requests (e.g. Java or Flash).

**Compatibility:** Not supported on Safari and iOS.

---

## `$other` — Other Requests

Matches requests whose type has not been determined or doesn't match the types listed above.

---

## `$ping` — Ping Requests

Matches requests caused by `navigator.sendBeacon()` or the `ping` attribute on links.

**Limitations:** CoreLibs apps often cannot accurately detect `navigator.sendBeacon()`. Not recommended in filter lists used by CoreLibs-based products.

**Compatibility:** Not supported on Safari and iOS.

---

## `$script` — Script Requests

Matches script requests (e.g. JavaScript, VBScript).

---

## `$stylesheet` — Stylesheet Requests

Matches CSS file requests.

**Alias:** `$css`

---

## `$subdocument` — Subdocument Requests

Matches embedded page requests — HTML tags `frame` and `iframe`.

**Alias:** `$frame`

**Examples:**
```adblock
||example.com^$subdocument
||example.com^$subdocument,domain=domain.com
```

**Limitations:** CoreLibs apps detect via `Sec-Fetch-Dest` header, otherwise may misidentify main pages as subdocuments. Not supported by Content Blocker.

---

## `$websocket` — WebSocket Requests

Applies only to WebSocket connections.

**Limitations:** Safari requires macOS Monterey+, iOS requires iOS 16+. Not supported by Content Blocker.

---

## `$xmlhttprequest` — AJAX Requests

Applies only to AJAX requests sent via `XMLHttpRequest`.

**Alias:** `$xhr`

**Compatibility:** CoreLibs apps may misidentify as `$other` or `$script` when filtering older browsers; only reliably detected in modern browsers supporting Fetch metadata request headers.

---

## Removed Modifiers

### `$object-subrequest` 🚫
Removed, rules treated as invalid. Was used to match browser plugin (Flash) sub-requests.

### `$webrtc` 🚫
Removed, rules treated as invalid. Use `nowebrtc` scriptlet to suppress WebRTC.
