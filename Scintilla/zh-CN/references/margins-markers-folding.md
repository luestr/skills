# Margins、Markers 与 Folding

Margins 可承载行号、折叠符号和调试器标记。为每个 margin 明确类型、宽度、mask、鼠标敏感性和空白区域行为；宽度应随 zoom/font 变化重新计算。

Markers 是行级 bit mask，可通过 `SCI_MARKERDEFINE`、颜色和 alpha 配置；点击 margin 时结合 `SCN_MARGINCLICK` 的 modifiers 决定折叠或调试操作。

折叠依赖 lexer 提供 fold levels。配置 `SCI_SETPROPERTY`、fold flags、自动折叠和折叠状态持久化时，区分 lexer 生成的 level 与用户展开/收起状态。文档重新加载或 lexer 改变后重新计算，避免缓存过期。
