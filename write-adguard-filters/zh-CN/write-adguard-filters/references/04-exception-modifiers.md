# 例外规则修饰符 & 泛型规则

> 例外规则以 `@@` 开头，用于放行请求。它们拥有专属修饰符来控制放行范围。
> 泛型规则是不限定特定域名的规则。

## 重要说明

默认情况下，例外规则修饰符仅对**主框架文档请求**生效。要对所有子请求生效，需配合内容类型修饰符。

---

## 例外规则专属修饰符

### `$content` — 禁用内容修改规则

在匹配页面上禁用 [HTML 过滤](#)、`$hls`、`$replace` 和 `$jsonprune` 规则。

```adblock
@@||example.com^$content
```

---

### `$elemhide` — 禁用外观规则

在匹配页面上禁用所有[外观规则](#)。

**别名：** `$ehide`

```adblock
@@||example.com^$elemhide
```

---

### `$extension` — 禁用用户脚本

禁用特定或所有用户脚本。

**语法：**
```
$extension[="脚本名1"[|"脚本名2"[...]]]
```

- 不指定脚本名则禁用所有用户脚本
- 使用 `~` 排除特定脚本（保留不禁用）
- 脚本名含特殊字符时需用引号包裹（单引号或双引号）
- 脚本名中的 `"`、`,`、`|` 需用 `\` 转义

**示例：**
```adblock
@@||example.com^$extension="AdGuard Assistant"
@@||example.com^$extension=MyUserscript
@@||example.com^$extension='AdGuard Assistant'|'AdGuard Popup Blocker'
@@||example.com^$extension=~"AdGuard Assistant"
@@||example.com^$extension  -- 禁用所有用户脚本
```

**兼容性：** 仅 CoreLibs apps。指定脚本名需 CoreLibs v1.13+。

---

### `$jsinject` — 禁用 JS 注入

禁止向页面添加 JavaScript 代码（脚本片段和 JS 规则）。

```adblock
@@||example.com^$jsinject
```

**限制：** MV3 中无法转为 DNR 规则，仅用于 TSUrlFilter 引擎。Content Blocker 不支持。

---

### `$stealth` — 禁用跟踪保护

禁用跟踪保护（原隐身模式）模块。

**语法：**
```
$stealth [= 选项1 [| 选项2 [| 选项3 [...]]]]
```

**可用选项：**
`searchqueries`、`donottrack`、`3p-cookie`、`1p-cookie`、`3p-cache`、`3p-auth`、`webrtc`、`push`、`location`、`flash`、`java`、`referrer`、`useragent`、`ip`、`xclientdata`、`dpi`

**示例：**
```adblock
@@||example.com^$stealth
@@||domain.com^$script,stealth,domain=example.com
@@||example.com^$stealth=3p-cookie|dpi
```

**注意：** `$stealth` 例外不会阻止 cookie 或移除跟踪参数。要完全禁用，需同时使用 `$stealth,removeparam,cookie`。

**限制：** 选项必须小写，不能否定。Browser Extension 仅支持部分选项。

**兼容性：** Windows/Mac/Android/Firefox/Chromium 扩展（不含 MV3）。

---

### `$urlblock` — 禁用所有请求拦截

禁用从匹配页面发出的所有请求的拦截，同时禁用 `$cookie` 规则。

```adblock
@@||example.com^$urlblock
```

**限制：** iOS/Safari 中等同于 `$document` 例外。Content Blocker 和 MV3 不支持。

---

## 泛型规则

**泛型规则**是不限定特定域名的规则。

**泛型规则示例：**
```
###banner
*###banner
#@#.adsblock
*#@#.adsblock
~domain.com###banner
||domain.com^
||domain.com^$domain=~example.com
```

**非泛型规则示例：**
```
domain.com###banner
||domain.com^$domain=example.com
```

### `$genericblock` — 禁用泛型基本规则

在匹配页面上禁用泛型基本规则。

```adblock
@@||example.com^$genericblock
```

**限制：** iOS/Safari 中等同于 `$document` 例外。Content Blocker 和 MV3 不支持。

---

### `$generichide` — 禁用泛型外观规则

在匹配页面上禁用所有泛型[外观规则](#)。

**别名：** `$ghide`

```adblock
@@||example.com^$generichide
```

---

### `$specifichide` — 禁用特定外观规则

禁用所有特定元素隐藏和 CSS 规则（但不禁用泛型规则）。效果与 `$generichide` 相反。

**别名：** `$shide`

```adblock
@@||example.org^$specifichide
```
禁用 `example.org##.banner`，但不禁用 `##.banner`。

**注意：** `$elemhide` 可禁用所有外观规则（包括特定和泛型）。iOS/Safari/Content Blocker 不支持。
