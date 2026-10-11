# 09. 上下文通信

用户脚本可以运行在 Tampermonkey 沙箱中、与页面 DOM 交互、通过 Tampermonkey 存储观察同一脚本的其他实例，并与页面或框架上下文交换消息。这些通道具有不同的信任和生命周期属性。将每条边界都视为输入验证边界，并将特权 API 保留在用户脚本内部。

## 选择通信通道

| 通道 | 适用场景 | 边界和限制 |
| --- | --- | --- |
| `GM_addValueChangeListener` | 在同一脚本的实例之间同步设置或状态 | 需要存储监听器 grant；接收 `remote` 标志，但不是事务或通用消息总线。 |
| `window.postMessage` | 页面 window 与另一个 window 或框架之间的结构化消息 | 验证 `event.source`、精确的 `event.origin`、消息形状和允许的消息类型。 |
| 自定义 DOM 事件 | 共享文档的代码之间的小型页面 DOM 信号 | 页面脚本可以观察事件；绝不要在 `detail` 中放凭据或特权函数句柄。 |
| 页面上下文桥接 | 调用或观察页面拥有的库或变量 | `unsafeWindow` 会跨入页面拥有的对象并扩大攻击面。优先使用范围狭窄的事件桥。 |
| 直接框架访问 | 与同源 iframe 通信 | 同源策略和框架生命周期适用；跨源框架需要消息传递和明确协作。 |

没有通用的跨脚本通道。Tampermonkey 存储通常限定在一个用户脚本内，因此一个脚本不应假设另一个脚本能读取其键。`postMessage` 可以到达参与通道的页面 window 或框架，但不会绕过来源策略，也不会让接收者变得可信。如果多个独立安装的脚本必须通信，应定义有文档记录、带版本的协议，并接受页面代码可能观察它。

## 同一脚本标签页同步

`GM_addValueChangeListener` 是同一用户脚本多个标签页共享设置的自然通道。回调接收 `key`、`oldValue`、`newValue` 和 `remote`。使用 `remote` 避免为当前实例已经应用的本地写入重复渲染，但不要假设存在顺序、锁、跨键原子更新或冲突解决。

```js
// ==UserScript==
// @name         Same-Script Tab Sync
// @namespace    https://userscripts.example.com/tab-sync
// @version      1.0.0
// @match        https://app.example.com/*
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_addValueChangeListener
// @grant        GM_removeValueChangeListener
// ==/UserScript==

(() => {
  'use strict';

  const key = 'tab-sync.enabled';
  let enabled = true;
  let listenerId = null;

  function readEnabled() {
    try {
      return GM_getValue(key, true) === true;
    } catch (error) {
      console.error('[tab-sync] read failed', error);
      return true;
    }
  }

  function render() {
    document.documentElement.dataset.tabSyncEnabled = String(enabled);
  }

  function setEnabled(nextEnabled) {
    const nextValue = nextEnabled === true;
    try {
      GM_setValue(key, nextValue);
      enabled = nextValue;
      render();
    } catch (error) {
      console.error('[tab-sync] write failed', error);
    }
  }

  function stop() {
    if (listenerId === null) return;
    try {
      GM_removeValueChangeListener(listenerId);
    } finally {
      listenerId = null;
    }
  }

  enabled = readEnabled();
  render();
  listenerId = GM_addValueChangeListener(key, (_key, _oldValue, newValue, remote) => {
    if (!remote) return;
    enabled = newValue === true;
    render();
  });
  window.addEventListener('pagehide', stop, { once: true });

  // 真实 UI 命令会调用 setEnabled(value)；这里有意不将其暴露给页面脚本，
  // 也不将其存储为 window 属性。
  void setEnabled;
})();
```

多个设置必须一起解释时，持久化带版本的聚合值。如果两个标签页可以编辑同一个值，明确是最后写入者胜出、经过验证的字段合并，还是需要显式 revision 检查。包括部分启动失败在内，都要在 teardown 时移除监听器。

## 验证 `postMessage`

来源检查必须精确。敏感消息不要使用 `'*'` 作为 `targetOrigin`，也不要仅因 `type` 字符串看起来熟悉就接受消息。检查发送方 window、精确来源、有界 payload 和预期协议版本。

