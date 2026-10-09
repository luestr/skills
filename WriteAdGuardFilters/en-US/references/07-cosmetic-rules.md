# Cosmetic Rules

> Used to hide or modify web page elements. Requires basic HTML and CSS knowledge.

## Non-Basic Rules Overview

| Category | CoreLibs | Chromium | MV3 | Firefox | iOS | Safari | Content Blocker |
|---|---|---|---|---|---|---|---|
| Element hiding | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CSS rules | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Extended CSS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| HTML filtering | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| JavaScript | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Scriptlets | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |

---

## Element Hiding Rules

Hide web page elements (equivalent to `display: none`).

**Syntax:**
```
rule = [domains] "##" selector
```

**Domain restrictions:**
```adblock
example.com##div.textad                        -- Restrict to domain
example.com,example.org###adblock              -- Multiple domains
~example.com##.textad                          -- Exclude domain
example.org,~subdomain.example.org##.textad    -- Mixed usage
```

**Exception rules:** Use `#@#` instead of `##`
```adblock
example.com#@#.textad
#@#.textad          -- Disable this rule on all domains
*#@#.textad         -- Same as above
```

**Safari limitation:** Cannot specify both allowed and excluded domains (e.g. `example.org,~foo.example.org##.textad`).

---

## CSS Rules

Inject custom CSS styles (more flexible than simple hiding).

**Syntax:**
```
rule = [domains] "#$#" selector "{" style "}"
```

**Example:**
```adblock
example.com#$#body { background-color: #333!important; }
```

**Exception rules:** Use `#@$#` instead of `#$#`
```adblock
example.com#@$#.textad { visibility: hidden; }
```

**Restrictions:** Styles that load resources are forbidden (cannot use `<url>` type values). Not supported by Content Blocker.

**ABP compatibility:** CoreLibs v1.18+ supports `remove: true` declaration in element hiding rules:
```adblock
example.org##body { remove: true; }
```

---

## Extended CSS Selectors

Extends CSS 3.0 capabilities, supporting matching based on element's own representation (style, text content, etc.) or relationships with other elements.

**Rule markers (recommended):**
- `#?#` — element hiding, `#@?#` — exception
- `#$?#` — CSS rules, `#@$?#` — exception

**Application scope:** Can be used in any cosmetic rule (element hiding or CSS rules).

Not supported by Content Blocker.

---

### ExtendedCss General Limitations

1. CSS comments and at-rules are not supported
2. Specific pseudo-classes have their own limitations (see below)

---

### `:has()` — Relational Matching

Selects target elements containing specified child elements. CSS 4.0 spec, natively supported by most browsers.

**Syntax:**
```
[target]:has(selector)
```

- `target` — optional, standard or extended CSS selector
- `selector` — required, supports selector lists (currently "match all")

**Detailed examples:**

```adblock
div:has(.banner)                  -- Select div containing .banner descendant
div:has(> .banner)                -- Select div with .banner as direct child
div:has(+ .banner)                -- Select div immediately before .banner (adjacent sibling)
div:has(~ .banner)                -- Select div before .banner (general sibling)
div:has(span, .banner)            -- Select div containing both span and .banner
```

**Compatibility:**
- CoreLibs v1.12+ native support
- Safari 16.4+ / SafariConverterLib v2.0.39+ native support
- Browser Extension v5.3+ native support (MV3 always uses native)
- Use `#?#` to force ExtendedCss implementation
- `:has()` cannot be nested inside another `:has()` (native implementation)

**Aliases:** `:-abp-has()` (compat). `:if()` removed.

---

### `:contains()` — Text Content Matching

Selects elements containing specified text or matching regex.

**Syntax:**
```
[target]:contains(unquoted text)
[target]:contains(/regexp/)
```

**Important:** `:contains()` matches using the `textContent` property, not `innerHTML`. This means it matches the element's plain text content, not the tag code of child elements.

**Examples:**
```adblock
div:contains(banner)               -- Match div containing text "banner"
div:contains(/as .*banner/)        -- Regex match
div:contains(/it .*banner/gi)      -- Regex with flags (case-insensitive)
```

**Note:** `:-abp-contains()` and `:has-text()` are synonyms.

---

### `:matches-css()` — CSS Property Matching

Selects elements with specified computed CSS properties.

**Syntax:**
```
[target]:matches-css([pseudo-element, ] property: value)
[target]:matches-css-after(property: value)
[target]:matches-css-before(property: value)
```

- `pseudo-element` — optional, standard pseudo-element like `before`, `after`, `first-line`, etc.
- `property` — required, CSS property name
- `value` — required, supports wildcards or regex (always case-insensitive)

