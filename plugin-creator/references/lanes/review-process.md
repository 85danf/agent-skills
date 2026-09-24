# Review Process Quality Reviewer

Use when reviewing the review-process quality lane of skill quality reviews.

Review whether skill changes have appropriate fresh-agent readback, diff-bounded findings, complete coverage matrices, and usable review evidence.

Use the criteria below as your complete checklist for this lane. Do not invent
extra criteria and do not edit shared files. If dispatched as a subagent, the
host agent will merge your lane result into the review coverage matrix; if
worked through directly, merge the result into the matrix yourself.

## Review Protocol

1. Review only this lane and the supplied diff or files.
2. Stay diff-bounded unless a nearby file is necessary to understand blast radius.
3. Mark each criterion `pass`, `fail`, or `na`.
4. Include concrete evidence for every row.
5. Return only the requested lane result table unless asked for analysis.

## Lane Criteria

- `review.fresh-agent-readback` - Fresh-agent readback is considered
  - Review: Check whether a new skill, substantial rewrite, or agent-facing workflow change needs an isolated comprehension readback, and whether any skip is explained.
- `review.diff-bounded-findings` - Findings are diff-bounded
  - Review: Check that review findings are limited to the diff and its realistic blast radius, with no unrelated style churn or historical rewrites.
- `review.matrix-complete` - Coverage matrix is complete
  - Review: Check that review evidence links intended checks to actual results, records blocked/skipped checks honestly, and does not treat planning or a coverage percentage as proof. Verify creation/update provenance is supported by the run, existing evidence survives initialization/migration, and unknown history is not guessed. Leave no applicable criterion not-reviewed. Distinguish complete review, passing repository checks and verified runtime behavior.
