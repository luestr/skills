---
name: write-ublock-origin-filters
description: "完整的 uBlock Origin (uBO) 静态过滤语法参考。编写 uBlock Origin 自定义过滤规则时使用此技能，涵盖广告拦截、隐私保护或内容过滤。包含基础网络过滤模式（||、*、^、|）、所有网络过滤选项（$domain、$third-party、$important、$redirect、$removeparam、$csp、$replace、$header、$method、$denyallow、$badfilter、$all 等）、内容类型选项（$script、$image、$stylesheet、$font、$media、$xhr、$popup、$document、$frame 等）、元素隐藏规则（## 选择器、实体匹配、主机名正则）、过程式元素隐藏过滤器（:has、:has-text、:matches-css、:upward、:xpath、:matches-path、:watch-attr 等）、动作操作符（:remove、:style、:remove-attr、:remove-class）、HTML 过滤器（##^）、响应头过滤（##^responseheader）、脚本注入（##+js()）以及预处理指令（!#include、!#if）。当用户提到 uBlock Origin 过滤规则、uBO 语法、广告拦截规则、元素隐藏规则、过程式选择器、脚本注入或希望编写/调试任何 uBO 兼容过滤列表时触发。即使用户只是在编写或调试 uBlock Origin 过滤规则、创建自定义过滤列表或从 AdBlock Plus/AdGuard 迁移过滤规则到 uBO，也应使用此技能。"
---

# uBlock Origin 静态过滤语法参考

> 来源：https://github.com/gorhill/uBlock/wiki/Static-filter-syntax

本技能是 uBlock Origin (uBO) 静态过滤语法的完整参考索引。**不要一次性加载所有参考文件** — 根据用户的问题只加载相关文件以节省 token。

## 快速路由：应加载哪个文件

| 用户需求 | 加载文件 |
|---|---|
| 基础 URL 模式匹配（`*`、`\|\|`、`^`、`\|`）、HOSTS 文件解析、`_`（noop）、`*`（所有 URL） | `references/01-network-filter-basics.md` |
| 内容类型选项：`$script`、`$image`、`$stylesheet`/`$css`、`$font`、`$media`、`$subdocument`/`$frame`、`$object`、`$other`、`$ping`、`$websocket`、`$xhr`、`$popup`、`$document`、`$top` | `references/02-content-type-options.md` |
| 行为修饰符：`$third-party`/`$3p`、`$first-party`/`$1p`、`$domain`/`$from`、`$to`、`$match-case`、`$important`、`$badfilter`、`$denyallow`、`$method`、`$header`、`$strict1p`、`$strict3p`、`$all`、`$elemhide`/`$ehide`、`$generichide`/`$ghide`、`$specifichide`/`$shide`、`$popunder`、`$inline-script`、`$inline-font`、`$cname`、`$ipaddress`、`$permissions` | `references/03-behavior-modifiers.md` |
| 修改器过滤器（响应修改）：`$csp`、`$redirect`、`$redirect-rule`、`$removeparam`、`$replace`、`$uritransform`、`$urlskip`、`$empty`、`$mp4` | `references/04-modifier-filters.md` |
| 元素隐藏过滤器（`##`/`#@#`）、实体匹配、主机名正则、特定泛型、过程式过滤器（`:has()`、`:has-text()`、`:matches-css()`、`:upward()`、`:xpath()`、`:matches-path()`、`:watch-attr()` 等）、动作操作符（`:remove()`、`:style()`、`:remove-attr()`、`:remove-class()`） | `references/05-cosmetic-filters.md` |
| HTML 过滤器（`##^`）、响应头过滤（`##^responseheader()`） | `references/06-html-response-header-filters.md` |
| 脚本注入（`##+js()`）、可用脚本、重定向资源、资源库 | `references/07-scriptlet-injection.md` |
| 预处理指令（`!#include`、`!#if`/`!#else`/`!#endif`）、不支持的功能、兼容性说明 | `references/08-preparsing-directives.md` |

## 规则类型速查

### 1. 网络过滤器 — 拦截/允许 URL 请求

```
模式 [$选项]
@@模式 [$选项]    （例外/白名单）
```

- `||example.com^` — 拦截 example.com 及其所有子域名的请求
- `|https://example.com/ad.js|` — 精确 URL 匹配
- `@@||example.com^` — 白名单允许 example.com
- `||example.com^$important` — 强制规则（覆盖例外规则）

### 2. 元素隐藏过滤器 — 隐藏/修改页面元素

- `example.com##.ad-banner` — 隐藏元素
- `example.com#@#.ad-banner` — 例外（取消隐藏）
- `example.com##h1:style(color: red !important)` — 注入 CSS 样式
- `example.com##.ad:remove()` — 从 DOM 中移除元素

### 3. HTML 过滤器 — 在浏览器解析前移除 HTML（仅限 Firefox）

- `example.com##^script:has-text(adScript)` — 从响应中移除 script 标签

### 4. 响应头过滤 — 移除响应头

- `example.com##^responseheader(refresh)` — 移除 refresh 头

### 5. 脚本注入 — 注入 JavaScript

- `example.com##+js(set-constant, adBlockDetected, false)` — 注入脚本

## 核心概念

- **注释**：以 `!` 开头的行是注释
- **例外规则**：以 `@@` 开头的规则允许请求
- **选项/修饰符**：`$` 后的参数，用于限制/改变规则行为
- **域名限制**：网络过滤器中的 `$domain=`，元素隐藏/扩展过滤器中的主机名前缀
- **第三方**：`$third-party`（`$3p`）限制为跨站请求
- **HOSTS 文件格式**：uBO 将裸主机名如 `example.com` 解释为 `||example.com^`
- **受信来源**：仅 uBO 自带过滤列表和用户的"我的过滤"（如已启用）可用于 `$replace`、脚本注入等
- **实体匹配**：`google.*` 匹配所有 Google 顶级域名（google.com、google.co.uk 等）
- **主机名正则**：扩展过滤器中使用 `/regex/` 作为主机名（为性能考虑应谨慎使用）

## 重要：uBO 与 ABP/AdGuard 的差异

| 功能 | uBO | ABP/AdGuard |
|---|---|---|
| `document` 用于整页例外 | ❌ 不支持 | ✅ 支持 |
| `genericblock` | ❌ 不支持 | ✅ 支持 |
| `$webrtc` 选项 | ❌ 使用 `##+js(nowebrtc)` | ✅ 支持 |
| `$replace` 过滤 | 仅受信来源 | 更宽松 |
| HOSTS 文件解释 | `example.com` → `\|\|example.com^` | `example.com` 匹配 URL 中任何位置 |
| `$badfilter` | ✅ 支持 | 部分支持 |
| `$denyallow` | ✅ 支持 | ❌ 不支持 |
| HTML 过滤（`##^`） | 仅 Firefox | CoreLibs 应用 |
| 脚本命名 | uBO 原生 + AG 兼容 | AG 原生 |
