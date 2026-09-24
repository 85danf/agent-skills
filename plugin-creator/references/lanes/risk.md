# Capability, Data, And Approval Risk Reviewer

Use when reviewing the capability, data, and approval-risk lane of skill quality reviews.

Review capability profile, sensitive data handling, external mutations, approvals, enforcement, redaction, and residual risks.

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

- `risk.capability-profile` - Capability risk is explicit
  - Review: Check that the skill states what it can read, write, delete, publish, deploy, restart, exec, trigger, expose, or intentionally omit.
- `risk.approval-and-enforcement` - Approval and enforcement are appropriate
  - Review: Check that external writes, destructive actions, privileged operations, sensitive exports, risk-accepting actions that weaken a safety or security control (for example suppressing scanner findings or disabling a gate), and out-of-scope actions require an appropriate approval tier and deterministic enforcement where practical.
- `risk.secrets-and-data` - Secrets and sensitive data are protected
  - Review: Check credential handling, redaction, customer/production data exposure, logs, diagnostics, generated artifacts, and residual prompt-only risks.
