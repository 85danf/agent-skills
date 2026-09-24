---
name: review-plan
description: Use when reviewing one or more implementation plan documents against the design, spec, or brainstorm doc that initiated them, before the plan is executed, to verify alignment, completeness, feasibility, and grounding in real code
disable-model-invocation: true
---

# Review Plan Against Design

Orchestrate a multi-lane review that a plan document is correctly derived from
its source design, is internally feasible, and is grounded in the actual
codebase — before the plan is executed.

This skill is the **orchestrator only**: it classifies inputs, gathers context,
picks a run mode, dispatches reviewer lanes, and aggregates their findings.
All review judgment lives in the `references/lanes/*.md` files. Never inline a
lane's checklist here — read and run the lane.

## Step 1: Classify input files

Split the provided files into designs and plans.

- **Plans:** filename contains "plan".
- **Designs:** filename contains "design", "architecture", "brainstorm", "spec",
  or "requirements".

If a file matches neither or both, ask the user which it is. If no design was
provided, ask for one — the review compares plan _against_ design and is far
weaker without it. If the user confirms there is no design, proceed in
**no-design mode**: record "no design provided" in the Context Summary, on **panel**
**skip Lane A entirely** (five of its six checks need a design), and in every
remaining dispatch prompt replace the design line with
`Design document(s): none — omit all design-fidelity checks.` Solo keeps both its
lanes — neither is design-only.

## Step 2: Map designs to plans

- **1 design + 1 plan** → one pair, proceed.
- **1 design + N plans** → map all plans to that design.
- **N designs + M plans** → ask the user for the mapping:

  > Multiple design and plan docs found. Which design governs which plan(s)?
  > Designs: {list} Plans: {list}
  > Example: "design-auth -> plan-auth; design-api -> plan-api + plan-integration"

## Step 3: Context round (always)

Before running anything, build shared context and measure complexity.

1. Read every design and plan doc **completely**.
2. Read project config: `CLAUDE.md` / `AGENTS.md` (and any it points to) for
   conventions, constraints, and preferred engineering standards. Project
   `CLAUDE.md` engineering preferences **override** the lanes' default rubric.
3. Follow links: if a plan cites a PRD/RFC/ADR, read it.
4. **Skip file globbing here** — the reviewer does its own grounding (the holistic
   lane on solo, the grounding lane on panel). Only note a path's status
   in the summary if the plan states it outright (marks a file "new"/"existing"),
   which needs no tool call.

Emit a **Context Summary** (3–5 bullets): key conventions, architecture/patterns
in play, test framework, and constraints that affect the review. Then emit a
one-line **signals** row (see `references/run-modes.md`): plan count, plan/design
line counts, referenced-file count, and which risk keywords appear.

## Step 4: Choose a track

There are two tracks. From the signals, **recommend** one using the thresholds in
[`references/run-modes.md`](references/run-modes.md), then confirm with the
user before proceeding — on a platform with a structured choice prompt (e.g.
Claude Code's `AskUserQuestion`), use it; otherwise just ask in plain text. Do
this here in the orchestrator, before any lane runs.

| Track     | What runs                                                           |
| --------- | -------------------------------------------------------------------- |
| **solo**  | `plan-review-holistic` **+ `plan-review-risk`** in parallel → merge |
| **panel** | lanes A–F in parallel → digest synthesis                            |

Accept `light` and `medium` as aliases for **solo**, and `heavy` for **panel**.

**The risk lane is not optional on solo.** One holistic pass is measurably weak on
exactly one dimension — validation/risk — and it under-covers it by _hedging_, not by
missing it outright. The risk lane is what escalates those findings. Numbers and the
per-lens breakdown live in [`references/run-modes.md`](references/run-modes.md);
that file is the single source — never restate its figures here or in a lane file
(three drifting copies of one recall claim have already gone stale).

**State the tradeoff when you recommend.** Size alone does not predict which track is
needed — risk density does. So the recommendation says which signal fired, what each
track costs, and when to override:

```
signals: plans=8 plan_lines=1478 files_referenced=41 risk=migration,data-loss,rollout

Recommend PANEL — 3 risk categories and 1,478 plan lines.
  solo:  ~$30, ~30min. One holistic pass plus the risk lane, which covers the
         dimension a single pass hedges on. Two lanes plus a merge, serialized.
  panel: ~$32, ~17min. Six lanes in parallel then a digest merge, so it is not
         the slower or dearer track it was once assumed to be.
Override to solo for a docs-only plan, or when you want the cheaper-to-reason-about
two-report output rather than a seven-lane merge.
```

Quote figures as indicative, not guaranteed: each is a single measured run on one large
plan, and that plan's wall clock proved sensitive to inference-infrastructure conditions —
an earlier version of panel failed to produce any report at all under load. Say so rather
than presenting either track as strictly better.

## Step 5: Run the reviewers

Read [`references/dispatch.md`](references/dispatch.md) now — it carries the
verbatim dispatch prompts for both tracks, the lane→file map, the per-lane digest
contract, and the merge rules. Two invariants that govern every run:

- **Never override a lane's model/effort setting.** Both are fixed per lane (see
  `references/dispatch.md` and `references/run-modes.md`) — do not substitute a
  different model or reasoning effort when running a lane.
- **Always use an output path/file for each lane's findings**, written
  incrementally rather than held to the end — a lane that dies partway through
  (a timeout, a dropped session) should still leave partial findings on disk or
  in a durable note, and the orchestrator should read findings back from there
  rather than trusting only what's said in the moment.

