# Comparison Guide Template

Use this structure when writing comparison documents (2+ items).

## Frontmatter

```yaml
---
topic: "{item1} vs {item2}"
date: "{YYYY-MM-DD}"
as_of: "{YYYY-MM-DD}" # from Phase 1 Step 1
depth: "{quick|standard|deep}"
sources_consulted: { count }
---
```

## Sections

1. **TL;DR** — key differentiator + when to pick each.
2. **At a Glance** — table: what it is, best for, mental model (per item).
3. **Key Differences** — per dimension: item1 approach vs item2 + verdict
   with source.
4. **Side-by-Side Comparison** — full table with sources per dimension.
5. **Getting Started with Each** — 2–3 steps per item.
6. **Community Verdict** — what practitioners recommend + in which scenarios.
7. **Decision Guide** — "Choose X if…" / "Choose Y if…" / "Consider both if…".
8. **Migration Considerations** — both directions.
9. **Sources** — all sources with quality ratings (A–E).
10. **Methodology Appendix** — search angles run, the **Run ledger**, AS_OF
    date, any mid-run refinements. For comparison mode, confirm equal-treatment
    audit: same source-tier mix and same number of subagent searches per item.

    The **Run ledger** (same shape as the study-guide template):

    ```yaml
    run_ledger:
      tier_claimed: standard | deep
      comparison_mode: true
      subagents_spawned: <count>
      models_used:
        haiku: <count>
        opus: <count>
        sonnet: <count>
      refinements: <count, 0 or 1>
      timeouts: [<role>, <role>]
      gaps: [<gap-description>, ...]
      tier_a_b_count_per_item:
        item1: <count>
        item2: <count>
    ```
