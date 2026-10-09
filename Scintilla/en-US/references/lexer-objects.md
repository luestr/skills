# Lexers, lexer objects, and Lexilla

Scintilla 5 moved lexers from Scintilla into Lexilla. Lexilla can be built as a shared or static library; applications may use Lexilla or a replacement lexer library exposing the same functions.

## Two usage paths

1. **Built-in or normal lexer path**: use `SCI_SETLEXER` or `SCI_SETLEXERLANGUAGE` for the lexer supplied by the distribution, then configure `SCI_SETPROPERTY` and `SCI_SETKEYWORDS`; whether the host explicitly loads Lexilla depends on deployment.
2. **External/replacement lexer library**: follow the external lexer protocol and let the host or supporting application load and select the lexer by name.
3. **Object lexer**: call Lexilla's `CreateLexer(const char *name)` to create an `ILexer5 *`, then use `SCI_SETILEXER`. This explicit object path is not required for ordinary DLL loading.

The lexer provides styling and usually folding. The host should respond to `SCN_STYLENEEDED` or visible-range styling needs promptly. A custom lexer must follow `ILexer5` and external lexer protocol lifetime, error, and release rules.

When migrating, inspect lexer library paths, names, properties/keywords, generated constants, ABI, and Scintilla/Lexilla versions. If a lexer is unavailable, keep a plain-text fallback instead of breaking basic editing.

Sources: https://www.scintilla.org/Lexilla.html, https://www.scintilla.org/LexillaDoc.html, and https://www.scintilla.org/Scintilla5Migration.html.
