# 元素隐藏过滤器

> 元素隐藏、CSS 注入、过程式选择器、动作操作符、实体匹配和主机名正则。

## 基础元素隐藏过滤器

### 语法

```
[主机名]##[CSS 选择器]           （隐藏元素）
[主机名]#@#[CSS 选择器]          （例外 — 取消隐藏）
```

- `##` 操作符创建隐藏匹配元素的过滤器
- `#@#` 操作符创建阻止隐藏的例外
- 元素隐藏过滤器**没有隐私价值** — 它们仅在视觉上隐藏元素

### 示例

```
example.com##.ad-banner
```
隐藏 example.com 上所有 class 为 `ad-banner` 的元素。

```
example.com,example.org##.ad-banner
```
应用于多个域名。

```
example.com#@#.ad-banner
```
例外：阻止在 example.com 上隐藏 `.ad-banner`。

### 通用 vs 特定

- **通用：** `##.ad-banner`（无主机名前缀）— 到处生效，仅在 DOM 探测器找到匹配时注入
- **特定：** `example.com##.ad-banner` — 在 example.com 上始终注入

## 实体匹配

所有扩展过滤器（元素隐藏、网络 `$domain=`）可使用实体表示法。实体将公共后缀替换为 `*`。

```
google.*###tads.c
```
匹配 `google.com`、`google.com.br`、`google.ca`、`google.co.uk` 等。

```
facebook.*##.ad-unit
```
匹配 `facebook.com`、`facebook.net`。

**重要：** `google.evil.biz` **不**匹配 `google.*` — 仅匹配基础域名部分。

## 主机名正则（1.46.1b15+）

在扩展过滤器以及 `$domain=`、`$to=`、`$from=` 选项中使用正则作为主机名。

```
/img[a-z]{3,5}\.buzz/##+js(nowoif)
```
匹配如 `imgabcd.buzz` 这样的主机。

```
/^nitter\.[^.]+\.[^.]+$/##.timeline-item:has-text(owned)
```
匹配 `nitter.abc.com` 但不匹配 `nitter.com` 或 `nitter.abc.xyz.com`。

```
/^example\.org$/##h1
```
仅匹配 `example.org`，不含任何子域名。

```
org,~/^example\.org$/##h1
```
匹配 `org` 及其所有子域名，排除 `example.org`（但 example.org 的子域名仍匹配）。

**性能提示：** 谨慎使用。uBO 必须迭代所有正则值，不像普通主机名是 O(1) 查找。

## 特定-通用（1.25.0+）

在通用元素隐藏过滤器前加 `*` 使其在所有页面上无条件注入：

```
*##.selector
```
在所有地方无条件注入（仍受 `$generichide` 例外禁用）。

```
##.selector
```
标准通用：仅在 DOM 探测器找到匹配元素时注入。

特定-通用过滤器**不会**被过滤列表面板中的"忽略通用元素隐藏过滤器"选项丢弃。

## 过程式元素隐藏过滤器

过程式过滤器使用 JavaScript 查找 DOM 元素。它们用强大的匹配能力扩展了 CSS 选择器。

**关键规则：**
1. 过程式过滤器**必须是特定的**（需要主机名前缀）
2. 仅在普通 CSS 选择器无法完成时使用
3. 不能在一个过滤器中连接多个过程式选择器
4. 使用 `#?#` 前缀替代 `##` 以阻止 uBO 尝试转换为原生 CSS

### `:has(arg)`

如果 `arg` 匹配一个或多个后代元素，则选择主题元素。

```
example.com##main [role="row"]:has(div:last-of-type span:has-text(/^Promoted by/))
```

当浏览器原生支持 `:has()`（Chromium 105+）时，uBO 自动使用原生版本，否则回退到过程式。

### `:has-text(needle)`

如果文本 `needle` 在元素内部或其子元素中被找到，则选择该元素。支持字面文本和正则。

```
example.com##body > div span:has-text(/^Promoted by/)        （开头匹配）
example.com##body > div span:has-text(/^Promoted by/i)       （不区分大小写）
example.com##body > div span:has-text(Promoted by)           （包含）
```

