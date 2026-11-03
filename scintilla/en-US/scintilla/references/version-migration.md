# Version, migration, and compatibility

This skill targets Scintilla.dll v5.6.4. The official home page records v5.6.4 as the release with pixel-aligned fractional scaling for Qt; 5.6.3 restored selection/scroll position for undo/redo in additional views, 5.6.2 added `SC_STATUS_OUTSIDE_DOCUMENT` and stopped out-of-bounds insertions earlier, 5.6.1 fixed a `SCI_CONVERTEOLS` regression and added tab-blob drawing, and 5.6.0 fixed a crash when the window was too narrow to show text.

The major Scintilla 5 boundary is that lexers moved to Lexilla. When migrating an older project, inspect build scripts, DLL search paths, lexer loading, headers, and generated constants.

Provisional APIs may change or be removed; define `SCI_DISABLE_PROVISIONAL` to exclude them. Deprecated/discouraged APIs such as old `WM_*`/`EM_*`, `SCI_SETSTYLEBITS`, and style-byte indicators should not be used in new code. Before upgrading, compare official documentation, headers, import libraries, and runtime DLLs, then run ABI and behavior regression tests.

Sources: https://www.scintilla.org/, https://www.scintilla.org/Scintilla5Migration.html, and https://www.scintilla.org/ScintillaHistory.html.
