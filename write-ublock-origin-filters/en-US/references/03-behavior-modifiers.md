# Behavior Modifiers

> Options that control how network filters behave — party restrictions, domain targeting, priority, and special behaviors.

## Party Restriction Options

### `$third-party` / `$3p`

Match only requests originating from a different domain than the currently visited site.

```
||tracker.com^$third-party
```
Blocks requests to tracker.com when made from OTHER sites. Won't block if you're directly visiting tracker.com.

### `$first-party` / `$1p`

Match only requests originating from the same domain (or related domains). Equivalent to `~third-party`.

```
||example.com/track^$first-party
```
Blocks tracking requests made by example.com on its own pages.

### `$strict1p`

New in uBO 1.20.0. Similar to `$first-party` but stricter: the request's origin must exactly match the document's origin (no domain relaxation).

```
||example.com^$strict1p
```

### `$strict3p`

New in uBO 1.20.0. Similar to `$third-party` but stricter: matches only when the request origin is strictly different from the document origin.

```
||tracker.com^$strict3p
```

## Domain Targeting Options

### `$domain=` / `$from=`

Restrict a filter to only apply when the page making the request matches specified domains. `$from` is the modern alias.

```
||tracker.com^$3p,domain=example.com|example.org
```
Blocks third-party tracker.com requests only when made from example.com or example.org.

**Negation:** Prefix domain with `~` to exclude:
```
||ads.com^$domain=example.com|~sub.example.com
```
Applies on example.com but NOT on sub.example.com.

**Entity matching:** `google.*` matches all Google TLDs:
```
||ads.com^$domain=google.*
```

**Regex domains** (1.46.1b15+):
```
@@*$ghide,domain=/img[a-z]{3,4}\.buzz/
```

### `$to=` 

New in uBO 1.20.0. Restrict a filter to match only when the request URL's target domain matches. Useful for narrowing which destinations a filter applies to.

```
*$frame,from=plainlight.com,to=~/youtube/
```
Block frames on plainlight.com targeting any domain except YouTube.

**Entity and regex support:** Same as `$domain`.

### `$denyallow`

New in uBO 1.26.0. Brings default-deny/allow-exceptionally ability to static network filtering. Requires `$domain=` to be present.

```
*$3p,script,denyallow=x.com|y.com,domain=a.com|b.com
```
When on a.com or b.com, block all 3rd-party scripts EXCEPT those from x.com and y.com.

This is much cleaner than using broad blocking + exception filters. Entity wildcard matching is NOT supported with `$denyallow`.

## Priority Options

### `$important`

Force a blocking filter to override all exception filters, regardless of specificity.

```
||ads.example.com^$important
```
This blocking rule wins over any `@@` exception rule for the same URL.

**Key behavior:** An `$important` blocking filter always beats an exception filter. Without `$important`, the more specific filter wins.

### `$badfilter`

Used to disable an existing filter from another filter list. The `badfilter` filter must exactly match the target filter's pattern and options.

```
*$image,badfilter
```
Disables the `*$image` filter wherever it's defined.

**After 1.19.0:** Filters of the form `|https://` or `|http://` with a `domain=` option are decomposed into per-domain filters, allowing you to `badfilter` just one domain:
```
|https://$domain=a.com|b.com
```
Can be selectively disabled:
```
|https://$domain=a.com,badfilter
```

## Display/Behavior Options

### `$elemhide` / `$ehide`

Disable all cosmetic filters (element hiding) on matching pages.

```
@@||example.com^$elemhide
```
Disables cosmetic filtering on example.com.

### `$generichide` / `$ghide`

Disable only generic cosmetic filters (those without a hostname prefix) on matching pages. Site-specific cosmetic filters still apply.

```
@@||example.com^$generichide
```

### `$specifichide` / `$shide`

Disable only site-specific cosmetic filters on matching pages. Generic cosmetic filters still apply.

```
@@||example.com^$specifichide
```

### `$popunder`

Match popunder windows (popups that open behind the current window).

```
||example.com^$popunder
```

### `$inline-script`

Prevent inline scripts from executing on the page. Blocks `<script>` tags that contain inline code (not external scripts).

```
||example.com^$inline-script
```

### `$inline-font`

Prevent inline fonts from loading (fonts defined in `<style>` tags or `style` attributes).

```
||example.com^$inline-font
```

## Request Matching Options

### `$match-case`

Make the filter pattern case-sensitive. By default, patterns are case-insensitive.

```
||Example.COM^$match-case
```
Only matches `Example.COM`, not `example.com` or `EXAMPLE.COM`.

### `$method=`

Match requests by HTTP method (GET, POST, PUT, DELETE, etc.). New in uBO.

```
||example.com/api^$method=post
```
Only matches POST requests to the API.

### `$header=`

Match requests based on the presence (or specific value) of a response header.

```
||example.com^$header=content-type:application/json
```
Matches when the response has the specified header value.

### `$permissions`

Set a Permissions-Policy header on responses. Trusted source only.

```
||example.com^$permissions=autoplay=()
```

### `$ipaddress`

Return a specific IP address for matched DNS requests. New in uBO.

```
||tracker.example.com^$ipaddress=0.0.0.0
```

### `$cname`

Framework compatibility: Firefox MV2 only (1.26.0+).

When used in an exception filter, bypasses CNAME uncloaked request blocking.

```
@@*$cname
```
Accepts network requests that are blocked due to CNAME uncloaking.

Filter list authors should use this sparingly and as narrowly as possible.

## Examples

```adblock
||tracker.com^$3p,domain=example.com|example.org,image
```
Block third-party image tracker requests from example.com and example.org

```adblock
*$script,denyallow=cdn.trusted.com|apis.safe.com,domain=news.example.com
```
On news.example.com, block all scripts except from cdn.trusted.com and apis.safe.com

```adblock
@@||example.com^$elemhide
```
Disable all element hiding on example.com

```adblock
||ads.example.com^$important,domain=~trusted.example.com
```
Force-block ads.example.com everywhere except on trusted.example.com

```adblock
||cdn.example.com^$image,badfilter
```
Disable an overly broad image blocking rule
