# 网络过滤规则选项

过滤规则选项修改拦截规则和例外规则的行为。它们附加在过滤规则模式末尾的 `$` 之后，以逗号分隔。

```
/模式/$选项1,选项2
```

## 类型选项

限制过滤规则适用的网络请求类型。可以组合多个类型。

| 选项 | 描述 |
|---|---|
| `script` | 通过 `<script>` 标签加载的外部脚本 |
| `image` | 通常来自 `<img>` 标签的图片 |
| `stylesheet` | 外部 CSS 样式表 |
| `object` | 浏览器插件处理的内容（Flash、Java） |
| `xmlhttprequest` | 通过 `XMLHttpRequest` 或 `fetch()` API 发起的请求 |
| `subdocument` | 嵌入的页面（iframe） |
| `ping` | 来自 `<a ping>` 或 `navigator.sendBeacon()` 的请求 |
| `websocket` | WebSocket 连接 |
| `webrtc` | WebRTC ICE 服务器连接 |
| `popup` | 在新标签页/窗口中打开的页面（**必须**明确指定才会拦截弹窗） |
| `font` | 外部字体文件 |
| `media` | 媒体文件（音频、视频） |
| `other` | 以上未涵盖的请求类型 |
| `match-case` | 使过滤规则模式区分大小写（默认不区分） |

**仅限例外规则的类型选项**（仅在 `@@` 规则中有意义）：

| 选项 | 描述 |
|---|---|
| `document` | 白名单页面本身 — 在该页面上禁用所有 ABP 功能 |
| `elemhide` | 在页面上禁用元素隐藏规则 |
| `generichide` | 仅禁用泛型元素隐藏规则 |
| `genericblock` | 仅禁用泛型拦截规则 |

**示例：**

```
||example.com/ads/*$script,stylesheet
```
仅拦截 `example.com` 的 `/ads/` 下的脚本和样式表请求。

```
*/BannerAd.gif$match-case
```
拦截 `BannerAd.gif`（大写 B 和 A）但不拦截 `bannerad.gif`。

## 反向类型选项 (`~`)

在类型前加 `~` 表示*排除*该类型。这是指定类型的反面。

```
||example.com/ads/*$~script,~image
```
拦截 `/ads/` 下*除*脚本和图片之外的所有请求。

可用的反向类型：`~script`、`~image`、`~stylesheet`、`~object`、`~xmlhttprequest`、`~subdocument`、`~ping`、`~websocket`、`~webrtc`、`~document`、`~elemhide`、`~other`。

## 第三方/第一方限制

```
||ads.example.com^$third-party
```
仅当请求来自与当前浏览页面**不同**的域名时，才拦截对 `ads.example.com` 的请求。

```
||example.com/analytics.js$~third-party
```
仅当从与页面**相同**的来源加载时（第一方才拦截 `analytics.js`。

## 域名限制 (`$domain`)

将过滤规则限制在特定域名：

```
||ads.example.com^$domain=example.com
```
仅在你访问 `example.com`（或其子域名/iframe）时才拦截广告请求。

多个域名（用管道分隔）：
```
||ads.example.com^$domain=example.com|example.net
```

排除域名（波浪号前缀）：
```
||ads.example.com^$domain=~example.com
```
在*除* `example.com` 之外的每个站点上拦截广告。

组合包含和排除：
```
||ads.example.com^$domain=example.com|~foo.example.com
```
在 `example.com` 上拦截广告，但不在 `foo.example.com` 子域名上拦截。

**注意：** 对于拦截规则，域名必须在 `$domain` 下指定，该规则才会被视为站点特定的（与 `$genericblock`/`$generichide` 相关）。

## 站点密钥限制 (`$sitekey`)

```
||ads.example.com^$sitekey=abcdsitekeydcba
```
仅在提供匹配公钥和可验证签名的页面上生效。多个站点密钥：`sitekey=key1|key2`。

站点密钥允许单个过滤规则跨多个域名生效，而无需逐一列出，但需要服务端实现（参见主文档中的站点密钥实现部分）。

## 内容安全策略 (`$csp`)

