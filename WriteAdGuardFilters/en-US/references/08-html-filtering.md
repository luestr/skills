# HTML Filtering Rules

> Remove specified elements from HTML source code before the browser loads the page.

## Compatibility

Only supported by: AdGuard for Windows/Mac/Android/Linux + Firefox extension. Other browser extensions cannot modify content at the network level.

CoreLibs v1.18+ / Browser Extension v5.3+ support optional attribute values.

## Syntax

### CoreLibs + Firefox + Browser Extension v5.2 and earlier

```
selector = [tagName] [attributes] [pseudoClasses]
combinator = ">"
      rule = [domains] "$$" selector *(combinator selector)
```

- `tagName` — lowercase element name
- `attributes` — attribute list: `[name[=value]]`
- `pseudoClasses` — pseudo-classes
- `combinator` — CSS child combinator `>` (v5.2 and earlier only)

### Browser Extension v5.3+

```
rule = [domains] "$$" CSS_selector
```

Supports standard CSS selectors (pseudo-elements like `::before`, `::after` not supported).

## Examples

```adblock
example.org$$script[data-src="banner"]
```
Removes all `<script>` elements with `data-src` attribute containing `banner` on `example.org`.

```adblock
example.org$$div[some_attribute]
```
Removes `<div>` elements with the `some_attribute` attribute (regardless of value).

## Special Attributes

### `:contains()` ⭐ Recommended

The primary way to filter elements by content. Supports plain text and regular expressions.

```adblock
example.com$$script:contains(Adverts)
example.com$$div:contains("Sponsored by")
example.com$$script:contains(/ad_system_\d+/)
```

**Compatibility:** CoreLibs v1.13+, Browser Extension v5.3+.

`:-abp-contains()` and `:has-text()` are synonyms.

**Limitation:** `:contains()` cannot appear to the left of a `>` combinator (no limitation in v5.3+).

---

### `tag-content` ⚠️ Legacy Attribute

Limits selection to elements whose innerHTML contains the specified substring. Use `""` to escape `"`.

```adblock
$$script[tag-content="banner"]
$$script[tag-content="alert(""this is ad"")"]
```

**Limitation:** Cannot appear to the left of a `>` combinator (no limitation in v5.3+).

---

### `wildcard` ⚠️ Legacy Attribute

Similar to `tag-content`, uses glob patterns to match innerHTML.

```adblock
$$script[wildcard="*banner*text*"]
$$script[wildcard=""banner""]
```

**Limitation:** Same as `tag-content`.

---

### `max-length`

Specifies the maximum length of HTML element content. Default value: **8192**.

```adblock
$$div[tag-content="banner"][max-length="400"]
```

---

### `min-length`

Specifies the minimum length of HTML element content.

```adblock
$$div[tag-content="banner"][min-length="400"]
```

## Exceptions

Use `$@$` instead of `$$`:

```adblock
example.com$@$script[tag-content="banner"]
$@$script[tag-content="banner"]      -- Disable on all domains
```
