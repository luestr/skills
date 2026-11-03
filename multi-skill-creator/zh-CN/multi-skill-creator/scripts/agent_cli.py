#!/usr/bin/env python3
"""Agent-agnostic CLI adapter.

The skill-creator workflow needs two kinds of model calls:

1. **Completion** — "here is a long prompt, give me text back". Used to rewrite
   a skill description from eval failures.
2. **Trigger probe** — "run this user query in a project where skill X is
   installed, and tell me whether the agent actually loaded skill X".

Both used to be hard-wired to `claude -p`. This module turns them into data:
an ``AgentSpec`` describes how to invoke *some* agent CLI, where that CLI looks
for skills, and how its output should be read. Presets cover the common CLIs;
anything else can be described with flags or an ``--agent-cmd`` template, so no
part of this skill depends on one vendor.

Resolution order for the active agent:

1. Explicit ``--agent-cmd`` / ``SKILL_CREATOR_AGENT_CMD`` command template.
2. ``--agent <preset>``.
3. First preset whose executable is on PATH (``auto``).

If nothing resolves, callers get an ``AgentUnavailable`` error with actionable
guidance instead of a confusing subprocess failure.
"""

from __future__ import annotations

import json
import os
import queue
import shlex
import shutil
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

# Environment variables some CLIs set when they are themselves running inside a
# session. They make nested non-interactive invocations fail on a few tools, so
# the probe strips them. Stripping an unknown name is harmless.
_NESTING_GUARDS = ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CODEX_SANDBOX", "GEMINI_CLI")

# Placeholders accepted inside a command template.
PLACEHOLDER_PROMPT = "{prompt}"
PLACEHOLDER_MODEL = "{model}"


class AgentUnavailable(RuntimeError):
    """No usable agent CLI could be resolved."""


@dataclass(frozen=True)
class InstallTarget:
    """Where to place the probe skill so the agent can discover it.

    ``style`` is either ``"skill_md"`` (write ``<dir>/<name>/SKILL.md``) or
    ``"command_md"`` (write ``<dir>/<name>.md`` as a slash-command style entry).
    """

    style: str
    rel_dir: str


@dataclass(frozen=True)
class AgentSpec:
    """How to drive one agent CLI."""

    name: str
    # Command used for a plain text completion. May contain {prompt}/{model}.
    complete_cmd: tuple[str, ...]
    # Command used for a trigger probe (prompt appended or templated).
    probe_cmd: tuple[str, ...]
    # How the prompt reaches the process for completions: "argv" or "stdin".
    transport: str = "stdin"
    # True when probe output is JSON-lines with tool_use events we can scan.
    structured_output: bool = False
    # Where this CLI discovers skills from, relative to the project root.
    install_targets: tuple[InstallTarget, ...] = ()
    # Flags used to select a model; empty means "this CLI has no such flag".
    model_flag: tuple[str, ...] = ()
    notes: str = ""


# --------------------------------------------------------------------------
# Presets
# --------------------------------------------------------------------------
#
# These are starting points, not gospel: agent CLIs rename flags between
# releases. Each one is documented so a mismatch is easy to spot and easy to
# override with --agent-cmd / --agent-* flags.

