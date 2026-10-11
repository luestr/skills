# Styling 与 Lexilla

Scintilla 将文本 byte 与 style byte 分离：lexer 产生 style，宿主配置 style 属性。style 可设置 foreground/background、font、size、bold、italic、underline、case、eol filled 等属性。清除或重算样式时不要把样式当作源文件内容保存。

Scintilla 5 将 lexers 移至 Lexilla。部署时同时安装匹配版本的 Lexilla shared/static library，设置 lexer、properties、keywords，并在需要时通过 `SCI_SETILEXER` 使用 `ILexer5`。外部 lexer 必须遵守官方 external lexer protocol。

样式化长文档时考虑 idle styling、visible-range styling、`SCN_STYLENEEDED` 和批量更新；避免在每个字符上进行昂贵的宿主回调。lexer 不存在或名称错误时，应显式报告并保留普通文本可编辑性。

来源：https://www.scintilla.org/Lexilla.html、https://www.scintilla.org/LexillaDoc.html、官方 `Lexer.txt`。
