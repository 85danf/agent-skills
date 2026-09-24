#!/usr/bin/env python3
"""Emit a copy-paste handoff prompt for a fresh session to implement a reviewed plan.

Captures a pinned baseline (git HEAD, branch, clean/dirty tree, optional test
run) and assembles a single fenced Markdown block. The agent supplies the
judgment parts (plan path, out-of-band pitfalls, extra context); this script
owns all formatting so the output cannot drift: backticked paths, one fenced
block, empty sections dropped, exactly one STOP gate in the baseline check.

Stdlib only. See SKILL.md for the agent workflow.
"""

from __future__ import annotations

import argparse
import os
import secrets
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def run_git(repo: str, *args: str) -> str | None:
    """Run git in `repo`; return stripped stdout, or None on failure."""
    try:
        out = subprocess.run(
            ["git", "-C", repo, *args],
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return out.stdout.strip()


@dataclass(frozen=True)
class SkillFamily:
    """A plan-execution skill family the handoff prompt can point to.

    Detected from the plan/spec paths (e.g. superpowers plans live under
    docs/superpowers/plans/). Add a new family here (e.g. another skill suite)
    without touching render() or detect_exec_skill_header().
    """

    id: str
    path_markers: tuple[str, ...]
    header_markers: tuple[str, ...]
    fallback_text: str


SKILL_FAMILIES: tuple[SkillFamily, ...] = (
    SkillFamily(
        id="superpowers",
        path_markers=("docs/superpowers/plans/", "docs/superpowers/specs/"),
        header_markers=("executing-plans", "subagent-driven-development", "REQUIRED SUB-SKILL"),
        fallback_text=(
            "Use your platform's plan-execution skill — `superpowers:executing-plans`, or "
            "`superpowers:subagent-driven-development` for independent tasks."
        ),
    ),
)

GENERIC_REQUIRED_SKILL_TEXT = "Implement the plan step-by-step."


def detect_skill_family(paths: list[str]) -> SkillFamily | None:
    """Identify the skill family in use from the plan/spec paths, if any."""
    for family in SKILL_FAMILIES:
        if any(marker in path for path in paths for marker in family.path_markers):
            return family
    return None


def required_skill_text(paths: list[str]) -> str:
    """'Required skill' fallback text: family-specific if detected, else generic."""
    family = detect_skill_family(paths)
    return family.fallback_text if family else GENERIC_REQUIRED_SKILL_TEXT


def detect_exec_skill_header(plan_text: str) -> bool:
    """True if the plan already names an execution skill in its header."""
    head = plan_text[:4000]
    markers = [marker for family in SKILL_FAMILIES for marker in family.header_markers]
    return any(marker in head for marker in markers)


def capture_baseline(
    repo: str,
    plan: str,
    specs: list[str],
    test_cmd: str | None,
    no_run: bool,
    pitfalls: list[str],
    context: list[str],
) -> dict[str, Any]:
    """Gather git state + optional test result + plan-header detection into a ctx dict."""
    toplevel = run_git(repo, "rev-parse", "--show-toplevel")
    if toplevel is None:
        sys.exit(f"error: {repo!r} is not inside a git working tree")
    repo_abs = toplevel

    plan_abs = plan if os.path.isabs(plan) else os.path.join(repo_abs, plan)
    if not os.path.isfile(plan_abs):
        sys.exit(f"error: plan file not found: {plan_abs}")
    with open(plan_abs, encoding="utf-8") as handle:
        plan_text = handle.read()

    spec_rels = []
    for spec in specs:
        spec_abs = spec if os.path.isabs(spec) else os.path.join(repo_abs, spec)
        if not os.path.isfile(spec_abs):
            sys.exit(f"error: spec file not found: {spec_abs}")
        spec_rels.append(os.path.relpath(spec_abs, repo_abs))

    main = run_git(repo_abs, "symbolic-ref", "refs/remotes/origin/HEAD", "--short")
    if main and main.startswith("origin/"):
        main = main[len("origin/") :]

    porcelain = run_git(repo_abs, "status", "--porcelain") or ""
    dirty_files = [line for line in porcelain.splitlines() if line.strip()]

    test_ran = bool(test_cmd) and not no_run
    test_passed: bool | None = None
    test_tail = ""
    if test_cmd and not no_run:
        proc = subprocess.run(shlex.split(test_cmd), cwd=repo_abs, capture_output=True, text=True)
        test_passed = proc.returncode == 0
        combined = (proc.stdout + proc.stderr).strip().splitlines()
        test_tail = combined[-1] if combined else ""

    plan_rel = os.path.relpath(plan_abs, repo_abs)

    return {
        "repo_abs": repo_abs,
        "plan_rel": plan_rel,
        "specs": spec_rels,
        "branch": run_git(repo_abs, "rev-parse", "--abbrev-ref", "HEAD") or "?",
        "main": main,
        "head_full": run_git(repo_abs, "rev-parse", "HEAD") or "?",
        "head_short": run_git(repo_abs, "rev-parse", "--short", "HEAD") or "?",
        "tree_clean": not dirty_files,
        "dirty_count": len(dirty_files),
        "test_cmd": test_cmd,
        "test_ran": test_ran,
        "test_passed": test_passed,
        "test_tail": test_tail,
        "has_header": detect_exec_skill_header(plan_text),
        "required_skill_text": required_skill_text([plan_rel, *spec_rels]),
        "pitfalls": pitfalls,
        "context": context,
    }


def render(ctx: dict[str, Any]) -> str:
    """Assemble the fenced handoff block. Empty sections are dropped."""
    repo = ctx["repo_abs"]
    lines: list[str] = ["```markdown"]
    lines.append(
        f"Implement the plan at `{ctx['plan_rel']}` in `{repo}`. Read it and follow its header."
    )

    lines.append("\n## Working directory and branch")
    lines.append(f"- Working directory: `{repo}`")
    lines.append(f"- Branch (already checked out): `{ctx['branch']}`")
    if ctx["main"]:
        lines.append(f"- Main branch: `{ctx['main']}`")

    if ctx["specs"]:
        lines.append("\n## Read these files first")
        for index, spec in enumerate(ctx["specs"], start=1):
            lines.append(f"{index}. `{spec}` — companion design/spec doc (the 'why').")
        lines.append(
            f"{len(ctx['specs']) + 1}. `{ctx['plan_rel']}` — the implementation "
            "plan; follow it task-by-task."
        )
    else:
        lines.append("\n## Plan file")
        lines.append(f"- `{ctx['plan_rel']}` — the implementation plan; follow it task-by-task.")

    if not ctx["has_header"]:
        lines.append("\n## Required skill")
        lines.append(f"The plan does not name an execution skill. {ctx['required_skill_text']}")

    lines.append("\n## Baseline check")
    lines.append(
        "Confirm the repo matches the state this plan was written against "
        "BEFORE starting. If anything below does not match, STOP and ask — do not start."
    )
    lines.append(
        f"- `git -C {repo} rev-parse HEAD` must equal `{ctx['head_full']}` (`{ctx['head_short']}`)."
    )
    if ctx["tree_clean"]:
        lines.append(
            f"- Working tree must be clean (`git -C {repo} status --porcelain` prints nothing)."
        )
    else:
        lines.append(
            f"- ⚠ At handoff the tree had {ctx['dirty_count']} uncommitted file(s). "
            "Commit or stash and re-pin the baseline before starting."
        )
    if ctx["test_ran"]:
        verdict = "passed" if ctx["test_passed"] else "⚠ FAILED"
        tail = f" (`{ctx['test_tail']}`)" if ctx["test_tail"] else ""
        lines.append(
            f"- Baseline tests {verdict} at handoff: `{ctx['test_cmd']}`{tail}. "
            "Re-run; if not green, STOP."
        )
    elif ctx["test_cmd"]:
        lines.append(
            f"- Baseline tests expected green: `{ctx['test_cmd']}`. "
            "Run before starting; if not green, STOP."
        )

    if ctx["pitfalls"]:
        lines.append("\n## Known friction")
        lines.extend(f"- {pitfall}" for pitfall in ctx["pitfalls"])

    if ctx["context"]:
        lines.append("\n## Other context")
        lines.extend(f"- {item}" for item in ctx["context"])

    lines.append("```")
    return "\n".join(lines)


def handoff_path(session_id: str, nonce: str) -> Path:
    """Build the session-namespaced, nonce-suffixed handoff file path."""
    return Path.home() / ".claude" / "tmp" / session_id / f"next-session-prompt-{nonce}.md"


def write_handoff(rendered: str) -> Path:
    """Write the handoff block to ~/.claude/tmp/<session>/next-session-prompt-<nonce>.md.

    Session subdir comes from CLAUDE_SESSION_ID; falls back to a random subdir when
    unset. The nonce is fresh per run so parallel sessions never collide.
    """
    session_id = os.environ.get("CLAUDE_SESSION_ID") or secrets.token_hex(4)
    path = handoff_path(session_id, secrets.token_hex(2))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered + "\n", encoding="utf-8")
    return path


