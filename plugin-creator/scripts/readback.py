#!/usr/bin/env python3
"""Read a built plugin back (SKILL.md Step 6).

Two checks the flow cannot get from reading its own work:

* ``prompt`` assembles a comprehension prompt from the plugin directory and
  NOTHING else. That is enforced, not asked for: the builder refuses a directory
  with no ``.claude-plugin/plugin.json``, so pointing at the parent - where the
  design doc is a sibling of ``plugins/`` - fails loudly instead of embedding it.
* ``invoke`` runs a headless ``claude -p`` session with the plugin loaded and
  reports whether the skill actually fired. That is the only check in the flow
  that tests discoverability, which reading a description can never do.

The transcript shape ``fired`` parses was measured from a real run, not assumed:
an ``assistant`` event carries ``message.content[*]``, and a skill invocation is a
``tool_use`` block named ``"Skill"`` whose ``input.skill`` is ``"<plugin>:<skill>"``.
There is no top-level ``skill`` or ``content`` key. Captured transcripts for both
outcomes live in ``tests/plugin-creator/fixtures/readback/``; change this parser only
alongside a fixture that shows the new shape.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Sibling script in this same scripts/ dir; see FULL_TEXT_DIRS below for why it is imported
# rather than restated. Top-level (not deferred like init_skill.py's in-function import),
# so `scripts/` must be on sys.path: it is for direct CLI execution (the script's own dir is
# sys.path[0]) and for the suite (conftest.py inserts it).
from classify_change import AGENT_FACING_DIRS, AGENT_FACING_NAMES

QUESTIONS = (
    "What is this plugin for?",
    "When would you invoke it, and on what user phrasing?",
    "Walk through what you would do for the scenario below.",
    "What is explicitly out of scope for it?",
)

# Every text suffix a plugin can ship. The Node set matters because a suffix missing here is
# invisible TWICE over: the file is neither loaded nor LISTED, so the agent cannot even name a
# file to open for it - the one gap the listing does not make visible (issue #933). am-pm ships
# Python and/or TypeScript plus shell, so both language sets belong here.
TEXT_SUFFIXES = frozenset(
    {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".txt", ".ts", ".tsx", ".mts", ".cts"}
)

INVOCATION_TIMEOUT_SECONDS = 600


# What an invocation actually loads, in full. A real invocation does not receive the
# whole plugin either: it loads SKILL.md and opens references ON DEMAND, per progressive
# disclosure. Restating the whole plugin builds a prompt the agent never gets, and for
# three plugins it did not fit a 200k-token window at all.
#
# ONE definition of "agent-facing", imported from the sibling that already owns it, so
# Step 0 (classify_change) and Step 6 (this) cannot disagree. The sibling import is the
# established pattern in this scripts/ dir (init_skill.py does the same); it is not a
# runtime-self-containment violation, which is about importing `ci.*` from a shipped
# plugin, not about two scripts that ship in the same directory.
#
# `plugin.json` is readback-only: the manifest declares which components exist, which the
# change classifier does not need to know.
#
# Hook and monitor BODIES go in full, not as listings: a hook's body is what it does,
# and a hook is the part of a plugin that acts without being invoked - which makes it
# disproportionately load-bearing for "when would you invoke it" and "what is out of
# scope". One plugin ships 345,790 chars of hooks; a readback omitting them would report
# on the small part of that plugin that is not hooks.
FULL_TEXT_DIRS = AGENT_FACING_DIRS
FULL_TEXT_NAMES = AGENT_FACING_NAMES | {"plugin.json"}


def _first_heading(path: Path) -> str:
    """The file's first MEANINGFUL line - a heading, a module docstring, a title.

    This is the whole payload of a listed file, so it has to be worth the line: a path
    alone cannot answer "which file would you open here". Boilerplate first lines are
    skipped rather than printed. Taking the first non-empty line made 350 of the corpus's
    1,167 listed files (29%) read as `!/usr/bin/env python3`, `{`, or `---` - a listing
    entry that says nothing the path did not already say.
    """
    try:
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip().lstrip("#").removeprefix("//").strip().strip("\"'").strip()
            # Shebang, frontmatter fence, pure punctuation, or an import: carries nothing
            # the path did not. An import names a DEPENDENCY, not what the file is for, and
            # it is the first line of most Python and TypeScript source.
            if not line or line.startswith(("!", "import ", "from ")):
                continue
            if not any(c.isalnum() for c in line):
                continue
            return line[:120]
    except OSError:
        pass
    return ""


#: Dirs that hold documentation and fixtures, never live components. A component dir name
#: appearing UNDER one of these describes a component rather than being one.
LISTED_ONLY_DIRS = frozenset({"references", "assets", "docs"})


def _is_full_text(relative: Path) -> bool:
    """True when this path is a component an invocation loads, not documentation about one.

    The documentation guard is where this DELIBERATELY diverges from
    `classify_change._is_agent_facing`, which matches a component dir anywhere in the path.
    That is right for the classifier - matching too much only routes a change to the more
    expensive review path, which is safe. Here it is actively wrong: a live readback showed
    `references/components/hooks/{audiences,exit-codes,output-format,stdin-payload}.md`
    loading in FULL while their parent `references/components/hooks.md` was merely listed,
    so the agent could reason about hook payloads in detail but not about whether to reach
    for a hook at all. The SETS stay shared (imported above); only the location rule differs.
    """
    if LISTED_ONLY_DIRS.intersection(relative.parts):
        return False
    return relative.name in FULL_TEXT_NAMES or bool(FULL_TEXT_DIRS.intersection(relative.parts))


def build_prompt(plugin_dir: Path, scenario: str) -> str:
    """Assemble a spec-blind comprehension prompt from ``plugin_dir`` alone.

    The agent-facing surface goes in full; everything else is one line - its path and
    its first heading. That is what an invocation loads, so it is what a comprehension
    readback should be graded on. It also gives the readback a question it could not ask
    before: with references listed rather than pre-loaded, "which file would you open
    here" has a right answer, so a SKILL.md that fails to route the reader to the right
    reference is finally detectable (context.progressive-disclosure).
    """
    plugin_dir = plugin_dir.resolve()
    is_claude_plugin = (plugin_dir / ".claude-plugin" / "plugin.json").is_file()
    # A portable/Codex-only skill has no plugin manifest at all -- its root is a SKILL.md
    # directly. Accept either shape rather than requiring the Claude Code plugin manifest,
    # so Step 6a's readback runs on every path, on every host, per SKILL.md.
    is_portable_skill = (plugin_dir / "SKILL.md").is_file()
    if not is_claude_plugin and not is_portable_skill:
        raise RuntimeError(
            f"{plugin_dir} is neither a Claude Code plugin directory (no "
            ".claude-plugin/plugin.json) nor a portable skill directory (no SKILL.md); "
            "point --plugin-dir at the plugin or skill root, not its parent"
        )
    parts = [
        "You are reading an Agent Skill"
        + (" (a Claude Code plugin)" if is_claude_plugin else "")
        + " you have never seen. You have no design "
        "document, no conversation history, and no author to ask. Answer only from the "
        "files below.",
        "",
        "The files an invocation loads are given in full. Everything else is listed by "
        "path and heading only, exactly as it would reach you in a real session: you "
        "would open it on demand. If a question cannot be answered from what is here, "
        "say so and name the file you would open.",
        "",
    ]
    listed: list[str] = []
    for path in sorted(plugin_dir.rglob("*")):
        if path.is_symlink() or not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        relative = path.relative_to(plugin_dir)
        if _is_full_text(relative):
            parts.append(f"--- {relative.as_posix()} ---")
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
            parts.append("")
        else:
            heading = _first_heading(path)
            listed.append(f"- {relative.as_posix()}" + (f" - {heading}" if heading else ""))
    if listed:
        parts.append("--- files you can open on demand (not loaded) ---")
        parts.extend(listed)
        parts.append("")
    parts.append("Answer each question separately and concretely:")
    parts.extend(f"{index}. {question}" for index, question in enumerate(QUESTIONS, start=1))
    parts.append("")
    parts.append(f"Scenario for question 3: {scenario}")
    return "\n".join(parts)


def fired(transcript: str, skill_name: str) -> bool:
    """True when ``skill_name`` was actually invoked in a ``claude -p`` transcript.

    Keys off the structured ``tool_use`` block, never a substring of prose: an
    assistant turn routinely says "I'll use the <name> skill" in a text block
    without ever invoking it, and the committed positive fixture contains exactly
    that sentence.
    """
    for raw in transcript.splitlines():
        line = raw.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "assistant":
            continue
        for block in (event.get("message") or {}).get("content") or []:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use" or block.get("name") != "Skill":
                continue
            invoked = (block.get("input") or {}).get("skill", "")
            if invoked and (invoked == skill_name or invoked.rpartition(":")[2] == skill_name):
                return True
    return False


def run_invocation(
    plugin_dir: Path, user_prompt: str, skill_name: str, workdir: Path
) -> dict[str, object]:
    """Load ``plugin_dir`` into a headless session and report whether the skill fired.

    Uses the CLI's own ``--plugin-dir`` loader rather than copying files into a config
    directory. ``--allowedTools Skill`` auto-approves the ``Skill`` tool so a permission
    prompt cannot be mistaken for a skill that was never found; it does NOT restrict the
    tool set - a measured run used ``Bash`` and ``Monitor`` despite it. Point ``workdir``
    at a scratch directory: the session can run commands there.
    """
    if shutil.which("claude") is None:
        raise RuntimeError("the `claude` CLI is not on PATH; the live invocation cannot run")
    workdir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        [
            "claude",
            "-p",
            user_prompt,
            "--plugin-dir",
            str(plugin_dir.resolve()),
            "--output-format",
            "stream-json",
            "--verbose",
            "--allowedTools",
            "Skill",
        ],
        cwd=workdir,
        capture_output=True,
        text=True,
        # Windows defaults to the locale codepage, which raises on a transcript
        # carrying any non-ASCII byte; the same pin as skill_review_orchestrate.py.
        encoding="utf-8",
        errors="replace",
        timeout=INVOCATION_TIMEOUT_SECONDS,
        check=False,
    )
    return {
        "fired": fired(result.stdout, skill_name),
        "exit_code": result.returncode,
        "transcript": result.stdout,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    prompt_parser = sub.add_parser("prompt", help="Build the spec-blind comprehension prompt")
    prompt_parser.add_argument("--plugin-dir", required=True, type=Path)
    prompt_parser.add_argument("--scenario", required=True)
    prompt_parser.add_argument("--out", type=Path)

    invoke_parser = sub.add_parser("invoke", help="Run the live firing test")
    invoke_parser.add_argument("--plugin-dir", required=True, type=Path)
    invoke_parser.add_argument("--prompt", required=True)
    invoke_parser.add_argument("--skill-name", required=True)
    invoke_parser.add_argument("--workdir", required=True, type=Path)

    args = parser.parse_args(argv)

    if args.command == "prompt":
        text = build_prompt(args.plugin_dir, args.scenario)
        if args.out:
            args.out.write_text(text, encoding="utf-8")
            print(f"wrote {args.out} ({len(text):,} chars)")
        else:
            print(text)
        return 0

    outcome = run_invocation(args.plugin_dir, args.prompt, args.skill_name, args.workdir)
    print(json.dumps({k: v for k, v in outcome.items() if k != "transcript"}, indent=2))
    if outcome["exit_code"] != 0:
        raise RuntimeError(
            f"the claude session failed (exit {outcome['exit_code']}); this is not a firing result"
        )
    return 0 if outcome["fired"] else 1


if __name__ == "__main__":
    sys.exit(main())
