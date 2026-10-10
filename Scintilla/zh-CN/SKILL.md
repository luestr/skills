---
name: Scintilla
version: 5.6.4
description: 在将 Scintilla.dll 5.6.4 集成到 Windows 编辑器、调用其消息 API、配置语法样式和通知、使用 Lexilla 或构建该 DLL 时使用。
---

# Scintilla.dll v5.6.4

这是一个面向 Windows 编辑器集成的索引技能。Scintilla 是带完整源码和宽松许可证的源代码编辑控件；Windows 端主要通过窗口消息通信。先确认 DLL、头文件和宿主程序来自同一版本，再按主题阅读具体参考。

## 快速索引

- [概览与集成边界](references/overview.md)：组件职责、版本、平台、Lexilla、生命周期。
- [消息 API 与数据约定](references/api.md)：`SCI_*`、`SCN_*`、位置/长度、指针和缓冲区规则。
- [编辑器功能配方](references/editor-features.md)：文本、选择、撤销、样式、折叠、补全、标记和通知。
- [Windows 构建与诊断](references/windows-build.md)：C++17、动态/静态链接、类注册、构建宏和排错。
- [完整消息参考导航](references/messages-reference.md)：官方 `SCI_*`/`SCN_*` 分组、参数合同和通知规则。
- [API 主题目录](references/api-catalog.md)：按官方 Contents 逐项覆盖消息主题、功能边界和版本核对入口。
- [SCN_* 通知目录](references/notification-catalog.md)：通知字段、生命周期和 reentrancy 规则。
- [Lexer、Lexer Objects 与 Lexilla](references/lexer-objects.md)：普通 lexer library、`ILexer5` 和 `CreateLexer`。
- [平台 API 与输入输出细节](references/platform-apis.md)：Windows、GTK、Cocoa、Qt、编码、行尾、RTL 和图片。
- [Deprecated、Never-supported 与 Removed API](references/compatibility-catalog.md)：兼容、弃用、未支持和移除功能。
- [Images 图像 API](references/images.md)：RGBA、XPM、图像注册、尺寸、alpha 和生命周期。
- [GTK API](references/gtk.md)：widget、message、ID、资源释放和线程边界。
- [Building Scintilla 构建矩阵](references/building.md)：Windows、GTK、Cocoa、Qt、regex 和构建宏。
- [官方章节精确核对清单](references/precision-audit.md)：官方锚点、5.6.4 headers、平台条件和不确定性标记。
- [查找、替换与正则](references/search-replace.md)：target、flags、regex、增量搜索和结果高亮。
- [Styling 与 Lexilla](references/styling-lexers.md)：style、lexer、properties、keywords 和 Lexilla 边界。
- [Indicators、Annotations 与可视反馈](references/indicators-annotations.md)：范围诊断、行注释和 marker 反馈。
- [Margins、Markers 与 Folding](references/margins-markers-folding.md)：行号、折叠、调试器标记和 fold levels。
- [Autocompletion、User Lists 与 Call Tips](references/autocomplete-calltips.md)：补全、用户列表、签名提示和通知生命周期。
- [Multiple Views、Document Interface 与 Direct Access](references/multiple-views-direct-access.md)：共享 document、视图状态和后台 IO。
- [输入输出、平台与可访问性](references/input-output-platform.md)：编码、换行、剪贴板、拖放、打印、RTL、DPI 和平台后端。
- [版本、迁移与兼容性](references/version-migration.md)：5.6.4 变更、Lexilla 迁移、provisional 和 deprecated API。

## 使用规则

1. 以官方文档为准，不凭旧版 RichEdit 或第三方 wrapper 的习惯猜测参数。
2. 所有未使用的 `wParam`/`lParam` 传 `0`；指针参数必须确认生命周期、编码和缓冲区大小。
3. 文档以 byte 为单位描述位置和长度；不要把 UTF-8 code point 数量当作 Scintilla position。
4. Scintilla 5 已将 lexer 移至 Lexilla；需要语法分析时同时检查 Lexilla 的部署和版本。
5. 将 `SCN_MODIFIED`、`SCN_SAVEPOINTREACHED`、`SCN_SAVEPOINTLEFT` 等通知接入宿主状态管理，并在保存后调用 `SCI_SETSAVEPOINT`。

## 官方来源

- 主页：https://www.scintilla.org/
- API 文档：https://www.scintilla.org/ScintillaDoc.html
- 下载：https://www.scintilla.org/ScintillaDownload.html
- Lexilla：https://www.scintilla.org/Lexilla.html

## 交付前检查

- DLL、import library、headers 的版本均为 5.6.4。
- Windows 控件已注册，宿主窗口可创建并能收发消息。
- 文本读写覆盖空指针探测长度、NUL 结尾和非 NUL 结尾两类返回规则。
- 只使用稳定 API，或明确启用并接受 provisional/deprecated API 的兼容风险。
- 已在目标架构上验证 UTF-8、换行、撤销、只读和通知行为。
