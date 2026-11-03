# Building and testing Lexilla

## Compiler and architecture requirements

The basic Lexilla library requires a recent compiler supporting C++17. The test framework contains some C++20 features; whether C++20 support is required for the test build depends on the toolchain. The 32-bit or 64-bit build must match the host application.

## Required layout

Lexilla needs Scintilla headers. Conventionally, `lexilla` and a Scintilla 5+ copy named `scintilla` are peer directories.

## Build commands

From `lexilla/src`:

```text
make                 # gcc or clang
nmake -f lexilla.mak # MSVC
```

Visual C++ and Xcode projects are also available as `src/Lexilla.vcxproj` and `src/Lexilla/Lexilla.xcodeproj`. Builds on Windows, macOS, and Linux are independent of GUI toolkits.

## Test commands

From `lexilla/test`:

```text
make test
nmake -f testlexers.mak test
```

`scripts/RunTest.sh` and `scripts/RunTest.bat` build and run tests with gcc/clang, not MSVC. The Visual C++ test project is `test/TestLexers.vcxproj`. See `test/README` for the complete `TestLexers` usage.

Successful runs display messages such as `Lexing ...`. Failures normally identify the example file and line where actual and expected results differ, for example `C:\\u\\hg\\lexilla\\test\\examples\\python\\x.py:1: is different`. When adding or changing a lexer, review both the sample input and expected output.

## C example

`examples/CheckLexilla` demonstrates accessing Lexilla from C. Build it with `make` and run it with `make check`. See `test/README` for the full TestLexers instructions.
