# Lexilla protocol and API

The Lexilla protocol is a superset of the external lexer protocol. A shared library implementing the Lexilla protocol may provide:

```cpp
int GetLexerCount();
void GetLexerName(unsigned int index, char *name, int buflength);
LexerFactoryFunction GetLexerFactory(unsigned int index);
ILexer5 *CreateLexer(const char *name);
const char *LexerNameFromID(int identifier);
const char *GetLibraryPropertyNames();
void SetLibraryProperty(const char *key, const char *value);
const char *GetNameSpace();
```

## Interface categories

- `GetLexerCount`, `GetLexerName`, and `GetLexerFactory` are the first three functions of the earlier external lexer protocol.
- `CreateLexer` is the main modern entry point for creating a lexer by name.
- `LexerNameFromID`, `GetLibraryPropertyNames`, `SetLibraryProperty`, and `GetNameSpace` are optional functions. A loader should check whether these symbols are present before calling them.
- `LexerNameFromID` is deprecated. It is only a migration aid for applications moving from numeric IDs to names, will be removed in a future version, and should not be used by new code.

## Recommended call path

`CreateLexer` is the main entry point. Request a lexer by name, for example `CreateLexer("cpp")`, then pass it to Scintilla through `SCI_SETILEXER`. The returned lexer is normally passed directly to Scintilla; most clients do not need to call `ILexer5` methods. C++ uses `ILexer5 *`; C should not include `ILexer.h` and uses `void *`.

To discover capabilities, call `GetLexerCount`, then call `GetLexerName` for indexes from `0` through `count - 1`. If a library implements `SetLibraryProperty`, `GetLibraryPropertyNames` can expose newline-separated property names. Set required initialization properties before calling `GetLexerCount` or `CreateLexer`; a library should ignore properties it does not understand. For example, a library using XML language definitions may first receive `SetLibraryProperty("definitions.directory", "/usr/share/xeditor/language-definitions")`. The application decides how properties are defined, persisted, and presented in its user interface.

`GetNameSpace` disambiguates equal lexer names, such as `xmllexers.cpp`, and avoids collisions between providers. An unqualified `cpp` request may be satisfied by either provider, while `xmllexers.cpp` selects one explicitly. A migration example is `LexerNameFromID(SCLEX_CPP) -> "cpp"`.

## Compatibility

The first three functions come from the earlier external lexer protocol, so clients supporting that protocol can load Lexilla. `GetLexerFactory` is now rarely used directly; modern clients should prefer `CreateLexer`. `LexerFactoryFunction` is a no-argument function-pointer type returning `ILexer5 *`, and most clients do not need to call it directly.

Types are defined by Scintilla's `include/ILexer.h` and Lexilla's `include/Lexilla.h`. In C++, include `ILexer.h` before `Lexilla.h`; C code should not include the C++ `ILexer.h`.
