# Extended CSS Selectors (Adblock Plus-specific)

Standard CSS selectors sometimes can't express the patterns needed to identify ad elements. Adblock Plus adds custom pseudo-selectors that go beyond CSS — they inspect element content, text, and computed styles. These selectors **must** use the `#?#` separator syntax.

**Performance warning:** Extended selectors are evaluated by ABP's JavaScript engine rather than the browser's native CSS engine, making them significantly slower. Always prefer standard `##` selectors when they can express the same rule. Reserve `#?#` for cases that genuinely require extended capabilities, and keep them as domain-specific as possible.

## `:-abp-has(selector)`

Selects elements based on their **descendant content**. Analogous to the browser-native `:has()` pseudo-class but works across all ABP-supported browsers.

```
example.com#?#div:-abp-has(> div > a.advertiser)
```
Selects `<div>` elements that contain, as a direct descendant, a `<div>` that contains an `<a>` with class `advertiser`.

The inner selector can:
- Use relative positioning (`>`, `+`)
- Nest other extended selectors, including `:-abp-has()` itself
- Use any pseudo-selector

**Critical gotcha — scope too broad:**
```
! BAD: Hides the entire page (matches <html> which contains .sponsored somewhere)
example.com#?#:-abp-has(.sponsored)

! GOOD: Narrow the scope with child/descendant combinator
example.com#?#:-abp-has(> .sponsored)
```

Without a `>` or `+` combinator, `:-abp-has()` can match ancestor elements all the way up to `<html>`, effectively hiding the whole page.

## `:-abp-contains(text)` (alias: `:has-text()`)

Selects elements based on their **text content**.

```
div.sidebar > span:-abp-contains(Advertisement)
```
Selects `<span>` elements inside `div.sidebar` that contain the text "Advertisement".

**Practical pattern** — combine with `:-abp-has()` to select the outer container:
```
example.com#?#div.sidebar > div:-abp-has(span:-abp-contains(Advertisement))
```
This selects the container `div` that *contains* a span labeled "Advertisement" — more robust than hiding the span alone.

**Scope warning:**
```
! BAD: Matches any element containing "filters" somewhere in its subtree
eyeo.com#?#:-abp-contains(filters)

! BETTER: Narrow to a specific tag
eyeo.com#?#div:-abp-contains(filters)

! BEST: Target only the exact element
eyeo.com#?#.article-heading:-abp-contains(filters)
```

## `:-abp-properties(properties)`

Selects elements based on their **computed CSS properties** (from stylesheets, including pseudo-elements like `::before` and `::after`).

```
:-abp-properties(width:300px;height:250px;)
```
Selects elements styled with exactly `width: 300px` and `height: 250px`.

**Wildcards in property values:**
```
:-abp-properties(width:*px;height:250px;)
```
Matches any width in pixels with a height of 250px.

**Regular expressions** (surround with `/`):
```
:-abp-properties(/width:30[2-8]px;height:250px;/)
```
Matches widths between 302px and 308px with height 250px.

**Pseudo-element matching:**
```
:-abp-properties(content:'Advertisement')
```
Matches elements where the string "Advertisement" appears in `::before` or `::after` pseudo-element content.

**Important notes:**
- Property names are matched **case-insensitively**.
- For `background-color`, use `rgb()` notation, not hex:
  ```
  ! WRONG:
  :-abp-properties(background-color: #3D9C4F;)
  ! CORRECT:
  :-abp-properties(background-color: rgb(61, 156, 79))
  ```
- Old bracket syntax `[-abp-properties='...']` is deprecated and auto-converted.

## `:not()` Integration

Extended selectors work correctly inside the standard CSS `:not()` pseudo-class (ABP 3.13+):

```
example.com#?#aside:not(:-abp-contains(Legitimate Content))
```
Hides all `<aside>` elements **except** those containing "Legitimate Content".

```
example.com#?#div:not(:-abp-has(> .keep))
```
Hides all `<div>` elements that do **not** have a direct child with class `keep`.

## `:xpath(expression)`

Selects elements using an **XPath expression** as an alternative to CSS selectors (ABP 3.13+).

```
:xpath(//*[contains(text(), 'ad')])
```
Selects any element containing the text "ad".

```
example.com#?#:xpath(//div[@class='ad-container']/..)
```
Selects the **parent** of any `div.ad-container` — useful when you need to hide the wrapper rather than the ad itself.

**When to use XPath:**
- Selecting parent/sibling elements (CSS can't go "up" the DOM tree)
- Complex text matching conditions
- Positional selection that CSS can't express

**Note:** XPath is powerful but verbose — prefer CSS selectors + `:-abp-has()`/`:-abp-contains()` when they can express the same logic.

## Best Practices

1. **Always use `#?#` separator** with extended selectors — `##` won't work.
2. **Be as domain-specific as possible** — `example.com#?#` is better than bare `#?#`.
3. **Avoid broad selectors** that could match `<body>` or `<html>`.
4. **Prefer `##` over `#?#`** — if standard CSS can express it, don't use extended selectors.
5. **Test thoroughly** — extended selectors are more likely to have unintended side effects.
