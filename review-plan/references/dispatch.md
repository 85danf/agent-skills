# Dispatch templates & merge rules

Read this at Step 5, once a track is chosen — it holds the verbatim subagent prompts,
the lane→agent map, the digest contract, and the merge rules for both tracks. Kept out
of `SKILL.md` because none of it is needed until a dispatch actually happens.

The agent's `model` (opus) and `effort` come from its own frontmatter — never
override them at dispatch. Never pass `model`/`effort` in the dispatch call.

**Always pass an output path.** Reviewers write their own reports (they hold `Write`)
and are told to write a skeleton early, then update incrementally. Pick one run
directory — `reviews/plan-review-{YYYY-MM-DD}-{slug}/` — and give each agent its own
file inside it. Read the files back rather than relying on the return message: a
reviewer that dies on a timeout still leaves partial findings on disk, and the
orchestrator never has to hold every report in its own context.

### Solo — holistic + risk lane

Dispatch **both** agents in a **single message** so they run in parallel:
`review-plan:plan-review-holistic` and `review-plan:plan-review-risk`. In
**no-design mode** (Step 1), replace the design line in both with the substitution string
given in `SKILL.md` Step 1 — both solo agents still run, neither is design-only.

```
subagent_type: "review-plan:plan-review-holistic"
description: "Holistic review of '{plan_filename}' against '{design_filename}'"
prompt: |
  ## Assignment
  Design document(s): {design_file_path(s)}
  Plan document(s):   {plan_file_path(s)}
  Context Summary (from orchestrator Step 3):
  {paste the Context Summary}
  Write your report to: {run_dir}/holistic.md

  Perform your full holistic review per your agent instructions. Read the design
  and plan completely, and ground every code claim, before writing any finding.
```

```
subagent_type: "review-plan:plan-review-risk"
description: "Risk/ops lane for '{plan_filename}'"
prompt: |
  ## Assignment
  Design document(s): {design_file_path(s)}
  Plan document(s):   {plan_file_path(s)}
  Context Summary (from orchestrator Step 3):
  {paste the Context Summary}
  Write your report to: {run_dir}/risk.md
  Peer report to cross-check, opportunistically (do NOT wait for it): {run_dir}/holistic.md

  Perform your lane's full review per your agent instructions. A holistic reviewer
  is covering every other dimension in parallel — cover ONLY your own: rollback,
  migration safety, backward compatibility, security, monitoring, and whether a
  fundamentally simpler approach was missed. Ground every claim.

  Then, if the peer report already has a Strengths table, run your Strengths cross-check
  against it. If it does not, write "N/A — peer report incomplete when checked" and stop;
  do not wait. The orchestrator repeats this check at merge time, so nothing is lost.
```

#### Merging the two (orchestrator, mechanically)

Read both files. Apply these rules and nothing else — you have no reviewer context,
so you may not author, reword, or re-rank a finding on your own judgment:

1. **Holistic's report is the base.** The risk lane contributes only risk/ops findings.
2. **Same root cause in both → keep the higher severity and the more specific
   evidence.** Do not average two severities and do not prefer the base's call. This is
   the point of the pairing: the single pass tends to _hedge_ risk findings that the risk
   lane rates Critical with a citation.
3. **Risk-lane-only findings append**, tagged `[F]`.
4. **Contradiction → grounding wins.** If the two disagree on a fact about code, the one
   citing `path:line` wins. If neither cites code, drop the finding to LOW and label it
   unverified.
