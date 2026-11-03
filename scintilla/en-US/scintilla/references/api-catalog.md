# API topic catalog (Scintilla 5.6.4)

This file is a topic index based on the official `ScintillaDoc.html` Contents; it does not replace the official per-message reference. Exact signatures, return values, defaults, and version markers must be checked against the official entry and 5.6.4 headers; do not infer a `SCI_GETxxxxx` companion solely from its name.

| Official topic | Main APIs/concepts | Integration point |
|---|---|---|
| Text retrieval and modification | `SCI_GETTEXT`, `SCI_SETTEXT`, `SCI_GETLINE`, `SCI_GETTEXTRANGE`, `SCI_INSERTTEXT`, `SCI_DELETERANGE` | Document text positions/lengths commonly count bytes; confirm NUL/buffer rules per message |
| Information | `SCI_GETLENGTH`, `SCI_GETLINECOUNT`, `SCI_GETMODIFY`, `SCI_GETDIRECTFUNCTION` | Follow each return-value definition |
| By character or UTF-16 code unit | `SCI_POSITIONRELATIVE`, `SCI_POSITIONRELATIVECODEUNITS`, `SCI_COUNTCHARACTERS`, `SCI_COUNTCODEUNITS` | Check byte, character, and UTF-16 code-unit semantics separately |
| Error handling | `SCI_GETSTATUS`, `SC_STATUS_*` | Handle `SC_STATUS_OK`, `SC_STATUS_FAILURE`, `SC_STATUS_BADALLOC`, and the officially defined `SC_STATUS_WARN_*`; do not treat an out-of-document condition as a status constant |
| Selection | anchor/current position, `SCI_SETSEL`, `SCI_GETSELTEXT`, `SCI_SETSELECTIONNSTART` | Process each selection when multiple selections are enabled |
| Multiple Selection and Virtual Space | `SCI_SETMULTIPLESELECTION`, `SCI_SETADDITIONALSELECTIONTYPING`, virtual-space APIs | Distinguish main selection, additional selections, and carets |
| Overtype | `SCI_SETOVERTYPE`, `SCI_GETOVERTYPE` | Test with selection, IME, and replacement operations |
| Searching and replacing | target APIs, `SCI_SEARCHINTARGET`, `SCI_REPLACETARGET`, `SCI_REPLACETARGETRE` | Handle empty matches, direction, target boundaries, and regex errors |
| Cut, copy and paste | `SCI_CUT`, `SCI_COPY`, `SCI_PASTE`, `SCI_CANPASTE`, `SCI_CLEAR` | Choose Scintilla clipboard APIs or an explicit host-menu policy |
| Undo and Redo | `SCI_UNDO`, `SCI_REDO`, `SCI_BEGINUNDOACTION`, `SCI_ENDUNDOACTION` | Align transaction boundaries with save points |
| Undo save and restore | `SCI_EMPTYUNDOBUFFER`, `SCI_SETUNDOSAVEPOINT`, `SCI_GETUNDOSEQUENCE` | Regression-test save/load and multiple views |
| Change history | `SCI_SETCHANGEHISTORY`, history markers | Distinguish change history from the undo stack |
| Scrolling and automatic scrolling | first visible line, x offset, `SCI_SCROLLCARET`, autoscroll | Scroll changes may produce `SCN_UPDATEUI` |
| White space | `SCI_SETVIEWWS`, `SCI_SETWHITESPACESIZE`, `SCI_SETEXTRAASCENT/DESCENT` | View whitespace is separate from document text |
| Cursor | `SCI_SETCARETFORE`, `SCI_SETCARETWIDTH`, `SCI_SETCARETPERIOD`, `SCI_SETCARETLINEVISIBLE` | Caret is view state |
| Mouse dwell / hover notifications | `SCI_SETMOUSEDWELLTIME` and dwell notifications; handle mouse capture through the host platform API where applicable | `SCI_SETMOUSEDWELLTIME` does not capture the mouse; follow platform event-loop rules |
| Line endings | `SCI_SETEOLMODE`, `SCI_CONVERTEOLS`, `SCI_GETLINEENDTYPES` | Handle CR, LF, CRLF, and CP/M caret constraints |
| Words | `SCI_WORDSTARTPOSITION`, `SCI_WORDENDPOSITION`, `SCI_SETWORDCHARS` | Define word-character behavior with lexer/host rules |
| Styling | `SCI_STARTSTYLING`, `SCI_SETSTYLING`, `SCI_CLEARDOCUMENTSTYLE` | Style bytes are derived state |
| Style definition | `SCI_STYLESETFORE/BACK/FONT/SIZE/BOLD/ITALIC` | Manage styles 0-255 separately from extended styles |
| Element colours | `SCI_SETELEMENTCOLOUR`, `SCI_GETELEMENTCOLOUR` | UI element colors are not lexer style colors |
| Selection, caret, and hotspot styles | selection colors, caret, hotspot style | Hotspot handlers have reentrancy limits |
| Character representations | `SCI_SETREPRESENTATION`, `SCI_SETREPRESENTATIONAPPEARANCE` | Display replacement does not change document bytes |
| Margins | `SCI_SETMARGINTYPEN/WIDTHN/MASKN/SENSITIVEN` | Match margin masks to marker types |
| Annotations | `SCI_ANNOTATIONSETTEXT/STYLES` | Separate regular and EOL annotations |
| End of Line Annotations | `SCI_EOLANNOTATIONSETTEXT/STYLES` | Test wrapping, folding, and visible width |
| Other settings | edge, extra ascent/descent, technology, drawing phases | Confirm platform support and defaults per item |
| Brace highlighting | `SCI_BRACEHIGHLIGHT`, `SCI_BRACEBAD`, `SCI_BRACEMATCH` | Show explicit state for invalid positions |
| Tabs and Indentation Guides | `SCI_SETTABWIDTH`, `SCI_SETUSETABS`, `SCI_SETINDENT`, guides | Keep tab/space policy aligned with formatters |
| Markers | `SCI_MARKERDEFINE`, `SCI_MARKERADD/DELETE`, marker handles | Line-level bit masks for breakpoints/folding |
| Indicators | `SCI_INDICSETSTYLE/FORE/ALPHA`, `SCI_INDICATORFILLRANGE` | Range diagnostics; never use style-byte indicators |
| Autocompletion | `SCI_AUTOCSHOW`, `SCI_AUTOCCANCEL`, `SCI_AUTOCSELECT` | Handle completion notification lifecycle |
| User lists | `SCI_USERLISTSHOW` | Define listType and selection notifications |
| Call tips | `SCI_CALLTIPSHOW/CANCEL/SETBACK` | Overload navigation and click notifications |
| Keyboard commands | `SCI_NULL`, command messages | Commands may come from keys, menus, or host code |
| Key bindings | `SCI_ASSIGNCMDKEY`, `SCI_CLEARCMDKEY`, `SCI_CLEARALLCMDKEYS` | Define modifiers/key codes per platform |
| Popup edit menu | `SCI_USEPOPUP` | Disable the default menu when supplying a host menu |
| Macro recording | `SCI_STARTRECORD`, `SCI_STOPRECORD`, `SCN_MACRORECORD` | Records messages, not arbitrary host state |
| Printing | `SCI_FORMATRANGE`, `SCI_SETPRINTMAGNIFICATION`, print colors | Manage device context, pagination, and selection range |
| Direct access | `SCI_GETDIRECTFUNCTION`, `SCI_GETDIRECTPOINTER` | Use only with explicit lifetime/thread boundaries |
| Multiple views | `SCI_CREATEDOCUMENT`, `SCI_ADDREFDOCUMENT`, `SCI_RELEASEDOCUMENT`, `SCI_SETDOCPOINTER` | Shared document; selection/scroll are generally view-local |
| Background loading and saving | Documented background load/save messages, save points, and thread boundaries | Verify the official message entries and headers; worker threads must not manipulate controls |
| Document interface | `IDocumentEditable`, document references, related headers, and reference counting | Verify create/add-reference/release order against the official section and headers |
| Folding | fold levels, `SCI_SETFOLDLEVEL`, `SCI_SETFOLDEXPANDED`, `SCI_FOLDALL` | Lexer-generated levels and user state are separate |
| Line wrapping | `SCI_SETWRAPMODE`, visual flags, wrap indent | Visual lines are not document lines |
| Zooming | `SCI_SETZOOM`, `SCI_GETZOOM` | `SCN_ZOOM` may require margin recalculation |
| Long lines | `SCI_SETEDGEMODE`, `SCI_SETEDGECOLUMN`, and long-line display/scroll settings | Balance horizontal scrolling and performance |
| Accessibility | accessibility support and notifications | Test screen readers, caret, and selection on target platform |
| Lexer | lexer name, properties, keywords, styles/fold | Scintilla 5 uses Lexilla |
| Lexer objects | `ILexer5`, `SCI_SETILEXER`, `CreateLexer` | Explicit object path is not ordinary DLL auto-loading |
| Notifications | `SCNotification`, `SCN_*` | Read only fields defined for the current notification |
| Images | RGBA, XPM, `SCI_RGBAIMAGESETWIDTH/HEIGHT`, marker/autocomplete images | RGBA is raw RGBA bytes with non-premultiplied alpha |
| GTK | `scintilla_new`, `scintilla_send_message`, `scintilla_release_resources` | GTK lifetime differs from the Windows control |
| Provisional messages | `SCI_DISABLE_PROVISIONAL` | May change or be removed |
| Deprecated messages | `INCLUDE_DEPRECATED_FEATURES`, old Edit/RichEdit compatibility | New code should use Scintilla APIs |
| Never-supported edit messages | unsupported `EM_*` | No effect; do not expect RichEdit behavior |
| Removed features | `SC_CP_DBCS`, palette, style-byte indicators | Remove from calling code |
| Building Scintilla | C++17, build scripts, regex implementation, macros | Keep DLL/headers/import library on one release |

Source: https://www.scintilla.org/ScintillaDoc.html