PRESETS: dict[str, AgentSpec] = {
    "claude": AgentSpec(
        name="claude",
        complete_cmd=("claude", "-p", "--output-format", "text"),
        probe_cmd=(
            "claude", "-p", PLACEHOLDER_PROMPT,
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
        ),
        transport="stdin",
        structured_output=True,
        install_targets=(
            InstallTarget("skill_md", ".claude/skills"),
            InstallTarget("command_md", ".claude/commands"),
        ),
        model_flag=("--model",),
        notes="Claude Code. Prompt for completions goes over stdin.",
    ),
    "codex": AgentSpec(
        name="codex",
        complete_cmd=("codex", "exec", "--skip-git-repo-check", "-"),
        probe_cmd=("codex", "exec", "--skip-git-repo-check", PLACEHOLDER_PROMPT),
        transport="stdin",
        structured_output=False,
        install_targets=(InstallTarget("skill_md", ".agents/skills"),),
        model_flag=("--model",),
        notes="OpenAI Codex CLI (non-interactive 'exec' mode).",
    ),
    "gemini": AgentSpec(
        name="gemini",
        complete_cmd=("gemini", "-p", PLACEHOLDER_PROMPT),
        probe_cmd=("gemini", "-p", PLACEHOLDER_PROMPT),
        transport="argv",
        structured_output=False,
        install_targets=(InstallTarget("skill_md", ".gemini/skills"),),
        model_flag=("-m",),
        notes="Google Gemini CLI.",
    ),
    "cursor-agent": AgentSpec(
        name="cursor-agent",
        complete_cmd=("cursor-agent", "-p", PLACEHOLDER_PROMPT),
        probe_cmd=("cursor-agent", "-p", PLACEHOLDER_PROMPT),
        transport="argv",
        structured_output=False,
        install_targets=(
            InstallTarget("skill_md", ".cursor/skills"),
            InstallTarget("skill_md", ".agents/skills"),
        ),
        model_flag=("--model",),
        notes="Cursor agent CLI.",
    ),
    "opencode": AgentSpec(
        name="opencode",
        complete_cmd=("opencode", "run", PLACEHOLDER_PROMPT),
        probe_cmd=("opencode", "run", PLACEHOLDER_PROMPT),
        transport="argv",
        structured_output=False,
        install_targets=(InstallTarget("skill_md", ".opencode/skills"),),
        model_flag=("--model",),
        notes="OpenCode CLI.",
    ),
    "finch": AgentSpec(
        name="finch",
        complete_cmd=("finch", "run", "--print", PLACEHOLDER_PROMPT),
        probe_cmd=("finch", "run", "--print", PLACEHOLDER_PROMPT),
        transport="argv",
        structured_output=False,
        install_targets=(
            InstallTarget("skill_md", ".finch/skills"),
            InstallTarget("skill_md", ".claude/skills"),
        ),
        model_flag=("--model",),
        notes="Finch desktop agent (adjust flags to your build if they differ).",
    ),
}


# --------------------------------------------------------------------------
# Command templates
# --------------------------------------------------------------------------

def _split_template(template: str) -> tuple[str, ...]:
    """Split a command template into argv, honouring quotes per platform.

    ``shlex.split(posix=True)`` would eat Windows backslashes, and
    ``posix=False`` leaves the quotes glued to the token, which subprocess then
    re-quotes into a literal ``"path"`` the CLI cannot open. So Windows gets
    ``posix=False`` plus an explicit quote strip.
    """
    if os.name == "nt":
        parts = shlex.split(template, posix=False)
        cleaned = []
        for part in parts:
            if len(part) >= 2 and part[0] == part[-1] and part[0] in ("'", '"'):
                part = part[1:-1]
            cleaned.append(part)
        return tuple(cleaned)
    return tuple(shlex.split(template, posix=True))


def _render(template: tuple[str, ...], prompt: str | None, model: str | None) -> list[str]:
    """Fill {prompt}/{model} placeholders.

    When a template has no {prompt} slot the prompt is appended as the final
    argument, which is what most CLIs expect.

    Model handling has two traps this function exists to avoid:

    * A bare ``{model}`` argument with no model requested must disappear
      *together with its flag*. Rendering it to an empty string would leave a
      dangling ``--model`` followed by nothing, which most CLIs reject as a
      missing value.
    * When the template already spells out the flag (``--model {model}``), the
      model must not also be appended by the caller, or the CLI sees the value
      twice. ``build_command`` is what guarantees that.
    """
    has_prompt_slot = any(PLACEHOLDER_PROMPT in part for part in template)

    # Drop "<flag> {model}" pairs entirely when there is no model, and drop a
    # standalone {model} token. Done as a pre-pass so flag/value pairs stay
    # aligned.
    parts: list[str] = []
    skip_next = False
    for part in template:
        if skip_next:
            skip_next = False
            continue
        if not model and part.strip() == PLACEHOLDER_MODEL:
            # Remove the preceding flag if the previous token looks like one.
            if parts and parts[-1].startswith("-"):
                parts.pop()
            continue
        if not model and PLACEHOLDER_MODEL in part:
            # e.g. "--model={model}" -> drop the whole token
            if placeholder_is_only_value(part):
                if parts and parts[-1].startswith("-"):
                    parts.pop()
                continue
        parts.append(part)

    argv: list[str] = []
    for part in parts:
        rendered = part.replace(PLACEHOLDER_MODEL, model) if model else part
        if prompt is not None:
            rendered = rendered.replace(PLACEHOLDER_PROMPT, prompt)
        argv.append(rendered)
    if prompt is not None and not has_prompt_slot:
        argv.append(prompt)
    return argv


def placeholder_is_only_value(part: str) -> bool:
    """True when a token is just a flag carrying {model}, e.g. ``--model={model}``."""
    if PLACEHOLDER_MODEL not in part:
        return False
    prefix, _, suffix = part.partition(PLACEHOLDER_MODEL)
    return prefix.endswith(("=", ":")) and not suffix


