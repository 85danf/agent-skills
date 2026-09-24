# Per-Source Summary Template

Use this template **only in Deep tier** when the document cites more than eight
sources. Each cited source gets its own short summary file under
`<study-guide-dir>/summaries/<slug>.md`. The main study guide cites these via
`[[<slug>]]` so a reviewer can verify a claim by opening one summary.

```markdown
---
created: <YYYY-MM-DD>
source_url: <verified URL>
source_tier: <A | B | C | D> (see references/source-quality.md)
as_of: <YYYY-MM or YYYY>
---

# <Source Title>

**URL:** <source_url>
**Author / Org:** <name or org>

## Citation

<Full citation: author, date, publisher, DOI or URL>

## Key Findings (max 5)

1. <one-sentence finding from the source>
2. <one-sentence finding>
   ...

## Notable Quote

> "<direct quote, scoped to the part that supports the cited claim>"

## Evidence Quality

- Strengths: <one line>
- Limitations: <one line>
- Possible biases: <one line>

## Used in the report for

- Section: <section title>
- Claim: <which claim in that section this source backs>
```

## When to skip

- Quick or Standard tier — do not generate per-source summaries.
- Deep tier with ≤ 8 sources — fold the equivalent context inline.
