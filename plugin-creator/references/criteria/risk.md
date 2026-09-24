# Capability, Data, And Approval Risk Criteria

Generated from `../../assets/skill-quality-criteria.json`. Do not edit by hand.

Use this lane while documenting what a skill can read, mutate, expose, omit, and how risky operations are approved or enforced.

## Examples

- Good: Classify read, write, delete, publish, deploy, restart, exec, external-message, and sensitive-export operations by approval tier, and enforce dry-run or confirmation controls where practical.
- Bad: Let the skill perform destructive or external mutations while only saying the agent should be careful.

- Good: Report credentials as set or missing, redact sensitive values in logs and artifacts, scope generated prompts, and document any residual prompt-only risk.
- Bad: Echo tokens, commit production logs or customer data, or leave generated diff prompts containing secrets in tracked files.

## `risk.capability-profile` - Capability risk is explicit

State what the skill can read, write, delete, publish, deploy, restart, exec, trigger, expose, and intentionally omit.

## `risk.approval-and-enforcement` - Approval and enforcement are appropriate

Classify external writes, destructive actions, privileged operations, sensitive exports, risk-accepting actions that weaken a safety or security control (for example suppressing scanner findings or disabling a gate), and out-of-scope actions with an appropriate approval tier and deterministic enforcement where practical.

## `risk.secrets-and-data` - Secrets and sensitive data are protected

Protect credentials, customer or production data, logs, diagnostics, generated artifacts, and residual prompt-only risks through redaction, scoping, and clear constraints.
