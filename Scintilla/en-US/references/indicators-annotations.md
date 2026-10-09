# Indicators, annotations, and visual feedback

- **Indicators** attach to text ranges and suit errors, search hits, diagnostics, and hotspots; configure indicator style, color, alpha, underline, and hover behavior.
- **Annotations** display near or at the end of lines and suit diagnostic explanations; distinguish regular and EOL annotations and test long text, wrapping, and contrast.
- **Markers** attach to lines and suit breakpoints, current line, folding state, and debugger state; display them in a margin.

For indicator/hotspot clicks, read position and modifiers from `SCN_INDICATORCLICK` and `SCN_HOTSPOTCLICK`. Validate document revision before applying asynchronous diagnostics so stale results cannot overwrite current text. Do not use removed style-byte indicators; use standard indicators.
