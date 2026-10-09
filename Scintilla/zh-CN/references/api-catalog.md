# API 主题目录（Scintilla 5.6.4）

本文件按官方 `ScintillaDoc.html` 的 Contents 建立主题入口；它是 topic index，不替代官方逐条消息 reference。每个 `SCI_*` 的精确签名、返回值、默认值和版本标记必须以官方条目及 5.6.4 headers 为准；`SCI_SETxxxxx` 的 companion `SCI_GETxxxxx` 不能据名称自动推断参数。

| 官方主题 | 主要 API/概念 | 集成要点 |
|---|---|---|
| Text retrieval and modification | `SCI_GETTEXT`, `SCI_SETTEXT`, `SCI_GETLINE`, `SCI_GETTEXTRANGE`, `SCI_INSERTTEXT`, `SCI_DELETERANGE` | 文档位置/文本长度通常按 byte；逐条确认 NUL 和 buffer 规则 |
| Information | `SCI_GETLENGTH`, `SCI_GETLINECOUNT`, `SCI_GETMODIFY`, `SCI_GETDIRECTFUNCTION` | 返回值语义以消息条目为准 |
| By character or UTF-16 code unit | `SCI_POSITIONRELATIVE`、`SCI_POSITIONRELATIVECODEUNITS`、`SCI_COUNTCHARACTERS`、`SCI_COUNTCODEUNITS`；分别核对 byte、字符和 UTF-16 code unit 语义 | DBCS/UTF-8 与 UTF-16 code unit 不可混算 |
| Error handling | `SCI_GETSTATUS`, `SC_STATUS_*` | 检查 `SC_STATUS_OK`、`SC_STATUS_FAILURE`、`SC_STATUS_BADALLOC` 和官方定义的 `SC_STATUS_WARN_*`；不要把文档越界状态误写成 status 常量 |
| Selection | anchor/current position、`SCI_SETSEL`、`SCI_GETSELTEXT`、`SCI_SETSELECTIONNSTART` | 多选时逐个 selection 处理 |
| Multiple Selection and Virtual Space | `SCI_SETMULTIPLESELECTION`、`SCI_SETADDITIONALSELECTIONTYPING`、virtual space API | 区分主 selection、additional selections 和 caret |
| Overtype | `SCI_SETOVERTYPE`、`SCI_GETOVERTYPE` | 与 selection、IME、替换操作共同测试 |
| Searching and replacing | target API、`SCI_SEARCHINTARGET`、`SCI_REPLACETARGET`、`SCI_REPLACETARGETRE` | 处理空匹配、方向、target 边界和 regex 错误 |
| Cut, copy and paste | `SCI_CUT`、`SCI_COPY`、`SCI_PASTE`、`SCI_CANPASTE`、`SCI_CLEAR` | 使用 Scintilla clipboard API 或明确宿主菜单策略 |
| Undo and Redo | `SCI_UNDO`、`SCI_REDO`、`SCI_BEGINUNDOACTION`、`SCI_ENDUNDOACTION` | 事务边界与 save point 一致 |
| Undo save and restore | `SCI_EMPTYUNDOBUFFER`、`SCI_SETUNDOSAVEPOINT`、`SCI_GETUNDOSEQUENCE` | 保存/加载及多视图回归测试 |
| Change history | `SCI_SETCHANGEHISTORY`、history markers | 区分修改历史与 undo 栈 |
| Scrolling and automatic scrolling | first visible line、x offset、`SCI_SCROLLCARET`、autoscroll | scroll 变化可能触发 `SCN_UPDATEUI` |
| White space | `SCI_SETVIEWWS`、`SCI_SETWHITESPACESIZE`、`SCI_SETEXTRAASCENT/DESCENT` | view white space 与 document text 分离 |
| Cursor | `SCI_SETCARETFORE`、`SCI_SETCARETWIDTH`、`SCI_SETCARETPERIOD`、`SCI_SETCARETLINEVISIBLE` | caret 是 view 状态 |
| Mouse dwell / hover notifications | `SCI_SETMOUSEDWELLTIME`、dwell notifications；mouse capture 使用宿主平台 API 时单独处理 | `SCI_SETMOUSEDWELLTIME` 不执行 mouse capture，遵守平台事件循环 |
| Line endings | `SCI_SETEOLMODE`、`SCI_CONVERTEOLS`、`SCI_GETLINEENDTYPES` | 处理 CR、LF、CRLF 和 CP/M 位置约束 |
| Words | `SCI_WORDSTARTPOSITION`、`SCI_WORDENDPOSITION`、`SCI_SETWORDCHARS` | lexer/word character 规则需明确 |
| Styling | `SCI_STARTSTYLING`、`SCI_SETSTYLING`、`SCI_CLEARDOCUMENTSTYLE` | style byte 是派生数据 |
| Style definition | `SCI_STYLESETFORE/BACK/FONT/SIZE/BOLD/ITALIC` | style 0-255 与 extended styles 分开管理 |
| Element colours | `SCI_SETELEMENTCOLOUR`、`SCI_GETELEMENTCOLOUR` | UI element colour 不等同 lexer style colour |
| Selection, caret, hotspot styles | selection colours、caret、hotspot style | hotspot handler 有 reentrancy 限制 |
| Character representations | `SCI_SETREPRESENTATION`、`SCI_SETREPRESENTATIONAPPEARANCE` | 显示替换不改变 document bytes |
| Margins | `SCI_SETMARGINTYPEN/WIDTHN/MASKN/SENSITIVEN` | margin mask 与 marker 类型匹配 |
| Annotations | `SCI_ANNOTATIONSETTEXT/STYLES` | 普通 annotation 与 EOL annotation 分开 |
| End of Line Annotations | `SCI_EOLANNOTATIONSETTEXT/STYLES` | 测试换行、折叠和可见宽度 |
| Other settings | edge、extra ascent/descent、technology、phases draw | 逐项确认平台支持和默认值 |
| Brace highlighting | `SCI_BRACEHIGHLIGHT`、`SCI_BRACEBAD`、`SCI_BRACEMATCH` | position 无效时显示明确状态 |
| Tabs and Indentation Guides | `SCI_SETTABWIDTH`、`SCI_SETUSETABS`、`SCI_SETINDENT`、guides | tab/space 策略需与 formatter 一致 |
| Markers | `SCI_MARKERDEFINE`、`SCI_MARKERADD/DELETE`、marker handle | 行级 bit mask，适合 breakpoint/folding |
| Indicators | `SCI_INDICSETSTYLE/FORE/ALPHA`、`SCI_INDICATORFILLRANGE` | 范围级诊断，不能使用 style-byte indicators |
| Autocompletion | `SCI_AUTOCSHOW`、`SCI_AUTOCCANCEL`、`SCI_AUTOCSELECT` | 处理 completion notification 生命周期 |
| User lists | `SCI_USERLISTSHOW` | 自定义 listType 与 selection 通知 |
| Call tips | `SCI_CALLTIPSHOW/CANCEL/SETBACK` | overload navigation 与 click notification |
| Keyboard commands | `SCI_NULL`、command messages | 命令可由键盘、菜单或宿主触发 |
| Key bindings | `SCI_ASSIGNCMDKEY`、`SCI_CLEARCMDKEY`、`SCI_CLEARALLCMDKEYS` | modifiers/key code 需按平台定义 |
| Popup edit menu | `SCI_USEPOPUP` | 宿主可禁用默认菜单并提供自定义菜单 |
| Macro recording | `SCI_STARTRECORD`、`SCI_STOPRECORD`、`SCN_MACRORECORD` | 记录消息而非任意宿主状态 |
| Printing | `SCI_FORMATRANGE`、`SCI_SETPRINTMAGNIFICATION`、print colours | device context、分页和 selection 范围需管理 |
| Direct access | `SCI_GETDIRECTFUNCTION`、`SCI_GETDIRECTPOINTER` | 仅在生命周期/线程边界明确时使用 |
| Multiple views | `SCI_CREATEDOCUMENT`、`SCI_ADDREFDOCUMENT`、`SCI_RELEASEDOCUMENT`、`SCI_SETDOCPOINTER` | document 共享，selection/scroll 通常 view-local |
| Background loading and saving | 文档规定的 background load/save 消息、save point 和线程边界 | 以官方消息条目和 headers 为准；worker thread 不直接操作控件 |
| Document interface | `IDocumentEditable`、document reference、相关 headers 和引用计数 | 按官方 Document interface 章节与 headers 核对创建、引用、释放顺序 |
| Folding | fold levels、`SCI_SETFOLDLEVEL`、`SCI_SETFOLDEXPANDED`、`SCI_FOLDALL` | lexer 生成 level，用户状态另行保存 |
| Line wrapping | `SCI_SETWRAPMODE`、visual flags、wrap start indent | visual line 不等于 document line |
| Zooming | `SCI_SETZOOM`、`SCI_GETZOOM` | zoom 触发 `SCN_ZOOM`，重算 margin 宽度 |
| Long lines | `SCI_SETEDGEMODE`、`SCI_SETEDGECOLUMN` 和 long-line display/scroll 设置 | 长行策略兼顾性能和水平滚动 |
| Accessibility | accessibility support and notifications | 目标平台上验证 screen reader 与 caret/selection |
| Lexer | lexer name、properties、keywords、style/fold | Scintilla 5 使用 Lexilla |
| Lexer objects | `ILexer5`、`SCI_SETILEXER`、`CreateLexer` | 直接对象路径不等同普通 DLL 自动加载 |
| Notifications | `SCNotification`、`SCN_*` | 只读取当前通知定义的字段 |
| Images | RGBA、XPM、`SCI_RGBAIMAGESETWIDTH/HEIGHT`、marker/autocomplete images | RGBA 为 RGBA bytes，不预乘 alpha |
| GTK | `scintilla_new`、`scintilla_send_message`、`scintilla_release_resources` | GTK 生命周期与 Windows 控件不同 |
| Provisional messages | `SCI_DISABLE_PROVISIONAL` | 可能变更或移除 |
| Deprecated messages | `INCLUDE_DEPRECATED_FEATURES`、旧 Edit/RichEdit compatibility | 新代码使用 Scintilla API |
| Never-supported edit messages | 不支持的 `EM_*` | 无效果，不要期待 RichEdit 行为 |
| Removed features | `SC_CP_DBCS`、palette、style-byte indicators | 必须从调用代码移除 |
| Building Scintilla | C++17、build scripts、regex implementation、macros | DLL/headers/import library 同版本 |

来源：https://www.scintilla.org/ScintillaDoc.html
