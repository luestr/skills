# 版本、迁移与兼容性

本技能目标版本为 Scintilla.dll v5.6.4。官方主页记录 v5.6.4 为 Qt pixel-aligned fractional scaling 版本；5.6.3 涉及 undo/redo 在 additional views 中恢复 selection/scroll，5.6.2 增加 `SC_STATUS_OUTSIDE_DOCUMENT` 并更早阻止越界插入，5.6.1 修复 `SCI_CONVERTEOLS` 回归并增加 tab blob 绘制模式，5.6.0 修复窗口过窄崩溃。

Scintilla 5 的重大边界是 lexer 移至 Lexilla。迁移旧项目时检查构建脚本、DLL 搜索路径、lexer 加载、headers 和 generated constants。

Provisional API 可能改变或移除；可定义 `SCI_DISABLE_PROVISIONAL` 排除。Deprecated/discouraged API（如旧 `WM_*`/`EM_*`、`SCI_SETSTYLEBITS`、style-byte indicators）不要用于新代码。升级前比较官方文档、headers、import library 和运行时 DLL，进行 ABI/行为回归测试。

来源：https://www.scintilla.org/、https://www.scintilla.org/Scintilla5Migration.html、https://www.scintilla.org/ScintillaHistory.html。
