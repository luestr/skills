# Special Comments (Filter List Metadata)

Filter lists use special comments (starting with `!`) to declare metadata that Adblock Plus reads for list management. These are distinct from regular `!` comments which are purely for human readers.

## Supported Special Comments

### `! Title: <name>`

Declares the display name of the filter list.

```
! Title: My Custom Ad Filters
```

Shown in ABP's settings UI. If absent, the filename or URL is used.

### `! Homepage: <url>`

Link to the filter list's homepage or repository.

```
! Homepage: https://github.com/example/filters
```

### `! Expires: <interval>`

How often ABP should check for updates to this filter list.

```
! Expires: 5 days
```

```
! Expires: 8 hours
```

- Valid range: **1 hour** to **14 days**.
- Can be specified in days or hours.
- The actual update time is slightly randomized to reduce server load — this is a target interval, not a guarantee.

### `! Redirect: <url>`

Tells ABP the filter list has moved to a new download location.

```
! Redirect: https://new-location.example.com/filters.txt
```

- ABP ignores all content after this comment and immediately tries downloading from the new URL.
- On success, the list's URL is updated in settings.
- If the new URL is the same as the current URL, this serves as a "canonical address" declaration (useful for enforcing the primary URL of a list).

### `! Version: <number>`

Declares a numerical version of the filter list.

```
! Version: 2024121501
```

- Displayed in issue reports.
- Used to verify that bug reports refer to the current version.
- Typically a date-based number (YYYYMMDDNN) or a simple incrementing integer.

### `! Checksum: <hash>`

A checksum value for verifying the integrity of the filter list content. Used by some filter list management tools to detect corruption or tampering.

```
! Checksum: aBcDeFgHiJkLmNoPqRsT
```

- Usually generated automatically by filter list editing tools.
- When present, ABP or third-party tools can verify that the list content hasn't been modified unexpectedly.

## Example Filter List Header

```
! Title: Example Ad Filters
! Homepage: https://example.com/filters
! Expires: 1 day
! Version: 2024121501
! Last modified: 2024-12-15
!
! This filter list blocks ads on example.com and related sites.
! Maintained by Example Team.

||ads.example.com^
||example.com/ads/*
example.com##.ad-banner
```

## Best Practices

- Always include `! Title:` — it makes the list identifiable in ABP's UI.
- Use `! Expires:` to control update frequency — shorter for actively maintained lists, longer for stable ones.
- Use `! Version:` for tracking — it's invaluable for debugging user-reported issues.
- `! Redirect:` is essential when migrating lists to a new host — old subscribers will seamlessly follow the redirect.
- Place special comments at the top of the file, before any filters.
