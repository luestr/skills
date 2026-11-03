---
name: lexilla
description: 使用 Lexilla 为 Scintilla 集成、构建、发现和扩展语言 lexer。
metadata:
  version: 5.5.1
---

# Lexilla 技能索引

本技能面向需要在 C/C++、Qt 或其他宿主应用中集成 Lexilla v5.5.1 的开发者。Lexilla 是用于 Scintilla 的语言 lexer 库，可作为静态库链接，也可作为共享库在运行时加载。

## 官方资料索引

- [项目概览](references/lexilla-overview.md)：定位、发布历史、版本、平台、许可证和官方链接。
- [协议与 API](references/lexilla-protocol.md)：共享库导出函数、`CreateLexer`、lexer 发现和库属性。
- [构建与测试](references/lexilla-build-test.md)：Scintilla peer 目录、`make`、`nmake`、Visual C++ 和测试命令。
- [集成与扩展](references/lexilla-integration.md)：C/C++、Qt 集成，以及编写自定义 lexer 的边界。

### 官方项目资源

- [下载 Lexilla](https://www.scintilla.org/LexillaDownload.html)
- [Lexilla 历史与贡献](https://www.scintilla.org/LexillaHistory.html)
- [GitHub issues](https://github.com/ScintillaOrg/lexilla/issues)
- [构建检查 CI](https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check.yml)、[Win32 CI](https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check-win32.yml)、[macOS CI](https://github.com/ScintillaOrg/lexilla/actions/workflows/build-check-macos.yml)
- [SciTE](https://www.scintilla.org/SciTE.html) 与 [相关项目](https://www.scintilla.org/ScintillaRelated.html)
- [scintilla-interest 邮件列表](https://groups.google.com/forum/#!forum/scintilla-interest)：用于问题、缺陷和新版本讨论。

## 快速工作流

1. 准备 Lexilla v5.5.1 与 Scintilla 5+ 源码；构建时让名为 `scintilla` 的目录与 `lexilla` 同级。
2. 选择静态链接或运行时加载共享库；Windows 通常使用 `.DLL`，Linux 使用 `.so`，macOS 使用 `.dylib`。
3. 通过 `CreateLexer("cpp")` 等名称创建 lexer，并用 Scintilla 的 `SCI_SETILEXER` 设置当前 lexer。
4. 在加载库后按需调用 `GetLexerCount` / `GetLexerName` 枚举 lexer；不要在新代码中依赖已弃用的 numeric ID 转换。
5. 修改 lexer 后运行 `TestLexers`，确认示例输入与期望结果一致。

## 关键注意事项

- 基础库要求支持 C++17 的近期编译器；测试框架使用部分 C++20 特性。
- 32 位和 64 位应用必须匹配对应架构的 Lexilla 库。
- `CreateLexer` 返回的对象应直接交给 Scintilla；C++ 使用 `ILexer5 *`，C 使用 `void *`。
- `SetLibraryProperty` 是可选接口，可能用于库初始化；`GetLibraryPropertyNames` 是可选的属性名声明接口。调用顺序应满足具体库的初始化要求。
- `LexerNameFromID` 是迁移兼容接口，已弃用，未来会移除；优先使用 lexer name。

## 资料来源

- https://www.scintilla.org/Lexilla.html
- https://www.scintilla.org/LexillaDoc.html
- https://github.com/ScintillaOrg/lexilla
- https://www.scintilla.org/License.txt
