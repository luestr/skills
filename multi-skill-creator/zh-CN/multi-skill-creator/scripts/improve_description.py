#!/usr/bin/env python3
"""Improve a skill description from trigger-eval results.

Takes the JSON produced by run_eval.py, asks the configured agent CLI for a
better description, and returns the new text plus the attempt history. Because
the agent is resolved through ``agent_cli``, this runs against whatever CLI the
user has — no vendor SDK, no API key, no separate auth.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts import agent_cli  # noqa: E402
    from scripts.utils import parse_skill_md  # noqa: E402
else:
    from scripts import agent_cli
    from scripts.utils import parse_skill_md

DESCRIPTION_CHAR_LIMIT = 1024


def build_improvement_prompt(
    skill_name: str,
    skill_content: str,
    current_description: str,
    eval_results: dict,
    history: list[dict],
    test_results: dict | None = None,
) -> str:
    """Assemble the rewrite prompt from eval failures and past attempts."""
    failed_triggers = [
        r for r in eval_results["results"] if r["should_trigger"] and not r["pass"]
    ]
    false_triggers = [
        r for r in eval_results["results"] if not r["should_trigger"] and not r["pass"]
    ]

    train_score = f"{eval_results['summary']['passed']}/{eval_results['summary']['total']}"
    if test_results:
        test_score = f"{test_results['summary']['passed']}/{test_results['summary']['total']}"
        scores_summary = f"Train: {train_score}, Test: {test_score}"
    else:
        scores_summary = f"Train: {train_score}"

    prompt = f"""You are optimizing the description of an agent skill named "{skill_name}".

A skill is progressive disclosure for an AI agent: the agent sees only the
name and description when deciding whether to load anything, and only then
reads SKILL.md with its full instructions and bundled resources. The
description is therefore the entire triggering mechanism. Your goal is a
description that loads the skill for relevant queries and stays silent for
irrelevant ones.

Here is the current description:
<current_description>
"{current_description}"
</current_description>

Current scores ({scores_summary}):
<scores_summary>
"""
    if failed_triggers:
        prompt += "FAILED TO TRIGGER (should have triggered but didn't):\n"
        for r in failed_triggers:
            prompt += f'  - "{r["query"]}" (triggered {r["triggers"]}/{r["runs"]} times)\n'
        prompt += "\n"

    if false_triggers:
        prompt += "FALSE TRIGGERS (triggered but shouldn't have):\n"
        for r in false_triggers:
            prompt += f'  - "{r["query"]}" (triggered {r["triggers"]}/{r["runs"]} times)\n'
        prompt += "\n"

    if history:
        prompt += (
            "PREVIOUS ATTEMPTS (do NOT repeat these — try something "
            "structurally different):\n\n"
        )
        for h in history:
            train_s = f"{h.get('train_passed', h.get('passed', 0))}/{h.get('train_total', h.get('total', 0))}"
            test_s = (
                f"{h.get('test_passed')}/{h.get('test_total')}"
                if h.get("test_passed") is not None
                else None
            )
            score_str = f"train={train_s}" + (f", test={test_s}" if test_s else "")
            prompt += f"<attempt {score_str}>\n"
            prompt += f'Description: "{h["description"]}"\n'
            if "results" in h:
                prompt += "Train results:\n"
                for r in h["results"]:
                    status = "PASS" if r["pass"] else "FAIL"
                    prompt += (
                        f'  [{status}] "{r["query"][:80]}" '
                        f"(triggered {r['triggers']}/{r['runs']})\n"
                    )
            if h.get("note"):
                prompt += f'Note: {h["note"]}\n'
            prompt += "</attempt>\n\n"

    prompt += f"""</scores_summary>

Skill content (for context on what the skill does):
<skill_content>
{skill_content}
</skill_content>

Write a new, better description based on those failures. "Based on the
failures" is a tricky line to walk: do not produce an ever-growing list of
specific queries this skill should or shouldn't fire on. Generalize instead —
step back from the individual failures to the broader categories of user intent
where this skill helps, and where a different approach is a better answer. Two
reasons: overfitting to a handful of examples makes the skill useless at scale,
and a long list gets injected into every single query, so it must stay compact.

Concretely: aim for roughly 100-200 words. There is a hard limit of
{DESCRIPTION_CHAR_LIMIT} characters — anything longer is truncated, so stay
comfortably under it.

What tends to work:
- Phrase it in the imperative — "Use this skill for ...", not "this skill does ...".
- Describe the user's intent and situation, not the internal mechanics.
- Compete for attention: the description sits next to other skills' descriptions,
  so make it distinctive and instantly recognizable.
- If several attempts have already failed, change the shape of the sentence,
  not just the adjectives.

Be creative; you get multiple attempts and the highest-scoring one wins.

