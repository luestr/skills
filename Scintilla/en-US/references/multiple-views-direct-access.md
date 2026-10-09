# Multiple views, document interface, and direct access

Scintilla supports multiple views sharing a document. Use the document interface with reference counting and shared undo state; distinguish view state (selection, scroll, zoom) from document state (text, styles, undo, save point). Do not release a document while another view still uses it.

Direct access can read internal document data when lifetime and thread-safety boundaries are explicit. Prefer the message API; use direct pointers only after profiling demonstrates a need, and treat them as invalid after document mutation, release, or reallocation.

Background loading/saving must not manipulate GUI controls from worker threads. Use snapshots, revision IDs, and GUI-thread commits, and handle conflicts when the user edits during IO.
