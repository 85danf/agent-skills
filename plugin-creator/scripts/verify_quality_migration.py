#!/usr/bin/env python3
"""Compare a pre-migration skill backup with the migrated skill."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

Fact = tuple[str, str, str]


def _normalize(text: str) -> str:
    return " ".join(text.strip().split())


def extract_markdown_facts(root: Path) -> list[Fact]:
    facts: list[Fact] = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root).as_posix()
        in_code_block = False
        current_kind: str | None = None
        current_parts: list[str] = []

        def flush_current(relative: str = relative) -> None:
            nonlocal current_kind, current_parts
            if current_kind and current_parts:
                text = _normalize(" ".join(current_parts))
                if text:
                    facts.append((relative, current_kind, text))
            current_kind = None
            current_parts = []

        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line.startswith("```"):
                flush_current()
                in_code_block = not in_code_block
                continue
            if in_code_block or not line or line.startswith("|"):
                flush_current()
                continue
            if line.startswith("#"):
                flush_current()
                text = _normalize(line.lstrip("#").strip())
                if text:
                    facts.append((relative, "heading", text))
            elif line.startswith("- "):
                flush_current()
                current_kind = "bullet"
                current_parts = [line[2:]]
            else:
                if current_kind is None:
                    current_kind = "paragraph"
                    current_parts = [line]
                else:
                    current_parts.append(line)
        flush_current()
    return facts


def _by_text(facts: list[Fact]) -> dict[str, list[Fact]]:
    grouped: dict[str, list[Fact]] = defaultdict(list)
    for fact in facts:
        grouped[fact[2]].append(fact)
    return dict(grouped)


def compare_facts(old_root: Path, new_root: Path) -> dict[str, list[dict[str, Any]]]:
    old_by_text = _by_text(extract_markdown_facts(old_root))
    new_by_text = _by_text(extract_markdown_facts(new_root))
    report: dict[str, list[dict[str, Any]]] = {
        "unchanged": [],
        "moved": [],
        "missing": [],
        "new": [],
    }

    for text, old_facts in old_by_text.items():
        new_facts = new_by_text.get(text, [])
        old_locations = sorted({fact[0] for fact in old_facts})
        new_locations = sorted({fact[0] for fact in new_facts})
        row = {"text": text, "old_locations": old_locations, "new_locations": new_locations}
        if not new_facts:
            report["missing"].append(row)
        elif old_locations == new_locations:
            report["unchanged"].append(row)
        else:
            report["moved"].append(row)

    for text, new_facts in new_by_text.items():
        if text not in old_by_text:
            report["new"].append(
                {
                    "text": text,
                    "old_locations": [],
                    "new_locations": sorted({fact[0] for fact in new_facts}),
                }
            )

    return report


def render_report(report: dict[str, list[dict[str, Any]]]) -> str:
    lines = [
        "# Plugin Creator Quality Migration Map",
        "",
        "Compare the pre-migration skill backup with the migrated skill.",
        "Every `missing` row requires either a deliberate-removal note or a follow-up fix.",
        "",
    ]
    for section in ["missing", "moved", "unchanged", "new"]:
        lines.extend([f"## {section.title()}", ""])
        rows = report[section]
        if not rows:
            lines.extend(["No rows.", ""])
            continue
        lines.extend(
            [
                "| detail | old location | new location | disposition |",
                "|---|---|---|---|",
            ]
        )
        lines.extend(
            "| "
            + row["text"].replace("|", "\\|")
            + " | "
            + ", ".join(row["old_locations"])
            + " | "
            + ", ".join(row["new_locations"])
            + " | review |"
            for row in rows
        )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-root", type=Path, required=True)
    parser.add_argument("--new-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    report = compare_facts(args.old_root, args.new_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_report(report), encoding="utf-8")


if __name__ == "__main__":
    main()
