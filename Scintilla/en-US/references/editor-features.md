# Editor feature recipes

## Initialization order

1. Create the Scintilla control and set font, encoding, line-ending, and tab conventions.
2. Set a lexer, usually supplied by Lexilla in Scintilla 5.
3. Configure styles, margins, markers, indicators, folding, and autocomplete.
4. Set text and call `SCI_SETSAVEPOINT`, or preserve the intended dirty state.
5. Subscribe to `SCN_MODIFIED`, save-point, and interaction notifications.

## Styling and lexers

Each document byte has a style byte; the style indexes a style array. The lexer classifies text, while the host maps styles to fonts, colors, bold, and italics. Styling is derived state and should not be persisted as source-file content.

## Selection, undo, and saving

Use Scintilla's selection, undo/redo, and save-point APIs instead of mixing in deprecated Edit/RichEdit messages. Call `SCI_SETSAVEPOINT` after a successful save. Use save-point reached/left notifications to update tabs, save buttons, and external document state.

## Completion and call tips

The host commonly supplies completion items from a lexer or language service. Handle `SCN_AUTOCSELECTION`, `SCN_AUTOCCOMPLETED`, and cancellation notifications. When a choice comes from a fill-up character, Tab, Enter, or a command, inspect `listCompletionMethod` rather than assuming a mouse selection.

## Margins, markers, and indicators

- Margins suit line numbers, folding controls, and debugger breakpoint markers.
- Markers represent line-level state; indicators represent range-level errors, search matches, or hotspots.
- For indicator/hotspot clicks, use the notification's position and modifiers and follow reentrancy restrictions.

## Migration

Avoid new dependencies on `WM_*`/`EM_*` compatibility messages, style-byte indicators, `SCI_SETSTYLEBITS`, and other deprecated or discouraged APIs. If legacy compatibility is required, isolate it in an adapter and document the replacement path.
