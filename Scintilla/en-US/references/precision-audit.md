# Official-section precision checklist

This file prevents a topic summary from being mistaken for a complete API reference. Every ScintillaDoc Contents entry must be checked against its official anchor, the 5.6.4 headers, and the actual platform build. The local skill provides navigation, semantic warnings, and test checkpoints rather than copying all generated prose.

## Topics requiring exact verification

- `Text retrieval and modification`: NUL termination, length probing, `Sci_TextRange`, and `Sci_TextRangeFull`.
- `Information`: return values, direct function/pointer, and document-byte semantics.
- `By character or UTF-16 code unit`: verify `SCI_POSITIONRELATIVE`, `SCI_POSITIONRELATIVECODEUNITS`, `SCI_COUNTCHARACTERS`, and `SCI_COUNTCODEUNITS` separately.
- `Error handling`: use only `SC_STATUS_*` constants present in the headers; never invent a constant from release news or an error description.
- `Notifications`: read `SCNotification` fields by `nmhdr.code`, recording pointer lifetime and reentrancy constraints.
- `Images`: verify `SCI_REGISTERIMAGE`, `SCI_CLEARREGISTEREDIMAGES`, RGBA/XPM dimensions, and resource lifetime.
- `GTK`: verify widget creation, ID, message return values, and resource release after all widgets are destroyed.
- `Building Scintilla`: verify the README, build files, compiler, regex options, exports, registration, and architecture.

## Output requirements

Keep official API names and links when citing an API. If behavior depends on a platform, build definition, or version, state the condition. If official pages or 5.6.4 headers do not prove a claim, mark it as “verify” instead of presenting it as a callable API.

Official documentation: https://www.scintilla.org/ScintillaDoc.html
