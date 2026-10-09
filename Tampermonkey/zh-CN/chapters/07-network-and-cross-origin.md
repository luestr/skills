# 07. 网络与跨源请求

网络访问是一条边界，而不只是另一个数据源。页面的浏览器 API 受页面源和 CORS 策略约束。Tampermonkey 的 `GM_xmlhttpRequest` 由 Tampermonkey 后台上下文派发，可以发起获准的跨源请求，但仍然需要明确的主机权限和谨慎的响应处理。

## 选择请求 API

当请求是同源，或目标服务有意支持页面的 CORS 策略时，使用原生 `fetch` API。它是浏览器 API，不需要 Tampermonkey grant。用户脚本需要获准的跨源请求，而页面 CORS 策略会阻止该请求时，使用 `GM_xmlhttpRequest`。

| 需求 | API | 权限和说明 |
| --- | --- | --- |
| 同源请求 | 浏览器 `fetch` | 不需要 Tampermonkey grant；应用普通浏览器 CORS 和 CSP 规则。 |
| 获准的跨源请求 | `GM_xmlhttpRequest` | 添加 `@grant GM_xmlhttpRequest` 和精确的 `@connect` 主机。 |
| 基于 Promise 的请求 | `GM.xmlHttpRequest` | 采用前检查已安装的 Tampermonkey 版本和命名空间 grant 语法。文档名称中的 `H` 为大写。 |

`GM_xmlhttpRequest` 不会让不可信 URL 变安全。宽泛的 `@connect *` 会扩大权限边界，使输入验证漏洞更加严重。声明功能实际需要的最小主机集合。Tampermonkey 可能请求用户批准新遇到的主机，因此意外的权限提示是需要处理的行为，而不是无限静默重试的理由。

## 元数据和请求生命周期

以下元数据是本示例回调 API 所需的最小集合。`@connect` 值是主机允许列表条目，不能替代 URL 验证。

```js
// ==UserScript==
// @name         Approved API Request Example
// @namespace    https://userscripts.example.com/approved-request
// @version      1.0.0
// @match        https://app.example.com/reports/*
// @grant        GM_xmlhttpRequest
// @connect      api.example.com
// ==/UserScript==
```

常见回调含义不同：

- `onload` 表示收到了响应，不表示 HTTP 状态成功。自行检查 `status`。
- `onerror` 表示请求无法正常完成。显示可恢复状态，避免暴露原始响应数据。
- `ontimeout` 是有界失败；可能适合重试时，应单独报告。
- `onabort` 表示脚本或用户取消了请求。不要为有意取消显示服务器错误。
- `onprogress` 和 `onreadystatechange` 是可选的检测钩子。不要对每个进度事件执行昂贵渲染。
- 返回的请求句柄暴露 `abort()`。面板拥有请求期间保留它，并在 teardown 或离开路由时调用。

使用响应数据前验证以下所有内容：

1. 最终 URL 必须存在、是字符串，并匹配固定获准来源、端点路径、查询和哈希策略。
2. 状态必须在接受范围内，通常为 `200 <= status < 300`。
3. body 存在，并且能解析为预期格式。
4. 解析后的值具有所需的形状、类型、边界和标识符。

要求 `finalUrl` 为字符串；当它缺失、格式错误，或不在固定获准来源、精确端点路径、查询或哈希策略内时，拒绝响应。当响应 headers 提供 `Content-Type` 时，只接受 `application/json` 或 `application/*+json` 等 JSON 媒体类型。定义清晰的最大响应大小，并在 `JSON.parse` 前测量 body；超大 body 必须以有界且对用户安全的消息失败。

不要把 `200` 响应当作可信 HTML。使用 `textContent` 渲染文本，从已验证的值创建属性；如果意外字段会改变安全敏感操作，则拒绝这些字段。

## 按约定声明类型的辅助函数

JavaScript 不会在运行时强制请求和响应类型。JSDoc 类型为编辑器和静态工具记录契约；运行时检查仍然必要。此辅助函数只接受固定 API 来源，限制重试次数，验证 JSON，并向调用方提供单一的成功或失败结果。

