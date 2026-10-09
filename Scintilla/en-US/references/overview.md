# Overview and integration boundaries

## Positioning

Scintilla is an embeddable source-code editing control, not a complete IDE. It provides text editing, syntax styling, error indicators, code completion, call tips, folding, markers, and multiple views. The host owns file IO, project models, commands, and language services.

The v5.6.4 home page highlights pixel-aligned fractional scaling for Qt. The current 5.* line requires a compiler supporting C++17.

## Windows integration

The Windows build is a Windows Control whose primary interface is window messages. With the dynamic DLL, load Scintilla and create the `Scintilla` window class. With the static library, link `bin/libscintilla.lib` and call `Scintilla_RegisterClasses`. A standalone DLL needs `ScintillaDLL.cxx` for `DllMain` and registration.

Message arguments correspond to `wParam` and `lParam` and are wide enough for pointers; return values are pointer-sized too. Do not narrow them unconditionally to `int`.

## Lexilla boundary

Since Scintilla 5.0, lexers live in Lexilla. Scintilla owns the GUI and invokes lexers; Lexilla supplies them as shared or static libraries. Check the Lexilla DLL, lexer name, and external lexer protocol when deploying syntax highlighting.

## Lifetime

Release host-owned resources before destroying controls. Do not retain internal pointers documented as valid only during a call. For multiple views sharing a document, distinguish view state from document state and test undo, selection, and scroll expectations.
