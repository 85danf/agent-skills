# Commands Component

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only
> skill.** This component and its runtime mechanics (frontmatter fields, JSON
> schema, `am-pm validate` command) exist only in Claude Code plugins; there is no
> equivalent in the portable Agent Skills standard or in Codex.


## What It Does

A command is a Markdown file with YAML frontmatter that adds a user-invocable
slash command. In am-pm, commands live under `commands/<name>.md` and remain
a supported component for user-invocable shortcuts.

> **Naming note.** Claude Code has unified commands and skills —
> `.claude/commands/` is the legacy layout; `.claude/skills/<name>/SKILL.md` is
> the recommended path. In am-pm plugins, the `commands/<name>.md`
> component is still a supported shortcut for simple, user-invoked workflows.

## How It Works At Runtime

1. **Discovery.** Typing `/` in Claude Code lists all available commands; typing
   letters filters the list.
2. **Invocation name.** Comes from the filename or directory name, not the
   `name` frontmatter field. `name` is a display label shown in the picker.
3. **Content lifecycle.** On invocation the full Markdown body enters the
   conversation. It stays for the session; auto-compaction carries it forward
   (first ~5 000 tokens per skill/command, ~25 000 tokens combined budget).

## String Substitutions

The Markdown body supports dynamic placeholders:

| Placeholder | Expands To |
|---|---|
| `$ARGUMENTS` | Full argument string the user typed after the command name. |
| `$ARGUMENTS[N]` | Nth positional argument (0-indexed). |
| `$name` | Named argument value (from `arguments` frontmatter). |
| `${CLAUDE_SESSION_ID}` | Current session identifier. |
| `${CLAUDE_EFFORT}` | Current effort level. |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the skill/command directory. |
| `` !`command` `` | Runs the shell command at load time and injects its stdout. |

## Frontmatter Fields

### am-pm required fields

am-pm validation requires these; Claude Code treats all frontmatter as
optional.

| Field | Type | Description |
|---|---|---|
| `name` | string | Display label in the command picker (kebab-case). Invocation name comes from the filename. |
| `description` | string | One-line summary shown in the picker. Combined `description` + `when_to_use` is truncated at 1 536 chars. |
| `allowed-tools` | string or string[] | **Grant list** — permits these tools without prompting. Every tool remains callable; listing a tool here only skips the confirmation prompt. |

### Optional fields

| Field | Type | Values / Notes |
|---|---|---|
| `when_to_use` | string | Trigger phrase or scenario; helps the router pick this command. Combined with `description`, truncated at 1 536 chars. |
| `argument-hint` | string | Hint shown when the user types the command name, e.g. `"<path> [--fix]"`. |
| `arguments` | object | Named arguments (key → description string). Values are substituted via `$name`. |
| `user-invocable` | boolean | Whether the command appears in `/` listing. Default `true`. |
| `disable-model-invocation` | boolean | When `true`, the model cannot auto-invoke this command. |
| `disallowed-tools` | string or string[] | Tools explicitly blocked during execution. |
| `model` | string | Override session model, e.g. `claude-sonnet-4-5`. |
| `effort` | enum | `low`, `medium`, `high`, `xhigh`, `max` — reasoning effort level. |
| `context` | enum | `fork` is the documented mode (runs in a subagent fork). `inject` and `none` exist in the schema but are not prominently documented by Claude Code. |
| `agent` | string | Subagent name when `context: fork`. The subagent must be defined separately. |
| `hooks` | object | Inline hook definitions scoped to this command. |
| `paths` | string or string[] | File-path globs the command operates on (scoping hint). |
| `shell` | enum | `bash`, `powershell` are the documented shells. |
| `compatibility` | string | Runtime requirements description (max 500 chars). |
| `metadata` | object | Arbitrary key-value pairs for tooling; not processed by the runtime. |

## Minimal Shape

```yaml
---
name: audit
description: Run the repository audit workflow.
allowed-tools: Read, Grep, Bash(python3 scripts/audit.py:*)
---
```

```text
Run the audit script and report findings.
Use $ARGUMENTS as the target path if provided.
```

## Cost

A command buys one thing over a skill: a single Markdown file instead of a skill directory.
It does **not** buy discoverability — `commands/deploy.md` and `skills/deploy/SKILL.md` both
create `/deploy` and both appear in the picker (`user-invocable` defaults `true` on either),
so reaching for a command to get a name in the `/` list buys nothing a skill would not.

It does not buy a trigger you can rely on. Typing the name fires it, and by default the model
may route to it as well (`disable-model-invocation: true` turns that half off — the same
field works on a skill) — but nothing *makes* either happen, so anything that must run every
time needs a hook, not a command. The body is not free once it does fire, either: it enters
the conversation and stays for the rest of the session (see How It Works At Runtime above),
so its length is paid for on every later turn, not only at invocation.

## Use When

- The workflow is frequent, bounded, and user-invoked by name.
- The task has predictable inputs and should route to scripts or references.
- The command improves consistency by giving agents a short, repeatable procedure.

## Do Not Use When

- The workflow is already covered by the skill's normal activation path.
- The task requires broad discovery or judgment before the right operation is known.
- A script alone is enough and there is no agent-facing command contract.

## Monorepo Path

- Plugin file: `groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/commands/<command>.md`

## Best Practices

- Keep each command small and action-oriented.
- Route deterministic work to scripts; keep parsing and API logic out of the body.
- Name required inputs, approval gates, output expectations, and verification.
- Prefer one command per natural user intent instead of a large command menu.
- Use `allowed-tools` to grant without prompting, not to restrict. Omit to use
  default permission behavior.

## Validation

- Run `am-pm validate command commands/<command>.md`.
- Confirm `name` matches the intended display label (invocation is by filename).
- Confirm `description` is one line suitable for the command picker.
- Smoke-test the command with a fresh-agent mindset; verify referenced scripts
  and references exist.
