# SKILL.md Authoring Guide

Detailed guidance for writing SKILL.md content. Read this during
`Step 5 — Implement` when writing or modifying a SKILL.md file.

## Frontmatter rules

```yaml
---
name: skill-name # Must match directory name, lowercase + hyphens only
description: > # 1-1024 chars. Include BOTH what it does AND when to use it.
  Verb-first action description. Include trigger keywords that help agents
  identify when this skill is relevant.
metadata:
  author: <author>
  version: "1.0"
allowed-tools: > # Optional: List of pre-approved tools (experimental)
  read_file run_command
compatibility: > # Only if specific requirements exist
  Runtime requirements, API versions, OS constraints.
disable-model-invocation: true # Optional: mark the skill manual-only (human intent
  # required, or destructive/risk-accepting); see the pre-screen and risk lanes
# Claude Code plugin-specific — skip the `hooks:` block entirely if authoring a
# portable/Codex-only skill; the Agent Skills standard and Codex have no equivalent.
hooks: # Optional: deterministic guardrails scoped to THIS skill (fire only while it
  # runs). matcher is the tool name, not the skill name
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/skills/skill-name/scripts/guard.sh"
---
```

`disable-model-invocation` is portable. `hooks:` is **Claude Code plugin-specific
— skip it entirely if authoring a portable/Codex-only skill.** Add
`disable-model-invocation: true` when the skill accepts risk or needs deliberate
human intent (see the pre-screen and risk lanes). Add a Claude Code `hooks:` block
only for a guardrail that must apply while this skill runs, and only when
authoring for Claude Code; the Hooks component recipe (selected during Component
Fit) covers the full skill-scoped-hook pattern.

## Skill type

Before writing the body, determine the skill type:

| Type                  | Examples                                                | Key traits                                                                                                                                                                                  |
| --------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **External-resource** | Jira, Confluence, Bitbucket, Jenkins, EKS               | Calls APIs; needs config, credentials, connectivity checks; defaults to read-only where practical; risky mutations need risk-tiered approval, `--dry-run`, and runtime enforcement analysis |
| **Local-only**        | Code analysis, review prompts, file transforms, linters | Operates on local files/repos; no credentials or API config; no approval gates needed for read-only operations                                                                              |

For local-only skills, simplify prerequisites, configuration, preflight, workflow, and error handling to match the actual runtime needs. Every other section still applies.

## Content positioning by reusability

Position content by how often it is needed relative to how often the skill is
invoked:

- **Every invocation** → SKILL.md (workflow, safety rules, operation routing)
- **Some invocations** → `references/<topic>.md` (loaded by the agent on demand)
- **Rare or deep** → sub-files under a parent index: `references/<topic>/<detail>.md`

Sub-files do not need to be referenced from SKILL.md — they belong to their
parent index file. Apply the same splitting pattern to any reference file where
sections have different reuse frequencies: create a parent index and a subfolder
(e.g. `COMPONENTS.md` → `components/*.md`, `hooks.md` → `hooks/*.md`).

**Every reference link needs a brief "when to read" trigger** — the same way a
skill's `description` tells the agent when to invoke it. Write "when X, read Y"
not "see Y". Keep the trigger short and clear so the agent can skip irrelevant
references at a glance.

## Signal-noise filter

Before writing any instruction, apply this four-question filter. Fail any question → cut or move to a reference:

1. **Would the agent ask about this if it were missing?** No → noise. The agent would behave correctly without it.
2. **Could the agent discover this by reading existing repo files?** Yes → noise. The agent pays twice and the instruction goes stale.
3. **Does this change frequently?** Yes → noise. Stale context poisons more than no context.
4. **Is this a standard convention the model already knows?** Yes → noise. Only document project-specific deviations.

Signal keeps: non-obvious build/test commands with exact flags, version constraints that override defaults, counterintuitive architectural decisions, non-negotiable deviations from common conventions, explicit permission boundaries.

Noise cuts: generic quality instructions ("write clean code"), standard professional conventions, codebase overviews the agent can read itself, content already in README or existing docs, time-sensitive sprint context, personality boosters.

## 3-zone layout

After applying the signal-noise filter, order the SKILL.md body using this attention curve:

| Zone | Position | What goes here |
|---|---|---|
| Zone 1 | Top ~15% | Security constraints, NEVER/ALWAYS rules, hard architectural decisions — if you'd be upset when the agent ignores it, put it here |
| Zone 2 | Middle ~70% | Patterns with examples, stack definitions, workflow steps, testing rules |
| Zone 3 | Bottom ~15% | Executable commands, workflow triggers, verification checklists |

Critical constraints buried in Zone 2 are routinely missed. Place them at the top.

## Body structure

Write these sections in this exact order:

1. **Title + one-liner** — `# Skill Name` + single sentence summary
2. **When to use this skill** — bullet list of trigger scenarios with action verbs
3. **Prerequisites** — numbered list: config file, credentials, dependencies
4. **Configuration** — minimal config example + link to `references/CONFIG.md`. Keep the main section limited to what the agent needs during normal operation; move first-run setup details, full schemas, optional tuning fields, and extended examples into `references/CONFIG.md`.
5. **Pre-flight checks** — a single script call that validates runtime, config, credentials, and connectivity/discovery as applicable. The agent calls the script once and reads the output; it does not run each check individually. If a config/setup failure is likely, the script output and `SKILL.md` must point to the relevant configuration reference.
6. **Workflow** — numbered steps: validate → determine scope → classify risk → build plan → get approval when required → execute → verify
7. **Operations** — one subsection per operation with exact CLI commands using `<skill_dir>`
8. **Important rules** — numbered list of invariants such as approval gates, security, and ordering
9. **Error handling** — table with columns: Error | Cause | Fix
10. **Troubleshooting** — table with columns: Problem | Fix

## Supporting files guidance

Use [QUALITY_CHECKLIST.md](QUALITY_CHECKLIST.md) to route to the relevant <!-- citation -->
generated criteria lanes. For scripts, config, tests, and repo integration,
resolve the active criteria lanes and apply the returned runtime, repo, and
review references while creating each file, not only at final review.

At minimum:

- Create `references/CONFIG.md` for skills with config loaders or config schemas. Use it for first-run setup details, full schemas, optional tuning fields, and extended examples so `SKILL.md` stays concise during normal operation.
- Route configuration recovery through `references/CONFIG.md`: `SKILL.md` should name the reference, and preflight/config errors should point to it when setup or field fixes are needed.
- Create operation-specific references for complex input/output formats, edge cases, and limitations
- Keep all required runtime instructions, scripts, references, assets, schemas, templates, and sample configs inside the skill directory
- Create focused scripts with clear CLI flags, structured exit codes, helpful diagnostics, `--dry-run` for destructive operations, and `--confirm` or equivalent runtime gates for high-risk actions where practical
- For shared repositories, update catalogs, design docs, tests, config docs, manifests, and exemptions according to repo conventions
- Let the host repo decide whether a PR owes a release-note fragment; do not add one on your own judgement. In am-pm, run `am-pm changelog-gate --base-ref <merge-target>` after committing and follow what it prints — it says a fragment is owed, and what it must answer, or prints nothing, and a plugin under `groups/` owes none unless the gate asks.
