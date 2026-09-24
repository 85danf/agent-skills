# Subagents Component

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only
> skill.** This component and its runtime mechanics (frontmatter fields, JSON
> schema, `am-pm validate` command) exist only in Claude Code plugins; there is no
> equivalent in the portable Agent Skills standard or in Codex.


## What It Does

A subagent is a specialized worker or reviewer that runs in its own context
window. The subagent file is Markdown instructions with YAML frontmatter that
defines the agent's role, boundaries, and available tools.

## Dispatch Mechanisms

- **Agent tool** — Claude auto-delegates based on description match; the main
  agent picks the best-fit subagent without user intervention.
- **@-mention** — the user explicitly names a subagent (e.g. `@config-reviewer`)
  to force dispatch to it.
- **`context: fork` in skills** — a skill's frontmatter can declare fork context,
  causing it to run as its own subagent session.
- **`--agent` flag** — launches a subagent definition as the main session agent
  for the entire CLI invocation.

## Frontmatter Fields

### Required (am-pm convention)

| Field | Type | Description |
|---|---|---|
| `name` | string | Kebab-case identifier for the subagent. |
| `description` | string | What the subagent does. **am-pm convention:** must start with "Use when" so dispatchers can choose from metadata alone. Claude Code itself does not enforce this prefix. |
| `tools` | string or list | Tools the subagent may use. **am-pm convention:** must be explicitly listed. In Claude Code, `tools` is optional — omitting it lets the subagent inherit all tools from the main conversation. |

### Optional

| Field | Type | Description |
|---|---|---|
| `model` | string | Model alias (`sonnet`, `opus`, `haiku`), full ID (`claude-opus-4-8`), or `inherit`. Resolution order: `CLAUDE_CODE_SUBAGENT_MODEL` env var > per-invocation override > frontmatter value > main conversation model. |
| `effort` | enum | Reasoning effort: `low`, `medium`, `high`, `xhigh`, `max`. |
| `maxTurns` | integer (>= 1) | Maximum conversation turns before the subagent stops. |
| `disallowedTools` | string or list | Tools the subagent must not use. |
| `skills` | list of strings | Skills whose content is preloaded at subagent startup. Without this field the subagent can still discover and invoke skills via the Skill tool at runtime. Skills with `disable-model-invocation: true` cannot be preloaded. |
| `memory` | enum | Memory scope: `user`, `project`, or `local`. Each maps to a filesystem path. When set, the first 200 lines / 25 KB of the corresponding MEMORY.md is auto-injected into the subagent's context. |
| `background` | boolean | When `true`, the subagent runs concurrently with the main agent. Any tool call that would prompt for permission is auto-denied. |
| `color` | string | UI display color. Allowed: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`. |
| `initialPrompt` | string | Prompt sent on startup. Only fires when the subagent runs as a main session via `--agent`; ignored during normal subagent invocation. |
| `isolation` | string | Isolation mode (e.g. `worktree`) for the subagent's working directory. |

### Banned for plugin-shipped subagents

These fields are silently ignored (not rejected) when the subagent is shipped
inside a plugin:

- `hooks`
- `mcpServers`
- `permissionMode`

The positive enumeration of allowed plugin-shipped fields is: `name`,
`description`, `model`, `effort`, `maxTurns`, `tools`, `disallowedTools`,
`skills`, `memory`, `background`, `isolation`.

## Tool Resolution

Subagents inherit the tool set from the main conversation. The following tools
are never available to subagents: `Agent`, `AskUserQuestion`, `EnterPlanMode`,
`ExitPlanMode`, `ScheduleWakeup`, `WaitForMcpServers`. Because `Agent` is
excluded, subagents cannot spawn other subagents.

## Minimal Example

```yaml
---
name: config-reviewer
description: Use when reviewing configuration files for portability issues.
tools:
  - Read
  - Grep
  - Glob
model: sonnet
effort: high
---
```

## Cost

Four gains, and one pitfall that colours all four.

You gain a **tool boundary the harness enforces** rather than a prompt asking nicely; a
**separate context window**; **parallelism** across genuinely independent tasks; and an
**agent definition fixed in advance**, which you can evaluate once.

You pay with the hand-off. The subagent sees only what you give it, and every crossing is
lossy in both directions: your brief may omit context it needed, its report may omit
findings you needed. Claude also rewrites the delegation message on every invocation, so
only the definition is fixed — the prompt that actually arrives is not, and neither is what
comes back. Net cost can exceed doing the work inline. The mitigations in
[Pitfalls](#pitfalls) below — write the report to a file, tell it its measurement wins — are
what make the gains survive that crossing; neither is optional.

## Use When

- The task benefits from independent review, parallel checks, or a fresh context
  window.
- The output is a bounded artifact: findings list, table, or patch plan.
- The role is reusable across many invocations of the skill or plugin.

## Do Not Use When

- A normal reference file gives enough guidance to the current agent.
- The work requires shared mutable state or step-by-step coordination with the
  main agent.
- The role would duplicate generic review guidance without adding a sharper focus.

## Monorepo Path

- Plugin file: `groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/agents/<agent>.md`

## Pitfalls

- **It saves the host's context, not total tokens.** The work still runs; it runs
  somewhere else. A subagent is not the cheaper option, it is the option that keeps the
  host's window clean — reach for it for the boundary, never to save spend.
- **Make the subagent write its report to a file before it replies.** A report that exists
  only in a reply is a report you can lose: replies are truncated, summarised, and gone
  after the turn.
- **Tell it its measurement wins.** State, in the brief, that if what it measures disagrees
  with what you told it, the measurement is right and you want to be told. Without that
  line a subagent will quietly reconcile its findings to your brief.

## Best Practices

- Give each subagent a narrow mission and explicit output shape.
- Include the minimum context it needs; avoid asking it to rediscover unrelated
  repo state.
- Use subagents for review and analysis before mutation unless the workflow has
  strong isolation and verification.
- Keep `tools` explicit and narrow for the role. Broad tool lists dilute focus
  and increase risk of unintended mutations.

## Validation

- Run `am-pm validate subagent agents/<agent>.md`.
- Confirm `tools` is explicit and narrow enough for the role.
- Run a prompt readback or dry run when the subagent is new.
