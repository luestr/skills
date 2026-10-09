# 查找、替换与正则

Scintilla 的查找替换以 target range 为核心：先用 `SCI_SETTARGETSTART`/`SCI_SETTARGETEND` 设置范围，再调用 `SCI_SEARCHINTARGET`；替换使用 `SCI_REPLACETARGET` 或 `SCI_REPLACETARGETRE`。循环搜索时必须处理 `-1`、空匹配、方向和 target 边界，避免无限循环。

## flags 与正则

使用 `SCI_SETSEARCHFLAGS` 配置 whole word、match case、word start、正则和双向搜索等行为；正则替换的捕获组语法以官方文档为准。不要把宿主语言的 regex 语法直接假定为 Scintilla regex 语法。

## 增量搜索

增量搜索应保存原始 target、selection 和滚动状态；每次输入重新设置 target，处理未找到、selection 更新和撤销边界。大文档搜索不要在 GUI 线程执行阻塞式全量循环。

## 高亮结果

用 indicators 或 markers 展示结果，避免修改 style byte。结果过期时清除旧 indicator range；跨文档或异步搜索必须校验 document 身份和版本号。
