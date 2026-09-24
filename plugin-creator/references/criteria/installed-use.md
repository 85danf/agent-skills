# Installed Use Criteria

Generated from `../../assets/skill-quality-criteria.json`. Do not edit by hand.

Use this lane while designing installed-user packaging, defaults, shipped files, and compatibility.

## Examples

- Good: Ship the preflight script, config loader, schemas, references, and fixtures needed for normal and recovery workflows inside the skill directory.
- Bad: Tell installed users to follow a parent-repo wiki page or call a sibling-repo script that is not included with the installed skill.

- Good: Preserve existing config keys, CLI flags, output contracts, generated files, and documented workflows, or document and test a migration.
- Bad: Rename existing config keys and CLI flags without compatibility tests or migration guidance.

## `installed-use.self-contained-runtime` - Runtime is self-contained

Keep required happy-path and recovery-path workflows inside the skill directory, including scripts, references, assets, schemas, and templates.

## `installed-use.installed-compatibility` - Installed-user compatibility is protected

Preserve existing config keys, CLI flags, output contracts, generated files, scripts, and documented workflows unless a breaking migration is explicit and tested.
