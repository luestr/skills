# 08. UI 与实用 API

Tampermonkey 实用 API 适合脚本拥有的命令、通知、剪贴板操作、下载、资源访问和打开相关页面。它们是特权浏览器扩展 API，因此每个示例都应只声明实际使用的 grant；如果原生浏览器 API 无需额外权限就能提供所需行为，仍应优先使用原生 API。

## API 范围和 grant

| 需求 | API | 所需 grant 和重要行为 |
| --- | --- | --- |
| 用户命令 | `GM_registerMenuCommand` | `@grant GM_registerMenuCommand`；页面未打开时也应保持命令有用。 |
| 通知 | `GM_notification` | `@grant GM_notification`；支持失败或权限被拒绝状态。 |
| 写入剪贴板 | `GM_setClipboard` | `@grant GM_setClipboard`；复制敏感内容前请求用户意图。 |
| 文件下载 | `GM_download` | `@grant GM_download`；验证 URL 和文件名，并处理 `onerror`。 |
| 新标签页 | `GM_openInTab` | `@grant GM_openInTab`；仅打开经过验证且预期的目标。 |
| 内置资源文本或 URL | `GM_getResourceText`、`GM_getResourceURL` | 匹配的 grant，以及 `@resource name url` 声明。 |
| 脚本元数据 | `GM_info` | `@grant GM_info`；用于诊断，不用于授权。 |
| 扩展日志 | `GM_log` | `@grant GM_log`；不要记录机密或原始页面内容。 |

现代命名空间 API，例如 `GM.notification`、`GM.download` 和 `GM.getResourceText`，是异步的，并且可用性依赖版本。在替换回调 API 前，检查当前 Tampermonkey 文档和支持矩阵。不要假设每个浏览器或 Tampermonkey 构建都支持命名空间 API。

只要足够，就优先使用原生浏览器 API：页面 UI 使用真正的 `<button>` 和 `addEventListener`，页面授权的剪贴板流程使用 `navigator.clipboard.writeText()`，浏览器弹窗策略和同源规则可接受时使用 `window.open()`，普通本地诊断使用 `console`。当用户脚本需要扩展介导的行为，或需要独立于页面 DOM 的面向用户命令时，使用 GM API。

## 设置菜单示例

菜单注册属于启动代码，并应具有幂等性。可以重启的脚本应保留返回的命令 ID，并在已安装版本支持 `GM_unregisterMenuCommand` 时于 teardown 注销命令。设置仍是不可信的持久化输入：读取时验证，并报告写入失败。