在匹配的响应中注入内容安全策略头：

```
||example.com^$csp=script-src: 'none'
```
注入 `script-src: 'none'` CSP 头，拦截匹配页面上的所有脚本（包括内联脚本）。

**谨慎使用** — 这是对抗高级规避的最后手段。尽可能优先使用具体的拦截规则。（需要 ABP 3.1+）

## 重定向到内部资源 (`$rewrite`)

将匹配的请求重定向到内部占位资源，而不是直接拦截：

```
||example.com/ads/analytics.js$rewrite=abp-resource:blank-js
```
浏览器收到一个空的 JavaScript 文件，而不是真实的文件 — 不会抛出错误。

**可用的内部资源：**

| 资源 | 内容 |
|---|---|
| `blank-text` | 空文本 |
| `blank-css` | 空样式表 |
| `blank-js` | 空 JavaScript |
| `blank-html` | 空 HTML 文档 |
| `blank-mp3` | 0.1 秒静音 MP3 |
| `blank-mp4` | 空白 MP4 视频 |
| `1x1-transparent-gif` | 1×1 透明 GIF |
| `2x2-transparent-png` | 2×2 透明 PNG |
| `3x2-transparent-png` | 3×2 透明 PNG |
| `32x32-transparent-png` | 32×32 透明 PNG |

**限制：**
- 必须与 `$domain=` 组合使用（不能没有域名限制）。
- 不能与 `$third-party` 一起使用，但可以与 `$~third-party` 一起使用。
- 过滤规则模式必须是 `*` 或以 `||` 开头。
- （需要 ABP 3.5+）

## 头部匹配 (`$header`)

基于 HTTP 头部拦截请求/响应：

```
||example.com^$header=x-tracking-id=some-value
```
如果 HTTP 响应包含头部 `x-tracking-id` 且其值包含 `some-value`，则拦截请求。

**仅检查头部是否存在**（省略内容和 `=`）：
```
||example.com^$header=x-tracking-id
```

**转义逗号**，用 `\x2c`：
```
||example.com^$header=x-custom=val1\x2c val2
```

**字面量 `\x2c`**，用 `\\` 转义：
```
||example.com^$header=x-custom=text\\x2c still literal
```

**注意事项：**
- 头部名称匹配不区分大小写。
- 仅支持 Firefox。
- 只能添加到用户自定义过滤规则或 ABP 反规避列表。
- 内容的正则表达式**尚不支持**（`header=/content/` 语法已保留）。
- （需要 ABP 3.11+）

## 添加头部 (`$addheader`)

向请求或响应注入 HTTP 头部，而不是拦截：

```
||example.com^$addheader=request:X-Custom-Header: value
```
向发送给服务器的**请求**添加头部 `X-Custom-Header: value`。

```
||example.com^$addheader=response:X-Frame-Options: DENY
```
向浏览器收到的**响应**添加头部 `X-Frame-Options: DENY`。

**前缀：** `request:` 用于请求头部，`response:` 用于响应头部。

**注意事项：**
- 仅支持 Firefox。
- （需要 ABP 4.32.0+）

## 正则表达式

将过滤规则模式包裹在 `/` 中以使用正则表达式：

```
/ad-[0-9]+\.example\.com/
```
匹配任何包含 `ad-` 后跟一个或多个数字和 `.example.com` 的 URL。

```
/^https?:\/\/[a-z]{8}\.example\.com\/[a-z]{3}\.js/
```
匹配来自 `example.com` 的具有 8 个字母子域名和 3 个字母 `.js` 文件的 URL。

正则表达式遵循与 JavaScript `RegExp` 相同的语法。可以与过滤规则选项组合：

```
/ad[-_]?banner/$image,third-party
```

**性能提示：** 正则表达式过滤规则比纯文本或通配符过滤规则慢。仅在更简单的模式无法表达匹配时才使用它们。

## 选项优先级

当多个过滤规则匹配同一个请求时，更具体的过滤规则优先。具有域名限制的过滤规则比泛型的更具体。例外规则 (`@@`) 对于相同的匹配始终优先于拦截规则。
