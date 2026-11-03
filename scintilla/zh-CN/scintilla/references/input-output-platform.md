# 输入输出、平台与可访问性

文档覆盖 UTF-8/DBCS、line endings、clipboard、drag and drop、keyboard commands、key bindings、mouse capture、printing、images、accessibility、GTK 和其他平台后端。Windows 宿主尤其要验证 Unicode 输入、换行转换、剪贴板格式、拖放文件路径和打印分页。

Scintilla 对 Arabic/Hebrew 等 RTL 语言只有有限的 experimental support；不要把“显示正确”当作 selection、caret 和 editing 交互完整。高 DPI/zoom、比例字体、RGBA/XPM 图片和 Direct2D/DirectWrite 后端也应在目标平台测试。

源码构建可使用 `DISABLE_D2D` 控制 Windows 图形后端；平台差异不能通过假设所有 GTK/Qt/macOS 消息行为相同来隐藏。
