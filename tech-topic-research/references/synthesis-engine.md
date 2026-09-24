# Synthesis Engine

Use this reference in Phase 4 (drafting the practical explanation) and Phase 6
(Deep-tier dive) to convert raw subagent findings into insights, not just facts.

## 1. Triangulate

Cross-reference findings across subagent outputs.

- A claim with three or more **independent** sources agreeing → high-confidence.
- A claim with one source → mark `[unverified]` or downgrade to LOW confidence
  (see `analysis-tools.md`).
- Conflicting sources → surface the conflict explicitly; do not pick a side
  silently.

## 2. Pattern recognition

Look across all findings for four pattern types:

| Pattern         | Definition                                           | What it tells you                                        |
| --------------- | ---------------------------------------------------- | -------------------------------------------------------- |
| **Convergence** | Multiple unrelated sources reach the same conclusion | High-confidence finding                                  |
| **Divergence**  | Two clear camps disagree                             | Both may be correct in different contexts; document both |
| **Silence**     | A topic that _should_ appear but doesn't             | Either too new or actively suppressed; flag explicitly   |
| **Trend**       | Directional shift across time                        | Note the direction and the date span                     |

## 3. Fact → Insight

A fact is `X happened`. An insight is `X happened + context + implication`.

| Fact                                  | Insight                                                                                                                                                                                                    |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "Vendor X launched feature Y in 2024" | "Vendor X launched feature Y in 2024, signalling that Y is now table-stakes for new entrants. Anyone evaluating the space now needs to match Y rather than treat it as a differentiator."                  |
| "Project A has 12k GitHub stars"      | "Project A has 12k GitHub stars and grew 4× in the last year, but issue close rate dropped from 60% to 18% over the same period — suggesting maintainer bandwidth is the real bottleneck, not popularity." |

Every major finding in Phase 4–6 must be elevated from fact to insight. If a
finding cannot be elevated, it is filler — drop it.

## 4. Red-team

Before finalising the document, attempt to disprove the emerging narrative.
This is mandatory in Deep tier, recommended in Standard.

Run through these questions:

- What is the strongest argument **against** the conclusion forming here?
- What would need to be true for the opposite conclusion to hold?
- Is there survivorship bias? (Are we only seeing the cases that worked?)
- Is there recency bias? (Are we overweighting last quarter's news?)
- Is there source bias? (Are most sources from one camp?)
- What would a sceptical practitioner say about this finding?

Surface the strongest counter-argument in the final document. If the conclusion
survives red-team, state that it survived and why. If the red-team raises real
doubts, flag them prominently.

## When to load this file

- Phase 4: load before drafting the practical explanation.
- Phase 6: load before writing strengths/weaknesses and "when NOT to use".
