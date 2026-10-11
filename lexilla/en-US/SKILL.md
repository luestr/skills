---
name: lexilla
description: Integrate, build, discover, and extend language lexers for Scintilla with Lexilla.
metadata:
  version: 5.5.1
---

# Lexilla Skill Index

Use this skill when integrating Lexilla v5.5.1 into a C/C++, Qt, or other host application. Lexilla is a library of language lexers for Scintilla and can be linked as a static library or loaded as a shared library at runtime.

## Official material index

- [Project overview](references/lexilla-overview.md): scope, release history, version, platforms, license, and official links.
- [Protocol and API](references/lexilla-protocol.md): exported functions, `CreateLexer`, discovery, and library properties.
- [Building and testing](references/lexilla-build-test.md): the Scintilla peer directory, `make`, `nmake`, Visual C++, and tests.
- [Integration and extension](references/lexilla-integration.md): C/C++ and Qt integration, plus custom lexer boundaries.

### Official project resources

- [Lexilla downloads](https://www.scintilla.org/LexillaDownload.html)
- [Lexilla history and contributors](https://www.scintilla.org/LexillaHistory.html)
- [GitHub issues](https://github.com/ScintillaOrg/lexilla/issues)
- [Build-check CI](https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check.yml), [Win32 CI](https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check-win32.yml), and [macOS CI](https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check-macos.yml)
- [SciTE](https://www.scintilla.org/SciTE.html) and [related projects](https://www.scintilla.org/ScintillaRelated.html)
- [scintilla-interest mailing list](https://groups.google.com/forum/#!forum/scintilla-interest) for questions, bugs, and release discussion.

## Quick workflow

1. Prepare Lexilla v5.5.1 and Scintilla 5+; for builds, place a directory named `scintilla` beside the `lexilla` top-level directory.
2. Choose static linking or runtime loading. Shared-library suffixes are normally `.DLL` on Windows, `.so` on Linux, and `.dylib` on macOS.
3. Create a lexer by name, such as `CreateLexer("cpp")`, then install it in Scintilla with `SCI_SETILEXER`.
4. Enumerate available lexers with `GetLexerCount` and `GetLexerName` when needed. Do not introduce new dependencies on the deprecated numeric-ID conversion.
5. Run `TestLexers` after changing a lexer and verify examples against expected output.

## Important constraints

- The basic library requires a recent C++17 compiler; the test framework uses some C++20 features.
- A 32-bit or 64-bit application must use a matching Lexilla library.
- Pass the object returned by `CreateLexer` to Scintilla; C++ uses `ILexer5 *`, while C uses `void *`.
- `SetLibraryProperty` is optional and may be required for library initialization; `GetLibraryPropertyNames` optionally advertises the supported property names.
- `LexerNameFromID` is a deprecated migration affordance and will be removed; prefer lexer names.

## Sources

- https://www.scintilla.org/Lexilla.html
- https://www.scintilla.org/LexillaDoc.html
- https://github.com/ScintillaOrg/lexilla
- https://www.scintilla.org/License.txt
