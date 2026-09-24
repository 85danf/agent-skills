# Hook Stdin Payload

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only skill.** Hooks are a Claude Code plugin component with no Codex/Agent-Skills-standard equivalent; see `../hooks.md`.


Every command hook receives a JSON object on stdin describing the event context.
The exact fields depend on the event, but a common base is always present.

## Common Fields

Every event includes:

| Field              | Type   | Description                                      |
| ------------------ | ------ | ------------------------------------------------ |
| `session_id`       | string | Unique identifier for the current session.       |
| `transcript_path`  | string | Path to the conversation transcript file.        |
| `cwd`              | string | Current working directory of the session.        |
| `hook_event_name`  | string | Name of the event that triggered the hook.       |

## Tool Events (PreToolUse / PostToolUse / PostToolUseFailure / PostToolBatch)

Tool-scoped events add:

| Field           | Type   | Description                                        |
| --------------- | ------ | -------------------------------------------------- |
| `tool_name`     | string | Name of the tool being invoked.                    |
| `tool_input`    | object | The input object passed to the tool.               |

`PostToolUse` and `PostToolUseFailure` also include:

| Field           | Type   | Description                                        |
| --------------- | ------ | -------------------------------------------------- |
| `tool_response` | any    | The output returned by the tool.                   |

## SessionStart

| Field    | Type   | Description                                               |
| -------- | ------ | --------------------------------------------------------- |
| `source` | string | How the session began: `startup`, `resume`, `clear`, or `compact`. |
| `model`  | string | Model name selected for the session.                      |

## UserPromptSubmit

| Field    | Type   | Description                                    |
| -------- | ------ | ---------------------------------------------- |
| `prompt` | string | The user-submitted prompt text.                |

## Other Events (Partial Reference)

| Event                | Notable extra fields                              |
| -------------------- | ------------------------------------------------- |
| `PermissionRequest`  | `tool_name`, `tool_input`                         |
| `PermissionDenied`   | `tool_name`, `tool_input`                         |
| `UserPromptExpansion` | `prompt`                                         |
| `MessageDisplay`     | (common fields only)                              |
| `Stop`               | `stop_reason`                                     |
| `Notification`       | `message`                                         |
| `SubagentStart`      | `subagent_id`, `prompt`                           |
| `SubagentStop`       | `subagent_id`                                     |
| `TaskCreated`        | `task_id`, `prompt`                               |
| `TaskCompleted`      | `task_id`                                         |
| `FileChanged`        | `file_path`                                       |
| `CwdChanged`         | `old_cwd`, `new_cwd`                              |
| `ConfigChange`       | `key`, `old_value`, `new_value`                   |
| `PreCompact`         | (common fields only)                              |
| `PostCompact`        | (common fields only)                              |
| `Elicitation`        | `prompt`, `options`                               |
| `ElicitationResult`  | `result`                                          |

Read stdin in your hook script with standard tools:

```bash
#!/usr/bin/env bash
payload=$(cat)
tool_name=$(echo "$payload" | jq -r '.tool_name // empty')
```
