# 基础过滤规则

本模块涵盖 Adblock Plus 拦截过滤规则的基础语法 — 如何使用纯文本、通配符、地址锚点和分隔符来匹配 URL，以及如何编写注释。

## 纯文本匹配

最简单的过滤规则是一段纯文本字符串。Adblock Plus 会将其视为两端都有通配符 — 它会匹配请求 URL 中的任何位置。

```
ad
```
这会匹配任何包含 "ad" 的 URL — 包括像 `/advice/` 这样的路径或像 `loadads.example` 这样的域名。注意不要使纯文本过滤规则太短或太通用，否则会导致意外拦截。

## 通配符

`*` 字符匹配零个或多个字符。它是显式通配符，尽管 ABP 会在每个过滤规则的开头和结尾隐式添加一个。

```
http://example.com/ads/banner*.gif
```
匹配 `/ads/` 下的 `banner123.gif`、`bannerABC.gif` 等。

```
http://example.com/ads/
```
拦截 `/ads/` 目录下的所有内容。

**警告：** 不要过度泛化。`http://example.com/` 会拦截该域名下的*所有内容* — 包括你可能想看的内容。

## 地址锚点 (`|`)

默认情况下，过滤规则匹配 URL 中的任何位置。管道符号 `|` 在开头或结尾创建明确的边界。

### 尾部锚点 (`...|`)
```
swf|
```
匹配*以* `swf` *结尾*的 URL — 拦截 `http://example.com/annoyingflash.swf`，但**不**拦截 `http://example.com/swf/index.html`。

### 头部锚点 (`|...`)
```
|http://baddomain.example/
```
匹配*以* `http://baddomain.example/` *开头*的 URL — 拦截 `http://baddomain.example/banner.gif`，但**不**拦截 `http://gooddomain.example/analyze?http://baddomain.example`。

### 域名锚点 (`||`)
```
||example.com/banner.gif
```
双管道 `||` 匹配域名名称的开头。这会拦截：
- `http://example.com/banner.gif`
- `https://example.com/banner.gif`
- `http://www.example.com/banner.gif`

但**不会**拦截：
- `http://badexample.com/banner.gif`（不同的域名）
- `http://gooddomain.example/analyze?http://example.com/banner.gif`（URL 不在域名边界处）

**`||` 是最常用且推荐的针对特定域名的方式。**

## 分隔符 (`^`)

`^` 是单个分隔符字符的占位符。分隔符是**非**字母、数字且不属于 `_`、`-`、`.`、`%` 之一的任何字符。URL 的末尾也算作分隔符。

```
http://example.com^
```
匹配 `http://example.com/` 和 `http://example.com:8000/`，但**不**匹配 `http://example.com.ar/`（因为 `.ar` 是字母/数字/点号，不是分隔符）。

**在 URL 中识别分隔符：**

```
http://example.com:8000/foo.bar?a=12&b=%D1%82
```
分隔符字符位置：`://`、`:`、`/`、`.`、`?`、`=`、`&`、`=`。`^` 可匹配其中任何一个。

**常见用法：** `||example.com^` 精确匹配域名 `example.com`，不管路径、端口或查询参数 — 这是"匹配整个域名"的标准模式。

## 组合使用

这些构建块可以组合在一起：

```
||cdn.example.com/ads/*.js$script
```
- `||cdn.example.com` — 匹配域名
- `/ads/*.js` — 匹配 `/ads/` 下的 JS 文件
- `$script` — 仅应用于脚本请求（参见网络过滤规则选项模块）

## 注释 (`!`)

任何以 `!` 开头的行都是注释。Adblock Plus 在拦截时会忽略它。

```
! 此规则拦截 example.com 的广告
||example.com/ads/

! 允许新闻板块通过
@@||example.com/news^$document
```

注释对于过滤规则列表维护至关重要 — 用它们来解释规则存在的*原因*，而不仅仅是做什么（语法本身通常可以表达"做什么"）。

## 技巧

- 优先使用 `||domain^` 而非宽泛的通配符来进行域名级别的拦截。
- 使用尾部锚点 (`|`) 来避免匹配不相关 URL 中的子字符串。
- 保持过滤规则尽可能具体，以减少误报。
- 始终为复杂过滤规则添加注释 — 未来的你（和其他过滤规则作者）会感谢你的。
