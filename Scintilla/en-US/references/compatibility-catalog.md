# Deprecated, never-supported, and removed APIs

## Deprecated / compatibility

The official documentation lists supported but replaceable Edit/RichEdit messages such as `WM_GETTEXT`, `WM_SETTEXT`, `EM_GETLINE`, `WM_UNDO`, `EM_SETSEL`, `EM_FINDTEXT`, and `EM_FORMATRANGE`. New code should use the corresponding Scintilla `SCI_*` API rather than depend on the compatibility layer.

Defining `INCLUDE_DEPRECATED_FEATURES` exposes some older features, including `SCI_SETKEYSUNICODE`, `SCI_SETTWOPHASEDRAW`, and `SCI_SETSTYLEBITS`. Do not add `SCI_SETSTYLEBITS` or style-byte indicators to new code; standard indicators are the replacement.

## Never-supported

Scintilla does not support many RichEdit-only messages, including word-break procedures, paragraph/character formatting, OLE, stream IO, IME options, event masks, password characters, and `EM_DISPLAYBAND`. These messages have no effect and must not be used with RichEdit semantics.

## Removed

Completely removed features include `SC_CP_DBCS`, palette mode (`SCI_SETUSEPALETTE`), and style-byte indicators. Use `SCI_SETCODEPAGE`, standard indicators, and current drawing APIs; remove removed symbols from calling code during migration.

## Provisional

Provisional messages can change or be removed. Define `SCI_DISABLE_PROVISIONAL` for builds that require only stable APIs, then re-check headers, generated constants, and behavior tests after upgrades.

Source: https://www.scintilla.org/ScintillaDoc.html#DeprecatedMessages
