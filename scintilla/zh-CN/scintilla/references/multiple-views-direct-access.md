# Multiple Views、Document Interface 与 Direct Access

Scintilla 支持多个 view 共享 document。通过 document interface 管理引用计数和共享 undo buffer；明确哪些属性属于 view（selection、scroll、zoom），哪些属于 document（text、styles、undo、save point）。关闭一个 view 前不要释放仍被其他 view 使用的 document。

Direct access 可在明确生命周期和线程安全边界后读取内部 document 数据。优先使用消息 API；只有性能分析证明必要时才使用 direct pointer，并在 document 修改、释放或重新分配后立即失效。

Background loading/saving 不应让后台线程直接操作 GUI 控件。使用快照、版本号和 GUI 线程提交，处理用户在 IO 期间编辑造成的冲突。
