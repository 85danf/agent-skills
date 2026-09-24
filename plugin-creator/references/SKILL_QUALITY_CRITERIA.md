# Skill Quality Criteria

Generated from `assets/skill-quality-criteria.json`. Do not edit by hand.

The lanes are used in both phases: use author guidance while creating or refactoring a skill, then use review prompts while filling the review coverage matrix.

The agent must explicitly open and read the relevant generated lane reference files before applying lane guidance; lane content is not automatically populated into agent context. The JSON is the source for generating this index, the lane references, and review prompts.

## Pre-Screen

Authoring: Use this lane before authoring or updating a skill to verify none of the six critical-fail conditions are present.

Review: Dispatch this lane first and halt all other review lanes if any criterion fires. These conditions make the skill undiscoverable, unsafe, or unreliable regardless of other quality scores.

### Examples

- Good: Description names a specific action and trigger scenario; all side-effecting operations require explicit user approval; scripts run non-interactively; all non-standard dependencies are documented; consequential operations have concrete verification commands; SKILL.md is inside its character budget and every reference is a leaf or an index over its own subdirectory.
- Bad: Description says 'Helps with database stuff'; skill auto-triggers and deletes records without an approval gate; a required Python package is not mentioned anywhere; no way to confirm a deployed change succeeded; SKILL.md runs past 25,000 characters and a reference sends the reader sideways to a sibling for a required step.

### `pre_screen.undiscoverable-description` - Description is specific and discoverable

Author guidance: MUST write a description that answers all three: what does this skill do (specific action, not a domain label), when should the agent invoke it (concrete trigger scenario), and what keywords would a user naturally say. A vague description makes the skill undiscoverable — no other quality dimension matters if the skill never activates.

Review prompt: Check that the description answers all three: (1) what does this skill do — a specific action, not a domain label; (2) when should the agent invoke it — a concrete trigger scenario; (3) what keywords would a user naturally say. Fail if any answer is unclear. This is a blocking condition.

### `pre_screen.side-effecting-auto-trigger` - Side-effecting skills have explicit approval gates

Author guidance: If the skill performs destructive or irreversible actions (deploys, file overwrites, sends messages, deletes resources), OR actions that accept risk on the user's behalf or weaken a safety or security control (suppressing scanner findings, disabling or bypassing a CI gate, adding an allow/ignore entry, loosening permissions), AND is auto-invocable (no disable-model-invocation: true), it MUST have at least one explicit user-approval gate before each such action. Otherwise, mark the skill manual-only via disable-model-invocation. When the skill's core purpose is to grant such an exception, prefer disable-model-invocation: that decision needs deliberate human intent.

Review prompt: Check whether the skill performs writes, deletes, deploys, sends, other side effects, OR actions that accept risk or weaken a safety/security control (suppressing scanner findings, disabling a gate, adding an allow/ignore entry, loosening permissions). If it does and it is auto-invocable, verify there is at least one explicit approval gate before each such action, or that the skill is marked disable-model-invocation. Fail if such an auto-trigger skill lacks gates. This is a blocking condition.

### `pre_screen.interactive-scripts` - Scripts are non-interactive

Author guidance: Scripts in scripts/ MUST NOT require TTY interaction — no stdin prompts, interactive menus, or password prompts without a non-interactive fallback. Agents cannot interact with TTY prompts. Provide --yes, --non-interactive, or equivalent flags for any step that would block.

Review prompt: Check each script for input(), read -p, select, interactive menus, or password prompts without a --yes or --non-interactive fallback. Fail if any script blocks on TTY input. This is a blocking condition.

### `pre_screen.implicit-dependencies` - Required dependencies are documented

Author guidance: Every non-standard dependency (Python packages, CLI tools, API keys, running services) MUST be documented in prerequisites or the preflight script. Standard OS utilities (git, curl, python, node, npm, pip) do not need documentation. A missing dependency that crashes silently on a clean machine is a critical failure.

Review prompt: Check whether the skill requires non-standard packages, CLI tools, API keys, or running services that are not documented in prerequisites or preflight. Standard utilities (git, curl, python, node, npm, pip) are exempt. Fail if any required non-standard dependency is undocumented. This is a blocking condition.

### `pre_screen.no-verification` - Consequential operations have verification

