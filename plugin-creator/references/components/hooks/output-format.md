# Hook JSON Output Patterns

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only skill.** Hooks are a Claude Code plugin component with no Codex/Agent-Skills-standard equivalent; see `../hooks.md`.


Command hooks that exit 0 can print structured JSON on stdout to control how
Claude and the user receive the result. Plain text stdout is shown verbatim in
the transcript; JSON unlocks richer behavior.

Output is capped at 10,000 characters; excess is saved to a temporary file.

## Universal Fields

These fields work for any event:

| Field                                    | Type    | Description                                    |
| ---------------------------------------- | ------- | ---------------------------------------------- |
| `systemMessage`                          | string  | Visible warning banner in the terminal for the user. |
| `hookSpecificOutput.additionalContext`   | string  | Injected as a system reminder for Claude (not visible to the user). |
| `suppressOutput`                         | boolean | Hides stdout from the user while `additionalContext` still reaches Claude. |
| `continue`                               | boolean | Set to `false` to abort the current turn. Pair with `stopReason` for clarity. |
| `stopReason`                             | string  | Reason string surfaced when `continue` is `false`. |

`hookSpecificOutput` **requires** a sibling `hookEventName` set to the event
name. Omit it and the object fails schema validation: the action proceeds and
the transcript shows a `<hook name> hook error` notice. (It is not silently
discarded -- that was the behaviour before v2.1.248, and it is the reason the
myth persists.)

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "..."
  }
}
```

`SessionStart` **does** surface `additionalContext`. It has *two* context channels: `additionalContext`, and
plain stdout -- `SessionStart` is one of only four events where plain stdout
becomes context (with `UserPromptSubmit`, `UserPromptExpansion`, and
`PostModelSwitch`). A hook that only loads context can print to stdout and skip
the JSON entirely; use the JSON form when you also need `sessionTitle`,
`watchPaths`, `initialUserMessage`, or `reloadSkills`.

The myth arises because `additionalContext` is delivered as a **system reminder
with no visible transcript entry**. Verify delivery in the debug log
(`claude --debug-file <path>`), never by eye.

Do not emit two shapes "to be safe": Claude Code reads both `additional_context`
and `hookSpecificOutput` without deduplicating, so the payload is injected twice.

## PreToolUse Output

PreToolUse hooks can influence whether a tool call proceeds:

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow"
  }
}
```

`permissionDecision` accepts:

- `"allow"` -- bypass the permission prompt and execute the tool.
- `"deny"` -- reject the tool call; Claude sees the denial.
- `"ask"` -- show the normal permission prompt to the user.
- `"defer"` -- let other hooks or the default policy decide.

PreToolUse hooks can also modify the tool input before execution:

```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow"
  },
  "updatedInput": {
    "command": "echo 'sanitized command'"
  }
}
```

`updatedInput` replaces the tool's input object. Use this to sanitize arguments,
inject flags, or redirect paths.

## PostToolUse Output

PostToolUse hooks can block a tool result after it has run:

```json
{
  "decision": "block"
}
```

When `decision` is `"block"`, Claude is told the result was rejected and sees
the hook's stderr or `systemMessage` as the reason.

## Example: Advisory Context Injection

```json
{
  "suppressOutput": true,
  "hookSpecificOutput": {
    "additionalContext": "The file written is a generated artifact. Remind the user to regenerate rather than hand-edit."
  }
}
```

The user sees nothing; Claude receives the advisory as a system reminder.
