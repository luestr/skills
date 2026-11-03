# 官方章节精确核对清单

本文件用于防止把主题摘要误当作完整 API reference。ScintillaDoc 的每个 Contents 条目都必须逐条对照官方锚点、5.6.4 headers 和实际平台构建；本地技能提供导航、语义提醒和测试检查点，不复制自动生成的全部正文。

## 必核对主题

- `Text retrieval and modification`：NUL 结尾、长度探测、`Sci_TextRange`/`Sci_TextRangeFull`。
- `Information`：返回值、direct function/pointer 和 document byte 语义。
- `By character or UTF-16 code unit`：`SCI_POSITIONRELATIVE`、`SCI_POSITIONRELATIVECODEUNITS`、`SCI_COUNTCHARACTERS`、`SCI_COUNTCODEUNITS` 分开验证。
- `Error handling`：只使用 headers 中存在的 `SC_STATUS_*`；不要从版本新闻或错误描述自行创造常量。
- `Notifications`：按 `nmhdr.code` 读取 `SCNotification` 字段，记录指针有效期和 reentrancy。
- `Images`：核对 `SCI_REGISTERIMAGE`、`SCI_CLEARREGISTEREDIMAGES`、RGBA/XPM 尺寸和资源生命周期。
- `GTK`：核对 widget 创建、ID、message 返回值和全部 widget 销毁后的资源释放。
- `Building Scintilla`：核对 README、build files、编译器、regex 选项、导出、注册和架构。

## 输出要求

引用 API 时保留官方名称和链接；如果某行为依赖平台、编译宏或版本，明确写出条件。无法从官方页面或 5.6.4 headers 证明的内容，标为“需核对”，不要写成确定的可调用 API。

官方文档：https://www.scintilla.org/ScintillaDoc.html
