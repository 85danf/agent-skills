# Skill Plan Template

Use this template across the plugin-creator workflow's two approval gates: the design
sections (1-4, 6-8, 11 and 12) are written and approved first, and only then are the
implementation sections (5, 9 and 10) written and approved. The plan is an approval
artifact for the user: readable enough to approve quickly, but complete enough
to show that the key quality lanes were considered.

Keep the plan concise. Do not duplicate the generated lane criteria; map each
lane to concrete design decisions and evidence instead.

## Plan artifact

Write the completed plan before requesting approval:

- In am-pm:
  `groups/<group>/<domain>/<lifecycle>/docs/<plugin>/internal/YYYY-MM-DD-<skill-name>-plan.md`
- In another workspace or shared repo:
  `docs/plans/YYYY-MM-DD-<skill-name>-plan.md`

The plan must not be written inside the shipped plugin directory or a skill's
`references/` directory. On initial creation, preserve an unrelated existing
file by selecting the first free numeric suffix, such as
`YYYY-MM-DD-<skill-name>-plan-2.md`. Revisions update the same selected file.
If the plan cannot be written, report the failing path and reason, then ask for
an alternative writable docs path. The workflow must not fall back to a conversation-only plan.

## Template

````markdown
# Skill Plan: <skill-name>

Plan artifact:

- Path: `<plan-path>`
- Target: `<plugin-or-standalone-skill>`
- Status: `awaiting approval`  <!-- → `design-approved` at the design gate → `plan-approved` at the implementation gate -->

Approval request: approve this plan to create or update `<skill-name>` with the
scope, structure, and review coverage below.

## 1. Goal

One or two sentences:

- What the skill helps an agent do
- Who or what it is for
- What successful use looks like

## 2. Scope

| Included | Deferred | Explicitly omitted |
|---|---|---|
| <core capability> | <future/nonessential item> | <risky or nonportable item> |

## 3. User Experience

First-use flow:

1. Agent runs preflight.
2. Agent reads or creates minimal config if needed.
3. Agent chooses the operation.
4. Agent presents an approval plan only when required.
5. Agent executes and verifies the result.

Minimal config:

- Config file: `<path/name>` or none
- Required fields: `<fields>` or none
- Discovery/setup helper: `<script>` or none

## 4. Capability And Operations Map

| Operation | Inputs | Output | Script/tool | Approval tier | Verification |
|---|---|---|---|---|---|
| `<operation>` | `<inputs>` | `<output>` | `<script/tool>` | none/bounded/fresh | `<check>` |

### 4.1. Dependencies and Verified Contracts

For each external dependency or host contract used by an included operation, record:

| Operation / dependency | Tested version and supported range | Contract needed | Primary source / observation | Unresolved assumption and resolution |
|---|---|---|---|---|
| `<operation / package and binary identity>` | `<version / range, or versionless API date>` | `<install/auth method, command/flags or endpoint, required and nullable fields>` | `<official URL or repo path + revision; observed command + date + evidence path>` | `<resolve before implementing the affected operation, or none>` |

Research only what the design uses. Prefer published schemas/manifests, official docs,
dependency source and reproducible observations. Record how fixtures were obtained,
the source version and how to refresh them; redact secrets and account data. An
observed version is not proof of every version in a claimed support range.

When assessing source independence and unresolved contracts, apply
`runtime.cli-and-config-contracts` from the active generated runtime lane. Record
installation/authentication evidence as well as operation contracts. <!-- citation -->

Keep research evidence in this plan or linked maintainer artifacts outside the shipped
plugin. Ship only the operational reference information installed users need. For a
local-only skill with no such dependency, write `N/A` with a reason. Broader exploratory
research remains optional.

## 5. Proposed File Structure

```text
<skill-name>/
├── SKILL.md
├── scripts/
├── references/
├── assets/
└── agents/openai.yaml
```

For multi-skill plugins (Claude Code plugin monorepo only — skip this tree shape
for a portable/Codex-only skill, which has no plugin root, no `agents/`,
`commands/`, `hooks/`, `.mcp.json`, `.lsp.json`, `monitors/`, or
`.claude-plugin/plugin.json`):

```text
plugin-name/
├── skills/
│   ├── skill-1/
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   ├── references/
│   │   └── assets/
│   └── skill-2/
│       ├── SKILL.md
│       ├── scripts/
│       └── references/
├── agents/
├── commands/
├── hooks/
├── .mcp.json
├── .lsp.json
├── monitors/
└── .claude-plugin/
    └── plugin.json
```

