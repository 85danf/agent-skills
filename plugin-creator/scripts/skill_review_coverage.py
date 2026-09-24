#!/usr/bin/env python3
"""Generate, merge, and validate Agent Skill review coverage matrices."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DEFAULT_CRITERIA_PATH = SKILL_DIR / "assets" / "review-coverage-criteria.json"
DEFAULT_QUALITY_CRITERIA_PATH = SKILL_DIR / "assets" / "skill-quality-criteria.json"
REPO_CHECKS_FILE = ".repo-checks.json"
DEFAULT_PROFILE = "generic-plugin"
ALLOWED_STATUSES = {"not-reviewed", "pass", "fail", "na"}
EVAL_EVIDENCE_STATUSES = {
    "not-applicable",
    "skipped",
    "manual-smoke-only",
    "automated-run",
    "record-lost",
}
EVAL_EVIDENCE_REQUIRED_FIELDS = {
    "not-applicable": {"reason"},
    # `record-lost` says an eval WAS run and its artifacts did not survive. The reason is
    # what keeps it from being a quiet exemption, so it is the one required field.
    "record-lost": {"reason"},
    "skipped": {"reason", "token_time_cost", "high_value_gating", "manual_smoke_test"},
    "manual-smoke-only": {"reason", "manual_smoke_test"},
    "automated-run": {
        "eval_plan_approved_by",
        "judges",
        "script_gates",
        "manual_smoke_test",
        "eval_count",
        "pass_rate",
        "quality_result",
        "trigger_result",
        "regression_result",
        "comparison_result",
        "failed_cases",
        "token_time_cost",
        "benchmark_report",
        "metrics_artifact",
    },
}
EVAL_EVIDENCE_ARTIFACT_FIELDS = {"benchmark_report", "metrics_artifact"}
EVAL_EVIDENCE_ARTIFACT_ROOT = ("reviews", "evals")
MCP_APPROVAL_CRITERION = "component-fit.mcp-approval"
# The lane-result contract: a sub-agent still writes its lane back as this markdown table.
# Only the committed matrix is YAML; `merge-lanes` reads these rows and folds them into it.
TABLE_HEADER = "| criterion_id | lane | status | evidence | reviewer |"
TABLE_SEPARATOR = "|---|---|---|---|---|"
CRITERION_COLUMNS = 5
EVIDENCE_COLUMN = 3
# Every standard eval field, in the order a fresh matrix records them.
EVAL_SKELETON: dict[str, str] = {
    "status": "skipped",
    "reason": "",
    "token_time_cost": "",
    "high_value_gating": "",
    "manual_smoke_test": "",
    "eval_plan_approved_by": "",
    "judges": "",
    "script_gates": "",
    "eval_count": "",
    "pass_rate": "",
    "quality_result": "",
    "trigger_result": "",
    "regression_result": "",
    "comparison_result": "",
    "failed_cases": "",
    "benchmark_report": "",
    "metrics_artifact": "",
}


@dataclass(frozen=True)
class Criterion:
    id: str
    title: str
    prompt: str


@dataclass(frozen=True)
class Lane:
    id: str
    name: str
    criteria: list[Criterion]
    review_agent: dict[str, Any] | None = None
    routing: dict[str, Any] | None = None


@dataclass(frozen=True)
class CriteriaSet:
    lanes: list[Lane]

    @property
    def criteria(self) -> list[Criterion]:
        return [criterion for lane in self.lanes for criterion in lane.criteria]

    @property
    def lane_by_criterion(self) -> dict[str, Lane]:
        return {criterion.id: lane for lane in self.lanes for criterion in lane.criteria}


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    errors: list[str]


def _lane_subagent_instruction(criterion_id: str, lane_id: str) -> str:
    lane_label = lane_id or "<missing>"
    return (
        f"{criterion_id}: not-reviewed is not allowed when complete review is required. "
        f"Run the lane sub-agent review for lane `{lane_label}` first: use "
        "`skill_review_orchestrate.py prepare`, dispatch that lane's manifest "
        "`subagent_type` with the lane prompt, merge the lane result, then set "
        "the row to pass/fail/na with concrete evidence and reviewer. "
        "Do not only mark this row complete."
    )


def _missing_criteria_instruction(missing: list[str], criteria: CriteriaSet) -> str:
    lanes = {
        criteria.lane_by_criterion[criterion_id].id
        for criterion_id in missing
        if criterion_id in criteria.lane_by_criterion
    }
    lane_text = ", ".join(f"`{lane}`" for lane in sorted(lanes)) or "<unknown>"
    return (
        f"missing criteria: {', '.join(missing)}. Regenerate the matrix and run "
        f"the lane sub-agent review for missing lane(s) {lane_text}: use "
        "`skill_review_orchestrate.py prepare`, dispatch each manifest "
        "`subagent_type` with its lane prompt, merge the lane results, then "
        "commit completed rows with concrete evidence and reviewer."
    )


def _criterion_prompt(data: dict[str, Any]) -> str:
    return str(data.get("prompt") or data.get("review_prompt") or "")


def load_criteria(path: Path | str = DEFAULT_CRITERIA_PATH) -> CriteriaSet:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    lanes: list[Lane] = []
    seen: set[str] = set()
    for lane_data in data.get("lanes", []):
        criteria: list[Criterion] = []
        for criterion_data in lane_data.get("criteria", []):
            criterion_id = str(criterion_data["id"])
            if criterion_id in seen:
                raise ValueError(f"duplicate criterion id: {criterion_id}")
            seen.add(criterion_id)
            criteria.append(
                Criterion(
                    id=criterion_id,
                    title=str(criterion_data["title"]),
                    prompt=_criterion_prompt(criterion_data),
                )
            )
        lanes.append(
            Lane(
                id=str(lane_data["id"]),
                name=str(lane_data["name"]),
                criteria=criteria,
                review_agent=lane_data.get("review_agent"),
                routing=lane_data.get("routing"),
            )
        )
    if not lanes:
        raise ValueError("criteria file must define at least one lane")
    return CriteriaSet(lanes=lanes)


def _load_repo_checks(repo_root: Path | str) -> dict[str, Any]:
    path = Path(repo_root) / REPO_CHECKS_FILE
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        msg = f"{path} must contain a JSON object"
        raise ValueError(msg)
    return data


def _load_profiles(path: Path | str | None = None) -> dict[str, list[str]]:
    """Read the ordered profile -> lane-id lists from the criteria asset."""
    profiles = json.loads(Path(path or DEFAULT_CRITERIA_PATH).read_text(encoding="utf-8")).get(
        "profiles"
    )
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError(f"{path} must define a non-empty 'profiles' object")
    return {str(name): [str(lane_id) for lane_id in lanes] for name, lanes in profiles.items()}


def _profile_lane_ids(config: dict[str, Any]) -> list[str]:
    profiles = _load_profiles()
    profile = str(config.get("skill_creator_lane_profile", DEFAULT_PROFILE))
    return profiles.get(profile, profiles[DEFAULT_PROFILE])


def active_skill_creator_lane_ids(config: dict[str, Any]) -> set[str]:
    return set(_profile_lane_ids(config))


def filter_criteria_for_profile(criteria: CriteriaSet, config: dict[str, Any]) -> CriteriaSet:
    lanes_by_id = {lane.id: lane for lane in criteria.lanes}
    return CriteriaSet(
        lanes=[
            lanes_by_id[lane_id] for lane_id in _profile_lane_ids(config) if lane_id in lanes_by_id
        ]
    )


def resolve_active_lanes(
    repo_root: Path | str = ".",
    criteria: CriteriaSet | None = None,
) -> CriteriaSet:
    return filter_criteria_for_profile(criteria or load_criteria(), _load_repo_checks(repo_root))


def coverage_matrix_path(plugin_dir: Path | str) -> Path:
    """Living review-coverage matrix for a plugin.

    Given the plugin dir ``groups/<g>/<d>/<lifecycle>/plugins/<plugin>``, the matrix is the
    ``reviews/<plugin>/coverage.yml`` sibling of the plugin's lifecycle dir — a single living
    file re-affirmed on every change, not a dated file per change.
    """
    plugin_dir = Path(plugin_dir)
    return plugin_dir.parents[1] / "reviews" / plugin_dir.name / "coverage.yml"


def render_active_lanes(repo_root: Path | str = ".", *, fmt: str = "references") -> str:
    criteria = resolve_active_lanes(repo_root, load_criteria(DEFAULT_QUALITY_CRITERIA_PATH))
    lines: list[str] = []
    for lane in criteria.lanes:
        routing = lane.routing or {}
        if fmt == "references":
            lines.append(f"{lane.id} references/criteria/{lane.id}.md")
        elif fmt == "checklist":
            lines.append(f"- `references/criteria/{lane.id}.md` {routing.get('checklist', '')}")
        elif fmt == "plan-table":
            lines.append(
                "| {name} | {decision} | {evidence} |".format(
                    name=f"{lane.id}: {routing.get('plan_label', lane.name)}",
                    decision=routing.get("plan_decision", ""),
                    evidence=routing.get("plan_evidence", ""),
                )
            )
        else:
            msg = f"unknown active lane format: {fmt}"
            raise ValueError(msg)
    return "\n".join(lines) + "\n"


def _dump(document: dict[str, Any]) -> str:
    # `width` must stay huge or PyYAML line-wraps the prose evidence cells.
    text: str = yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=10**6)
    return text


def load_matrix(text: str) -> dict[str, Any]:
    """Parse a ``coverage.yml`` body, raising a readable error for anything else."""
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        msg = f"coverage.yml is not valid YAML: {exc}"
        raise ValueError(msg) from exc
    if not isinstance(document, dict):
        msg = "coverage.yml must be a mapping"
        raise ValueError(msg)
    return document


def _preserved(existing: str | None) -> dict[str, Any]:
    """The authored parts of an existing matrix that a regeneration must not clobber.

    ``render_matrix`` owns only the criterion rows; the provenance stamp and the eval
    block are authored (or stamped once) and survive, the way the markdown format's
    trailing sections used to.
    """
    if not (existing or "").strip():
        return {}
    try:
        return load_matrix(existing or "")
    except ValueError:
        # An unreadable predecessor is not a licence to invent provenance. That applies to
        # ALL FOUR provenance fields, not just created_with: defaulting review_status to
        # "recorded" here would assert that a review is on file, silently upgrading a
        # `record-lost` predecessor (and discarding its required note) into a bare positive
        # claim that `_leaf_badges` would then publish as a badge. `none` asserts nothing,
        # which is the only honest thing to say about a file we could not read.
        return {
            "created_with": "unknown",
            "updated_with": "unknown",
            "review_status": "none",
            "review_note": None,
        }


def render_matrix(
    skill: str,
    change_type: str,
    *,
    criteria: CriteriaSet | None = None,
    existing: str | None = None,
) -> str:
    """Render the living coverage matrix for ``skill`` as ``coverage.yml`` text.

    Two independent provenance facts, and only ``updated_with`` is loose.

    ``created_with`` is stamped ``plugin-creator`` only when this generates a matrix that
    did not exist for a ``new`` plugin -- a legacy plugin's first ``update`` /
    ``review-only`` matrix gets ``unknown``, since the tool did not create that plugin.
    The workflow's ``begin`` command uses these same creation/update rules at entry,
    without claiming a completed review. The scaffolder alone is not a reliable witness
    that plugin-creator ran. An existing file keeps whatever claim it already carries --
    a regeneration never upgrades `manual` or `unknown`.

    An earlier revision of this change DID upgrade a prior ``unknown`` at
    ``--change-type new``. It was removed in review: ``--change-type`` is a flag an
    operator types, not something this function can measure -- it has no base ref -- so
    the upgrade trusted a claim rather than a fact. Two ways that bit. Re-running the
    documented command on an existing plugin wrote a claim CI then rejected as back-dated,
    reddening every group; and a beta->stable promotion (``classify_change`` returns
    ``new``, ``move-plugin`` carries the ``reviews/`` sidecar, and the gate's deliberate
    ``--no-renames`` reads the moved manifest as added) would have written a FALSE
    ``plugin-creator`` and been waved through. Nothing here may reintroduce it without a
    real base-ref measurement.

    ``updated_with`` is monotone with NO back-dating rule: every ``update`` run stamps it,
    and a stamp already on file survives. It is unaffected by the above -- it asserts that
    the generator ran on an update, which needs no base ref, and it has no ``manual``
    member, so it can never overwrite a contrary claim. ``review-only`` does not stamp it
    -- the tool ran on the review, not on the plugin, and the ``reviewed`` badge already
    says that. Two badges must not assert one fact.
    """
    criteria = criteria or load_criteria()
    prior = _preserved(existing)
    document: dict[str, Any] = {
        "created_with": prior.get(
            "created_with", "plugin-creator" if not prior and change_type == "new" else "unknown"
        ),
        "updated_with": (
            "plugin-creator"
            if prior.get("updated_with") == "plugin-creator" or change_type == "update"
            else "unknown"
        ),
        "review_status": prior.get("review_status", "recorded"),
        "review_note": prior.get("review_note"),
        # `--change-type` is a REQUIRED CLI argument; discarding its value made the flag a
        # no-op and dropped a field 65 of the 66 markdown matrices carried.
        "change_type": change_type,
        "criteria": [
            {
                "id": criterion.id,
                "lane": lane.id,
                "status": "not-reviewed",
                "evidence": "",
                "reviewer": "",
            }
            for lane in criteria.lanes
            for criterion in lane.criteria
        ],
        "eval": prior.get("eval") or dict(EVAL_SKELETON),
    }
    return _dump(document)


def _split_table_line(line: str, *, columns: int | None = None) -> list[str]:
    """Split a markdown table row into stripped cells.

    A raw ``|`` in the free-text evidence cell over-splits the row. When ``columns``
    is given, the surplus cells are coalesced back into evidence — keeping
    id/lane/status first and reviewer last — so the reviewer's row is recovered
    instead of being silently dropped as malformed. Mirrors ``ci/shared/review/matrix.py``.
    """
    cells = line.strip().strip("|").split("|")
    if columns is not None and len(cells) > columns:
        end = EVIDENCE_COLUMN + len(cells) - columns + 1
        cells[EVIDENCE_COLUMN:end] = ["|".join(cells[EVIDENCE_COLUMN:end])]
    return [cell.strip() for cell in cells]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(set(cell) <= {"-", ":"} for cell in cells)


def _parse_rows(markdown: str) -> list[dict[str, str]]:
    """Read ``| criterion_id | lane | status | evidence | reviewer |`` rows.

    Only lane RESULTS are markdown now; the committed matrix is YAML.
    """
    rows: list[dict[str, str]] = []
    headers: list[str] | None = None
    for line in markdown.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = _split_table_line(line, columns=len(headers) if headers else None)
        if _is_separator(cells):
            continue
        if cells[:5] == ["criterion_id", "lane", "status", "evidence", "reviewer"]:
            headers = cells
            continue
        if headers is None or len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells, strict=True)))
    return rows


def _eval_fields(document: dict[str, Any]) -> dict[str, str] | None:
    """The eval block, flattened — standard fields plus everything under ``notes``.

    Mirrors the loader in ``ci/shared/review/coverage_yaml.py`` so the two views of a
    matrix agree on what an eval field is.
    """
    block = document.get("eval")
    if not isinstance(block, dict):
        return None
    fields = {
        key: ("" if value is None else str(value)) for key, value in block.items() if key != "notes"
    }
    notes = block.get("notes") or {}
    if isinstance(notes, dict):
        fields.update({key: str(value) for key, value in notes.items()})
    return fields


def _artifact_path_from_value(value: str) -> str:
    match = re.fullmatch(r"\[[^\]]+\]\(([^)]+)\)", value.strip())
    return match.group(1).strip() if match else value.strip()


def _validate_eval_artifact(root: Path, field: str, value: str) -> list[str]:
    artifact_value = _artifact_path_from_value(value)
    artifact_path = Path(artifact_value)
    if artifact_path.is_absolute() or ".." in artifact_path.parts:
        return [f"Eval Evidence {field} must be a relative repository path: {artifact_value}"]
    if artifact_path.parts[:2] != EVAL_EVIDENCE_ARTIFACT_ROOT:
        return [f"Eval Evidence {field} must live under reviews/evals/: {artifact_value}"]
    if not (root / artifact_path).is_file():
        return [f"Eval Evidence linked artifact does not exist: {artifact_value}"]
    return []


def _validate_eval_evidence(document: dict[str, Any], *, root: Path) -> list[str]:
    fields = _eval_fields(document)
    if fields is None:
        return ["Eval Evidence section is missing"]

    status = fields.get("status", "")
    if not status:
        return ["Eval Evidence missing status"]
    if status not in EVAL_EVIDENCE_STATUSES:
        allowed = ", ".join(sorted(EVAL_EVIDENCE_STATUSES))
        return [f"Eval Evidence unknown status {status}; expected one of: {allowed}"]

    errors = [
        f"Eval Evidence {status} missing {field}"
        for field in sorted(EVAL_EVIDENCE_REQUIRED_FIELDS[status])
        if not fields.get(field, "").strip()
    ]

    if status == "automated-run":
        for field in sorted(EVAL_EVIDENCE_ARTIFACT_FIELDS):
            value = fields.get(field, "").strip()
            if value:
                errors.extend(_validate_eval_artifact(root, field, value))
    return errors


def _validate_mcp_approval(rows: list[dict[str, str]], *, required: bool) -> list[str]:
    """The MCP attestation is the ``component-fit.mcp-approval`` row, not a prose section.

    The schema is closed (``additionalProperties: false``), so the old
    ``## MCP Security Approval`` table has no home in ``coverage.yml``; the attestation
    lives in that criterion's own evidence cell, which ``_validate_row`` already requires
    to be non-empty. This is the same rule the CI gate enforces
    (``ci/pr/skill_review_coverage.py``), so the two no longer disagree.
    """
    if not required:
        return []
    status = next(
        (row["status"] for row in rows if row["criterion_id"] == MCP_APPROVAL_CRITERION), None
    )
    if status != "pass":
        return [
            f"{MCP_APPROVAL_CRITERION} must be pass with the attestation as its evidence "
            f"when an MCP surface (.mcp.json) changed; found {status or '<missing>'}"
        ]
    return []


def _validate_row(
    row: dict[str, str],
    *,
    require_complete: bool,
    expected_ids: set[str] | None,
) -> list[str]:
    criterion_id = row["criterion_id"]
    status = row["status"]
    errors: list[str] = []
    if status not in ALLOWED_STATUSES:
        return [f"{criterion_id}: unknown status {status}"]
    if require_complete and status == "not-reviewed":
        errors.append(_lane_subagent_instruction(criterion_id, row.get("lane", "")))
    if status in {"pass", "fail", "na"} and not row["evidence"].strip():
        errors.append(f"{criterion_id}: missing evidence for status {status}")
    if status in {"pass", "fail", "na"} and not row["reviewer"].strip():
        errors.append(f"{criterion_id}: missing reviewer for status {status}")
    if expected_ids is not None and criterion_id not in expected_ids:
        errors.append(f"unknown criterion: {criterion_id}")
    return errors


def _criterion_rows(document: dict[str, Any]) -> list[dict[str, str]]:
    """The YAML criteria list in the shape the row validators already speak."""
    criteria = document.get("criteria")
    if not isinstance(criteria, list):
        return []
    return [
        {
            "criterion_id": str(row.get("id", "")),
            "lane": str(row.get("lane", "")),
            "status": str(row.get("status", "")),
            "evidence": str(row.get("evidence") or ""),
            "reviewer": str(row.get("reviewer") or ""),
        }
        for row in criteria
        if isinstance(row, dict)
    ]


def validate_matrix(
    text: str,
    *,
    require_complete: bool,
    mcp_required: bool = False,
    root: Path | str = ".",
    criteria: CriteriaSet | None = None,
) -> ValidationResult:
    try:
        document = load_matrix(text)
    except ValueError as exc:
        return ValidationResult(ok=False, errors=[str(exc)])

    errors: list[str] = []
    rows = _criterion_rows(document)
    if not rows:
        errors.append("criteria list is missing or empty")

    expected_ids: set[str] | None = None
    if criteria is not None:
        expected_ids = {criterion.id for criterion in criteria.criteria}

    seen: set[str] = set()
    for row in rows:
        criterion_id = row["criterion_id"]
        if criterion_id in seen:
            errors.append(f"duplicate criterion: {criterion_id}")
        seen.add(criterion_id)
        errors.extend(
            _validate_row(row, require_complete=require_complete, expected_ids=expected_ids)
        )

    if expected_ids is not None:
        missing = sorted(expected_ids - seen)
        if missing:
            if criteria is None:
                errors.append(f"missing criteria: {', '.join(missing)}")
            else:
                errors.append(_missing_criteria_instruction(missing, criteria))

    if require_complete:
        errors.extend(_validate_eval_evidence(document, root=Path(root)))
    errors.extend(_validate_mcp_approval(rows, required=mcp_required))

    return ValidationResult(ok=not errors, errors=errors)


def merge_lane_results(base_matrix: str, lane_outputs: list[str]) -> str:
    """Fold each lane's markdown result table into the YAML matrix.

    Only rows the base already declares are updated: a lane may not introduce a criterion
    the matrix does not carry. Everything else in the document — the provenance stamp, the
    eval block — is passed through untouched.
    """
    updates: dict[str, dict[str, str]] = {}
    for output in lane_outputs:
        for row in _parse_rows(output):
            if row["status"] in ALLOWED_STATUSES:
                updates[row["criterion_id"]] = row

    document = load_matrix(base_matrix)
    for row in document.get("criteria") or []:
        update = updates.get(str(row.get("id", "")))
        if update is None:
            continue
        row["lane"] = update["lane"]
        row["status"] = update["status"]
        row["evidence"] = update["evidence"]
        row["reviewer"] = update["reviewer"]
    return _dump(document)


def _write_or_print(text: str, output: str | None) -> None:
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8", newline="\n")
        return
    print(text, end="")


def _load_begin_matrix(text: str) -> dict[str, Any]:
    """Reject lossy YAML before workflow entry can rewrite historical evidence."""
    loader = yaml.SafeLoader(text)
    try:
        node = loader.get_single_node()
        pending: list[object] = [node]
        visited: set[int] = set()
        while pending:
            current = pending.pop()
            if id(current) in visited:
                continue
            visited.add(id(current))
            if isinstance(current, yaml.MappingNode):
                keys: set[str] = set()
                for key_node, value_node in current.value:
                    key = str(key_node.value)
                    if key in keys:
                        raise ValueError(f"coverage.yml repeats the key {key!r}")
                    keys.add(key)
                    pending.append(value_node)
            elif isinstance(current, yaml.SequenceNode):
                pending.extend(current.value)
        document = None if node is None else loader.construct_document(node)
    except yaml.YAMLError as exc:
        raise ValueError(f"coverage.yml is not valid YAML: {exc}") from exc
    finally:
        loader.dispose()
    if not isinstance(document, dict):
        raise ValueError("coverage.yml must be a mapping")
    rows = document.get("criteria")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("coverage.yml criteria must be a list of mappings")
    # Empty record-lost skeletons are legitimate history, not an incomplete review to fix.
    if rows:
        result = validate_matrix(text, require_complete=False)
        if not result.ok:
            raise ValueError("; ".join(result.errors))
    return document


def _run_begin(args: argparse.Namespace) -> None:
    """Record workflow entry without regenerating or claiming review results."""
    output = Path(args.output)
    try:
        if output.exists():
            document = _load_begin_matrix(output.read_text(encoding="utf-8"))
            # A historical document is never evidence that this tool created the plugin.
            document.setdefault("created_with", "unknown")
            document.setdefault("updated_with", "unknown")
            document.setdefault("review_status", "none")
            document.setdefault("review_note", None)
            document["change_type"] = args.change_type
            if args.change_type == "update":
                document["updated_with"] = "plugin-creator"
        else:
            legacy = output.with_suffix(".md")
            if legacy.exists():
                raise ValueError(f"legacy predecessor {legacy} must be migrated first")
            criteria = resolve_active_lanes(args.repo_root, load_criteria())
            document = load_matrix(render_matrix(args.skill, args.change_type, criteria=criteria))
            document["review_status"] = "none"
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Refusing to begin coverage at {output}: {exc}") from exc
    _write_or_print(_dump(document), args.output)


def _run_generate(args: argparse.Namespace) -> None:
    criteria = resolve_active_lanes(args.repo_root, load_criteria())
    output = Path(args.output) if args.output else None
    matrix = render_matrix(
        args.skill,
        args.change_type,
        criteria=criteria,
        existing=output.read_text(encoding="utf-8") if output and output.is_file() else None,
    )
    _write_or_print(matrix, args.output)


def _run_check(args: argparse.Namespace) -> None:
    text = Path(args.input).read_text(encoding="utf-8")
    result = validate_matrix(
        text,
        require_complete=args.require_complete,
        mcp_required=args.mcp_required,
        root=args.repo_root,
        criteria=resolve_active_lanes(args.repo_root, load_criteria()),
    )
    if result.ok:
        print("[PASS] skill review coverage matrix is valid")
        return
    for error in result.errors:
        print(f"[FAIL] {error}")
    sys.exit(1)


def _run_merge_lanes(args: argparse.Namespace) -> None:
    base = Path(args.matrix).read_text(encoding="utf-8")
    outputs = [
        path.read_text(encoding="utf-8")
        for path in sorted(Path(args.results_dir).glob("*.md"))
        if path.resolve() != Path(args.matrix).resolve()
    ]
    merged = merge_lane_results(base, outputs)
    _write_or_print(merged, args.output)


def _run_active_lanes(args: argparse.Namespace) -> None:
    print(render_active_lanes(args.repo_root, fmt=args.format), end="")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    begin = sub.add_parser("begin", help="Record workflow provenance, preserving existing reviews")
    begin.add_argument("--skill", required=True)
    begin.add_argument("--change-type", required=True, choices=["new", "update", "review-only"])
    begin.add_argument("--repo-root", default=".", help="Repository root for lane profile")
    begin.add_argument("-o", "--output", required=True)
    begin.set_defaults(func=_run_begin)

    generate = sub.add_parser("generate", help="Generate an empty review coverage matrix")
    generate.add_argument("--skill", required=True)
    generate.add_argument("--change-type", required=True, choices=["new", "update", "review-only"])
    generate.add_argument("--repo-root", default=".", help="Repository root for lane profile")
    generate.add_argument("-o", "--output")
    generate.set_defaults(func=_run_generate)

    check = sub.add_parser("check", help="Validate a review coverage matrix")
    check.add_argument("--input", required=True)
    check.add_argument("--require-complete", action="store_true")
    check.add_argument("--mcp-required", action="store_true")
    check.add_argument("--repo-root", default=".", help="Repository root for eval artifact links")
    check.set_defaults(func=_run_check)

    merge = sub.add_parser("merge-lanes", help="Merge lane result files into a matrix")
    merge.add_argument("--matrix", required=True)
    merge.add_argument("--results-dir", required=True)
    merge.add_argument("-o", "--output")
    merge.set_defaults(func=_run_merge_lanes)

    active = sub.add_parser("active-lanes", help="Print active plugin-creator lanes")
    active.add_argument("--repo-root", default=".", help="Repository root for lane profile")
    active.add_argument(
        "--format",
        choices=["references", "checklist", "plan-table"],
        default="references",
    )
    active.set_defaults(func=_run_active_lanes)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
