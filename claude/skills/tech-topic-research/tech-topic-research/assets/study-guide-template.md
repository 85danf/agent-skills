# Study Guide Template

Use this structure when writing the final study guide document.

## Frontmatter

```yaml
---
topic: "{topic}"
date: "{YYYY-MM-DD}"
as_of: "{YYYY-MM-DD}" # from Phase 1 Step 1
depth: "{quick|standard|deep}"
sources_consulted: { count }
---
```

## Sections

Include all sections for Standard tier. Sections marked `*` are Deep-only.

1. **TL;DR** — 2–3 sentences (from gist).
2. **What It Is** — core explanation + mental model + ecosystem context.
3. **Key Concepts** — each with a plain-language explanation; apply "So What?"
   to the top 3–5.
4. **How It Works** — simplified mental model (not implementation details).
5. **Getting Started** — prerequisites, install, hello world, first real use,
   common pitfalls.
6. **Common Patterns** — 2–3 integration patterns.
7. **If You Only Remember 3 Things** — key takeaways.
8. \***Strengths & Weaknesses** — with confidence levels + source URLs.
9. \***Alternatives** — comparison table: name, best for, trade-off, source.
10. \***Community Sentiment** — praise, complaints, trend direction with
    evidence.
11. \***When to Use / When NOT to Use** — decision guide with real scenarios.
12. **Further Reading** — annotated links.
13. **Sources** — all sources with quality ratings (A–E).
14. **Methodology Appendix** — search angles run, the **Run ledger**, AS_OF
    date, any mid-run refinements (what changed, why, which extra subagents
    ran).

    The **Run ledger** captures actual run shape for post-hoc audit:

    ```yaml
    run_ledger:
      tier_claimed: standard | deep
      comparison_mode: false | true
      subagents_spawned: <count>
      models_used:
        haiku: <count>
        opus: <count>
        sonnet: <count>
      refinements: <count, 0 or 1>
      timeouts: [<role>, <role>]
      gaps: [<gap-description>, ...]
      tier_a_b_count_per_item: # comparison mode only
        item1: <count>
        item2: <count>
    ```
