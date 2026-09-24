# Component Fit Reviewer

> **Claude Code plugin-specific — skip this entire lane for a portable/Codex-only
> skill.** It reviews optional Claude Code plugin components (commands, subagents,
> hooks, MCP, LSP, monitors), none of which exist outside a Claude Code plugin.
> A portable/Codex-only skill has nothing for this lane to review.

Use when reviewing optional am-pm component fit for skill quality reviews.

Review whether optional am-pm components are justified, omitted intentionally, and safe, especially MCP usage.

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

- `component-fit.justified-components` - Selected components are justified
  - Review: For each selected component, check the artifact names its aim, the advantage over its nearest alternative, and the cost accepted. Flag any component justified only by restating what it is, or justified in isolation without comparison to the neighbour that would also work.
- `component-fit.intentional-omissions` - Omitted components are intentional
  - Review: Check omissions are recorded with the cost avoided, not a bare "not needed". Do NOT treat a skill-only design as incomplete; flag the opposite — a component added without a cost being weighed.
- `component-fit.mcp-approval` - MCP usage is approved and auditable
  - Review: If .mcp.json is included, check that direct API usage was considered and that the review artifact contains explicit auditable evidence that the user said the MCP server is security-approved for company use.
- `component-fit.enforce-over-instruct` - Deterministic enforcement is preferred over prompt rules
  - Review: Check deterministic checks use hooks, scripts, or validators rather than prompt-only instructions. Flag a guarantee ("always", "never", "every time") resting only on a skill description when a deterministic alternative exists. Also flag the reverse — a forced hook: one whose trigger the design cannot name in a sentence, one whose injected content is static (that is CLAUDE.md or a skill, not a subprocess), or one on an event that cannot act on what it sees (only 11 events carry additionalContext; Setup, InstructionsLoaded and StopFailure discard JSON output entirely). A guard hook shipped without a documented negative test — a command it must refuse — is unverified: hooks fail open, and a broken one still looks configured.
