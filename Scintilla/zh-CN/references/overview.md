# 概览与集成边界

## 定位

Scintilla 是可嵌入的源代码编辑控件，不是完整 IDE。它提供文本编辑、语法样式、错误指示器、代码补全、call tips、折叠、markers 和多视图等能力。宿主负责文件 IO、项目模型、命令系统和语言服务。

v5.6.4 的主页特别注明 Qt 的 pixel-aligned fractional scaling；当前 5.* 分支要求支持 C++17 的编译器。

## Windows 集成

Windows 版本是 Windows Control，主要接口是窗口消息。使用动态 DLL 时加载 Scintilla DLL 并创建 `Scintilla` 窗口类；使用静态库时链接 `bin/libscintilla.lib`，并调用 `Scintilla_RegisterClasses`。独立 DLL 需要包含 `ScintillaDLL.cxx` 提供 `DllMain` 和注册函数。

消息函数的两个参数相当于 `wParam` 和 `lParam`，其宽度足以容纳指针；返回值同样可容纳指针。不要把它们无条件缩窄为 `int`。

## Lexilla 边界

从 Scintilla 5.0 起 lexer 已拆到 Lexilla。Scintilla 负责 GUI 和调用 lexer，Lexilla 提供 lexer，可作为 shared 或 static library。部署语法高亮时同时检查 Lexilla DLL、lexer 名称和 `SCI_SETILEXER`/外部 lexer 协议。

## 生命周期

销毁控件前释放宿主持有的资源；不要保存只在一次消息调用期间有效的内部指针。多视图共享 document 时，明确区分 view 状态与 document 状态，并验证撤销、选择和滚动位置的预期。