```js
// ==UserScript==
// @name         Typed-by-Convention Request Helper
// @namespace    https://userscripts.example.com/request-helper
// @version      1.0.0
// @match        https://app.example.com/reports/*
// @grant        GM_xmlhttpRequest
// @connect      api.example.com
// ==/UserScript==

(() => {
  'use strict';

  /** @typedef {{ id: string, label: string, value: number }} ReportRow */
  /** @typedef {{ rows: ReportRow[] }} ReportResponse */
  /** @typedef {{ ok: true, value: ReportResponse } | { ok: false, error: string, retryable: boolean }} RequestResult */

  const API_ORIGIN = 'https://api.example.com';
  const API_PATH = '/v1/reports/current';
  const REQUEST_TIMEOUT_MS = 8000;
  const MAX_ATTEMPTS = 3;
  const RETRY_DELAY_MS = 400;
  const MAX_RESPONSE_BYTES = 1_000_000;

  function isRecord(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }

  /** @param {unknown} value @returns {ReportResponse} */
  function parseReportResponse(value) {
    if (!isRecord(value) || !Array.isArray(value.rows)) {
      throw new Error('Response schema is invalid');
    }

    const rows = value.rows.map((row) => {
      if (!isRecord(row) || typeof row.id !== 'string' || row.id.length > 100) {
        throw new Error('Response row id is invalid');
      }
      if (typeof row.label !== 'string' || row.label.length > 500) {
        throw new Error('Response row label is invalid');
      }
      if (typeof row.value !== 'number' || !Number.isFinite(row.value)) {
        throw new Error('Response row value is invalid');
      }
      return { id: row.id, label: row.label, value: row.value };
    });

    return { rows };
  }

  /** @returns {string} */
  function makeApiUrl() {
    const url = new URL(API_PATH, API_ORIGIN);
    if (url.origin !== API_ORIGIN || url.pathname !== API_PATH || url.search !== '' || url.hash !== '') {
      throw new Error('Request URL is outside the approved endpoint');
    }
    return url.href;
  }

  /** @param {unknown} response @param {URL} expectedUrl @returns {boolean} */
  function hasApprovedFinalUrl(response, expectedUrl) {
    if (!isRecord(response) || typeof response.finalUrl !== 'string') return false;
    try {
      const finalUrl = new URL(response.finalUrl);
      return finalUrl.origin === API_ORIGIN
        && finalUrl.pathname === expectedUrl.pathname
        && finalUrl.search === expectedUrl.search
        && finalUrl.hash === expectedUrl.hash;
    } catch {
      return false;
    }
  }

  /** @param {unknown} response @returns {boolean} */
  function hasJsonContentType(response) {
    if (!isRecord(response) || typeof response.responseHeaders !== 'string') return true;
    const contentTypeLine = response.responseHeaders
      .split(/\r?\n/)
      .find((line) => /^content-type\s*:/i.test(line));
    if (!contentTypeLine) return true;
    const contentType = contentTypeLine
      .slice(contentTypeLine.indexOf(':') + 1)
      .trim()
      .split(';', 1)[0]
      .toLowerCase();
    return contentType === 'application/json' || contentType.endsWith('+json');
  }

  /** @param {string} url @returns {Promise<RequestResult>} */
  function requestReport(url) {
    return new Promise((resolve) => {
      let settled = false;
      let requestHandle = null;
      const finish = (result) => {
        if (settled) return;
        settled = true;
        resolve(result);
      };

      requestHandle = GM_xmlhttpRequest({
        method: 'GET',
        url,
        timeout: REQUEST_TIMEOUT_MS,
        headers: { Accept: 'application/json' },
        onload(response) {
          if (response.status < 200 || response.status >= 300) {
            finish({ ok: false, error: `Server returned HTTP ${response.status}`, retryable: response.status >= 500 });
            return;
          }
          const expectedUrl = new URL(url);
          if (!hasApprovedFinalUrl(response, expectedUrl)) {
            finish({ ok: false, error: 'Response final URL is outside the approved API', retryable: false });
            return;
          }
          if (!hasJsonContentType(response)) {
            finish({ ok: false, error: 'Response content type is not JSON', retryable: false });
            return;
          }

          try {
            const raw = response.responseText;
            if (typeof raw !== 'string') {
              finish({ ok: false, error: 'Response body is not text', retryable: false });
              return;
            }
            const responseBytes = new TextEncoder().encode(raw).byteLength;
            if (responseBytes > MAX_RESPONSE_BYTES) {
              finish({ ok: false, error: `Response body exceeds ${MAX_RESPONSE_BYTES} bytes`, retryable: false });
              return;
            }
            const parsed = JSON.parse(raw);
            finish({ ok: true, value: parseReportResponse(parsed) });
          } catch (error) {
            finish({ ok: false, error: `Invalid JSON response: ${String(error.message || error)}`, retryable: false });
          }
        },
        onerror() {
          finish({ ok: false, error: 'The request could not reach the service', retryable: true });
        },
        ontimeout() {
          finish({ ok: false, error: 'The service did not respond in time', retryable: true });
        },
        onabort() {
          finish({ ok: false, error: 'The request was cancelled', retryable: false });
        },
      });

      // 在闭包中保留句柄，以便更大的控制器能够暴露 abort 路径。
      void requestHandle;
    });
  }

  /** @returns {Promise<RequestResult>} */
  async function requestWithRetry() {
    const url = makeApiUrl();
    let lastResult = { ok: false, error: 'No request was attempted', retryable: true };

    for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
      lastResult = await requestReport(url);
      if (lastResult.ok || !lastResult.retryable || attempt === MAX_ATTEMPTS) return lastResult;
      await new Promise((resolve) => window.setTimeout(resolve, RETRY_DELAY_MS * attempt));
    }

    return lastResult;
  }

  function showResult(result) {
    const status = document.querySelector('[data-report-status]');
    if (!status) return;
    status.textContent = result.ok ? `Loaded ${result.value.rows.length} rows` : `Report unavailable: ${result.error}`;
    status.dataset.state = result.ok ? 'ready' : 'error';
  }

  requestWithRetry().then(showResult).catch((error) => {
    showResult({ ok: false, error: 'Unexpected request failure', retryable: false });
    console.error('[request-helper] unexpected failure', error);
  });
})();
```

