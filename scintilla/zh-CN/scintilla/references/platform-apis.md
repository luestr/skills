# 平台 API 与输入输出细节

## Windows

Windows 版本是 Windows Control，主要通过消息工作。动态 DLL 使用 Scintilla window class；静态链接需要 `Scintilla_RegisterClasses(HINSTANCE)`。Unicode 输入、clipboard、drag/drop、IME、printing 和高 DPI 必须在宿主目标版本上验证。

## GTK、Cocoa 与 Qt

官方文档列出 GTK 的 `scintilla_new`、`scintilla_set_id`、`scintilla_send_message` 和 `scintilla_release_resources`。GTK 资源释放应发生在所有 Scintilla widget 销毁后。Scintilla 也构建 Cocoa 和 Qt；不要把 Windows window-message 生命周期直接套用到其他平台。

## 编码与行尾

Scintilla 文档中的 character 通常是 document byte；DBCS 字符和 CRLF 可能阻止 caret 位于中间 byte。区分 UTF-8、DBCS、UTF-16 code unit、CR、LF、CRLF 和 CP/M 行尾。读取/保存时明确 `SCI_SETCODEPAGE`、`SCI_SETEOLMODE`、`SCI_CONVERTEOLS` 的作用。

## RTL、IME、DPI 与图片

Windows 上 Arabic/Hebrew 支持有限且 experimental，显示正确不代表交互完整。RGBA 图片使用逐像素 RGBA byte，不预乘 alpha，尺寸由 `SCI_RGBAIMAGESETWIDTH/HEIGHT` 预先设置；XPM 受官方格式限制。zoom 与平台 DPI scaling 是不同层次，分别测试。

来源：https://www.scintilla.org/ScintillaDoc.html#GTK
