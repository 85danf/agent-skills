# Prompt Engineering Best Practices for Skills

Distilled from Anthropic, OpenAI, and Windsurf documentation. Apply these when writing SKILL.md instructions.

## Core Principles

### 0. Scripts absorb complexity, agent stays simple

The overall guideline: prefer a simpler agent surface over simpler scripts. When logic can be a script, it should be — but this is a balance, not a dogma. Don't write overly complex scripts to avoid trivial agent decisions. The goal is to minimize the number of agent steps where things can go wrong while keeping scripts readable and maintainable.

- Agent workflow should be a short, linear sequence of script calls — not branching logic or multi-step reasoning
- Each script should handle its own validation, error reporting, and output formatting
- The agent's job is to pick the right script, pass the right args, and present the output

**Rule of thumb:** if logic can be a script, it should be — even a single decision point. The bar for keeping logic on the agent side is "does this genuinely require agent judgment (e.g., interpreting user intent)?" If not, script it.

### 1. Be clear and direct

Think of the agent as a brilliant new employee with zero context on your norms and workflows. The more precisely you explain what you want, the better the result.

**Golden rule:** Show your SKILL.md to a colleague who has never used the tool. If they'd be confused, the agent will be too.

- Be specific about desired output format and constraints
- Provide instructions as sequential steps using numbered lists when order matters
- Use bullet points for unordered sets of options

### 2. Add context and motivation

Explain WHY a rule exists, not just WHAT it is. Context helps the agent make better decisions in edge cases.

Bad: "Never delete without confirmation."
Good: "Never delete without showing the plan first and getting explicit user approval. Deletion is destructive and irreversible (except via trash recovery)."

### 3. Say what TO do, not what NOT to do

Positive instructions are clearer and more actionable.

Bad: "Do not proceed without checking credentials."
Good: "Confirm credential environment variables are set before running any operation."

### 4. Use examples effectively

Examples are the most reliable way to steer output format, tone, and structure. When adding examples:

- **Relevant**: Mirror actual use cases closely
- **Diverse**: Cover edge cases and vary enough to avoid unintended pattern-matching
- **Structured**: Clearly delimit examples from instructions (use fenced code blocks)

Show exact CLI commands with realistic arguments:

```bash
.tool-venv/bin/python <skill_dir>/scripts/create_item.py \
  --config .tool.json \
  --type story \
  --summary "My Item Title" \
  --description "Description text"
```

### 5. Structure with clear hierarchy

Use markdown headings, numbered steps, and tables to create unambiguous structure:

