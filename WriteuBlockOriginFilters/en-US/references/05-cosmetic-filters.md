# Cosmetic Filters

> Element hiding, CSS injection, procedural selectors, action operators, entity matching, and hostname regex.

## Basic Cosmetic Filters

### Syntax

```
[hostname(s)]##[CSS selector]           (hide element)
[hostname(s)]#@#[CSS selector]          (exception — unhide)
```

- The `##` operator creates a cosmetic filter that hides matching elements
- The `#@#` operator creates an exception that prevents hiding
- Cosmetic filters have NO privacy value — they only hide elements visually

### Examples

```
example.com##.ad-banner
```
Hides all elements with class `ad-banner` on example.com.

```
example.com,example.org##.ad-banner
```
Applies to multiple domains.

```
example.com#@#.ad-banner
```
Exception: prevents hiding `.ad-banner` on example.com.

### Generic vs Specific

- **Generic:** `##.ad-banner` (no hostname prefix) — applies everywhere, only injected when DOM surveyor finds a match
- **Specific:** `example.com##.ad-banner` — always injected on example.com

## Entity Matching

All extended filters (cosmetic, network domain=) can use entity notation. An entity replaces the Public Suffix with `*`.

```
google.*###tads.c
```
Matches `google.com`, `google.com.br`, `google.ca`, `google.co.uk`, etc.

```
facebook.*##.ad-unit
```
Matches `facebook.com`, `facebook.net`.

**Important:** `google.evil.biz` does NOT match `google.*` — only the base domain part is matched.

## Hostname Regex (1.46.1b15+)

Use regex as hostname in extended filters and in `$domain=`, `$to=`, `$from=` options.

```
/img[a-z]{3,5}\.buzz/##+js(nowoif)
```
Matches hosts like `imgabcd.buzz`.

```
/^nitter\.[^.]+\.[^.]+$/##.timeline-item:has-text(owned)
```
Matches `nitter.abc.com` but NOT `nitter.com` or `nitter.abc.xyz.com`.

```
/^example\.org$/##h1
```
Matches ONLY `example.org` without any subdomains.

```
org,~/^example\.org$/##h1
```
Matches `org` with all subdomains, excluding `example.org` (but subdomains of example.org still match).

**Performance note:** Use sparingly. uBO must iterate all regex values unlike plain hostnames which are O(1) lookups.

## Specific-Generic (1.25.0+)

Prefix a generic cosmetic filter with `*` to make it unconditionally injected on all pages:

```
*##.selector
```
Injected unconditionally everywhere (still disabled by `$generichide` exceptions).

```
##.selector
```
Standard generic: only injected when DOM surveyor finds a matching element.

Specific-generic filters are NOT discarded by "Ignore generic cosmetic filters" in the Filter lists pane.

## Procedural Cosmetic Filters

Procedural filters use JavaScript to find DOM elements. They extend CSS selectors with powerful matching capabilities.

**Key rules:**
1. Procedural filters MUST be specific (hostname prefix required)
2. Use only when plain CSS selectors won't work
3. Multiple procedural selectors cannot be concatenated in one filter
4. Use `#?#` prefix instead of `##` to prevent uBO from trying to convert to native CSS

### `:has(arg)`

Select subject element if `arg` matches one or more descendants.

```
example.com##main [role="row"]:has(div:last-of-type span:has-text(/^Promoted by/))
```

uBO automatically uses native `:has()` when available in the browser (Chromium 105+), falling back to procedural.

### `:has-text(needle)`

Select element if text `needle` is found inside it or its children. Supports literal text and regex.

```
example.com##body > div span:has-text(/^Promoted by/)        (starts with)
example.com##body > div span:has-text(/^Promoted by/i)       (case-insensitive)
example.com##body > div span:has-text(Promoted by)           (contains)
```

### `:matches-attr(arg)`

Select elements by attribute values, useful for randomized attributes.

