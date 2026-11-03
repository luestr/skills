# Snippet Filters

Snippet filters run specialized JavaScript code snippets on pages within specified domains. They're the most powerful filter type — capable of manipulating page behavior in ways that CSS selectors cannot.

**Security note:** Snippet filters can only be added to a user's custom filters or the ABP Anti-Circumvention Filter List.

## Basic Syntax

```
<domains>#$#<snippet-command> <arguments>
```

The `#$#` separator marks a snippet filter. Multiple snippets can be chained with `;`:

```
example.com#$#abort-on-property-read adblock; hide-if-contains ad .ad-class
```

## Argument Rules

- Arguments are strings; wrap in single quotes (`'`) if they contain spaces.
- Escape a single quote within quotes: `\'`
- Escape spaces without quoting: `\ ` (backslash-space)
- Unicode: `\uNNNN` (e.g., `\u1F601` = 😀)
- Special chars: `\r`, `\n`, `\t`
- Literal backslash: `\\`

## Debug & Logging Snippets

| Snippet | Purpose | Example |
|---|---|---|
| `log` | Print to web console | `example.com#$#log Hello` |
| `trace` | Log in document context (not content script) | `example.com#$#trace OK` |
| `debug` | Enable debug mode for following snippets | `example.com#$#debug; abort-on-property-read atob` |
| `profile` | Measure snippet performance via Performance API | `example.com#$#profile; abort-on-property-read atob` |

**Debug filtering:** `debug hello; snippet-name` — only shows debug logs containing "hello". Supports regex: `debug /json-prune\|json-override/; snippet-name`.

## Performance

| Snippet | Purpose |
|---|---|
| `race start;` ... `race stop;` | Race multiple snippets; winners signal, losers are stopped |

```
example.com#$#race start; snippet-a 1 2 3; snippet-b 4 5 6; race stop;
```

```
example.com#$#race start 2; first 1; second 2; third 3; fourth 4; race stop;
```
(first 2 to signal "win" are kept, rest stopped)

## Behavioral Snippets

These alter page execution behavior:

### `abort-on-property-read`

Patches a property on `window` to abort script execution when the property is **read**.

```
example.com#$#abort-on-property-read adblock
```

| Param | Required | Description |
|---|---|---|
| `property` | Yes | Property name or dot-path (e.g., `navigator.userAgent`) |
| `setConfigurable` | No | Set to `false` if the site circumvents by making the property non-configurable |

### `abort-on-property-write`

Same as above but triggers on **write**:

```
example.com#$#abort-on-property-write adblockDetected
```

### `abort-current-inline-script`

Aborts an inline script when a property is read or written:

```
example.com#$#abort-current-inline-script document.write adblock
```

| Param | Required | Description |
|---|---|---|
| `api` | Yes | Property to anchor on |
| `search` | No | Only abort scripts containing this string (supports regex if wrapped in `/`) |

### `abort-on-iframe-property-read` / `abort-on-iframe-property-write`

Like the above but targets iframe properties:

```
example.com#$#abort-on-iframe-property-read prop1 prop2
```

### `cookie-remover`

Remove cookies by name pattern:

```
example.com#$#cookie-remover tracking_id
```

| Param | Required | Description |
|---|---|---|
| `cookie` | Yes | Cookie name or regex (wrap in `/`) |
| `autoRemoveCookie` | No | `true` — continuously monitors and removes the cookie every 1s |

### `set-constant`

Set a JavaScript property to a constant value:

```
example.com#$#set-constant adblock false
```

| Param | Required | Description |
|---|---|---|
| `property` | Yes | Property name or dot-path |
| `value` | Yes | Value to set (string, number, boolean, `null`, `undefined`, `noopFunc`, `trueFunc`, `falseFunc`, `noopArray`, `noopString`) |

### `json-prune`

Remove properties from JSON responses:

```
example.com#$#json-prune ads.* tracking
```

| Param | Required | Description |
|---|---|---|
| `props` | Yes | Space-separated property paths to remove (supports wildcards) |
| `requiredProps` | No | Only prune if these properties exist |

