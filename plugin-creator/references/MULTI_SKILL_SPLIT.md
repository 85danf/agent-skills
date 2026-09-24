# Multi-Skill Split

Read this only when deciding whether one skill should be **several**. Any number of skills
is allowed; nothing caps N. A single-skill design does not need this file.

## Structure

A plugin can hold several skills under `skills/<name>/`. Each skill owns its own
`scripts/`, `references/`, and `assets/`; the plugin's components (hooks, subagents, MCP,
LSP, monitors, commands) stay at the plugin root, shared across every skill in it.

## Split signals

- different triggers
- different audiences
- different tool sets
- independent lifecycles
- conflicting context budgets

## Merge signals

- shared logic > 50%
- each part too thin (just a script wrapper)
- operation variants of one domain
- the user thinks of it as one thing
- **two skills need the same script** — they may be too similar to justify the split

**These apply pairwise across any N.** Check every pair of proposed skills, not just the
first split you thought of — they are what stops a two-way split becoming a six-way one,
and widening to N without them removes the only brake on the number.

## The test

Each skill after splitting must have **meaningful capability** — its own workflow, its own
judgment decisions, its own progressive disclosure. A part that fails this test is not a
skill; it is a section of one.

## If split is recommended, present

One row per proposed skill, however many that is:

| Skill | Responsibility | Trigger |
|---|---|---|
| `<skill-1>` | `<what it does>` | `<user-invoked or model-invoked>` |
| `<skill-2>` | `<what it does>` | `<user-invoked or model-invoked>` |
| `<skill-N>` | `<what it does>` | `<user-invoked or model-invoked>` |

Shared plugin components: `<list or none>`
