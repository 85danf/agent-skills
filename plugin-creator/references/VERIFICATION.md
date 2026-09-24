# Skill Verification

Run every applicable check before presenting a generated or refactored skill as
complete. Quality criteria live in generated lane references; this file records
the verification procedure.

## 1. Select Criteria Lanes

Resolve the active lane references for the current repo, then open only the
returned files that match the change:

```bash
python3 <skill_dir>/scripts/skill_review_coverage.py active-lanes --repo-root . --format references
```

Use `SKILL_QUALITY_CRITERIA.md` only when you need the full generated index.

## 2. Run Skill Checks

For the skill under review, always run plugin-creator's structural preflight — it
is a plugin-creator tool (Python) and validates SKILL.md/metadata regardless of
the authored plugin's language:

```bash
python3 <skill_dir>/scripts/sc_preflight.py
```

Then syntax-check and smoke-run the skill's *own* `scripts/` with the toolchain
for the plugin's language — Python, Node/TypeScript, or POSIX shell:

```bash
# Python
python3 -m py_compile <skill_dir>/scripts/*.py
<skill_dir>/scripts/<script>.py --help

# Node / TypeScript (from the domain that owns the deps)
npx tsc --noEmit
npx tsx <skill_dir>/scripts/<script>.ts --help

# POSIX shell
shellcheck <skill_dir>/scripts/*.sh
sh <skill_dir>/scripts/<script>.sh --help
```

**Claude Code plugin-specific (am-pm monorepo) — skip section 2a and the
`am-pm` commands below entirely for a portable/Codex-only skill or a skill
outside the am-pm monorepo.** For shared am-pm changes, the focused validators
below are useful for tight inner-loop iteration:

```bash
.venv/bin/am-pm validate skill <skill-dir>
.venv/bin/am-pm validate repo
```

### 2a. Shared-repo PR parity (Claude Code plugin-specific, am-pm monorepo only)

Inner-loop validation is not a substitute for the full pre-PR sequence. Before declaring a shared-repo skill change complete, run the host repo's canonical pre-PR command and confirm exit code 0:

```bash
.venv/bin/am-pm ci pr-check --base-ref <merge-target>
```

This runs pre-commit, `validate repo`, capability-embedding freshness, the version-bump check, and the plugin's tests under the coverage gate — run with the test runner for the plugin's language: **pytest** for Python, **Vitest** for Node/TypeScript, or **bats** for POSIX shell. Each enforces the group's `coverage_min` floor (default ≥ 75%, overridable per group in `groups/<group>/group.yml`) — the same five steps the host repo's CI pipeline runs. See the host repo's `docs/pr-checklist.md` for the full sequence, the failure → fix table, and the post-PR watch loop.

For a portable/Codex-only skill (or any skill outside the am-pm monorepo), section
2a does not apply; run whatever pre-merge check your own repo defines instead, or
skip this step entirely for a standalone skill install.

## 3. Execute the Verification Plan

