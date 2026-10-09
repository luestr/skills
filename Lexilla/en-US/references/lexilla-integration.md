# Lexilla integration and extension

## C/C++ integration

Include `lexilla/include/Lexilla.h`. C++ code must include `scintilla/include/ILexer.h` first. For runtime loading, the application defines where Lexilla can be found and maps file extensions or project settings to lexer names. Check each step—loading the shared library, resolving required symbols, creating a lexer, and setting `SCI_SETILEXER`—for failure.

C++ applications can use `access/LexillaAccess.cxx` and `LexillaAccess.h`. Compile the module into the application, or copy and customize it for requirements such as code-signature checks. SciTE uses this module, which supports loading multiple shared libraries implementing the Lexilla protocol.

## Qt integration

Qt can use `LexillaAccess` or `QLibrary`. On Windows, the function pointer must use `__stdcall`; other platforms use a normal function pointer. After resolving `CreateLexer`, check whether `QLibrary::resolve` returned a null pointer. Also check the created lexer before passing its pointer to Scintilla through `SCI_SETILEXER`. The third `SCI_SETILEXER` argument uses Scintilla's `sptr_t` for the lexer pointer.

```cpp
#if _WIN32
typedef void *(__stdcall *CreateLexerFn)(const char *name);
#else
typedef void *(*CreateLexerFn)(const char *name);
#endif
QFunctionPointer fn = QLibrary::resolve("lexilla", "CreateLexer");
if (!fn) {
    // Report that CreateLexer could not be resolved.
}
void *lexCpp = ((CreateLexerFn)fn)("cpp");
if (!lexCpp) {
    // Report that the requested lexer is unavailable.
}
Call(SCI_SETILEXER, 0, (sptr_t)(void *)lexCpp);
```

An application can discover the lexers provided by a library with `GetLexerCount` and `GetLexerName`. If it uses `SetLibraryProperty`, set properties before discovery or creation calls. The application should define shared-library search locations and diagnose a missing library, missing symbols, unsupported names, and architecture mismatches.

## Adding a lexer or creating a library

A compatible library exports the same functions as Lexilla and can add or replace lexers. For optional initialization properties, implement `SetLibraryProperty` and optionally advertise supported names through `GetLibraryPropertyNames`. Unknown properties should be ignored.

See `examples/SimpleLexer` for a minimal compatible library. Build the example library and validate it with `CheckLexilla`; for the C example, enter `examples/CheckLexilla`, run `make`, then run `make check`. For built-in lexer changes, use `test/TestLexers` to verify lexing results.

## Other implementations

- [Scintillua](https://orbitalquark.github.io/scintillua/) provides Lua-based lexers with [Lua](https://www.lua.org/) and [LPeg](https://www.inf.puc-rio.br/~roberto/lpeg/).
- [NppTreeSitter](https://github.com/Thorium/NppTreeSitter) wraps [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) for [Notepad++](https://notepad-plus-plus.org/).

These projects demonstrate how the Lexilla protocol can serve as a protocol boundary between lexer providers and host applications.
