# Component Fit Criteria

Generated from `../../assets/skill-quality-criteria.json`. Do not edit by hand.

Use this lane during skill planning to decide whether supported am-pm plugin components should supplement the core skill.

## Examples

- Good: Keep a skill-only primitive when scripts and references are enough; add a command only for a frequent explicit workflow and a hook only for deterministic guardrails.
- Bad: Add MCP, hooks, monitors, and subagents to every new skill because they are available.

- Good: For SaaS integrations, use direct API scripts by default and include MCP only when the user explicitly requests it and attests it is security-approved for company use.
- Bad: Choose MCP for a third-party service without an auditable approval statement or when a simple tested API script would be clearer.

## `component-fit.justified-components` - Selected components are justified

For each selected component, state its aim in one line, what it buys that the alternatives do not, and what it costs. Justify it against its nearest neighbour, not in isolation — a trigger is a skill (semantic, the model decides) or a hook (an event decides); noticing something is a monitor (external, continuous), a hook (a session event), or an on-demand check; capability is a script/CLI or MCP; isolation is a subagent or inline work. Valid reasons include trigger reliability and context economy, not only drift control, consistency, guardrails, ergonomics, observability, and reusable runtime tooling.

## `component-fit.intentional-omissions` - Omitted components are intentional

Skill-only is the expected outcome, not a gap. When a component might seem relevant but is omitted, name the cost it would have imposed — context consumed, latency per call, a dependency, a server to trust, a gate that cannot be verified by inspection — rather than only asserting it is not needed.

## `component-fit.mcp-approval` - MCP usage is approved and auditable

Prefer direct API scripts for third-party SaaS, websites, and services. Include MCP only when justified or user-requested, and require explicit user attestation that the MCP server is security-approved for company use.

## `component-fit.enforce-over-instruct` - Deterministic enforcement is preferred over prompt rules

Prefer hooks, LSP, scripts, or CI gates for checks that can be deterministic. Reserve prompt-only rules for judgment calls that cannot be scripted. A behaviour the design GUARANTEES is not guaranteed while it rests on a description: a 90%-compliant model is not a control. The rule cuts the other way too — do not reach for a hook when the injected content never changes (that is CLAUDE.md or a skill, however cleanly the moment names itself) or when recognising the trigger needs judgement. Most plugins name no moment worth hooking, and that is the expected answer. For a guardrail that should apply only while one skill runs, declare a `hooks:` block in that skill's SKILL.md frontmatter (scoped to the skill, fires only while it is active) instead of an always-on plugin hook (see references/components/hooks.md).
