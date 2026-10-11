# 非基本规则修饰符

> 为外观规则、HTML 过滤规则、JavaScript 规则和脚本片段规则添加额外限制。

## 语法

```
规则 = "[$" 修饰符列表 "]" [规则文本]
```

**示例：** `[$domain=example.com,app=test_app]##selector`

**转义：** 修饰符值中的 `[`、`]`、`,`、`\` 需用 `\` 转义。

## 兼容性总览

| 修饰符 | CoreLibs | Chromium | MV3 | Firefox | iOS | Safari | Content Blocker |
|---|---|---|---|---|---|---|---|
| `$app` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$domain` | ✅ | ✅ | ✅*[1]* | ✅ | ✅ | ✅ | ❌ |
| `$path` | ✅ | ✅*[2]* | ❌ | ✅*[2]* | ✅ | ✅ | ❌ |
| `$url` | ✅ | ✅*[3]* | ✅*[3]* | ✅*[3]* | ❌ | ❌ | ❌ |

---

## `$app` — 限定应用程序

行为和语法与[基本规则的 `$app` 修饰符](#)完全相同。

```adblock
[$app=org.example.app]example.com##.textad
[$app=~org.example.app1|~org.example.app2]example.com##.textad
[$app=com.apple.Safari]example.org#%#//scriptlet('prevent-setInterval', 'check', '!300')
[$app=org.example.app]#@#.textad
```

仅 CoreLibs apps。

---

## `$domain` — 限定来源域名

行为和语法与[基本规则的 `$domain` 修饰符](#)完全相同。

```adblock
[$domain=example.com]##.textad
[$domain=example.com|example.org]###adblock
[$domain=~example.com]##.textad
```

**两种指定域名的方式：**
1. 经典方式：`example.com##.textad`
2. 修饰符方式：`[$domain=example.com]##.textad`

**不能混合使用**，如 `[$domain=example.org]example.com##.textad` 会被忽略。

Content Blocker 不支持。

---

## `$path` — 限定 URL 路径

限制规则仅在特定 URL 路径/页面上生效。

**语法：**
```
$path ["=" pattern]
```

- `pattern` — 路径掩码，语法与基本规则模式相同（支持特殊字符，但 `||` 无意义）
- 不设 pattern 时，仅匹配网站主页
- 匹配查询字符串
- 支持正则表达式

**示例：**
```adblock
[$path=page.html]##.textad                    -- 匹配 /page.html、/sub/page.html、/another_page.html
[$path=/page.html]##.textad                   -- 匹配 /page.html、/sub/page.html，不匹配 /another_page.html
[$path=|/page.html]##.textad                  -- 仅匹配 /page.html（不含子路径）
[$path=/page.html|]##.textad                  -- 匹配 /page.html、/sub/page.html（不含查询字符串）
[$path=/page*.html]example.com##.textad       -- 通配符匹配
[$path]example.com##.textad                   -- 仅主页
[$domain=example.com,path=/page.html]##.textad -- 组合使用
[$path=/\\/(sub1|sub2)\\/page\\.html/]##.textad -- 正则匹配
```

**限制：** Browser Extension 中，`$path` 与其他非基本修饰符组合时需放在最后。Content Blocker 不支持。

---

### Path-in-domain 语法 ⭐ 新功能

在外观规则中，可直接在域名部分指定路径，替代 `$path` 修饰符。

**语法：**
```
规则 = [目标] "##" 选择器
目标 = [目标0, 目标1[, ...]]
目标 = 域名 [路径]
```

**示例：**
```adblock
example.org/checkout##.promo-banner
news.site.com/article##.sidebar-ad
domain1.com,example.org/path##.banner
/example\.org\/article\d+/##.ad
```

适用于所有外观规则类型（`##`、`#@#`、`#$#`、`$$`、`$@$`、`#%#`、`#@%#`）。

**兼容性：** CoreLibs v1.20、Browser Extension v5.4+。

---

## `$url` — 限定完整 URL

限制规则仅适用于匹配指定掩码的 URL。

**语法：**
```
$url = pattern
```

`pattern` 与基本规则模式相同，支持特殊字符和正则表达式。

**示例：**
```adblock
[$url=||example.com/content/*]##div.textad
[$url=||example.org^]###adblock
[$url=/[a-z]+\.example\.com^/]##.textad
```

**限制：** Browser Extension 中不与域名特定规则和其他非基本修饰符（`$domain`、`$path`）兼容。

**兼容性：** CoreLibs v1.11+、TSUrlFilter v3.0.0+。
