# Hook Exit Codes

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only skill.** Hooks are a Claude Code plugin component with no Codex/Agent-Skills-standard equivalent; see `../hooks.md`.


Command hooks communicate their result through the process exit code.

## Exit 0 -- Success

The hook completed successfully. Stdout is parsed for JSON output; the field
schema lives in [output-format.md](output-format.md) — do not restate it here. <!-- citation -->
If stdout is not valid JSON it is shown as plain text in the transcript.

## Exit 2 -- Blocking Error

The hook detected a policy violation. Stderr is fed directly to Claude as
context, and stdout / JSON output is ignored. Claude sees the error and must
address it before retrying the blocked action.

Use exit 2 whenever the hook enforces a hard policy -- for example rejecting a
write to a generated file, blocking a commit without required metadata, or
preventing a dangerous shell command. **If your hook enforces a policy, you MUST
use exit 2.**

## Exit 1 (or any other non-zero code) -- Non-Blocking Error

The hook encountered an unexpected failure. A warning is shown in the terminal
but execution continues normally. This is the fallback for crashes, unhandled
exceptions, missing dependencies, or transient network errors.

Do not rely on exit 1 for enforcement; Claude will proceed despite the warning.

## Summary Table

| Exit code | Blocking? | Stdout parsed? | Stderr shown? | Typical use            |
| --------- | --------- | -------------- | ------------- | ---------------------- |
| 0         | No        | Yes (JSON)     | No            | Success / advisory     |
| 2         | Yes       | No             | Yes           | Policy enforcement     |
| 1 / other | No        | No             | Warning only  | Unexpected failure     |
