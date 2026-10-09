# GTK API

The official GTK entry points are:

- `GtkWidget *scintilla_new()`: create a Scintilla widget for a GTK container.
- `void scintilla_set_id(ScintillaObject *sci, uptr_t id)`: set the notification `idFrom`, equivalent to `SCI_SETIDENTIFIER`.
- `sptr_t scintilla_send_message(ScintillaObject *sci, unsigned int iMessage, uptr_t wParam, sptr_t lParam)`: send any Scintilla message and receive an `sptr_t` result.
- `void scintilla_release_resources()`: release remaining global resources after all Scintilla widgets are destroyed.

GTK uses a message API similar to Windows, but widget, container, main-loop, and resource lifetimes follow GTK. Do not manipulate a widget from a worker thread; marshal calls to the thread owning the GTK widget. Supported GTK versions, glib dependencies, and build definitions must be taken from the Scintilla v5.6.4 source README/build configuration; do not infer them from the generic API page alone.

Typical setup creates the widget, adds it to a container, sets its ID, sends configuration messages, connects host notifications, and enters the GTK main loop. Call `scintilla_release_resources()` only after every widget is destroyed.

Source: https://www.scintilla.org/ScintillaDoc.html#GTK
