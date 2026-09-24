# Multi-Phase Skill Patterns

Read this when `Step 2 — Doctrine, component fit, and structure` concluded that a
multi-phase structure is warranted.
Do not read this for single-skill or multi-skill-split designs.

<!-- authors: Sagy Ashlag, Israel Abudi -->

## When multi-phase is warranted

Multi-phase is the right structure when **at least two** of these are true:

- Distinct dependent stages where stage N requires stage N-1's output artifact
- User approval is required between stages before proceeding
- Each stage produces a structured manifest written to disk that the next stage reads
- Skipping a stage causes downstream failures (not just poor output — actual failures)

If only one is true, use a single skill with sequential workflow steps instead.

## Hard constraints

- **2–5 phases only.** More than five phases signals the skill is trying to do too much.
- **Strictly linear.** No branching, no optional phases, no loops back.
- **One manifest per phase.** Written to disk via file write, never to chat output.
- **Code modification restricted to designated execution phases.** Analysis and planning phases MUST NOT write production code.
- **References one level deep from SKILL.md.** Phase reference files link back to SKILL.md, never to each other.
- **Gates are hard stops.** A gate means the agent MUST wait for explicit user approval before advancing.
- **SKILL.md body stays an orchestrator.** All phase detail lives in `references/phase-N-<name>.md`. The body's only budget is the character cap in `SKILL_SPEC.md`, which `quick_validate.py` decides.

## File structure

```text
my-skill/
├── SKILL.md                              # Orchestrator only
├── references/
│   ├── phase-1-<name>.md                 # Full phase workflow
│   ├── phase-2-<name>.md
│   └── <domain-knowledge>.md             # Optional bundled rules
└── templates/
    ├── phase-1-manifest-template.md      # One template per phase
    └── phase-2-manifest-template.md
```

## Designing phase architecture

Present this table to the user and iterate until confirmed before implementing:

| Phase | Name | Purpose | Produces | Gate | Code allowed? |
|---|---|---|---|---|---|
| 1 | `<name>` | `<what it does>` | `<manifest-path>` | `<approval description>` | ❌ |
| 2 | `<name>` | `<what it does>` | `<manifest-path>` | `<approval description>` | ✅ |

**Phase boundary rules:**

- Each boundary must represent a genuine mode shift (analysis → planning, planning → execution)
- Each boundary must have a concrete artifact the next phase requires
- Each boundary where the user must decide something gets a gate

## Phase reference file structure (`references/phase-N-<name>.md`)

Each phase reference file follows this structure:

```markdown
# Phase N: <Name>

**Purpose:** <one sentence>
**Inputs:** <what this phase requires — manifest from previous phase, user input, etc.>
**Outputs:** `<manifest-path>` — written to disk before the gate

## Role

Act as <domain-specific role with bounded authority for this phase>.

## Steps

1. <Imperative step with explicit inputs and outputs>
2. ...

## Guardrails

- MUST NOT <things out of scope for this phase>
- MUST write manifest before presenting gate

## Output manifest

The manifest at `<path>` MUST contain:
- `<field>`: `<what it represents>`

## Gate: <Gate name>

Present the manifest to the user and wait for explicit approval before Phase N+1.

## Definition of Done

- [ ] All steps completed
- [ ] Manifest written to `<path>` and verified
- [ ] User has approved the gate

**MANDATORY NEXT STEP:** With user approval, proceed to Phase N+1 following `references/phase-N+1-<name>.md`.
```

## Manifest template design (`templates/phase-N-manifest-template.md`)

Use `{{PLACEHOLDER}}` syntax for all variable fields. All sections mandatory. Include a "Next Phase" pointer at the end.

```markdown
# Phase N Manifest: {{SKILL_NAME}}

Status: {{STATUS}}
Created: {{DATE}}

## <Section>

{{PLACEHOLDER}}

## Next Phase

Proceed to Phase N+1 only after explicit user approval of this manifest.
```

## SKILL.md orchestrator structure

SKILL.md is the map, not the territory. It contains:

1. **Phase enforcement block** — table of all phases with their gate names, explicit rule that phases cannot be skipped
2. **Goal** — one sentence
3. **When to use / NOT** — include that single-step requests should skip multi-phase
4. **Phase overviews** — 3–5 lines each: purpose, what it produces, link to phase reference
5. **Phase sequence** — ordering + prerequisites + gate names
6. **Verification** — combined per-phase checklists
7. **Common failures** — phase skipping, stale manifests, gate bypass
8. **References** — links to all phase reference files and manifest templates

## Common failures and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Agent skips a phase | Phase wasn't named as a hard prerequisite | Add explicit "Phase N MUST complete before Phase N+1" rule in Phase Sequence section |
| Stale manifest causes wrong output | Previous run's manifest read instead of current | Name manifests with a session ID or require user to confirm manifest path before each phase |
| Gate bypassed silently | Gate phrased as suggestion | Replace with MUST: "MUST present manifest and wait for explicit approval before proceeding" |
| Phase reference too long | All logic in one file | Split into sub-steps by reuse frequency; reference files have no size budget |
| Code written in analysis phase | Boundary not enforced | Add "MUST NOT write or modify production files" to phase guardrails |
