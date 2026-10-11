# Lexilla protocol 与 API

Lexilla protocol 是 external lexer protocol 的超集。实现 Lexilla protocol 的共享库可以提供以下接口：

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

## 接口分类

- `GetLexerCount`、`GetLexerName` 和 `GetLexerFactory` 构成早期 external lexer protocol 的前三个接口。
- `CreateLexer` 是现代应用创建指定 lexer 的主要入口。
- `LexerNameFromID`、`GetLibraryPropertyNames`、`SetLibraryProperty` 和 `GetNameSpace` 是可选接口。加载共享库时，调用方应检查这些符号是否存在。
- `LexerNameFromID` 已弃用，仅用于帮助旧应用从 numeric ID 迁移到名称；它会在未来版本移除，不应用于新代码。

## 推荐调用路径

`CreateLexer` 是主要入口。应用按名称请求 lexer，例如 `CreateLexer("cpp")`，然后将结果传给 Scintilla 的 `SCI_SETILEXER`。返回的 lexer 通常直接交给 Scintilla；多数客户端不需要调用 `ILexer5` 方法。C++ 中返回类型为 `ILexer5 *`；C 中不包含 `ILexer.h`，使用 `void *`。

需要发现库能力时，先调用 `GetLexerCount`，再对 `0` 到 `count - 1` 调用 `GetLexerName`。如果库实现 `SetLibraryProperty`，可通过 `GetLibraryPropertyNames` 获取以换行分隔的属性名。应在调用 `GetLexerCount` 或 `CreateLexer` 前设置所需的初始化属性；库应忽略不理解的属性。例如，使用 XML language definitions 的库可能需要先调用 `SetLibraryProperty("definitions.directory", "/usr/share/xeditor/language-definitions")`。属性的定义、保存和用户界面呈现由应用决定。

`GetNameSpace` 可为同名 lexer 提供命名空间，例如 `xmllexers.cpp`，从而避免不同提供方之间的名称冲突。未限定的 `cpp` 请求可能由任一提供方满足，而 `xmllexers.cpp` 可明确指定提供方。`LexerNameFromID(SCLEX_CPP)` 的迁移结果示例为 `"cpp"`。

## 兼容性

前三个函数来自早期 external lexer protocol，因此支持该旧协议的应用可以加载 Lexilla。`GetLexerFactory` 现在很少直接使用；现代应用应优先调用 `CreateLexer`。`LexerFactoryFunction` 是无参数并返回 `ILexer5 *` 的函数指针类型，多数客户端不需要直接调用它。

类型定义来自 Scintilla 的 `include/ILexer.h` 与 Lexilla 的 `include/Lexilla.h`。C++ 应先包含 `ILexer.h`，再包含 `Lexilla.h`；C 代码不应包含 C++ 的 `ILexer.h`。
