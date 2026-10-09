# Element Hiding (Content Filters)

Element hiding filters target page content that can't be blocked at the network level — advertisements embedded directly in the HTML, styled as regular content. These filters use CSS selectors to identify and hide (or manipulate) DOM elements.

## Content Filter Structure

All content filters follow this pattern:

```
<domains><separator><body>
```

- **domains** — Comma-separated domain list (may be empty for generic filters)
- **separator** — Determines the filter type
- **body** — CSS selector or snippet code

### Separator Reference

| Separator | Type | Body Content |
|---|---|---|
| `##` | Element hiding | CSS selector |
| `#?#` | Element hiding emulation | Extended CSS selector |
| `#@#` | Element hiding exception | CSS selector |
| `#$#` | Snippet filter | JavaScript snippet code |

## Element Hiding (`##`)

The `##` separator creates an element hiding rule. The body is a standard CSS selector that identifies elements to hide.

```
##.textad
```
Hides any element with `class="textad"` on **all** sites.

```
###sponsorad
```
Hides the element with `id="sponsorad"`.

```
##textad
```
Hides all `<textad>` elements (by tag name).

## Domain-Limited Rules

Prefix the filter with domains to restrict where it applies:

```
example.com##.sponsor
```
Hides `.sponsor` elements on `example.com` and its subdomains (e.g., `sub.example.com`), including inside iframes with matching URLs.

**Multiple domains** (comma-separated):
```
domain1.example,domain2.example,domain3.example##.sponsor
```

**Exclude a domain** (tilde prefix):
```
~example.com##.sponsor
```
Hides `.sponsor` on every site **except** `example.com`.

**Combine inclusion and exclusion:**
```
example.com,~foo.example.com##.sponsor
```
Hides `.sponsor` on `example.com` but not on `foo.example.com`.

**Important:** Domain restrictions in element hiding only work with full domain names — you cannot use partial matches or address paths.

## Attribute Selectors

Use CSS attribute selectors to target elements without IDs or classes:

```
##table[width="80%"]
```
Hides tables with `width` attribute set to `80%`.

```
##div[title*="adv"]
```
Hides `<div>` elements whose `title` attribute *contains* "adv".

```
##div[title^="adv"][title$="ert"]
```
Hides `<div>` elements with `title` **starting** with "adv" and **ending** with "ert".

**Multiple attribute conditions:**
```
##table[width="80%"][bgcolor="white"]
```
Matches tables with both `width="80%"` and `bgcolor="white"`.

### CSS Attribute Selector Quick Reference

| Selector | Meaning |
|---|---|
| `[attr="val"]` | Exact match |
| `[attr*="val"]` | Contains "val" |
| `[attr^="val"]` | Starts with "val" |
| `[attr$="val"]` | Ends with "val" |
| `[attr~="val"]` | Contains word "val" (space-separated) |
| `[attr\|="val"]` | Starts with "val" (hyphen-separated) |

## Advanced CSS Selectors

Any CSS selector supported by browsers can be used:

```
##.adheader + *
```
Hides anything immediately following an element with class "adheader".

```
##div.sidebar > span
```
Hides `<span>` elements that are direct children of `div.sidebar`.

Common advanced selectors:
- **Combinators:** `>`, `+`, `~`, ` ` (descendant)
- **Pseudo-classes:** `:first-child`, `:nth-child()`, `:not()`, `:has()` (browser-native)
- **Pseudo-elements:** `::before`, `::after`

**Performance warning:** Complex selectors (especially descendant and sibling combinators) are slower to process than class/ID selectors. Use them only when simpler selectors can't target the element.

**Validation:** Adblock Plus rejects filters with invalid CSS syntax — always verify your selectors.

## Element Hiding Emulation (`#?#`)

When standard CSS selectors aren't powerful enough, use `#?#` with ABP's extended CSS selectors (see the Extended Selectors module for details):

```
example.com#?#div:-abp-has(.sponsored)
```

**Performance note:** `#?#` filters are slower than `##` because they require ABP to evaluate the extended selectors actively. Use `##` whenever standard CSS can express the rule, and reserve `#?#` for cases that genuinely need extended selectors.

## Element Hiding Exception (`#@#`)

Deactivate an element hiding rule on specific domains:

```
##.textad
example.com#@#.textad
```
The first rule hides `.textad` everywhere. The second rule exempts `example.com`. The combined effect is identical to `~example.com##.textad`.

Exception rules also apply to extended CSS selectors (`#?#` rules).

**When to use exceptions vs. domain restriction:**
- If you control the original filter → use domain restriction (`~example.com##.textad`)
- If you're extending someone else's filter list → use exceptions (`#@#`)

**Inline style and remove action:** If the filter being exempted has inline CSS styles or `remove: true;`, the exception rule only needs to match the CSS selector — the style/remove part is automatically exempted.

```
##aside.info {remove: true}
example.com#@#aside.info     ← This exempts the remove action too
```