def build_command(
    template: tuple[str, ...],
    spec: AgentSpec,
    *,
    prompt: str | None,
    model: str | None,
) -> list[str]:
    """Render a command line, adding the model flag only when it isn't templated.

    This is the single place that decides how a model reaches the CLI, so
    ``complete`` and ``probe_trigger`` cannot disagree about it.
    """
    argv = _render(template, prompt, model)
    if model and spec.model_flag and not utilises_model_placeholder(template):
        argv = argv + list(spec.model_flag) + [model]
    return argv


def utilises_model_placeholder(template: tuple[str, ...]) -> bool:
    """True when the template already places the model itself."""
    return any(PLACEHOLDER_MODEL in part for part in template)


def spec_from_template(
    template: str,
    *,
    name: str = "custom",
    transport: str = "argv",
    model_flag: tuple[str, ...] = (),
) -> AgentSpec:
    """Build a spec from a raw command template such as ``myagent -p {prompt}``.

    A custom template is used for both completions and probes, with no
    structured event stream, and skill discovery falls back to the common
    locations so a probe can still install something findable.

    ``model_flag`` is empty by default: an unknown CLI may not accept
    ``--model`` at all, and guessing wrong turns an otherwise working run into
    an argument-error crash. Callers who know their CLI's flag can pass it, or
    simply put ``{model}`` in the template where it belongs.
    """
    argv = _split_template(template)
    if not argv:
        raise AgentUnavailable("Empty --agent-cmd template.")
    return AgentSpec(
        name=name,
        complete_cmd=argv,
        probe_cmd=argv,
        transport=transport,
        structured_output=False,
        install_targets=(
            InstallTarget("skill_md", ".claude/skills"),
            InstallTarget("command_md", ".claude/commands"),
            InstallTarget("skill_md", ".finch/skills"),
            InstallTarget("skill_md", ".agents/skills"),
        ),
        model_flag=model_flag,
        notes="User-supplied command template.",
    )


def discover_preset() -> AgentSpec | None:
    """Return the first preset whose executable exists on PATH."""
    for spec in PRESETS.values():
        exe = spec.complete_cmd[0]
        if shutil.which(exe):
            return spec
    return None


def resolve_agent(
    preset: str | None = None,
    cmd_template: str | None = None,
    *,
    transport: str = "argv",
    install_roots: list[str] | None = None,
    model_flag: str | None = None,
) -> AgentSpec:
    """Pick the agent spec to use, or raise AgentUnavailable with guidance.

    ``install_roots`` overrides where the probe skill is written, for CLIs whose
    skill location is not one of the known conventions. ``model_flag`` declares
    how a custom template accepts a model; presets carry their own.
    """
    template = cmd_template or os.environ.get("SKILL_CREATOR_AGENT_CMD")
    if template:
        spec = spec_from_template(
            template,
            transport=transport,
            model_flag=(model_flag,) if model_flag else (),
        )
    elif preset:
        key = preset.strip().lower()
        if key == "auto":
            spec = discover_preset()
            if spec is None:
                raise AgentUnavailable(_no_agent_message())
            return _apply_roots(spec, install_roots)
        if key not in PRESETS:
            raise AgentUnavailable(
                f"Unknown agent preset '{preset}'. Known presets: "
                f"{', '.join(sorted(PRESETS))}, auto."
            )
        spec = PRESETS[key]
    else:
        spec = discover_preset()
        if spec is None:
            raise AgentUnavailable(_no_agent_message())

    exe = spec.complete_cmd[0]
    if shutil.which(exe) is None:
        raise AgentUnavailable(
            f"Agent CLI '{exe}' (preset '{spec.name}') is not on PATH. "
            f"Install it, choose a different --agent, or pass --agent-cmd "
            f"with a command template."
        )
    return _apply_roots(spec, install_roots)


def _apply_roots(spec: AgentSpec, install_roots: list[str] | None) -> AgentSpec:
    if not install_roots:
        return spec
    from dataclasses import replace

    targets = tuple(InstallTarget("skill_md", root) for root in install_roots)
    return replace(spec, install_targets=targets)


def _no_agent_message() -> str:
    known = ", ".join(sorted(PRESETS))
    return (
        "No supported agent CLI found on PATH. Add one of these\n"
        f"  presets: {known}\n"
        "or point the skill at any CLI with:\n"
        "  --agent-cmd \"your-agent --flag {prompt}\"\n"
        "  SKILL_CREATOR_AGENT_CMD=\"your-agent --flag {prompt}\""
    )


