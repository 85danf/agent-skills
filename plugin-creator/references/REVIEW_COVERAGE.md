# Review coverage

The scripts and the living-matrix mechanism below are portable — any shared repo
can adopt a committed `coverage.yml` per skill. **The exact path convention
(`groups/<group>/<domain>/<lifecycle>/reviews/<plugin>/coverage.yml`) is Claude
Code plugin-specific (am-pm monorepo)** — outside that repo, pick an equivalent
committed path for your own repo (e.g. `reviews/<skill-name>/coverage.yml`) and
pass it as `--output`/`--matrix`/`--input`. The MCP-attestation row described
below is also Claude Code plugin-specific — skip it for a portable/Codex-only
skill, which cannot ship `.mcp.json`.

For shared-repo skill changes, keep a single committed **living** review coverage
matrix per plugin and complete every row before presenting the change as done. It
lives at the `reviews/<plugin>/coverage.yml` sibling of the plugin's lifecycle dir
(`groups/<group>/<domain>/<lifecycle>/reviews/<plugin>/coverage.yml`) and is
re-affirmed on each change — one file, not a dated file per change.

## What the file holds

`coverage.yml` is validated against a closed schema (`additionalProperties: false`), so it
has exactly these top-level keys:

| key | values | who writes it |
|---|---|---|
| `created_with` | `plugin-creator` · `manual` · `unknown` | `begin` (or `generate`) stamps `plugin-creator` only for `--change-type new` with NO prior file; otherwise `unknown`. An existing value is never changed by a regeneration -- `--change-type` is operator-supplied and this script has no base ref, so it cannot tell a real new plugin from a promotion. CI rejects a later change TO `plugin-creator` (a claim may not be back-dated), so `unknown` on the PR that adds a plugin is permanent and the lane warns about it. |
| `updated_with` | `plugin-creator` · `unknown` · omitted | OPTIONAL, and omitted means `unknown`. `begin` (or `generate`) stamps `plugin-creator` at `--change-type update`, and an existing stamp survives. NOT stamped by `--change-type review-only`: the tool ran on the review, not on the plugin, and the `reviewed` badge already says that. There is no back-dating rule and no `manual` member -- an update is repeatable, so the next `update` run stamps it anyway. |
| `review_status` | `recorded` · `record-lost` · `none` | `recorded` when the rows below are the review. `record-lost` means a review happened but its record did not survive here -- it REQUIRES `review_note` naming where and at which ref. `none` asserts nothing. |
| `review_note` | prose or omitted | The `record-lost` pointer, or any caveat about the review. |
| `change_type` | `new` · `update` · `review-only` | From `--change-type`. |
| `criteria` | list of `{id, lane, status, evidence, reviewer}` | `id` and `lane` must match the criteria asset; `status` is `pass` · `fail` · `na` · `not-reviewed`. |
| `eval` | `status` + evidence fields | `status` is `not-applicable` · `skipped` · `manual-smoke-only` · `automated-run` · `record-lost`; `skipped` and `record-lost` require `reason`. Author-chosen extra fields go under `eval.notes`. |

`record-lost` is never a quiet exemption: it asserts the work happened. Something that
never happened is `none` / `not-applicable` / `skipped` with its reason.

**MCP attestation (Claude Code plugin-specific, skip for a portable skill).** There is no `## MCP Security Approval` section any more. When the
plugin ships `.mcp.json`, the user's security approval goes in the
`component-fit.mcp-approval` row: status `pass`, evidence naming the server, approver and
date. The CI gate reads that row whenever `.mcp.json` changes.

## Begin Before Source Edits

At the start of approved implementation, initialize the matrix with `begin` using the
classifier mapping below. This captures provenance before it can be lost during
review preparation. A fresh matrix has `review_status: none`: starting the workflow
is not a claim that a review happened. On an existing matrix, `begin` preserves all
rows, eval evidence and creation provenance; update runs stamp only update provenance
and the change type. Repeating it is safe. Do not infer authorship from a copied plan.

```bash
python3 <skill_dir>/scripts/skill_review_coverage.py begin \
  --skill <skill-name> \
  --change-type <new|update|review-only> \
  --repo-root . \
  --output groups/<group>/<domain>/<lifecycle>/reviews/<plugin>/coverage.yml
```

If a legacy `coverage.md` exists without the YAML, or the YAML is unreadable, `begin`
refuses to overwrite it. Preserve and migrate the original review evidence first;
carry known provenance forward and use `unknown` when creation evidence is absent.
Do not manufacture `manual` or `plugin-creator` during migration. The generator does
not establish how an imported personal skill was originally created.

Record the plan path and the plugin-creator version/revision actually used in
`review_note`, preserving any existing note, including required record-lost pointers.
These are attestations to the authoring run, not proof the entire workflow succeeded.

## Refresh at Review Time

Every applicable row must be decided before the change is presented as done.
Only at review time use `generate` to refresh the active criteria: it deliberately
resets rows to `not-reviewed`. Do not use it to initialize provenance on a completed
matrix. Merge lane outputs and set `review_status: recorded` only once the review
has actually been performed. Preserve historical provenance throughout.

Record verification check IDs and actual outcomes in the relevant criterion evidence,
following VERIFICATION.md when filling results. The plan holds intended checks, not a
second result checklist. Use the existing eval block for actual eval results. <!-- citation -->

**Pick `--change-type` from Step 0's classifier `path`** -- it is not always `update`,
and a new plugin run with `update` is exactly what loses its `created_with` stamp
forever:

| classifier `path` | `--change-type` |
|---|---|
| `new` | `new` |
| `behavior-change` · `mechanical` · `package` | `update` |
| (no payload change -- a reviews-only PR) | `review-only` |

```bash
python3 <skill_dir>/scripts/skill_review_coverage.py generate \
  --skill <skill-name> \
  --change-type <new|update|review-only> \
  --output groups/<group>/<domain>/<lifecycle>/reviews/<plugin>/coverage.yml
```

When a sub-agent backend is available, prepare lane-specific prompts instead of
asking every reviewer to edit the same matrix file:

```bash
git diff --no-color <base-ref>...HEAD > /tmp/<skill-name>-review.diff
python3 <skill_dir>/scripts/skill_review_orchestrate.py prepare \
  --skill <skill-name> \
  --change-type <new|update|review-only> \
  --diff /tmp/<skill-name>-review.diff \
  --output-dir /tmp/<skill-name>-review
```

Read `/tmp/<skill-name>-review/manifest.json`. For each lane, dispatch the listed
`subagent_type`, pass that lane's `prompt_path` as the complete task context, and
ask it to write only the lane result table to `result_path`. Because the prompt
can contain the full diff, review it for secrets, production data, or sensitive
customer details before sending it to any backend outside the approved local
environment. Merge the lane outputs into the committed matrix, then validate:

```bash
python3 <skill_dir>/scripts/skill_review_coverage.py merge-lanes \
  --matrix groups/<group>/<domain>/<lifecycle>/reviews/<plugin>/coverage.yml \
  --results-dir /tmp/<skill-name>-review/lanes \
  --output groups/<group>/<domain>/<lifecycle>/reviews/<plugin>/coverage.yml

python3 <skill_dir>/scripts/skill_review_coverage.py check \
  --input groups/<group>/<domain>/<lifecycle>/reviews/<plugin>/coverage.yml \
  --require-complete
```