def selfcheck() -> int:
    """Assert the renderer's section logic. Returns process exit code."""
    base = {
        "repo_abs": "/repo",
        "plan_rel": "docs/plan.md",
        "specs": [],
        "branch": "feature/x",
        "main": "master",
        "head_full": "0" * 40,
        "head_short": "0000000",
        "tree_clean": True,
        "dirty_count": 0,
        "test_cmd": "uv run pytest",
        "test_ran": True,
        "test_passed": True,
        "test_tail": "142 passed",
        "has_header": True,
        "required_skill_text": GENERIC_REQUIRED_SKILL_TEXT,
        "pitfalls": [],
        "context": [],
    }
    out = render(base)
    assert out.startswith("```markdown") and out.rstrip().endswith("```"), "one fenced block"
    assert out.count("```") == 2, "exactly one fenced block"
    assert "## Required skill" not in out, "defer to header when present"
    assert "STOP" in out, "baseline STOP gate present"
    assert f"`{base['head_full']}`" in out and "`feature/x`" in out, "backticked sha/branch"
    assert "142 passed" in out, "test tail surfaced"

    no_header = render({**base, "has_header": False})
    assert "## Required skill" in no_header, "name skill when header missing"
    assert GENERIC_REQUIRED_SKILL_TEXT in no_header, "generic fallback surfaced verbatim"

    family_text = SKILL_FAMILIES[0].fallback_text
    family_header = render({**base, "has_header": False, "required_skill_text": family_text})
    assert family_text in family_header, "family-specific fallback surfaced verbatim"

    with_specs = render({**base, "specs": ["docs/spec.md"]})
    assert "## Read these files first" in with_specs and "## Plan file" not in with_specs

    dirty = render({**base, "tree_clean": False, "dirty_count": 3})
    assert "3 uncommitted file(s)" in dirty, "dirty tree surfaced"

    red = render({**base, "test_passed": False})
    assert "FAILED" in red, "red baseline surfaced"

    minimal = render({**base, "test_cmd": None, "test_ran": False})
    assert "## Known friction" not in minimal and "## Other context" not in minimal, "drop empties"

    assert detect_skill_family(["docs/superpowers/plans/x.md"]) is SKILL_FAMILIES[0], (
        "path-based family detection"
    )
    assert detect_skill_family(["docs/plan.md"]) is None, "no family for an unrelated path"

    path = handoff_path("sess-123", "1e3f")
    assert path.name == "next-session-prompt-1e3f.md", "nonce in filename"
    assert path.parent.name == "sess-123", "session-namespaced subdir"
    assert path.parts[-3] == "tmp", "lives under .claude/tmp"

    print("selfcheck OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repo path (resolved to git toplevel)")
    parser.add_argument("--plan", help="plan file path (relative to repo root or absolute)")
    parser.add_argument(
        "--spec", action="append", default=[], help="companion design/spec/notes file (repeatable)"
    )
    parser.add_argument("--test-cmd", help="baseline test command, e.g. 'uv run pytest'")
    parser.add_argument(
        "--no-run", action="store_true", help="record the test command without running it"
    )
    parser.add_argument(
        "--pitfall",
        action="append",
        default=[],
        help="out-of-band friction not in the plan (repeatable)",
    )
    parser.add_argument(
        "--context",
        action="append",
        default=[],
        help="other context not in the plan or repo rules (repeatable)",
    )
    parser.add_argument("--selfcheck", action="store_true", help="run internal assertions and exit")
    args = parser.parse_args()

    if args.selfcheck:
        return selfcheck()
    if not args.plan:
        parser.error("--plan is required")

    ctx = capture_baseline(
        args.repo, args.plan, args.spec, args.test_cmd, args.no_run, args.pitfall, args.context
    )
    if not ctx["tree_clean"]:
        print(
            f"warning: working tree has {ctx['dirty_count']} uncommitted file(s); "
            "baseline is ambiguous until committed/stashed",
            file=sys.stderr,
        )
    if ctx["test_ran"] and not ctx["test_passed"]:
        print("warning: baseline tests FAILED — do not hand off a red baseline", file=sys.stderr)
    rendered = render(ctx)
    print(rendered)
    saved = write_handoff(rendered)
    print(f"saved handoff to {saved}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
