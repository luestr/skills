# Basic Modifiers

> The most common and simplest modifiers, primarily used to limit rule application scope.

## Compatibility Overview

| Modifier | CoreLibs | Chromium | MV3 | Firefox | iOS | Safari | Content Blocker |
|---|---|---|---|---|---|---|---|
| `$app` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$denyallow` | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| `$domain` | ✅ | ✅ | ✅*[1]* | ✅ | ✅*[1]* | ✅*[1]* | ✅ |
| `$header` | ✅ | ✅*[2]* | ✅*[2]* | ✅*[2]* | ❌ | ❌ | ❌ |
| `$important` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `$match-case` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$method` | ✅ | ✅ | ✅ | ✅ | ✅*[2]* | ✅*[2]* | ❌ |
| `$popup` | ✅*[3]* | ✅ | ✅*[3]* | ✅ | ✅*[3]* | ✅*[3]* | ❌ |
| `$strict-first-party` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$strict-third-party` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$third-party` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$to` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## `$app` — Restrict to Application

Limits the rule to a specific application (or list of applications).

**Syntax:**
```
$app = ["~"] entry_0 ["|" ["~"] entry_1 [...]]
entry = ( regular_app / wildcard_app / regexp )
```

- `regular_app` — regular app name, e.g. `org.example.app`
- `wildcard_app` — ending with `*`, e.g. `org.example.*`
- `regexp` — regex enclosed in `/`

**Examples:**
```adblock
||baddomain.com^$app=org.example.app
||baddomain.com^$app=org.example.app1|org.example.app2
||baddomain.com^$app=~org.example.app
||baddomain.com^$app=org.example.*
||baddomain.com^$app=/org\.example\.[a-z0-9_]+/
```

**Restrictions:** Cannot mix negated and non-negated expressions; wildcards cannot be used mid-string.

**Compatibility:** CoreLibs apps only. Regex and mixed types require CoreLibs v1.19+.

---

## `$denyallow` — Exclude Target Domains

Avoids creating additional exclusion rules for specific domains. Matches target domains only, not referrer domains.

**Equivalence:**
```adblock
*$script,domain=a.com|b.com,denyallow=x.com|y.com
```
Is equivalent to:
```adblock
*$script,domain=a.com|b.com
@@||x.com$script,domain=a.com|b.com
@@||y.com$script,domain=a.com|b.com
```

**Restrictions:**
- Rule pattern cannot start with `||`
- Cannot be used with `$to`
- No negated domains, TLD wildcards, or regex

**Compatibility:** Not supported on iOS/Safari/Content Blocker.

---

## `$domain` — Restrict to Source Domain

Limits the rule to requests made **from** the specified domains and their subdomains (based on Referer header).

**Syntax:**
```
$domain = ["~"] entry_0 ["|" ["~"] entry_1 [...]]
entry = ( regular_domain / any_tld_domain / regexp )
```

- `regular_domain` — regular domain, e.g. `domain.com` (includes subdomains)
- `any_tld_domain` — ending with `.*`, e.g. `example.*` (matches all public suffixes)
- `regexp` — regex; `/`, `$`, `,`, `|` must be escaped with `\`

**Alias:** `$from` (CoreLibs v1.12+)

**Examples:**
```adblock
||baddomain.com^$domain=example.org
||baddomain.com^$domain=example.org|example.com
||baddomain.com^$domain=~example.org
||baddomain.com^$domain=example.org|~foo.example.org
||baddomain.com^$domain=/(^\|.+\.)example\.(com|org)$/
```

**Special behavior:** When the rule contains `$cookie`, `$csp`, `$permissions`, `$removeparam`, `$domain` can also match the target domain (not just referrer).

**Restrictions:**
- MV3 does not support regex and TLD wildcards
- Safari/iOS has additional limitations
- Regex requires CoreLibs v1.11+

---

## `$header` — Match HTTP Response Header

Matches requests with specific HTTP response headers.

**Syntax:**
```
$header = h_name [":" h_value]
h_value = string / regexp
```

**Examples:**
```adblock
||example.com^$header=set-cookie:foo
||example.com^$header=set-cookie
@@||example.com^$header=set-cookie:/foo\, bar$/
```

**Restrictions:** Can only match after response headers are received; Browser Extension only compatible with specific modifiers.

**Compatibility:** CoreLibs v1.11+, TSUrlFilter v3.0.0+, MV3 v5.3+.

---

## `$important` — Increase Priority

Increases rule priority above rules without this modifier (including basic exception rules).

**Examples:**
```adblock
||example.org^$important
@@||example.org^
```
The blocking rule takes effect because `$important` has higher priority.

```adblock
||example.org^$important
@@||example.org^$important
```
Both have `$important`, so the exception rule takes effect.

---

## `$match-case` — Case-Sensitive Matching

Rules are case-insensitive by default. This modifier makes the rule match only when case matches exactly.

**Example:**
```adblock
*/BannerAd.gif$match-case
```
Blocks `https://example.com/BannerAd.gif`, but not `https://example.com/bannerad.gif`

---

## `$method` — Restrict HTTP Method

Limits the rule to requests using specified HTTP methods. Methods must be lowercase, but matching is case-insensitive. Negation is supported.

**Examples:**
```adblock
||evil.com^$method=get|head
||evil.com^$method=~post|~put
@@||evil.com$method=get
```

**Restrictions:** Cannot mix negated and non-negated values. Negation not supported on iOS/Mac.

**Compatibility:** CoreLibs v1.12+, TSUrlFilter v2.1.1+.

---

## `$popup` — Close Popups

AdGuard will try to close the browser tab with any address that matches a blocking rule with this modifier.

**Example:**
```adblock
||domain.com^$popup
```

**Restrictions:**
- MV3 may not convert to declarative rules, falls back to TSUrlFilter engine
- iOS/Safari blocks the page directly
- Not supported by Content Blocker

---

## `$strict-first-party` — Strict First-Party (`$strict1p`)

Similar to `$~third-party`, but treats the request as first-party only if referrer and origin have **exactly the same hostname**. Requests without a referrer are also treated as first-party.

**Example:**
```adblock
domain.com$strict-first-party
```
Request from `sub.domain.com` to `domain.com/icon.ico` will **not** match (treated as third-party).

**Compatibility:** CoreLibs v1.16+

---

## `$strict-third-party` — Strict Third-Party (`$strict3p`)

Similar to `$third-party`, but requests from a domain to its subdomains (or vice versa) are also treated as third-party.

**Example:**
```adblock
||domain.com^$strict-third-party
```
Loading `domain.com/banner.jpg` from `sub.domain.com` will also match.

**Compatibility:** CoreLibs v1.16+

---

## `$third-party` — Third-Party Restriction (`$3p`)

Limits the rule to cross-domain requests. `$~third-party` restricts to same-domain requests.

**Third-party determination conditions:**
1. Referrer is not a subdomain of the target domain (or vice versa)
2. `Sec-Fetch-Site` header is set to `cross-site`

**Examples:**
```adblock
||domain.com^$third-party
```
Applies to all domains except `domain.com`. Does not match when there is no referrer.

```adblock
||domain.com$~third-party
```
Applies only to `domain.com` and its subdomains. Requests without a referrer also match.

---

## `$to` — Restrict Target Domain

Limits the rule to requests made **to** the specified domains and their subdomains.

**Examples:**
```adblock
/ads$to=evil.com|evil.org
/ads$to=~not.evil.com|evil.com
/ads$to=~good.com|~good.org
```

**Restrictions:** Cannot be used with `$denyallow`.

**Compatibility:** CoreLibs v1.12+, TSUrlFilter v2.1.3+