Use the operation/check IDs in the approved plan's section 10. For an update, test the
changed behavior and its realistic effects; for an import, do not treat the source's
claimed working status as evidence. For paths without full plan gates, use the lightweight sections 4.1 and 10 recorded
before source edits; refresh older plans that lack them. Map affected operations to
concrete checks in review evidence. Confirm the dimension assertions already recorded
in the plan, including independently derived review cases, are covered. The dimensions
originate in the [plan template](PLAN_TEMPLATE.md#required-verification-dimensions). <!-- citation -->
Record observed side effects and operator interventions alongside the main
outcome; a successful main operation does not erase a failed scope or safety assertion.

For every applicable check:

1. Identify the behavior and expected outcome before running it.
2. Run the recorded command or procedure against the actual target revision.
3. Record the observed outcome, exit code/assertions, tested dependency version,
   date/revision and a compact evidence path. A test name alone is not a result.
4. Record untested branches and limitations; never infer success from coverage percent.

### Independent Contracts

Use the plan's section 4.1 sources as the external test oracle. Capture the argv or
request actually built by the plugin and compare it with the real dependency's
versioned manifest, schema, parser or equivalent authoritative evidence. Include
optional/dynamic arguments and flags injected by wrappers, not only list literals
visible to a static scan. Response fixtures should include documented or observed
nulls, missing fields, empty results and errors; record source/version and redaction.
A unit mock assembled from the same implementation cannot establish this contract.

Verify installation/authentication instructions and version preflight against the
chosen dependency. A supported-version range needs evidence for that range, not just
a single version label. Use a deliberately invalid command/flag or payload to check
that the contract test rejects the class of defect it is intended to catch.

### Integration and Alpha Acceptance

Exercise the actual dependency through the plugin, separating credential-free
integration from live service operations. Run safe reads and sandbox mutations when
credentials, an appropriate target and required authorization are available. Never
use production writes merely to complete verification. Check results, not just exit
codes; include cleanup for test mutations. A successful skill-trigger invocation
proves discoverability, not the generated plugin's service integration.

When deciding whether missing live evidence is acceptable, read
[`runtime.live-validation` in the generated runtime lane](criteria/runtime.md#runtimelive-validation---live-validation-is-explicit).
That criterion owns the alpha acceptance rule and the distinction between unavailable
access and an observed defect. Apply it to each affected operation and record the
outcome below. For mutations, record the deterministic evidence required by
`runtime.deterministic-tests`, plus any residual direct CLI/API bypass risk. <!-- citation -->

### Recording Outcomes

The plan describes intended checks; the living review matrix holds actual results.
For shared-repo plugins, put check IDs, outcomes and evidence links in the relevant
existing `criteria[].evidence` cells and actual eval evidence in `eval`. Do not add
new top-level keys or new criterion status values to the closed coverage schema.
Standalone work uses the same outcome vocabulary in its verification report.

| Actual check outcome | Matrix representation |
|---|---|
| passed | `pass` only for a criterion whose applicable assertions were actually met; cite the evidence |
| failed | `fail`, naming the failing assertion and affected operation |
| blocked | `fail` for the unverified runtime criterion; evidence starts `blocked:` and names the missing prerequisite |
| skipped | `fail` if the criterion applies; evidence starts `skipped:` and explains the decision |
| not applicable | `na` with a reason, subject to the repository's mandatory-lane rules |

Apply the generated lane's alpha rule to a live-validation row left `fail` with
`blocked:` evidence; do not relabel it `pass` to make a badge or summary green.
Report repository checks and operational verification separately. A review being
complete means all rows are decided, not that every capability passed. Likewise,
use `eval.status: skipped` for a declined eval and `manual-smoke-only` only when a
manual smoke test actually ran. Planning an eval or running a discoverability probe
is not an automated eval result.

## 4. Compare Against Source Material

When refactoring an existing skill or converting existing scripts, compare the
source material with the result. Imported code gets the same verification burden as
new code; preserving an existing defect is not a successful compatibility check:

- Preserved behavior and details.
- Deliberate generalization.
- Refactoring with no behavior change.
- Added safeguards or runtime contracts.
- Removed or materially changed capabilities.

Any removed or materially changed capability needs an explicit reason in review
evidence.

## 5. Complete Review Coverage

Generate, fill, and validate the review coverage matrix. The exact command
sequence — and the secret-scrubbing rule that applies before a diff reaches any
backend outside the approved local environment — lives in
[REVIEW_COVERAGE.md](REVIEW_COVERAGE.md); do not restate it here. <!-- citation -->

## 6. Report Results

Report verification as a concise checklist with:

- Planned check IDs, commands run, observed outcomes and compact evidence links.
- Review coverage artifact path.
- Eval evidence status and reason or metrics.
- Integration results, blocked/skipped capabilities and any alpha acceptance limitation.
- Source comparison result when applicable.
- Any residual risk or follow-up.
