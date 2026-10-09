# Indicators、Annotations 与可视反馈

- **Indicators**：附着于文本范围，适合错误、搜索命中、诊断和 hotspot；配置 indicator style、颜色、alpha、under 和 hover 行为。
- **Annotations**：显示在线号附近或行尾，适合诊断说明；区分普通 annotation 与 EOL annotation，并验证长文本、换行和颜色可读性。
- **Markers**：附着于行，适合 breakpoint、当前行、折叠状态和调试器标记；通过 margin 显示。

点击 indicator/hotspot 时从 `SCN_INDICATORCLICK`、`SCN_HOTSPOTCLICK` 的 position/modifiers 读取上下文。异步诊断更新前校验 document revision，避免旧结果覆盖新文本。不要使用已移除的 style-byte indicators；应使用标准 indicators。