Regex support: `:matches-css(width: /3[0-9]0px/)`

**Escaping rules:** In non-regex mode, `(`, `)`, `[`, `]` must be **unescaped**; in regex mode, `\` must be **escaped**.

**Examples:**
```adblock
div:matches-css(before, content: block me)    -- Pseudo-element match
div:matches-css(before, content: block*)      -- Wildcard
div:matches-css(before, content: /block me/)  -- Regex
```

**Note:** Regex mode does **not** support flags. Deprecated `:matches-css-before()` and `:matches-css-after()` are still supported for compatibility.

---

### `:matches-attr()` — Attribute Pattern Matching

Selects elements with attributes matching specified patterns.

**Syntax:**
```
[target]:matches-attr("name"[="value"])
```

Both name and value support wildcards and regular expressions.

**Examples:**
```adblock
div:matches-attr("ad-link")                   -- Match div with ad-link attribute
div:matches-attr("data-*"="adBanner")         -- Wildcard match attribute name
div:matches-attr(*unit*=/^click$/)            -- Wildcard name + regex value
*:matches-attr("/.{5,}delay$/"="/^[0-9]*$/")  -- Regex match name and value
```

**Escaping rules:** In regex mode, `"` and `\` must be escaped, e.g. `div:matches-attr(class=/[\\w]{5}/)`. Regex mode does **not** support flags.

---

### `:matches-property()` — JS Property Matching

Selects elements with matching JavaScript properties.

**Syntax:**
```
[target]:matches-property("name"[="value"])
```

**Examples:**
```adblock
div:matches-property(check.track)
div:matches-property("check./^unit_.{4,8}$/")
div:matches-property("check.unit_*"=true)
div:matches-property(memoizedProps.key="null")
```

**Debugging tip:** In DevTools, select the element and run `console.dir($0)` in Console to view properties.

---

### `:xpath()` — XPath Expression

Selects elements via XPath expression.

**Syntax:**
```
[target]:xpath(expression)
```

**Limitations:**
- When target is omitted, automatically limited to `body` tag
- Only valid at the end of selector (except `:remove()`)

**Examples:**
```adblock
:xpath(//*[@class="banner"])
:xpath(//*[@class="inner"]/..)
```

---

### `:nth-ancestor()` — Nth Ancestor

Looks up the Nth ancestor element.

**Syntax:**
```
subject:nth-ancestor(n)
```
N: 1~255

**Limitation:** Cannot be used inside `:not()` argument.

---

### `:upward()` — Match Ancestor

Looks up matching ancestor elements.

**Syntax:**
```
subject:upward(ancestor)
```
`ancestor` can be a number (1~255, equivalent to `:nth-ancestor()`) or a standard CSS selector.

**Limitation:** Cannot be used inside `:not()` argument.

---

### `:remove()` — Remove Elements

Removes matching elements (not just hides them). **Can only be placed at the end of a selector.**

**Syntax:**
```adblock
selector:remove()
selector { remove: true; }    -- Pseudo-property, requires #$?# marker
```

**Examples:**
```adblock
div.banner:remove()
div:has(> div[ad-attr]):remove()
div:contains(advertisement) { remove: true; }
```

When using `:remove()`, all style properties are ignored (except `debug`). To select any element, use `*`: `.banner > *:remove()`.

---

### `:is()` — Match Any

Implementation of standard CSS `:is()`. Matches elements that can be selected by any selector in the list.

**Syntax:**
```
[target]:is(selectors)
```

**Limitations:**
- Extended selector arguments only support compound selectors, not complex selectors
- `#?#:is(...)` and `#?#*:is(...)` are parsed as `#?#html *:is(...)`
- Uses native implementation when `##` marker is used with no other extended selectors

---

### `:not()` — Negation Matching

Implementation of standard CSS `:not()`. Selects elements that do not match the argument selectors.

**Syntax:**
```
[target]:not(selectors)
```

**Limitations:**
- `:nth-ancestor()` and `:upward()` cannot be used inside `:not()` argument
- Uses native implementation when `##` marker is used with no other extended selectors

`:if-not()` removed.

---

## Cosmetic Rules Priority

How cosmetic rules are applied varies by platform:

| Platform | Implementation | Characteristics |
|---|---|---|
| CoreLibs apps | Injected stylesheet | Same priority as website CSS, **cannot override inline styles** |
| Browser Extension | User stylesheet | Priority **higher than inline styles** |
| Extended CSS selectors | JavaScript | Adds inline styles, **can override any style** |
