#!/usr/bin/env python3
"""Run a trigger evaluation for a skill description.

Answers one question: given this description, does an agent actually load the
skill for the queries where it should, and stay away from the ones where it
shouldn't? The agent is whatever CLI ``agent_cli`` resolves — Claude Code,
Codex, Gemini CLI, Cursor, OpenCode, Finch, or any custom command template — so
this works the same way in any harness that can run Python.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

if __package__ in (None, ""):
    # Allow `python scripts/run_eval.py` as well as `python -m scripts.run_eval`.
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts import agent_cli  # noqa: E402
    from scripts.utils import parse_skill_md  # noqa: E402
else:
    from scripts import agent_cli
    from scripts.utils import parse_skill_md


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from cwd looking for a recognizable agent project marker.

    The probe skill has to be installed inside the project the CLI treats as
    its root, otherwise the agent will not discover it. We look for the marker
    directories of the known CLIs first, then fall back to cwd or git root.
    """
    current = (start or Path.cwd()).resolve()
    markers = {
        ".claude", ".finch", ".agents", ".gemini", ".cursor",
        ".opencode", ".git",
    }
    for parent in [current, *current.parents]:
        if any((parent / marker).exists() for marker in markers):
            return parent
    return current


def run_single_query(
    query: str,
    marker: str,
    timeout: int,
    project_root: str,
    agent_spec: agent_cli.AgentSpec,
    model: str | None = None,
) -> bool:
    """Probe one query against the shared, already-installed probe skill."""
    return agent_cli.run_probe(
        query=query,
        project_root=Path(project_root),
        marker=marker,
        spec=agent_spec,
        model=model,
        timeout=timeout,
    )


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    agent_spec: agent_cli.AgentSpec,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
) -> dict:
    """Run the full eval set and return per-query trigger rates.

    The probe skill is installed **once** for the whole batch and removed in a
    finally block. Every worker shares its marker, which is what keeps parallel
    measurement honest: the probe content is identical across queries (same
    skill, same description), so one shared copy is both cheaper and immune to
    the cross-talk that per-query probes would cause. Installing a distinct
    token per query meant a worker reading a neighbour's copy scored as "did not
    trigger" even though the skill was plainly used — with the default 8 workers
    that quietly depressed every trigger rate.
    """
    created, marker = agent_cli.install_probe_skill(
        project_root, skill_name, description, agent_spec
    )
    if not created:
        raise agent_cli.AgentUnavailable(
            "Could not install the probe skill in the project — every candidate "
            "directory was unwritable. Pass --install-root to point at a "
            "writable skill directory."
        )

    results = []
    try:
        # A spec is picklable, but a freshly-resolved one may carry a Path; pass it
        # explicitly so child processes never re-resolve the agent differently.
        with ProcessPoolExecutor(max_workers=max(1, num_workers)) as executor:
            future_to_info = {}
            for index, item in enumerate(eval_set):
                for run_idx in range(runs_per_query):
                    future = executor.submit(
                        run_single_query,
                        item["query"],
                        marker,
                        timeout,
                        str(project_root),
                        agent_spec,
                        model,
                    )
                    future_to_info[future] = ({**item, "_index": index}, run_idx)

        # Key results by the entry's position, not its query text. Two eval
        # entries that happen to share a query string are still two test cases:
        # keying by text would merge them into one result with an inflated
        # "runs" count, and the summary total would stop matching what the user
        # authored. `index` is the entry's ordinal in the eval set.
        triggers_by_index: dict[int, list[bool]] = {}
        failures_by_index: dict[int, str] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            idx = item["_index"]
            triggers_by_index.setdefault(idx, [])
            try:
                triggers_by_index[idx].append(future.result())
            except Exception as exc:
                print(f"Warning: query failed: {exc}", file=sys.stderr)
                failures_by_index[idx] = str(exc)
                # A driver-level failure (missing CLI, unwritable project) is
                # not evidence that the skill failed to trigger. Counting it as
                # "did not trigger" silently biases every score downward.
                triggers_by_index[idx].append(False)

    finally:
        # Always remove the probe, even when a worker raised or the pool broke.
        agent_cli.remove_probe_skill(created)

    for idx in sorted(triggers_by_index):
        item = eval_set[idx]
        triggers = triggers_by_index[idx]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        did_pass = (
            trigger_rate >= trigger_threshold
            if should_trigger
            else trigger_rate < trigger_threshold
        )
        entry = {
            "query": item["query"],
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        }
        if idx in failures_by_index:
            # Surface the reason instead of hiding it behind a plain False.
            entry["error"] = failures_by_index[idx]
        results.append(entry)

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "agent": agent_cli.describe(agent_spec),
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def add_agent_arguments(parser: argparse.ArgumentParser) -> None:
    """Flags shared by every script that needs to talk to an agent CLI.

    Kept in one place so run_eval / improve_description / run_loop cannot drift
    apart on how the agent is selected.
    """
    group = parser.add_argument_group("agent")
    group.add_argument(
        "--agent",
        default=None,
        help=(
            "Agent CLI preset: "
            + ", ".join(sorted(agent_cli.PRESETS))
            + ", or 'auto' (default: auto-detect on PATH)."
        ),
    )
    group.add_argument(
        "--agent-cmd",
        default=None,
        help=(
            "Command template for any CLI, e.g. \"my-agent --print {prompt}\". "
            "Overrides --agent and the SKILL_CREATOR_AGENT_CMD env var."
        ),
    )
    group.add_argument(
        "--agent-transport",
        choices=("argv", "stdin"),
        default="argv",
        help="How a custom --agent-cmd receives the prompt (default: argv).",
    )
    group.add_argument(
        "--install-root",
        action="append",
        default=None,
        metavar="DIR",
        help=(
            "Skill directory to install the probe skill into, relative to the "
            "project root. Repeatable; overrides the preset's guess."
        ),
    )
    group.add_argument(
        "--agent-model-flag",
        default=None,
        metavar="FLAG",
        help=(
            "Flag a custom --agent-cmd uses to select a model (e.g. --model). "
            "Only needed with --agent-cmd; presets carry their own. Alternatively "
            "put {model} in the template."
        ),
    )


def resolve_from_args(args: argparse.Namespace) -> agent_cli.AgentSpec:
    return agent_cli.resolve_agent(
        preset=args.agent,
        cmd_template=args.agent_cmd,
        transport=args.agent_transport,
        install_roots=args.install_root,
        model_flag=args.agent_model_flag,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a trigger evaluation for a skill description"
    )
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=8, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="Model to pass to the agent CLI, if it accepts one")
    parser.add_argument("--project-root", default=None, help="Project root where the probe skill is installed")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    add_agent_arguments(parser)
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, _ = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = Path(args.project_root).resolve() if args.project_root else find_project_root()

    try:
        spec = resolve_from_args(args)
    except agent_cli.AgentUnavailable as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    if args.verbose:
        print(f"Agent: {agent_cli.describe(spec)}", file=sys.stderr)
        print(f"Project root: {project_root}", file=sys.stderr)
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        agent_spec=spec,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(
                f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}",
                file=sys.stderr,
            )

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
