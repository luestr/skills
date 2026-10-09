# Lexilla 集成与扩展

## C/C++ 集成

包含 `lexilla/include/Lexilla.h`。C++ 还需先包含 `scintilla/include/ILexer.h`。运行时加载时，应用负责确定 Lexilla 的搜索路径，并将文件扩展名或项目设置映射到 lexer name。加载共享库、解析必需符号、创建 lexer 和设置 `SCI_SETILEXER` 的每一步都应检查失败结果。

C++ 可使用 `access/LexillaAccess.cxx` 与 `LexillaAccess.h`。它可以直接编译进应用，也可以复制后按需定制，例如增加 code signature 检查；SciTE 使用该模块。它支持同时加载多个实现 Lexilla protocol 的共享库。

## Qt 集成

Qt 可以使用 `LexillaAccess` 或 `QLibrary`。Windows 的函数指针调用约定需要 `__stdcall`，其他平台使用普通函数指针。解析 `CreateLexer` 后，应检查 `QLibrary::resolve` 是否返回空指针；创建 lexer 后也应检查返回值，再将其指针转换为 Scintilla 所需的参数并调用 `SCI_SETILEXER`。`SCI_SETILEXER` 的第三个参数使用 Scintilla 的 `sptr_t` 表示 lexer 指针。

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

应用可以先调用 `GetLexerCount` 和 `GetLexerName` 发现库提供的 lexer。若使用 `SetLibraryProperty`，应在这些发现或创建调用前设置属性。应用还应定义共享库搜索位置，并针对库不存在、符号缺失、名称不支持和架构不匹配提供诊断。

## 新增 lexer 或新建库

实现与 Lexilla 相同的导出函数即可创建兼容库；库可以补充或替换内置 lexer。对于可选的初始化属性，实现 `SetLibraryProperty` 并可通过 `GetLibraryPropertyNames` 声明属性。未知属性应忽略。

可参考 `examples/SimpleLexer`。构建示例库后，使用 `CheckLexilla` 验证；C 示例的标准流程是进入 `examples/CheckLexilla` 后执行 `make`，再执行 `make check`。修改 Lexilla 自带 lexer 时，使用 `test/TestLexers` 验证词法结果。

## 其他实现

- [Scintillua](https://orbitalquark.github.io/scintillua/)：使用 [Lua](https://www.lua.org/) 与 [LPeg](https://www.inf.puc-rio.br/~roberto/lpeg/) 实现 lexer。
- [NppTreeSitter](https://github.com/Thorium/NppTreeSitter)：为 [Notepad++](https://notepad-plus-plus.org/) 封装 [Tree-sitter](https://tree-sitter.github.io/tree-sitter/)。

这些项目说明 Lexilla protocol 可作为 lexer 提供方与宿主应用之间的协议边界。
