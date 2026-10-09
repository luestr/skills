# 10. 安全与隐私

用户脚本把页面控制的输入与扩展介导的能力结合起来。脚本运行期间，页面可以改变 DOM、导航、时机和 JavaScript 对象。因此，安全取决于减少权限、验证边界、限制披露，并让副作用对用户可见。

## 先建立威胁模型

编写脚本前确认：

- 哪些页面来源和 URL 路径可以启动脚本？
- 哪些页面文本、属性、URL、表单值、消息、框架和网络响应是不可信的？
- 哪些能力可能披露数据或造成外部副作用？
- 哪些数据敏感、可以存放在哪里、应保留多长时间？
- 被入侵的页面、第三方库、重定向或更新后的 API 是否可以观察或影响操作？
- 在下载、外部请求、剪贴板写入或账户操作之前，用户会看到什么？

答案应决定元数据，而不是反过来。只添加本地按钮的脚本不应需要网络、存储、剪贴板或 `unsafeWindow`（页面 `window`）访问。

## 最小权限元数据

针对实际协议、主机和路由使用精确的 `@match` 条目。避免 `@include *`、宽泛主机模式和不必要的 `@noframes` 例外。每使用一个特权 API 就添加一个 `@grant`，重构后移除 grant。跨源请求使用精确的 `@connect` 主机，绝不要把 `@connect *` 当成无害便利。

```js
// ==UserScript==
// @name         Narrowly Scoped Enhancement
// @namespace    https://userscripts.example.com/narrow-enhancement
// @version      1.0.0
// @match        https://shop.example.com/products/*
// @grant        none
// @noframes
// ==/UserScript==
```

只有脚本使用浏览器 API 且不使用 Tampermonkey API 时，`@grant none` 才合适。如果脚本调用 `GM_*` API，应明确声明匹配的 grant。`@sandbox` 和其他元数据条目依赖版本；记录最低版本并测试实际执行上下文，不要声称普遍支持。

## DOM 注入和 XSS

页面文本和属性即使看起来像标签也不可信。优先使用 `textContent`、`createElement` 和明确属性赋值。对于来自页面、网络响应、存储、查询字符串或消息的值，避免使用 `innerHTML`。如果必须解析可信模板，应让动态值远离 HTML 源，并在插入前使用经过审查的清理器清理结果。

不要将不可信字符串变成选择器、CSS、URL 或 JavaScript。如果选择器必须包含标识符，应验证字符集和长度，或在浏览器支持和选择器语义合适时使用 `CSS.escape`。绝不要用 `eval`、`Function` 或字符串拼接的事件处理器执行页面文本。

```js
const productStatusOwnerSelector = ':scope > [data-tm-product-status-region-owner="true"]';

function renderProductStatus(host, product) {
  let region = host.querySelector(productStatusOwnerSelector);
  if (!region) {
    region = document.createElement('div');
    region.dataset.tmProductStatusRegionOwner = 'true';
    region.setAttribute('aria-live', 'polite');
    host.append(region);
  }

  const status = document.createElement('span');
  status.className = 'tm-product-status';
  status.textContent = typeof product.status === 'string'
    ? product.status.slice(0, 120)
    : 'Status unavailable';

  const detailsUrl = safeProductUrl(product.detailsUrl);
  if (detailsUrl !== null) {
    const detailsLink = document.createElement('a');
    detailsLink.textContent = 'View details';
    detailsLink.href = detailsUrl;
    detailsLink.rel = 'noopener noreferrer';
    detailsLink.target = '_blank';
    region.replaceChildren(status, detailsLink);
    return;
  }

  const unavailable = document.createElement('span');
  unavailable.textContent = 'Details are unavailable for this product.';
  unavailable.dataset.state = 'unavailable';
  region.replaceChildren(status, unavailable);
}

function safeProductUrl(value) {
  if (typeof value !== 'string') return null;
  try {
    const url = new URL(value, location.href);
    if (url.protocol !== 'https:' || url.origin !== location.origin || !url.pathname.startsWith('/products/')) return null;
    return url.href;
  } catch {
    return null;
  }
}
```

无效 URL 会产生解释性文本，而不是活动链接。`host` 由调用方提供，可能包含页面拥有的子节点，因此 `renderProductStatus` 只创建或复用其直接的 `data-tm-product-status-region-owner="true"` 子节点，并且只在这个脚本命名空间拥有的区域内调用 `replaceChildren`，绝不会清空页面拥有的宿主本身，也不会复用通用 status 标记。如果设计需要该状态下的控件，应渲染带 `disabled` 的禁用按钮，而不是赋值 `'#'`。渲染可能异常大的响应前，始终限制文本长度和数组数量。

