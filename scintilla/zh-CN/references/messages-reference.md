# 完整消息参考导航

官方 `ScintillaDoc.html` 按功能列出 `SCI_*` 消息和 `SCN_*` 通知；本技能不复制数千行生成 API，而是提供完整导航和调用规则。使用某个消息前必须打开官方锚点确认参数、返回值、introduced/deprecated 状态。

## 官方消息分组

- 文本读写：`SCI_GETTEXT`、`SCI_SETTEXT`、`SCI_GETTEXTRANGE`、`SCI_INSERTTEXT`、`SCI_DELETERANGE`、`SCI_APPENDTEXT`
- 文档信息：`SCI_GETLENGTH`、`SCI_GETCHARAT`、`SCI_GETSTYLEAT`、`SCI_LINEFROMPOSITION`、`SCI_POSITIONFROMLINE`
- 选择与光标：`SCI_GETSELECTIONSTART`、`SCI_SETSEL`、`SCI_SETMULTIPLESELECTION`、`SCI_SETADDITIONALSELECTIONTYPING`
- 查找替换：`SCI_SETTARGETSTART`、`SCI_SETTARGETEND`、`SCI_SEARCHINTARGET`、`SCI_REPLACETARGET`
- 撤销：`SCI_UNDO`、`SCI_REDO`、`SCI_EMPTYUNDOBUFFER`、`SCI_BEGINUNDOACTION`、`SCI_ENDUNDOACTION`
- 视图：滚动、可见行、缩放、换行、长行、caret 和多视图消息
- 样式：`SCI_STYLESETFORE`、`SCI_STYLESETBACK`、`SCI_STYLESETFONT`、`SCI_SETLEXER`
- UI 标注：margins、markers、indicators、annotations、EOL annotations
- 交互：剪贴板、键盘、鼠标、拖放、popup menu、macro、printing
- 高级：document interface、direct access、background loading/saving、images、accessibility

## 参数合同

`wParam`/`lParam` 的宽度必须使用 `WPARAM`/`LPARAM` 或 `uptr_t`/`sptr_t`。未使用参数传 `0`。`position` 与文本长度按 byte 计；`line` 从 0 开始；`INVALID_POSITION` 为 `-1`。输出缓冲区是否 NUL-terminated、是否可用 `NULL` 探测长度，必须逐条确认。

## 通知合同

处理 `SCN_MODIFIED`、`SCN_UPDATEUI`、`SCN_CHARADDED`、`SCN_SAVEPOINTREACHED`、`SCN_SAVEPOINTLEFT`、`SCN_AUTOCSELECTION`、`SCN_DWELLSTART`、`SCN_ZOOM`、`SCN_FOCUSIN/OUT` 等通知时读取 `SCNotification` 中该通知实际使用的字段，不要假设所有字段有效。遵守文档注明的 reentrancy 限制。

## 来源

完整列表和每个消息的正式签名以 https://www.scintilla.org/ScintillaDoc.html 为准；C++ 类型安全封装参考 `ScintillaTypes.h`、`ScintillaMessages.h`、`ScintillaStructures.h`、`ScintillaCall.h`。
