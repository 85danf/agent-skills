#!/usr/bin/env python3
"""am-pm monorepo detection + ``where-does-it-fit`` placement bridge.

plugin-creator is a portable skill: used standalone it asks the user where to
install a new skill (global / workspace / shared) and scaffolds there. But when
it runs INSIDE the am-pm plugin monorepo, a new plugin must land in the right
taxonomy slot — ``groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/`` — instead of a
default spot. This module gives plugin-creator the deterministic pieces it needs
to make that placement conditional, and is a no-op (reports ``in_monorepo:
false``) outside the monorepo so the standalone flow stays unchanged.

Responsibilities, each independently unit-testable:

* :func:`find_monorepo_root` / :func:`is_am_pm_monorepo` — DETECT the monorepo
  robustly, with no hardcoded absolute path, by walking up from a start directory
  for the unambiguous marker triple: a ``groups/`` taxonomy dir, a ``ci/`` dir,
  and a ``pyproject.toml`` whose ``[project].name`` is ``am-pm``.
* :func:`advise_placement` — BRIDGE to the repo-local ``where-does-it-fit`` skill
  by shelling out to its ``placement.py --group --intent --json``. The domain
  ranking stays owned by that skill and is never reimplemented here; the
  ``runner`` seam is injected in tests so the bridge needs no live skill.
* :func:`plugin_dir` / :func:`scaffold_skills_dir` — COMPUTE the on-disk target
  from a chosen group/domain/lifecycle/plugin, ready to hand to
  ``init_skill.py --path``.

The CLI ties them together: it always reports ``in_monorepo`` (+ ``root``), adds
a ``suggestion`` when given ``--group``/``--intent`` inside the monorepo, and adds
a ``scaffold_path`` when given full ``--group``/``--domain``/``--lifecycle``/
``--plugin`` coordinates. Outside the monorepo it reports ``in_monorepo: false``
and consults nothing.
"""

from __future__ import annotations

import argparse
import json
import subprocess  # noqa: S404 - only ever invokes the trusted repo-local placement.py
import sys
import tomllib
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol

# Lifecycle tiers a plugin can live under, per the taxonomy layout
# groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/.
LIFECYCLES: tuple[str, ...] = ("stable", "beta", "alpha", "internal")

# Repo-relative location of the where-does-it-fit skill's placement adviser. It
# lives in .claude/skills/ (repo-local tooling), NOT as an importable package, so
# we shell out to it rather than importing it.
PLACEMENT_REL_PATH = Path(
    ".claude/skills/where-does-it-fit/skills/where-does-it-fit/scripts/placement.py"
)


class PlacementError(RuntimeError):
    """Raised when the where-does-it-fit placement adviser cannot be consulted."""


class _CompletedProcess(Protocol):
    """The subset of ``subprocess.CompletedProcess`` :func:`advise_placement` reads."""

    returncode: int
    stdout: str
    stderr: str


class _Runner(Protocol):
    """The ``subprocess.run`` shape :func:`advise_placement` shells out through.

    Declared as a Protocol so tests inject a tiny fake without monkeypatching and
    the injected ``runner`` stays precisely typed (no bare ``Any``).
    """

    def __call__(
        self,
        args: Sequence[str],
        *,
        capture_output: bool,
        text: bool,
        check: bool,
    ) -> _CompletedProcess: ...


def _pyproject_is_am_pm(pyproject: Path) -> bool:
    """True when ``pyproject`` declares ``[project].name == "am-pm"``.

    Parses TOML rather than substring-matching ``name = "am-pm"`` so an unrelated
    ``name`` elsewhere in the file (an author, an optional-dependency group) never
    produces a false positive.
    """
    try:
        with pyproject.open("rb") as handle:
            data = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return False
    project = data.get("project")
    return isinstance(project, dict) and project.get("name") == "am-pm"


def find_monorepo_root(start: Path | None = None) -> Path | None:
    """Walk up from ``start`` (default cwd) to the am-pm monorepo root, or ``None``.

    Returns the nearest ancestor carrying ALL of: a ``groups/`` directory, a
    ``ci/`` directory, and a ``pyproject.toml`` whose project name is ``am-pm``.
    The triple marker makes a false match against an unrelated repo effectively
    impossible, and nothing is hardcoded to an absolute path, so a clone anywhere
    is detected. ``None`` means plugin-creator is running standalone.
    """
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (
            (candidate / "groups").is_dir()
            and (candidate / "ci").is_dir()
            and _pyproject_is_am_pm(candidate / "pyproject.toml")
        ):
            return candidate
    return None


def is_am_pm_monorepo(start: Path | None = None) -> bool:
    """Convenience boolean wrapper over :func:`find_monorepo_root`."""
    return find_monorepo_root(start) is not None


def placement_script(root: Path) -> Path | None:
    """Return the where-does-it-fit ``placement.py`` under ``root`` if present."""
    candidate = root / PLACEMENT_REL_PATH
    return candidate if candidate.is_file() else None


