#!/usr/bin/env python3
"""Generate plugin-creator quality criteria artifacts from one JSON source."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
# Claude Code plugin layout is <plugin>/skills/<name>/scripts/<this file> -- PLUGIN_DIR is two
# levels up only when that layout is actually present. A portable/Codex-only install (this
# skill's own directory, e.g. <repo>/plugin-creator/scripts/<this file>) has no plugin root at
# all, so PLUGIN_DIR is None there and the agents/skill-review-*.md targets below are skipped
# instead of writing outside the skill directory.
PLUGIN_DIR = SKILL_DIR.parents[1] if SKILL_DIR.parent.name == "skills" else None
DEFAULT_SOURCE = SKILL_DIR / "assets" / "skill-quality-criteria.json"
DEFAULT_TEMPLATE = SKILL_DIR / "assets" / "review-agent-template.md"
ROUTING_START = "<!-- skill-creator-lane-routing:start -->"
ROUTING_END = "<!-- skill-creator-lane-routing:end -->"


def replace_bounded_section(content: str, marker: str, new_section: str) -> str:
    """Replace content between bounded markers in a file.

    Markers are HTML comments: <!-- skill-creator-{marker}:start/end -->.
    """
    start = f"<!-- skill-creator-{marker}:start -->"
    end = f"<!-- skill-creator-{marker}:end -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = f"{start}\n{new_section}\n{end}"
    if pattern.search(content):
        return pattern.sub(replacement, content)
    raise ValueError(f"Bounded section markers for '{marker}' not found")


def _load(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return data


def render_skill_md_lane_routing(source: Path = DEFAULT_SOURCE) -> str:
    return "\n".join(
        [
            "Resolve the active lane set for the current repo before opening criteria:",
            "",
            "```bash",
            "python3 <skill_dir>/scripts/skill_review_coverage.py active-lanes "
            "--repo-root . --format references",
            "```",
            "",
            "Open only the lane reference files printed by that command. If no "
            "repo policy is configured, the resolver uses the generic plugin "
            "profile.",
        ]
    )


def render_quality_checklist_lane_routing(source: Path = DEFAULT_SOURCE) -> str:
    return "\n".join(
        [
            "Resolve the active checklist lanes for the current repo:",
            "",
            "```bash",
            "python3 <skill_dir>/scripts/skill_review_coverage.py active-lanes "
            "--repo-root . --format checklist",
            "```",
            "",
            "Open only the lane reference files printed by that command.",
        ]
    )


def render_plan_template_lane_rows(source: Path = DEFAULT_SOURCE) -> str:
    return "\n".join(
        [
            "| Active lanes | Run the resolver for this repo before filling lane "
            "rows. | `python3 <skill_dir>/scripts/skill_review_coverage.py "
            "active-lanes --repo-root . --format plan-table` |",
            "| Returned rows only | Copy only rows printed by the resolver into "
            "this table. | Completed plan decisions for the active lane set. |",
        ]
    )


def _replace_marked_section(text: str, replacement: str, *, path: Path) -> str:
    start_count = text.count(ROUTING_START)
    end_count = text.count(ROUTING_END)
    if start_count != 1 or end_count != 1:
        msg = f"{path} must contain exactly one lane-routing section"
        raise ValueError(msg)
    before, rest = text.split(ROUTING_START, 1)
    _old, after = rest.split(ROUTING_END, 1)
    return f"{before}{ROUTING_START}\n{replacement}\n{ROUTING_END}{after}"


def _render_marked_file(path: Path, replacement: str) -> str:
    return _replace_marked_section(path.read_text(encoding="utf-8"), replacement, path=path)


def render_review_coverage_criteria_text(source: Path = DEFAULT_SOURCE) -> str:
    data = _load(source)
    present = {lane["id"] for lane in data["lanes"]}
    canonical_order = [
        "pre_screen",
        "context",
        "genericity",
        "component-fit",
        "installed-use",
        "runtime",
        "repo",
        "risk",
        "review",
    ]
    generic_plugin = [lane_id for lane_id in canonical_order if lane_id in present]
    rendered = {
        "version": 2,
        "profiles": {
            "generic-plugin": generic_plugin,
            "domain-child": [lane_id for lane_id in generic_plugin if lane_id != "genericity"],
        },
        "mandatory_lanes": ["pre_screen", "risk"],
        "risk_rules": {
            "path_globs": [
                {
                    # Capability surfaces: component-fit + risk, no MCP attestation.
                    # `.mcp.json` is split into its own rule below so a hooks-only
                    # (or commands-/monitors-/lsp-only) change cannot demand an MCP
                    # security approval from a plugin that ships no MCP server (#610).
                    "globs": ["hooks/**", ".lsp.json", "monitors/**", "commands/**"],
                    "require_lanes": ["component-fit", "risk"],
                    "risky_surface": True,
                },
                {
                    "globs": [".mcp.json"],
                    "require_lanes": ["component-fit", "risk"],
                    "risky_surface": True,
                    "require_mcp_security": True,
                },
                {
                    # Plugin-root code AND skill-nested code (skills/<skill>/scripts|lib/…),
                    # which is where a skill's runtime code actually lives.
                    "globs": ["scripts/**", "lib/**", "skills/*/scripts/**", "skills/*/lib/**"],
                    "require_lanes": ["runtime", "repo", "risk"],
                },
            ],
            "frontmatter_lanes": ["context", "genericity"],
            "size_requires_all_discretionary": True,
        },
        "lanes": [
            {
                "id": lane["id"],
                "name": lane["name"],
                "criteria": [
                    {
                        "id": criterion["id"],
                        "title": criterion["title"],
                        "prompt": criterion["review_prompt"],
                    }
                    for criterion in lane["criteria"]
                ],
            }
            for lane in data["lanes"]
        ],
    }
    # ensure_ascii=True (the json.dumps default) matches the hand-authored source
    # JSON's own escaping style and the repo's pretty-format-json pre-commit hook
    # (.pre-commit-config.yaml has no --no-ensure-ascii) — ensure_ascii=False here
    # produced literal Unicode that hook would silently rewrite on the next commit
    # that touches this file, permanently reopening the round-trip check.
    return json.dumps(rendered, indent=2) + "\n"


def render_quality_reference_text(source: Path = DEFAULT_SOURCE) -> str:
    data = _load(source)
    lines = [
        "# Skill Quality Criteria",
        "",
        "Generated from `assets/skill-quality-criteria.json`. Do not edit by hand.",
        "",
        (
            "The lanes are used in both phases: use author guidance while creating or "
            "refactoring a skill, then use review prompts while filling the review "
            "coverage matrix."
        ),
        "",
        (
            "The agent must explicitly open and read the relevant generated lane "
            "reference files before applying lane guidance; lane content is not "
            "automatically populated into agent context. The JSON is the source for "
            "generating this index, the lane references, and review prompts."
        ),
        "",
    ]
    for lane in data["lanes"]:
        lines.extend(
            [
                f"## {lane['name']}",
                "",
                f"Authoring: {lane['author_summary']}",
                "",
                f"Review: {lane['review_summary']}",
                "",
            ]
        )
        _append_examples(lines, lane.get("examples", []), heading="### Examples")
        for criterion in lane["criteria"]:
            lines.extend(
                [
                    f"### `{criterion['id']}` - {criterion['title']}",
                    "",
                    f"Author guidance: {criterion['author_guidance']}",
                    "",
                    f"Review prompt: {criterion['review_prompt']}",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


def render_lane_reference_texts(source: Path = DEFAULT_SOURCE) -> dict[Path, str]:
    data = _load(source)
    rendered: dict[Path, str] = {}
    for lane in data["lanes"]:
        lines = [
            f"# {lane['name']} Criteria",
            "",
            "Generated from `../../assets/skill-quality-criteria.json`. Do not edit by hand.",
            "",
            lane["author_summary"],
            "",
        ]
        _append_examples(lines, lane.get("examples", []), heading="## Examples")
        for criterion in lane["criteria"]:
            lines.extend(
                [
                    f"## `{criterion['id']}` - {criterion['title']}",
                    "",
                    criterion["author_guidance"],
                    "",
                ]
            )
        rendered[Path(f"{lane['id']}.md")] = "\n".join(lines).rstrip() + "\n"
    return rendered


def _append_examples(
    lines: list[str],
    examples: list[dict[str, str]],
    *,
    heading: str,
) -> None:
    if not examples:
        return
    lines.extend([heading, ""])
    for example in examples:
        lines.extend(
            [
                f"- Good: {example['good']}",
                f"- Bad: {example['bad']}",
                "",
            ]
        )


def _agent_tools(tools: list[str]) -> str:
    return "[" + ", ".join(tools) + "]"


def _criteria_markdown(lane: dict[str, Any]) -> str:
    parts: list[str] = []
    for criterion in lane["criteria"]:
        parts.extend(
            [
                f"- `{criterion['id']}` - {criterion['title']}",
                f"  - Review: {criterion['review_prompt']}",
            ]
        )
    return "\n".join(parts)


def render_review_agents(
    source: Path = DEFAULT_SOURCE,
    template_path: Path | None = None,
) -> dict[Path, str]:
    data = _load(source)
    template = (template_path or DEFAULT_TEMPLATE).read_text(encoding="utf-8")
    rendered: dict[Path, str] = {}
    for lane in data["lanes"]:
        agent = lane["review_agent"]
        content = template.format(
            agent_name=agent["name"],
            agent_description=agent["description"],
            agent_tools=_agent_tools(agent.get("tools", ["Read", "Grep"])),
            lane_name=lane["name"],
            agent_focus=agent["focus"],
            criteria_markdown=_criteria_markdown(lane),
        )
        rendered[Path("agents") / f"{agent['name']}.md"] = content
    return rendered


def _target_artifacts(source: Path = DEFAULT_SOURCE) -> dict[Path, str]:
    targets = {
        SKILL_DIR
        / "assets"
        / "review-coverage-criteria.json": render_review_coverage_criteria_text(source),
        SKILL_DIR / "references" / "SKILL_QUALITY_CRITERIA.md": render_quality_reference_text(
            source
        ),
        SKILL_DIR / "SKILL.md": _render_marked_file(
            SKILL_DIR / "SKILL.md",
            render_skill_md_lane_routing(source),
        ),
        SKILL_DIR / "references" / "QUALITY_CHECKLIST.md": _render_marked_file(
            SKILL_DIR / "references" / "QUALITY_CHECKLIST.md",
            render_quality_checklist_lane_routing(source),
        ),
        SKILL_DIR / "references" / "PLAN_TEMPLATE.md": _render_marked_file(
            SKILL_DIR / "references" / "PLAN_TEMPLATE.md",
            render_plan_template_lane_rows(source),
        ),
    }
    for relative_path, content in render_lane_reference_texts(source).items():
        targets[SKILL_DIR / "references" / "criteria" / relative_path] = content
    # Claude Code plugin-specific: agents/skill-review-*.md live at the plugin root, one level
    # above skills/<name>/. A portable/Codex-only install has no plugin root, so PLUGIN_DIR is
    # None and these targets are skipped -- references/lanes/*.md is the portable equivalent and
    # is maintained by hand, not generated.
    if PLUGIN_DIR is not None:
        for relative_path, content in render_review_agents(source).items():
            targets[PLUGIN_DIR / relative_path] = content
    return targets


def _remove_stale_generated_files(targets: dict[Path, str]) -> None:
    target_paths = {path.resolve() for path in targets}
    pattern_roots = [(SKILL_DIR / "references" / "criteria", "*.md")]
    if PLUGIN_DIR is not None:
        pattern_roots.append((PLUGIN_DIR / "agents", "skill-review-*.md"))
    for pattern_root, pattern in pattern_roots:
        if not pattern_root.exists():
            continue
        for path in pattern_root.glob(pattern):
            if path.resolve() not in target_paths:
                path.unlink()


def write_artifacts(source: Path = DEFAULT_SOURCE, *, check: bool = False) -> list[str]:
    targets = _target_artifacts(source)
    stale: list[str] = []
    for path, content in targets.items():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    if not check:
        _remove_stale_generated_files(targets)
    return stale


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    stale = write_artifacts(args.source, check=args.check)
    if stale:
        for path in stale:
            print(f"[STALE] {path}")
        raise SystemExit(1)
    print(
        "[PASS] quality artifacts are fresh" if args.check else "[OK] generated quality artifacts"
    )


if __name__ == "__main__":
    main()
