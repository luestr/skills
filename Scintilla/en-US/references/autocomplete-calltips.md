# Autocompletion, user lists, and call tips

`SCI_AUTOCSHOW` displays host-supplied candidates; configure separators, fill-up characters, cancellation, insertion, and sorting. Handle `SCN_AUTOCSELECTION`, `SCN_AUTOCCANCELLED`, and `SCN_AUTOCCOMPLETED` across the full lifecycle.

`SCI_USERLISTSHOW` provides custom lists; `SCI_CALLTIPSHOW` provides signature tips. `SCN_CALLTIPCLICK` can switch between overload signatures. When candidates come from an external language service, validate request version, caret position, and document identity.

Do not unconditionally trigger completion again from its notifications; avoid reentrant or recursive popups. Define behavior for empty lists, cancellation, fill-up submission, and single-choice completion.
