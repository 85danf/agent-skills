---
name: plan-handoff-prompt
description: Use when ending a session and the user wants a kickoff prompt for a fresh next session that picks up plan execution, plan verification, or research-then-commit work with checked-in docs and an in-progress branch
disable-model-invocation: true
---

# Plan Handoff Prompt

Generate a stand-alone kickoff prompt that a fresh Claude session can paste-and-run to continue plan-driven work without re-deriving context. The output is a prompt the **user pastes into a new session**, not something the current session executes.

## When to Use

- The user says "prepare a prompt I can give you in a fresh session", "kickoff prompt", "handoff prompt", "next-session prompt", or "draft the prompt for next time".
- The current session has finished a phase (plan written; tasks 1–N committed) and a follow-up phase will run separately.
- A plan file (and often a design/notes/spec file) exists under `docs/superpowers/`.

## Required inputs (ask only for missing; never invent)

1. **Phase verb** — `picking up`, `running`, `implementing`, `executing`, `validating`, or `continuing`.
2. **Working directory** — absolute path. Verify with `git -C <path> rev-parse --show-toplevel`.
3. **Current branch** + **main branch**. Verify with `git -C <path> branch --show-current` and `git -C <path> symbolic-ref refs/remotes/origin/HEAD --short`. Trust the user if the symref is unset.
4. **Plan file path** (relative to working dir). Required. Read first ~40 lines for task count and step style (`- [ ]` checkbox vs free-form).
5. **Companion design/notes/spec** — optional. Include when present under `docs/superpowers/notes/` or `/specs/`. Label by role: "canonical 'why' document", "design rationale", or "ground-truth spec".
6. **Required state** — commits or test counts next session confirms before starting. Get from `git log --oneline <base>..HEAD` (last 10–20). Include commit-prefix convention (e.g. `<JIRA-PREFIX> - `) and the exact `git log` command.
7. **Required skill** — usually `superpowers:subagent-driven-development` (independent tasks, same session) or `superpowers:executing-plans` (parallel session). Match the plan's structure.
8. **Friction notes** — gotchas next session needs (stale .class files, IDE false positives, credential issues). Skip the section if none.
9. **Commit convention** — JIRA prefix from branch name (`bugfix/<JIRA>-<slug>` → `<JIRA> - <message>`), per the user's CLAUDE.md.

## Output structure (canonical section spine)

Read `template.md` (sibling to this file) for the full spine. It defines, in fixed order, eight `##` sections — `Working directory and branch`, `Required state`, `Read these files first` / `Plan file`, `Why this work exists`, `Required skill`, `Baseline check`, `Known friction`, `Commit convention` — with placeholder hints for each. Emit sections in that order, drop empty ones, and use exactly one of the two file-block headings depending on inputs.

## Drafting rules

- **Backticks** around paths, branches, commands, commit hashes.
- **Absolute paths** for working directory; **relative paths** (to working dir) for plan/notes/spec/test files.
- **Quote next session's gates verbatim** — `git log --oneline HEAD~10..HEAD`, `mvn -pl ingest test`, etc.
- **No invented state.** Didn't read the plan? Don't assert task count. Didn't run `git log`? Don't list commits.
- **One "stop" condition per gate.** Always include "If commits NOT present, STOP and ask…" on Required state.
- **Drop empty sections.**
- **Preserve user's phrase bank** when it fits: "do NOT batch tasks", "STOP and ask me", "spec-compliance reviewer + code-quality reviewer between tasks".

## Workflow

1. Read the plan file (always). Read the notes/spec file if cited (always). Run `git -C <path> status -sb && git -C <path> log --oneline -20` against the working dir to ground Required state. Never let these commands fall back to the current shell CWD — that is the wrong-tree case the gate catches.
2. Ask only for inputs you cannot derive: phase verb, required skill (if ambiguous), friction notes, and any "Required state" details not in the commit log.
3. Draft the prompt by filling the spine. Drop empty sections.
4. Save to `~/.claude/tmp/next-session-prompt.md` (creating the directory if needed) AND print it inside a fenced ` ```markdown ` block.
5. Tell the user: paste from chat, or run `pbcopy < ~/.claude/tmp/next-session-prompt.md` (macOS; substitute `xclip -selection clipboard` or `wl-copy` on Linux).

## Example

Illustrative values — substitute your own.

```markdown
You are implementing the <PLAN-NAME> plan (code-changes phase) in <repo/service> using subagent-driven execution.

## Working directory and branch

- Working directory: `/Users/<you>/work/<repo>`
- Branch (already checked out): `bugfix/<JIRA>-<slug>`
- Main branch: `master`
- The branch is ~12 commits ahead of origin (prior-session work). New tasks build on top.

## Plan file

- `docs/superpowers/plans/<plan>.md` — N tasks with verbatim code blocks; steps use `- [ ]` checkboxes. Follow task-by-task. Do NOT touch the companion verification plan — that is a separate session.

## Required skill

Use `superpowers:subagent-driven-development`. Dispatch a fresh subagent per task with the FULL task text + context inline. Spec-compliance reviewer + code-quality reviewer between tasks. Do NOT batch tasks.

## Why this work exists

A scenario-validation pass surfaced three regressions in <feature>. These tasks plug each one without breaking the off-by-default behavior from the prior session.

## Commit convention

Commit messages use the prefix `<JIRA> - <message>`, matching what is already on the branch.
```

## Red flags — stop and re-draft

- Prompt has more than 8 `##` sections → drop empty placeholders.
- No backticked paths → will rot when files move.
- Asserts unverified test counts/commits/branch state → invented state. Re-run `git log`, read the plan, or ask.
- Required state lacks the "STOP and ask" gate → next session continues blindly on a wrong tree.
- Wrapped in extra commentary instead of a single fenced ```markdown block → the output IS the prompt.
- JIRA prefix does not match branch name → re-derive from `bugfix/<JIRA>-<slug>` → `<JIRA> - <message>`.
