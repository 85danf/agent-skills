# Source Quality Tiers

> **For spawned subagents:** every tech-topic-research role applies these tiers when classifying sources. Tag each source A/B/C/D — Tier E is do-not-cite (omit). Time-sensitive topics: downgrade sources older than 12 months by one tier per the AS_OF freshness gate.

Use this reference whenever you cite a source in a Phase 4–7 document.

## Tier definitions

| Tier  | Definition                               | Examples                                                                                                         |
| ----- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **A** | Primary, peer-reviewed, or official      | Standards bodies, government data, academic papers, official docs, audited filings                               |
| **B** | Reputable industry or technical analysis | Industry analyst reports with stated methodology, maintainer blog posts with disclosures, conference proceedings |
| **C** | Expert practitioner content              | Recognised-author technical blogs, deep podcast/interview transcripts                                            |
| **D** | General community signal                 | Forum threads, Q&A answers, average Dev.to/Medium posts, generic StackOverflow answers                           |
| **E** | Anecdotal or unverifiable                | Single tweets, marketing pages, undated content, content with no author                                          |

## Per-tier usage gates

Apply these gates in Phase 4 (Standard) and Phase 6 (Deep).

| Tier  | Standard depth                                               | Deep depth                                         |
| ----- | ------------------------------------------------------------ | -------------------------------------------------- |
| **A** | 1 source can support a claim                                 | 1 source can support a claim                       |
| **B** | 1 source if A is unavailable; cite freshness date            | 2 sources required for a claim                     |
| **C** | 2 sources required for a claim                               | 2 sources required + at least one A or B alongside |
| **D** | Supporting evidence only — never the sole source for a claim | Same                                               |
| **E** | Do not cite                                                  | Do not cite                                        |

## Tier signals (how to assign)

- Date present, author named, methodology disclosed → can be A or B.
- Domain matches the source's own product (e.g. vendor blog) → at most B.
- No date or no author → E by default.
- Conflict between sources → keep the higher-tier source, note the conflict.

## Time-sensitive topics

For technology versions, market data, or regulatory state: downgrade any source
older than 12 months by one tier. See `analysis-tools.md` AS_OF policy.