Scripts, references, and assets belong to their skill. Components at the
plugin root are shared across all skills.

For a **multi-skill** plugin, show each skill's `SKILL.md`, `scripts/`,
`references/`, and `assets/` under its own `skills/<name>/`; the shared
plugin-root components; and why each skill is a separate skill (cite the split
assessment from `Step 2 — Doctrine, component fit, and structure`).

For a **multi-phase** skill, show each phase with its name, purpose, inputs,
outputs (manifest path), gate, and code-allowed flag; `SKILL.md` as a <=200 line
orchestrator with the detail in `references/phase-N-<name>.md`; and one manifest
template per phase under `templates/`.

Notes:

- `SKILL.md`: hot-path workflow, safety rules, and operation routing
- `references/CONFIG.md`: first-run setup, full schema, and extended examples
- `scripts/<name>`: deterministic mechanics that should not depend on agent reasoning
- `<other file>`: `<why it exists>`

## 6. Plugin Metadata

**Claude Code plugin-specific — skip this section entirely for a portable/Codex-only
skill**, which has no plugin manifest, lifecycle tier, or group taxonomy.

In a plugin monorepo, a multi-skill plugin lives directly at
`groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/` — the committed folder is the
plugin; there is no separate generated output and no build step.

- **Name:** `<plugin-name>`
- **Lifecycle:** `<stable | beta | alpha | internal>`
- **Standalone:** `<true | false>`
- **Group:** `<domain group>`
- **Dependencies:** `<list of plugin dependencies, or none>`
- **Skills:** `<single: skill-name | multi: skill-1, skill-2, …, skill-N>`
- **Split rationale:** `<why these are separate skills, or "single skill — no split needed">`

## 7. Primitive Components

**Claude Code plugin-specific — skip this section entirely for a portable/Codex-only
skill.** Commands, subagents, hooks, MCP, LSP, and monitors are all Claude Code plugin
components; none of them exist outside a Claude Code plugin, so there is nothing to
decide here for a portable skill beyond "Skill: include."

| Component | Decision | Rationale | Files |
|---|---|---|---|
| Skill | include | Core entry point for activation and workflow. | `SKILL.md` |
| Commands | include/omit | `<why direct invocation helps or is unnecessary>` | `commands/<name>.md` |
| Subagents | include/omit | `<why delegated review/work helps or is unnecessary>` | `agents/<name>.md` |
| Hooks | include/omit | `<deterministic guardrail or omission reason>` | `hooks/hooks.json` |
| MCP | include/omit | `<direct API preferred unless user-approved MCP is needed>` | `.mcp.json` |
| LSP | include/omit | `<language diagnostics value or omission reason>` | `.lsp.json` |
| Monitors | include/omit | `<recurring drift check value or omission reason>` | `monitors/monitors.json` |

For third-party SaaS, websites, and services, prefer direct API scripts or CLIs
over MCP unless the user explicitly overrides that default. If MCP is included,
the `component-fit.mcp-approval` row of `coverage.yml` must be `pass`, with the
user's attestation (server, approver, date) in that row's `evidence` cell -- the
schema is closed, so there is no separate section to add.

## 8. Review Lane Coverage

Each active lane gets one review sub-agent that reviews the entire plugin
(all components, not just SKILL.md) against that lane's criteria. Dispatch via
`skill_review_orchestrate.py prepare` → one sub-agent per manifest lane.

| Lane | Plan decision | Evidence to create |
|---|---|---|
<!-- skill-creator-lane-routing:start -->
| Active lanes | Run the resolver for this repo before filling lane rows. | `python3 <skill_dir>/scripts/skill_review_coverage.py active-lanes --repo-root . --format plan-table` |
| Returned rows only | Copy only rows printed by the resolver into this table. | Completed plan decisions for the active lane set. |
<!-- skill-creator-lane-routing:end -->

## 9. Parallel Work Items

Independent, well-defined work items can be dispatched to sub-agents in
parallel. The host agent reviews alignment after all items complete.

| Work item | Sub-agent scope | Complexity | Depends on |
|---|---|---|---|
| `<script or file>` | `<what to create and key constraints>` | `<standard or high>` | `<dependency or "nothing">` |

Use **standard** complexity for bounded, well-specified items (a single script,
a config file, a reference doc). Use **high** complexity for items that require
cross-file reasoning, architectural judgment, or broad context. The host agent
may use a more capable model for high-complexity items.

