# Runtime Contracts And Tests Criteria

Generated from `../../assets/skill-quality-criteria.json`. Do not edit by hand.

Use this lane while creating scripts, CLI behavior, config contracts, output formats, and tests.

## Examples

- Good: Merge a validate-config, check-credentials, and verify-connectivity sequence into one preflight script that reports all results in a single agent step.
- Bad: Have the agent call three separate scripts sequentially, parse each output, decide whether to continue, and handle errors at each step.

- Good: Document a command's flags, config lookup, exit codes, stdout or file output shape, and dry-run behavior, then enforce those contracts with deterministic positive and negative tests.
- Bad: Tell the agent to inspect configuration manually, infer valid arguments from prose, and summarize output without stable schemas, exit codes, or tests.

- Good: When updating a config or policy file that may already exist, read the current file, merge the new entries in, write the result, then run a check that every prior entry still exists (count or key diff) before reporting success.
- Bad: Overwrite an existing config or policy file with only the new entries, silently dropping whatever the user already had.

## `runtime.cli-and-config-contracts` - CLI and config contracts are enforced

Document flags, config schemas, setup paths, credential lookup, and parser behavior, then enforce them with deterministic script behavior and focused tests. Before implementing operations that depend on an external CLI, API, library or host behavior, record dependency identity, tested version/supported range, relevant contracts and primary-source or reproducible observation evidence in the plan. Validate the actual constructed argv/requests and response shapes against that independent evidence, including dynamic and wrapper-injected options. Imported scripts, copied docs and mocks derived from the implementation do not establish the external contract. Verify installation/authentication and reject unresolved or invented interfaces. Preflight must detect missing dependencies and route to evidenced setup steps.

## `runtime.output-contracts` - Output contracts are stable

Document and test machine-readable output, generated file formats, stdout/stderr conventions, and exit codes used by downstream agents, scripts, CI, or users.

## `runtime.safe-file-mutation` - Edits to existing files merge and are verified

When a skill writes to a file that may already exist (config, policy, lockfile, generated output), design the write as a merge that preserves prior entries rather than a blind overwrite, and add an operational check that confirms nothing pre-existing was dropped, for example comparing entry/key counts before and after or diffing against `git show HEAD:<file>`. Skills that only create fresh files or emit transient output do not need this.

## `runtime.deterministic-tests` - Deterministic tests cover risk

Plan operation-specific unit, contract, integration and eval checks before implementation, with commands/procedures, expected outcomes, evidence sources, environment and cleanup; explain inapplicable layers. Cover safety, nullable/missing/empty inputs, parser, config, output and preflight failure paths without requiring live credentials by default. Mutation tests must establish approval enforcement, preview/execution correspondence and partial-failure accounting. A coverage percentage alone does not establish operation correctness; use a deliberately invalid contract case to prove the external checker rejects that defect class. Map the verification dimensions already recorded in the plan to checks derived from intended capabilities and risks, explaining inapplicable dimensions. Their definition belongs to PLAN_TEMPLATE.md section 10.

## `runtime.agent-step-economy` - Agent surface is minimized

The agent surface is the number of steps the agent must perform to achieve a goal — each step is a reasoning decision that can go wrong. Minimize it: merge multiple script calls into one orchestrating script when possible, move repeatable logic into deterministic scripts, and keep the agent workflow short and linear.

## `runtime.live-validation` - Live validation is explicit

Exercise the actual dependency through the plugin and record observed integration results, separately from mocked tests and skill discoverability. Alpha may remain explicitly integration unverified only when required unit and independently grounded contract checks pass and live testing lacks credentials, service access or a safe target. Record affected operations and blocked/skipped evidence without claiming pass. An observed integration failure or unsupported contract must be fixed or the capability removed before merge. Test safe reads/sandbox mutations only within authorization, with assertions and cleanup; contract validity alone does not prove service-side effects.

## `runtime.eval-consideration` - Eval need is considered

Consider eval coverage for high-usage, shared, risky, or behavior-sensitive skill changes; disclose token/time cost before automated evals and record manual smoke evidence when evals are not useful. Use the high-reliability eval loop only after the user has approved the created or revised skill as worth deeper validation. Reserve A/B comparison for meaningful behavior changes such as trigger wording, workflow ordering, bundled scripts, output contracts, or quality/reliability changes, not routine edits.

## `runtime.shared_repo_pr_parity` - Shared-repo pre-PR parity is achieved

When the skill ships in a shared repository, run the host repo's canonical pre-PR command (for example `am-pm ci pr-check --base-ref <merge-target>`) and confirm exit code 0 before declaring the change complete. Record the command and observed exit code in the review evidence.

## `runtime.state-management` - Workflow state is tracked explicitly

For small in-session tasks, use in-prompt checklists or the Task tool. For multi-step workflows and plans, use committed state files (review matrices, coverage checklists, phase manifests) driven by scripts or hooks. For multi-phase skills, each phase MUST write its output to a committed manifest file before the next phase begins — the manifest is the explicit handoff contract and prevents lost progress across phase boundaries. Choose the lightest mechanism that prevents lost progress.
