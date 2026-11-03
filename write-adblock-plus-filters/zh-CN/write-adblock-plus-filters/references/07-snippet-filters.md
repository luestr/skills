# 代码片段过滤器

代码片段过滤器在指定域名的页面上运行专门的 JavaScript 代码片段。它们是最强大的过滤器类型 — 能够以 CSS 选择器无法实现的方式操纵页面行为。

**安全提示：** 代码片段过滤器只能添加到用户自定义过滤规则或 ABP 反规避过滤列表中。

## 基础语法

```
<域名>#$#<代码片段命令> <参数>
```

`#$#` 分隔符标记代码片段过滤器。多个代码片段可以用 `;` 链接：

```
example.com#$#abort-on-property-read adblock; hide-if-contains ad .ad-class
```

## 参数规则

- 参数是字符串；如果包含空格，用单引号 (`'`) 包裹。
- 在引号内转义单引号：`\'`
- 不加引号时转义空格：`\ `（反斜杠-空格）
- Unicode：`\uNNNN`（如 `\u1F601` = 😀）
- 特殊字符：`\r`、`\n`、`\t`
- 字面反斜杠：`\\`

## 调试与日志代码片段

| 代码片段 | 用途 | 示例 |
|---|---|---|
| `log` | 打印到 Web 控制台 | `example.com#$#log Hello` |
| `trace` | 在文档上下文中记录（非内容脚本） | `example.com#$#trace OK` |
| `debug` | 为后续代码片段启用调试模式 | `example.com#$#debug; abort-on-property-read atob` |
| `profile` | 通过 Performance API 测量代码片段性能 | `example.com#$#profile; abort-on-property-read atob` |

**调试过滤：** `debug hello; snippet-name` — 仅显示包含 "hello" 的调试日志。支持正则：`debug /json-prune\|json-override/; snippet-name`。

## 性能

| 代码片段 | 用途 |
|---|---|
| `race start;` ... `race stop;` | 多个代码片段竞速；胜者发出信号，败者被停止 |

```
example.com#$#race start; snippet-a 1 2 3; snippet-b 4 5 6; race stop;
```

```
example.com#$#race start 2; first 1; second 2; third 3; fourth 4; race stop;
```
（前 2 个发出信号的"胜出"，其余被停止）

## 行为代码片段

这些代码片段改变页面的执行行为：

### `abort-on-property-read`

修补 `window` 上的属性，在属性被**读取**时中止脚本执行。

```
example.com#$#abort-on-property-read adblock
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `property` | 是 | 属性名或点路径（如 `navigator.userAgent`） |
| `setConfigurable` | 否 | 设为 `false` 可阻止网站通过将属性设为不可配置来规避 |

### `abort-on-property-write`

与上面相同，但在属性被**写入**时触发：

```
example.com#$#abort-on-property-write adblockDetected
```

### `abort-current-inline-script`

当属性被读取或写入时中止内联脚本：

```
example.com#$#abort-current-inline-script document.write adblock
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `api` | 是 | 用于锚定的属性 |
| `search` | 否 | 仅中止包含此字符串的脚本（支持用 `/` 包裹的正则表达式） |

### `abort-on-iframe-property-read` / `abort-on-iframe-property-write`

类似上面的版本但针对 iframe 属性：

```
example.com#$#abort-on-iframe-property-read prop1 prop2
```

### `cookie-remover`

按名称模式删除 Cookie：

```
example.com#$#cookie-remover tracking_id
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `cookie` | 是 | Cookie 名称或正则表达式（用 `/` 包裹） |
| `autoRemoveCookie` | 否 | `true` — 持续监控并每 1 秒删除该 Cookie |

### `set-constant`

将 JavaScript 属性设置为常量值：

```
example.com#$#set-constant adblock false
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `property` | 是 | 属性名或点路径 |
| `value` | 是 | 要设置的值（字符串、数字、布尔值、`null`、`undefined`、`noopFunc`、`trueFunc`、`falseFunc`、`noopArray`、`noopString`） |

### `json-prune`

从 JSON 响应中移除属性：

