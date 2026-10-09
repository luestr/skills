---
name: Write AdblockPlus Filters
description: "Write, debug, and explain Adblock Plus (ABP) filter syntax. Use this skill whenever the user needs to create ABP filters, understand filter syntax, build filter lists, debug why a filter isn't working, convert between filter types, or learn about ABP-specific features like extended CSS selectors, snippet filters, or sitekey. Also trigger when users mention ad blocking rules, element hiding, filter options, EasyList format, or any ABP filter-related question — even if they don't explicitly say 'Adblock Plus.'"
---

# Write Adblock Plus Filters

You are an expert in Adblock Plus filter syntax. Your job is to help users write correct, efficient filters and filter lists.

## How to Use This Skill

This skill is organized into **8 reference modules** covering every aspect of ABP filter syntax. Based on the user's question, read **only the relevant module(s)** — do not load all references at once.

### Routing Guide

| User Question About | Read This Reference |
|---|---|
| Basic filter syntax, wildcards (`*`), address matching (`\|`, `\|\|`), separator (`^`), comments (`!`) | `references/01-basic-rules.md` |
| Exception rules (`@@` prefix), allowlisting requests/pages | `references/02-exception-rules.md` |
| Filter options: `$script`, `$image`, `$domain`, `$third-party`, `$match-case`, `$popup`, `$csp`, `$rewrite`, `$header`, `$addheader`, regex filters, etc. | `references/03-network-options.md` |
| Element hiding (`##`), CSS selectors, attribute selectors, domain limiting for content filters | `references/04-element-hiding.md` |
| Extended CSS selectors: `:-abp-has()`, `:-abp-contains()`, `:-abp-properties()`, `:xpath()`, `:not()` | `references/05-extended-selectors.md` |
| Inline CSS styles in filters, `remove: true;` action | `references/06-inline-styles-remove.md` |
| Snippet filters (`#$#`), behavioral snippets, conditional hiding, shadow DOM, JSONPath | `references/07-snippet-filters.md` |
| Special comments: `! Title:`, `! Homepage:`, `! Expires:`, `! Redirect:`, `! Version:` | `references/08-special-comments.md` |

### Multi-Topic Questions

If the user's question spans multiple topics (e.g., "write a filter that blocks scripts on example.com and hides a div"), read all relevant modules. For a full syntax overview or "how do ABP filters work" questions, you may read modules 01–04 as the core set.

### Workflow

1. **Understand** the user's intent — what they want to block, hide, allow, or debug.
2. **Read** the relevant reference module(s) listed above.
3. **Write** the filter(s) with a brief explanation of each syntax element used.
4. **Validate** — double-check syntax against the reference before presenting.
5. If the user provides a filter that isn't working, **diagnose** by checking each syntax component against the reference.

### Key Principles

- Filters are case-insensitive by default. Use `$match-case` if case matters.
- The `^` separator matches anything except letters, digits, and `_ - . %`.
- `||domain^` is the standard pattern for matching an entire domain.
- Element hiding (`##`) works at the CSS level — it hides but doesn't block.
- Extended selectors (`#?#`) have a performance cost — prefer standard `##` when possible.
- Snippet filters (`#$#`) can only be added to user custom filters or the ABP Anti-Circumvention list.
- Header matching (`$header=`) and add header (`$addheader=`) are Firefox-only features.

### Pre-installed Filter Lists

Adblock Plus comes with these filter lists pre-installed:
- **Acceptable Ads** — allows non-intrusive ads by default (can be disabled)
- **EasyList** — the primary ad-blocking list, plus a bundled language-specific list based on browser locale
- **ABP Anti-Circumvention Filter List** — targets sites that try to bypass ad blockers

Users can add their own custom filters via the ABP Settings page (Advanced tab → "Create and edit your filter list").

### Generic vs. Specific Filters

The distinction between generic and specific filters matters for `$generichide` and `$genericblock`:

- **Specific filter** — matches one or more domains or has a sitekey. Examples: `example.com##.textad`, `/ads/*$domain=example.com`
- **Generic filter** — has no domain restrictions (or only domain exceptions) and no sitekey. Examples: `##.textad`, `~example.com##.textad`, `||example.com^`

For blocking rules, the domain must be under `$domain` to be specific: `||example.com^` is generic, but `/ads/*$domain=example.com` is specific.

### Common Patterns Quick Reference

```
||example.com^                    Block entire domain
||example.com/ads/*$script        Block scripts under /ads/
@@||example.com^$document         Allowlist entire site
example.com##.ad-banner           Hide .ad-banner on example.com
example.com#?#div:-abp-has(.ad)   Hide divs containing .ad (extended)
example.com#$#abort-on-property-read adblock   Run snippet on example.com
```
