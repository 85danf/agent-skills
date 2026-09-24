#!/usr/bin/env python3
"""Prepare and run lane-based Agent Skill review prompts."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from skill_review_coverage import Lane, load_criteria, render_matrix, resolve_active_lanes

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_ORCHESTRATION_CRITERIA_PATH = SKILL_DIR / "assets" / "skill-quality-criteria.json"


def _lane_prompt(
    skill: str,
    change_type: str,
    lane: Lane,
    diff_text: str,
    *,
    subagent_type: str = "",
) -> str:
    rows = [
        "| criterion_id | lane | status | evidence | reviewer |",
        "|---|---|---|---|---|",
    ]
    criteria_text: list[str] = []
    for criterion in lane.criteria:
        criteria_text.append(f"- `{criterion.id}`: {criterion.prompt}")
        rows.append(f"| {criterion.id} | {lane.id} | not-reviewed |  |  |")
    table = "\n".join(rows)
    criteria_block = "\n".join(criteria_text)
    return f"""# Skill Review Lane: {lane.name}

Review skill `{skill}` for change type `{change_type}`.

Recommended subagent: `{subagent_type}`

Fill only this lane's rows. Use status `pass`, `fail`, or `na`; include concrete
evidence and your reviewer name/handle for every reviewed row.

## Criteria

{criteria_block}

## Output Table

{table}

## Diff

```diff
{diff_text}
```
"""


def prepare_review(
    skill: str,
    change_type: str,
    diff_text: str,
    output_dir: Path,
    *,
    criteria_file: Path | str | None = None,
    repo_root: Path | str = ".",
) -> dict[str, Any]:
    criteria = resolve_active_lanes(
        repo_root,
        load_criteria(criteria_file or DEFAULT_ORCHESTRATION_CRITERIA_PATH),
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    lanes_dir = output_dir / "lanes"
    lanes_dir.mkdir(exist_ok=True)

    matrix_path = output_dir / "coverage-matrix.yml"
    matrix_path.write_text(
        render_matrix(
            skill,
            change_type,
            criteria=criteria,
            # Re-preparing over an existing matrix must not drop its authored sections.
            existing=matrix_path.read_text(encoding="utf-8") if matrix_path.is_file() else None,
        ),
        encoding="utf-8",
    )

    lanes: list[dict[str, str]] = []
    for lane in criteria.lanes:
        prompt_path = lanes_dir / f"{lane.id}.prompt.md"
        result_path = lanes_dir / f"{lane.id}.result.md"
        subagent_type = lane.review_agent["name"] if lane.review_agent else ""
        prompt_path.write_text(
            _lane_prompt(skill, change_type, lane, diff_text, subagent_type=subagent_type),
            encoding="utf-8",
        )
        entry: dict[str, str] = {
            "id": lane.id,
            "name": lane.name,
            "subagent_type": subagent_type,
            "prompt_path": str(prompt_path),
            "result_path": str(result_path),
        }
        # Propagate the blocking flag so callers know to halt other lanes if this one fails.
        raw_lane = next(
            (
                ld
                for ld in _raw_lanes(criteria_file or DEFAULT_ORCHESTRATION_CRITERIA_PATH)
                if ld["id"] == lane.id
            ),
            {},
        )
        if raw_lane.get("blocking"):
            entry["blocking"] = "true"
        lanes.append(entry)

    manifest: dict[str, Any] = {
        "skill": skill,
        "change_type": change_type,
        "matrix_path": str(matrix_path),
        "lanes": lanes,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def _raw_lanes(criteria_file: Path | str) -> list[dict[str, Any]]:
    """Return raw lane dicts from the criteria JSON, keeping non-schema fields like blocking."""
    data: dict[str, Any] = json.loads(Path(criteria_file).read_text(encoding="utf-8"))
    lanes: list[dict[str, Any]] = data.get("lanes", [])
    return lanes


def run_backend(
    command: str, lane: dict[str, str], *, timeout_seconds: int
) -> subprocess.CompletedProcess[str]:
    prompt_path = Path(lane["prompt_path"])
    result_path = Path(lane["result_path"])
    env = os.environ.copy()
    env.update(
        {
            "SKILL_REVIEW_LANE_ID": lane["id"],
            "SKILL_REVIEW_LANE_NAME": lane["name"],
            "SKILL_REVIEW_PROMPT_FILE": str(prompt_path),
            "SKILL_REVIEW_OUTPUT_FILE": str(result_path),
        }
    )
    result = subprocess.run(
        shlex.split(command),
        input=prompt_path.read_text(encoding="utf-8"),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout_seconds,
        check=False,
        env=env,
    )
    result_path.parent.mkdir(parents=True, exist_ok=True)
    if result.returncode == 0:
        result_path.write_text(result.stdout, encoding="utf-8")
    else:
        result_path.write_text(
            f"RETURN_CODE={result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}",
            encoding="utf-8",
        )
    return result


def _run_prepare(args: argparse.Namespace) -> None:
    diff_text = Path(args.diff).read_text(encoding="utf-8") if args.diff else sys.stdin.read()
    manifest = prepare_review(
        args.skill,
        args.change_type,
        diff_text,
        Path(args.output_dir),
        criteria_file=args.criteria_file,
        repo_root=args.repo_root,
    )
    print(json.dumps(manifest, indent=2))


def _run_backend(args: argparse.Namespace) -> None:
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    failed = 0
    blocking_failed = False
    for lane in manifest["lanes"]:
        is_blocking = lane.get("blocking") == "true"
        if blocking_failed and not is_blocking:
            print(f"[SKIP] {lane['id']} (blocked by a failing pre-screen lane)")
            continue
        result = run_backend(args.command_line, lane, timeout_seconds=args.timeout_seconds)
        if result.returncode != 0:
            failed += 1
            print(f"[FAIL] {lane['id']} returned {result.returncode}")
            if is_blocking:
                blocking_failed = True
                print(
                    f"[HALT] {lane['id']} is a blocking lane — "
                    "fix critical-fail conditions before running remaining lanes"
                )
        else:
            print(f"[PASS] {lane['id']}")
    if failed:
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare", help="Prepare matrix and lane prompt files")
    prepare.add_argument("--skill", required=True)
    prepare.add_argument("--change-type", required=True, choices=["new", "update", "review-only"])
    prepare.add_argument("--output-dir", required=True)
    prepare.add_argument("--diff", help="Diff file. Reads stdin when omitted.")
    prepare.add_argument("--criteria-file")
    prepare.add_argument("--repo-root", default=".", help="Repository root for lane profile")
    prepare.set_defaults(func=_run_prepare)

    run = sub.add_parser("run", help="Run a backend command once per lane")
    run.add_argument("--manifest", required=True)
    run.add_argument("--command-line", required=True)
    run.add_argument("--timeout-seconds", type=int, default=600)
    run.set_defaults(func=_run_backend)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
