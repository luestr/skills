# HTML Filters & Response Header Filtering

> Remove elements from response data before browser parsing, and remove response headers.

## HTML Filters

### Overview

HTML filters act on **response data** before the browser parses it. They remove matching elements from the streamed HTML so the browser never sees them.

**Platform:** Firefox only (requires `cap_html_filtering`).

### Syntax

Prefix the selector with `^` after `##`:

```
[hostname(s)]##^[CSS or procedural selector]
[hostname(s)]#@#^[selector]     (exception)
```

### Important: How to Create HTML Filters

**Do NOT use browser DevTools inspector** — that shows parsed DOM, not raw response data.

**Use `view-source:[URL]`** to see the actual response data. Find the relevant HTML elements there, then create filters based on what you see in the source.

### Examples

```
example.com##^.ad-container
```
Remove all elements with class `ad-container` from the response stream.

```
example.com##^script:has-text(7c9e3a5d51cdacfc)
```
Remove `<script>` tags containing specific text from the response.

```
example.com##^script:has-text(/ad[-_]?block/i)
```
Remove scripts matching a regex pattern.

### Supported Selectors

HTML filtering supports both CSS selectors and procedural operators that make sense in the pre-parse context:
- `:has-text()` — Match by text content
- `:min-text-length()` — Match by minimum text length
- `:has()` — Match by descendant elements
- Native CSS selectors

**Not supported in HTML filtering:** Operators that require a live DOM (like `:matches-css()`, `:upward()`, etc.)

### Negated Hostnames (1.48.5b4+)

```
google.com,~translate.google.com##^script:has-text(consentCookiePayload)
```
Applies on google.com but NOT on translate.google.com.

### Character Encoding Support

HTML filtering works only with these encodings:
- UTF-8
- ISO-8859-1
- Windows-1250
- Windows-1251
- Windows-1252

### Relationship to Cosmetic Filters

HTML filters remove elements **before** parsing. Cosmetic filters hide elements **after** parsing (via CSS). HTML filtering is more powerful because the browser never processes the removed content at all — scripts don't execute, images don't load, etc.

### Historical Note

The deprecated `script:contains(...)` syntax is internally converted to `##^script:has-text(...)`.

## Response Header Filtering

### Overview

A special case of HTML filtering that targets response headers instead of the response body.

**Platform:** All browsers (header removal occurs at `onHeaderReceived` time).

### Syntax

```
[hostname(s)]##^responseheader(header-name)
```

The `header-name` **must be lowercase**.

### Examples

```
example.com##^responseheader(refresh)
```
Remove the `refresh` header to prevent timed redirects.

```
example.com##^responseheader(set-cookie)
```
Remove `set-cookie` headers.

### Supported Headers

Only a limited set can be removed for security reasons:

- `location`
- `refresh`
- `report-to`
- `set-cookie`

This limitation ensures uBO never weakens the security profile of web pages (e.g., `content-security-policy` cannot be removed).

### Scope

Response header filtering can only be applied to **document resources** (main frames and sub-frames), not to sub-resources like scripts or images.

### Related

To filter network responses based on whether a specific header IS present and matches a value, use the `$header=` network filter option instead.
