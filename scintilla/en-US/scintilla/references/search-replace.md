# Search, replace, and regular expressions

Scintilla search/replace is target-based: set a range with `SCI_SETTARGETSTART`/`SCI_SETTARGETEND`, then call `SCI_SEARCHINTARGET`; replace with `SCI_REPLACETARGET` or `SCI_REPLACETARGETRE`. A search loop must handle `-1`, empty matches, direction, and target boundaries to avoid infinite loops.

## Flags and regex

Use `SCI_SETSEARCHFLAGS` for whole word, match case, word start, regular expressions, and related behavior. Use the official replacement capture syntax; do not assume the host language's regex syntax is identical to Scintilla's.

## Incremental search

An incremental search should preserve the original target, selection, and scroll state. On each input, reset the target and handle not-found, selection updates, and undo boundaries. Do not block the GUI thread with a full-document loop on large documents.

## Highlighting results

Use indicators or markers for results rather than changing style bytes. Clear stale indicator ranges; asynchronous search must validate document identity and revision before applying results.