```
example.com#$#json-prune ads.* tracking
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `props` | 是 | 空格分隔的要移除的属性路径（支持通配符） |
| `requiredProps` | 否 | 仅在这些属性存在时才修剪 |

**JSONPath 支持**（ABP 4.36+）：用 `jsonpath(` 前缀：
```
example.com#$#json-prune jsonpath($..ad_tracking)
```

### `json-override`

覆盖 JSON 属性值：

```
example.com#$#json-override ads.enabled false
```

**JSONPath 支持：**
```
example.com#$#json-override jsonpath($.items[(@.is_sponsored==true)].label) "Clean Content"
```

### `override-property-read`

覆盖属性被读取时返回的值：

```
example.com#$#override-property-read document.hasFocus trueFunc
```

### `run-at`

控制代码片段何时运行：

```
example.com#$#run-at document-start abort-on-property-read adblock
```

值：`document-start`、`document-end`、`document-idle`

### `prevent-listener`

阻止添加事件监听器：

```
example.com#$#prevent-listener visibilitychange
```

### `prevent-addEventListener`

阻止特定的 `addEventListener` 调用：

```
example.com#$#prevent-addEventListener click /ad[_-]?click/
```

### `prevent-setTimeout` / `prevent-setInterval`

阻止匹配模式的定时器调用：

```
example.com#$#prevent-setTimeout /ad[_-]?display/
```

### `event-override`

代理和修改事件（ABP 4.22.2+）：

```
example.com#$#event-override click trusted
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `eventType` | 是 | 事件类型（如 `click`、`mouseover`） |
| `mode` | 是 | `trusted`（使 isTrusted 为 true）或 `disable`（阻止事件） |
| `needle` | 否 | 仅当监听器函数包含此字符串时才覆盖 |

### `blob-override`

覆盖 Blob 内容（ABP 4.22.2+）：

```
example.com#$#blob-override /ad[_-]?code/ ''
```

### `array-override`

覆盖 Array.prototype 方法（ABP 4.8+）：

```
example.com#$#array-override push /ad[_-]?slot/
```

## 条件隐藏代码片段

### `hide-if-contains`

隐藏包含特定文本的元素：

```
example.com#$#hide-if-contains ad .ad-class
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `search` | 是 | 要查找的字符串。用 `/` 包裹则视为正则表达式。 |
| `selector` | 是 | 元素必须匹配的 CSS 选择器才会被隐藏。 |
| `searchSelector` | 否 | 包含字符串的元素必须匹配的 CSS 选择器。默认为 `selector`。 |

### `hide-if-contains-visible-text`

类似 `hide-if-contains` 但仅匹配**可见**文本（遵守 CSS 可见性、字体大小、颜色、不透明度和溢出）：

```
example.com#$#hide-if-contains-visible-text ad .ad-class
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `search` | 是 | 要查找的字符串。用 `/` 包裹则视为正则表达式。 |
| `selector` | 是 | 元素必须匹配的 CSS 选择器才会被隐藏。 |
| `searchSelector` | 否 | 包含字符串的元素必须匹配的 CSS 选择器。默认为 `selector`。 |
| `optionalParameters` | 否 | 额外的可见性检查，格式为 `key:value` 用单引号包裹，如 `'-disable-font-check:true' 'opacity:0'`。 |

**注意：** 支持 `^^sh^^` 分隔符，但**不支持** `^^svg^^`。

### `hide-if-contains-image`

隐藏包含具有特定特征的图片的元素：

```
example.com#$#hide-if-contains-image /ad[_-]?banner/ .ad-container
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `search` | 是 | 匹配图片 alt 文本或 src 的字符串或正则表达式。 |
| `selector` | 是 | 元素必须匹配的 CSS 选择器才会被隐藏。 |

### `hide-if-contains-similar-text`

隐藏文本与给定字符串相似（模糊匹配）的元素：

```
example.com#$#hide-if-contains-similar-text '赞助内容' .ad-class 0.8
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `search` | 是 | 用于比较的文本（模糊匹配）。 |
| `selector` | 是 | 元素必须匹配的 CSS 选择器才会被隐藏。 |
| `threshold` | 是 | 相似度阈值（0-1）。越高越严格。 |

### `hide-if-contains-and-matches-style`

隐藏文本内容匹配字符串且计算样式匹配条件的元素：

```
example.com#$#hide-if-contains-and-matches-style ad .ad-class .parent
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `search` | 是 | 要查找的字符串。用 `/` 包裹则视为正则表达式。 |
| `selector` | 是 | 元素必须匹配的 CSS 选择器才会被隐藏。 |
| `searchSelector` | 否 | 包含字符串的元素必须匹配的 CSS 选择器。默认为 `selector`。 |
| `style` | 否 | 匹配 `selector` 的元素的计算样式必须包含的字符串。支持正则。 |
| `searchStyle` | 否 | 匹配 `searchSelector` 的元素的计算样式必须包含的字符串。支持正则。 |
| `waitUntil` | 否 | 延迟运行直到达到指定状态。接受：`loading`、`interactive`、`complete`、`load` 或任意事件名。 |
| `windowWidthMin` | 否 | 当 `window.innerWidth` 小于此值时禁用代码片段。 |
| `windowWidthMax` | 否 | 当 `window.innerWidth` 大于此值时禁用代码片段。 |

### `hide-if-has-and-matches-style`

隐藏后代匹配选择器且计算样式满足条件的元素：

```
example.com#$#hide-if-has-and-matches-style .ad-child .container
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `search` | 是 | 匹配后代元素的 CSS 选择器。 |
| `selector` | 是 | 元素必须匹配的 CSS 选择器才会被隐藏。 |
| `searchSelector` | 否 | 包含指定后代的元素必须匹配的 CSS 选择器。默认为 `selector`。 |
| `style` | 否 | 匹配 `selector` 的元素的计算样式必须包含的字符串。支持正则。 |
| `searchStyle` | 否 | 匹配 `searchSelector` 的元素的计算样式必须包含的字符串。支持正则。 |
| `waitUntil` | 否 | 延迟运行直到达到指定状态。 |
| `windowWidthMin` | 否 | 当 `window.innerWidth` 小于此值时禁用代码片段。 |
| `windowWidthMax` | 否 | 当 `window.innerWidth` 大于此值时禁用代码片段。 |

### `hide-if-shadow-contains`

隐藏 **Shadow DOM** 中包含匹配文本的元素：

```
example.com#$#hide-if-shadow-contains ad .shadow-host
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `search` | 是 | 要查找的字符串。用 `/` 包裹则视为正则表达式。 |
| `selector` | 是 | 元素必须匹配的 CSS 选择器才会被隐藏。 |

### `hide-if-labelled-by`

隐藏具有指向包含特定文本的标签的 `aria-labelledby` 的元素：

```
example.com#$#hide-if-labelled-by ad [aria-labelledby]
```

### `hide-if-matches-xpath`

通过 XPath 1.0 查询隐藏元素：

```
example.com#$#hide-if-matches-xpath //div[contains(@class,'ad')]
```

### `hide-if-matches-xpath3`

通过 XPath 3.1 查询隐藏元素（ABP 3.19+）。

### `hide-if-matches-computed-xpath`

通过带正则提取的动态构建 XPath 隐藏元素：

```
example.com#$#hide-if-matches-computed-xpath //div[@class='{{}}'] //span[@id='source'] /ad[_-]?[\w]+/
```

### `hide-if-svg-contains`

隐藏包含具有特定可见文本的 SVG 图片的元素（ABP 4.26+）。

## Shadow DOM 访问

在 CSS 选择器中使用分隔符来访问 Shadow DOM 元素：

| 分隔符 | 目标 | 示例 |
|---|---|---|
| `^^sh^^` | 开放/封闭的 shadow root | `.parent ^^sh^^ .child` |
| `^^svg^^` | SVG `<use>` 引用的元素 | `.use-element ^^svg^^` |

```
example.com#$#hide-if-contains ad .host ^^sh^^ .inner-element
```

可以链接多个分隔符来访问嵌套的 Shadow DOM。

## 其他实用代码片段

| 代码片段 | 用途 |
|---|---|
| `freeze-element` | 冻结 DOM 元素以阻止添加新节点（详见下方） |
| `simulate-mouse-event` | 在元素上模拟鼠标事件（详见下方） |
| `replace-node-text` | 替换匹配节点中的文本内容 |
| `replace-xhr-response` | 替换 XHR 响应中的内容 |
| `replace-xhr-request` | 替换 XHR 请求中的内容 |
| `adjust-setInterval` / `adjust-setTimeout` | 修改定时器间隔/延迟 |
| `nano-setInterval-booster` / `nano-setTimeout-booster` | 加速基于定时器的广告脚本 |
| `remove-attr` | 从元素上移除属性 |
| `remove-class` | 从元素上移除 CSS 类 |
| `set-attr` | 在元素上设置属性 |
| `add-class` | 向元素添加 CSS 类 |

### `freeze-element`（详细）

冻结 DOM 元素，阻止在其内部添加新节点（ABP 3.10+）。

```
example.com#$#freeze-element .ad-container
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `selector` | 是 | 要冻结元素的 CSS 选择器 |
| `property` | 否 | 要监控变化的特定属性 |
| `value` | 否 | 被监控属性的期望值 |

### `simulate-mouse-event`（详细）

在匹配 CSS 选择器的元素上模拟鼠标事件。对于仅在用户交互时运行的广告加载代码很有用：

```
example.com#$#simulate-mouse-event .ad-button click
```

| 参数 | 必需 | 描述 |
|---|---|---|
| `selector` | 是 | 目标元素的 CSS 选择器。支持 `^^sh^^` 和 `^^svg^^` 分隔符。 |
| `event` | 是 | 鼠标事件类型：`click`、`mousedown`、`mouseup`、`mouseover`、`mouseout`、`mousemove` |

## JSONPath 语法（ABP 4.36+）

在 `json-prune`、`json-override`、`replace-xhr-response`、`replace-xhr-request` 中支持。用 `jsonpath(` 前缀路径。

| 运算符 | 名称 | 示例 |
|---|---|---|
| `$` | 根 | `$.data` |
| `.` | 点访问 | `$.store.book` |
| `..` | 递归下降 | `$..ad_id` |
| `*` | 通配符 | `$.items[*]` |
| `[]` | 方括号表示法 | `$['complex-key']` |
| `[?()]` | 过滤表达式 | `[?(@.type=='ad')]` |

过滤运算符：`==`、`!=`、`<`、`<=`、`>`、`>=`、`^=`（以...开头）、`$=`（以...结尾）、`*=`（包含）。
