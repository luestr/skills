# Basic Rules Syntax

> The simplest rule type for blocking or allowing requests to specific URLs.

## Important Notes

- Basic rules apply only to **sub-requests** by default — they do not block page loading (unless `$document` is used)
- Blocked requests appear as "request failed" in the browser
- Rules shorter than **4 characters** are ignored
- AdGuard truncates URLs to **4096 characters** for faster matching

## Syntax

```
rule = ["@@"] pattern ["$" modifiers]
modifiers = [modifier0, modifier1[, ...[, modifierN]]]
```

- **pattern** — address mask; every request URL is matched against this mask
- **`@@`** — exception marker; starting with `@@` means the rule allows requests
- **modifiers** — parameters that limit or change rule behavior

## Special Characters

### `*` — Wildcard

Matches any set of characters (can be empty string or any length).

### `||` — Domain Match

Applies the rule to the specified domain and its subdomains. Equivalent to matching `https://*.`, `http://*.`, `ws://*.`, `wss://*.` simultaneously.

**Example:**
```
||example.com^
```
Blocks:
- `https://example.com/ad1.gif`
- `https://subdomain.example.com/ad1.gif`
- `https://ads.example.com:8000/`

Does not block:
- `https://example.org/`
- `https://example.com.us/ad1.gif`

### `^` — Separator Marker

A separator is any character **except letters, digits, `_`, `-`, `.`, `%`**. The end of the URL is also treated as a separator.

**Example:**
```
http://example.com/?t=1&t2=t3
```
Separator characters (bold): `://`, `/`, `?`, `=`, `&`, `=`

### `|` — Address Start/End Marker

Depending on placement, matches the beginning or end of the address.

**Example:**
```
swf|
```
Matches `https://example.com/annoyingflash.swf`
Does not match `https://example.com/swf/index.html`

```
|https://example.org
```
Matches `https://example.org`
Does not match `https://domain.com?url=https://example.org`

### Important Limitation

`|`, `||`, `^` can only be used with rules that have a URL pattern. For example, `||example.com##.advert` is incorrect.

## Regular Expressions Support

For more flexible matching, you can use regular expressions instead of the simplified mask with special characters.

**Performance note:** Regex rules match more slowly — avoid them or limit their scope to specific domains.

**Syntax:** Pattern enclosed in `/`:
```
pattern = "/" regexp "/"
```

**Example:**
```
/banner\d+/$third-party
```
Applies the regex `banner\d+` to all third-party requests.

**Exception rule:**
```
@@/banner\d+/
```

### Compatibility

AdGuard Safari and AdGuard for iOS do not fully support regular expressions (Content Blocking API restrictions).

## TLD Wildcard Support

TLD wildcard `.*` is supported in domain patterns of cosmetic rules, HTML filtering, and JavaScript rules.

**Cosmetic rule example:**
```
example.*##.banner
```
Matches `example.com`, `sub.example.net`, `example.co.uk`, etc.

**`$domain` modifier in basic rules:**
```
||*/banners/*$image,domain=example.*
```

### Compatibility

- In AdGuard for Windows/Mac/Android and Browser Extension, `.*` matches any public suffix (eTLD)
- AdGuard for Safari/iOS has a limited list of supported TLDs
- AdGuard Content Blocker does not support TLD wildcards

## Basic Rule Examples

```adblock
||example.com/ads/*
```
Matches `https://example.com/ads/banner.jpg` and `https://subdomain.example.com/ads/otherbanner.jpg`

```adblock
||example.org^$third-party
```
Blocks third-party requests to example.org and its subdomains

```adblock
@@||example.com$document
```
Completely disables filtering on example.com and all subdomains