**Executing a lane, platform-agnostically:** On a platform with subagent/parallel-task
dispatch (e.g. Claude Code's Task tool), dispatch each active lane as its own subagent
in parallel using the corresponding file in `references/lanes/` as its prompt, then run
the synthesis lane last on the combined output. On a platform without subagent dispatch,
work through each active lane's checklist yourself, sequentially, writing down its
findings before moving to the next lane, then perform the synthesis step yourself.

This changes only how a lane's instructions get executed. It does not change which
lanes run — that selection is fixed by the track chosen in Step 4 (solo: holistic +
risk; panel: lanes A–F + synthesis), per the lane→file map and dispatch prompts in
`references/dispatch.md`.

## Step 6: Report

**Solo:** the holistic report is the base; fold in the risk lane per the merge rules in
[`references/dispatch.md`](references/dispatch.md) and emit the format below. Do not re-rank or add findings beyond those rules —
each reviewer's own precision judgment is what the pairing preserves.

**Panel (aggregating the lanes):** compile the findings into the format below under
one rule — **traceability, not volume**:

- Merge findings sharing a root cause into one, keeping the highest severity and
  citing every lane that found it.
- **Drop a finding only when a cited-code check falsifies it** — and say so in one
  line under _Falsified claims_ with the citation.
- Never drop a finding merely to shorten the report.
- An empty dimension is a pass, not a hole.

This replaces an earlier "omit nothing" instruction, which combined with per-lane
obligation-to-find manufactured false positives at multiples of the cost (figures in
[`references/run-modes.md`](references/run-modes.md)). Making _volume_ the safety
property is what caused it; the rule above makes _evidence_ the safety property, so a
dropped finding must be justified while a hedged, unverifiable one is no longer
force-promoted into the report.

```markdown
# Plan Review Summary

## Overall Assessment: [Aligned / Aligned with Fixes / Misaligned]

## Context Summary

- {the 3–5 bullets from Step 3}

## Critical Issues (X)

- [{lane-letter}][{plan_filename}]: {issue} [{design}:{ref} -> {plan}:{ref}] (CONF: HIGH/MED/LOW)

## Important Issues (X)

- [{lane-letter}][{plan_filename}]: {issue} [{design}:{ref} -> {plan}:{ref}] (CONF: …)

## Minor Issues (X)

- [{lane-letter}][{plan_filename}]: {issue}

## Documentation Drift (X)

- {docs the plan will invalidate but does not update, or "None flagged"}

## Strengths

- {what is well-aligned / well-grounded across the docs}

## Summary of Issues

| ID   | Severity  | Lane | Plan Location    | Design Ref    | Description | Proposed Fix |
| ---- | --------- | ---- | ---------------- | ------------- | ----------- | ------------ |
| A-C1 | Critical  | A    | plan-core.md:124 | design.md:101 | …           | …            |
| E-I1 | Important | E    | plan-core.md:88  | src/foo.py:42 | …           | …            |
```

**Issue ID format:** `{lane-letter}-{severity-initial}{sequence}` — severity
initials C=Critical, I=Important, M=Minor; sequence is 1-based per severity per
lane (A-C1 = Lane A first Critical; E-I3 = Lane E third Important). Use this
exact format in the issue bullets above AND the ID column, so the synthesis
section's cross-references resolve. If only one lane ran, drop the lane prefix.

**Determination logic:**

- **Aligned** — zero critical, zero/few important.
- **Aligned with Fixes** — zero critical but important issues exist, OR 1–2
  criticals whose fix is a targeted, bounded revision to the plan (not a
  fundamental redesign of the approach).
- **Misaligned** — multiple criticals or a fundamental design↔plan disconnect.

Preserve every lane's empty-category "None found" notes.

**Audit the Strengths section — do not pass it through unread.** Audit it per merge rule 5
in [`references/dispatch.md`](references/dispatch.md), which is the single
description of this procedure.

A wrong Strength is a false positive with the same cost as a wrong finding, and it is
worse than silence: a reader trusts it and stops looking.

## Lane reference

Solo (both run, in parallel or in sequence per Step 5):

- `references/lanes/plan-review-holistic.md` — one integrated pass over all dimensions A–F
  with precision discipline; the base reviewer.
- `references/lanes/plan-review-risk.md` (F) — rollback, migration, back-compat, security,
  monitoring, simpler-alternative check. Mandatory: it covers the one dimension the
  holistic pass measurably hedges on.

Panel lanes:

- `references/lanes/plan-review-alignment.md` (A) — design↔plan contradiction, fidelity,
  completeness, use-case coverage, gap analysis, documentation drift.
- `references/lanes/plan-review-quality.md` (B) — required plan artifacts, internal
  consistency, right-sizing (engineering rubric).
- `references/lanes/plan-review-sequence.md` (C) — dependency order, no cycles, new-file
  marking, no magical thinking.
- `references/lanes/plan-review-validation.md` (D) — runnable validation commands, specific
  manual steps, test coverage of new paths/edges/regressions.
- `references/lanes/plan-review-grounding.md` (E) — file paths exist, symbols/signatures
  real, current-state claims accurate, hidden call-sites, local conventions.
- `references/lanes/plan-review-risk.md` (F) — as above; used by both tracks.
- `references/lanes/plan-review-synthesis.md` (panel) — adversarial cross-lane merge over
  bounded lane digests.
