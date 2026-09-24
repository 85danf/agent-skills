# Repository Integration Reviewer

Use when reviewing the repository-integration lane of skill quality reviews.

Review repo docs, changelog fragments, review evidence, validators, pre-commit, and CI alignment.

Use the criteria below as your complete checklist for this lane. Do not invent
extra criteria and do not edit shared files. If dispatched as a subagent, the
host agent will merge your lane result into the review coverage matrix; if
worked through directly, merge the result into the matrix yourself.

## Review Protocol

1. Review only this lane and the supplied diff or files.
2. Stay diff-bounded unless a nearby file is necessary to understand blast radius.
3. Mark each criterion `pass`, `fail`, or `na`.
4. Include concrete evidence for every row.
5. Return only the requested lane result table unless asked for analysis.

## Lane Criteria

- `repo.catalogs-and-docs` - Catalogs and docs are aligned
  - Review: Check README.md, SKILLS.md, AGENTS.md, design docs, CONFIG.md, and repo-facing examples for stale references or missing updates caused by the skill change.
- `repo.changelog-and-pr` - A changelog fragment exists only when the host repo's gate owes one (**Claude Code plugin-specific, am-pm monorepo only — skip for a portable skill or a repo with no equivalent changelog gate**)
  - Review: Check that a changelog fragment was added only where the host repo's gate would ask for one (am-pm: the diff touches the ambassador contract or a declared tier-2 surface; an ordinary plugin under `groups/` is neither). A fragment on a not-applicable diff is a defect, and so is a missing one where the gate fires.
- `repo.validation-alignment` - Validation stays aligned
  - Review: Check that repo validators, pre-commit, tests, and CI expectations cover the new requirement without adding skill-specific exceptions where a shared rule is appropriate.