**JSONPath support** (ABP 4.36+): Prefix with `jsonpath(`:
```
example.com#$#json-prune jsonpath($..ad_tracking)
```

### `json-override`

Override JSON property values:

```
example.com#$#json-override ads.enabled false
```

**JSONPath support:**
```
example.com#$#json-override jsonpath($.items[(@.is_sponsored==true)].label) "Clean Content"
```

### `override-property-read`

Override what a property returns when read:

```
example.com#$#override-property-read document.hasFocus trueFunc
```

### `run-at`

Control when a snippet runs:

```
example.com#$#run-at document-start abort-on-property-read adblock
```

Values: `document-start`, `document-end`, `document-idle`

### `prevent-listener`

Prevent event listeners from being added:

```
example.com#$#prevent-listener visibilitychange
```

### `prevent-addEventListener`

Block specific `addEventListener` calls:

```
example.com#$#prevent-addEventListener click /ad[_-]?click/
```

### `prevent-setTimeout` / `prevent-setInterval`

Block timer-based calls matching a pattern:

```
example.com#$#prevent-setTimeout /ad[_-]?display/
```

### `event-override`

Proxy and modify events (ABP 4.22.2+):

```
example.com#$#event-override click trusted
```

| Param | Required | Description |
|---|---|---|
| `eventType` | Yes | Event type (e.g., `click`, `mouseover`) |
| `mode` | Yes | `trusted` (make isTrusted true) or `disable` (block event) |
| `needle` | No | Only override if listener function contains this string |

### `blob-override`

Override Blob content (ABP 4.22.2+):

```
example.com#$#blob-override /ad[_-]?code/ ''
```

### `array-override`

Override Array.prototype methods (ABP 4.8+):

```
example.com#$#array-override push /ad[_-]?slot/
```

## Conditional Hiding Snippets

### `hide-if-contains`

Hide elements containing specific text:

```
example.com#$#hide-if-contains ad .ad-class
```

| Param | Required | Description |
|---|---|---|
| `search` | Yes | String to look for. If wrapped in `/`, treated as regex. |
| `selector` | Yes | CSS selector the element must match to be hidden. |
| `searchSelector` | No | CSS selector the element containing the string must match. Defaults to `selector`. |

### `hide-if-contains-visible-text`

Like `hide-if-contains` but only matches **visible** text (respects CSS visibility, font size, color, opacity, and overflow):

```
example.com#$#hide-if-contains-visible-text ad .ad-class
```

| Param | Required | Description |
|---|---|---|
| `search` | Yes | String to look for. If wrapped in `/`, treated as regex. |
| `selector` | Yes | CSS selector the element must match to be hidden. |
| `searchSelector` | No | CSS selector the element containing the string must match. Defaults to `selector`. |
| `optionalParameters` | No | Additional visibility checks as `key:value` in single quotes, e.g. `'-disable-font-check:true' 'opacity:0'`. |

**Note:** `^^sh^^` demarcator is supported, but `^^svg^^` is NOT supported for this snippet.

### `hide-if-contains-image`

Hide elements containing images with specific characteristics:

```
example.com#$#hide-if-contains-image /ad[_-]?banner/ .ad-container
```

| Param | Required | Description |
|---|---|---|
| `search` | Yes | String or regex to match against the image's alt text or src. |
| `selector` | Yes | CSS selector the element must match to be hidden. |

### `hide-if-contains-similar-text`

Hide elements with text similar (fuzzy match) to a given string:

```
example.com#$#hide-if-contains-similar-text 'sponsored content' .ad-class 0.8
```

| Param | Required | Description |
|---|---|---|
| `search` | Yes | Text to compare against (fuzzy matching). |
| `selector` | Yes | CSS selector the element must match to be hidden. |
| `threshold` | Yes | Similarity threshold (0-1). Higher = stricter match. |

### `hide-if-contains-and-matches-style`

Hide elements with text content matching a string AND computed style matching criteria:

```
example.com#$#hide-if-contains-and-matches-style ad .ad-class .parent
```

### `hide-if-has-and-matches-style`

