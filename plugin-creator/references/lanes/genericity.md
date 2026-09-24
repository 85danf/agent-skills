# Genericity Reviewer

Use when reviewing whether a generic plugin avoids local or organization-specific assumptions.

Review whether runtime vocabulary and behavior avoid local, workplace, or repo-specific assumptions.

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

- `genericity.runtime-vocabulary` - Runtime vocabulary is generic
  - Review: Check that profile names, environments, queues, teams, tenants, workflow labels, field names, URLs, credential names, and other runtime vocabulary are configurable, discoverable, CLI-provided, or obvious placeholders instead of local defaults.
- `genericity.no-local-assumptions` - No local assumptions leak into behavior
  - Review: Check for organization-specific identifiers, paths, naming conventions, status services, repository hosts, branches, projects, dashboards, or workflow rules that would only work for the creator's machine or workplace.
