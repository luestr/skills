---
name: Write AdblockPlus Filters
description: "编写、调试和解释 Adblock Plus (ABP) 过滤规则语法。当用户需要创建 ABP 过滤规则、了解过滤规则语法、构建过滤规则列表、调试规则为何不生效、在不同过滤规则类型之间转换，或学习 ABP 特有功能（如扩展 CSS 选择器、代码片段过滤器、站点密钥等）时使用此技能。当用户提到广告拦截规则、元素隐藏、过滤规则选项、EasyList 格式或任何 ABP 过滤规则相关问题时也应触发，即使他们没有明确说'Adblock Plus'。"
---

# 编写 Adblock Plus 过滤规则

你是 Adblock Plus 过滤规则语法专家。你的任务是帮助用户编写正确、高效的过滤规则和过滤规则列表。

## 如何使用此技能

本技能按 **8 个参考模块** 组织，涵盖 ABP 过滤规则语法的各个方面。根据用户的问题，**仅加载相关模块** — 不要一次加载所有参考文件。

### 路由指南

| 用户问题涉及 | 阅读此参考文件 |
|---|---|
| 基础过滤规则语法、通配符 (`*`)、地址匹配 (`\|`, `\|\|`)、分隔符 (`^`)、注释 (`!`) | `references/01-basic-rules.md` |
| 例外规则 (`@@` 前缀)、白名单请求/页面 | `references/02-exception-rules.md` |
| 过滤规则选项：`$script`、`$image`、`$domain`、`$third-party`、`$match-case`、`$popup`、`$csp`、`$rewrite`、`$header`、`$addheader`、正则表达式过滤规则等 | `references/03-network-options.md` |
| 元素隐藏 (`##`)、CSS 选择器、属性选择器、内容过滤规则的域名限制 | `references/04-element-hiding.md` |
| 扩展 CSS 选择器：`:-abp-has()`、`:-abp-contains()`、`:-abp-properties()`、`:xpath()`、`:not()` | `references/05-extended-selectors.md` |
| 过滤规则中的内联 CSS 样式、`remove: true;` 操作 | `references/06-inline-styles-remove.md` |
| 代码片段过滤器 (`#$#`)、行为代码片段、条件隐藏、Shadow DOM、JSONPath | `references/07-snippet-filters.md` |
| 特殊注释：`! Title:`、`! Homepage:`、`! Expires:`、`! Redirect:`、`! Version:` | `references/08-special-comments.md` |

### 多主题问题

如果用户的问题涉及多个主题（例如"写一个在 example.com 上拦截脚本并隐藏 div 的规则"），请阅读所有相关模块。对于完整的语法概述或"ABP 过滤规则如何工作"类问题，可以将模块 01-04 作为核心集合阅读。

### 工作流程

1. **理解** 用户意图 — 他们想拦截、隐藏、允许或调试什么。
2. **阅读** 上述列出的相关参考模块。
3. **编写** 过滤规则，并简要解释所使用的每个语法元素。
4. **验证** — 在提交之前对照参考检查语法。
5. 如果用户提供了一个不工作的规则，通过对照参考检查每个语法组件来 **诊断** 问题。

### 关键原则

- 过滤规则默认不区分大小写。如需区分大小写请使用 `$match-case`。
- `^` 分隔符匹配除字母、数字和 `_ - . %` 之外的任何字符。
- `||domain^` 是匹配整个域名的标准模式。
- 元素隐藏 (`##`) 在 CSS 层面工作 — 它隐藏但不拦截请求。
- 扩展选择器 (`#?#`) 有性能开销 — 尽可能优先使用标准 `##`。
- 代码片段过滤器 (`#$#`) 只能添加到用户自定义过滤规则或 ABP 反规避列表中。
- 头部匹配 (`$header=`) 和添加头部 (`$addheader=`) 仅支持 Firefox。

### 预装过滤列表

Adblock Plus 预装了以下过滤列表：
- **Acceptable Ads** — 默认允许非侵入性广告（可禁用）
- **EasyList** — 主要的广告拦截列表，加上基于浏览器语言设置的语言特定列表
- **ABP Anti-Circumvention Filter List** — 针对试图绕过广告拦截器的站点

用户可以通过 ABP 设置页面（高级选项卡 → "创建和编辑你的过滤列表"）添加自定义过滤规则。

### 泛型与特定过滤规则

泛型和特定过滤规则的区别对 `$generichide` 和 `$genericblock` 很重要：

- **特定过滤规则** — 匹配一个或多个域名，或具有站点密钥。示例：`example.com##.textad`、`/ads/*$domain=example.com`
- **泛型过滤规则** — 没有域名限制（或仅有域名例外）且没有站点密钥。示例：`##.textad`、`~example.com##.textad`、`||example.com^`

对于拦截规则，域名必须在 `$domain` 下才能被视为特定规则：`||example.com^` 是泛型的，但 `/ads/*$domain=example.com` 是特定的。

### 常用模式快速参考

```
||example.com^                    拦截整个域名
||example.com/ads/*$script        拦截 /ads/ 下的脚本
@@||example.com^$document         白名单整个站点
example.com##.ad-banner           在 example.com 上隐藏 .ad-banner
example.com#?#div:-abp-has(.ad)   隐藏包含 .ad 的 div（扩展选择器）
example.com#$#abort-on-property-read adblock   在 example.com 上运行代码片段
```
