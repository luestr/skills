# Images API

The official Images section covers RGBA and XPM formats. Images can be used in margin markers, autocomplete lists, and call tips.

## RGBA

RGBA is contiguous 4-byte pixel data in red, green, blue, alpha order. There is no row padding and color bytes are not premultiplied. Because the data carries no dimensions, set `SCI_RGBAIMAGESETWIDTH` and `SCI_RGBAIMAGESETHEIGHT` before registering or using the image. Alpha `0` is fully transparent and `255` is opaque.

## XPM

XPM must use Scintilla's restricted format: one character per pixel, no named colors, and optionally a transparent color named `None`. Both lines form and text form are supported; text form starts with `/* XPM */`.

## Registration and lifetime

Use `SCI_REGISTERIMAGE` to register images for autocomplete/call-tip use and `SCI_CLEARREGISTEREDIMAGES` to clear the registry. Confirm list type, image ID, and display location in each API entry. After registration, Scintilla manages the registered image; clear it with `SCI_CLEARREGISTEREDIMAGES` and align cleanup with control and autocomplete/call-tip list lifetimes. Do not confuse registered images with unregistered temporary image input.

RGBA is supported on Windows, GTK, and macOS Cocoa; XPM is supported on all platforms. PNG decoding belongs to the platform or a third-party library; Scintilla receives converted pixel data.

Source: https://www.scintilla.org/ScintillaDoc.html#Images