示例中的 `requestHandle` 只在 promise 内保留，用于展示 abort 句柄应位于何处。生产控制器应将该句柄存入自身状态，并在面板移除时 abort。不要把 bearer token 放进 URL、在回调中记录 token，或将其复制到页面可见的 DOM。优先设计通过获准的浏览器凭据或短期、范围严格的凭据进行认证的服务器；正确选择取决于服务和浏览器权限。

## 状态、超时、abort 和重试策略

重试需要理由和预算。使用短暂退避重试瞬时传输失败、超时和选定的 `5xx` 响应。不要重试格式错误的 JSON、`4xx` 授权错误或用户取消，除非用户明确要求重试。在许多安装同时重试时加入 jitter。

遵守服务速率限制：

- 不要对每次 DOM mutation 或按键进行轮询。
- 当允许数据过期时，在明确且有界的生命周期内缓存结果。
- API 提供文档化的 `Retry-After` 信息时遵守它。
- 除非并发请求是有意设计的，否则每个路由或键只允许一个进行中的请求。
- 用户离开路由时取消路由专属工作。

UI 应区分加载中、就绪、空和错误状态。失败消息应说明下一步安全操作，例如重试、检查权限或稍后返回。不应要求用户将 token 粘贴到页面字段，也不应暴露原始响应 body。

## 凭据和 CORS 边界

`GM_xmlhttpRequest` 和 `fetch` 的凭据行为并不相同。只有在服务、浏览器、Tampermonkey 模式和用户权限都支持时，请求才可能包含 cookies、credentials 或自定义 headers。将 `anonymous`、`user`、`password` 和 `cookie` 请求选项视为安全敏感项。不要向功能不需要的主机发送页面 cookies 或账户标识符。

跨源权限不等于服务器授权。`@connect api.example.com` 允许用户脚本请求该主机；它不保证端点接受请求、cookies 可用或重定向安全。当重定向可能把数据移到另一来源时，验证最终 URL，并保持获准主机列表狭窄。

## 网络审查清单

- [ ] 当页面的同源和 CORS 策略足够时使用原生 `fetch`。
- [ ] `GM_xmlhttpRequest` 具有 `@grant GM_xmlhttpRequest` 和精确的 `@connect` 主机。
- [ ] URL 构造会拒绝意外来源、协议和路径。
- [ ] `onload` 拒绝缺失或未获准的最终 URL，然后验证精确的最终 URL 来源/路径/查询/哈希、状态、可用时的 JSON content type、解析前的有界 body 大小和响应形状。
- [ ] 超时、abort、传输错误和用户取消有不同处理。
- [ ] 重试次数有限、受速率限制，并且仅用于可重试失败。
- [ ] UI 或路由消失时取消进行中的请求。
- [ ] 不记录或披露凭据、token、cookies 和页面机密。
- [ ] 加载中、空、成功和失败状态可见且可恢复。
- [ ] 根据已安装 Tampermonkey 文档验证版本特定的命名空间 API。

## 官方参考

- [Tampermonkey `GM_xmlhttpRequest`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_xmlhttpRequest)
- [Tampermonkey `@connect`](https://www.tampermonkey.net/documentation.php?locale=en&q=connect)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [Tampermonkey 常见问题：运行时主机权限](https://www.tampermonkey.net/faq.php?locale=en&q=Q306)
- [MDN CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [MDN `fetch`](https://developer.mozilla.org/en-US/docs/Web/API/Window/fetch)