```js
// 本示例中的页面 window 和用户脚本共享这一精确来源。
const TRUSTED_ORIGIN = 'https://app.example.com';
const PROTOCOL_VERSION = 1;

function isRecord(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function isSafeRequestMessage(value) {
  return (
    isRecord(value) &&
    value.channel === 'report-panel' &&
    value.version === PROTOCOL_VERSION &&
    value.type === 'request-refresh' &&
    typeof value.requestId === 'string' &&
    value.requestId.length > 0 &&
    value.requestId.length <= 80
  );
}

function onMessage(event) {
  if (event.source !== window || event.origin !== TRUSTED_ORIGIN) return;
  if (!isSafeRequestMessage(event.data)) return;

  // 在用户脚本内部执行特权工作。不要将 GM_xmlhttpRequest 函数、token
  // 或存储值发送给页面。
  refreshReport().then((summary) => {
    window.postMessage({
      channel: 'report-panel',
      version: PROTOCOL_VERSION,
      type: 'refresh-result',
      requestId: event.data.requestId,
      ok: true,
      summary: { count: summary.count },
    }, TRUSTED_ORIGIN);
  }).catch(() => {
    window.postMessage({
      channel: 'report-panel',
      version: PROTOCOL_VERSION,
      type: 'refresh-result',
      requestId: event.data.requestId,
      ok: false,
    }, TRUSTED_ORIGIN);
  });
}

window.addEventListener('message', onMessage);
window.addEventListener('pagehide', () => {
  window.removeEventListener('message', onMessage);
}, { once: true });
```

接收代码仍必须在渲染前验证 `refreshReport()` 返回的值。当页面代码可以反复触发协议时，消息协议应限制大小和速率。如果受信页面来源可能在导航期间变化，应根据当前路由重新计算明确允许的来源，并拒绝过期消息。

## 自定义事件和页面上下文桥接

当双方共享文档时，自定义事件很方便，但页面可以派发相同事件并检查事件数据。使用带命名空间的事件名和普通数据 `detail` 对象，并像处理 `postMessage` 一样验证 detail。

`unsafeWindow` 暴露的是页面的 `window`，而不是扩展 window。检查页面拥有的库可能需要它，但页面脚本可以影响页面拥有的对象，也可能干扰桥接。保持桥接范围狭窄：通过事件或消息交换不可变、经过 schema 检查的数据，并将所有 `GM_*` 调用、token、存储和请求句柄保留在用户脚本内部。不要将特权函数（例如 `window.myUserscriptFetch = ...`）附加到页面。

Tampermonkey 的 `@sandbox` 元数据可以选择执行上下文，文档将其标记为版本特定（`4.18+`）。不要把它当作跨处理器或浏览器的可移植保证。检查已安装版本，并在目标环境中测试确切的桥接。

## iframe 和 window 边界

iframe 有自己的文档、URL、事件监听器和生命周期。只应在顶层页面运行的脚本可以声明 `@noframes`；增强框架的脚本必须匹配框架 URL，并使用框架本地选择器。`window.top`、`window.parent` 和 `event.source` 不可与当前 window 混用。

对于同源框架，直接 DOM 或 `contentWindow` 访问可能可行，但要等待框架加载，并在其被替换时清理。对于跨源框架，使用带精确目标来源的 `postMessage`，并要求框架配合。不要因为框架由信任的页面嵌入就降低验证要求。

## 通信审查清单

- [ ] 同一脚本标签页状态使用带版本的值，并移除变更监听器。
- [ ] 跨脚本假设明确；不把存储当作通用总线。
- [ ] `postMessage` 检查精确的 `event.origin`、`event.source`、协议版本、类型和 payload 形状。
- [ ] 敏感消息使用精确的 `targetOrigin`，绝不使用 `'*'`。
- [ ] 自定义事件 detail 只包含有界普通数据，不含凭据或特权函数。
- [ ] 页面上下文桥接将 GM API、token 和存储保持为私有。
- [ ] `unsafeWindow` 和 `@sandbox` 的使用有理由且经过版本测试。
- [ ] iframe 行为区分顶层 window、同源框架和跨源框架。
- [ ] teardown 时移除监听器、观察器、计时器和桥接钩子。

## 官方参考

- [Tampermonkey `GM_addValueChangeListener`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values#api:GM_addValueChangeListener)
- [Tampermonkey `GM_removeValueChangeListener`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values#api:GM_removeValueChangeListener)
- [Tampermonkey `unsafeWindow`](https://www.tampermonkey.net/documentation.php?locale=en&q=unsafeWindow)
- [Tampermonkey `@sandbox`](https://www.tampermonkey.net/documentation.php?locale=en&q=sandbox)
- [Tampermonkey `@noframes`](https://www.tampermonkey.net/documentation.php?locale=en&q=noframes)
- [MDN `Window.postMessage`](https://developer.mozilla.org/en-US/docs/Web/API/Window/postMessage)
- [MDN 同源策略](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy)
- [MDN `Window: message` 事件](https://developer.mozilla.org/en-US/docs/Web/API/Window/message_event)
