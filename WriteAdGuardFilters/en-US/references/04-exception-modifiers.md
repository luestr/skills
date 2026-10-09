# Exception Rule Modifiers & Generic Rules

> Exception rules start with `@@` and are used to allow requests. They have dedicated modifiers to control the allow scope.
> Generic rules are rules not limited to specific domains.

## Important Note

By default, exception rule modifiers apply only to **main frame document requests**. To apply to all sub-requests, combine with content-type modifiers.

---

## Exception Rule Exclusive Modifiers

### `$content` — Disable Content Modification Rules

Disables [HTML filtering](#), `$hls`, `$replace`, and `$jsonprune` rules on matching pages.

```adblock
@@||example.com^$content
```

---

### `$elemhide` — Disable Cosmetic Rules

Disables all [cosmetic rules](#) on matching pages.

**Alias:** `$ehide`

```adblock
@@||example.com^$elemhide
```

---

### `$extension` — Disable Userscripts

Disables specific or all userscripts.

**Syntax:**
```
$extension[="userscript_name1"[|"userscript_name2"[...]]]
```

- Omitting the name disables all userscripts
- Use `~` to exclude specific scripts (keep them enabled)
- Script names with special characters must be enclosed in quotes (single or double)
- `"`, `,`, `|` in script names must be escaped with `\`

**Examples:**
```adblock
@@||example.com^$extension="AdGuard Assistant"
@@||example.com^$extension=MyUserscript
@@||example.com^$extension='AdGuard Assistant'|'AdGuard Popup Blocker'
@@||example.com^$extension=~"AdGuard Assistant"
@@||example.com^$extension  -- Disable all userscripts
```

**Compatibility:** CoreLibs apps only. Named script support requires CoreLibs v1.13+.

---

### `$jsinject` — Disable JS Injection

Forbids adding JavaScript code to the page (scriptlets and JS rules).

```adblock
@@||example.com^$jsinject
```

**Limitations:** Cannot be converted to DNR rules in MV3; only used in TSUrlFilter engine. Not supported by Content Blocker.

---

### `$stealth` — Disable Tracking Protection

Disables the Tracking Protection (formerly Stealth Mode) module.

**Syntax:**
```
$stealth [= opt1 [| opt2 [| opt3 [...]]]]
```

**Available options:**
`searchqueries`, `donottrack`, `3p-cookie`, `1p-cookie`, `3p-cache`, `3p-auth`, `webrtc`, `push`, `location`, `flash`, `java`, `referrer`, `useragent`, `ip`, `xclientdata`, `dpi`

**Examples:**
```adblock
@@||example.com^$stealth
@@||domain.com^$script,stealth,domain=example.com
@@||example.com^$stealth=3p-cookie|dpi
```

**Note:** `$stealth` exception does not block cookies or remove tracking parameters. To fully disable, use `$stealth,removeparam,cookie`.

**Restrictions:** Options must be lowercase, cannot be negated. Browser Extension supports only partial options.

**Compatibility:** Windows/Mac/Android/Firefox/Chromium extension (not MV3).

---

### `$urlblock` — Disable All Request Blocking

Disables blocking of all requests sent from matching pages, also disables `$cookie` rules.

```adblock
@@||example.com^$urlblock
```

**Limitations:** On iOS/Safari, equivalent to `$document` exception. Not supported by Content Blocker and MV3.

---

## Generic Rules

**Generic rules** are rules not limited to specific domains.

**Generic rule examples:**
```
###banner
*###banner
#@#.adsblock
*#@#.adsblock
~domain.com###banner
||domain.com^
||domain.com^$domain=~example.com
```

**Non-generic rule examples:**
```
domain.com###banner
||domain.com^$domain=example.com
```

### `$genericblock` — Disable Generic Basic Rules

Disables generic basic rules on matching pages.

```adblock
@@||example.com^$genericblock
```

**Limitations:** On iOS/Safari, equivalent to `$document` exception. Not supported by Content Blocker and MV3.

---

### `$generichide` — Disable Generic Cosmetic Rules

Disables all generic [cosmetic rules](#) on matching pages.

**Alias:** `$ghide`

```adblock
@@||example.com^$generichide
```

---

### `$specifichide` — Disable Specific Cosmetic Rules

Disables all specific element hiding and CSS rules (but not generic rules). Has the opposite effect of `$generichide`.

**Alias:** `$shide`

```adblock
@@||example.org^$specifichide
```
Disables `example.org##.banner` but not `##.banner`.

**Note:** `$elemhide` disables all cosmetic rules (both specific and generic). Not supported by iOS/Safari/Content Blocker.
