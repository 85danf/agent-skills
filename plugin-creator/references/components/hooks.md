# Hooks Component

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only
> skill.** This component and its runtime mechanics (frontmatter fields, JSON
> schema, `am-pm validate` command) exist only in Claude Code plugins; there is no
> equivalent in the portable Agent Skills standard or in Codex.


## What It Does

Hooks attach deterministic guardrails or automation to supported agent lifecycle
events. They are best for checks that should happen reliably around tool use or
repo changes.

## Capabilities

- Hooks run automatically at named lifecycle events: session start/end,
  prompt submission/expansion, tool use, permission flows, subagent/task
  activity, file/config/worktree changes, compaction, notifications, and MCP
  elicitation.
- The hook file is JSON with an optional top-level `description` and a required
  top-level `hooks` object keyed by event name.
- Supported events are `SessionStart`, `Setup`, `InstructionsLoaded`,
  `UserPromptSubmit`, `UserPromptExpansion`, `MessageDisplay`, `PreToolUse`,
  `PermissionRequest`, `PermissionDenied`, `PostToolUse`,
  `PostToolUseFailure`, `PostToolBatch`, `Notification`, `SubagentStart`,
  `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure`,
  `TeammateIdle`, `ConfigChange`, `CwdChanged`, `FileChanged`,
  `WorktreeCreate`, `WorktreeRemove`, `PreCompact`, `PostCompact`,
  `SessionEnd`, `Elicitation`, and `ElicitationResult`.
- A hook group can include `matcher` when the event supports matching. Tool
  events match tool names such as `Write`, `Edit`, `Bash`, or
  `mcp__<server>__<tool>`; some events always fire and ignore `matcher`.
- Each group runs one or more handler objects inside a `hooks` array. am-pm
  validates handler `description` for review/debug clarity.
- Handler `type` can be `command`, `http`, `mcp_tool`, `prompt`, or `agent`.
  Common fields include `if`, `timeout`, `statusMessage`, and `once`.
- `command` handlers require `command`; optional `args`, `async`,
  `asyncRewake`, and `shell` control execution.
- `http` handlers require `url`; optional `headers` and `allowedEnvVars`
  support authenticated local or internal services.
- `mcp_tool` handlers require `server` and `tool`; optional `input` passes
  static arguments. Use only with an already-approved and connected MCP server.
- `prompt` and `agent` handlers require `prompt`; optional `model` and (for
  prompt) `continueOnBlock`. Use them sparingly for checks that genuinely need
  model judgment.
- Hooks can block or add feedback depending on the event and output; use
  blocking hooks only for deterministic checks with clear messages.
- Sync by default; set `async: true` for fire-and-forget background hooks, or
  `asyncRewake: true` for background execution that wakes Claude on exit 2.
- All matching hooks run in parallel. Identical handlers are deduplicated
  across **settings files** only: a plugin's or skill's copy of the same handler
  stays separate and runs a second time.
- Default timeouts are per handler type AND per event -- there are six, not one:
  `command`/`http`/`mcp_tool` = 600 s; `prompt` = 30 s; `agent` = 60 s;
  `UserPromptSubmit`, `PreModelSwitch`, `PostModelSwitch` = 30 s;
  `MessageDisplay` = 10 s; and every `SessionEnd` hook shares a **1.5 s budget**
  across all of them (a longer per-hook `timeout` raises it, capped at 60 s).
- Plugin hooks merge with (not replace) user-level and project-level hooks.
- The legacy flat format (with `event` and `command` at the same level) passes
  schema validation but should never be used: always prefer the
  matcher/hooks nested format.

For exit code semantics see [hooks/exit-codes.md](hooks/exit-codes.md).
For stdin payload format see [hooks/stdin-payload.md](hooks/stdin-payload.md).
For JSON output patterns see [hooks/output-format.md](hooks/output-format.md).

## Minimal Shape

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/check-generated.sh",
            "description": "Block stale generated output before writes."
          }
        ]
      }
    ]
  }
}
```

## Skill-Scoped Hooks (SKILL.md Frontmatter)

The `hooks/hooks.json` file above is **plugin-level**: it is always on for every
session where the plugin is installed. When a guardrail should fire **only while
one skill is running**, declare the hook in that skill's **SKILL.md frontmatter**
instead. Claude Code loads a frontmatter `hooks:` block only while the skill is
active, so the guardrail scopes itself to the skill with no extra matching logic.

Key point: the `matcher` matches the **tool name** (e.g. `Bash`, `Write`,
`Edit`), **not** the skill name. Scoping comes from *where* the block lives (the
skill's frontmatter), not from the matcher.

```yaml
---
name: my-skill
description: ...
hooks:
  PreToolUse:
    - matcher: Bash          # tool name, not skill name
      hooks:
        - type: command
          command: "${CLAUDE_PLUGIN_ROOT}/skills/my-skill/scripts/block-git-write.sh"
