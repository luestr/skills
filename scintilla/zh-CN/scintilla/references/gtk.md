# GTK API

官方 GTK 入口包含：

- `GtkWidget *scintilla_new()`：创建 Scintilla widget，可加入 GTK container。
- `void scintilla_set_id(ScintillaObject *sci, uptr_t id)`：设置通知中的 `idFrom`，等价于 `SCI_SETIDENTIFIER`。
- `sptr_t scintilla_send_message(ScintillaObject *sci, unsigned int iMessage, uptr_t wParam, sptr_t lParam)`：发送任意 Scintilla message，返回值为 `sptr_t`。
- `void scintilla_release_resources()`：所有 Scintilla widget 销毁后释放剩余全局资源。

GTK 版本使用与 Windows 类似的 message API，但 widget、container、main loop 和资源释放遵循 GTK 生命周期。不要在 worker thread 直接操作 widget；消息调用应回到拥有 GTK widget 的线程。支持的 GTK 版本、glib 依赖和构建宏必须以 Scintilla v5.6.4 源码 README/build configuration 为准；不能仅根据通用 API 页面推断。

初始化顺序通常是创建 widget、加入 container、设置 ID、发送 Scintilla 配置消息、连接宿主通知，然后进入 GTK main loop。销毁全部 widget 后再调用 `scintilla_release_resources()`。

来源：https://www.scintilla.org/ScintillaDoc.html#GTK
