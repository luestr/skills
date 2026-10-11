# Lexilla v5.5.1 项目概览

Lexilla 是用于 [Scintilla](https://www.scintilla.org/) 编辑组件的语言 lexer 库。当前发布版本为 v5.5.1，改进了 Baan、HTML 和 XML；项目提供完整源代码及允许免费项目和商业产品使用的许可证，许可证文本见 [License.txt](https://www.scintilla.org/License.txt)。

## 适用场景

Lexilla 不处理显示，因此不绑定 GUI toolkit。同一个共享库可供使用不同 GUI toolkit 的应用复用。它支持 Intel Win32、macOS 和 Linux 兼容系统，并已在 Windows 10、macOS 10.13+、Ubuntu 20.04 上运行。由于它没有 GUI 功能，通常也可能在更早的系统上运行。宿主应用与 Lexilla 的 32 位或 64 位架构必须匹配；同一台机器在需要时可以同时部署两种架构的库。

## 架构选择

- **静态库**：构建时链接进应用，部署简单。
- **共享库**：运行时加载，可替换 lexer 库，也允许多个实现 Lexilla protocol 的库并存。常见扩展名为 Windows `.DLL`、Linux `.so`、macOS `.dylib`；应用需要定义库搜索位置并处理加载失败。
- **扩展库**：第三方库可以补充或替换 Lexilla 提供的 lexer。

Lexilla 从 Scintilla 中拆出，是为了让贡献者更容易新增语言支持和修复现有 lexer，同时定义了可由其他项目实现的协议。

## 发布历史

- `5.5.1`：改进 Baan、HTML 和 XML。
- `5.5.0`：改进 Fortran 和 LaTeX。
- `5.4.9`：改进 Assembler、C++、F#、LaTeX、Pascal 和 Ruby。
- `5.4.8`：改进 Batch、Forth、JavaScript 和 JSON。
- `5.4.7`：新增 EscapeSequence lexer `escseq`，并改进 Errorlist、Makefile、Perl 和 Progress。

## 版本与链接

- 当前版本：`5.5.1`
- 下载：https://www.scintilla.org/LexillaDownload.html
- 文档：https://www.scintilla.org/LexillaDoc.html
- 源码：https://github.com/ScintillaOrg/lexilla
- 构建状态：https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check.yml
- Windows 构建状态：https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check-win32.yml
- macOS 构建状态：https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check-macos.yml
- 问题追踪：https://github.com/ScintillaOrg/lexilla/issues
- 历史与贡献者：https://www.scintilla.org/LexillaHistory.html
- 讨论：https://groups.google.com/forum/#!forum/scintilla-interest
- 隐私：https://www.scintilla.org/Privacy.html