---
```

The command script reads the `PreToolUse` payload on stdin, inspects the tool
input, and exits `2` to block the call (exit `2` is the only code that blocks a
`PreToolUse` call):

```bash
#!/usr/bin/env bash
set -euo pipefail
input="$(cat)"
cmd="$(printf '%s' "$input" | jq -r '.tool_input.command // ""')"
if printf '%s' "$cmd" | grep -Eq 'git[[:space:]].*(commit|push)'; then
  echo "This skill only stages files; leave them staged for the user to commit." >&2
  exit 2
fi
exit 0
```

Use a skill-scoped hook when the constraint is specific to one skill's workflow
(e.g. "this skill stages a file but must never commit it"). A blocklist on a
literal command string is **defense-in-depth on top of a prose rule, not a hard
security boundary** — say so in the script, and keep the prose rule too.

## Cost — the proof burden a hook takes on

A skill is cheap to build and impossible to prove it fires. A hook inverts both: trivial to
prove it fires, and **unverifiable by inspection that it works**. A wrong path, a
non-executable script, or a missing interpreter all fail open — the guard silently does not
exist while appearing configured, and the notice it prints reads like noise beside an action
that succeeded. Skill failure is invisible and probabilistic; hook failure is visible but
ignorable. Neither is free, and a guardrail must therefore be **tested live**.
**So the standing default is: would a skill description be enough? Then use one.**

## REACH — four shapes, widest last

An author who asks *"is there an event for exactly my moment?"* almost always answers no:
there are ~33 events and your moment is not one of them. The right question is **"is there
an event NEAR my moment?"**, and the answer is nearly always yes: three of the four shapes
below — derived, reshaped, **adjacent proxy** — exist to get you there. So REACH is not where
your judgement goes; spend it on AUDIENCE and WORTH.

| Shape | The event is | Example |
|---|---|---|
| **Named** | exactly your moment | session start |
| **Derived** | an event narrowed by a predicate | `Write` where the path matches `docs/**/plans/*.md` |
| **Reshaped** | your moment restated as an observable one | "after the plan is approved" → "when the plan file gains a `## Delivery` section" |
| **Adjacent / proxy** | *near* your moment, not it | the `writing-plans` skill finishing stands in for "a plan is ready to hand off" |

Worked example of the widest shape: `plan-layers` hooks `PostToolUse` with matcher `Skill`,
keyed on `superpowers:writing-plans`. No event means "a plan is ready to layer"; the skill
completing is close enough, and the hook injects a few lines of `additionalContext` — the
reminder that would otherwise be missed.

**The discipline that pays for adjacency: the broader the event, the smaller the payload.**
`plan-layers` says so in its own comment — it "is injected into EVERY writing-plans session,
so it stays two lines, not an essay." An adjacent-event hook injecting a page of context is
a context tax on every near-miss.

## AUDIENCE — who receives what the hook returns

Name the audience before asking whether the hook is worth it: it decides which payload you
can use, and which worth factors actually bite. Ask **"who needs to know?"** and the
payload follows.

- **The agent** — `additionalContext`, or (`Stop`/`SubagentStop`) `decision: "block"` + `reason`.
- **The tool call** — `permissionDecision` or `updatedInput`; wrong is a false positive.
- **A person** — `systemMessage`, a visible banner; spent as attention, not tokens.
- **The permission classifier** — `classifierContext`; it never sees tool results, so a hook is its only channel in.
- **The session** — `reloadSkills`, `sessionTitle`, `watchPaths`, `initialUserMessage`.
- **Nobody** — pure side effect (logging, cleanup); poor alignment here is genuinely fine.

## WORTH — the four factors

- **Alignment** — how often does this event fire when my moment is NOT happening?
- **Distance** — how far is "the rule was loaded" from "the rule matters"?
- **Consequence** — what actually breaks if it never fires?
- **Honesty** — is this genuinely expressible deterministically?

At the tool call, alignment, consequence and honesty are all critical and distance is
irrelevant; at the agent, distance is what argues for it at all; for a pure side effect,
none of them bite. Read [the audience reference](hooks/audiences.md) once you have named the
audience and need its full weighting or its payload fields.

## Can the event you named actually act?

Naming an event is routing, not permission. This check runs LAST, once worth is
established. Abridged to what a plugin author decides on:

| Event | Blocks? | `permissionDecision` | Rewrites input/output | `additionalContext` |
|---|---|---|---|---|
| `SessionStart` | no | no | no | **yes** (plain stdout also works) |
| `SubagentStart` | no | no | no | **yes** |
| `UserPromptSubmit` | **yes** (erases the prompt) | no | no — cannot replace the prompt | **yes** (plain stdout too) |
| `UserPromptExpansion` | **yes** | no | no | **yes** |
| `PreToolUse` | **yes** | **yes** allow/deny/ask/defer | **`updatedInput`** | **yes** |
| `PermissionRequest` | **no — exit 2 is IGNORED** | `decision.behavior` | `decision.updatedInput` | no |
| `PostToolUse` | no (exit 2 shows stderr to Claude) | no | **`updatedToolOutput`** | **yes** |
| `PostToolUseFailure` | no (exit 2 shows stderr to Claude) | no | no | **yes** |
| `PostToolBatch` | **yes** (stops the agentic loop) | no | no | **yes** |
| `Stop` / `SubagentStop` | **yes** | no | no | **yes** |
| `PreModelSwitch` | **yes** | **yes** allow/deny/ask | no | no |
| `PostModelSwitch` | no | no | no | **yes** (plain stdout too) |
| `PreCompact` | **yes** | no | no | no |
| `TaskCreated` / `TaskCompleted` / `TeammateIdle` | **yes** | no | no | no |
| `ConfigChange` | **yes** (except `policy_settings`) | no | no | no |
| `WorktreeCreate` | **yes — ANY non-zero exit aborts** | no | returns the worktree path on stdout | no |
| `MessageDisplay` | no | no | **`displayContent`** (screen only) | no |
| `Elicitation` / `ElicitationResult` | **yes** | no | **`content`** | no |
| `Setup`, `InstructionsLoaded`, `StopFailure` | no | no | no | **no — all JSON discarded** |
| `Notification`, `SessionEnd`, `PostCompact`, `CwdChanged`, `FileChanged`, `DirectoryAdded`, `WorktreeRemove`, `PermissionDenied` | no | no | no | no |

Three facts this table exists to prevent:

- **Only 11 events carry `additionalContext`.** `InstructionsLoaded` and `Setup`
  discard every JSON field, so a hook that detects something there can tell
  nobody. When the event that *sees* the thing cannot *act* on it, pair it with
  one that can and share state on disk (detect on `InstructionsLoaded`, write a
  lock file, enforce on `PreToolUse`).
- **`PermissionRequest` ignores exit 2.** A guard written there with `exit 2` is
  a no-op that looks correct; deny via `decision.behavior`.
- **Only `PreToolUse` and `PreModelSwitch` take `permissionDecision`.**

## The four return modes, plus the one that returns nothing

1. **Context injection** — `hookSpecificOutput.additionalContext`. Reaches
   Claude as a system reminder; the **user never sees it**. If the user must
   read it, say so in the payload ("print this verbatim") or use
   `systemMessage`, which is the only user-facing channel a hook has.
2. **Decision** — `permissionDecision` on `PreToolUse`/`PreModelSwitch`, or
   `exit 2`. Exit 2 blocks whether or not you print JSON; **exit 1 does not
   block** on any event but `WorktreeCreate`. A hook can TIGHTEN restrictions but
   never loosen them: `"deny"` is unbypassable (it fires before every permission
   mode, `bypassPermissions` included), while `"allow"` does not override a deny
   rule and cannot suppress the prompt for a tool marked `requiresUserInteraction`.
3. **Input/output rewrite** — `updatedInput` (`PreToolUse`) replaces the
   **entire** input object, so echo back every unchanged field; parallel writers
   race and the last to finish wins. `updatedToolOutput` (`PostToolUse`) changes
   only what Claude sees — the tool already ran.
4. **Instruction channel** — `Stop`/`SubagentStop` `decision: "block"` +
   `reason` is the ONLY documented way to hand Claude a new instruction and keep
   the turn going. See "Loop safety" below. `UserPromptSubmit`'s `reason` reaches
   the **user**, not Claude — do not use it to instruct.
5. **Nothing.** A hook that exits 0 with empty stdout is a complete, successful
   hook, and on the "None" decision-control events (`SessionEnd`, `FileChanged`,
   `CwdChanged`, `DirectoryAdded`, `Notification`, `InstructionsLoaded`,
   `PostCompact`, `Setup`, `StopFailure`, `WorktreeRemove`) it is the only honest
   shape — `additionalContext` there is a discarded string. Make pure recorders
   `async: true` or they add their whole runtime to every matching call.

## Pattern catalogue

Shapes that recur in shipped plugins. The first is the one authors get backwards — they
treat hook and skill as either/or, when the hybrid usually wins. The hook decides **when**,
the skill carries the **what**, so the moment cannot be missed and the judgement still gets
made.

| Pattern | Shape | Why it beats the alternative |
|---|---|---|
| **Deterministic trigger, skill does the work** | `PostToolUse` on `Write\|Edit` + a ~15-line predicate that names the skill to run *now*, on *this* path | A description is a lottery ticket; this is a trigger. Plugin-shipped hooks run about 11:3 in favour of pointing at a skill over doing the work — a plugin can ship a skill, a hand-written user-level hook cannot |
| **Juncture routing table** | `PostToolUse` on `Skill`, keyed by `tool_input.skill` | Lets a bundle state an ordering between two plugins that neither may state about the other |
| **Persona re-injection** | `SubagentStart` | `SessionStart` context never reaches a `Task`-spawned subagent. Any plugin that injects rules at `SessionStart` and also spawns subagents is silently half-installed |
| **Artifact-as-state idempotence** | The output file's own content is the "already done" flag | No seen-list to go stale. Self-correcting: delete the section and the hook re-offers |
| **Honest non-dedupe** | Tolerate a double fire and write down why | There is no session store a `PostToolUse` hook can trust. Two nudges cost a few tokens; dedupe state costs correctness on every session that misses it |
| **Measured threshold with a dead zone** | Fire on the top quartile of a real corpus, stay silent on the rest **on purpose** | The difference between a nudge and noise |
| **Command-line regex** | `matcher: "Bash"`, then re-derive the real trigger in the script | A `matcher` is a regex over the **tool name only** — anything command-shaped must be matched inside the hook |
| **Observer outside the control loop** | Compliance measurement, audit logs, guardrails on the agent's own config | A skill cannot observe its own compliance rate. Here the hook's value is the vantage point, not the timing |

## Loop safety on `Stop` / `SubagentStop`

Three obligations, all mandatory, when you use the instruction channel:

1. **Read `stop_hook_active` and exit 0 when it is `true`.** It marks re-entry.
2. **Carry your own iteration ceiling.** Claude Code overrides the hook after
   **8 consecutive** blocks (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`; `0` disables).
   That is a backstop, not a design — the counter resets on any non-blocking
   turn, so a block→allow→block hook can run indefinitely.
3. **Check a condition the hook can observe** — a sentinel in
   `last_assistant_message`, a file, a passing test. Never "block until it looks
   done."

`hookSpecificOutput.additionalContext` on `Stop` is **not** a loop-safe
alternative: same `stop_hook_active`, same 8-block cap, only a friendlier
transcript label. `prompt` handlers get a fourth affordance — honour
`impossible: true` so the model can end a loop it cannot satisfy.

## Pitfalls

- **A broken hook fails OPEN, loudly but ignorably.** A bad path or a
  non-executable script exits ~127 and prints a `hook error` notice beside an
  action that succeeded anyway — indistinguishable from a formatter hiccup. Since
  `CLAUDE_PLUGIN_ROOT` changes on every plugin update, a path that worked
  yesterday is a fresh chance to fail open.
- **The genuinely silent failure: exit 0 with contaminated stdout.** Shell-form
  hooks spawn `sh -c` / Git Bash / PowerShell, and a profile that echoes
  unconditionally prepends to your stdout. The output no longer starts with `{`,
  Claude Code treats all of it as plain text, and **nothing is reported** — the
  parse attempt lands only in the debug log. This is per-machine: the same plugin
  enforces on your laptop and no-ops on a teammate's. Prefer **exec form**
  (`args` present, no shell) for any guard; it removes this class by construction.
- **Therefore: a hook-based guardrail is unverifiable by inspection.** Reading
  `hooks.json` proves it is configured, never that it fires or that its verdict is
  honoured. **Ship every guard hook with a documented negative test — a command it
  must refuse — and run it after install and after every plugin update.**
- **Matchers are unanchored regexes.** Only `[A-Za-z0-9_- ,|]` means exact match;
  any other character switches to regex, so `Edit.*` also matches `NotebookEdit`
  and a plugin-scoped agent name (`my-plugin:reviewer`, which contains `:`) must
  be anchored `^my-plugin:reviewer$`. Matchers are case-sensitive.
- **`if:` is best-effort and over-fires.** It is evaluated only on the tool and
  permission events — on any other event a hook with `if` set **never runs at
  all** — it holds exactly one rule, and it runs your hook anyway when Claude Code
  cannot resolve what a Bash command expands to.
- **`suppressOutput` hides the hook's stdout, not its effect.** `additionalContext`
  still reaches Claude. It is read at runtime — the display call is guarded by
  `!suppressOutput` (measured in the 2.1.257 binary).
- **Print exactly one JSON object.** Multi-line output where one line sets a
  JSON-output field is a parse failure, not two decisions.
- **Plugin-shipped subagents cannot declare `hooks`** (nor `mcpServers` or
  `permissionMode`), for security reasons. Ship the hook in `hooks/hooks.json` or
  in a **skill's** frontmatter instead.
- **`hooks/` is not live-reloaded.** `SKILL.md` edits take effect immediately;
  `hooks/`, `.mcp.json`, and `agents/` need `/reload-plugins` or a restart, and
  after a mid-session update hook commands keep running from the OLD plugin root.
- **A timed-out hook does not block** on `PreToolUse` — the call proceeds through
  the normal permission flow. Do not count on a stalled hook to act as a gate.
  Two inversions: a timed-out `PreModelSwitch` hook DOES block the switch, and an
  Agent SDK callback that times out on `PreToolUse`/`UserPromptSubmit` DOES block.
- **Resume replays, it does not re-run.** Resuming with `--continue`/`--resume`
  replays the saved injected text for mid-session events, so timestamps, SHAs,
  and branch names go stale. Volatile context belongs on `SessionStart`, which
  does re-run (with `source` set to `resume`, `compact`, `clear`, or `fork`).

## Use When

- A rule must be enforced consistently, not merely remembered in instructions.
- The check is deterministic, fast, and has a clear pass/fail result.
- The hook prevents drift, unsafe edits, stale generated output, or missing
  required artifacts.

## Do Not Use When

- The behavior requires subjective reasoning or broad context.
- The check is slow, flaky, network-dependent, or likely to block normal work.
- A repo validator, test, or preflight script already enforces the same rule.

## Monorepo Path

- Plugin file: `groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/hooks/hooks.json`
- Claude Code auto-discovers `hooks/hooks.json` from the plugin directory.
  A `"hooks"` path field in `plugin.json` is not required.

## Best Practices

- Always use the **matcher/hooks nested format**, never the flat format. The
  flat format passes schema validation but breaks plugin loading at runtime.
  Use `"matcher": "*"` for hooks that fire unconditionally.
- Always use `${CLAUDE_PLUGIN_ROOT}/hooks/<script>` in command hooks. Bare
  CLI names and relative paths silently fail when the CLI is not on PATH.
  Every installed plugin resolves scripts through this variable.
- Available environment variables at runtime:
  - `CLAUDE_PLUGIN_ROOT` -- plugin install directory (use in command paths).
  - `CLAUDE_PLUGIN_DATA` -- writable data directory for the plugin.
  - `CLAUDE_PROJECT_DIR` -- project working directory.
  - `CLAUDE_EFFORT` -- current effort level (`low`, `medium`, `high`).
- Keep hooks deterministic and narrowly scoped.
- Prefer hooks that call tested scripts instead of embedding logic in config.
- Provide clear failure messages with the exact fix command or file.
- Make hooks advisory only when blocking would create too much friction.

## Validation

- Run `am-pm validate hook hooks/hooks.json`.
- Confirm every hook has a human-readable `description`.
- Confirm each event name is one of the supported values above.
- Confirm handler fields match the selected `type`: `command`, `http`,
  `mcp_tool`, `prompt`, or `agent`.
- Run the hook target script directly with passing and failing fixtures.
- Regenerate plugins, then run `am-pm validate repo` to confirm hook paths
  resolve from the generated plugin.
