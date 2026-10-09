# Lexilla v5.5.1 Project Overview

Lexilla is a library of language lexers for the [Scintilla](https://www.scintilla.org/) editing component. The current release is v5.5.1, improving Baan, HTML, and XML. It includes complete source code and a license permitting use in free projects and commercial products; see the [License.txt](https://www.scintilla.org/License.txt) text.

## Use cases

Lexilla does not interact with display output, so it is independent of GUI toolkits. One shared library can be used by applications built with different GUI toolkits. It is available for Intel Win32, macOS, and Linux-compatible systems, and has run on Windows 10, macOS 10.13+, and Ubuntu 20.04. Since it has no GUI functionality, it is likely to run on earlier systems as well. The 32-bit or 64-bit architecture of Lexilla must match the host application; both architectures may need to be installed on the same system.

## Architecture choices

- **Static library**: linked into the application at build time.
- **Shared library**: loaded at runtime, allowing lexer libraries to be replaced or multiple implementations to coexist. Common suffixes are `.DLL` on Windows, `.so` on Linux, and `.dylib` on macOS; the application must define search locations and handle loading failures.
- **Extension library**: a third-party library can augment or replace Lexilla's lexers.

The lexer functionality was extracted from Scintilla so contributors can add language support and fix existing lexers more easily. Lexilla also defines a protocol for independent lexer providers.

## Release history

- `5.5.1`: improves Baan, HTML, and XML.
- `5.5.0`: improves Fortran and LaTeX.
- `5.4.9`: improves Assembler, C++, F#, LaTeX, Pascal, and Ruby.
- `5.4.8`: improves Batch, Forth, JavaScript, and JSON.
- `5.4.7`: adds the EscapeSequence lexer `escseq` and improves Errorlist, Makefile, Perl, and Progress.

## Version and links

- Current version: `5.5.1`
- Downloads: https://www.scintilla.org/LexillaDownload.html
- Documentation: https://www.scintilla.org/LexillaDoc.html
- Source: https://github.com/ScintillaOrg/lexilla
- Build status: https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check.yml
- Windows build status: https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check-win32.yml
- macOS build status: https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check-macos.yml
- Issues: https://github.com/ScintillaOrg/lexilla/issues
- History and contributors: https://www.scintilla.org/LexillaHistory.html
- Discussion: https://groups.google.com/forum/#!forum/scintilla-interest
- Privacy: https://www.scintilla.org/Privacy.html
