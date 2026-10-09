# Non-Basic Rule Modifiers

> Add extra constraints to cosmetic rules, HTML filtering rules, JavaScript rules, and scriptlet rules.

## Syntax

```
rule = "[$" modifiers "]" [rule text]
```

**Example:** `[$domain=example.com,app=test_app]##selector`

**Escaping:** `[`, `]`, `,`, `\` in modifier values must be escaped with `\`.

## Compatibility Overview

| Modifier | CoreLibs | Chromium | MV3 | Firefox | iOS | Safari | Content Blocker |
|---|---|---|---|---|---|---|---|
| `$app` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$domain` | ✅ | ✅ | ✅*[1]* | ✅ | ✅ | ✅ | ❌ |
| `$path` | ✅ | ✅*[2]* | ❌ | ✅*[2]* | ✅ | ✅ | ❌ |
| `$url` | ✅ | ✅*[3]* | ✅*[3]* | ✅*[3]* | ❌ | ❌ | ❌ |

---

## `$app` — Restrict to Application

Behavior and syntax are identical to the [basic rule `$app` modifier](#).

```adblock
[$app=org.example.app]example.com##.textad
[$app=~org.example.app1|~org.example.app2]example.com##.textad
[$app=com.apple.Safari]example.org#%#//scriptlet('prevent-setInterval', 'check', '!300')
[$app=org.example.app]#@#.textad
```

CoreLibs apps only.

---

## `$domain` — Restrict to Source Domain

Behavior and syntax are identical to the [basic rule `$domain` modifier](#).

```adblock
[$domain=example.com]##.textad
[$domain=example.com|example.org]###adblock
[$domain=~example.com]##.textad
```

**Two ways to specify domain restrictions:**
1. Classic way: `example.com##.textad`
2. Modifier way: `[$domain=example.com]##.textad`

**Cannot mix** both styles — e.g. `[$domain=example.org]example.com##.textad` will be ignored.

Not supported by Content Blocker.

---

## `$path` — Restrict URL Path

Limits the rule to specific URL paths/pages.

**Syntax:**
```
$path ["=" pattern]
```

- `pattern` — path mask, same syntax as basic rule patterns (special characters supported, but `||` is meaningless)
- Without pattern, only matches the website's main page
- Matches query string
- Supports regular expressions

**Examples:**
```adblock
[$path=page.html]##.textad                    -- Matches /page.html, /sub/page.html, /another_page.html
[$path=/page.html]##.textad                   -- Matches /page.html, /sub/page.html, not /another_page.html
[$path=|/page.html]##.textad                  -- Only matches /page.html (no sub-paths)
[$path=/page.html|]##.textad                  -- Matches /page.html, /sub/page.html (no query string)
[$path=/page*.html]example.com##.textad       -- Wildcard match
[$path]example.com##.textad                   -- Main page only
[$domain=example.com,path=/page.html]##.textad -- Combined
[$path=/\\/(sub1|sub2)\\/page\\.html/]##.textad -- Regex match
```

**Restrictions:** In Browser Extension, `$path` must be placed last when combined with other non-basic modifiers. Not supported by Content Blocker.

---

### Path-in-Domain Syntax ⭐ New Feature

In cosmetic rules, you can specify the path directly in the domain part instead of using the `$path` modifier.

**Syntax:**
```
rule = [targets] "##" selector
targets = [target0, target1[, ...]]
target = domain [path]
```

**Examples:**
```adblock
example.org/checkout##.promo-banner
news.site.com/article##.sidebar-ad
domain1.com,example.org/path##.banner
/example\.org\/article\d+/##.ad
```

Works with all cosmetic rule types (`##`, `#@#`, `#$#`, `$$`, `$@$`, `#%#`, `#@%#`).

**Compatibility:** CoreLibs v1.20, Browser Extension v5.4+.

---

## `$url` — Restrict Full URL

Limits the rule to URLs matching the specified mask.

**Syntax:**
```
$url = pattern
```

`pattern` follows the same rules as basic rule patterns, supporting special characters and regular expressions.

**Examples:**
```adblock
[$url=||example.com/content/*]##div.textad
[$url=||example.org^]###adblock
[$url=/[a-z]+\.example\.com^/]##.textad
```

**Restrictions:** In Browser Extension, not compatible with domain-specific rules and other non-basic modifiers (`$domain`, `$path`).

**Compatibility:** CoreLibs v1.11+, TSUrlFilter v3.0.0+.