def advise_placement(
    root: Path,
    group: str,
    intent: str,
    *,
    runner: _Runner = subprocess.run,
) -> dict[str, Any]:
    """Consult where-does-it-fit for the best-fit domain in ``group``.

    Shells out to that skill's ``placement.py --group --intent --json`` and
    returns the parsed suggestion (``group_exists``, ``recommend_new_domain``,
    ``best_domain``, ranked ``matches`` …). The ranking contract is owned by
    where-does-it-fit and is never duplicated here. ``runner`` is injected in tests
    so the bridge does not depend on the live skill. Raises :class:`PlacementError`
    if the skill is missing, exits non-zero, or emits non-JSON.
    """
    script = placement_script(root)
    if script is None:
        raise PlacementError(
            f"where-does-it-fit placement adviser not found at {root / PLACEMENT_REL_PATH}"
        )
    completed = runner(
        [sys.executable, str(script), "--group", group, "--intent", intent, "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise PlacementError(
            f"placement adviser failed (exit {completed.returncode}): "
            f"{(completed.stderr or '').strip()}"
        )
    try:
        data = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise PlacementError(f"placement adviser output is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise PlacementError("placement adviser output is not a JSON object")
    return data


def plugin_dir(root: Path, group: str, domain: str, lifecycle: str, plugin: str) -> Path:
    """Compute ``groups/<group>/<domain>/<lifecycle>/plugins/<plugin>`` under ``root``."""
    if lifecycle not in LIFECYCLES:
        raise ValueError(f"lifecycle must be one of {LIFECYCLES}, got {lifecycle!r}")
    return root / "groups" / group / domain / lifecycle / "plugins" / plugin


def scaffold_skills_dir(root: Path, group: str, domain: str, lifecycle: str, plugin: str) -> Path:
    """The ``skills/`` dir to pass as ``init_skill.py --path``.

    The skill itself lands in ``<plugin>/skills/<name>/``, so the scaffolder's
    ``--path`` is the plugin's ``skills/`` directory.
    """
    return plugin_dir(root, group, domain, lifecycle, plugin) / "skills"


def build_result(
    *,
    start: Path | None,
    group: str | None,
    intent: str | None,
    domain: str | None,
    lifecycle: str | None,
    plugin: str | None,
    runner: _Runner = subprocess.run,
) -> dict[str, Any]:
    """Assemble the CLI/agent result for the given inputs (pure given ``runner``).

    Always carries ``in_monorepo`` and (inside the monorepo) ``root`` +
    ``placement_available``. When ``group`` + ``intent`` are supplied it adds a
    ``suggestion`` from where-does-it-fit; when full ``group``/``domain``/
    ``lifecycle``/``plugin`` coordinates are supplied it adds ``scaffold_path``.
    Outside the monorepo it returns ``{"in_monorepo": False}`` and consults
    nothing — this is the standalone path that keeps plugin-creator's behavior
    unchanged.
    """
    root = find_monorepo_root(start)
    if root is None:
        return {"in_monorepo": False}

    result: dict[str, Any] = {
        "in_monorepo": True,
        "root": str(root),
        "placement_available": placement_script(root) is not None,
    }
    if group and intent:
        result["suggestion"] = advise_placement(root, group, intent, runner=runner)
    if group and domain and lifecycle and plugin:
        result["scaffold_path"] = str(scaffold_skills_dir(root, group, domain, lifecycle, plugin))
    return result


def _render_human(result: dict[str, Any]) -> str:
    """Render :func:`build_result` output as readable lines for the agent."""
    if not result.get("in_monorepo"):
        return (
            "Not inside the am-pm monorepo — plugin-creator uses its standard "
            "install-location flow (global / workspace / shared)."
        )
    lines = [f"Inside the am-pm monorepo (root: {result['root']})."]
    if not result.get("placement_available"):
        lines.append(
            "where-does-it-fit adviser not found; choose the group/domain manually "
            "from `am-pm taxonomy`."
        )
    suggestion = result.get("suggestion")
    if isinstance(suggestion, dict):
        if not suggestion.get("group_exists"):
            lines.append(
                f"Group '{suggestion.get('group')}' does not exist yet "
                "-> scaffold-group first, then scaffold-domain."
            )
        elif suggestion.get("recommend_new_domain"):
            lines.append("No existing domain is a confident fit -> scaffold a NEW domain.")
        else:
            lines.append(f"Suggested domain: '{suggestion.get('best_domain')}'.")
    scaffold = result.get("scaffold_path")
    if scaffold:
        lines.append(f"Scaffold path (init_skill.py --path): {scaffold}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="monorepo_placement",
        description=(
            "Detect the am-pm monorepo and, inside it, bridge to where-does-it-fit "
            "to place a new plugin in the right group/domain/lifecycle."
        ),
    )
    parser.add_argument("--start", help="Directory to detect from (default: cwd).")
    parser.add_argument("--group", help="Taxonomy group the new plugin belongs to.")
    parser.add_argument("--intent", help="One-line description of what the new skill/plugin does.")
    parser.add_argument(
        "--domain",
        help="Target domain (with --group/--lifecycle/--plugin yields scaffold_path).",
    )
    parser.add_argument("--lifecycle", choices=LIFECYCLES, help="Target lifecycle tier.")
    parser.add_argument("--plugin", help="New plugin (folder) name.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    start = Path(args.start) if args.start else None
    try:
        result = build_result(
            start=start,
            group=args.group,
            intent=args.intent,
            domain=args.domain,
            lifecycle=args.lifecycle,
            plugin=args.plugin,
        )
    except PlacementError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result))
    else:
        print(_render_human(result))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
