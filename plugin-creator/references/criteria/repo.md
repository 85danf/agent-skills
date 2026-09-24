# Repository Integration Criteria

Generated from `../../assets/skill-quality-criteria.json`. Do not edit by hand.

Use this lane while updating repo-facing docs, changelog fragments, review evidence, validators, and CI expectations.

## Examples

- Good: When a skill adds a config field or workflow, update catalog docs, design docs, CONFIG references, tests, and the linked review coverage artifact.
- Bad: Change the skill interface while README examples, design docs, validators, and review evidence still describe the old behavior.

- Good: When a new requirement applies broadly, update the shared validator, schema, docs, and regression tests.
- Bad: Add a one-off repo-check exemption for a skill because the shared validator does not yet understand the new requirement.

## `repo.catalogs-and-docs` - Catalogs and docs are aligned

Update README.md, SKILLS.md, AGENTS.md, design docs, CONFIG.md, and repo-facing examples when the skill change makes them stale.

## `repo.changelog-and-pr` - A changelog fragment exists only when the host repo's gate owes one

Never decide on your own judgement that a PR owes a release note. After committing, run the host repo's changelog gate (am-pm: `am-pm changelog-gate --base-ref <merge-target>`) and do exactly what it prints: it says a fragment is owed, and what it must answer, or prints nothing. A plugin under `groups/` owes none unless the gate asks.

## `repo.validation-alignment` - Validation stays aligned

Update shared validators, pre-commit, tests, and CI expectations for new requirements instead of adding skill-specific exceptions when a shared rule is appropriate.
