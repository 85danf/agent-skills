<!-- Canonical section spine for the plan-handoff-prompt skill.
     Replace <...> placeholders with content from the Required inputs.
     Drop any section whose body is empty rather than leaving a placeholder.
     For the files block, use exactly one heading:
       "## Read these files first" — when notes/spec exist (list both)
       "## Plan file"              — when only a plan exists
-->

<Opening: 1–3 sentences framing role + task. Use the phase verb.>

## Working directory and branch

- Working directory: `<absolute path>`
- Branch (already checked out): `<branch>`
- Main branch: `<main>`
- <Optional: branch-state context (e.g. "~N commits ahead of origin")>

## Required state

<Only when required commits/tests exist. Otherwise omit this section.>

- The N tasks from `<plan path>` plus follow-up commits are already committed.
- Confirm with `git log --oneline <base>..HEAD`. Expect commits prefixed `<JIRA-PREFIX> - ` for, in order: <list>.
- If commits NOT present, STOP and ask before proceeding.

## Read these files first ← when notes/spec exist

## Plan file ← when only a plan exists

<Use exactly one heading above. With notes/spec, list notes first then plan; plan-only lists just the plan.>

1. `<notes/spec path>` — <role: "canonical 'why' document", "design rationale", or "ground-truth spec">.
2. `<plan path>` — <task count + step style, e.g. "10 tasks; steps use `- [ ]` checkboxes">.

## Why this work exists

<2–4 sentences from notes/spec. Include the non-negotiable invariant if present. Skip if the plan self-explains.>

## Required skill

Use `<skill name>`. <One-line behavior summary, e.g. "Dispatch a fresh subagent per task with the FULL task text + context inline. Spec-compliance reviewer + code-quality reviewer between tasks. Do NOT batch tasks.">

## Baseline check

<Only when test counts or build state must be verified before Task 1. Otherwise omit.>

Before Task 1, run `<exact mvn/uv command>` to confirm `<expected result, e.g. 173/173 green>`. Catches drift between sessions.

## Known friction

<Only when relevant. Otherwise omit.>

- <terse gotcha>

## Commit convention

Commit messages use the prefix `<JIRA-PREFIX> - <message>`, matching what is already on the branch.
