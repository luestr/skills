# 基本修饰符

> 最常用、最简单的修饰符，主要用于限制规则的适用范围。

## 兼容性总览

| 修饰符 | CoreLibs | Chromium | MV3 | Firefox | iOS | Safari | Content Blocker |
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

## `$app` — 限定应用程序

将规则限定到特定应用（或应用列表）。

**语法：**
```
$app = ["~"] 入口0 ["|" ["~"] 入口1 [...]]
入口 = ( 普通应用 / 通配符应用 / 正则表达式 )
```

- `regular_app` — 普通应用名，如 `org.example.app`
- `wildcard_app` — 以 `*` 结尾，如 `org.example.*`
- `regexp` — 以 `/` 包围的正则表达式

**示例：**
```adblock
||baddomain.com^$app=org.example.app
||baddomain.com^$app=org.example.app1|org.example.app2
||baddomain.com^$app=~org.example.app
||baddomain.com^$app=org.example.*
||baddomain.com^$app=/org\.example\.[a-z0-9_]+/
```

**限制：** 不支持混合否定和非否定表达式；通配符不能在字符串中间使用。

**兼容性：** 仅 AdGuard for Windows/Mac/Android。正则表达式和混合类型需 CoreLibs v1.19+。

---

## `$denyallow` — 排除目标域名

避免为特定域名创建额外排除规则。仅匹配目标域名，不匹配 referrer 域名。

**等价关系：**
```adblock
*$script,domain=a.com|b.com,denyallow=x.com|y.com
```
等价于：
```adblock
*$script,domain=a.com|b.com
@@||x.com$script,domain=a.com|b.com
@@||y.com$script,domain=a.com|b.com
```

**限制：**
- 规则模式不能以 `||` 开头
- 不能与 `$to` 同时使用
- 不支持否定域名或 TLD 通配符或正则表达式

**兼容性：** 不支持 AdGuard for iOS/Safari/Content Blocker。

---

## `$domain` — 限定来源域名

限制规则仅适用于从指定域名及其子域名发出的请求（基于 Referer 头）。

**语法：**
```
$domain = ["~"] 入口0 ["|" ["~"] 入口1 [...]]
入口 = ( 普通域名 / 任意TLD域名 / 正则表达式 )
```

- `regular_domain` — 普通域名，如 `domain.com`（包含子域名）
- `any_tld_domain` — 以 `.*` 结尾，如 `example.*`（匹配所有公共后缀）
- `regexp` — 正则表达式，`/`、`$`、`,`、`|` 需用 `\` 转义

**别名：** `$from`（CoreLibs v1.12+）

**示例：**
```adblock
||baddomain.com^$domain=example.org
||baddomain.com^$domain=example.org|example.com
||baddomain.com^$domain=~example.org
||baddomain.com^$domain=example.org|~foo.example.org
||baddomain.com^$domain=/(^\|.+\.)example\.(com|org)$/
```

**特殊行为：** 当规则包含 `$cookie`、`$csp`、`$permissions`、`$removeparam` 时，`$domain` 也可匹配目标域名（不仅是 referrer）。

**限制：**
- MV3 中不支持正则表达式和 TLD 通配符
- Safari/iOS 有额外限制
- 正则表达式需 CoreLibs v1.11+

---

## `$header` — 匹配 HTTP 响应头

匹配具有特定 HTTP 响应头的请求。

**语法：**
```
$header = h_name [":" h_value]
h_value = 字符串 / 正则表达式
```

**示例：**
```adblock
||example.com^$header=set-cookie:foo
||example.com^$header=set-cookie
@@||example.com^$header=set-cookie:/foo\, bar$/
```

**限制：** 仅在接收到响应头后匹配；Browser Extension 中仅与特定修饰符兼容。

**兼容性：** CoreLibs v1.11+、TSUrlFilter v3.0.0+、MV3 v5.3+。

---

## `$important` — 提升优先级

将规则优先级提升到高于不带此修饰符的规则（包括基本例外规则）。

**示例：**
```adblock
||example.org^$important
@@||example.org^
```
拦截规则生效，因为 `$important` 优先级更高。

```adblock
||example.org^$important
@@||example.org^$important
```
两者都有 `$important`，例外规则生效。

---

## `$match-case` — 区分大小写

默认规则不区分大小写。添加此修饰符后仅匹配大小写完全一致的地址。

**示例：**
```adblock
*/BannerAd.gif$match-case
```
拦截 `https://example.com/BannerAd.gif`，不拦截 `https://example.com/bannerad.gif`

---

## `$method` — 限定 HTTP 方法

限制规则仅适用于指定 HTTP 方法的请求。方法必须全部小写，但匹配时不区分大小写。支持否定。

**示例：**
```adblock
||evil.com^$method=get|head
||evil.com^$method=~post|~put
@@||evil.com$method=get
```

**限制：** 不支持混合否定和非否定值。iOS/Mac 中不支持否定。

**兼容性：** CoreLibs v1.12+、TSUrlFilter v2.1.1+。

---

## `$popup` — 关闭弹窗

AdGuard 将尝试关闭匹配地址打开的浏览器标签页。

**示例：**
```adblock
||domain.com^$popup
```

**限制：**
- MV3 中可能无法转为声明式规则，改用 TSUrlFilter 引擎
- iOS/Safari 中会直接阻止页面加载
- Content Blocker 不支持

---

## `$strict-first-party` — 严格第一方 (`$strict1p`)

类似 `$~third-party`，但仅在 referrer 和 origin 的**主机名完全相同时**才视为第一方。无 referrer 的请求也视为第一方。

**示例：**
```adblock
domain.com$strict-first-party
```
从 `sub.domain.com` 到 `domain.com/icon.ico` 的请求**不会**匹配（被视为第三方）。

**兼容性：** CoreLibs v1.16+

---

## `$strict-third-party` — 严格第三方 (`$strict3p`)

类似 `$third-party`，但从域名到其子域名（或反之）的请求也视为第三方。

**示例：**
```adblock
||domain.com^$strict-third-party
```
从 `sub.domain.com` 加载 `domain.com/banner.jpg` 也会匹配。

**兼容性：** CoreLibs v1.16+

---

## `$third-party` — 第三方限制 (`$3p`)

限制规则仅适用于跨域请求。`$~third-party` 限制为同域请求。

**第三方判定条件：**
1. referrer 不是目标域名的子域名（或反之）
2. `Sec-Fetch-Site` 头设置为 `cross-site`

**示例：**
```adblock
||domain.com^$third-party
```
适用于 `domain.com` 以外的所有域名。无 referrer 时不匹配。

```adblock
||domain.com$~third-party
```
仅适用于 `domain.com` 及其子域名。无 referrer 的请求也匹配。

---

## `$to` — 限定目标域名

限制规则仅适用于发送到指定域名及子域名的请求。

**示例：**
```adblock
/ads$to=evil.com|evil.org
/ads$to=~not.evil.com|evil.com
/ads$to=~good.com|~good.org
```

**限制：** 不能与 `$denyallow` 同时使用。

**兼容性：** CoreLibs v1.12+、TSUrlFilter v2.1.3+