Hide elements with descendants matching a selector AND computed style criteria:

```
example.com#$#hide-if-has-and-matches-style .ad-child .container
```

### `hide-if-shadow-contains`

Hide elements whose **shadow DOM** contains matching text:

```
example.com#$#hide-if-shadow-contains ad .shadow-host
```

### `hide-if-labelled-by`

Hide elements with `aria-labelledby` pointing to labels containing specific text:

```
example.com#$#hide-if-labelled-by ad [aria-labelledby]
```

### `hide-if-matches-xpath`

Hide elements via XPath 1.0 query:

```
example.com#$#hide-if-matches-xpath //div[contains(@class,'ad')]
```

### `hide-if-matches-xpath3`

Hide elements via XPath 3.1 query (ABP 3.19+).

### `hide-if-matches-computed-xpath`

Hide elements via dynamically constructed XPath with regex extraction:

```
example.com#$#hide-if-matches-computed-xpath //div[@class='{{}}'] //span[@id='source'] /ad[_-]?[\w]+/
```

### `hide-if-svg-contains`

Hide elements containing SVG images with specific visible text (ABP 4.26+).

## Shadow DOM Access

Use demarcators in CSS selectors to access shadow DOM elements:

| Demarcator | Target | Example |
|---|---|---|
| `^^sh^^` | Open/closed shadow roots | `.parent ^^sh^^ .child` |
| `^^svg^^` | SVG `<use>` referenced elements | `.use-element ^^svg^^` |

```
example.com#$#hide-if-contains ad .host ^^sh^^ .inner-element
```

Multiple demarcators can be chained for nested shadow DOMs.

## Other Utility Snippets

| Snippet | Purpose |
|---|---|
| `freeze-element` | Freeze a DOM element to prevent adding new nodes (see below) |
| `simulate-mouse-event` | Simulate mouse events on elements (see below) |
| `replace-node-text` | Replace text content in matching nodes |
| `replace-xhr-response` | Replace content in XHR responses |
| `replace-xhr-request` | Replace content in XHR requests |
| `adjust-setInterval` / `adjust-setTimeout` | Modify timer intervals/delays |
| `nano-setInterval-booster` / `nano-setTimeout-booster` | Boost timer-based ad scripts |
| `remove-attr` | Remove attributes from elements |
| `remove-class` | Remove CSS classes from elements |
| `set-attr` | Set attributes on elements |
| `add-class` | Add CSS classes to elements |

### `freeze-element` (detail)

Freezes a DOM element so it prevents adding new nodes inside it (ABP 3.10+).

```
example.com#$#freeze-element .ad-container
```

| Param | Required | Description |
|---|---|---|
| `selector` | Yes | CSS selector for the element to freeze |
| `property` | No | Specific property to monitor for changes |
| `value` | No | Expected value of the monitored property |

### `simulate-mouse-event` (detail)

Simulates mouse events on elements matching a CSS selector. Useful for triggering ad-loading code that only runs on user interaction:

```
example.com#$#simulate-mouse-event .ad-button click
```

| Param | Required | Description |
|---|---|---|
| `selector` | Yes | CSS selector for the target element. Supports `^^sh^^` and `^^svg^^` demarcators. |
| `event` | Yes | Mouse event type: `click`, `mousedown`, `mouseup`, `mouseover`, `mouseout`, `mousemove` |

## JSONPath Syntax (ABP 4.36+)

Supported within `json-prune`, `json-override`, `replace-xhr-response`, `replace-xhr-request`. Prefix path with `jsonpath(`.

| Operator | Name | Example |
|---|---|---|
| `$` | Root | `$.data` |
| `.` | Dot access | `$.store.book` |
| `..` | Recursive descent | `$..ad_id` |
| `*` | Wildcard | `$.items[*]` |
| `[]` | Bracket notation | `$['complex-key']` |
| `[?()]` | Filter expression | `[?(@.type=='ad')]` |

Filter operators: `==`, `!=`, `<`, `<=`, `>`, `>=`, `^=` (starts with), `$=` (ends with), `*=` (contains).
