# Monitors Component

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only
> skill.** This component and its runtime mechanics (frontmatter fields, JSON
> schema, `am-pm validate` command) exist only in Claude Code plugins; there is no
> equivalent in the portable Agent Skills standard or in Codex.


## What It Does

A monitor defines recurring or event-like checks that watch for drift, stale
state, missing generated output, broken integrations, or other conditions that
should surface after the initial skill run.

Requires Claude Code v2.1.105 or later.

## Capabilities

- Registers recurring or event-like checks that run a command and report an
  actionable result back to the user or host environment.
- The file is a JSON array. Each entry is one monitor.
- Each monitor declares a stable `name`, a human-readable `description`, and the
  executable `command`.
- Optional `args` pass command-line arguments. Optional `env` provides string
  environment variables.
- Optional `when` controls when the monitor runs: `always` (default) or
  `on-skill-invoke:<skill-name>` to scope it to a specific skill.
- am-pm treats monitors as experimental and records them through
  `experimental.monitors` in generated plugin metadata.
- Each stdout line from the monitor process is delivered to Claude as a
  notification.

Minimal shape:

```json
[
  {
    "name": "generated-output-drift",
    "command": "python3",
    "args": ["scripts/check_generated.py"],
    "description": "Detect stale generated plugin output."
  }
]
```

## Scope Restriction

Monitors do NOT load for project-scope `@skills-dir` plugins. Only
personal-scope plugins get monitors. If the plugin is project-scoped, its
monitors are silently skipped.

## Interactive Only

Monitors run only in interactive CLI sessions. They do not execute in
non-interactive or headless modes.

## Lifecycle

Disabling a plugin mid-session does not stop its already-running monitors. They
continue until the process exits or the session ends.

## Name Deduplication

The `name` field prevents duplicate processes on reload. When `/reload-plugins`
runs, a monitor with the same `name` as an already-running monitor is not
launched again.

## Cost

Every stdout line the monitor emits becomes context, and the component has **no rate
limiting and no auto-stop** — your filter is the only governor, and the process outlives the
intent that started it (see Lifecycle above).

Against that you buy one thing: no polling loop spending a turn and its output on every
check. If you were not otherwise going to check repeatedly, there is nothing to save and the
cost is all you get.

## Use When

- The value comes from repeated checking over time.
- The monitor can report a small actionable result instead of creating noisy
  updates.
- The check helps catch drift, broken credentials, stale data, or external
  service changes.

## Do Not Use When

- A one-time preflight, test, hook, or validator is enough.
- The check would be noisy, expensive, or dependent on fragile external state.
- The user did not ask for recurring follow-up or the repo does not support
  monitor execution.
- You need ONE notification: a monitor stays armed after the event, so background the
  command instead. Repeated **action** rather than repeated watching is a cron.

## Monorepo Path

- Plugin file: `groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/monitors/monitors.json`

## Best Practices

- For plugin-bundled monitor scripts, use `${CLAUDE_PLUGIN_ROOT}/scripts/<name>`
  in `command` or `args`. Relative paths do not resolve when the plugin is
  installed outside the project root.
- Make monitor output brief, actionable, and tied to a clear owner action.
- Include thresholds or debounce behavior when a condition may flap.
- **A success-only filter is silent through a crash or a hang** — indistinguishable from
  "nothing is wrong". Emit on failure and on the monitor's own inability to run, or you
  have built a check that reports healthy precisely when it is broken.
- Prefer read-only checks and document any credentials or external access.
- Keep monitor definitions separate from the core skill workflow unless the
  skill needs to explain how to interpret results.

## Validation

- Run `am-pm validate monitor monitors/monitors.json`.
- Confirm every monitor has `name`, `command`, and `description`.
- Confirm `args` is a string list and `env` values are strings when present.
- Run the monitor target command or query in a safe dry-run mode when possible.
- Confirm the review artifact explains why recurring checking is useful.
