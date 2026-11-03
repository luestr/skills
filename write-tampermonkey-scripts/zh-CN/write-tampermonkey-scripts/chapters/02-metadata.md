# 02. 用户脚本元数据

元数据块是脚本的执行契约。Tampermonkey 会在执行脚本主体前读取它，因此 URL 范围、时机、特权、依赖和更新行为必须在运行时代码能够弥补错误之前就正确。

权威参考是 [Tampermonkey 文档](https://www.tampermonkey.net/documentation.php?locale=en)。下面的链接使用其中的元数据条目。

## 指令参考

| 指令 | 用途和实践指南 |
| --- | --- |
| `@name` | 在 Tampermonkey 中显示的可读脚本名称。保持稳定且具有描述性。参见 [`@name`](https://www.tampermonkey.net/documentation.php?locale=en&q=name#meta:name)。 |
| `@namespace` | 与 `@name` 一起标识脚本，并帮助区分同名的无关脚本。使用由你控制的稳定命名空间。参见 [`@namespace`](https://www.tampermonkey.net/documentation.php?locale=en&q=name#meta:namespace)。 |
| `@version` | 用于更新比较和显示的版本。行为、权限、依赖或存储数据处理发生变化时递增。参见 [`@version`](https://www.tampermonkey.net/documentation.php?locale=en&q=version)。 |
| `@description` | 在脚本管理界面显示的简短说明。说明目标和用户可见行为，不要承诺不支持的范围。参见 [`@description`](https://www.tampermonkey.net/documentation.php?locale=en&q=description)。 |
| `@author` | 发布者或维护者身份。保持准确；用户需要报告问题时添加支持 URL。参见 [`@author`](https://www.tampermonkey.net/documentation.php?locale=en&q=author)。 |
| `@match` | 脚本可以运行的页面 URL 模式。优先使用精确的协议、主机、子域名和路径模式。参见 [`@match`](https://www.tampermonkey.net/documentation.php?locale=en&q=include#meta:match)。 |
| `@include` | 较旧或更灵活的 URL 匹配方式。可使用通配符或正则表达式形式，但更容易超出预期范围。普通 URL 范围优先使用 `@match`。参见 [`@include`](https://www.tampermonkey.net/documentation.php?locale=en&q=include#meta:include)。 |
| `@exclude` | 从 `@match` 或 `@include` 范围中移除 URL。用于明确例外，但不要用宽泛 include 加很长排除列表来代替精确匹配。参见 [`@exclude`](https://www.tampermonkey.net/documentation.php?locale=en&q=meta:exclude)。 |
| `@noframes` | 阻止脚本在匹配页面范围内的框架中执行。顶层文档是唯一目标时使用，并在目标浏览器和 Tampermonkey 版本中验证框架行为。参见 [`@noframes`](https://www.tampermonkey.net/documentation.php?locale=en&q=meta:noframes)。 |
| `@run-at` | 最早注入时机：`document-start`、`document-body`、`document-end`、`document-idle` 或受支持的特殊模式。它不保证应用已经完成渲染。参见 [`@run-at`](https://www.tampermonkey.net/documentation.php?locale=en&q=run_at)。 |
| `@grant` | 将 Tampermonkey API、`unsafeWindow` 和选定的强大 window 函数列入白名单。只声明脚本实际调用的内容。参见 [`@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)。 |
| `@require` | 在脚本主体前加载外部 JavaScript 依赖。固定依赖 URL 或版本，审查其源代码，并将其视为与脚本具有相同权限的可信代码。参见 [`@require`](https://www.tampermonkey.net/documentation.php?locale=en&q=externals#meta:require)。 |
| `@resource` | 向脚本提供命名的外部资源。使用对应的资源 API（如 `GM_getResourceText` 或 `GM_getResourceURL`）读取，并在需要时声明 API grant。参见 [`@resource`](https://www.tampermonkey.net/documentation.php?locale=en&q=externals#meta:resource)。 |
| `@connect` | 为 `GM_xmlhttpRequest` 将域名列入白名单。严格列出已知域名，并考虑重定向，因为初始 URL 和最终 URL 都会检查。参见 [`@connect`](https://www.tampermonkey.net/documentation.php?locale=en&q=connect)。 |
| `@updateURL` | 检查更新元数据的 URL。这是部署决策；使用提供预期用户脚本元数据的稳定端点。参见 [`@updateURL`](https://www.tampermonkey.net/documentation.php?locale=en&q=update_url#meta:updateURL)。 |
| `@downloadURL` | 下载更新脚本的 URL。除非有明确的部署拆分，否则使其与已发布脚本和更新 URL 保持一致。参见 [`@downloadURL`](https://www.tampermonkey.net/documentation.php?locale=en&q=update_url#meta:downloadURL)。 |
| `@supportURL` | 向用户显示的帮助、问题或联系 URL。应说明如何报告失败和兼容性信息。参见 [`@supportURL`](https://www.tampermonkey.net/documentation.php?locale=en&q=update_url#meta:supportURL)。 |
| `@sandbox` | Tampermonkey `4.18+` 引入的版本特定功能。表示脚本是否需要 `raw`、`JavaScript` 或 `DOM` 访问。验证安装环境中的可用性和实际行为。参见 [`@sandbox`](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox)。 |

Tampermonkey 还记录了 `@run-in`、`@tag` 和 `@webRequest` 等其他元数据，但它们依赖版本或具体功能，超出本章的最小契约。没有明确需求和版本检查时不要添加它们。

## 范围与最小权限

`@match` 控制 Tampermonkey 认为脚本有资格运行的位置。当行为依赖路径、查询、页面状态或已认证账户时，它不能替代运行时检查。注入后使用代码验证这些细节。

优先使用：

```text
https://app.example.com/orders/*
```

而不是：

```text
*://*/*
```

当标准匹配模式可以表达目标时，也优先使用 `@match` 而不是宽泛的 `@include`。一个应用主机足够时，不要匹配整个父域名。对打印视图等少量明确例外使用 `@exclude`。

最小 grant 能降低风险，因为它们使特权行为可见，减少意外代码的影响，并使审查更容易。普通浏览器 API 不需要 Tampermonkey grant。调用 `GM_addStyle` 需要 `@grant GM_addStyle`；调用 `GM_getValue` 需要 `@grant GM_getValue`；调用 `unsafeWindow` 需要 `@grant unsafeWindow`。明确声明每个 API，并移除未使用的 grant。

不要把缺少 `@grant` 与 `@grant none` 混为一谈。Tampermonkey 对空 grant 列表和 `@grant none` 的说明不同。`@grant none` 会禁用沙箱，使 `GM_*` API 不可用（`GM_info` 除外）；因此它是有意选择页面上下文，而不是请求无权限的通用方式。

## 完整示例块

这是一个完整、有效的示例，脚本为订单页面添加样式、存储本地偏好，并读取一个已知 API 域名。URL 仅为占位符。移除改造后脚本不使用的指令和 grant。

```js
// ==UserScript==
// @name         Order Page Helper
// @namespace    https://userscripts.example.com/order-page-helper
// @version      1.2.0
// @description  Adds a small, persistent helper to the order page.
// @author       Example Maintainer
// @match        https://app.example.com/orders/*
// @exclude      https://app.example.com/orders/print/*
// @noframes
// @run-at       document-idle
// @grant        GM_addStyle
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_xmlhttpRequest
// @require      https://cdn.example.com/order-helper@1.2.0/dist/helper.min.js
// @resource     helper-theme https://cdn.example.com/order-helper@1.2.0/theme.css
// @connect      api.example.com
// @updateURL    https://updates.example.com/order-page-helper.meta.js
// @downloadURL  https://updates.example.com/order-page-helper.user.js
// @supportURL   https://support.example.com/order-page-helper
// @sandbox      DOM
// ==/UserScript==
```

`@sandbox DOM` 是版本特定功能（`4.18+`），只有当脚本经过测试的行为确实需要此访问权限时才应保留。如果脚本使用资源文本或资源 URL，请按需添加 `@grant GM_getResourceText` 或 `@grant GM_getResourceURL`。如果使用 `GM.getValue` 等异步命名空间 API，请声明已安装 Tampermonkey 版本所需的命名空间 grant，并在该版本中测试。

示例有意包含多种能力，以展示完整块的形状。真实脚本不需要 `@require`、`@resource`、`@connect` 和未使用的 grant 时应将其移除。

## 常见错误

- 因为没有分析目标 URL 就匹配 `*://*/*`。这会在无关网站上运行。
- 认为 `@match` 可以区分查询字符串或 URL 哈希。应在代码中检查这些值。
- 使用 `@include` 正则表达式却没有测试端口、子域名或包含相似字符串的 URL 等边界情况。
- 没有确认所需元素确实位于框架中就添加 `@noframes`。
- 将 `document-idle` 当作“SPA 已就绪”，而不是注入时机选择。
- 添加 `@grant GM_xmlhttpRequest` 却没有范围狭窄的 `@connect` 列表，或没有记录理由就添加 `@connect *`。
- 引入内容可能在脚本版本不变时发生变化的浮动或未固定版本的 `@require` 依赖。
- 声明资源却忘记匹配的 `GM_getResourceText` 或 `GM_getResourceURL` grant。
- 使用 `@grant none` 后仍期待 `GM_getValue`、`GM_addStyle` 或其他 `GM_*` API 存在。
- 发布提供与可下载脚本不一致的元数据文件的更新 URL。
- 添加 `@sandbox` 却没有说明最低 Tampermonkey 版本，也没有测试浏览器特定的回退行为。

## 验证清单

- [ ] 元数据块位于文件开头，并使用精确的 `// ==UserScript==` 和 `// ==/UserScript==` 标记。
- [ ] 每个 `@match` 都尽可能符合需求的最窄范围。
- [ ] `@exclude` 条目具体且经过测试。
- [ ] 框架行为和 `@run-at` 是有意选择的。
- [ ] 每次 Tampermonkey API 调用都有所需的 `@grant`。
- [ ] `@connect` 仅包含所需域名。
- [ ] 外部代码和资源已固定版本、审查并记录。
- [ ] 版本特定指令说明了最低版本和回退行为。
- [ ] 更新、下载和支持 URL 指向预期部署。

## 官方参考

- [Tampermonkey 元数据文档](https://www.tampermonkey.net/documentation.php?locale=en)
- [Tampermonkey `@match` 和 `@include`](https://www.tampermonkey.net/documentation.php?locale=en&q=include)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [Tampermonkey `@sandbox`（`4.18+`）](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox)
- [Tampermonkey 更新 URL](https://www.tampermonkey.net/documentation.php?locale=en&q=update_url)
