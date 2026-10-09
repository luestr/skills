# Basic Filter Rules

This module covers the foundational syntax of Adblock Plus blocking filters — how to match URLs using plain text, wildcards, address anchors, and separator characters, plus how to write comments.

## Plain Text Matching

The simplest filter is a plain string. Adblock Plus treats it as if surrounded by wildcards on both ends — it matches anywhere in the request URL.

```
ad
```
This matches any URL containing "ad" anywhere — including paths like `/advice/` or domains like `loadads.example`. Be careful not to make plain-text filters too short or generic, as they cause unintended blocking.

## Wildcards

The `*` character matches zero or more characters. It's the explicit wildcard, though ABP implicitly adds one at the start and end of every filter.

```
http://example.com/ads/banner*.gif
```
Matches `banner123.gif`, `bannerABC.gif`, etc. under `/ads/`.

```
http://example.com/ads/
```
Blocks everything in the `/ads/` directory.

**Warning:** Don't over-generalize. `http://example.com/` blocks *everything* from that domain — including content you probably want to see.

## Address Anchors (`|`)

By default, filters match anywhere in the URL. The pipe symbol `|` creates a definite boundary at the start or end.

### End anchor (`...|`)
```
swf|
```
Matches URLs *ending* with `swf` — blocks `http://example.com/annoyingflash.swf` but **not** `http://example.com/swf/index.html`.

### Start anchor (`|...`)
```
|http://baddomain.example/
```
Matches URLs *starting* with `http://baddomain.example/` — blocks `http://baddomain.example/banner.gif` but **not** `http://gooddomain.example/analyze?http://baddomain.example`.

### Domain anchor (`||`)
```
||example.com/banner.gif
```
The double pipe `||` matches at the beginning of the domain name. This blocks:
- `http://example.com/banner.gif`
- `https://example.com/banner.gif`
- `http://www.example.com/banner.gif`

But does **not** block:
- `http://badexample.com/banner.gif` (different domain)
- `http://gooddomain.example/analyze?http://example.com/banner.gif` (URL not at domain boundary)

**`||` is the most common and recommended way to target a specific domain.**

## Separator Character (`^`)

The `^` is a placeholder for a single separator character. A separator is any character that is **not** a letter, digit, or one of `_`, `-`, `.`, `%`. The end of the URL also counts as a separator.

```
http://example.com^
```
Matches `http://example.com/` and `http://example.com:8000/` but **not** `http://example.com.ar/` (because `.ar` is letters/digits/dots, not a separator).

**Identifying separators in a URL:**

```
http://example.com:8000/foo.bar?a=12&b=%D1%82
```
Separator characters at positions: `://`, `:`, `/`, `.`, `?`, `=`, `&`, `=` (shown bolded in ABP docs). The `^` matches any of these.

**Common use:** `||example.com^` matches exactly the domain `example.com` with any path, port, or query — the standard "match entire domain" pattern.

## Combining Techniques

These building blocks compose together:

```
||cdn.example.com/ads/*.js$script
```
- `||cdn.example.com` — matches the domain
- `/ads/*.js` — matches JS files under `/ads/`
- `$script` — only applies to script requests (see Network Options module)

## Comments (`!`)

Any line starting with `!` is a comment. Adblock Plus ignores it for blocking purposes.

```
! This filter blocks example.com ads
||example.com/ads/

! Allow news section through
@@||example.com/news^$document
```

Comments are essential for filter list maintenance — use them to explain *why* a filter exists, not just what it does (the syntax itself is usually readable for the "what").

## Tips

- Prefer `||domain^` over broad wildcards for domain-level blocking.
- Use end anchors (`|`) to avoid matching substrings in unrelated URLs.
- Keep filters as specific as possible to reduce false positives.
- Always comment complex filters — your future self (and other filter authors) will thank you.
