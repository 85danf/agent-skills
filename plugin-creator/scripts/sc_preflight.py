#!/usr/bin/env python3
"""Pre-flight checks for plugin-creator skill.

Verifies Python version, PyYAML and `claude` CLI dependencies, and expected scripts.
Run this before first use. Exits 0 if all checks pass, 1 if any fail.

Usage:
    python3 sc_preflight.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

_PASS = "[PASS]"
_FAIL = "[FAIL]"
_WARN = "[WARN]"

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent


def _check_python() -> bool:
    """Check Python version >= 3.10."""
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 10:
        print(f"{_PASS} Python {major}.{minor}")
        return True
    print(f"{_FAIL} Python {major}.{minor} — requires 3.10+")
    return False


def _check_pyyaml() -> bool:
    """Check that PyYAML is importable."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import yaml; print(yaml.__version__)"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"{_PASS} PyYAML — {version}")
            return True
        print(f"{_FAIL} PyYAML — not installed")
        print("  Hint: pip install PyYAML==6.0.3")
        return False
    except subprocess.TimeoutExpired:
        print(f"{_WARN} PyYAML — import check timed out")
        return True
    except Exception as e:
        print(f"{_FAIL} PyYAML — {e}")
        return False


def _check_claude_cli() -> bool:
    """Check the `claude` CLI, which `readback.py invoke` (SKILL.md Step 6b) shells out to.

    WARN rather than FAIL: every other step works without it, so a missing CLI must not
    report the whole skill unusable — but a silent absence made `Step 6b` fail at dispatch
    time instead of here.
    """
    path = shutil.which("claude")
    if path:
        print(f"{_PASS} claude CLI — {path}")
    else:
        print(f"{_WARN} claude CLI — not on PATH; Step 6b's live invocation cannot run")
    return True


def _check_scripts() -> bool:
    """Check that expected scripts exist."""
    expected = [
        "init_skill.py",
        "quick_validate.py",
        "generate_openai_yaml.py",
        "skill_review_coverage.py",
        "skill_review_orchestrate.py",
        "generate_quality_artifacts.py",
        "verify_quality_migration.py",
        "classify_change.py",
        "readback.py",
        "monorepo_placement.py",
    ]
    missing = [s for s in expected if not (SCRIPT_DIR / s).exists()]
    if missing:
        print(f"{_FAIL} Skill scripts — missing: {', '.join(missing)}")
        return False
    print(f"{_PASS} Skill scripts — all {len(expected)} scripts present")
    return True


def _check_references() -> bool:
    """Check that key reference docs exist."""
    refs_dir = SKILL_DIR / "references"
    expected = [
        "SKILL_SPEC.md",
        "PROMPT_ENGINEERING.md",
        "SKILL_TEMPLATE.md",
        "PLAN_TEMPLATE.md",
        "SKILL_QUALITY_CRITERIA.md",
    ]
    if not refs_dir.is_dir():
        print(f"{_FAIL} References — references/ directory not found")
        return False

    missing = [r for r in expected if not (refs_dir / r).exists()]
    if missing:
        print(f"{_FAIL} References — missing: {', '.join(missing)}")
        return False
    criteria_dir = refs_dir / "criteria"
    expected_criteria = [
        "context.md",
        "genericity.md",
        "component-fit.md",
        "installed-use.md",
        "runtime.md",
        "repo.md",
        "risk.md",
        "review.md",
    ]
    missing_criteria = [
        f"criteria/{name}" for name in expected_criteria if not (criteria_dir / name).exists()
    ]
    if missing_criteria:
        print(f"{_FAIL} References — missing: {', '.join(missing_criteria)}")
        return False
    print(
        f"{_PASS} References — all {len(expected)} reference docs and "
        f"{len(expected_criteria)} criteria docs present"
    )
    return True


def _check_assets() -> bool:
    """Check that key assets exist."""
    assets_dir = SKILL_DIR / "assets"
    expected = [
        "review-coverage-criteria.json",
        "skill-quality-criteria.json",
        "review-agent-template.md",
    ]
    if not assets_dir.is_dir():
        print(f"{_FAIL} Assets — assets/ directory not found")
        return False

    missing = [asset for asset in expected if not (assets_dir / asset).exists()]
    if missing:
        print(f"{_FAIL} Assets — missing: {', '.join(missing)}")
        return False
    print(f"{_PASS} Assets — all {len(expected)} assets present")
    return True


def _check_agents() -> bool:
    """Check plugin-level agent prompts when this skill is installed in a Claude Code plugin.

    The Claude Code plugin layout is <plugin>/skills/<name>/scripts/<this file>, so
    ``agents/`` sits two levels above SKILL_DIR only under that layout. A portable/Codex-only
    install (this skill's own directory) has no plugin root at all -- checking
    SKILL_DIR.parent.name guards against reporting on an unrelated ``agents/`` two levels up.
    """
    expected = [
        "skill-review-context-engineer.md",
        "skill-review-genericity.md",
        "skill-review-component-fit.md",
        "skill-review-installed-use.md",
        "skill-review-runtime-contracts.md",
        "skill-review-repo-integration.md",
        "skill-review-risk.md",
        "skill-review-process.md",
    ]
    if SKILL_DIR.parent.name != "skills":
        print(f"{_WARN} Agents — standalone skill install; review lanes are in references/lanes/")
        return True
    agents_dir = SKILL_DIR.parents[1] / "agents"
    if not agents_dir.is_dir():
        print(f"{_WARN} Agents — plugin agents/ directory not found; standalone skill install")
        return True

    missing = [agent for agent in expected if not (agents_dir / agent).exists()]
    if missing:
        print(f"{_FAIL} Agents — missing: {', '.join(missing)}")
        return False
    print(f"{_PASS} Agents — all {len(expected)} agents present")
    return True


def _check_quality_artifacts_fresh() -> bool:
    """Check that generated quality artifacts are fresh."""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "generate_quality_artifacts.py"), "--check"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
        )
    except subprocess.TimeoutExpired:
        print(f"{_FAIL} Quality artifacts — freshness check timed out")
        return False
    except Exception as e:
        print(f"{_FAIL} Quality artifacts — {e}")
        return False

    if result.returncode == 0:
        print(f"{_PASS} Quality artifacts — fresh")
        return True
    print(f"{_FAIL} Quality artifacts — generated files are stale")
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    return False


def main() -> None:
    print("Plugin Creator — Pre-flight Checks")
    print("=" * 36)
    print()

    results = []

    # 1. Python version
    results.append(_check_python())

    # 2. PyYAML dependency
    results.append(_check_pyyaml())

    # 3. claude CLI (Step 6b)
    results.append(_check_claude_cli())

    # 4. Scripts
    results.append(_check_scripts())

    # 4. Reference docs
    results.append(_check_references())

    # 5. Assets
    results.append(_check_assets())

    # 6. Agent prompts
    results.append(_check_agents())

    # 7. Generated quality artifacts
    results.append(_check_quality_artifacts_fresh())

    # Summary
    passed = sum(results)
    total = len(results)
    print()
    print("=" * 36)
    if all(results):
        print(f"All {total} checks passed. Ready to use.")
        sys.exit(0)
    else:
        failed = total - passed
        print(f"{passed}/{total} passed, {failed} failed. Fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
