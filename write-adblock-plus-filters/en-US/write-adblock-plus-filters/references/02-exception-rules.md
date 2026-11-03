# Exception Rules

Exception rules define cases where blocking filters should *not* be applied. They allow you to "punch holes" in existing filters without modifying them — essential when extending filter lists you don't control.

## Basic Syntax

Prefix any filter pattern with `@@` to create an exception rule:

```
@@advice
```
This prevents any filter matching `advice` from blocking a request. So if you have the filter `adv` which accidentally blocks `http://example.com/advice.html`, the exception `@@advice` rescues that page.

Exception rules use the same matching syntax as blocking filters — wildcards, anchors (`|`, `||`), separator (`^`), and regular expressions all work.

## Page-Level Exception (`$document`)

The `$document` option turns off **all** Adblock Plus blocking on the matched page:

```
@@||example.com^$document
```
When you visit any page on `example.com`, ABP is completely disabled — no filters of any kind apply. This is the "whitelist the entire site" escape hatch.

## Element Hiding Exception (`$elemhide`)

Similar to `$document`, but only disables element hiding rules — network-level blocking still applies:

```
@@||example.com^$elemhide
```
On `example.com`, all `##` element hiding rules are turned off, but network requests can still be blocked.

## Generic Exception (`$generichide`, `$genericblock`)

These are more targeted exceptions:

```
@@||example.com^$generichide
```
Disables only *generic* element hiding rules on `example.com` (rules without domain restrictions, like `##.ad-banner`). Site-specific rules (like `example.com##.sponsor`) still apply.

```
@@||example.com^$genericblock
```
Same concept but for *generic* blocking rules (network-level filters without domain restrictions).

## Combining Exception Options

You can combine multiple exception options:

```
@@||example.com^$document,elemhide
```
This is equivalent to `$document` alone (since `$document` already implies `$elemhide`), but being explicit can improve readability.

## When to Use Exception Rules

| Scenario | Use |
|---|---|
| A filter blocks something it shouldn't | `@@<matching-pattern>` |
| Whitelist an entire site | `@@\|\|site.com^$document` |
| Disable element hiding on a site | `@@\|\|site.com^$elemhide` |
| Disable only generic rules on a site | `@@\|\|site.com^$generichide` |
| Extending a filter list you can't modify | Add exceptions to your own list |

## Exception vs. Domain Restriction

When you *can* modify the original filter, prefer restricting it with `$domain=` over adding an exception. Exception rules are the tool of last resort — use them when you're extending someone else's filter list and can't change the overly broad filter.

```
! Prefer this (restrict the filter):
||example.com/ads/$domain=example.com|example.net

! Over this (broad filter + exception):
||example.com/ads/
@@||example.com/ads/$domain=example.org
```

## Important Notes

- Exception rules apply to *all* matching filters, not just one specific filter.
- `$document` exceptions are very broad — use them sparingly.
- Exception rules for element hiding use the `#@#` syntax instead of `@@` (see Element Hiding module).