5. **Cross-check the Strengths yourself — you are the guaranteed path.** The risk lane
   runs in parallel and usually finishes before the holistic report has its Strengths, so
   its own cross-check commonly reports `N/A`. That is expected. **Do not treat `N/A` as
   "nothing to check."** With both final reports in hand, run the check and delete — not
   soften — any Strength that fails it, recording each under _Falsified claims_ with the
   citation:
   - Every `REFUTED:` entry the lane did produce.
   - Any Strength asserting how the CODE behaves without a `path:line` you can verify.
   - Any Strength crediting the plan for describing what the OLD code did, unless its
     citation holds when you open it.
   - Any Strength that merely restates the plan's own assurance that something is handled —
     a test that proves a property, a mitigation, a gate. Measured: a reviewer credited the
     plan's per-task test gates for giving real confidence while the risk lane's own
     Critical showed those gates give false confidence. That is a finding the reviewer
     failed to make, inverted into praise.

   Do not soften a refuted Strength or keep it with a caveat: a wrong Strength is a false
   positive, and a reader trusts it and stops looking.

Do not add a third agent to merge these two. Two reports with one dimension of overlap
and an explicit authority rule is a bounded, mechanical merge; a merge agent here would
rebuild the expensive step that panel needs and solo does not.

### Panel — lanes A–F + digest synthesis

**In no-design mode (Step 1): dispatch only B–F — skip Lane A entirely**, since five of
its six checks require a design, and replace the design line in every remaining prompt with
`Design document(s): none — omit all design-fidelity checks.`

Otherwise dispatch all six lane agents (A–F) in a **single message** with
`run_in_background: true`, then, after they return, dispatch synthesis.

```
subagent_type: "review-plan:<agent-name>"   # see lane→agent map below
description: "Lane <X>: review '{plan_filename}' against '{design_filename}'"
prompt: |
  ## Assignment
  Design document(s): {design_file_path(s)}
  Plan document(s):   {plan_file_path(s)}
  Context Summary (from orchestrator Step 3):
  {paste the Context Summary}
  Write your full report to: {run_dir}/lane-<X>.md
  Then append a DIGEST section to that file, one line per finding, six fields:
    {CRIT|IMP|MINOR|DOCDRIFT} | {file}:{line} | {READ|INFER|NOCITE} | {claim} | CONF:{HIGH|MED|LOW} | FIX:{stub}
  - Field 3 is how you know the claim: READ = you opened the cited code and saw it;
    INFER = you cite it but did not read it; NOCITE = no citation. Synthesis resolves
    code-reality disputes on this field, so do not mark READ unless you read it.
  - {claim} states your CONCLUSION, not your title. If your body ends up clearing a
    finding your title called broken, the digest line must say so.
  - Escape any literal `|` inside a field as `\|` (Java `||`, a grep alternation).
  - One line per finding. A sub-bullet is part of its parent finding, never its own row.
  - Cap at 40 lines, dropping the LEAST severe first: never omit a CRIT or IMP. State
    what you omitted and at what severity — a cap must never read as "nothing more found".

  Perform your lane's full review per your agent instructions. Read both
  documents completely before writing any finding.
```

Lane → agent map (use for `<agent-name>`):

```
A → plan-review-alignment    D → plan-review-validation
B → plan-review-quality      E → plan-review-grounding
C → plan-review-sequence     F → plan-review-risk    Synthesis → plan-review-synthesis
```

After A–F finish, dispatch `review-plan:plan-review-synthesis`. **Pass the digests,
not the full lane text** — with each lane's full-report path so it can pull what it
must adjudicate. Six full reports ran ~370 KB in one measured run, most of it
redundant by merge time (six findings restated by 5+ lanes each); digests compress
that ~10× and keep the orchestrator from holding every report in its own context.
Synthesis supplements, never replaces, the lane findings.

```
subagent_type: "review-plan:plan-review-synthesis"
description: "Synthesis: merge all lane findings for '{plan_filename}'"
prompt: |
  ## Assignment
  Design document(s): {design_file_path(s)}
  Plan document(s):   {plan_file_path(s)}
  Context Summary: {paste the Context Summary}
  Write your merged report to: {run_dir}/synthesis.md

  ## Lane digests
  {paste each lane's DIGEST section, labeled, each with its full-report path:
   ### Lane A  (full report: {run_dir}/lane-A.md)
   {digest lines, incl. any truncation notice}}
```