Respond with only the new description inside <new_description> tags, nothing else."""

    return prompt


def extract_description(text: str) -> str:
    """Pull the description out of <new_description> tags, tolerating misses."""
    match = re.search(r"<new_description>(.*?)</new_description>", text, re.DOTALL)
    return (match.group(1) if match else text).strip().strip('"').strip()


def validate_description(candidate: str) -> str | None:
    """Return a reason string when a proposed description must be rejected.

    The rewrite is written straight into SKILL.md, so a bad one is worse than
    no rewrite at all. These checks mirror the ones quick_validate.py applies,
    but run *before* the file is touched — catching a bad description here is
    recoverable, catching it after means the skill is temporarily invalid.
    """
    if not candidate.strip():
        return "empty description"
    if "<" in candidate or ">" in candidate:
        return "contains angle brackets, which the frontmatter schema rejects"
    if len(candidate) > DESCRIPTION_CHAR_LIMIT:
        return (
            f"{len(candidate)} characters, over the {DESCRIPTION_CHAR_LIMIT}"
            "-character limit"
        )
    return None


def improve_description(
    skill_name: str,
    skill_content: str,
    current_description: str,
    eval_results: dict,
    history: list[dict],
    spec: agent_cli.AgentSpec,
    model: str | None = None,
    test_results: dict | None = None,
    log_dir: Path | None = None,
    iteration: int | None = None,
    timeout: int = 600,
) -> str:
    """Ask the agent for an improved description and enforce the char limit."""
    prompt = build_improvement_prompt(
        skill_name=skill_name,
        skill_content=skill_content,
        current_description=current_description,
        eval_results=eval_results,
        history=history,
        test_results=test_results,
    )

    response = agent_cli.complete(prompt, spec, model=model, timeout=timeout)
    description = extract_description(response)

    transcript: dict = {
        "iteration": iteration,
        "agent": agent_cli.describe(spec),
        "prompt": prompt,
        "response": response,
        "parsed_description": description,
        "char_count": len(description),
        "over_limit": len(description) > DESCRIPTION_CHAR_LIMIT,
    }

    # The prompt states the limit, but a model can still blow past it. One
    # extra call that quotes the too-long text is cheaper than shipping a
    # description the harness will silently truncate.
    if len(description) > DESCRIPTION_CHAR_LIMIT:
        shorten_prompt = (
            f"{prompt}\n\n---\n\n"
            f"A previous attempt produced this description, which at "
            f"{len(description)} characters is over the {DESCRIPTION_CHAR_LIMIT}"
            f"-character hard limit:\n\n"
            f'"{description}"\n\n'
            f"Rewrite it to be under {DESCRIPTION_CHAR_LIMIT} characters while "
            f"keeping the most important trigger words and intent coverage. "
            f"Respond with only the new description in <new_description> tags."
        )
        shorten_response = agent_cli.complete(
            shorten_prompt, spec, model=model, timeout=timeout
        )
        shortened = extract_description(shorten_response)

        transcript["rewrite_prompt"] = shorten_prompt
        transcript["rewrite_response"] = shorten_response
        transcript["rewrite_description"] = shortened
        transcript["rewrite_char_count"] = len(shortened)
        description = shortened

    # A rejected rewrite must not reach SKILL.md. Keeping the previous
    # description is strictly better than installing an invalid one, and the
    # reason is logged so the caller can report it.
    rejection = validate_description(description)
    if rejection:
        transcript["rejected_description"] = description
        transcript["rejection_reason"] = rejection
        description = current_description
        print(
            f"Warning: rejected the proposed description ({rejection}); "
            f"keeping the current one.",
            file=sys.stderr,
        )

    transcript["final_description"] = description

    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"improve_iter_{iteration or 'unknown'}.json"
        log_file.write_text(
            json.dumps(transcript, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    return description


def main() -> None:
    from scripts.run_eval import add_agent_arguments, resolve_from_args

    parser = argparse.ArgumentParser(
        description="Improve a skill description based on eval results"
    )
    parser.add_argument("--eval-results", required=True, help="Path to eval results JSON (from run_eval.py)")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--history", default=None, help="Path to history JSON (previous attempts)")
    parser.add_argument("--model", default=None, help="Model to pass to the agent CLI, if it accepts one")
    parser.add_argument("--timeout", type=int, default=600, help="Timeout per agent call in seconds")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    add_agent_arguments(parser)
    args = parser.parse_args()

    skill_path = Path(args.skill_path)
    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    eval_results = json.loads(Path(args.eval_results).read_text(encoding="utf-8"))
    history = []
    if args.history:
        history = json.loads(Path(args.history).read_text(encoding="utf-8"))

    try:
        spec = resolve_from_args(args)
    except agent_cli.AgentUnavailable as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    name, _, content = parse_skill_md(skill_path)
    current_description = eval_results["description"]

    if args.verbose:
        print(f"Agent: {agent_cli.describe(spec)}", file=sys.stderr)
        print(f"Current: {current_description}", file=sys.stderr)
        print(
            f"Score: {eval_results['summary']['passed']}/{eval_results['summary']['total']}",
            file=sys.stderr,
        )

    new_description = improve_description(
        skill_name=name,
        skill_content=content,
        current_description=current_description,
        eval_results=eval_results,
        history=history,
        spec=spec,
        model=args.model,
        timeout=args.timeout,
    )

    if args.verbose:
        print(f"Improved: {new_description}", file=sys.stderr)

    output = {
        "description": new_description,
        "history": history + [{
            "description": current_description,
            "passed": eval_results["summary"]["passed"],
            "failed": eval_results["summary"]["failed"],
            "total": eval_results["summary"]["total"],
            "results": eval_results["results"],
        }],
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
