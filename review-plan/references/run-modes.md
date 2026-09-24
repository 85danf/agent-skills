# Tracks & Dispatch Matrix

The orchestrator reads this after the Step 3 context round to recommend a track,
then confirms with the user (`AskUserQuestion`).

Two tracks: **solo** (`plan-review-holistic` + `plan-review-risk` in parallel → a
mechanical merge) and **panel** (lanes A–F → digest synthesis). `light`/`medium` are
accepted aliases for solo, `heavy` for panel.

## Complexity signals

Emit one signals row after the context round:

```
signals: plans=<n> plan_lines=<n> design_lines=<n> files_referenced=<n> risk=<comma-separated categories or none>
```

**Risk keyword categories** (count a category if any of its words appear in the
design or plan): `migration` (migration, backfill, schema change), `data-loss`
(delete, drop, truncate, destructive), `auth` (auth, permission, token, secret),
`breaking` (breaking change, API contract, remove endpoint, version bump),
`rollout` (feature flag, canary, phased, downtime), `concurrency` (concurrent,
race, lock, parallel).

## Recommendation thresholds

Recommend **panel** if any signal reaches its column; otherwise **solo**.

| Signal           | solo (default) | panel |
| ---------------- | -------------- | ----- |
| plan count       | 1              | ≥ 2   |
| plan lines       | ≤ 600          | > 600 |
| design lines     | ≤ 600          | > 600 |
| files referenced | ≤ 20           | > 20  |
| risk categories  | ≤ 2            | ≥ 3   |

Recommend, then let the user override — panel on a small high-stakes change, solo on a
large docs-only plan. **Risk-category count is the signal to weight most**, not size:
size predicts how much material there is, risk density predicts whether the dimension
solo hedges on is load-bearing.

Solo runs the risk lane either way, so a plan that is merely _large_ is not
automatically panel material; the case for panel is **many independent dimensions**
worth separate attention, which is what plan count and file count measure.

## Track → agents → effort map

`model: opus` for every agent (set in each agent's own frontmatter — never
override at dispatch).

| Track     | Agents dispatched                                        | Effort            |
| --------- | -------------------------------------------------------- | ----------------- |
| **solo**  | `plan-review-holistic` + `plan-review-risk`, in parallel | xhigh             |
| **panel** | lanes A–F → `plan-review-synthesis` (over lane digests)  | xhigh / C,D: high |

Panel lanes and their effort: `plan-review-alignment` (A, xhigh),
`plan-review-quality` (B, xhigh), `plan-review-sequence` (C, high),
`plan-review-validation` (D, high), `plan-review-grounding` (E, xhigh),
`plan-review-risk` (F, xhigh), `plan-review-synthesis` (xhigh).

## Eval record — the single source for these numbers

`SKILL.md` and the agent files link here rather than restating any of this; three
drifting copies of one recall claim have already gone stale once.

**Small planted-defect fixtures (2026-07-16/17).** The lane fan-out and one holistic
pass tied on recall (1.00), but lanes raised **21 false positives vs 3** at 6.6× cost
($28.59 vs $4.33) — each lane felt obliged to find something, and an "omit nothing"
merge surfaced all of it. One holistic pass with precision discipline: recall 1.00,
**1 FP**, $7.39. That is why solo runs one integrated reviewer, not a fan-out.

**Real 1,478-line plan vs a 434-file codebase (2026-08-02), 3 repeats/arm, graded
against a 29-entry key.** Recall 1.00 did **not** generalize — holistic scored core
recall **0.640** (range 0.53–0.76), 0 FP in all three runs, $22.38/case. Two
consequences that shape this skill:

- **Recall is largely stochastic.** The union of three runs caught 27/29; only two
  entries eluded all three. A single run cannot demonstrate a regression.
- **There is one systematic blind spot.** Grouping graded entries by lens, holistic's
  full-credit rate was: internal-consistency 0.90 · design-fidelity 0.79 ·
  cross-phase-sequence 0.78 · code-grounding 0.67 · history-mined 0.48 ·
  **validation-risk 0.38**. Ten entries never reached full credit and **seven carry
  the validation-risk lens** — rollback, cutover data state, observability. Worse,
  only two were never seen: the other eight were noticed and then **hedged to
  Minor/LOW**. So the risk/ops dimension needs escalation, not just discovery, and
  the reviewer's own Strengths section has certified plans as sound on exactly this
  axis while missing it.

**On panel timing out.** Round 3's fan-out produced 0/3 usable reports, but a later
offline replay of the identical merge on saved lane output **completed in 4m41s** —
longer than either original timeout — so that failure is attributed to inference
infrastructure on the day, **not** to the merge contract or request size. Do not cite
"0/3" as a property of the strategy. What the replay did establish: a synthesis pass
told to hunt inherited false premises settled a known contradiction on code evidence,
where the same pass without that instruction relayed a lane's verdict and then
demoted it. Hence the `Falsified claims` mandate in `plan-review-synthesis`.

These figures come from the skill's own eval rounds; the full write-ups live in the
am-pm repo under `groups/Global/devex/stable/reviews/review-plan/evals/` and do not ship
with the plugin.

Dispatch mechanics — the verbatim prompts, lane→agent map, digest contract and merge
rules — live in [`dispatch.md`](dispatch.md), read at Step 5.
