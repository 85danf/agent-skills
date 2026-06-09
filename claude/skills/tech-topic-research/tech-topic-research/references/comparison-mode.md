# Comparison Mode

> **For spawned subagents:** `comparison-searcher` reads § Equal-treatment rule for the per-item FFS minimum and the Phase 7 numeric audit. Other roles do not need this file.

Comparison mode is triggered automatically in Phase 0 when the user's prompt
contains `vs`, `versus`, `compared to`, or `or` between two or more named
items. The lead agent confirms comparison mode before continuing.

This file collects every comparison-specific rule the workflow needs, so each
phase in `SKILL.md` can simply say "see `references/comparison-mode.md`"
instead of repeating the same callouts.

## Per-phase behaviour

| Phase                         | Comparison-mode behaviour                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Phase 1 (Gist)**            | Deliver a brief gist for _each_ item, then state the single key differentiator.                                                                                                                                                                                                                                                                                                                                                                   |
| **Phase 2 (Clarify)**         | Focus-area options derive from the comparison dimensions (performance, ecosystem, ease of use, cost, maturity, lock-in, license).                                                                                                                                                                                                                                                                                                                 |
| **Phase 3 (Fan-out)**         | If "alternatives" or "comparison" is a focus area — or always in comparison mode — also spawn `agents/comparison-searcher.md`.                                                                                                                                                                                                                                                                                                                    |
| **Phase 4 (Explanation)**     | Side-by-side concept comparison; each item gets its own column.                                                                                                                                                                                                                                                                                                                                                                                   |
| **Phase 5 (Getting started)** | Two parallel "Getting started with X" subsections, equal length.                                                                                                                                                                                                                                                                                                                                                                                  |
| **Phase 6 (Deep dive)**       | Side-by-side strengths and weaknesses tables. Add a "Which one for your situation" decision framework using `assets/comparison-guide-template.md`.                                                                                                                                                                                                                                                                                                |
| **Phase 7 (QA)**              | Verify each item received equal research effort and equal source-quality treatment. **Loop-back contract:** for HIGH issues in items' explanation sections (At a Glance / Key Differences / Side-by-Side / Community Verdict) → return to Phase 4. For issues in decision-oriented sections (Decision Guide / Migration Considerations / Sources) → return to Phase 6. Span-both → earlier. One loop-back cap shared with the numeric-gate audit. |

## Equal-treatment rule (mandatory)

Each item under comparison receives:

- The same number of subagent searches.
- The same source-tier mix (see `source-quality.md`).
- The same depth of analysis in every section.

**Per-item FFS minimum.** Phase 4 may not start until each item has all four searcher results (per the SKILL.md First-finish-search rule). Asymmetric synthesis is forbidden. If one side has thinner findings, re-spawn that side's searcher and rerun Phase 4–6 for that side before delivering. Never publish an asymmetric comparison.

**Phase 7 numeric audit (mandatory).** Before delivery, count Tier-A + Tier-B sources for each item from the JSON envelope. If `|item1.A+B − item2.A+B| > 1`, re-spawn the lighter side's searcher pool (or the specific searcher role whose category is underrepresented) and re-run Phase 6 for that side. Record the audit count in the Methodology Appendix even when it passes.

## Output template

Use `assets/comparison-guide-template.md` for the final document instead of
`assets/study-guide-template.md`.
