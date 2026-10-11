# 构建与测试 Lexilla

## 编译器与架构要求

基础 Lexilla library 需要支持 C++17 的近期编译器；测试框架包含部分 C++20 特性，测试构建是否需要 C++20 支持取决于所使用的工具链。构建目标的 32/64 位架构必须与宿主应用匹配。

## 前置目录

Lexilla 构建需要 Scintilla 的头文件。常见布局是：`lexilla` 与 `scintilla` 作为同级目录，且 `scintilla` 为 Scintilla 5+ 副本。

## 构建命令

在 `lexilla/src` 中：

```text
make                 # gcc 或 clang
nmake -f lexilla.mak # MSVC
```

仓库也提供 Visual C++ 项目 `src/Lexilla.vcxproj` 和 Xcode 项目 `src/Lexilla/Lexilla.xcodeproj`。Windows、macOS 与 Linux 构建不绑定 GUI toolkit。

## 测试命令

在 `lexilla/test` 中：

```text
make test
nmake -f testlexers.mak test
```

也可以运行 `scripts/RunTest.sh` 或 `scripts/RunTest.bat`；这些脚本使用 gcc/clang 构建并运行测试，不使用 MSVC。Visual C++ 测试项目为 `test/TestLexers.vcxproj`。完整的 `TestLexers` 用法见 `test/README`。

成功测试会显示类似 `Lexing ...`。错误通常指出示例文件、行号以及实际结果与期望结果的差异，例如 `C:\\u\\hg\\lexilla\\test\\examples\\python\\x.py:1: is different`。新增或修改 lexer 时，应把测试样例和期望输出一起检查。

## C 示例

`examples/CheckLexilla` 展示从 C 访问 Lexilla，使用 `make` 构建并通过 `make check` 运行。测试 lexer 实现的完整说明见 `test/README`。
