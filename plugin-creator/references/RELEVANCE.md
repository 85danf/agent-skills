# Relevance Authoring

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only
> skill, or a skill outside the am-pm monorepo.** The `relevance` sidecar and the
> proactive-suggestion mechanism described here are a Claude Code plugin feature
> with no Codex/Agent-Skills-standard equivalent. Skip this file unless you are
> authoring a Claude Code plugin inside the am-pm monorepo.

Claude Code can proactively suggest a plugin when a user's session context
matches a `relevance` block the plugin declares. This file is the authoring
judgement for that block: what it is, when to add one, how to choose signals,
and how to verify it. It does not restate Claude Code's field rules — those
are owned by the client and enforced by the gate below; restating them here
would repeat the mistake this repo already made once: one hand-written schema
mirroring the client's rules produced five separate divergences from the real
client — see the am-pm monorepo's
`docs/superpowers/specs/2026-08-10-plugin-relevance-design.md` for the record.

## When a plugin should declare relevance

A plugin whose usefulness is predictable from the user's current context
deserves a block: a Terraform plugin when the user is in an infra directory,
a Slack-API plugin when a manifest depends on the Slack SDK. A plugin that
applies everywhere — a general code-review or writing-style skill — does not:
the suggestion surface is shared across every am-pm plugin, and an over-broad
signal crowds out suggestions that would actually help someone. When no
signal is a good fit, record that decision instead of forcing one.

## The five signal kinds

`signals` is an object; the client accepts five signal kinds — `cwd`,
`filesRead`, `cli`, `hosts`, `manifestDeps` — and requires at least one when a
plugin declares a relevance block at all (the gate states the rest: field
shape, allowed characters, counts). Choose the ones that actually predict
this plugin's usefulness; more is not better. Each key participates as an OR
against the matched session, evaluated in a fixed order (`cli` → `hosts` →
`cwd` → `filesRead` → `manifestDeps`, stopping at the first match — this only
changes which trap text a live session renders, never whether the block
fires). Traps below are not discoverable from the field names — verified
against Claude Code **2.1.228**:

- **`cwd`** — glob patterns against the working directory, matched against
  both the absolute path and the path relative to the project root. The only
  signal that can match at session start, before the first turn. Prefer it
  when the plugin's fit is about *where* the user is working (an infra repo,
  a specific service directory) — write the pattern relative to the repo
  root; an absolute-path-only pattern misses the common case.
- **`filesRead`** — glob patterns against files the session touches. Also
  covers files Claude wrote or edited, and auto-loaded `CLAUDE.md` files —
  so a pattern here can match on files the user never opened by hand. Prefer
  it when the plugin's fit is about *what kind of file* is in play (a config
  format, a schema, a manifest).
- **`cli`** — leading commands of shell invocations the session runs, after
  the client drops a leading `sudo` and any `VAR=value` environment
  assignment. Records only the leading command: `cd infra && terraform plan`
  records `cd`, not `terraform`. A signal naming `terraform` will not fire on
  that common shell idiom — prefer `cwd`/`filesRead` for tools users
  typically chain after a `cd`, and reserve `cli` for a command that is
  usually invoked first or alone.
- **`hosts`** — hostnames scraped from `http(s)://` URLs in the **Bash
  commands** the session runs. Traffic the session sends via WebFetch or an
  MCP server is not seen at all — `hosts` only fits a plugin whose service
  the user actually reaches by shell commands shaped like a URL, not one
  reached only through a tool call.
- **`manifestDeps`** — regex pairs matched against manifest files (e.g.
  `package.json`, `pyproject.toml`) the session has already read — it does
  not scan the disk, so a pattern on a manifest the session never opened
  silently never fires; pair it with a `filesRead` pattern that gets the
  manifest read in the first place. The only signal that compiles and runs
  author-supplied JavaScript regexes against file content — write patterns
  deliberately; the gate ReDoS-probes them, but a pattern that is
  technically safe and still wrong (matching an unrelated dependency name)
  is a false suggestion the gate cannot catch.

## How to test a block

Do not hand-validate a `relevance/<plugin>.json` sidecar against remembered
field rules — run the gate, which validates against the schema and, for the
mechanically checkable parts, against the real client:

```bash
am-pm ci check --plugin <path-to-plugin-dir>
```

This runs the plugin-lane `relevance` check among the others. It fails when
`relevance` appears in `plugin.json` (it belongs only in the sidecar), when
the sidecar violates the schema, and when the client's own validator rejects
the staged marketplace entry built from it. A green check is the actual bar
— not a read of this file.

CI proves the sidecar is schema-valid and that the generated marketplace
loads; it cannot prove Claude Code actually *surfaces* the suggestion in a
live session (that surface is TUI-only). Inside the am-pm monorepo, the
manual end-to-end recipe is at `ci/docs/relevance-verification.md` (repo
root) — run it by hand only when changing the sidecar shape or the regen
emission, not for a routine per-plugin authoring pass. One fact worth
knowing before interpreting a live test, verified against Claude Code
**2.1.228**: a suggestion appears at most once per plugin per three
sessions, and never once the plugin is installed — a quiet session is not
proof the block is wrong.

## What NOT to do

Do not copy field limits, allowed characters, or counts into a plugin's
design doc or PR description "for reference" — a hand-copied limit becomes a
second, un-versioned copy that drifts the moment the client changes. If a
value is rejected, the gate's failure message names the field and the reason;
fix from that, not from memory of a limit written down here or anywhere else.
