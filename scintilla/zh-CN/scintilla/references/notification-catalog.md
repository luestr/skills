# SCN_* 通知目录

`SCNotification` 是 union-like 结构：不同通知只保证部分字段有效。先判断 `nmhdr.code`，再读取该通知规定的字段；不要把未定义字段当作默认值。

| 通知 | 重点字段/用途 |
|---|---|
| `SCN_STYLENEEDED` | `position`：需要 styling 的终点 |
| `SCN_CHARADDED` | `ch`：加入的字符 |
| `SCN_SAVEPOINTREACHED/LEFT` | 文档 dirty/save 状态 |
| `SCN_MODIFIED` | modification type、position、length、text、linesAdded、line、foldLevelNow/Prev |
| `SCN_MODIFYATTEMPTRO` | 只读文档的修改尝试 |
| `SCN_UPDATEUI` | selection、content、vertical/horizontal scroll、zoom 等 UI 变化标志 |
| `SCN_MARGINCLICK` | margin、position、modifiers |
| `SCN_NEEDSHOWN` | 需要显示的范围 |
| `SCN_PAINTED` | 一次绘制完成 |
| `SCN_DOUBLECLICK` | position、line、modifiers |
| `SCN_MACRORECORD` | 被记录的 message、wParam、lParam |
| `SCN_KEY` | key、modifiers |
| `SCN_DWELLSTART/END` | position、x、y |
| `SCN_ZOOM` | zoom 变化；无额外字段 |
| `SCN_HOTSPOTCLICK/DOUBLECLICK/RELEASECLICK` | position、modifiers；handler 避免不允许的 selection/caret 修改 |
| `SCN_INDICATORCLICK/RELEASE` | position、modifiers |
| `SCN_CALLTIPCLICK` | 使用 `position` 获取文档位置；使用 `ch` 判断 call tip 上箭头、下箭头或其他区域 |
| `SCN_AUTOCSELECTION` | position、text、ch、listCompletionMethod；可在返回前取消插入 |
| `SCN_AUTOCCANCELLED` | completion 被取消 |
| `SCN_AUTOCCHARDELETED` | completion 激活时删除字符 |
| `SCN_AUTOCCOMPLETED` | completion 已插入；`position`、`text`、`listCompletionMethod` 等字段按官方结构读取，不能假设所有字段在每个阶段都有效 |
| `SCN_AUTOCSELECTIONCHANGE` | listType、text、position |
| `SCN_USERLISTSELECTION` | listType、text |
| `SCN_FOCUSIN/OUT` | focus 状态，无额外字段 |

`SCN_URIDROPPED` | URI/file-drop 文本位于 `text`；按官方编码和生命周期规则复制后再异步处理 |

通知处理原则：GUI 线程内快速返回；异步结果携带 document revision；遵循官方对 hotspot、completion 和 macro notification 的 reentrancy 规则。

来源：https://www.scintilla.org/ScintillaDoc.html#Notifications