```js
// ==UserScript==
// @name         Menu Settings Example
// @namespace    https://userscripts.example.com/menu-settings
// @version      1.0.0
// @match        https://app.example.com/*
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_registerMenuCommand
// @grant        GM_unregisterMenuCommand
// @grant        GM_notification
// ==/UserScript==

(() => {
  'use strict';

  const settingsKey = 'menu-settings.settings';
  const defaultSettings = { enabled: true };
  let settings = defaultSettings;
  const menuIds = [];
  let inlineStatus = null;
  const menuStatusOwnerSelector = '[data-tm-menu-settings-status-owner="true"]';

  function updateInlineStatus(text, isError) {
    if (inlineStatus !== null && !inlineStatus.isConnected) inlineStatus = null;
    if (inlineStatus === null) {
      inlineStatus = document.querySelector(menuStatusOwnerSelector);
    }
    if (inlineStatus === null && document.body) {
      inlineStatus = document.createElement('p');
      inlineStatus.dataset.tmMenuSettingsStatusOwner = 'true';
      inlineStatus.setAttribute('role', 'status');
      document.body.append(inlineStatus);
    }
    if (inlineStatus === null) return false;
    inlineStatus.textContent = text;
    inlineStatus.dataset.state = isError ? 'error' : 'ready';
    return true;
  }

  function notifyOrFallback(text, isError = false) {
    const updatedInlineStatus = updateInlineStatus(text, isError);
    if (!updatedInlineStatus) {
      const log = isError ? console.error : console.info;
      log(`[menu-settings] ${text}`);
    }
    if (typeof GM_notification === 'function') {
      try {
        GM_notification({ text, title: 'Menu Settings' });
      } catch (error) {
        console.error('[menu-settings] notification failed', error);
      }
    }
  }

  function loadSettings() {
    try {
      const stored = GM_getValue(settingsKey, defaultSettings);
      return stored !== null && typeof stored === 'object' && !Array.isArray(stored)
        ? { enabled: stored.enabled !== false }
        : defaultSettings;
    } catch (error) {
      console.error('[menu-settings] settings read failed', error);
      notifyOrFallback('Settings could not be read; defaults are active.', true);
      return defaultSettings;
    }
  }

  function saveSettings(nextSettings) {
    try {
      GM_setValue(settingsKey, nextSettings);
      settings = nextSettings;
      notifyOrFallback(settings.enabled ? 'Enhancement enabled.' : 'Enhancement disabled.');
    } catch (error) {
      console.error('[menu-settings] settings write failed', error);
      notifyOrFallback('The setting could not be saved.', true);
    }
  }

  function registerMenus() {
    if (menuIds.length > 0) return;
    menuIds.push(
      GM_registerMenuCommand(
        'Toggle enhancement',
        () => saveSettings({ enabled: !settings.enabled }),
      ),
    );
    menuIds.push(
      GM_registerMenuCommand(
        'Show current setting',
        () => notifyOrFallback(
          settings.enabled ? 'Enhancement is enabled.' : 'Enhancement is disabled.',
        ),
      ),
    );
  }

  function unregisterMenus() {
    while (menuIds.length > 0) {
      const id = menuIds.pop();
      try {
        GM_unregisterMenuCommand(id);
      } catch (error) {
        console.debug('[menu-settings] menu cleanup failed', error);
      }
    }
  }

  settings = loadSettings();
  registerMenus();
  window.addEventListener('pagehide', unregisterMenus, { once: true });
})();
```

菜单回调不应假设页面仍然拥有注册时的 DOM。命令执行时重新查询稳定元素；如果当前路由不适用，显示可操作通知。对于普通页面工作流中的操作，菜单不能替代可见且可访问的控件。

## 通知和剪贴板

通知适合展示标签页变化后原本会隐藏的完成和失败状态。文字要简短，避免包含机密；用户需要更多细节时，提供操作或页面位置。通知权限和支持可能因浏览器及 Tampermonkey 模式不同而变化，因此应独立于 `GM_notification` 调用脚本拥有的 inline status 更新器或安全的控制台回退；通知调用即使返回但没有显示任何内容，也不能隐藏错误。只复用此脚本命名空间的精确 `data-tm-menu-settings-status-owner="true"` 标记，需要时追加带有相同脚本拥有标记的 status 节点，绝不要通过替换页面拥有的内容来创建回退。

剪贴板写入应由明确的用户操作发起，并准确说明将复制的内容。使用 `textContent` 显示预览；不要仅因访问令牌、cookie 或页面机密可用就复制它。`GM_setClipboard` 接受可选 MIME 类型描述；调用前验证内容，并根据使用的 API 形式处理其回调或被拒绝的命名空间 promise。

## 下载

当用户没有明确请求时，把下载视为需要确认的外部副作用。根据允许列表验证源 URL，生成有界文件名，并包含合适扩展名。Tampermonkey 文档指出，请求的扩展名可能需要在其选项中列入白名单，浏览器也可能修改最终文件名。`GM_download` 使用的 `Blob` 和 `File` URL 形式文档标注为 `v5.4.6226+`；应设置该最低版本，或为较旧安装使用单独测试过的基于 URL 的路径。