```
k-rauta.fi##button:matches-attr(class="/[\w]{7}/")
```

### `:matches-css(arg)` / `:matches-css-before(arg)` / `:matches-css-after(arg)`

Select elements by computed CSS style. Value can be literal or regex.

```
example.com##div:matches-css(position: absolute)
example.com##div:matches-css(background-image: /^url\("data:image/png;base64,/)
```

### `:matches-media(arg)`

Filter by media query.

```
example.com###target:matches-media((min-width: 800px))
example.com###target:matches-media((min-width: 1920px) and (min-height: 930px)):style(color: red !important)
```

### `:matches-path(arg)`

Narrow filter by URL path of the current document. Best used as the first operator.

```
example.com##:matches-path(/shop) p
```
Hides `<p>` on `/shop` pages only.

```
example.com##:matches-path(/^/$/) p
```
Hides `<p>` on the main page only.

### `:matches-prop(arg)`

Select elements by JavaScript property, optionally matching value.

```
example.org##div:matches-prop(imanad)
example.org##img:matches-prop(naturalWidth=160)
```

### `:min-text-length(n)`

Select elements with text length >= n characters.

```
quoka.de##^script:min-text-length(35000)
```

### `:not(arg)`

Select elements where arg matches zero elements. When arg is valid CSS, uses native `:not()`.

### `:others()`

Target all elements OUTSIDE the currently selected set. Useful for "reader mode" style filters.

```
twitter.com##:matches-path(/^/home/) [data-testid="primaryColumn"]:others()
```

### `:upward(arg)`

Lookup ancestor elements. arg is either a positive number (distance) or a CSS selector.

```
example.com##.ad-link:upward(3)          (3 levels up)
example.com##.ad-link:upward(.container) (first ancestor matching .container)
```

### `:nth-ancestor(n)` (deprecated)

Predecessor of `:upward(n)` with identical functionality but only accepts a numeric argument. Deprecated but may appear in existing filter lists. Use `:upward()` instead.

```
example.com##.detLink:has-text(VPN):xpath(../../..)
```
Equivalent to `example.com##.detLink:has-text(VPN):upward(3)`

### `:watch-attr(arg)`

Force re-evaluation when specified attributes change on matching elements.

```
example.com##.j-mini-player[class]:watch-attr(class):remove-attr(class)
```

### `:xpath(arg)`

Evaluate XPath expression. Unlike other operators, can CREATE new element sets.

```
facebook.com##:xpath(//div[@id="stream_pagelet"]//div[starts-with(@id,"hyperfeed_story_id_")])
```

## Action Operators

Action operators must be the LAST in the chain. They cannot be chained further.

### `:remove()`

Remove elements from the DOM entirely (not just hide).

```
example.com##.ad-banner:remove()
```

### `:style(arg)`

Apply CSS styles to elements. Must specify a hostname.

```
example.com##h1:style(background-color: blue !important)
example.com##.overlay:style(display: none !important)
```

**Forbidden in style values:** `url(...)`, `image-set(...)`, comments (`/* */`), backslashes, `//`.

uBO can transparently convert and use AdGuard's [CSS injection rules](https://kb.adguard.com/en/general/how-to-create-your-own-ad-filters#cosmetic-css-rules-syntax) (`#$#` syntax). This means you can use AdGuard's syntax in uBO if you prefer.

### `:remove-attr(arg)`, `:remove-class(arg)` (1.45.3b13+)

Remove attribute(s) from elements.

```
example.com##[onclick]:remove-attr(onclick)
example.com##selector:remove-attr(/^on[a-z]+/)
```

### `:remove-class(arg)`

Remove class name(s) from elements.

```
example.com##html[cookie-banner-open]:remove-class(cookie-banner-open)
```

## Quoting Rules

Use quotes when arguments cause parsing issues. Either `"` or `'` works. Escape the same quote character inside: `'it\'s'` or `"he said \"hi\""`.
