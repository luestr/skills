# Lexer、Lexer Objects 与 Lexilla

Scintilla 5 将 lexer 从 Scintilla 移到 Lexilla。Lexilla 可构建为 shared/static library，应用可以使用 Lexilla，也可以使用提供相同函数的替代 lexer library。

## 两条使用路径

1. **内置或普通 lexer 路径**：根据发行版提供的 lexer 使用 `SCI_SETLEXER` 或 `SCI_SETLEXERLANGUAGE`，再配置 `SCI_SETPROPERTY` 和 `SCI_SETKEYWORDS`；是否需要显式加载 Lexilla library 取决于宿主部署方式。
2. **外部/替代 lexer library**：遵守 external lexer protocol，由宿主或支持它的应用载入并按名称取得 lexer。
3. **对象 lexer**：通过 Lexilla 的 `CreateLexer(const char *name)` 创建 `ILexer5 *`，再使用 `SCI_SETILEXER`。这是显式对象路径，不是普通 DLL 加载的必经步骤。

lexer 负责 styling 和通常的 folding；宿主应在 `SCN_STYLENEEDED` 或可见范围 styling 需求下及时提供样式。自定义 lexer 需要遵守 `ILexer5` 和 external lexer protocol 的生命周期、错误和释放规则。

迁移旧项目时检查 lexer library 路径、名称、properties/keywords、generated constants、ABI 和 Scintilla/Lexilla 版本。缺失 lexer 时保留 plain-text fallback，不能让编辑器失去基本编辑能力。

来源：https://www.scintilla.org/Lexilla.html、https://www.scintilla.org/LexillaDoc.html、https://www.scintilla.org/Scintilla5Migration.html。
