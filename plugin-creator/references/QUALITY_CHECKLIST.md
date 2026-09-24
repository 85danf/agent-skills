# Skill Quality Checklist

Use this file as the procedural entry point for skill quality checks. The
criteria themselves are generated from `assets/skill-quality-criteria.json`; do
not duplicate or edit criteria text here.

The lanes are used in both phases: apply the lane author guidance during skill
creation or refactoring, then apply the same lane's review prompts during
review coverage. Treat them as inputs to authoring decisions and as checks
before completion.

The agent must explicitly open and read the relevant generated lane reference
files before applying lane guidance; lane content is not automatically populated into agent context.
The JSON remains the canonical source for the generator, while agents use the
generated references during authoring.

## Creation-Time Routing

Open only the lanes needed for the file you are writing:

<!-- skill-creator-lane-routing:start -->
Resolve the active checklist lanes for the current repo:

```bash
python3 <skill_dir>/scripts/skill_review_coverage.py active-lanes --repo-root . --format checklist
```

Open only the lane reference files printed by that command.
<!-- skill-creator-lane-routing:end -->

Use `references/SKILL_QUALITY_CRITERIA.md` only as an index when you need to
see every lane together.

## Review-Time Routing

For shared-repo skill changes, complete the committed review coverage matrix.
The exact command sequence — generate, prepare lane prompts, merge lanes, check —
lives in [REVIEW_COVERAGE.md](REVIEW_COVERAGE.md). Read it there; do not restate it here. <!-- citation -->
It carries the secret-scrubbing rule that applies before any diff leaves
the approved local environment.

## Maintenance Rule

To change quality standards, edit `assets/skill-quality-criteria.json`, then
run:

```bash
python3 <skill_dir>/scripts/generate_quality_artifacts.py
```

Commit the source JSON and generated artifacts together.
