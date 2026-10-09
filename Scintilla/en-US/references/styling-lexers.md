# Styling and Lexilla

Scintilla separates document bytes from style bytes: the lexer produces styles and the host configures style properties. Styles can define foreground/background, font, size, bold, italic, underline, case, and EOL fill. Styling is derived state and should not be saved as source-file content.

Scintilla 5 moved lexers to Lexilla. Deploy the matching Lexilla shared/static library, configure lexer, properties, and keywords, and use `SCI_SETILEXER` with `ILexer5` when required. External lexers must follow the official external lexer protocol.

For large documents, consider idle styling, visible-range styling, `SCN_STYLENEEDED`, and batched updates. Avoid expensive host callbacks per character. If a lexer is missing or its name is invalid, report it explicitly while keeping plain-text editing available.

Sources: https://www.scintilla.org/Lexilla.html, https://www.scintilla.org/LexillaDoc.html, and the official `Lexer.txt`.
