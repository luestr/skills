---
name: WriteAdGuardFilters
description: "编写 AdGuard 自定义过滤规则时使用此技能。涵盖基本规则语法、所有修饰符（$domain/$third-party/$important/$redirect/$replace/$removeparam/$cookie/$csp 等）、外观规则（元素隐藏/CSS/Extended CSS 选择器）、HTML 过滤、JavaScript/脚本片段规则、非基本规则修饰符、预处理器指令和调试技巧。当用户提及 AdGuard 过滤规则、广告拦截规则语法、过滤器列表编写、ABP 语法兼容、元素隐藏规则、Extended CSS 选择器（:has/:contains/:matches-css 等）时触发。即使用户只是在编写或调试任何类型的广告过滤规则，也应使用此技能。"
---

# AdGuard 过滤规则语法参考

> 来源: https://adguard.com/kb/general/ad-filtering/create-own-filters/

本技能是 AdGuard 过滤规则语法的完整参考索引。**不要一次性加载所有参考文件**——根据用户问题的类型，只加载相关的参考文件以节省 token。

## 快速判断：加载哪个参考文件

根据用户的意图，按以下优先级加载对应文件：

| 用户需求 | 加载文件 |
|---|---|
| 基本规则语法、特殊字符 (`*`, `\|\|`, `^`, `\|`)、正则表达式、TLD 通配符 | `references/01-basic-rules-syntax.md` |
| `$domain`、`$third-party`、`$important`、`$match-case`、`$app`、`$denyallow`、`$header`、`$method`、`$popup`、`$strict-first-party`、`$strict-third-party`、`$to` | `references/02-basic-modifiers.md` |
| `$document`、`$image`、`$script`、`$stylesheet`、`$font`、`$media`、`$subdocument`、`$websocket`、`$xmlhttprequest`、`$ping`、`$object`、`$other` | `references/03-content-type-modifiers.md` |
| 例外规则 (`@@`) 的修饰符：`$elemhide`、`$content`、`$urlblock`、`$jsinject`、`$stealth`、`$extension`；泛型规则：`$genericblock`、`$generichide`、`$specifichide` | `references/04-exception-modifiers.md` |
| `$all`、`$badfilter`、`$cookie`、`$csp`、`$hls`、`$inline-script`、`$inline-font`、`$jsonprune`、`$xmlprune`、`$network`、`$permissions`、`$redirect`、`$redirect-rule`、`$referrerpolicy`、`$removeheader`、`$removeparam`、`$replace`、`$urltransform`、`$reason`、`noop`、`$empty`(废弃)、`$mp4`(废弃) | `references/05-advanced-modifiers.md` |
| 规则优先级计算、优先级冲突解决 | `references/06-rule-priorities.md` |
| 外观规则（元素隐藏 `##`、CSS 规则 `#$#`）、Extended CSS 选择器（`:has()`、`:contains()`、`:matches-css()`、`:matches-attr()`、`:matches-property()`、`:xpath()`、`:nth-ancestor()`、`:upward()`、`:remove()`、`:is()`、`:not()`） | `references/07-cosmetic-rules.md` |
| HTML 过滤规则 (`$$`)、特殊属性（`tag-content`、`wildcard`、`max-length`、`min-length`）、`:contains()` 伪类 | `references/08-html-filtering.md` |
| JavaScript 规则 (`#%#`)、脚本片段规则 (`//scriptlet()`)、受信脚本片段 | `references/09-javascript-scriptlet.md` |
| 非基本规则的修饰符：`[$domain=...]`、`[$app=...]`、`[$path=...]`、`[$url=...]` 语法 | `references/10-non-basic-modifiers.md` |
| 预处理器指令 (`!#include`、`!#if`/`!#else`/`!#endif`、`!#safari_cb_affinity`)、提示 (`NOT_OPTIMIZED`、`PLATFORM`/`NOT_PLATFORM`、`NOT_VALIDATE`)、调试方法（过滤日志、选择器调试、脚本片段调试）、兼容性图例 | `references/11-preprocessor-debugging.md` |
| **Safari/iOS 限制**、SafariConverterLib 兼容性细节、Content Blocker 限制、受信过滤器定义、已移除/废弃修饰符列表 | `references/12-restrictions-safari.md` |

## 规则类型速查

### 1. 基本规则 (Basic Rules) — 拦截/放行 URL 请求

```
规则 = ["@@"] 模式 ["$" 修饰符列表]
```

- `||example.com^` — 拦截 example.com 及子域名的所有请求
- `|https://example.com|` — 精确匹配 URL
- `@@||example.com^` — 放行 example.com
- `||example.com^$important` — 强制规则（覆盖例外）

### 2. 外观规则 (Cosmetic Rules) — 隐藏/修改页面元素

- `example.com##.ad-banner` — 隐藏元素
- `example.com#$#body { background: #fff; }` — 注入 CSS
- `example.com#?#div:has(> .ad)` — Extended CSS 选择器
- `example.com#@#.ad-banner` — 例外（取消隐藏）

### 3. HTML 过滤规则 — 在页面加载前修改 HTML

- `example.com$$script[data-src="banner"]` — 移除 HTML 元素
- `example.com$@$script[data-src="banner"]` — 例外

### 4. JavaScript 规则 — 注入 JS 代码

- `example.com#%#window.__gaq = undefined;` — 执行 JS

### 5. 脚本片段规则 — 声明式 JS 函数

- `example.com#%#//scriptlet('abort-on-property-read', 'alert')` — 使用脚本片段

## 关键概念

- **注释**: 以 `!` 开头的行是注释
- **例外规则**: 以 `@@` 开头放行请求
- **修饰符**: `$` 后跟的参数，限制/改变规则行为
- **域限制**: `$domain=` 或在外观规则中域名前缀
- **第三方**: `$third-party` (`$3p`) 限制为跨站请求
- **规则最短 4 字符**，否则被视为无效
- **URL 截断**: AdGuard 将 URL 截断到 4096 字符以加速匹配
- **受信过滤器**: `$replace`、`$hls`、JavaScript 规则、脚本片段规则等只能在受信过滤器中使用

## 兼容性速查

| 缩写 | 含义 |
|---|---|
| CoreLibs apps | AdGuard for Windows/Mac/Android/Linux |
| AdGuard for Chromium | Chrome/Edge/Opera 扩展 |
| AdGuard for Chrome MV3 | Chrome MV3 扩展 |
| AdGuard for Firefox | Firefox 扩展 |
| AdGuard for iOS | iOS Safari |
| AdGuard for Safari | 桌面 Safari |
| AdGuard Content Blocker | Android 的三星/Yandex 浏览器 |

| 符号 | 含义 |
|---|---|
| ✅ | 完全支持 |
| ✅ * | 有限制支持 |
| ❌ | 不支持 |
| 👎 | 已废弃 |
| 🚫 | 已移除 |
