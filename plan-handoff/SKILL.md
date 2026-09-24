---
name: plan-handoff
description: >
  Generate a short, accurate kickoff prompt that a fresh session pastes to
  implement an already-reviewed plan after the planning session's context is
  cleared. Pins an exact baseline (git HEAD, clean tree, green tests) and
  carries only out-of-band context the plan itself does not. Use when the user
  says "handoff prompt", "next-session prompt", "kickoff prompt to implement the
  plan", "prepare to continue in a fresh session", or "the context is full,
  hand this plan off". For writing the plan use writing-plans; for executing it
  use executing-plans — this skill only bridges them.
disable-model-invocation: true
metadata:
  author: Dan Feldman
  version: "0.1"
compatibility: >
  Requires Python 3.10+ and git. Reads the repo's git state and optionally runs
  the repo's own test command once, as a subprocess in the repo root (no
  shell). No external services or credentials.
---

# Plan Handoff

> **Safety:** never relay a clean-looking handoff over a dirty tree or a red
> baseline test run — if the script warns, fix the baseline first. `--test-cmd`
> runs as a plain subprocess (no shell), but its last output line is echoed
> verbatim into the prompt, so don't pass a command whose last line could print
> a secret.

> **Claude-Code-specific, flagged not rewritten:** the `disable-model-invocation:
> true` frontmatter field is a Claude Code directive (only trigger on an
> explicit user request, never automatically). If the host platform has no
> equivalent, the skill's description text is the only signal it has for when
> to trigger this skill.

Emit a copy-paste prompt that lets a fresh session implement a reviewed plan
against a pinned baseline. The output is a prompt the **user pastes into a new
session** — this session does not execute the plan.

The plan and the repo rules (CLAUDE.md, AGENTS.md, the plan's own header) already
carry most context. This skill adds **only what they don't**: an exact baseline
to verify, and out-of-band friction the planning session hit but never wrote down.

## Workflow

1. **Identify inputs.** The plan file path (required) and any companion
   design/spec/notes file. Confirm both are **committed** — the baseline pins a
   commit, so a dirty plan means an ambiguous handoff.
2. **Read the plan** so you do not restate it. Then collect, from this session
   only, items that are NOT already in the plan, spec, CLAUDE.md, AGENTS.md, or
   another repo skill:
   - **Pitfalls / friction** the planning session surfaced but did not record.
   - **Other context** that did not make the plan.
     If there are none, pass none — the script drops empty sections.
3. **Find the test command** from the repo's rules (e.g. `uv run pytest`,
   `mvn test`). This is what the new session re-runs to confirm the baseline.
4. **Run the script** — it captures git HEAD/branch/tree, runs the tests once to
   confirm green, prints the finished block, and also saves it to a
   session-namespaced file (see Script contract):

   ```bash
   python3 <skill_dir>/scripts/emit_handoff.py \
     --repo <repo-root> \
     --plan <plan-path> \
     --test-cmd "<test command>" \
     [--spec <spec-path>]... \
     [--pitfall "<friction not in the plan>"]... \
     [--context "<other out-of-band context>"]...
   ```

5. **Relay the fenced block verbatim** to the user. If the script printed a
   warning (uncommitted tree, or red baseline tests), surface it and fix the
   baseline before handing off — never emit a clean baseline over a dirty or
   red repo.

## Script contract

`emit_handoff.py` owns all formatting so it cannot drift: backticked paths, one
fenced block, empty sections dropped, exactly one STOP gate.

- `--plan` (required), `--repo` (default `.`, resolved to git toplevel),
  `--test-cmd`, `--spec` / `--pitfall` / `--context` (each repeatable),
  `--no-run` (record the test command without running it), `--selfcheck`.
- `--test-cmd` runs as a subprocess in the repo root (parsed via `shlex.split`,
  no shell); use `--no-run` to record it without running. Its last output line
  is echoed into the prompt — don't pass a command that prints secrets on its
  final line.
- It **defers to the plan's header** for the execution skill: if the plan names
  one (`executing-plans` / `subagent-driven-development`), no "Required skill"
  section is emitted. Otherwise it names a skill based on the plan/spec path's
  convention (e.g. `docs/superpowers/plans/` or `docs/superpowers/specs/` →
  `superpowers`), or falls back to a generic "implement step-by-step"
  instruction when no known convention matches. Add a new convention in
  `emit_handoff.py`'s `SKILL_FAMILIES` list, not here.
  (Flagged, not rewritten: the built-in "superpowers" family's fallback text
  names skills as `superpowers:executing-plans` /
  `superpowers:subagent-driven-development` — that `plugin:skill`
  colon-qualified form is a Claude Code plugin-invocation convention. A
  Codex-only user without the `superpowers` plugin installed should read this
  as "your platform's equivalent plan-execution skill, if any" rather than a
  literal command.)
- It prints the block to stdout **and** saves a copy to
  `~/.claude/tmp/<session>/next-session-prompt-<nonce>.md`, printing that path to
  stderr. The session subdir is `CLAUDE_SESSION_ID` (a random subdir when unset);
  the nonce is fresh per run, so parallel sessions never overwrite each other.
  (`CLAUDE_SESSION_ID` is a Claude-Code-specific environment variable — a
  Codex environment won't set it, so this always falls back to a random
  subdir there; the script already handles that gracefully.)
- Exits non-zero with a clear message if the plan or a spec path is missing.

## What this skill does NOT do

- It does not write the plan (use writing-plans) or execute it (use
  executing-plans).
- It does not restate the plan header, CLAUDE.md, AGENTS.md, or other skills.
  Adding what the next session can already read is noise.
