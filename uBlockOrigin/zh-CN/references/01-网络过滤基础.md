# 网络过滤基础

> uBlock Origin 网络过滤器的 URL 模式匹配基础。

## 过滤语法概览

```
模式 [$选项]
@@模式 [$选项]    （例外/白名单）
```

- **模式** — URL 地址掩码；每个请求 URL 都会与此掩码匹配
- **`@@`** — 例外标记；以 `@@` 开头的规则允许请求（白名单）
- **选项** — `$` 后的参数，用于限制/改变规则行为

## 特殊字符

### `*` — 通配符

匹配任意字符集（可以是空字符串或任意长度）。用于填补 URL 模式中的间隙。

```
||example.com/ads/*
```
匹配：`https://example.com/ads/banner.jpg`、`https://example.com/ads/video.mp4`

### `||` — 域名锚点

匹配 URL 的开头部分，覆盖协议和域名。等同于同时匹配 `https://*.、`、`http://*.、`、`ws://*.、`、`wss://*.`。这是最常用的模式锚点。

```
||example.com^
```
拦截：
- `https://example.com/ad1.gif`
- `https://subdomain.example.com/ad1.gif`
- `https://ads.example.com:8000/`

不拦截：
- `https://example.org/`
- `https://example.com.us/ad1.gif`

### `^` — 分隔符字符

分隔符是**除了**字母、数字、`_`、`-`、`.`、`%` 之外的任何字符。URL 的末尾也被视为分隔符。

```
||example.com^
```
这是匹配域名及其所有路径/查询的标准方式，同时确保域名边界得到尊重。

### `|` — URL 起始/结束标记

根据放置位置，匹配 URL 的开头或结尾。

**结束标记：**
```
.swf|
```
匹配：`https://example.com/annoyingflash.swf`
不匹配：`https://example.com/swf/index.html`

**起始标记：**
```
|https://example.org
```
匹配：`https://example.org`
不匹配：`https://domain.com?url=https://example.org`

**精确匹配（双标记）：**
```
|https://example.org/|
```
仅精确匹配 `https://example.org/`。

### 重要限制

`|`、`||`、`^` 只能用于网络过滤模式（URL 匹配）。不能用于元素隐藏选择器（如 `||example.com##.advert` 是无效的）。

## 正则表达式过滤器

使用 `/` 包裹的正则表达式进行更灵活的匹配：

```
/banner\d+/$third-party
```
对所有第三方请求应用正则 `banner\d+`。

```
@@/banner\d+/
```
上述正则模式的例外规则。

**性能提示：** 正则过滤器评估更慢 — 尽可能优先使用 `||`、`^`、`*` 的普通模式，并通过 `$domain=` 限制正则的作用范围。

## HOSTS 文件解析

uBO 可以解析类 HOSTS 文件的资源。所有主机名条目被解释为等同于 `||hostname^` 过滤器。

**歧义解析：** 裸条目如 `example.com` 会被 uBO 解释为 `||example.com^`（拦截该站点及其所有子域名），而不是"拦截包含 `example.com` 的 URL"（这是 ABP 的解释方式）。

要强制 ABP 风格的解释（包含匹配），添加通配符：
```
example.com*
```

要确保文件名不被解析为主机名，前置斜杠：
```
/example.js
```

**重要：** uBO 的 HOSTS 解释包括拦截主文档本身（严格拦截）。详见 `document` 选项。

## `_` 即 "noop"

一个不执行任何操作的占位符选项。用于解决解析歧义，特别是带有正则参数的 `$removeparam` 过滤器（可能被误解析为普通正则过滤器）：

```
/ad-$removeparam=/^foo=bar\d$/,_
```

从 1.50.1b11 起，支持多个 `_` 选项以提高可读性：
```
||example.com$_,removeparam=/^ss\\$/,_,image
||example.com$replace=/bad/good/,___,~third-party
```

## `*` 即 "所有 URL" 模式

通配符 `*` 作为整个模式时应用于**所有** URL。始终应配合选项缩小范围：

- `*$third-party` — 拦截所有第三方网络请求
- `*$script,domain=example.com` — 拦截 example.com 上的所有脚本请求
- `*$image,important` — 强制拦截所有图片

通常动态过滤规则更适合大范围拦截。

## 过滤示例

```adblock
||example.com/ads/*
```
匹配：`https://example.com/ads/banner.jpg`、`https://subdomain.example.com/ads/otherbanner.jpg`

```adblock
||example.org^$third-party
```
拦截到 example.org 及其子域名的第三方请求

```adblock
@@||example.com$document
```
完全白名单允许 example.com 及其所有子域名

```adblock
||tracker.example.com^$important
```
即使存在例外规则也强制拦截 tracker.example.com

```adblock
/ad[-_]?banner/
```
正则过滤器匹配 ad-banner、ad_banner 或 adbanner 模式