### `:matches-attr(arg)`

按属性值选择元素，适用于随机化属性。

```
k-rauta.fi##button:matches-attr(class="/[\w]{7}/")
```

### `:matches-css(arg)` / `:matches-css-before(arg)` / `:matches-css-after(arg)`

按计算出的 CSS 样式选择元素。值可以是字面文本或正则。

```
example.com##div:matches-css(position: absolute)
example.com##div:matches-css(background-image: /^url\("data:image/png;base64,/)
```

### `:matches-media(arg)`

按媒体查询过滤。

```
example.com###target:matches-media((min-width: 800px))
```

### `:matches-path(arg)`

按当前文档的 URL 路径缩小过滤范围。最好作为第一个操作符使用。

```
example.com##:matches-path(/shop) p
```
仅在 `/shop` 页面上隐藏 `<p>`。

```
example.com##:matches-path(/^/$/) p
```
仅在主页上隐藏 `<p>`。

### `:matches-prop(arg)`

按 JavaScript 属性选择元素，可选匹配值。

```
example.org##div:matches-prop(imanad)
example.org##img:matches-prop(naturalWidth=160)
```

### `:min-text-length(n)`

选择文本长度 >= n 字符的元素。

```
quoka.de##^script:min-text-length(35000)
```

### `:not(arg)`

选择 arg 匹配零个元素的元素。当 arg 是有效 CSS 时，使用原生 `:not()`。

### `:others()`

选择当前选中集合**之外**的所有元素。适用于"阅读模式"风格的过滤器。

```
twitter.com##:matches-path(/^/home/) [data-testid="primaryColumn"]:others()
```

### `:upward(arg)`

查找祖先元素。arg 是正整数（距离）或 CSS 选择器。

```
example.com##.ad-link:upward(3)          （向上 3 层）
example.com##.ad-link:upward(.container) （第一个匹配 .container 的祖先）
```

### `:nth-ancestor(n)`（已弃用）

`:upward(n)` 的前身，功能相同但仅接受数字参数。已弃用但仍可能在现有过滤列表中遇到。建议使用 `:upward()` 替代。

```
example.com##.detLink:has-text(VPN):xpath(../../..)
```
等效于 `example.com##.detLink:has-text(VPN):upward(3)`

### `:watch-attr(arg)`

当匹配元素上的指定属性变化时强制重新评估。

```
example.com##.j-mini-player[class]:watch-attr(class):remove-attr(class)
```

### `:xpath(arg)`

评估 XPath 表达式。与其他操作符不同，可以**创建**新的元素集合。

```
facebook.com##:xpath(//div[@id="stream_pagelet"]//div[starts-with(@id,"hyperfeed_story_id_")])
```

## 动作操作符

动作操作符必须是链中的**最后一个**。不能继续链接。

### `:remove()`

从 DOM 中完全移除元素（不仅仅是隐藏）。

```
example.com##.ad-banner:remove()
```

### `:style(arg)`

对元素应用 CSS 样式。必须指定主机名。

```
example.com##h1:style(background-color: blue !important)
example.com##.overlay:style(display: none !important)
```

uBO 可以透明转换并使用 AdGuard 的 [CSS 注入规则](https://kb.adguard.com/en/general/how-to-create-your-own-ad-filters#cosmetic-css-rules-syntax)（`#$#` 语法）。这意味着你可以在 uBO 中使用 AdGuard 的语法。

**禁止在样式值中：** `url(...)`、`image-set(...)`、注释（`/* */`）、反斜杠、`//`。

### `:remove-attr(arg)`、`:remove-class(arg)`（1.45.3b13+）

从元素中移除属性。

```
example.com##[onclick]:remove-attr(onclick)
example.com##selector:remove-attr(/^on[a-z]+/)
```

### `:remove-class(arg)`

从元素中移除类名。

```
example.com##html[cookie-banner-open]:remove-class(cookie-banner-open)
```

## 引用规则

当参数导致解析问题时使用引号。`"` 或 `'` 均可。内部相同引号需转义：`'it\'s'` 或 `"he said \"hi\""`。
