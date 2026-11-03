# 06. Storage and State

Tampermonkey storage is useful for userscript-scoped settings and coordination between script instances. Treat stored values as untrusted, versioned input: users can edit or delete them, older script versions may have written another shape, and another tab can change a value while the current tab is using it.

The examples in this chapter use the synchronous `GM_*` APIs. Every example that calls a Tampermonkey storage API declares the corresponding grant in its metadata.

## Storage API Surface

| Need | Synchronous API and grant | Modern namespaced form | Notes |
| --- | --- | --- | --- |
| Read one value | `GM_getValue` with `@grant GM_getValue` | `GM.getValue` with the matching namespaced grant | Always pass a default and validate the returned value. |
| Write one value | `GM_setValue` with `@grant GM_setValue` | `GM.setValue` with the matching namespaced grant | Handle write errors and do not assume read-modify-write is atomic. |
| Delete one value | `GM_deleteValue` with `@grant GM_deleteValue` | `GM.deleteValue` with the matching namespaced grant | Use for explicit cleanup or migration, not as an implicit reset. |
| List keys | `GM_listValues` with `@grant GM_listValues` | `GM.listValues` with the matching namespaced grant | Treat the result as metadata, not as a complete state validation. |
| Read several values | `GM_getValues` with `@grant GM_getValues` | `GM.getValues` | Documented as `5.3+`; the synchronous form accepts keys or defaults. |
| Write several values | `GM_setValues` with `@grant GM_setValues` | `GM.setValues` | Documented as `5.3+`; use when an adapted version requires bulk writes. |
| Delete several values | `GM_deleteValues` with `@grant GM_deleteValues` | `GM.deleteValues` | Documented as `5.3+`; verify support before using it in a distributed script. |
| Observe a key | `GM_addValueChangeListener` with `@grant GM_addValueChangeListener` | `GM.addValueChangeListener` | The callback receives `key`, `oldValue`, `newValue`, and `remote`. |
| Remove an observer | `GM_removeValueChangeListener` with `@grant GM_removeValueChangeListener` | `GM.removeValueChangeListener` | Always call it during teardown. |

The [Tampermonkey value API documentation](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values) is authoritative for signatures and version labels. Tampermonkey's modern namespaced APIs are asynchronous and can return promises; use `await` or handle rejection. Do not silently mix synchronous and asynchronous forms in one code path without an explicit error strategy.

The bulk APIs `GM_getValues`, `GM_setValues`, and `GM_deleteValues` are marked `v5.3+` in the current documentation. They are version-specific features, not browser APIs. State the minimum supported Tampermonkey version and provide a single-key fallback only when the compatibility requirement justifies maintaining one.

## Defaults, Validation, and Serialization

Pass a default to `GM_getValue` so a first run is deterministic. Then validate the result even if a default was supplied: an older version, manual editing, or another code path can produce a different shape.

Tampermonkey documents storage values as supporting `null`, objects, strings, numbers, `undefined`, and booleans, including nested object properties. Keep persisted values to plain data:

- Use strings, numbers, booleans, null, arrays, and plain objects.
- Do not store DOM nodes, functions, promises, cyclic objects, page-window objects, or class instances that require executable methods.
- Validate enum values, ranges, object keys, and array lengths when reading.
- Avoid storing secrets. Tampermonkey storage is not a general-purpose secure secret vault.
- Keep schema version inside the value so migrations are deterministic.

If a value crosses a JSON boundary, remember that `undefined`, dates, special numbers, prototypes, and custom classes need an explicit representation. Do not use `JSON.parse` on arbitrary storage text without a `try/catch` and shape validation.

## Namespacing and Key Design

Tampermonkey normally scopes storage to a userscript, but logical key namespaces still make migrations, debugging, and cleanup safer. Use a stable prefix and one key per versioned aggregate when settings are read together:

```text
order-helper.settings
order-helper.cache.<safe-id>
order-helper.last-sync
```

Do not put raw URLs, page text, or unbounded user input directly into keys. Normalize and length-limit dynamic identifiers. Keep cache data separate from durable settings so a cache migration or deletion cannot reset user preferences.

## Concurrent Tabs and Change Listeners

`GM_addValueChangeListener` receives a `remote` boolean that indicates whether the change originated from another userscript instance, such as another tab. Use it to refresh UI or state when another instance changes a setting. Do not assume that a listener callback provides a transaction, lock, ordering guarantee across several keys, or conflict resolution.

For a read-modify-write operation, define a policy:

- Last writer wins for a simple preference, with a visible refresh if the value changes remotely.
- Merge only validated fields when separate tabs can edit independent settings.
- Include a revision or timestamp only when the conflict policy needs one, and validate it as data.

Listeners are resources. Store the listener ID returned by `GM_addValueChangeListener`, call `GM_removeValueChangeListener` in `stop()`, and ensure teardown is safe when registration failed or startup stopped early.

## Failure Handling

Synchronous storage calls can throw, and modern asynchronous calls can reject. Keep persistence outside the critical rendering path where possible:

1. Load with a validated default.
2. Render using in-memory state even if persistence is unavailable.
3. Catch a failed write and report it in a way the user can act on.
4. Do not overwrite a valid stored value with a fallback merely because a transient write failed.
5. Log enough context to diagnose the key and operation, but do not log sensitive values.
6. If migration cannot understand a future schema, preserve the original value and use safe defaults instead of destroying data.

## Versioned Settings with Migration

This example supports a version 1 setting with a `compact` boolean and migrates it to version 2 with a `density` enum. It uses `GM_getValue`, `GM_setValue`, `GM_addValueChangeListener`, and `GM_removeValueChangeListener`, so all four grants are declared.

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

The version 2 branch normalizes even a valid-looking object, so invalid fields do not leak into application code. It compares the normalized value with the stored representation and writes only when that representation changes. Before a migration write, it reads the key again and abandons the write if another tab has changed the value since the original read; this avoids applying a stale read-modify-write migration to newer data. The synchronous API has no compare-and-swap primitive, so a product that needs stronger conflict guarantees must use an explicit coordination policy.

A migration that encounters a future schema leaves the stored value untouched in this example and falls back in memory. That is safer than overwriting data owned by a newer script version. A product with a controlled downgrade policy can choose a different behavior, but it must be explicit.

## Storage Review Checklist

- [ ] Every storage API call has its matching `@grant`.
- [ ] Version-specific bulk APIs (`5.3+`) have a documented minimum version and fallback decision.
- [ ] Reads provide defaults and validate the returned shape.
- [ ] Persisted values contain a schema version and use plain data.
- [ ] Migrations are deterministic, tested, and preserve unknown future data.
- [ ] Keys are stable, namespaced, length-limited, and free of raw untrusted input.
- [ ] Concurrent-tab behavior and conflict policy are explicit.
- [ ] `remote` listener events are handled without assuming transactions.
- [ ] Read, write, and migration failures have observable behavior.
- [ ] Listener IDs are removed during teardown, including partial-start failure.
- [ ] Sensitive values are not logged or stored without a reviewed need.

## Official References

- [Tampermonkey storage APIs](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values)
- [Tampermonkey `@grant`](https://www.tampermonkey.net/documentation.php?locale=en&q=grant)
- [Tampermonkey `GM_addValueChangeListener`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values#api:GM_addValueChangeListener)
- [Tampermonkey `GM_removeValueChangeListener`](https://www.tampermonkey.net/documentation.php?locale=en&q=GM_values#api:GM_removeValueChangeListener)
- [MDN Web Storage API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API) (for comparison with page-scoped browser storage)
