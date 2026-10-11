# Complete message-reference navigation

The official `ScintillaDoc.html` lists `SCI_*` messages and `SCN_*` notifications by feature. This skill does not duplicate thousands of generated API lines; it provides complete navigation and call contracts. Before using a message, open its official anchor and confirm parameters, return value, and introduced/deprecated status.

## Official message groups

- Text: `SCI_GETTEXT`, `SCI_SETTEXT`, `SCI_GETTEXTRANGE`, `SCI_INSERTTEXT`, `SCI_DELETERANGE`, `SCI_APPENDTEXT`
- Information: `SCI_GETLENGTH`, `SCI_GETCHARAT`, `SCI_GETSTYLEAT`, `SCI_LINEFROMPOSITION`, `SCI_POSITIONFROMLINE`
- Selection/caret: `SCI_GETSELECTIONSTART`, `SCI_SETSEL`, `SCI_SETMULTIPLESELECTION`, `SCI_SETADDITIONALSELECTIONTYPING`
- Search/replace: `SCI_SETTARGETSTART`, `SCI_SETTARGETEND`, `SCI_SEARCHINTARGET`, `SCI_REPLACETARGET`
- Undo: `SCI_UNDO`, `SCI_REDO`, `SCI_EMPTYUNDOBUFFER`, `SCI_BEGINUNDOACTION`, `SCI_ENDUNDOACTION`
- View: scrolling, visible lines, zoom, wrapping, long lines, caret, and multiple-view messages
- Styling: `SCI_STYLESETFORE`, `SCI_STYLESETBACK`, `SCI_STYLESETFONT`, `SCI_SETLEXER`
- UI annotations: margins, markers, indicators, annotations, and EOL annotations
- Interaction: clipboard, keyboard, mouse, drag/drop, popup menu, macro, and printing
- Advanced: document interface, direct access, background loading/saving, images, and accessibility

## Argument contract

Use `WPARAM`/`LPARAM` or `uptr_t`/`sptr_t`; do not narrow pointer-sized values. Pass `0` for unused arguments. Positions and text lengths count bytes; lines are zero-based; `INVALID_POSITION` is `-1`. Confirm per message whether output is NUL-terminated and whether `NULL` probes the required length.

## Notification contract

For `SCN_MODIFIED`, `SCN_UPDATEUI`, `SCN_CHARADDED`, `SCN_SAVEPOINTREACHED`, `SCN_SAVEPOINTLEFT`, `SCN_AUTOCSELECTION`, `SCN_DWELLSTART`, `SCN_ZOOM`, and `SCN_FOCUSIN/OUT`, read only the fields of `SCNotification` used by that notification and follow documented reentrancy restrictions.

## Source

The complete list and formal signature of every message is authoritative at https://www.scintilla.org/ScintillaDoc.html. For type-safe C++, see `ScintillaTypes.h`, `ScintillaMessages.h`, `ScintillaStructures.h`, and `ScintillaCall.h`.
