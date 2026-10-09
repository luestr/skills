# Input/output, platforms, and accessibility

The documentation covers UTF-8/DBCS, line endings, clipboard, drag/drop, keyboard commands, key bindings, mouse capture, printing, images, accessibility, GTK, and other platform backends. Windows hosts should explicitly test Unicode input, line-ending conversion, clipboard formats, dropped-file paths, and print pagination.

Scintilla has limited experimental support for RTL languages such as Arabic and Hebrew; correct rendering does not imply complete selection, caret, and editing interaction. Test high DPI/zoom, proportional fonts, RGBA/XPM images, and Direct2D/DirectWrite on target platforms.

The `DISABLE_D2D` build definition controls the Windows graphics backend. Do not hide platform differences by assuming GTK, Qt, macOS, and Windows behavior is identical.
