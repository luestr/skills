#!/usr/bin/env python3
"""Validate a skill directory against the Agent Skills layout.

Checks the things that break discovery or installation:
- SKILL.md exists and opens with YAML frontmatter
- name / description are present, well-typed and within spec limits
- no unexpected top-level frontmatter keys
- optional ``metadata.language`` is a valid language tag when present

YAML parsing uses PyYAML when it is installed and falls back to a small
built-in parser otherwise, so this works on a bare Python install — a skill
validator that needs extra packages is a validator people skip.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ALLOWED_PROPERTIES = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
    "compatibility",
}

DESCRIPTION_LIMIT = 1024
COMPATIBILITY_LIMIT = 500
NAME_LIMIT = 64

# BCP 47-ish: language subtag, optionally a script or region subtag.
LANGUAGE_TAG = re.compile(r"^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2}|-[0-9]{3})?$")


def _parse_frontmatter(text: str) -> dict:
    """Parse simple YAML frontmatter, preferring PyYAML when available."""
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("frontmatter must be a mapping")
        return data
    except ImportError:
        return _parse_frontmatter_fallback(text)


def _strip_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def _parse_frontmatter_fallback(text: str) -> dict:
    """Minimal YAML subset: top-level scalars, block scalars and nested maps.

    Enough for SKILL.md frontmatter, and deliberately forgiving: anything it
    cannot represent is returned as a string rather than raising, so validation
    reports a content problem instead of a parser problem.
    """
    lines = text.split("\n")
    data: dict = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if line[0] in (" ", "\t"):
            i += 1
            continue

        if ":" not in line:
            i += 1
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()

        if raw in ("|", ">", "|-", ">-", "|+", ">+"):
            block: list[str] = []
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i][:1] in (" ", "\t")):
                block.append(lines[i].strip())
                i += 1
            joiner = "\n" if raw.startswith("|") else " "
            data[key] = joiner.join(b for b in block).strip()
            continue

        if raw == "":
            # Possibly a nested mapping (e.g. metadata:)
            nested: dict = {}
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i][:1] in (" ", "\t")):
                child = lines[i].strip()
                if child and ":" in child:
                    ckey, _, cval = child.partition(":")
                    nested[ckey.strip()] = _strip_scalar(cval)
                i += 1
            data[key] = nested if nested else ""
            continue

        data[key] = _strip_scalar(raw)
        i += 1

    return data


def validate_skill(skill_path) -> tuple[bool, str]:
    """Return (is_valid, message) for a skill directory."""
    skill_path = Path(skill_path)
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, "SKILL.md not found"

    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return False, "No YAML frontmatter found"

    match = re.match(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    try:
        frontmatter = _parse_frontmatter(match.group(1))
    except Exception as exc:  # noqa: BLE001 - any parse failure is a validation result
        return False, f"Invalid YAML in frontmatter: {exc}"

    if not isinstance(frontmatter, dict):
        return False, "Frontmatter must be a YAML dictionary"

    unexpected = set(frontmatter) - ALLOWED_PROPERTIES
    if unexpected:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    if "name" not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if "description" not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    name = frontmatter.get("name", "")
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            return False, (
                f"Name '{name}' should be kebab-case "
                f"(lowercase letters, digits, and hyphens only)"
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            return False, (
                f"Name '{name}' cannot start/end with hyphen or contain "
                f"consecutive hyphens"
            )
        if len(name) > NAME_LIMIT:
            return False, f"Name is too long ({len(name)} characters). Maximum is {NAME_LIMIT}."

    description = frontmatter.get("description", "")
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        if "<" in description or ">" in description:
            return False, "Description cannot contain angle brackets (< or >)"
        if len(description) > DESCRIPTION_LIMIT:
            return False, (
                f"Description is too long ({len(description)} characters). "
                f"Maximum is {DESCRIPTION_LIMIT}."
            )

    compatibility = frontmatter.get("compatibility", "")
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > COMPATIBILITY_LIMIT:
            return False, (
                f"Compatibility is too long ({len(compatibility)} characters). "
                f"Maximum is {COMPATIBILITY_LIMIT}."
            )

    metadata = frontmatter.get("metadata") or {}
    if isinstance(metadata, dict) and metadata.get("language"):
        language = str(metadata["language"]).strip()
        if not LANGUAGE_TAG.match(language):
            return False, (
                f"metadata.language '{language}' is not a valid language tag. "
                f"Expected something like zh-CN or en-US."
            )

    return True, "Skill is valid!"


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)

    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)


if __name__ == "__main__":
    main()
