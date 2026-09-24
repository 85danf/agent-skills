# Runtime Contracts And Tests Reviewer

Use when reviewing the runtime-contracts lane of skill quality reviews.

Review deterministic scripts, CLI contracts, config loading, output formats, parser behavior, tests, and live-validation evidence. Before reviewing tests, read the Required Verification Dimensions in this skill's `references/PLAN_TEMPLATE.md` section 10; use them to challenge the supplied plan independently.

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

- `runtime.cli-and-config-contracts` - CLI and config contracts are enforced
  - Review: Check that external contracts used by the changed operations have independently sourced, versioned evidence in the plan: dependency identity, installation/authentication, commands/flags or endpoints, response shapes and support assumptions. Inspect the actual argv/request paths, including dynamic/injected options, and the contract test oracle. Fail if tests only repeat locally invented contracts or accept every mocked call. Imported source gets the same burden as new code; an unsupported interface is not excused by missing credentials. Verify config and dependency preflight behavior.
- `runtime.output-contracts` - Output contracts are stable
  - Review: Check that machine-readable output, generated file formats, stdout/stderr conventions, and exit codes are documented and tested where downstream agents, scripts, CI, or users rely on them.
- `runtime.safe-file-mutation` - Edits to existing files merge and are verified
  - Review: If the skill writes to a file that can already exist (config, policy, lockfile, generated output), check that the write merges rather than clobbers and that an operational check confirms pre-existing content was preserved. Flag blind overwrites of user or shared files. Not applicable to skills that only create new files or emit transient output.
- `runtime.deterministic-tests` - Deterministic tests cover risk
  - Review: Check that each included or changed operation maps to concrete planned checks and expected outcomes. Verify deterministic coverage of realistic input and failure shapes, and for mutations approval enforcement, preview/execution correspondence and partial-failure accounting. Inspect independent contract evidence and a negative control that proves the checker can reject an invalid interface. Fail generic test/coverage checklists that cannot observe the relevant defect. Do not require live credentials for unit or offline contract checks. Independently derive cases from the capability/risk map before comparing with authored tests; check applicable dimensions and intervention evidence, including whether operator repairs conceal a failing shipped workflow. Require design correction when evidence exposes an unenforceable scope or safety claim.
- `runtime.agent-step-economy` - Agent surface is minimized
  - Review: Check that the agent surface is minimized: repeatable logic lives in scripts, multiple sequential script calls are merged where practical, and the agent workflow has the fewest reasoning steps needed. Flag unnecessary agent branching that a script could handle.
- `runtime.live-validation` - Live validation is explicit
  - Review: Check actual dependency/service integration evidence and distinguish it from mocks, preflight and skill-trigger invocation. If live access is unavailable, verify required unit and independent contract checks pass, affected operations are named, and alpha acceptance explicitly says integration unverified. Keep the unverified row fail with blocked/skipped evidence; do not call it pass or na because access is missing. Fail acceptance of observed integration failures, invented contracts, or use of the alpha exception for other lifecycles without repository policy. Verify mutation assertions and cleanup when exercised.
- `runtime.eval-consideration` - Eval need is considered
  - Review: Check that high-usage, shared, risky, or behavior-sensitive skill changes consider eval coverage. The author should either add or update eval evidence, record a manual smoke-test result, or explain why evals are not useful yet. Automated evals should not be required by default; token/time cost must be disclosed to the user before automated evals, automated evals should be reserved for high-value skills or high-risk changes, and manual smoke testing should be acknowledged where relevant. If automated evals ran, the review file must summarize quality, trigger, regression, comparison, failed-case, and token/time metrics where applicable and link the committed benchmark/metrics artifacts. Confirm the high-reliability eval loop was used only after the user approved the created or revised skill as worth deeper validation, and that A/B comparison was reserved for meaningful behavior changes, not routine edits.
- `runtime.shared_repo_pr_parity` - Shared-repo pre-PR parity is achieved (**Claude Code plugin-specific, am-pm monorepo only — skip for a portable skill or a repo without an equivalent gate**)
  - Review: Check that the change is verified against the host repository's canonical pre-PR command (for example `am-pm ci pr-check`) with exit code 0 recorded in the review evidence, not only inner-loop validators such as `validate skill` or `validate repo` alone.
- `runtime.state-management` - Workflow state is tracked explicitly
  - Review: Check that multi-step workflows have explicit state tracking — checklists, committed files, or Task tool (or equivalent) usage — proportional to the workflow's complexity. For skills with phase-gated workflows, verify each phase writes a manifest before the next phase can start. Flag workflows that rely on memory alone for state that could be lost on compaction.
