# 编辑器功能配方

## 初始化顺序

1. 创建 Scintilla 控件并设置字体、编码、换行和 tab 约定。
2. 设置 lexer（Scintilla 5 中通常来自 Lexilla）。
3. 配置 style、margin、marker、indicator、folding 和 autocomplete。
4. 设置文本后调用 `SCI_SETSAVEPOINT`，或根据文件状态决定是否保留 dirty 状态。
5. 订阅 `SCN_MODIFIED`、保存点和用户交互通知。

## 样式与 lexer

每个 document byte 对应一个 style byte；style 是样式数组的索引。lexer 负责分类，宿主负责把 style 配置为字体、前景色、背景色、粗体、斜体等。不要把样式当作应持久化到源文件的内容。

## 选择、撤销与保存

使用 Scintilla 自己的 selection、undo/redo 和 save-point API，而不是混用已废弃的 Edit/RichEdit 消息。保存成功后调用 `SCI_SETSAVEPOINT`；收到 save-point reached/left 通知时更新标签、保存按钮和外部文档状态。

## 补全与 call tips

补全列表通常由宿主根据当前 lexer/语言服务提供；处理 `SCN_AUTOCSELECTION`、`SCN_AUTOCCOMPLETED` 和取消通知。若选择来自 fill-up character、Tab、Enter 或命令，读取对应的 `listCompletionMethod`，不要假设所有选择都来自鼠标。

## Margin、marker、indicator

- margin 适合行号、折叠和调试器 breakpoint marker。
- marker 表示行级状态；indicator 表示文本范围级别的错误、搜索或热点。
- 点击 indicator/hotspot 时从通知的 position 和 modifiers 推导操作，并遵守事件重入限制。

## 版本迁移

避免新的代码依赖 `WM_*`/`EM_*` 兼容消息、style-byte indicators、`SCI_SETSTYLEBITS` 等 deprecated/discouraged API。需要临时兼容旧代码时，在适配层集中封装并记录替换计划。
