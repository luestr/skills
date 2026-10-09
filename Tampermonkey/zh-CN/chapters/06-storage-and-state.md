# 06. 存储与状态

Tampermonkey 存储适合保存用户脚本范围的设置，以及协调脚本实例之间的状态。将存储值视为不可信的、带版本的输入：用户可以编辑或删除它们，旧脚本版本可能写入过另一种形状，另一个标签页也可能在当前标签页使用值时修改它。

本章示例使用同步 `GM_*` API。每个调用 Tampermonkey 存储 API 的示例都在元数据中声明对应 grant。

## 存储 API 范围

| 需求 | 同步 API 和 grant | 现代命名空间形式 | 说明 |
| --- | --- | --- | --- |
| 读取一个值 | 带 `@grant GM_getValue` 的 `GM_getValue` | 带匹配命名空间 grant 的 `GM.getValue` | 始终传入默认值，并验证返回值。 |
| 写入一个值 | 带 `@grant GM_setValue` 的 `GM_setValue` | 带匹配命名空间 grant 的 `GM.setValue` | 处理写入错误，不要假设读-改-写是原子的。 |
| 删除一个值 | 带 `@grant GM_deleteValue` 的 `GM_deleteValue` | 带匹配命名空间 grant 的 `GM.deleteValue` | 用于明确清理或迁移，不要作为隐式重置。 |
| 列出键 | 带 `@grant GM_listValues` 的 `GM_listValues` | 带匹配命名空间 grant 的 `GM.listValues` | 将结果视为元数据，而不是完整的状态验证。 |
| 读取多个值 | 带 `@grant GM_getValues` 的 `GM_getValues` | `GM.getValues` | 文档标注为 `5.3+`；同步形式接受键或默认值。 |
| 写入多个值 | 带 `@grant GM_setValues` 的 `GM_setValues` | `GM.setValues` | 文档标注为 `5.3+`；改造版本有批量写入需求时使用。 |
| 删除多个值 | 带 `@grant GM_deleteValues` 的 `GM_deleteValues` | `GM.deleteValues` | 文档标注为 `5.3+`；在分发脚本中使用前验证支持情况。 |
| 观察一个键 | 带 `@grant GM_addValueChangeListener` 的 `GM_addValueChangeListener` | `GM.addValueChangeListener` | 回调接收 `key`、`oldValue`、`newValue` 和 `remote`。 |
| 移除观察器 | 带 `@grant GM_removeValueChangeListener` 的 `GM_removeValueChangeListener` | `GM.removeValueChangeListener` | teardown 时始终调用。 |

[Tampermonkey 值 API 文档](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values)是签名和版本标签的权威来源。Tampermonkey 的现代命名空间 API 是异步的，并且可以返回 promise；使用 `await` 或处理拒绝。没有明确错误策略时，不要在同一代码路径中悄然混用同步和异步形式。

批量 API `GM_getValues`、`GM_setValues` 和 `GM_deleteValues` 在当前文档中标记为 `v5.3+`。它们是版本特定功能，不是浏览器 API。说明最低支持的 Tampermonkey 版本；仅当兼容性需求值得维护时，才提供单键回退。

## 默认值、验证和序列化

向 `GM_getValue` 传入默认值，使首次运行具有确定性。即使提供了默认值，也要验证结果：旧版本、手动编辑或其他代码路径可能产生不同形状。

Tampermonkey 文档说明存储值支持 `null`、对象、字符串、数字、`undefined` 和布尔值，包括嵌套对象属性。将持久化值限制为普通数据：

- 使用字符串、数字、布尔值、null、数组和普通对象。
- 不要存储 DOM 节点、函数、promise、循环对象、页面 window 对象或依赖可执行方法的类实例。
- 读取时验证枚举值、范围、对象键和数组长度。
- 避免存储机密。Tampermonkey 存储不是通用的安全机密库。
- 将 schema 版本保存在值内，使迁移具有确定性。

