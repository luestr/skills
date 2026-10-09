# Deprecated、Never-supported 与 Removed API

## Deprecated / compatibility

官方文档列出仍支持但应替换的旧 Edit/RichEdit 消息，例如 `WM_GETTEXT`、`WM_SETTEXT`、`EM_GETLINE`、`WM_UNDO`、`EM_SETSEL`、`EM_FINDTEXT` 和 `EM_FORMATRANGE`。新代码应使用对应的 Scintilla `SCI_*` API，而不是依赖兼容层。

定义 `INCLUDE_DEPRECATED_FEATURES` 后才暴露部分旧特性，如 `SCI_SETKEYSUNICODE`、`SCI_SETTWOPHASEDRAW` 和 `SCI_SETSTYLEBITS`。`SCI_SETSTYLEBITS`/style-byte indicators 不应加入新代码；标准 indicators 是替代方案。

## Never-supported

Scintilla 不支持许多 RichEdit 专用消息，包括 word-break procedure、paragraph/character format、OLE、stream IO、IME options、event mask、password character 和 `EM_DISPLAYBAND`。这些消息无效果，不能按 RichEdit 语义使用。

## Removed

已完全移除的内容包括 `SC_CP_DBCS`、palette mode (`SCI_SETUSEPALETTE`) 和 style-byte indicators。应使用 `SCI_SETCODEPAGE`、标准 indicators 和当前绘制 API；升级时从调用代码删除 removed symbols。

## Provisional

Provisional messages 可能改变或移除；需要稳定 API 的构建可定义 `SCI_DISABLE_PROVISIONAL`。升级后必须重新检查 headers、generated constants 和行为测试。

来源：https://www.scintilla.org/ScintillaDoc.html#DeprecatedMessages