Items that depend on nothing can run concurrently. Items that depend on
earlier work (e.g. SKILL.md needs the final component inventory) run after
their dependencies complete. The host agent verifies cross-file consistency
(hooks reference the right scripts, SKILL.md routes to the right references)
and runs validation at the end.

## 10. Verification Plan

Design these checks before implementation. Every included operation from section 4
must map to check IDs; consider all four layers and explain any inapplicable layer.
Scale the detail to the plugin, not to a target number of tests or coverage percentage.

| Check ID / operation | Layer | Risk / case | Command or exact procedure | Expected outcome | Independent evidence / fixture | Environment and cleanup |
|---|---|---|---|---|---|---|
| `<ID / operation>` | unit / contract / integration / eval | `<behavior, failure or claim>` | `<test command / reproducible steps>` | `<observable assertion, including failure output>` | `<section 4.1 source or observed fixture; N/A for local logic>` | `<dependency, credentials, safe target, cleanup or none>` |

- **Unit:** local behavior, nullable/missing/empty inputs, config, preflight failures,
  output and exit codes. For mutations, test approval enforcement, preview/execution
  correspondence and partial-failure accounting.
- **Contract:** validate actual constructed argv/requests against section 4.1's
  independent evidence, including dynamic options and wrapper-injected flags. Check
  response shapes and supported versions. A mock that accepts any call, or repeats
  the implementation's expected spelling, cannot validate an external contract.
- **Integration:** run the actual dependency through the plugin's execution path.
  Specify setup/auth, representative operations, assertions and cleanup. Separate
  credential-free checks (real CLI parsing/help or a local service) from service
  tests that need credentials and a safe target. A mocked transport or `--help` alone
  does not establish that the service operation works.
- **Eval:** record the existing eval-worth decision, proposed scenarios and expected
  behavior; keep model execution subject to the cost and approval policy below.
  No prior baseline does not by itself make eval inapplicable to a new plugin.

Also plan structural/frontmatter checks, links, portability and repository PR checks.
Keep this table as planned work. Record actual outcomes and evidence in the living
review matrix using the procedure in VERIFICATION.md; do not check off skipped tests
as passed or maintain a second result checklist here. <!-- citation -->

### Required Verification Dimensions

Apply these dimensions to the checks above; they are not extra test layers. For each
applicable dimension, identify check IDs and observable assertions. Explain omissions
where the capability is absent. Derive expected behavior from the capability/risk map
and requirements, independently of the implementation and its existing test names.

| Dimension | When it applies and what the checks must establish |
|---|---|
| Execution boundaries | For installed workflows, start in a disposable environment using declared prerequisites and shipped setup instructions, without relying on undeclared ambient credentials, maintainer paths or personal agent rules. Exercise setup → child process → dependency, including environment/config propagation. Cover platform-specific paths for claimed OS/runtime support and inspect actual resolved dependency versions. |
| Scope and isolation | For hooks, stateful workflows or mutations, seed unrelated sessions, files and resources and assert they remain unaffected outside the declared scope. Exercise hook activation and state cleanup where applicable, plus allowed operations that must remain allowed. Inspect actual writes, staged files, requests and diagnostic/audit output; synthetic secret canaries must not appear in exposed artifacts. |
| Adversarial and recovery cases | For parsers, guardrails, external data and multi-step operations, test bypass variants as well as false positives: alternative command forms, hostile quoting/substitution, misleading identifiers or paths, malformed responses, failures, retries and cleanup. Verify effects and residual state, including duplicate prevention where retries could repeat a mutation; a few passing mutation controls do not establish complete enforcement. |
| Behavioral invariants | For each promised behavior, name what must always hold or never happen: exact target identity, configured limits and precedence, preview/execution agreement, preservation of unrelated work, related policy dates, or assessment of the version actually installed. Assert these outcomes across applicable normal and failure cases. A schema-valid request to the wrong resource is a failure. |

Record ordinary documented setup and authorization separately from operator repairs.
A run rescued by undeclared environment fixes, manual path substitution or personal
instructions compensating for unsafe behavior is not a pass for the shipped workflow.
Record the intervention and affected check, fix the shipped instructions/code, then
rerun that path. Apply VERIFICATION.md's existing failed/blocked outcome rules.

