# Message API and data contracts

## Common messages

| Goal | API | Important detail |
|---|---|---|
| Read all text | `SCI_GETTEXT` | Allocate `length + 1`; result is NUL-terminated |
| Replace all text | `SCI_SETTEXT` | Input is a NUL-terminated string |
| Read a line | `SCI_GETLINE` | Probe with `SCI_LINELENGTH`; result is not automatically NUL-terminated |
| Replace selection | `SCI_REPLACESEL` | Inserts at the caret when there is no selection |
| Read-only mode | `SCI_SETREADONLY` | Modification attempts produce `SCN_MODIFYATTEMPTRO` |
| Save point | `SCI_SETSAVEPOINT` | Marks the document unmodified after save/load |

## Types and memory

- Message arguments use pointer-sized `sptr_t`/`uptr_t`; the exact meaning of `position` and `line` is defined per message. Do not generalize text positions/lengths to one encoding unit; `line` is a zero-based line number.
- Document positions and lengths count bytes, even for multibyte encodings.
- `const char *` may require NUL termination, or a separate argument may provide its length; read each message entry.
- For output `char *` APIs, the caller may need to provide the full buffer. Pass `NULL` for length probing only where the official message entry explicitly permits it.
- `INVALID_POSITION` is `-1`; do not feed it into range arithmetic.
- `colour` is `red | (green << 8) | (blue << 16)`; `colouralpha` adds alpha in the high byte.

## Notifications

The host receives modification, save-point, completion, focus, dwell, hotspot, and zoom events. Follow each notification's reentrancy constraints. For example, hotspot click handlers should avoid changing selection or caret position unless the documentation permits it.

## Safe C++ pattern

```cpp
std::string GetText(HWND editor) {
    const sptr_t length = ::SendMessage(editor, SCI_GETTEXT, 0, 0);
    if (length < 0 || length > kMaximumDocumentBytes) {
        throw std::runtime_error("invalid document length");
    }
    std::string text(static_cast<size_t>(length) + 1, '\0');
    ::SendMessage(editor, SCI_GETTEXT, static_cast<WPARAM>(length),
                  reinterpret_cast<LPARAM>(text.data()));
    text.resize(static_cast<size_t>(length));
    return text;
}
```

Replace the length limit, error policy, and thread ownership with host conventions; control messages normally belong on the GUI thread that created the control.