- **Headings** for major sections (## Workflow, ## Operations)
- **Numbered lists** for sequential procedures (### Step 1 — Validate)
- **Bullet lists** for unordered options
- **Tables** for reference data (error codes, config fields)
- **Code blocks** for commands and config examples

### 6. Progressive disclosure

Keep the main SKILL.md body concise — the enforced size limits live in
[SKILL_SPEC.md](SKILL_SPEC.md) (Progressive disclosure); do not restate them here. <!-- citation -->
Put detailed content in reference files:

| Content type | Location |
|---|---|
| Trigger keywords, workflow overview | SKILL.md body |
| Full config schema with all fields | references/CONFIG.md |
| Input/output format specifications | references/FORMAT.md |
| Domain-specific field mappings | references/FIELD_MAPPING.md |
| Skill approval plan templates | references/PLAN_TEMPLATE.md |

The agent loads SKILL.md on activation, then reads references only when needed.

The full context-engineering criteria used by plugin-creator live in
[criteria/context.md](criteria/context.md); do not restate them here. <!-- citation -->
This file stays focused on general prompt-engineering patterns; criteria-level
checks are generated from `assets/skill-quality-criteria.json`.

## Skill-Specific Patterns

### Trigger keywords in description

The frontmatter `description` field determines when the agent activates the skill. Include:

- **Action verbs**: create, update, fetch, delete, publish, analyze, validate, diff, export
- **Domain nouns**: tickets, pages, documents, reports, configs
- **Tool names**: Jira, Confluence, GitHub, etc.
- **Common phrasings**: "bulk create from spec", "compare local vs remote"

Bad: "Manages things in a tool."
Good: "Create, update, fetch, delete, diff, and validate Jira tickets from structured markdown or JSON sources. Use when the user asks to create Jira tickets, update existing issues, bulk-create stories and subtasks from a spec, compare local definitions against live Jira state."

### Pre-flight checks

Pre-flight checks should be a **single script** that the agent calls once — not individual agent steps. The script validates everything and reports a clear pass/fail summary. The agent reads the output and proceeds or stops.

The preflight script should check:

1. **Runtime environment** — language version, venv exists, dependencies installed
2. **Configuration file** — exists and has required fields; report what's missing
3. **Credentials** — confirm env vars are SET without printing values
4. **Connectivity/discovery** — optional first-run validation

This is a prime example of the core principle: the agent runs one command and reads the result, rather than executing four separate checks with branching logic.

### Risk-tiered approval gates

External-resource skills should classify actions before executing. This is the
single wording of the three tiers; the gated criterion that reads them lives in
`risk.approval-and-enforcement` in [criteria/risk.md](criteria/risk.md); do not restate it here. <!-- citation -->

- **No approval**: read-only discovery, status, list, fetch, diff, or diagnostics inside the user's requested scope.
- **Bounded approval**: a named plan for a scoped operational task, such as investigating one repository, tenant, cluster, browser session, database, topic, or queue.
- **Fresh approval**: writes, deletes, publishes, deploys, restarts, exec, permission changes, admin/security changes, external messages, bulk actions, sensitive data exports, or leaving the approved scope.

For bounded or fresh approval:

1. Build a plan showing exactly what will happen.
2. Present the plan to the user in a clear visual format.
3. Wait for explicit user approval before executing.
4. Support `--dry-run` for preview without side effects where practical.
5. For high-risk skills, prefer runtime-enforced confirmation through a wrapper or script instead of relying only on prompt instructions.

If runtime approval tokens or markers are used, they should be issued by the user, host, or wrapper; be scoped and short-lived; and live outside the agent's normal write permissions. If the skill cannot enforce that boundary, document that the approval is prompt-only and name the residual bypass risk.

### Workflow pattern

Every skill should follow this workflow sequence:

1. **Validate** — run pre-flight checks
2. **Determine scope** — what does the user want to do?
3. **Classify risk** — decide no approval, bounded approval, or fresh approval
4. **Build the plan** — show what will happen when approval is required
5. **Get approval** — wait for explicit confirmation when required
6. **Execute** — run the operation
7. **Verify** — offer to validate results

### Error handling

Include two tables:

**Error handling** — for API/runtime errors:

| Error | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | Bad credentials | Verify env vars are set and token has correct permissions |

**Troubleshooting** — for setup/environment issues:

| Problem | Fix |
|---|---|
| `python3: command not found` | macOS: `brew install python3` / Linux: `apt install python3` |

## Anti-patterns to avoid

| Anti-pattern | Better approach |
|---|---|
| Vague description ("helps with stuff") | Rich description with action verbs and domain keywords |
| Hardcoded values in SKILL.md | Config file + discovery script |
| Monolithic SKILL.md (10K+ tokens) | Progressive disclosure with references/ |
| No pre-flight checks | Numbered checks run before every operation |
| No approval gates | Risk tier → plan when needed → approve when required → execute |
| Agent-writable approval marker | Host/user-issued scoped approval outside normal agent write permissions |
| Printing credentials | Only confirm SET/MISSING status |
| Single mega-script | One script per operation + shared config loader |
| Complex agent branching logic | Push decision logic into scripts; agent calls scripts with simple args |
| No error guidance | Error table + troubleshooting table |
| Negative instructions ("don't do X") | Positive instructions ("do Y instead") |
| No examples | Exact CLI commands with realistic arguments |
