#!/usr/bin/env python3
"""Decide which plugin-creator flow path governs a change (SKILL.md Step 0).

The path decides which gates run, so it is derived from file paths rather than
judged. The one boundary this cannot decide - whether a large edit is a rewrite -
is left to the author with an explicit override, deliberately carrying no size
threshold. That is a deliberate design choice, not a citation of #140 — #140 governs the
SKILL.md body budget, not how a change is classified.

Every ambiguity resolves toward the expensive path: `mechanical` drops the design gate, the
implementation gate and the live invocation, so it is only ever returned about a diff that
exists and was read.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path, PurePosixPath

# Component surfaces. `hooks`, `commands`, `monitors`, `.mcp.json` and `.lsp.json` are the
# repo's own risky surfaces (ci/shared/review/risk.py SAFETY_GLOBS, and the risky_surface
# path_globs generate_quality_artifacts.py renders); `agents` and `SKILL.md` are added here
# because they are prompt text the agent executes. A change to any of these changes what the
# agent does, so it cannot take the cheap path.
AGENT_FACING_DIRS = frozenset({"agents", "hooks", "commands", "monitors"})
AGENT_FACING_NAMES = frozenset({"SKILL.md", ".mcp.json", ".lsp.json"})

# plugin.json fields that are bookkeeping. Every OTHER field declares a component, describes
# the plugin, or flips a runtime switch, so the set is a denylist: a field Claude Code adds
# to the manifest later routes to the expensive path until someone decides otherwise, rather
# than silently going cheap. (Checked against ci/shared/schemas/plugin.schema.json, whose
# `outputStyles` an allow-list draft of this set had already missed.)
MECHANICAL_MANIFEST_FIELDS = frozenset(
    {"$schema", "version", "author", "license", "repository", "homepage"}
)

PATHS = ("new", "behavior-change", "mechanical", "package")


def _is_agent_facing(path: str) -> bool:
    posix = PurePosixPath(path.strip())
    if posix.name in AGENT_FACING_NAMES:
        return True
    return bool(AGENT_FACING_DIRS.intersection(posix.parts))


def classify(
    changed_paths: list[str],
    *,
    plugin_exists: bool,
    manifest_fields_changed: frozenset[str] = frozenset(),
    intent: str | None = None,
) -> tuple[str, str]:
    """Return ``(path, reason)``. ``path`` is one of :data:`PATHS`.

    ``manifest_fields_changed`` is the set of top-level ``plugin.json`` keys whose value
    differs from the base. Passing it explicitly keeps this function pure and testable;
    the CLI computes it with git.

    Pure, but not caller-agnostic: ``changed_paths`` must come from :func:`_changed_paths`
    or an equivalent. It owns both halves of the collection contract — a rename arrives as
    BOTH sides (``--no-renames``), and an entry that is not a plain file arrives with a
    trailing slash. Raw ``git diff --name-only`` output satisfies neither and misroutes.
    """
    if not plugin_exists:
        return "new", "target plugin does not exist at the base ref (or is gone from the worktree)"
    # Intent is checked AFTER existence: a declared package intent must not mask a plugin
    # that has never been through the flow.
    if intent == "package":
        return "package", "declared intent: package or export an existing plugin"
    if not changed_paths and not manifest_fields_changed:
        # Step 0's first run happens before the edits exist. An empty diff is undetermined,
        # never cheap: the answer that binds is the one from the re-run on the real diff.
        return "behavior-change", "no diff yet — run this again once the change exists"
    behavioural = sorted(manifest_fields_changed - MECHANICAL_MANIFEST_FIELDS)
    if behavioural:
        return "behavior-change", f"plugin.json {', '.join(behavioural)} changed"
    for path in changed_paths:
        if path.endswith("/"):
            # `_changed_paths` marks every entry that is not a plain file. Not "an agent-facing
            # surface" — the contents are unreadable, which is a different thing and a
            # `references/` subtree hits it too.
            return "behavior-change", f"{path} is not a plain file — contents unknown"
        if _is_agent_facing(path):
            return "behavior-change", f"{path} is an agent-facing surface"
    # references/ lands here on purpose: routing every reference typo through two approval
    # gates would empty the cheap path and the flow would be routed around. The comprehension
    # readback runs on every path and is the compensating control. Do not "fix" this.
    return "mechanical", "no agent-facing surface in the diff"


def _git(args: list[str], repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True, check=True)


def _exists_at(rel: str, base_ref: str, repo_root: Path) -> bool:
    """True if ``rel`` is present in the tree at ``base_ref``."""
    return (
        subprocess.run(
            ["git", "cat-file", "-e", f"{base_ref}:{rel}"],
            cwd=repo_root,
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )


def _mark_non_file(path: str, plugin_root: Path) -> str:
    """Trailing-slash any entry that is not a plain file: its contents are unknown.

    Every producer has a shape it cannot enumerate — ``ls-files --others`` stops at a nested
    repository and emits the directory, a symlink to a directory arrives as a bare name, and
    a submodule is a gitlink in the diff. One type test covers all three; testing the
    spelling git happens to use caught only the first. An entry absent from the worktree is
    a deletion, and its name still routes it.
    """
    entry = plugin_root / path
    if entry.is_symlink() or (entry.exists() and not entry.is_file()):
        return path.rstrip("/") + "/"
    return path


def _changed_paths(rel: str, base_ref: str, repo_root: Path) -> list[str]:
    """Plugin-relative paths of everything git sees under ``rel``, tracked or not.

    Untracked files never appear in ``git diff``, so a brand-new ``hooks/`` script or a whole
    new skill would otherwise be invisible and take the cheap path. ``-z`` is load-bearing
    twice: it splits on NUL, and it makes git emit paths verbatim — the default quoting
    (``"skills/d\\303\\251mo/SKILL.md"``) hid every non-ASCII path from the surface check.
    """
    prefix = f"{rel}/"
    out = "".join(
        _git([*cmd, "-z", "--", rel], repo_root).stdout
        for cmd in (
            # --no-renames: rename detection reports only the destination, which hides a
            # `SKILL.md` -> `guide.md` (or `hooks/h.sh` -> `scripts/h.sh`) move entirely.
            ["diff", "--name-only", "--no-renames", base_ref],
            ["ls-files", "--others", "--exclude-standard"],
        )
    )
    plugin_root = repo_root / rel
    return sorted(
        {_mark_non_file(path.removeprefix(prefix), plugin_root) for path in out.split("\0") if path}
    )


def _manifest_fields_changed(plugin_dir: Path, base_ref: str, repo_root: Path) -> frozenset[str]:
    """Top-level plugin.json keys whose value differs from ``base_ref``.

    A manifest deleted from the worktree reports every key the base declared: dropping the
    manifest drops every component it declared, which is the opposite of a config tweak.
    """
    manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    rel = manifest.resolve().relative_to(repo_root.resolve()).as_posix()
    try:
        before = _git(["show", f"{base_ref}:{rel}"], repo_root).stdout
    except subprocess.CalledProcessError:
        return frozenset()  # not in the base tree; `plugin_exists` already routed that New
    old = json.loads(before)
    if not manifest.exists():
        return frozenset(old)
    new = json.loads(manifest.read_text(encoding="utf-8"))
    return frozenset(k for k in set(old) | set(new) if old.get(k) != new.get(k))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin-dir", required=True, type=Path)
    parser.add_argument("--base-ref", default="origin/main")
    parser.add_argument("--repo-root", default=Path.cwd(), type=Path)
    parser.add_argument("--intent", choices=["package"], default=None)
    args = parser.parse_args(argv)

    rel = args.plugin_dir.resolve().relative_to(args.repo_root.resolve()).as_posix()
    # "Exists" means exists at the base ref, not on disk. A plugin already scaffolded into
    # the working tree is still New: a disk-only check would let a second run of Step 0 route
    # a plugin that has never been reviewed to the cheap path.
    plugin_exists = args.plugin_dir.is_dir() and _exists_at(
        f"{rel}/.claude-plugin/plugin.json", args.base_ref, args.repo_root
    )
    changed = _changed_paths(rel, args.base_ref, args.repo_root) if plugin_exists else []

    path, reason = classify(
        changed,
        plugin_exists=plugin_exists,
        manifest_fields_changed=(
            _manifest_fields_changed(args.plugin_dir, args.base_ref, args.repo_root)
            if plugin_exists
            else frozenset()
        ),
        intent=args.intent,
    )
    print(json.dumps({"path": path, "reason": reason, "changed": changed}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
