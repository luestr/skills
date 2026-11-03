# Inline CSS Styles & Remove Action

Element hiding filters can do more than just hide elements — they can apply custom CSS properties or completely remove elements from the DOM. These features extend the `##` and `#?#` syntax.

## Inline CSS Styles

Instead of hiding an element, you can apply specific CSS properties to it. This is useful for fixing layout artifacts left behind after hiding ads elsewhere on the page.

### Syntax

Append a CSS property block after the selector, separated by a space:

```
<domains>##<selector> { <property>: <value>; }
```

### Examples

```
example.com##.banner { margin-bottom: 0 }
```
On `example.com`, sets `margin-bottom: 0` on elements matching `.banner` (instead of hiding them).

```
example.com#?#.banner:-abp-has(.ad) { margin-bottom: 0 }
```
Same, but using an extended selector to find `.banner` elements that contain `.ad`.

### Valid CSS Properties

For security, not all CSS properties are allowed:

**Property names:** Must be valid CSS property names. Cannot start with `--` (custom properties are blocked).

**Property values:** Must match one of the following patterns:

| Category | Allowed Values |
|---|---|
| Global keywords | `inherit`, `initial`, `none`, `revert`, `revert-layer`, `unset` |
| Colors | Hex format only: `#000`, `#009900`, `#aabbccdd` (3–8 hex digits) |
| Color keywords | `currentcolor`, `transparent` |
| Numbers | Any literal number, optionally with units: `0`, `10px`, `1.5em`, `100%` |
| Number regex | `/^[+-]?(\d+(\.\d+)?|\.\d+)(e[+-]?\d+)?(cm\|mm\|q\|in\|pc\|pt\|px\|em\|ex\|ch\|rem\|lh\|rlh\|vw\|vh\|vmin\|vmax\|vb\|vi\|svw\|svh\|lvw\|lvh\|dvw\|dvh\|%\|fr)?$/` |
| Display values | `block`, `inline`, `inline-block`, `flex`, `inline-flex`, `grid`, `inline-grid`, `table`, `inline-table`, `table-row`, `flow-root`, `flow`, `list-item`, `ruby`, `none` |
| Position values | `absolute`, `relative`, `fixed`, `static`, `sticky`, `inset` |
| Visibility | `visible`, `hidden`, `collapse`, `clip` |
| Overflow | `auto`, `scroll`, `hidden` |
| Border styles | `solid`, `dashed`, `dotted`, `double`, `groove`, `ridge`, `inset`, `outset`, `thin` |
| Pointer | `pointer`, `default` |
| Other | `all`, `both`, `contain`, `element`, `fit-content`, `left`, `right`, `max-content`, `min-content`, `text`, `true` |

**Common use cases:**
```
! Fix gap left by removed ad banner
example.com##.content-wrapper { margin-top: 0 }

! Make room for content
news.example.com##.sidebar { width: 0 }

! Correct spacing
forum.example.com##.post-separator { border: none }
```

## Remove Action

The `remove: true;` declaration completely removes matching elements from the DOM, rather than just hiding them with CSS. This is more thorough — hidden elements can still trigger scripts or affect layout.

### Syntax

```
<domains>##<selector> { remove: true; }
```

### Examples

```
example.com##.banner { remove: true; }
```
Removes all `.banner` elements from the DOM on `example.com`.

```
example.com#?#.banner:-abp-has(.ad) { remove: true; }
```
Removes `.banner` elements containing `.ad` using an extended selector.

### Key Behaviors

- **Takes precedence** over any CSS properties — if both `remove: true;` and style properties are present, the element is removed.
- Works with both `##` and `#?#` selectors.
- Removed elements are gone from the DOM entirely — they can't be inspected in dev tools or trigger MutationObservers.

### Exception Rules for Remove and Inline Styles

Exception rules (`#@#`) only need to match the CSS selector — you don't need to repeat the style/remove block:

```
##aside.info { remove: true }
example.com#@#aside.info    ← This exempts the remove action
```

This makes exceptions cleaner — the selector match alone is sufficient to deactivate the entire filter (including its style or remove action).

## When to Use Each

| Goal | Approach |
|---|---|
| Hide an element (still in DOM, takes space) | `##selector` |
| Hide and collapse (no space) | `##selector { display: none }` or just `##selector` |
| Fix layout after hiding ads | `##selector { margin-top: 0 }` |
| Completely remove from DOM | `##selector { remove: true; }` |
| Remove elements matching complex criteria | `#?#selector { remove: true; }` |

## Security Notes

- Inline styles are restricted to safe CSS properties — no `url()`, no `expression()`, no custom properties.
- Property values are validated against an allowlist (see Valid CSS Properties above).
- `remove: true;` is irreversible within the page lifecycle — the element is gone until page reload.
