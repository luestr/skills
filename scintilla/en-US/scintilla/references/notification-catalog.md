# SCN_* notification catalog

`SCNotification` is a union-like structure: each notification guarantees only some fields. Inspect `nmhdr.code` first, then read only fields defined for that notification.

| Notification | Main fields/use |
|---|---|
| `SCN_STYLENEEDED` | `position`: styling end point |
| `SCN_CHARADDED` | `ch`: added character |
| `SCN_SAVEPOINTREACHED/LEFT` | document dirty/save state |
| `SCN_MODIFIED` | modification type, position, length, text, linesAdded, line, foldLevelNow/Prev |
| `SCN_MODIFYATTEMPTRO` | modification attempt on read-only document |
| `SCN_UPDATEUI` | selection/content/scroll/zoom UI change flags |
| `SCN_MARGINCLICK` | margin, position, modifiers |
| `SCN_NEEDSHOWN` | range that should be made visible |
| `SCN_PAINTED` | paint operation completed |
| `SCN_DOUBLECLICK` | position, line, modifiers |
| `SCN_MACRORECORD` | recorded message, wParam, lParam |
| `SCN_KEY` | key, modifiers |
| `SCN_DWELLSTART/END` | position, x, y |
| `SCN_ZOOM` | zoom changed; no extra fields |
| `SCN_HOTSPOTCLICK/DOUBLECLICK/RELEASECLICK` | position, modifiers; obey selection/caret reentrancy rules |
| `SCN_INDICATORCLICK/RELEASE` | position, modifiers |
| `SCN_CALLTIPCLICK` | Use `position` for the document position; use `ch` to identify the call-tip up arrow, down arrow, or other area |
| `SCN_AUTOCSELECTION` | position, text, ch, listCompletionMethod; insertion can be cancelled before return |
| `SCN_AUTOCCANCELLED` | completion cancelled |
| `SCN_AUTOCCHARDELETED` | character deleted while completion is active |
| `SCN_AUTOCCOMPLETED` | completion inserted; read `position`, `text`, `listCompletionMethod`, and other fields according to the official structure rather than assuming every field is valid at every stage |
| `SCN_AUTOCSELECTIONCHANGE` | listType, text, position |
| `SCN_USERLISTSELECTION` | listType, text |
| `SCN_FOCUSIN/OUT` | focus state; no extra fields |

`SCN_URIDROPPED` | URI/file-drop text is in `text`; copy it before asynchronous processing and follow the official encoding/lifetime rules.

Keep handlers short on the GUI thread. Attach document revision IDs to asynchronous results and follow the official reentrancy rules for hotspot, completion, and macro notifications.

Source: https://www.scintilla.org/ScintillaDoc.html#Notifications