## URL、请求和披露

打开标签页、获取资源、设置图片源或下载文件前，验证 URL 协议、来源、路径和所需标识符。除非功能明确需要其他协议，否则只接受 `https:`。导航和资源属性要拒绝 `javascript:`、`data:`、`file:` 和意外的自定义协议。

跨源披露不止包括响应 body。查询参数、headers、cookies、referrer、下载文件名、日志和时序都可能泄露账户或页面信息。不要仅因为 `GM_xmlhttpRequest` 能访问某服务就向其发送页面机密。从 URL 和错误消息中移除 token，使用最小请求 payload，并在 API 或处理器支持重定向时验证最终 URL。

## 存储和敏感值

Tampermonkey 存储限定在用户脚本内，但不是安全机密库。除非风险、保留期限和用户同意已经明确审查，否则不要存储密码、长期 bearer token、会话 cookie、私有文档或完整页面快照。只存储尽可能少的非敏感设置，读取时验证，并为迁移包含 schema 版本。

避免记录存储值。调试语句可能将机密泄露到扩展日志、页面控制台、问题报告或屏幕录制中。诊断需要标识符时，记录短的不可逆标签或经过脱敏的前缀。

## 供应链和 `@require`

`@require` 脚本以用户脚本的权限执行。审查其源代码、更新策略、所有权和传递依赖。固定到经过审查的版本；当稳定哈希可用时，使用 Tampermonkey 文档记录的 Subresource Integrity 形式：

```js
// @require      https://cdn.example.com/reviewed-lib@1.4.2/lib.min.js#sha256-BASE64_HASH
```

用发布流程产生的真实哈希替换 `BASE64_HASH`。示意占位符不是有效的完整性检查。主动升级时重新审查哈希；如果小型本地实现更清晰且风险更低，则完全移除依赖。

同样的审查适用于 `@resource` 内容、远程配置和由响应驱动的代码。绝不要执行从请求或页面字段接收的 JavaScript。内容安全策略可以阻止某些页面上下文操作，但 CSP 不是清理器，不应作为脚本的主要防御手段。

## `unsafeWindow`、下载和同意

`unsafeWindow` 提供页面的 `window`，因此会跨入页面代码控制的对象。仅在范围狭窄且有文档的集成中使用。将特权函数、请求句柄、存储访问和凭据保留在用户脚本沙箱中。通过经过验证的事件或消息通道交换经过 schema 检查的普通数据。

通过 `GM_download` 下载（需要 `@grant GM_download`）、剪贴板写入、外部请求和账户变更都是用户可见的副作用。当触发方式不明显时，需要明确操作或确认，显示目标或文件名，并报告成功或失败。不要在启动时静默上传页面内容、自动下载大文件或复制机密。

## 威胁模型清单

- [ ] `@match` 对协议、主机、路径、框架范围和生命周期都足够精确。
- [ ] `@grant` 只列出实际使用的 API；`@connect` 只列出所需主机。
- [ ] 页面文本和属性不使用不安全 HTML 或字符串构建的处理器插入。
- [ ] 选择器、URL、协议、路径和长度在使用前经过验证。
- [ ] 网络 payload、headers、重定向和错误不会披露页面机密。
- [ ] 存储值尽可能非敏感，经过 schema 检查，且不记录日志。
- [ ] `@require` 和 `@resource` 来源已固定、审查，并在可行时进行完整性保护。
- [ ] `unsafeWindow` 和页面桥接不暴露特权函数或凭据。
- [ ] 下载、剪贴板写入、外部请求和账户操作具有透明同意流程。
- [ ] 失败状态保护隐私，不显示原始响应 body 或机密。
- [ ] 安全假设已在目标浏览器和 Tampermonkey 版本中测试。

## 官方参考

- [Tampermonkey `@match`](https://www.tampermonkey.net/documentation.php?locale=en&q=match)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [Tampermonkey `@connect`](https://www.tampermonkey.net/documentation.php?locale=en&q=connect)
- [Tampermonkey `unsafeWindow`](https://www.tampermonkey.net/documentation.php?locale=en&q=unsafeWindow)
- [Tampermonkey Subresource Integrity](https://www.tampermonkey.net/documentation.php?locale=en&q=sri)
- [Tampermonkey `@require`](https://www.tampermonkey.net/documentation.php?locale=en&q=externals)
- [Tampermonkey 常见问题：所需权限](https://www.tampermonkey.net/faq.php?locale=en&q=Q304)
- [MDN 跨站脚本攻击](https://developer.mozilla.org/en-US/docs/Glossary/Cross-site_scripting)
- [MDN `innerHTML` 安全注意事项](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML#security_considerations)
