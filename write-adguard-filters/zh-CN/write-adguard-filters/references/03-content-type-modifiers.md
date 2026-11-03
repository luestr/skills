# 内容类型修饰符

> 用于将规则限制到特定类型的请求内容（图片、脚本、样式表等）。可组合使用。

## 兼容性总览

| 修饰符 | CoreLibs | Chromium | MV3 | Firefox | iOS | Safari | Content Blocker |
|---|---|---|---|---|---|---|---|
| `$document` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `$font` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$image` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$media` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$object` | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| `$other` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `$ping` | ✅*[1]* | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ |
| `$script` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$stylesheet` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$subdocument` | ✅*[2]* | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| `$websocket` | ✅ | ✅ | ✅ | ✅ | ✅*[3]* | ✅*[3]* | ❌ |
| `$xmlhttprequest` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `$webrtc` 🚫 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `$object-subrequest` 🚫 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

## 内容类型检测方式

- **Browser Extension**: 浏览器直接提供内容类型
- **CoreLibs apps**: 先通过 `Sec-Fetch-Dest` 头或文件扩展名判断；若未被拦截，再通过 `Content-Type` 响应头判断

## 组合示例

```adblock
||example.org^$image
||example.org^$script,stylesheet
||example.org^$~image,~script,~stylesheet
```

---

## `$document` — 主文档请求

匹配主框架文档请求（浏览器标签页中加载的 HTML 文档），不匹配 iframe。

- 默认情况下，AdGuard 不会拦截标签页中加载的请求（"主框架豁免"）
- 明确使用 `$document` 修饰符时，AdGuard 会阻止页面加载并显示"拦截页面"
- 作为**例外规则**使用时（`@@...$document`），等同于同时使用 `$elemhide`、`$content`、`$urlblock`、`$jsinject`、`$extension`

**别名：** `$doc`

**示例：**
```adblock
@@||example.com^$document           -- 完全禁用过滤
||example.com^$document             -- 阻止页面加载
||example.com^$document,redirect=noopframe  -- 重定向为空页面
||example.com^$document,removeparam=test    -- 移除查询参数
||example.com^$document,replace=/test1/test2/ -- 替换内容
```

---

## `$font` — 字体请求

匹配字体请求（如 `.woff` 文件扩展名）。

---

## `$image` — 图片请求

匹配图片请求。

---

## `$media` — 媒体请求

匹配媒体文件请求（音乐和视频，如 `.mp4` 文件）。

---

## `$object` — 插件资源请求

匹配浏览器插件资源请求（如 Java 或 Flash）。

**兼容性：** AdGuard for Safari 和 iOS 不支持。

---

## `$other` — 其他请求

匹配类型未确定或不属于上述类型的请求。

---

## `$ping` — Ping 请求

匹配由 `navigator.sendBeacon()` 或链接的 `ping` 属性触发的请求。

**限制：** CoreLibs apps 往往无法准确检测 `navigator.sendBeacon()`。不推荐在 CoreLibs 产品使用的过滤列表中使用。

**兼容性：** Safari 和 iOS 不支持。

---

## `$script` — 脚本请求

匹配脚本请求（如 JavaScript、VBScript）。

---

## `$stylesheet` — 样式表请求

匹配 CSS 文件请求。

**别名：** `$css`

---

## `$subdocument` — 子文档请求

匹配内置页面请求——HTML 标签 `frame` 和 `iframe`。

**别名：** `$frame`

**示例：**
```adblock
||example.com^$subdocument
||example.com^$subdocument,domain=domain.com
```

**限制：** CoreLibs apps 通过 `Sec-Fetch-Dest` 头检测，否则可能误判主页面为子文档。Content Blocker 不支持。

---

## `$websocket` — WebSocket 请求

仅适用于 WebSocket 连接。

**限制：** Safari 需 macOS Monterey+，iOS 需 iOS 16+。Content Blocker 不支持。

---

## `$xmlhttprequest` — AJAX 请求

仅适用于通过 `XMLHttpRequest` 发送的 AJAX 请求。

**别名：** `$xhr`

**兼容性：** CoreLibs apps 在过滤旧浏览器时可能误判为 `$other` 或 `$script`，仅在支持 Fetch metadata 请求头的现代浏览器中可靠检测。

---

## 已移除的修饰符

### `$object-subrequest` 🚫
已移除，规则视为无效。曾用于匹配浏览器插件（Flash）的子请求。

### `$webrtc` 🚫
已移除，规则视为无效。如需抑制 WebRTC，请使用 `nowebrtc` 脚本片段。