Author guidance: If the skill generates code, modifies configs, deploys, or creates infrastructure, it MUST include at least one concrete verification command or check that confirms the output is correct. 'Make sure it looks right' does not count — verification must be operational (a command to run, an assertion to check, a file to inspect).

Review prompt: Check whether the skill performs consequential operations (generates code, modifies configs, deploys, creates infrastructure). If so, verify at least one concrete command or check confirms the output is correct. 'Review the output' is not sufficient. Fail if consequential operations have no operational verification. This is a blocking condition.

### `pre_screen.bloated-body` - SKILL.md is within its size limit and references do not chain

Author guidance: SKILL.md size is authoritative in CHARACTERS (see references/SKILL_SPEC.md) and is the ONLY size budget — reference files have none, in lines or characters. A reference MUST NOT depend on a sibling reference as a dependency chain — "read A to learn you must then read B to do the work" takes two decisions to reach the content, so the odds it arrives are squared. Two sibling links ARE legal: a citation, which only says where a fact lives and is marked `<!-- citation -->` on its line, and an index link, where a parent links down into its own subdirectory. When a reference grows too long to read in one pass it becomes an index over leaves; it does not link sideways.

Review prompt: Check SKILL.md is within the character limits in references/SKILL_SPEC.md; reference files have no size budget, so do not judge one by its length. Check no reference DEPENDS on a sibling: a sibling link is legal only as a marked citation (`<!-- citation -->`, stating where a fact lives) or as a parent indexing down into its own subdirectory. Apply the test: if the agent never follows this link, does the work still complete? Yes means citation; no means dependency, which fails. `scripts/quick_validate.py` decides all of this mechanically — run it rather than judging by eye.

## Genericity

Authoring: Use this lane while making generic/shared plugins work across repos and organizations.

Review: Use this lane while reviewing whether a generic/shared plugin avoids creator-local defaults and assumptions.

### Examples

- Good: Configure service URLs, profile names, environments, queues, and credential environment variables in a project config file; scripts accept explicit profile arguments and discover available labels when possible.
- Bad: Default to one workplace's production profile, read a user-specific absolute path, or assume one release branch.

### `genericity.runtime-vocabulary` - Runtime vocabulary is generic

Author guidance: Make profile names, environments, queues, teams, tenants, workflow labels, field names, URLs, credential names, and other runtime vocabulary configurable, discoverable, CLI-provided, or obvious placeholders.

Review prompt: Check that profile names, environments, queues, teams, tenants, workflow labels, field names, URLs, credential names, and other runtime vocabulary are configurable, discoverable, CLI-provided, or obvious placeholders instead of local defaults.

### `genericity.no-local-assumptions` - No local assumptions leak into behavior

Author guidance: Do not bake organization-specific identifiers, paths, naming conventions, status services, repository hosts, branches, projects, dashboards, or workflow rules into behavior.

Review prompt: Check for organization-specific identifiers, paths, naming conventions, status services, repository hosts, branches, projects, dashboards, or workflow rules that would only work for the creator's machine or workplace.

## Installed Use

Authoring: Use this lane while designing installed-user packaging, defaults, shipped files, and compatibility.

Review: Use this lane while reviewing whether installed users can run the skill without missing files or broken contracts.

### Examples

- Good: Ship the preflight script, config loader, schemas, references, and fixtures needed for normal and recovery workflows inside the skill directory.
- Bad: Tell installed users to follow a parent-repo wiki page or call a sibling-repo script that is not included with the installed skill.

- Good: Preserve existing config keys, CLI flags, output contracts, generated files, and documented workflows, or document and test a migration.
- Bad: Rename existing config keys and CLI flags without compatibility tests or migration guidance.

### `installed-use.self-contained-runtime` - Runtime is self-contained

Author guidance: Keep required happy-path and recovery-path workflows inside the skill directory, including scripts, references, assets, schemas, and templates.

Review prompt: Check that installed users can run required happy-path and recovery-path workflows from the skill directory without relying on sibling repo docs, unrelated skills, or external review prompts.

### `installed-use.installed-compatibility` - Installed-user compatibility is protected

Author guidance: Preserve existing config keys, CLI flags, output contracts, generated files, scripts, and documented workflows unless a breaking migration is explicit and tested.