```js
// 需要：@grant GM_download
function downloadReport(csvText) {
  const blob = new Blob([csvText], { type: 'text/csv;charset=utf-8' });
  const filename = `report-${new Date().toISOString().slice(0, 10)}.csv`;

  if (!window.confirm(`Download ${filename}?`)) {
    return;
  }

  const objectUrl = URL.createObjectURL(blob);
  let cleanedUp = false;
  let cleanupTimer = null;
  function cleanupObjectUrl() {
    if (cleanedUp) return;
    cleanedUp = true;
    if (cleanupTimer !== null) window.clearTimeout(cleanupTimer);
    cleanupTimer = null;
    window.removeEventListener('pagehide', cleanupObjectUrl);
    URL.revokeObjectURL(objectUrl);
  }
  cleanupTimer = window.setTimeout(cleanupObjectUrl, 60_000);
  window.addEventListener('pagehide', cleanupObjectUrl, { once: true });

  try {
    const download = GM_download({
      url: objectUrl,
      name: filename,
      saveAs: true,
      onload() {
        cleanupObjectUrl();
        console.info('[download] report saved');
      },
      onerror(details) {
        cleanupObjectUrl();
        const reason = details?.error || 'unknown error';
        console.error('[download] report failed', reason);
        window.alert(`The report could not be downloaded: ${reason}`);
      },
      ontimeout() {
        cleanupObjectUrl();
        window.alert('The report download timed out.');
      },
    });

    return download;
  } catch (error) {
    cleanupObjectUrl();
    throw error;
  }
}
```

object URL 会通过成功、失败、异常、pagehide 和独立的有界计时器撤销，因此清理不只依赖回调。如果下载来自远程 URL，仅当 API 需要时使用 `@connect`，验证重定向和来源假设，不要把浏览器历史或下载管理器可能保留的敏感查询参数放进 URL。下载错误可能表示 `not_enabled`、`not_whitelisted`、`not_permitted`、`not_supported` 或传输失败；已知时应显示具体且安全的恢复路径。

## 资源、标签页、元数据和日志

明确声明静态资源：

```js
// @resource      help-template https://cdn.example.com/help-template.html
// @grant         GM_getResourceText
// @grant         GM_getResourceURL
```

使用 `GM_getResourceText` 获取将在插入前解析并清理的文本模板。使用 `GM_getResourceURL` 获取可以赋给经过验证的元素属性的图片或其他资源 URL。资源仍然是供应链输入；审查其来源和更新策略。

`GM_openInTab` 应接收由固定来源和经过验证的路径构建的 URL。不要将任意页面文本传给它，也不要假设目标页面自身代码运行前标签页已聚焦或加载。`GM_info` 可以在诊断期间识别脚本名称、版本、处理器和下载模式。`GM_log` 是扩展介导的日志，但不是机密存储；记录前要删除标识符和 payload。

## UI 与实用 API 审查清单

- [ ] 每次 GM API 调用都有匹配的 `@grant`，并说明版本假设。
- [ ] 菜单命令只注册一次，保留 ID，并安全清理。
- [ ] 通知使用安全文本；权限或支持不可用时有独立的脚本拥有 inline status 或安全控制台回退。
- [ ] 剪贴板操作需要明确用户意图，且不复制机密。
- [ ] 下载验证源 URL、文件名、扩展名、确认和回调。
- [ ] 本地下载通过回调和独立清理路径撤销 object URL。
- [ ] 资源已声明、审查，并在插入 DOM 前清理。
- [ ] 打开的标签页使用经过验证的目标，不暴露页面机密。
- [ ] `GM_info` 和日志用于诊断，不把元数据当作授权。
- [ ] 当原生浏览器 API 能以更少权限提供相同行为时使用它。

## 官方参考

- [Tampermonkey `GM_registerMenuCommand`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_registerMenuCommand)
- [Tampermonkey `GM_notification`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_notification)
- [Tampermonkey `GM_setClipboard`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_setClipboard)
- [Tampermonkey `GM_download`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_download)
- [Tampermonkey `GM_openInTab`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_openInTab)
- [Tampermonkey `GM_getResourceText` 和 `GM_getResourceURL`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_getResource)
- [Tampermonkey `GM_info`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_info)
- [Tampermonkey `GM_log`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_log)
- [MDN `URL.createObjectURL`](https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL_static)
