# Autocompletion、User Lists 与 Call Tips

`SCI_AUTOCSHOW` 显示宿主提供的候选项；配置分隔符、fill-up characters、取消行为、选择插入和排序。通过 `SCN_AUTOCSELECTION`、`SCN_AUTOCCANCELLED`、`SCN_AUTOCCOMPLETED` 处理完整生命周期。

`SCI_USERLISTSHOW` 用于自定义列表；`SCI_CALLTIPSHOW` 用于函数签名提示。处理 `SCN_CALLTIPCLICK` 时可切换重载签名。候选文本来自外部语言服务时，校验请求版本、caret position 和 document identity。

不要在通知中无条件再次触发 completion；避免重入和递归弹窗。列表为空、用户取消、填充字符提交和单候选自动选择都应有明确行为。