Review prompt: Check that existing config keys, CLI flags, output contracts, generated files, scripts, and documented workflows are preserved or explicitly migrated with compatibility tests.

## Context Engineering

Authoring: Use this lane while writing SKILL.md and references so default-loaded context stays high value.

Review: Use this lane while reviewing a diff for context bloat, weak routing, avoidable token consumption, or confusing duplicated guidance.

### Examples

- Good: SKILL.md contains workflow, safety, and routing. A reference file that covers 7 components is split into COMPONENTS.md (always read during component-fit) and components/*.md (read only for relevant components). Each level loads only what the agent needs.
- Bad: Load all 7 component field tables into SKILL.md or a single reference file. The agent reads thousands of tokens of hook event details when it only needs the MCP recipe.

- Good: For high-volume logs, diffs, search results, or eval outputs, provide compact defaults, filters, field allowlists, caps, or staged reference loading to control token usage with clear quality, safety, recall, or coverage justification.
- Bad: Dump every returned field, full transcript, complete search result, or broad exploration trace by default without filters, allowlists, caps, or staged loading.

- Good: Ship the config schema once as templates/config-template.yml and link to it from SKILL.md with a 'when configuring, copy templates/config-template.yml' trigger.
- Bad: Paste the full config schema inline in SKILL.md and also ship templates/config-template.yml, so the two copies drift apart.

### `surface.high-usage-skill-md` - SKILL.md contains high-usage context

Author guidance: Keep default-loaded SKILL.md context likely to help most invocations; move first-run setup, rare troubleshooting, full schemas, historical notes, and deep examples into referenced files.

Review prompt: Check that the main SKILL.md contains only context likely to be used in most skill invocations. Move first-run setup, rare troubleshooting, full schemas, historical notes, and deep examples into referenced files.

### `surface.preflight-config-routing` - Config failures route to references

Author guidance: When setup or configuration is the likely fix, route agents from SKILL.md, preflight output, and config errors to the relevant reference instead of embedding full setup details in default context.

Review prompt: Check that SKILL.md and preflight/config error output point to the relevant configuration reference when setup or configuration is the likely fix.

### `context.progressive-disclosure` - Details are progressively disclosed

Author guidance: Position content by reusability: how often it is needed relative to the number of times the skill is invoked. High-reuse content (workflow, safety rules, operation routing) belongs in SKILL.md. Lower-reuse content (full schemas, rare operations, setup depth) belongs in references/. Within references, split long files into a parent index and sub-files in a folder when sections have different reuse frequencies. Sub-files belong to their parent, not to SKILL.md. Every reference link in SKILL.md and in parent index files must include a 'when to read' trigger — write the link as a conditional ('when X, read Y') so the agent can skip irrelevant references.

Review prompt: Check that content is positioned by reusability: high-reuse in SKILL.md, lower-reuse in references/. Check that long reference files are split into parent + sub-files when sections have different reuse frequencies. Check that every reference link includes a 'when to read' trigger so the agent knows when to skip it. Flag links that say 'see X' without stating when X is relevant.

### `context.token-economy` - Token-heavy paths are controlled or justified

Author guidance: For service, workflow, review, eval, exploration, and generated-output skills likely to consume high context through broad file reads, large diffs, logs, schemas, transcripts, search results, API responses, or eval artifacts, add token-control measures such as filters, allowlists, caps, compact formats, staged reference loading, grep/find patterns, summary-first output, explicit exploration boundaries, and stop conditions. If high token use is intentional because it improves quality, safety, recall, or coverage for this skill, state that trade-off and cite eval, benchmark, smoke-test, or creator-provided evidence when available.

Review prompt: Check whether anticipated or observed high-token paths across service, workflow, review, eval, exploration, and generated-output skills have token-control measures such as filters, allowlists, caps, compact formats, staged reference loading, grep/find patterns, summary-first output, explicit exploration boundaries, or stop conditions. If they do not, check that the creator explicitly justifies the token cost with a quality, safety, recall, or coverage benefit and includes eval, benchmark, smoke-test, or creator-provided evidence when available.

### `context.no-duplicated-criteria` - Criteria are not duplicated by hand

Author guidance: Keep quality criteria in the canonical criteria source and generated references; hand-written docs may route to criteria but must not restate them as a second source.

Review prompt: Check that quality criteria are not duplicated by hand across SKILL.md, checklists, verification docs, generated agents, or review prompts.

### `context.single-source-content` - Shipped templates and references are the single source

Author guidance: When content is authored once as a shipped template, asset, or reference example, reference it by path (with a 'when to read' trigger) from SKILL.md and other docs instead of pasting a second copy, because duplicated content drifts as one copy is updated and the other is forgotten. This generalizes the no-duplicated-criteria rule to all shipped content. Cross-document references of this kind are citations, not dependency chains: mark the line `<!-- citation -->` so the check can tell them apart, and phrase the pointer as a condition for reading ("read this when you need the factor weighting"), never as a topic ("see hooks.md for more on hooks").

Review prompt: Check that content shipped as a template, asset, or reference file is referenced by path rather than duplicated inline in SKILL.md or other docs. Flag inline copies of a bundled template or reference block; the shipped file should be the single source.

### `context.signal-noise-ratio` - Every instruction passes the signal-noise filter

Author guidance: For each section or instruction in SKILL.md and references, apply the four-question filter before keeping it: (1) Would the agent ask about this if it were missing? If no, it is noise — remove it. (2) Could the agent discover this by reading existing repo files? If yes, it is noise — the agent would pay twice and the instruction goes stale. (3) Does this change frequently? If yes, it is noise — stale context poisons more than no context. (4) Is this a standard convention the model already knows? If yes, it is noise — only document project-specific deviations. Apply the 3-zone layout to the final SKILL.md: top 15% for security constraints, NEVER/ALWAYS rules, and hard architectural decisions; middle 70% for patterns, examples, and stack definitions; bottom 15% for executable commands, workflow triggers, and verification checklists.

Review prompt: Check whether instructions in SKILL.md and references pass the four-question signal-noise filter: (1) Would the agent ask about this if missing? (2) Could the agent discover this from repo files? (3) Does this change frequently? (4) Is this a standard convention the model already knows? Flag sections that are noise by these tests. Also check that critical constraints and NEVER/ALWAYS rules are in the top 15% of the file, not buried in the middle.

### `context.examples-are-effective` - Examples are effective

Author guidance: Use examples that are relevant to real use, diverse enough to avoid accidental overfitting, clearly delimited from instructions, and placed in references when they are deep, rare, or lengthy.

Review prompt: Check that examples are relevant, diverse enough to avoid accidental overfitting, clearly delimited from instructions, and placed in references when deep, rare, or lengthy.

## Component Fit

Authoring: Use this lane during skill planning to decide whether supported am-pm plugin components should supplement the core skill.

Review: Use this lane while reviewing whether selected components are justified and omitted components were considered.

### Examples

- Good: Keep a skill-only primitive when scripts and references are enough; add a command only for a frequent explicit workflow and a hook only for deterministic guardrails.
- Bad: Add MCP, hooks, monitors, and subagents to every new skill because they are available.

- Good: For SaaS integrations, use direct API scripts by default and include MCP only when the user explicitly requests it and attests it is security-approved for company use.
- Bad: Choose MCP for a third-party service without an auditable approval statement or when a simple tested API script would be clearer.

### `component-fit.justified-components` - Selected components are justified

Author guidance: For each selected component, state its aim in one line, what it buys that the alternatives do not, and what it costs. Justify it against its nearest neighbour, not in isolation — a trigger is a skill (semantic, the model decides) or a hook (an event decides); noticing something is a monitor (external, continuous), a hook (a session event), or an on-demand check; capability is a script/CLI or MCP; isolation is a subagent or inline work. Valid reasons include trigger reliability and context economy, not only drift control, consistency, guardrails, ergonomics, observability, and reusable runtime tooling.

Review prompt: For each selected component, check the artifact names its aim, the advantage over its nearest alternative, and the cost accepted. Flag any component justified only by restating what it is, or justified in isolation without comparison to the neighbour that would also work.

### `component-fit.intentional-omissions` - Omitted components are intentional

Author guidance: Skill-only is the expected outcome, not a gap. When a component might seem relevant but is omitted, name the cost it would have imposed — context consumed, latency per call, a dependency, a server to trust, a gate that cannot be verified by inspection — rather than only asserting it is not needed.

Review prompt: Check omissions are recorded with the cost avoided, not a bare "not needed". Do NOT treat a skill-only design as incomplete; flag the opposite — a component added without a cost being weighed.

### `component-fit.mcp-approval` - MCP usage is approved and auditable

Author guidance: Prefer direct API scripts for third-party SaaS, websites, and services. Include MCP only when justified or user-requested, and require explicit user attestation that the MCP server is security-approved for company use.

Review prompt: If .mcp.json is included, check that direct API usage was considered and that the review artifact contains explicit auditable evidence that the user said the MCP server is security-approved for company use.

### `component-fit.enforce-over-instruct` - Deterministic enforcement is preferred over prompt rules

Author guidance: Prefer hooks, LSP, scripts, or CI gates for checks that can be deterministic. Reserve prompt-only rules for judgment calls that cannot be scripted. A behaviour the design GUARANTEES is not guaranteed while it rests on a description: a 90%-compliant model is not a control. The rule cuts the other way too — do not reach for a hook when the injected content never changes (that is CLAUDE.md or a skill, however cleanly the moment names itself) or when recognising the trigger needs judgement. Most plugins name no moment worth hooking, and that is the expected answer. For a guardrail that should apply only while one skill runs, declare a `hooks:` block in that skill's SKILL.md frontmatter (scoped to the skill, fires only while it is active) instead of an always-on plugin hook (see references/components/hooks.md).

Review prompt: Check deterministic checks use hooks, scripts, or validators rather than prompt-only instructions. Flag a guarantee ("always", "never", "every time") resting only on a skill description when a deterministic alternative exists. Also flag the reverse — a forced hook: one whose trigger the design cannot name in a sentence, one whose injected content is static (that is CLAUDE.md or a skill, not a subprocess), or one on an event that cannot act on what it sees (only 11 events carry additionalContext; Setup, InstructionsLoaded and StopFailure discard JSON output entirely). A guard hook shipped without a documented negative test — a command it must refuse — is unverified: hooks fail open, and a broken one still looks configured.

## Runtime Contracts And Tests

Authoring: Use this lane while creating scripts, CLI behavior, config contracts, output formats, and tests.

Review: Use this lane while reviewing whether documented behavior is enforced by deterministic runtime behavior and tests.

### Examples

- Good: Merge a validate-config, check-credentials, and verify-connectivity sequence into one preflight script that reports all results in a single agent step.
- Bad: Have the agent call three separate scripts sequentially, parse each output, decide whether to continue, and handle errors at each step.

- Good: Document a command's flags, config lookup, exit codes, stdout or file output shape, and dry-run behavior, then enforce those contracts with deterministic positive and negative tests.
- Bad: Tell the agent to inspect configuration manually, infer valid arguments from prose, and summarize output without stable schemas, exit codes, or tests.

- Good: When updating a config or policy file that may already exist, read the current file, merge the new entries in, write the result, then run a check that every prior entry still exists (count or key diff) before reporting success.
- Bad: Overwrite an existing config or policy file with only the new entries, silently dropping whatever the user already had.

### `runtime.cli-and-config-contracts` - CLI and config contracts are enforced

Author guidance: Document flags, config schemas, setup paths, credential lookup, and parser behavior, then enforce them with deterministic script behavior and focused tests. Before implementing operations that depend on an external CLI, API, library or host behavior, record dependency identity, tested version/supported range, relevant contracts and primary-source or reproducible observation evidence in the plan. Validate the actual constructed argv/requests and response shapes against that independent evidence, including dynamic and wrapper-injected options. Imported scripts, copied docs and mocks derived from the implementation do not establish the external contract. Verify installation/authentication and reject unresolved or invented interfaces. Preflight must detect missing dependencies and route to evidenced setup steps.

Review prompt: Check that external contracts used by the changed operations have independently sourced, versioned evidence in the plan: dependency identity, installation/authentication, commands/flags or endpoints, response shapes and support assumptions. Inspect the actual argv/request paths, including dynamic/injected options, and the contract test oracle. Fail if tests only repeat locally invented contracts or accept every mocked call. Imported source gets the same burden as new code; an unsupported interface is not excused by missing credentials. Verify config and dependency preflight behavior.

### `runtime.output-contracts` - Output contracts are stable

Author guidance: Document and test machine-readable output, generated file formats, stdout/stderr conventions, and exit codes used by downstream agents, scripts, CI, or users.

Review prompt: Check that machine-readable output, generated file formats, stdout/stderr conventions, and exit codes are documented and tested where downstream agents, scripts, CI, or users rely on them.

### `runtime.safe-file-mutation` - Edits to existing files merge and are verified

Author guidance: When a skill writes to a file that may already exist (config, policy, lockfile, generated output), design the write as a merge that preserves prior entries rather than a blind overwrite, and add an operational check that confirms nothing pre-existing was dropped, for example comparing entry/key counts before and after or diffing against `git show HEAD:<file>`. Skills that only create fresh files or emit transient output do not need this.

Review prompt: If the skill writes to a file that can already exist (config, policy, lockfile, generated output), check that the write merges rather than clobbers and that an operational check confirms pre-existing content was preserved. Flag blind overwrites of user or shared files. Not applicable to skills that only create new files or emit transient output.

### `runtime.deterministic-tests` - Deterministic tests cover risk

Author guidance: Plan operation-specific unit, contract, integration and eval checks before implementation, with commands/procedures, expected outcomes, evidence sources, environment and cleanup; explain inapplicable layers. Cover safety, nullable/missing/empty inputs, parser, config, output and preflight failure paths without requiring live credentials by default. Mutation tests must establish approval enforcement, preview/execution correspondence and partial-failure accounting. A coverage percentage alone does not establish operation correctness; use a deliberately invalid contract case to prove the external checker rejects that defect class. Map the verification dimensions already recorded in the plan to checks derived from intended capabilities and risks, explaining inapplicable dimensions. Their definition belongs to PLAN_TEMPLATE.md section 10.

Review prompt: Check that each included or changed operation maps to concrete planned checks and expected outcomes. Verify deterministic coverage of realistic input and failure shapes, and for mutations approval enforcement, preview/execution correspondence and partial-failure accounting. Inspect independent contract evidence and a negative control that proves the checker can reject an invalid interface. Fail generic test/coverage checklists that cannot observe the relevant defect. Do not require live credentials for unit or offline contract checks. Independently derive cases from the capability/risk map before comparing with authored tests; check applicable dimensions and intervention evidence, including whether operator repairs conceal a failing shipped workflow. Require design correction when evidence exposes an unenforceable scope or safety claim.

### `runtime.agent-step-economy` - Agent surface is minimized

Author guidance: The agent surface is the number of steps the agent must perform to achieve a goal — each step is a reasoning decision that can go wrong. Minimize it: merge multiple script calls into one orchestrating script when possible, move repeatable logic into deterministic scripts, and keep the agent workflow short and linear.

Review prompt: Check that the agent surface is minimized: repeatable logic lives in scripts, multiple sequential script calls are merged where practical, and the agent workflow has the fewest reasoning steps needed. Flag unnecessary agent branching that a script could handle.

### `runtime.live-validation` - Live validation is explicit

Author guidance: Exercise the actual dependency through the plugin and record observed integration results, separately from mocked tests and skill discoverability. Alpha may remain explicitly integration unverified only when required unit and independently grounded contract checks pass and live testing lacks credentials, service access or a safe target. Record affected operations and blocked/skipped evidence without claiming pass. An observed integration failure or unsupported contract must be fixed or the capability removed before merge. Test safe reads/sandbox mutations only within authorization, with assertions and cleanup; contract validity alone does not prove service-side effects.

Review prompt: Check actual dependency/service integration evidence and distinguish it from mocks, preflight and skill-trigger invocation. If live access is unavailable, verify required unit and independent contract checks pass, affected operations are named, and alpha acceptance explicitly says integration unverified. Keep the unverified row fail with blocked/skipped evidence; do not call it pass or na because access is missing. Fail acceptance of observed integration failures, invented contracts, or use of the alpha exception for other lifecycles without repository policy. Verify mutation assertions and cleanup when exercised.

### `runtime.eval-consideration` - Eval need is considered

Author guidance: Consider eval coverage for high-usage, shared, risky, or behavior-sensitive skill changes; disclose token/time cost before automated evals and record manual smoke evidence when evals are not useful. Use the high-reliability eval loop only after the user has approved the created or revised skill as worth deeper validation. Reserve A/B comparison for meaningful behavior changes such as trigger wording, workflow ordering, bundled scripts, output contracts, or quality/reliability changes, not routine edits.

Review prompt: Check that high-usage, shared, risky, or behavior-sensitive skill changes consider eval coverage. The author should either add or update eval evidence, record a manual smoke-test result, or explain why evals are not useful yet. Automated evals should not be required by default; token/time cost must be disclosed to the user before automated evals, automated evals should be reserved for high-value skills or high-risk changes, and manual smoke testing should be acknowledged where relevant. If automated evals ran, the review file must summarize quality, trigger, regression, comparison, failed-case, and token/time metrics where applicable and link the committed benchmark/metrics artifacts. Confirm the high-reliability eval loop was used only after the user approved the created or revised skill as worth deeper validation, and that A/B comparison was reserved for meaningful behavior changes, not routine edits.

### `runtime.shared_repo_pr_parity` - Shared-repo pre-PR parity is achieved

Author guidance: When the skill ships in a shared repository, run the host repo's canonical pre-PR command (for example `am-pm ci pr-check --base-ref <merge-target>`) and confirm exit code 0 before declaring the change complete. Record the command and observed exit code in the review evidence.

Review prompt: Check that the change is verified against the host repository's canonical pre-PR command (for example `am-pm ci pr-check`) with exit code 0 recorded in the review evidence, not only inner-loop validators such as `validate skill` or `validate repo` alone.

### `runtime.state-management` - Workflow state is tracked explicitly

Author guidance: For small in-session tasks, use in-prompt checklists or the Task tool. For multi-step workflows and plans, use committed state files (review matrices, coverage checklists, phase manifests) driven by scripts or hooks. For multi-phase skills, each phase MUST write its output to a committed manifest file before the next phase begins — the manifest is the explicit handoff contract and prevents lost progress across phase boundaries. Choose the lightest mechanism that prevents lost progress.

Review prompt: Check that multi-step workflows have explicit state tracking — checklists, committed files, or Task tool usage — proportional to the workflow's complexity. For skills with phase-gated workflows, verify each phase writes a manifest before the next phase can start. Flag workflows that rely on memory alone for state that could be lost on compaction.

## Repository Integration

Authoring: Use this lane while updating repo-facing docs, changelog fragments, review evidence, validators, and CI expectations.

Review: Use this lane while reviewing whether the repository metadata and validation surface match the skill change.

### Examples

- Good: When a skill adds a config field or workflow, update catalog docs, design docs, CONFIG references, tests, and the linked review coverage artifact.
- Bad: Change the skill interface while README examples, design docs, validators, and review evidence still describe the old behavior.

- Good: When a new requirement applies broadly, update the shared validator, schema, docs, and regression tests.
- Bad: Add a one-off repo-check exemption for a skill because the shared validator does not yet understand the new requirement.

### `repo.catalogs-and-docs` - Catalogs and docs are aligned

Author guidance: Update README.md, SKILLS.md, AGENTS.md, design docs, CONFIG.md, and repo-facing examples when the skill change makes them stale.

Review prompt: Check README.md, SKILLS.md, AGENTS.md, design docs, CONFIG.md, and repo-facing examples for stale references or missing updates caused by the skill change.

### `repo.changelog-and-pr` - A changelog fragment exists only when the host repo's gate owes one

Author guidance: Never decide on your own judgement that a PR owes a release note. After committing, run the host repo's changelog gate (am-pm: `am-pm changelog-gate --base-ref <merge-target>`) and do exactly what it prints: it says a fragment is owed, and what it must answer, or prints nothing. A plugin under `groups/` owes none unless the gate asks.

Review prompt: Check that a changelog fragment was added only where the host repo's gate would ask for one (am-pm: the diff touches the ambassador contract or a declared tier-2 surface; an ordinary plugin under `groups/` is neither). A fragment on a not-applicable diff is a defect, and so is a missing one where the gate fires.

### `repo.validation-alignment` - Validation stays aligned

Author guidance: Update shared validators, pre-commit, tests, and CI expectations for new requirements instead of adding skill-specific exceptions when a shared rule is appropriate.

Review prompt: Check that repo validators, pre-commit, tests, and CI expectations cover the new requirement without adding skill-specific exceptions where a shared rule is appropriate.

## Capability, Data, And Approval Risk

Authoring: Use this lane while documenting what a skill can read, mutate, expose, omit, and how risky operations are approved or enforced.

Review: Use this lane while reviewing sensitive, destructive, external-resource, or privileged capability changes.

### Examples

- Good: Classify read, write, delete, publish, deploy, restart, exec, external-message, and sensitive-export operations by approval tier, and enforce dry-run or confirmation controls where practical.
- Bad: Let the skill perform destructive or external mutations while only saying the agent should be careful.

- Good: Report credentials as set or missing, redact sensitive values in logs and artifacts, scope generated prompts, and document any residual prompt-only risk.
- Bad: Echo tokens, commit production logs or customer data, or leave generated diff prompts containing secrets in tracked files.

### `risk.capability-profile` - Capability risk is explicit

Author guidance: State what the skill can read, write, delete, publish, deploy, restart, exec, trigger, expose, and intentionally omit.

Review prompt: Check that the skill states what it can read, write, delete, publish, deploy, restart, exec, trigger, expose, or intentionally omit.

### `risk.approval-and-enforcement` - Approval and enforcement are appropriate

Author guidance: Classify external writes, destructive actions, privileged operations, sensitive exports, risk-accepting actions that weaken a safety or security control (for example suppressing scanner findings or disabling a gate), and out-of-scope actions with an appropriate approval tier and deterministic enforcement where practical.

Review prompt: Check that external writes, destructive actions, privileged operations, sensitive exports, risk-accepting actions that weaken a safety or security control (for example suppressing scanner findings or disabling a gate), and out-of-scope actions require an appropriate approval tier and deterministic enforcement where practical.

### `risk.secrets-and-data` - Secrets and sensitive data are protected

Author guidance: Protect credentials, customer or production data, logs, diagnostics, generated artifacts, and residual prompt-only risks through redaction, scoping, and clear constraints.

Review prompt: Check credential handling, redaction, customer/production data exposure, logs, diagnostics, generated artifacts, and residual prompt-only risks.

## Review Process Quality

Authoring: Use this lane while preparing review coverage, fresh-agent readback evidence, and completion checks.

Review: Use this lane while reviewing whether the review itself is complete, diff-bounded, and supported by evidence.

### Examples

- Good: Complete every matrix row with pass, fail, or na plus concrete evidence such as tests run, artifacts checked, reviewer attribution, and fresh-agent readback when the workflow changed.
- Bad: Leave rows as not-reviewed, write evidence such as looks good, or treat one self-review as enough for a major agent-facing rewrite.

- Good: Keep findings limited to the changed files and realistic blast radius, and explain any skipped readback or live validation.
- Bad: Use the review to rewrite unrelated historical docs or raise style findings outside the diff.

### `review.fresh-agent-readback` - Fresh-agent readback is considered

Author guidance: For a new skill, substantial rewrite, or agent-facing workflow change, run or explain an isolated comprehension readback by a fresh agent.

Review prompt: Check whether a new skill, substantial rewrite, or agent-facing workflow change needs an isolated comprehension readback, and whether any skip is explained.

### `review.diff-bounded-findings` - Findings are diff-bounded

Author guidance: Keep review findings limited to the diff and realistic blast radius; avoid unrelated style churn or historical rewrites.

Review prompt: Check that review findings are limited to the diff and its realistic blast radius, with no unrelated style churn or historical rewrites.

### `review.matrix-complete` - Coverage matrix is complete

Author guidance: Before completion, decide each applicable criterion with concrete evidence and reviewer attribution; scope unaffected rows according to repository policy. Link planned check IDs to actual commands, observations and evidence artifacts in the living matrix; keep the plan as intended work. Distinguish passed, failed, blocked and skipped checks using the existing schema. A complete review is not an all-pass result. Initialize provenance before source edits without erasing prior evidence, preserve known provenance during migration, and use unknown rather than guessing how imported code was created.

Review prompt: Check that review evidence links intended checks to actual results, records blocked/skipped checks honestly, and does not treat planning or a coverage percentage as proof. Verify creation/update provenance is supported by the run, existing evidence survives initialization/migration, and unknown history is not guessed. Leave no applicable criterion not-reviewed. Distinguish complete review, passing repository checks and verified runtime behavior.
