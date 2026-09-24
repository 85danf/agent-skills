# Review Process Quality Criteria

Generated from `../../assets/skill-quality-criteria.json`. Do not edit by hand.

Use this lane while preparing review coverage, fresh-agent readback evidence, and completion checks.

## Examples

- Good: Complete every matrix row with pass, fail, or na plus concrete evidence such as tests run, artifacts checked, reviewer attribution, and fresh-agent readback when the workflow changed.
- Bad: Leave rows as not-reviewed, write evidence such as looks good, or treat one self-review as enough for a major agent-facing rewrite.

- Good: Keep findings limited to the changed files and realistic blast radius, and explain any skipped readback or live validation.
- Bad: Use the review to rewrite unrelated historical docs or raise style findings outside the diff.

## `review.fresh-agent-readback` - Fresh-agent readback is considered

For a new skill, substantial rewrite, or agent-facing workflow change, run or explain an isolated comprehension readback by a fresh agent.

## `review.diff-bounded-findings` - Findings are diff-bounded

Keep review findings limited to the diff and realistic blast radius; avoid unrelated style churn or historical rewrites.

## `review.matrix-complete` - Coverage matrix is complete

Before completion, decide each applicable criterion with concrete evidence and reviewer attribution; scope unaffected rows according to repository policy. Link planned check IDs to actual commands, observations and evidence artifacts in the living matrix; keep the plan as intended work. Distinguish passed, failed, blocked and skipped checks using the existing schema. A complete review is not an all-pass result. Initialize provenance before source edits without erasing prior evidence, preserve known provenance during migration, and use unknown rather than guessing how imported code was created.
