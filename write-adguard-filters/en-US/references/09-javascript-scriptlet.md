# JavaScript Rules & Scriptlet Rules

## JavaScript Rules

Inject arbitrary JavaScript code into website pages. **Strongly recommend using scriptlet rules instead.** JS rules are mainly for debugging.

**Syntax:**
```
rule = [domains] "#%#" script
```

- `domains` — domain restriction
- `script` — **single-line** JavaScript code

**Example:**
```adblock
example.org#%#window.__gaq = undefined;
```

**Exception rules:** Use `#@%#` instead of `#%#`
```adblock
example.com#@%#window.__gaq = undefined;
#@%#window.__gaq = undefined;       -- Disable on all domains
```

**Restrictions:** Can only be used in **trusted filters**. Not supported by Content Blocker.

---

## Scriptlet Rules

Scriptlets are JavaScript functions for content blocking, used declaratively in filtering rules.

**Syntax:**
```
[domains]#%#//scriptlet(name[, arg1[, arg2[, ...]]])
```

**Examples:**
```adblock
example.org#%#//scriptlet('abort-on-property-read', 'alert')
example.org#%#//scriptlet('remove-class', 'branding', 'div[class^="inner"]')
```

**Exception rule syntax:**
```
[domains]#@%#//scriptlet([name[, arguments]])
```

- Omitting name → disables all scriptlets
- Specifying name → disables only that specific scriptlet
- Specifying arguments → matches rules with the same arguments

**Examples:**
```adblock
! Disable specific scriptlet
example.org,example.com#%#//scriptlet("abort-on-property-read", "alert")
example.com#@%#//scriptlet("abort-on-property-read", "alert")

! Disable all scriptlets with specified name
example.com#@%#//scriptlet("abort-on-property-read")

! Disable all scriptlets
example.com#@%#//scriptlet()

! Mixed usage
#%#//scriptlet('set-constant', 'adList', 'emptyArr')
#%#//scriptlet('set-cookie', 'accepted', 'true')
example.org#@%#//scriptlet('set-cookie')
```

**Compatibility:** Not supported by Content Blocker. Full exception syntax requires CoreLibs v1.16+ / TSUrlFilter v3.0+.

**Restrictions:** Can only be used in **trusted filters**.

More scriptlet info: https://github.com/AdguardTeam/Scriptlets#scriptlets

---

## Trusted Scriptlets

Scriptlets with extended functionality, prefixed with `trusted-` (e.g. `trusted-set-cookie`).

**Syntax and restrictions:** Same as regular scriptlets.

**Notes:**
- Not compatible with other ad blockers (AdGuard only)
- Can only be used in **trusted filters**
- Not supported by Content Blocker

More trusted scriptlet info: https://github.com/AdguardTeam/Scriptlets#trusted-scriptlets
