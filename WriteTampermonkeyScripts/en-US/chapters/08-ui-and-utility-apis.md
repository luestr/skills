# 08. UI and Utility APIs

Tampermonkey utility APIs are useful for script-owned commands, notifications, clipboard operations, downloads, resource access, and opening a related page. They are privileged browser-extension APIs, so every example should declare only the grants it uses and should still prefer native browser APIs when they provide the required behavior without extra permission.

## API Surface and Grants

| Need | API | Required grant and important behavior |
| --- | --- | --- |
| User command | `GM_registerMenuCommand` | `@grant GM_registerMenuCommand`; keep the command useful when the page is not open. |
| Notification | `GM_notification` | `@grant GM_notification`; support a failure or permission-denied state. |
| Clipboard write | `GM_setClipboard` | `@grant GM_setClipboard`; ask for user intent before copying sensitive content. |
| File download | `GM_download` | `@grant GM_download`; validate the URL and filename, and handle `onerror`. |
| New tab | `GM_openInTab` | `@grant GM_openInTab`; open only validated, expected destinations. |
| Bundled resource text or URL | `GM_getResourceText`, `GM_getResourceURL` | Matching grants plus an `@resource name url` declaration. |
| Script metadata | `GM_info` | `@grant GM_info`; use it for diagnostics, not as authorization. |
| Extension log | `GM_log` | `@grant GM_log`; do not log secrets or raw page content. |

The modern namespaced APIs, such as `GM.notification`, `GM.download`, and `GM.getResourceText`, are asynchronous and have version-specific availability. Check the current Tampermonkey documentation and support matrix before replacing a callback API. Do not assume that a namespaced API is available in every browser or Tampermonkey build.

Native browser APIs are preferable when they are sufficient: use a real `<button>` and `addEventListener` for page UI, `navigator.clipboard.writeText()` for a page-authorized clipboard flow, `window.open()` when the browser's popup policy and same-origin rules are acceptable, and `console` for ordinary local diagnostics. The GM API is appropriate when the userscript needs extension-mediated behavior or a user-facing command that is independent of the page DOM.

## Settings Menu Example

Menu registration belongs in startup code and should be idempotent. A script that can be restarted must retain the returned command IDs and unregister them during teardown when the installed version supports `GM_unregisterMenuCommand`. Settings are still untrusted persisted input: validate them on read and report a failed write.

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

The menu callback should not assume the page still has the DOM that was present at registration time. Re-query stable elements when the command runs, and show an actionable notification if the current route is not applicable. A menu is not a substitute for a visible accessible control when the action is part of the normal page workflow.

## Notifications and Clipboard

Notifications are useful for completion and failure states that would otherwise be hidden after a tab changes. Keep their text short, avoid including secrets, and provide an action or a page location when the user needs more detail. Notification permission and support can vary by browser and Tampermonkey mode, so call a script-owned inline status updater or safe console fallback independently of `GM_notification`; a notification call that returns without displaying anything must not hide an error. Reuse only the exact `data-tm-menu-settings-status-owner="true"` marker from this script namespace, append a matching script-owned status node when needed, and never replace page-owned content to create the fallback.

Clipboard writes should be initiated by a clear user action and should expose exactly what will be copied. Use `textContent` for a preview and never copy an access token, cookie, or page secret merely because it is available. `GM_setClipboard` accepts an optional MIME-type description; validate the content before calling it and handle its callback or rejected namespaced promise according to the API form in use.

## Downloads

Treat a download as an external side effect that needs confirmation when the user did not explicitly request it. Validate the source URL against an allowlist, derive a bounded filename, and include a suitable extension. Tampermonkey documentation notes that the requested extension may need to be whitelisted in its options and that the browser may modify the final filename. The `Blob` and `File` URL forms used by `GM_download` are documented as `v5.4.6226+`; set that minimum version or use a separately tested URL-based path for older installations.

```js
// Requires: @grant GM_download
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

The object URL is revoked by success, failure, exception, pagehide, and an independent bounded timer, so cleanup does not depend only on callbacks. If the download is from a remote URL, use `@connect` only when the API requires it, validate redirects and origin assumptions, and do not put sensitive query parameters in a URL that the browser history or download manager may retain. A download error can mean `not_enabled`, `not_whitelisted`, `not_permitted`, `not_supported`, or a failed transfer; show the specific safe recovery path when it is known.

## Resources, Tabs, Metadata, and Logging

Declare static resources explicitly:

```js
// @resource      help-template https://cdn.example.com/help-template.html
// @grant         GM_getResourceText
// @grant         GM_getResourceURL
```

Use `GM_getResourceText` for a text template that will be parsed and sanitized before insertion. Use `GM_getResourceURL` for an image or other resource URL that can be assigned to a validated element attribute. A resource is still a supply-chain input; review its origin and update policy.

`GM_openInTab` should receive a URL built from a fixed origin and validated path. Do not pass arbitrary page text to it, and do not assume the tab is focused or loaded before the destination's own page code runs. `GM_info` can identify the script name, version, handler, and download mode during diagnosis. `GM_log` is extension-mediated logging, but it is not a secret store; redact identifiers and payloads before logging.

## UI and Utility Review Checklist

- [ ] Each GM API call has its matching `@grant` and version assumptions are stated.
- [ ] Menu commands are registered once, retain IDs, and clean up safely.
- [ ] Notifications have safe text and an independent script-owned inline status or safe console fallback when permission or support is unavailable.
- [ ] Clipboard actions require clear user intent and do not copy secrets.
- [ ] Downloads validate source URLs, filenames, extensions, confirmation, and callbacks.
- [ ] Object URLs are revoked after local downloads through callbacks and an independent cleanup path.
- [ ] Resources are declared, reviewed, and sanitized before DOM insertion.
- [ ] Opened tabs use validated destinations and do not expose page secrets.
- [ ] `GM_info` and logs are used for diagnosis without treating metadata as authorization.
- [ ] Native browser APIs are used when they provide the same behavior with less privilege.

## Official References

- [Tampermonkey `GM_registerMenuCommand`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_registerMenuCommand)
- [Tampermonkey `GM_notification`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_notification)
- [Tampermonkey `GM_setClipboard`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_setClipboard)
- [Tampermonkey `GM_download`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_download)
- [Tampermonkey `GM_openInTab`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_openInTab)
- [Tampermonkey `GM_getResourceText` and `GM_getResourceURL`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_getResource)
- [Tampermonkey `GM_info`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_info)
- [Tampermonkey `GM_log`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_log)
- [MDN `URL.createObjectURL`](https://developer.mozilla.org/en-US/docs/Web/API/URL/createObjectURL_static)
