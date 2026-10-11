---
name: scintilla
description: Use when integrating Scintilla.dll 5.6.4 into a Windows editor, calling its message API, configuring syntax styling, notifications, Lexilla, or building the DLL.
metadata:
  version: 5.6.4
---

# Scintilla.dll v5.6.4

This skill is an index for integrating the embeddable Scintilla source-code editing control on Windows. Confirm that the DLL, headers, import library, and host bindings are from the same release before using the topic references.

## Index

- [Overview and integration boundaries](references/overview.md): responsibilities, version, platforms, Lexilla, and lifetime.
- [Message API and data contracts](references/api.md): `SCI_*`, `SCN_*`, positions, pointers, encodings, and buffers.
- [Editor feature recipes](references/editor-features.md): text, selection, undo, styling, folding, completion, markers, and notifications.
- [Windows build and diagnostics](references/windows-build.md): C++17, dynamic/static linking, class registration, build macros, and troubleshooting.
- [Complete message-reference navigation](references/messages-reference.md): official `SCI_*`/`SCN_*` groups, argument contracts, and notifications.
- [API topic catalog](references/api-catalog.md): every official Contents topic, feature boundary, and version-check entry point.
- [SCN_* notification catalog](references/notification-catalog.md): notification fields, lifecycles, and reentrancy rules.
- [Lexers, lexer objects, and Lexilla](references/lexer-objects.md): normal lexer libraries, `ILexer5`, and `CreateLexer`.
- [Platform APIs and input/output details](references/platform-apis.md): Windows, GTK, Cocoa, Qt, encoding, line endings, RTL, and images.
- [Deprecated, never-supported, and removed APIs](references/compatibility-catalog.md): compatibility, deprecated, unsupported, and removed features.
- [Images API](references/images.md): RGBA, XPM, image registration, dimensions, alpha, and lifetime.
- [GTK API](references/gtk.md): widgets, messages, IDs, resource release, and thread boundaries.
- [Building Scintilla](references/building.md): Windows, GTK, Cocoa, Qt, regex, and build definitions.
- [Official-section precision checklist](references/precision-audit.md): official anchors, 5.6.4 headers, platform conditions, and uncertainty markers.
- [Search, replace, and regular expressions](references/search-replace.md): targets, flags, regex, incremental search, and result highlighting.
- [Styling and Lexilla](references/styling-lexers.md): styles, lexers, properties, keywords, and the Lexilla boundary.
- [Indicators, annotations, and visual feedback](references/indicators-annotations.md): range diagnostics, line annotations, and marker feedback.
- [Margins, markers, and folding](references/margins-markers-folding.md): line numbers, folding, debugger markers, and fold levels.
- [Autocompletion, user lists, and call tips](references/autocomplete-calltips.md): completion, user lists, signature tips, and notification lifecycles.
- [Multiple views, document interface, and direct access](references/multiple-views-direct-access.md): shared documents, view state, and background IO.
- [Input/output, platforms, and accessibility](references/input-output-platform.md): encoding, line endings, clipboard, drag/drop, printing, RTL, DPI, and backends.
- [Version, migration, and compatibility](references/version-migration.md): 5.6.4 changes, Lexilla migration, provisional and deprecated APIs.

## Operating rules

1. Use the official documentation rather than guessing from legacy Edit/RichEdit conventions or wrapper behavior.
2. Pass `0` for unused `wParam`/`lParam`; verify pointer lifetime, encoding, and buffer capacity for every pointer argument.
3. Scintilla positions and lengths are documented in bytes. Do not substitute UTF-8 code-point counts.
4. Scintilla 5 moved lexers to Lexilla; verify Lexilla deployment and version whenever syntax highlighting is required.
5. Handle `SCN_MODIFIED`, `SCN_SAVEPOINTREACHED`, and `SCN_SAVEPOINTLEFT` in the host state model, and call `SCI_SETSAVEPOINT` after a successful save.

## Official sources

- Home: https://www.scintilla.org/
- API documentation: https://www.scintilla.org/ScintillaDoc.html
- Downloads: https://www.scintilla.org/ScintillaDownload.html
- Lexilla: https://www.scintilla.org/Lexilla.html

## Delivery checklist

- DLL, import library, and headers are all 5.6.4.
- The Windows control class is registered and can send and receive messages.
- Text retrieval handles length probing, NUL-terminated and non-NUL-terminated results.
- Stable APIs are preferred; provisional or deprecated APIs are explicitly justified.
- UTF-8, line endings, undo, read-only behavior, and notifications are tested on the target architecture.
