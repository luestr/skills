# Images 图像 API

官方 Images 章节覆盖两类图像格式：RGBA 和 XPM。图像可用于 margin markers、autocompletion 列表和 call tips。

## RGBA

RGBA 是连续的 4-byte pixel 数据，顺序为 red、green、blue、alpha；行之间没有 padding，颜色 byte 不预乘 alpha。由于数据不携带尺寸，先调用 `SCI_RGBAIMAGESETWIDTH` 和 `SCI_RGBAIMAGESETHEIGHT`，再注册/使用图像。alpha 为 `0` 时完全透明，`255` 时完全不透明。

## XPM

XPM 必须符合 Scintilla 支持的受限格式：每个 pixel 使用一个字符，颜色不能使用 named colours，并可有名为 `None` 的透明色。支持 lines form 和 text form；text form 以 `/* XPM */` 开始。

## 注册和生命周期

使用 `SCI_REGISTERIMAGE` 注册供 autocomplete/call tip 使用的图像，使用 `SCI_CLEARREGISTEREDIMAGES` 清理注册表；具体 list type、image id 和显示位置按对应 API 条目确认。注册后由 Scintilla 管理注册图像；通过 `SCI_CLEARREGISTEREDIMAGES` 清理，并使清理时机与控件和 autocomplete/call-tip 列表生命周期一致。不要把注册 API 与未注册的临时图像输入混为一谈。

RGBA 在 Windows、GTK、macOS Cocoa 支持；XPM 在所有平台支持。PNG 等文件格式的解码由平台或第三方库负责，Scintilla 接收已转换的数据。

来源：https://www.scintilla.org/ScintillaDoc.html#Images