def describe(spec: AgentSpec) -> str:
    """One-line summary for logs and reports."""
    exe = spec.complete_cmd[0]
    where = shutil.which(exe) or "not found on PATH"
    return f"agent={spec.name} exe={exe} ({where})"


def agent_environment() -> dict[str, str]:
    """Environment for nested invocations, with nesting guards removed."""
    return {k: v for k, v in os.environ.items() if k not in _NESTING_GUARDS}


# --------------------------------------------------------------------------
# Completion
# --------------------------------------------------------------------------

def complete(
    prompt: str,
    spec: AgentSpec,
    *,
    model: str | None = None,
    timeout: int = 300,
    cwd: str | Path | None = None,
) -> str:
    """Send one prompt to the agent CLI and return its text answer."""
    argv = build_command(
        spec.complete_cmd,
        spec,
        prompt=prompt if spec.transport == "argv" else None,
        model=model,
    )

    try:
        result = subprocess.run(
            argv,
            input=prompt if spec.transport == "stdin" else None,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=agent_environment(),
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
        )
    except FileNotFoundError as exc:
        raise AgentUnavailable(
            f"Agent CLI '{spec.complete_cmd[0]}' could not be started: {exc}"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Agent CLI timed out after {timeout}s while generating a completion."
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            f"{spec.complete_cmd[0]} exited {result.returncode}\n"
            f"stderr: {(result.stderr or '').strip()[:2000]}"
        )
    return result.stdout


# --------------------------------------------------------------------------
# Trigger probe
# --------------------------------------------------------------------------

def install_probe_skill(
    project_root: Path,
    skill_name: str,
    description: str,
    spec: AgentSpec,
) -> tuple[list[Path], str]:
    """Publish a throwaway copy of the skill so the agent can discover it.

    Returns ``(created_paths, marker)``. The marker is a random token that
    appears **only** inside the skill body, never in the skill's name. That
    distinction matters: an agent that merely lists or echoes the skill name
    without reading it must not count as triggered, and the name is visible in
    the skill list whereas the body is not.

    Both supported layouts are written because CLIs differ: some read
    ``<dir>/<name>/SKILL.md``, others read ``<dir>/<name>.md`` commands.
    """
    unique = uuid.uuid4().hex[:8]
    probe_name = f"{skill_name}-probe-{unique}"
    # The token deliberately omits the skill name so it cannot be matched by an
    # echo of the skill list. Surrounding it with an unusual prefix makes an
    # accidental collision with real output essentially impossible.
    marker = f"PROBE-TOKEN-{unique}"
    created: list[Path] = []

    body = (
        f"---\n"
        f"name: {probe_name}\n"
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        f"---\n\n"
        f"# {probe_name}\n\n"
        f"Marker: {marker}\n\n"
        f"{description}\n"
    )

    for target in spec.install_targets:
        base = project_root / target.rel_dir
        try:
            base.mkdir(parents=True, exist_ok=True)
            if target.style == "skill_md":
                skill_dir = base / probe_name
                skill_dir.mkdir(parents=True, exist_ok=True)
                path = skill_dir / "SKILL.md"
            else:
                path = base / f"{probe_name}.md"
            path.write_text(body, encoding="utf-8")
            created.append(path)
        except OSError as exc:  # read-only or sandboxed project
            print(
                f"Warning: could not install probe skill at {base}: {exc}",
                file=sys.stderr,
            )
    return created, marker


def remove_probe_skill(paths: list[Path]) -> None:
    """Remove probe files, then any skill directory left empty by the cleanup."""
    for path in paths:
        try:
            path.unlink(missing_ok=True)
            parent = path.parent
            # Only remove directories this probe created, never a skills root.
            if "-probe-" in parent.name and parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()
        except OSError as exc:
            print(f"Warning: could not clean up probe file {path}: {exc}", file=sys.stderr)


def _load_json_event(line: str) -> dict | None:
    line = line.strip()
    if not line or not line.startswith("{"):
        return None
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return None
    return event if isinstance(event, dict) else None


