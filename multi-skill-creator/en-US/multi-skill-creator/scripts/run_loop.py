#!/usr/bin/env python3
"""Run the eval + improve loop until every query passes or iterations run out.

Combines run_eval.py and improve_description.py, tracking each attempt and
returning the best description found. A train/test split keeps the optimizer
from overfitting: improvements are driven by train failures and the winner is
picked by held-out test score.

The agent behind both halves is whatever ``agent_cli`` resolves, so the loop is
not tied to one vendor's CLI.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
import time
import webbrowser
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts import agent_cli  # noqa: E402
    from scripts.generate_report import generate_html  # noqa: E402
    from scripts.improve_description import improve_description  # noqa: E402
    from scripts.run_eval import (  # noqa: E402
        add_agent_arguments,
        find_project_root,
        resolve_from_args,
        run_eval,
    )
    from scripts.utils import parse_skill_md  # noqa: E402
else:
    from scripts import agent_cli
    from scripts.generate_report import generate_html
    from scripts.improve_description import improve_description
    from scripts.run_eval import (
        add_agent_arguments,
        find_project_root,
        resolve_from_args,
        run_eval,
    )
    from scripts.utils import parse_skill_md


def split_eval_set(
    eval_set: list[dict], holdout: float, seed: int = 42
) -> tuple[list[dict], list[dict]]:
    """Split into train/test, stratified so both keep triggering examples.

    Small eval sets are normal while a skill is still being drafted, so each
    stratum leaves at least one query in train. If a stratum is too small to
    split at all, its queries all stay in train — an empty train set would let
    the loop report success without actually testing anything.
    """
    random.seed(seed)

    trigger = [e for e in eval_set if e["should_trigger"]]
    no_trigger = [e for e in eval_set if not e["should_trigger"]]

    random.shuffle(trigger)
    random.shuffle(no_trigger)

    def split(group: list[dict]) -> tuple[list[dict], list[dict]]:
        if len(group) < 2:
            return group, []
        n_test = min(max(1, int(len(group) * holdout)), len(group) - 1)
        return group[n_test:], group[:n_test]

    trigger_train, trigger_test = split(trigger)
    no_trigger_train, no_trigger_test = split(no_trigger)

    return trigger_train + no_trigger_train, trigger_test + no_trigger_test


def run_loop(
    eval_set: list[dict],
    skill_path: Path,
    description_override: str | None,
    num_workers: int,
    timeout: int,
    max_iterations: int,
    runs_per_query: int,
    trigger_threshold: float,
    holdout: float,
    spec: agent_cli.AgentSpec,
    model: str | None,
    verbose: bool,
    improve_timeout: int = 600,
    live_report_path: Path | None = None,
    log_dir: Path | None = None,
) -> dict:
    """Run the eval + improvement loop and return the best description found."""
    project_root = find_project_root()
    name, original_description, content = parse_skill_md(skill_path)
    current_description = description_override or original_description

    if holdout > 0:
        train_set, test_set = split_eval_set(eval_set, holdout)
    else:
        train_set, test_set = eval_set, []

    if not train_set:
        raise ValueError(
            "The eval set is empty, so there is nothing to evaluate. Add a few "
            "should-trigger and should-not-trigger queries first."
        )

    if verbose:
        print(f"Agent: {agent_cli.describe(spec)}", file=sys.stderr)
        if test_set:
            print(
                f"Split: {len(train_set)} train, {len(test_set)} test (holdout={holdout})",
                file=sys.stderr,
            )
        else:
            print(f"No holdout: all {len(train_set)} queries used for training", file=sys.stderr)

    history: list[dict] = []
    exit_reason = "unknown"

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n{'=' * 60}", file=sys.stderr)
            print(f"Iteration {iteration}/{max_iterations}", file=sys.stderr)
            print(f"Description: {current_description}", file=sys.stderr)
            print(f"{'=' * 60}", file=sys.stderr)

        # Evaluate train and test in one batch so the workers stay saturated.
        all_results = run_eval(
            eval_set=train_set + test_set,
            skill_name=name,
            description=current_description,
            num_workers=num_workers,
            timeout=timeout,
            project_root=project_root,
            agent_spec=spec,
            runs_per_query=runs_per_query,
            trigger_threshold=trigger_threshold,
            model=model,
        )

        train_queries = {q["query"] for q in train_set}
        train_results_list = [r for r in all_results["results"] if r["query"] in train_queries]
        test_results_list = [r for r in all_results["results"] if r["query"] not in train_queries]

        train_passed = sum(1 for r in train_results_list if r["pass"])
        train_total = len(train_results_list)
        train_summary = {
            "passed": train_passed,
            "failed": train_total - train_passed,
            "total": train_total,
        }
        train_results = {"results": train_results_list, "summary": train_summary}

        if test_set:
            test_passed = sum(1 for r in test_results_list if r["pass"])
            test_total = len(test_results_list)
            test_summary = {
                "passed": test_passed,
                "failed": test_total - test_passed,
                "total": test_total,
            }
            test_results = {"results": test_results_list, "summary": test_summary}
        else:
            test_results = None
            test_summary = None

        history.append({
            "iteration": iteration,
            "description": current_description,
            "train_passed": train_summary["passed"],
            "train_failed": train_summary["failed"],
            "train_total": train_summary["total"],
            "train_results": train_results["results"],
            "test_passed": test_summary["passed"] if test_summary else None,
            "test_failed": test_summary["failed"] if test_summary else None,
            "test_total": test_summary["total"] if test_summary else None,
            "test_results": test_results["results"] if test_results else None,
            # Kept for the report generator, which reads the flat keys.
            "passed": train_summary["passed"],
            "failed": train_summary["failed"],
            "total": train_summary["total"],
            "results": train_results["results"],
        })

        if live_report_path:
            live_report_path.write_text(
                generate_html(
                    {
                        "original_description": original_description,
                        "best_description": current_description,
                        "best_score": "in progress",
                        "iterations_run": len(history),
                        "holdout": holdout,
                        "train_size": len(train_set),
                        "test_size": len(test_set),
                        "agent": agent_cli.describe(spec),
                        "history": history,
                    },
                    auto_refresh=True,
                    skill_name=name,
                ),
                encoding="utf-8",
            )

        if verbose:
            def print_stats(label: str, results: list[dict]) -> None:
                pos = [r for r in results if r["should_trigger"]]
                neg = [r for r in results if not r["should_trigger"]]
                tp = sum(r["triggers"] for r in pos)
                pos_runs = sum(r["runs"] for r in pos)
                fn = pos_runs - tp
                fp = sum(r["triggers"] for r in neg)
                neg_runs = sum(r["runs"] for r in neg)
                tn = neg_runs - fp
                total = tp + tn + fp + fn
                precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
                accuracy = (tp + tn) / total if total > 0 else 0.0
                print(
                    f"{label}: {tp + tn}/{total} correct, precision={precision:.0%} "
                    f"recall={recall:.0%} accuracy={accuracy:.0%}",
                    file=sys.stderr,
                )
                for r in results:
                    status = "PASS" if r["pass"] else "FAIL"
                    print(
                        f"  [{status}] rate={r['triggers']}/{r['runs']} "
                        f"expected={r['should_trigger']}: {r['query'][:60]}",
                        file=sys.stderr,
                    )

            print_stats("Train", train_results["results"])
            if test_summary:
                print_stats("Test ", test_results["results"])

        if train_summary["failed"] == 0:
            exit_reason = f"all_passed (iteration {iteration})"
            if verbose:
                print(f"\nAll train queries passed on iteration {iteration}!", file=sys.stderr)
            break

        if iteration == max_iterations:
            exit_reason = f"max_iterations ({max_iterations})"
            if verbose:
                print(f"\nMax iterations reached ({max_iterations}).", file=sys.stderr)
            break

        if verbose:
            print("\nImproving description...", file=sys.stderr)

        # Strip test scores before asking for an improvement, so the rewrite
        # cannot be tuned against the held-out set.
        blinded_history = [
            {k: v for k, v in h.items() if not k.startswith("test_")} for h in history
        ]
        current_description = improve_description(
            skill_name=name,
            skill_content=content,
            current_description=current_description,
            eval_results=train_results,
            history=blinded_history,
            spec=spec,
            model=model,
            log_dir=log_dir,
            iteration=iteration,
            timeout=improve_timeout,
        )

        if verbose:
            print(f"Proposed: {current_description}", file=sys.stderr)

    # Pick the winner by held-out score when we have one, otherwise by train.
    if test_set:
        best = max(history, key=lambda h: h["test_passed"] or 0)
        best_score = f"{best['test_passed']}/{best['test_total']}"
    else:
        best = max(history, key=lambda h: h["train_passed"])
        best_score = f"{best['train_passed']}/{best['train_total']}"

    if verbose:
        print(f"\nExit reason: {exit_reason}", file=sys.stderr)
        print(f"Best score: {best_score} (iteration {best['iteration']})", file=sys.stderr)

    return {
        "exit_reason": exit_reason,
        "agent": agent_cli.describe(spec),
        "original_description": original_description,
        "best_description": best["description"],
        "best_score": best_score,
        "best_train_score": f"{best['train_passed']}/{best['train_total']}",
        "best_test_score": f"{best['test_passed']}/{best['test_total']}" if test_set else None,
        "final_description": current_description,
        "iterations_run": len(history),
        "holdout": holdout,
        "train_size": len(train_set),
        "test_size": len(test_set),
        "history": history,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the eval + improve loop")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override starting description")
    parser.add_argument("--num-workers", type=int, default=8, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout per query in seconds")
    parser.add_argument("--improve-timeout", type=int, default=600, help="Timeout per rewrite call in seconds")
    parser.add_argument("--max-iterations", type=int, default=5, help="Max improvement iterations")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--holdout", type=float, default=0.4, help="Fraction held out for testing (0 disables)")
    parser.add_argument("--model", default=None, help="Model to pass to the agent CLI, if it accepts one")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    parser.add_argument(
        "--report",
        default="auto",
        help="HTML report path (default: 'auto' for a temp file, 'none' to disable)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Write the report but never try to open a browser (headless hosts).",
    )
    parser.add_argument(
        "--results-dir",
        default=None,
        help="Save results.json, report.html and logs to a timestamped subdirectory here",
    )
    add_agent_arguments(parser)
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text(encoding="utf-8"))
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    try:
        spec = resolve_from_args(args)
    except agent_cli.AgentUnavailable as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    name, _, _ = parse_skill_md(skill_path)

    live_report_path = None
    if args.report != "none":
        if args.report == "auto":
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            live_report_path = (
                Path(tempfile.gettempdir())
                / f"skill_description_report_{skill_path.name}_{timestamp}.html"
            )
        else:
            live_report_path = Path(args.report)
        live_report_path.write_text(
            "<html><body><h1>Starting optimization loop...</h1>"
            "<meta http-equiv='refresh' content='5'></body></html>",
            encoding="utf-8",
        )
        # webbrowser.open is a no-op on headless hosts, but it can raise on
        # some sandboxes — the report is still written either way.
        if not args.no_browser:
            try:
                webbrowser.open(live_report_path.as_uri())
            except Exception as exc:  # noqa: BLE001 - browser opening is optional
                print(f"Note: could not open a browser ({exc}); report at {live_report_path}", file=sys.stderr)

    results_dir = None
    if args.results_dir:
        timestamp = time.strftime("%Y-%m-%d_%H%M%S")
        results_dir = Path(args.results_dir) / timestamp
        results_dir.mkdir(parents=True, exist_ok=True)

    log_dir = results_dir / "logs" if results_dir else None

    output = run_loop(
        eval_set=eval_set,
        skill_path=skill_path,
        description_override=args.description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        max_iterations=args.max_iterations,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        holdout=args.holdout,
        spec=spec,
        model=args.model,
        verbose=args.verbose,
        improve_timeout=args.improve_timeout,
        live_report_path=live_report_path,
        log_dir=log_dir,
    )

    json_output = json.dumps(output, indent=2, ensure_ascii=False)
    print(json_output)
    if results_dir:
        (results_dir / "results.json").write_text(json_output, encoding="utf-8")

    if live_report_path:
        report_html = generate_html(output, auto_refresh=False, skill_name=name)
        live_report_path.write_text(report_html, encoding="utf-8")
        print(f"\nReport: {live_report_path}", file=sys.stderr)
        if results_dir:
            (results_dir / "report.html").write_text(report_html, encoding="utf-8")

    if results_dir:
        print(f"Results saved to: {results_dir}", file=sys.stderr)


if __name__ == "__main__":
    main()
