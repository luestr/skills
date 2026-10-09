# Rule Priorities

> When multiple rules match the same request, priority determines which rule takes effect. Priority is a positive integer; higher value = higher priority.

## Core Concepts

- Base priority = **1**
- Floating-point priorities are **rounded up** to the smallest integer
- When same-priority rules conflict, the engine implementation decides
- Priority concept is especially important in Manifest V3 (rules need to be converted to declarativeNetRequest)

**Compatibility:** Introduced in TSUrlFilter v2.1.0 / CoreLibs v1.13. iOS/Safari/Content Blocker rely on browser implementation and do not follow these rules.

## Priority Categories (Low to High)

### Category 1: Basic Modifiers (each adds +1)

- `$app` (negated apps with `~`)
- `$denyallow`
- `$domain` (negated domains with `~`)
- `$match-case`
- `$method` (negated methods with `~`)
- `$strict-first-party`
- `$strict-third-party`
- `$third-party`
- `$to`
- Restricted content types (with `~`)

**Note:** When negating domains/apps/methods/content-types, regardless of the number of negations, only **1** point is added (since the rule's scope is already infinitely broad).

### Category 2: Content-Types/Methods/Headers/$all/$popup/Specific Exceptions

Defined content-type modifiers (`$document`, `$font`, `$image`, `$media`, `$object`, `$other`, `$ping`, `$script`, `$stylesheet`, `$subdocument`, `$websocket`, `$xmlhttprequest`):

**Adds `(50 + 50/N)`**, where N is the number of modifiers.

```adblock
||example.com^$image,script   -- 50 + 50/2 = 75
```

Also includes:
- `$all` (implicitly adds all content types)
- `$popup` (implicitly adds `$document`)
- Specific exceptions (`$content`, `$elemhide`, `$extension`, `$genericblock`, `$generichide`, `$jsinject`, `$specifichide`, `$urlblock`, implicitly add `$document,subdocument`)
- `$method` allowed methods: **(50 + 50/N)**
- `$header`: **+50**

### Category 3: `$domain` / `$app` with Allowed Domains/Apps

**Adds `(100 + 100/N)`**, where N is the number of modifier values.

```adblock
||example.com^$domain=example.com|example.org|example.net  -- 100 + 100/3 ≈ 135
||example.com^$app=org.example.app1|org.example.app2       -- 100 + 100/2 = 150
||example.com^$domain=example.com,app=org.example.app1|org.example.app2
  -- $domain: 100+100/1 + $app: 100+100/2 = 350
```

TLD wildcards and regex are counted as regular entries.

### Category 4: Specific Exceptions

`$content`, `$elemhide`, `$extension`, `$genericblock`, `$generichide`, `$jsinject`, `$specifichide`, `$urlblock`: each **+10⁴**

`$document` is an alias for the above, **adds 10⁴×5 = 50000**

### Category 5: Allowlist Rules

`@@` marker **+10⁵**

### Category 6: `$redirect` Rules

`$redirect` and `$redirect-rule`: each **+10³**

### Category 7: `$important` Rules

`$important` **+10⁶**

### Modifiers Without Priority Weight

Other [advanced modifiers](#) that perform pre/post-processing do not add to rule priority.

**Exception:** `$replace` takes precedence over all blocking rules from categories 1-3 and exception rules from categories 3-5, **but** `$content` exception can override `$replace`.

## Calculation Examples

| Rule | Calculation | Result |
|---|---|---|
| `\|\|example.com^` | Base | **1** |
| `\|\|example.com^$match-case` | 1 + cat.1: 1 | **2** |
| `\|\|example.org^$removeparam=p` | 1 + 0 (no weight) | **1** |
| `\|\|example.org^$document,redirect=nooptext` | 1 + cat.3: (100+100/1) + cat.6: 1000 | **1201** |
| `@@\|\|example.org^$removeparam=p,document` | 1 + cat.5: 10000 + cat.2: (50+50/1) | **10101** |
| `@@\|\|example.com/ad/*$domain=example.org\|example.net,important` | 1 + 10000 + 1000000 + (100+100/2) | **1010152** |
| `@@\|\|example.org^$document` | 1 + cat.4: 10000×4 + cat.2: (50+50/2) | **40076** |
| `*$script,domain=a.com,denyallow=x.com\|y.com` | 1 + cat.2: (50+50/1) + cat.3: (100+100/1) + cat.1: 1 | **303** |
| `\|\|example.com^$all` | 1 + cat.2 popup: (50+50/12) | **55** |

## Priority Quick Reference

```
$important (10⁶) > @@ (10⁵) > specific exceptions (10⁴) > $redirect (10³) > $domain/$app (100+) > content types (50+) > basic modifiers (1) > no weight (0)
```