def _structured_probe(process: subprocess.Popen, marker: str, timeout: int) -> bool:
    """Watch a JSON-lines event stream and report whether the skill was loaded.

    Structured CLIs announce tool calls as ``content_block_start`` events. If
    the agent's first tool call is a skill lookup that names our probe skill we
    count it as triggered; any other tool call means it went another way.
    """
    assert process.stdout is not None
    triggered = False
    pending_tool: str | None = None
    accumulated = ""
    deadline = time.time() + timeout
    lines: queue.Queue[bytes | None] = queue.Queue()

    def _pump() -> None:
        """Forward one line at a time.

        Reading fixed-size byte blocks instead would block until the buffer
        fills, so a CLI that emits an event and then goes quiet would hide the
        trigger until timeout. Iterating the stream yields each newline as soon
        as it arrives.
        """
        try:
            for raw in process.stdout:  # type: ignore[union-attr]
                lines.put(raw)
        except (OSError, ValueError):
            pass
        finally:
            lines.put(None)

    threading.Thread(target=_pump, daemon=True).start()

    def handle_line(raw: bytes) -> bool | None:
        """Interpret one stream line. True/False stops, None continues."""
        nonlocal pending_tool, accumulated, triggered
        event = _load_json_event(raw.decode("utf-8", errors="replace"))
        if not event:
            return None
        kind = event.get("type")
        if kind == "stream_event":
            se = event.get("event") or {}
            se_type = se.get("type", "")
            if se_type == "content_block_start":
                block = se.get("content_block") or {}
                if block.get("type") == "tool_use":
                    name = block.get("name", "")
                    if name in ("Skill", "Read"):
                        pending_tool = name
                        accumulated = ""
                    else:
                        return False
            elif se_type == "content_block_delta" and pending_tool:
                delta = se.get("delta") or {}
                if delta.get("type") == "input_json_delta":
                    accumulated += delta.get("partial_json", "")
                    if marker in accumulated:
                        return True
            elif se_type in ("content_block_stop", "message_stop"):
                if pending_tool:
                    return marker in accumulated
                if se_type == "message_stop":
                    return False
        elif kind == "assistant":
            for item in (event.get("message") or {}).get("content", []) or []:
                if item.get("type") != "tool_use":
                    continue
                payload = json.dumps(item.get("input") or {}, ensure_ascii=False)
                name = item.get("name", "")
                if name in ("Skill", "Read") and marker in payload:
                    triggered = True
                return triggered
        elif kind == "result":
            return triggered
        return None

    while True:
        remaining = deadline - time.time()
        if remaining <= 0:
            break
        try:
            raw = lines.get(timeout=remaining)
        except queue.Empty:
            break
        if raw is None:
            break
        stop = handle_line(raw)
        if stop is not None:
            return stop
    return triggered


def probe_trigger(
    query: str,
    project_root: Path,
    skill_name: str,
    description: str,
    spec: AgentSpec,
    *,
    model: str | None = None,
    timeout: int = 60,
    extra_marker: str | None = None,
) -> bool:
    """Run one query and report whether the agent loaded the probe skill.

    Structured CLIs are detected from their event stream. For plain-text CLIs
    the fallback is a text heuristic: the answer must contain the probe token,
    which exists only inside the installed skill body and never in the skill's
    name. That keeps an agent that merely lists skill names from scoring as
    triggered, but it is still weaker evidence than an event stream — a CLI
    that pastes skill bodies into context without being asked could match it.
    This limitation is documented in SKILL.md rather than hidden.
    """
    created, marker = install_probe_skill(project_root, skill_name, description, spec)
    if not created:
        raise AgentUnavailable(
            "Could not install the probe skill anywhere — every candidate "
            "directory was unwritable. Pass --install-root to point at a "
            "writable skill directory."
        )
    try:
        return run_probe(
            query=query,
            project_root=project_root,
            marker=marker,
            spec=spec,
            model=model,
            timeout=timeout,
        )
    finally:
        remove_probe_skill(created)


def run_probe(
    query: str,
    project_root: Path,
    marker: str,
    spec: AgentSpec,
    *,
    model: str | None = None,
    timeout: int = 60,
) -> bool:
    """Run one query against an ALREADY installed probe and report a trigger.

    Split out from ``probe_trigger`` so a batch run can install the probe once
    and share it. That matters for correctness, not just speed: the probe body
    is identical for every query in an eval (same skill, same description), so
    concurrent workers seeing each other's copies is harmless when they share
    one marker. Installing a fresh probe per query would give each copy a
    different token, and a worker that happened to read a neighbour's copy would
    be scored as "did not trigger" even though the skill was clearly used.
    """
    argv = build_command(spec.probe_cmd, spec, prompt=query, model=model)

    process = subprocess.Popen(
        argv,
        stdin=subprocess.PIPE if spec.transport == "stdin" else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env=agent_environment(),
        cwd=str(project_root),
    )
    if spec.transport == "stdin" and process.stdin:
        try:
            process.stdin.write(query.encode("utf-8"))
            process.stdin.close()
        except OSError:
            pass

    try:
        if spec.structured_output:
            return _structured_probe(process, marker, timeout)
        raw = process.communicate(timeout=timeout)[0] or b""
        return marker in raw.decode("utf-8", errors="replace")
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