如果值跨越 JSON 边界，请记住 `undefined`、日期、特殊数字、原型和自定义类需要明确表示。不要在没有 `try/catch` 和形状验证的情况下对任意存储文本使用 `JSON.parse`。

## 命名空间和键设计

Tampermonkey 通常将存储限定在一个用户脚本内，但逻辑键命名空间仍能让迁移、调试和清理更安全。当设置需要一起读取时，使用稳定前缀，并为每个带版本的聚合设置一个键：

```text
order-helper.settings
order-helper.cache.<safe-id>
order-helper.last-sync
```

不要把原始 URL、页面文本或无界用户输入直接放入键中。规范化动态标识符并限制长度。将缓存数据与持久设置分开，使缓存迁移或删除不会重置用户偏好。

## 并发标签页和变更监听器

`GM_addValueChangeListener` 接收一个 `remote` 布尔值，表示变更是否来自另一个用户脚本实例，例如另一个标签页。使用它在另一实例改变设置时刷新 UI 或状态。不要假设监听器回调提供事务、锁、多个键之间的顺序保证或冲突解决。

对于读-改-写操作，定义策略：

- 简单偏好使用最后写入者胜出，并在值远程变化时显示刷新。
- 当不同标签页可以编辑独立设置时，只合并经过验证的字段。
- 仅当冲突策略需要时才加入 revision 或 timestamp，并将其作为数据验证。

监听器是资源。保存 `GM_addValueChangeListener` 返回的监听器 ID，在 `stop()` 中调用 `GM_removeValueChangeListener`，并确保注册失败或启动提前停止时 teardown 仍然安全。

## 失败处理

同步存储调用可能抛出异常，现代异步调用可能被拒绝。尽可能将持久化放在关键渲染路径之外：

1. 使用经过验证的默认值加载。
2. 即使持久化不可用，也使用内存状态渲染。
3. 捕获写入失败，并以用户可以采取行动的方式报告。
4. 不要仅因一次瞬时写入失败就用回退值覆盖有效的存储值。
5. 记录足够的上下文以诊断键和操作，但不要记录敏感值。
6. 如果迁移无法理解未来 schema，保留原始值并使用安全默认值，而不是销毁数据。

## 带迁移的版本化设置

此示例支持带 `compact` 布尔值的版本 1 设置，并将其迁移为带 `density` 枚举的版本 2。它使用 `GM_getValue`、`GM_setValue`、`GM_addValueChangeListener` 和 `GM_removeValueChangeListener`，因此声明了全部四个 grant。

