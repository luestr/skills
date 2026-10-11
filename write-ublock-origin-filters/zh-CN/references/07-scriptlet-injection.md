# 脚本注入

> 使用 uBO 的脚本注入语法和资源库向网页注入 JavaScript 代码。

## 语法

```
[主机名]##+js(脚本名[, 参数1[, 参数2[, ...]]])
```

- `##+js(...)` 语法从 uBO 的[资源库](https://github.com/gorhill/uBlock/wiki/Resources-Library)注入 JavaScript
- 脚本过滤器**必须是特定的**（需要主机名前缀）— 通用的 `+js` 过滤器会被忽略
- 参数中的逗号必须转义：`foo\,bar`（或正则字面量中使用 `/foo\x2cbar/`）

## 例外语法（1.22.0+）

对特定站点禁用脚本注入：
```
example.com#@#+js()
```

在所有地方禁用所有脚本注入：
```
#@#+js()
```

空形式 `example.com##+js()` 无意义且会被忽略。

## 常用脚本

### `abort-on-property-read` / `aopr`

当属性被**读取**时中止脚本执行。

```
example.com##+js(aopr, adBlockDetected)
```

### `abort-on-property-write` / `aopw`

当属性被**写入**时中止脚本执行。

```
example.com##+js(aopw, Fingerprint2)
```

### `abort-current-script` / `acs`

当内联脚本尝试访问属性时中止其执行（抛出 `ReferenceError`）。

```
example.com##+js(acis, Math.random)
```

### `abort-on-stack-trace` / `aost`

当属性访问发生在匹配的堆栈跟踪中时中止脚本。

```
example.com##+js(aost, Math.random, /ads\.example\.com/)
```

### `set-constant` / `set`

将属性设置为指定值，阻止页面更改它。

```
example.com##+js(set, adBlockDetected, false)
example.com##+js(set, isAdFree, true)
```

### `addEventListener-defuser` / `aeld`

阻止匹配的事件监听器被添加。

```
example.com##+js(aeld, load, /adblock/)
```

### `prevent-setTimeout` / `nostif`

阻止匹配模式的 `setTimeout` 调用。

```
example.com##+js(nostif, /adblock/)
```

### `prevent-setInterval` / `nosiif`

阻止匹配模式的 `setInterval` 调用。

```
example.com##+js(nosiif, detectAd)
```

### `prevent-xhr` / `no-xhr-if`

阻止匹配指定模式的 XHR 请求。

```
example.com##+js(no-xhr-if, /\/ads\//)
```

### `prevent-fetch` / `no-fetch-if`

阻止匹配指定模式的 fetch 请求。

```
example.com##+js(no-fetch-if, /\/tracking\//)
```

### `prevent-window-open` / `nowoif`

阻止或重定向 `window.open()` 调用。

```
example.com##+js(nowoif)
```
阻止所有 window.open 调用。

### `set-cookie`

设置 cookie 值。

```
example.com##+js(set-cookie, consent, accepted)
```

### `remove-cookie` / `cookie-remover`

移除 cookie。

```
example.com##+js(remove-cookie, tracking_id)
```

### `set-local-storage-item` / `set-session-storage-item`

在 localStorage 或 sessionStorage 中设置值。

```
example.com##+js(set-local-storage-item, adFree, true)
```

### `remove-attr` / `ra`

从 DOM 元素中移除属性。（建议改用 `:remove-attr()` 元素隐藏过滤器。）

### `remove-class` / `rc`

从 DOM 元素中移除类名。（建议改用 `:remove-class()` 元素隐藏过滤器。）

### `remove-node-text` / `rmnt`

从匹配节点中移除文本内容。在 HTML 过滤上下文中很有用。

### `json-prune`

从页面解析的 JSON 数据中移除属性。

```
example.com##+js(json-prune, ads, )
```

### `object-prune`

使用 JSONPath 查询从对象中移除属性。

### `noeval` / `noeval-if`

阻止 `eval()` 调用（可选匹配模式）。

### `nowebrtc`

阻止 WebRTC 连接（替代已弃用的 `$webrtc` 网络选项）。

```
example.com##+js(nowebrtc)
```

### `spoof-css`

欺骗 `getComputedStyle` 返回的 CSS 属性值。

### `prevent-canvas`

阻止 canvas 指纹识别。

### `close-window` / `window-close-if`

满足条件时关闭窗口。

### `overlay-buster`

移除阻止页面交互的覆盖层对话框。

### `alert-buster`

通过将消息重定向到控制台来抑制 `alert()` 对话框。

### `href-sanitizer`

通过移除跟踪参数来清理链接。

### `disable-newtab-links`

阻止在新标签页中打开链接。

## 受信脚本

标记为 `[Trusted]` 的脚本仅在受信来源下可用（uBO 自带过滤列表或用户启用信任的"我的过滤"）：

- `trusted-click-element` — 以编程方式点击元素
- `trusted-set-constant` — 扩展的 set-constant，支持更多值类型
- `trusted-set-cookie` — 设置带过期时间和路径的 cookie
- `trusted-set-local-storage-item` / `trusted-set-session-storage-item`
- `trusted-set-attr` — 在元素上设置属性
- `trusted-create-HTML` — 创建 HTML 元素
- `trusted-replace-xhr-response` / `trusted-replace-fetch-response`
- `trusted-replace-node-text` / `trusted-replace-outbound-text`
- `trusted-replace-argument`
- `trusted-prevent-xhr` / `trusted-prevent-fetch`
- `trusted-prune-inbound-object` / `trusted-prune-outbound-object`
- `trusted-suppress-native-method`
- `trusted-override-element-method`
- `trusted-prevent-dom-bypass`

## `edit` 系列脚本

使用 uBO 风格 JSONPath 查询编辑对象的脚本家族：

- `edit-outbound-object` — 从方法返回的对象中删除属性
- `edit-inbound-object` — 从作为参数传递的对象中删除属性
- `edit-this-object` — 通过对象自身方法删除属性
- `edit-element-object` — 从 DOM 元素中删除属性
- `json-edit` — 编辑通过 `JSON.parse()` 生成的对象
- `json-edit-xhr-response` / `json-edit-fetch-response` — 编辑获取的 JSON
- `json-edit-xhr-request` / `json-edit-fetch-request` — 编辑请求体 JSON
- `jsonl-edit-xhr-response` / `jsonl-edit-fetch-response` — 编辑 JSONL 响应

## 绕过脚本

专门用于中和特定广告拦截检测脚本的脚本：

- `nobab` — 绕过 BlockAdblock
- `nobab2` — 绕过 BAB 4.2b
- `nofab` — 绕过 FuckAdBlock/BlockAdBlock/SniffAdBlock
- `popads-dummy` / `popads` — 中和 PopAds
- `prebid-ads` — Prebid-ads 垫片
- `fingerprint2` / `fingerprint3` — FingerprintJS 垫片
- `ampproject_v0` — 移除 AMP 动画延迟

## 空重定向资源

与 `$redirect=` 选项配合使用以提供空/最小响应：

**图片：** `1x1.gif`、`2x2.png`、`3x2.png`、`32x32.png`
**代码：** `noop.js`、`noop.css`、`noop.html`、`noop.json`、`noop.txt`
**媒体：** `noop-0.1s.mp3`、`noop-0.5s.mp3`、`noop-1s.mp4`
**XML：** `noop-vast2.xml`、`noop-vast3.xml`、`noop-vast4.xml`、`noop-vmap1.xml`
**特殊：** `none`（禁用重定向）、`click2load.html`（iframe 可交互占位符）

## 特定 URL 替代资源

经清理的特定域名重定向资源：
- `google-analytics_analytics.js` / `google-analytics_ga.js`
- `googletagservices_gpt.js` / `googletagmanager_gtm.js`
- `googlesyndication_adsbygoogle.js`
- `amazon_ads.js` / `amazon_apstag.js`
- `scorecardresearch_beacon.js`
- `google-ima.js`
- `outbrain-widget.js`
- `hd-main.js`