During review, independently derive missing cases from the intended capabilities and
risk map before comparing them with the author's tests. Reject a plan that cannot
observe its relevant failure modes. If a check exposes a design that cannot reliably
keep its claimed scope or safety guarantees, revise the design rather than accepting
successful happy-path tests as sufficient evidence.

### Eval Decision

**Evaluating whether the change is actually better?** Use the `eval` skill
(`Global/plugin-lifecycle`) — `plugin-creator` depends on it — via `/eval-plan`, `/eval-run`,
`/eval-compare`, `/eval-view`. This is how a plugin's unprovable trigger gets evidence.
Recommend it after a meaningful behavior change; skip it for routine edits. **It spends real
model tokens — say so and give a number before running it**, grounded with
`eval plan --calibrate <prior benchmark.json>` rather than guessed. Approval gate and artifact
contracts: the eval skill's `references/EVALS.md`.

Eval-worth decision: `<automated-run planned / manual-smoke-only planned / skipped / not-applicable>`,
with rationale, scenario/check IDs and required approval. Planned execution is not
actual evidence; the existing `eval` block in coverage.yml records what ran.

## 11. Open Decisions

List only decisions the user must make before implementation:

1. Install location: global/workspace/shared repo
2. Supported operations: `<choice>`
3. Approval posture: `<choice>`
4. Config format: `<choice>`

## 12. Key Design Decisions

Every line here is presented to the user and needs approval before implementation.

- **Skill name:** lowercase, hyphens, 1-64 chars
- **Implementation language:** for a portable/Codex-only skill, pick whatever
  language fits the scripts — no am-pm language-SET constraint applies. **Claude
  Code plugin-specific (am-pm monorepo), skip for a portable skill:** a plugin's
  languages are a SET, not a choice — Python, TypeScript, or BOTH, plus optional
  POSIX shell (`.sh`) helpers; no other language. Two plugins joined by a bundle
  `dependencies` list is still the recommended default: reach for one
  multi-language plugin only when the halves are genuinely one capability that
  cannot be installed separately. Inside the am-pm monorepo see
  MONOREPO_PLACEMENT.md for what each language costs at the gate.
- **Config file format and name**, for example `.tool-name.json`
- **Supported operations**
- **Approval tiers:** what is read-only/no-approval, what runs under one bounded
  approval, and what needs fresh approval
- **Enforcement:** whether high-risk approval controls are runtime-enforced,
  prompt-only, or deferred with documented residual risk
- **Storage location:** global, workspace, or shared repo (**Claude Code
  plugin-specific, skip for a portable skill:** inside the am-pm monorepo this is
  decided by taxonomy placement — see MONOREPO_PLACEMENT.md)
- **Optional plugin components** (**Claude Code plugin-specific — skip entirely
  for a portable/Codex-only skill**, which has none of these): skill, commands,
  subagents, hooks, MCP, LSP, and monitors — why each selected component helps,
  and why each omitted one is not needed
- **MCP posture** (**Claude Code plugin-specific, skip for a portable skill**):
  prefer direct API scripts or CLIs for third-party SaaS, websites, and services
  unless the user overrides that default; include MCP only with auditable user
  attestation that the server is security-approved for company use
- **Capability risk profile:** sensitive data the skill can read, destructive or
  privileged actions it can perform, production/customer-data exposure, mitigations,
  and intentionally omitted risky features
- **Backward compatibility** expectations for existing configs, scripts, CLI flags,
  outputs, and documented workflows
- **Portability:** which defaults hold for every instance of the target service, and
  which values must come from setup, config, discovery, or CLI flags
- **Relevance** (**Claude Code plugin-specific, skip entirely for a portable
  skill** — Codex and the Agent Skills standard have no proactive-suggestion
  mechanism): what work this plugin is relevant to, or why no signal fits and
  none is declared (see RELEVANCE.md)

## Approval

This plan has been saved at `<plan-path>`. Please approve, revise, or reject it.
Approve the design sections first — that sets the status above to `design-approved`
and unblocks writing sections 5, 9 and 10, which are then presented for the second
approval and set `plan-approved`. I will not create or modify target skill/plugin
source until this saved plan is `plan-approved`.
````

## Scaling Guidance

For a small local-only skill, keep each section to one or two bullets and mark
non-applicable lanes as `N/A` with a reason. For an external-resource or
high-risk skill, expand the operations map, approval tiers, config setup, and
verification plan enough that the user can see exactly what will happen after
approval.

Use concrete names where they are portable. Use placeholders where a value is
instance-specific, sensitive, or user-owned.