```js
// ==UserScript==
// @name         Versioned Settings Example
// @namespace    https://userscripts.example.com/versioned-settings
// @version      1.0.0
// @match        https://app.example.com/*
// @run-at       document-idle
// @grant        GM_getValue
// @grant        GM_setValue
// @grant        GM_addValueChangeListener
// @grant        GM_removeValueChangeListener
// ==/UserScript==

(() => {
  'use strict';

  const key = 'settings-example.settings';
  const currentSchemaVersion = 2;
  let settings = null;
  let listenerId = null;
  let started = false;

  function isRecord(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }

  function sameStoredRepresentation(left, right) {
    try {
      return JSON.stringify(left) === JSON.stringify(right);
    } catch {
      return false;
    }
  }

  function defaults() {
    return {
      schemaVersion: currentSchemaVersion,
      enabled: true,
      density: 'comfortable',
      filters: { showArchived: false },
    };
  }

  function migrate(raw) {
    if (raw === null || raw === undefined) {
      return { settings: defaults(), changed: false };
    }

    if (!isRecord(raw)) {
      return { settings: defaults(), changed: true };
    }

    if (raw.schemaVersion === 1) {
      const nextSettings = {
        ...defaults(),
        enabled: raw.enabled !== false,
        density: raw.compact === true ? 'compact' : 'comfortable',
      };
      return {
        settings: nextSettings,
        changed: !sameStoredRepresentation(raw, nextSettings),
      };
    }

    if (raw.schemaVersion === currentSchemaVersion) {
      const filters = isRecord(raw.filters) ? raw.filters : {};
      const nextSettings = {
        schemaVersion: currentSchemaVersion,
        enabled: raw.enabled !== false,
        density: raw.density === 'compact' ? 'compact' : 'comfortable',
        filters: { showArchived: filters.showArchived === true },
      };
      return {
        settings: nextSettings,
        changed: !sameStoredRepresentation(raw, nextSettings),
      };
    }

    throw new Error(`Unsupported settings schema: ${String(raw.schemaVersion)}`);
  }

  function persistMigration(raw, nextSettings) {
    if (sameStoredRepresentation(raw, nextSettings)) return;

    try {
      const latest = GM_getValue(key, null);
      if (!sameStoredRepresentation(latest, raw)) return;
      if (sameStoredRepresentation(latest, nextSettings)) return;
      GM_setValue(key, nextSettings);
    } catch (error) {
      console.error('[settings-example] settings write failed', error);
    }
  }

  function load() {
    let raw;
    try {
      raw = GM_getValue(key, null);
    } catch (error) {
      console.error('[settings-example] settings read failed', error);
      return defaults();
    }

    try {
      const result = migrate(raw);
      if (result.changed) persistMigration(raw, result.settings);
      return result.settings;
    } catch (error) {
      console.error('[settings-example] settings migration failed', error);
      return defaults();
    }
  }

  function render(nextSettings) {
    settings = nextSettings;
    document.documentElement.dataset.settingsExampleDensity = settings.density;
  }

  function start() {
    if (started) return;
    started = true;
    try {
      render(load());
      listenerId = GM_addValueChangeListener(
        key,
        (_changedKey, _oldValue, newValue, remote) => {
          if (!remote) return;
          try {
            render(migrate(newValue).settings);
          } catch (error) {
            console.error('[settings-example] remote settings ignored', error);
          }
        },
      );
    } catch (error) {
      started = false;
      throw error;
    }
  }

  function stop() {
    if (listenerId !== null) {
      GM_removeValueChangeListener(listenerId);
      listenerId = null;
    }
    started = false;
  }

  try {
    start();
    window.addEventListener('pagehide', stop, { once: true });
  } catch (error) {
    console.error('[settings-example] startup failed', error);
    stop();
  }
})();
```

版本 2 分支会规范化即使看似有效的对象，因此无效字段不会泄漏到应用代码。它将规范化后的值与存储表示比较，仅当表示发生变化时写入。迁移写入前，它会再次读取键；如果自原始读取后另一个标签页已修改值，就放弃写入，从而避免把过时的读-改-写迁移应用到更新的数据。同步 API 没有 compare-and-swap 原语，因此需要更强冲突保证的产品必须使用明确的协调策略。

本示例遇到未来 schema 时会保持存储值不变，并在内存中回退。这比覆盖较新脚本版本拥有的数据更安全。具有受控降级策略的产品可以选择不同的行为，但必须明确规定。

## 存储审查清单

- [ ] 每次存储 API 调用都有匹配的 `@grant`。
- [ ] 版本特定的批量 API（`5.3+`）记录了最低版本和回退决策。
- [ ] 读取提供默认值，并验证返回的形状。
- [ ] 持久化值包含 schema 版本，并使用普通数据。
- [ ] 迁移具有确定性，经过测试，并保留未知的未来数据。
- [ ] 键稳定、有命名空间、限制长度，且不包含原始不可信输入。
- [ ] 并发标签页行为和冲突策略明确。
- [ ] `remote` 监听器事件在没有假设事务的情况下处理。
- [ ] 读取、写入和迁移失败都有可观察行为。
- [ ] 监听器 ID 在 teardown 时移除，包括部分启动失败的情况。
- [ ] 未经审查确有需要时，不记录或存储敏感值。

## 官方参考

- [Tampermonkey 存储 API](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [Tampermonkey `GM_addValueChangeListener`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values#api:GM_addValueChangeListener)
- [Tampermonkey `GM_removeValueChangeListener`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values#api:GM_removeValueChangeListener)
- [MDN Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API)（与页面范围浏览器存储比较）
