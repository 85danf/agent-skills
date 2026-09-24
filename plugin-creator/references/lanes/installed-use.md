# Installed Use Reviewer

Use when reviewing whether installed users receive a self-contained, compatible skill.

Review whether installed users have the required scripts, references, assets, config, compatibility, and migration behavior.

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

- `installed-use.self-contained-runtime` - Runtime is self-contained
  - Review: Check that installed users can run required happy-path and recovery-path workflows from the skill directory without relying on sibling repo docs, unrelated skills, or external review prompts.
- `installed-use.installed-compatibility` - Installed-user compatibility is protected
  - Review: Check that existing config keys, CLI flags, output contracts, generated files, scripts, and documented workflows are preserved or explicitly migrated with compatibility tests.
