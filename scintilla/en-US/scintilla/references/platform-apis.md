# Platform APIs and input/output details

## Windows

The Windows build is a Windows Control driven primarily by messages. Dynamic use creates the Scintilla window class; static linking calls `Scintilla_RegisterClasses(HINSTANCE)`. Test Unicode input, clipboard, drag/drop, IME, printing, and high DPI on the host's supported versions.

## GTK, Cocoa, and Qt

The official documentation lists GTK functions `scintilla_new`, `scintilla_set_id`, `scintilla_send_message`, and `scintilla_release_resources`. Release GTK resources after all Scintilla widgets are destroyed. Scintilla also builds for Cocoa and Qt; do not transplant Windows window-message lifetime assumptions unchanged.

## Encoding and line endings

In the documentation, “character” normally means a document byte; DBCS characters and CRLF can prevent the caret from sitting between component bytes. Distinguish UTF-8, DBCS, UTF-16 code units, CR, LF, CRLF, and CP/M line endings. Define the roles of `SCI_SETCODEPAGE`, `SCI_SETEOLMODE`, and `SCI_CONVERTEOLS` during load/save.

## RTL, IME, DPI, and images

Arabic/Hebrew support on Windows is limited and experimental; correct rendering does not imply complete interaction. RGBA images use raw RGBA bytes with non-premultiplied alpha, and dimensions are set first with `SCI_RGBAIMAGESETWIDTH/HEIGHT`; XPM is restricted to the documented format. Test zoom and platform DPI scaling as separate layers.

Source: https://www.scintilla.org/ScintillaDoc.html#GTK
