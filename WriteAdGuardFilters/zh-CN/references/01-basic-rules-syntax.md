# 基本规则语法

> 最简单的规则类型，用于拦截或放行对特定 URL 的请求。

## 重要说明

- 基本规则默认只作用于**子请求**（sub-requests），不会阻止页面加载（除非使用 `$document`）
- 被拦截的请求在浏览器中显示为"请求出错"
- 规则长度**少于 4 字符**的会被忽略
- AdGuard 将 URL 截断到 **4096 字符**以加速匹配

## 语法

```
规则 = ["@@"] 模式 ["$" 修饰符列表]
修饰符列表 = [修饰符0, 修饰符1[, ...[, 修饰符N]]]
```

- **模式 (pattern)** — 地址掩码，每个请求 URL 会与此掩码匹配
- **`@@`** — 例外标记，以 `@@` 开头表示放行请求
- **修饰符 (modifiers)** — 参数，限制或改变规则行为

## 特殊字符

### `*` — 通配符

匹配任意字符集（可以是空字符串或任意长度的字符串）。

### `||` — 域名匹配

将规则应用于指定域名及其子域名。等同于同时匹配 `https://*.`、`http://*.`、`ws://*.`、`wss://*.`。

**示例：**
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

### `^` — 分隔符标记

分隔符是**除字母、数字、`_`、`-`、`、`%` 之外**的任何字符。URL 结尾也被视为分隔符。

**示例：**
```
http://example.com/?t=1&t2=t3
```
分隔符字符（加粗）：`://`、`/`、`?`、`=`、`&`、`=`

### `|` — 地址起止标记

根据位置不同，匹配地址的开始或结束。

**示例：**
```
swf|
```
匹配 `https://example.com/annoyingflash.swf`
不匹配 `https://example.com/swf/index.html`

```
|https://example.org
```
匹配 `https://example.org`
不匹配 `https://domain.com?url=https://example.org`

### 重要限制

`|`、`||`、`^` 只能用于带 URL 模式的规则。例如 `||example.com##.advert` 是错误的。

## 正则表达式支持

需要更灵活的匹配时，可以使用正则表达式代替简化掩码。

**性能提醒：** 正则表达式规则匹配速度更慢，建议避免使用或限制在特定域名范围。

**语法：** 模式用 `/` 包围：
```
模式 = "/" 正则表达式 "/"
```

**示例：**
```
/banner\d+/$third-party
```
将正则表达式 `banner\d+` 应用于所有第三方请求。

**例外规则：**
```
@@/banner\d+/
```

### 兼容性

AdGuard Safari 和 AdGuard for iOS 不完全支持正则表达式（Content Blocking API 限制）。

## TLD 通配符支持

外观规则、HTML 过滤和 JavaScript 规则的域名模式中支持 TLD 通配符 `.*`。

**外观规则示例：**
```
example.*##.banner
```
匹配 `example.com`、`sub.example.net`、`example.co.uk` 等。

**基本规则中的 `$domain` 修饰符：**
```
||*/banners/*$image,domain=example.*
```

### 兼容性

- AdGuard for Windows/Mac/Android 和 Browser Extension 中，`.*` 匹配任何公共后缀（eTLD）
- AdGuard for Safari/iOS 支持的 TLD 列表受限
- AdGuard Content Blocker 不支持 TLD 通配符

## 基本规则示例

```adblock
||example.com/ads/*
```
匹配 `https://example.com/ads/banner.jpg` 和 `https://subdomain.example.com/ads/otherbanner.jpg`

```adblock
||example.org^$third-party
```
拦截对 example.org 及其子域名的第三方请求

```adblock
@@||example.com$document
```
完全禁用 example.com 及所有子域名的过滤
