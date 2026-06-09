# Subagent Output Envelope

> **For spawned subagents:** if a tech-topic-research role file (`agents/<role>.md`) sent you here, read § Shape and § Anti-fabrication. The Shape section is the JSON envelope you must produce verbatim; Anti-fabrication is the WebFetch-every-URL discipline and the `[unverified]` cap rule.

Every researcher subagent spawned in Phase 3 returns a markdown document
**plus** a JSON envelope at the end. The envelope is the structured contract
that Phase 4–6 synthesise against; do not omit it. The free-form markdown
above the envelope keeps each per-prompt format spec intact (so the existing
`agents/<role>.md` instructions still apply); the envelope makes synthesis
cheap and reduces the chance of fabricated URLs surviving the merge.

Phase 3's invocation template pastes this section's contents into every
subagent prompt verbatim, so this reference is the single source of truth
for the envelope shape.

## Shape

```json
{
  "subagent": "{role}",
  "topic": "{topic}",
  "run_as_of": "<YYYY-MM-DD anchored at Phase 1 Step 1>",
  "findings": [
    {
      "title": "<source title>",
      "url": "<verified URL>",
      "source_tier": "A | B | C | D",
      "key_finding": "<one-sentence finding>",
      "confidence": "HIGH | MEDIUM | LOW | SPECULATIVE",
      "as_of": "<source publication YYYY-MM or YYYY>"
    }
  ],
  "gaps": ["<what you searched for but could not find>"]
}
```

## Field semantics

- **`subagent`** — the role name (e.g. `docs-searcher`, `community-searcher`).
- **`topic`** — the user's research topic, copied from the assignment.
- **`run_as_of`** — today's date (YYYY-MM-DD), anchored in Phase 1 Step 1.
  This is the **run anchor**, not a source date. Phase 4–6 use this as the
  reference point for the AS_OF freshness gate.
- **`findings[]`** — one entry per source you cite. Do not include sources
  you could not WebFetch successfully.
  - **`title`** — the source's actual title.
  - **`url`** — the verified URL (must have returned 2xx from WebFetch in
    this run).
  - **`source_tier`** — A | B | C | D per
    [`source-quality.md`](source-quality.md) tier definitions. Tier E
    sources are "do not cite" — they should not appear in this list.
  - **`key_finding`** — one sentence stating what this source contributes.
  - **`confidence`** — HIGH | MEDIUM | LOW | SPECULATIVE per the Confidence
    Criteria in [`analysis-tools.md`](analysis-tools.md).
  - **`as_of`** — the source's own publication date (YYYY-MM, or YYYY when
    month is unknown). Distinct from `run_as_of` at the top level.
- **`gaps`** — short strings describing what you searched for but could
  not find. Phase 4–6 surface these as explicit limitations.

## Anti-fabrication (mandatory)

This is the **canonical** anti-fabrication contract for the tech-topic-research skill. SKILL.md and `troubleshooting.md` cross-reference this block; do not duplicate the wording elsewhere.

1. **WebFetch every URL before listing it.** A URL that has not returned 2xx in the current run does not exist for synthesis purposes.
2. **On 4xx/5xx, drop the URL.** Do not substitute a different URL with the same title. Do not mark the URL `[broken]` and ship it. Do not retry indefinitely (one retry maximum).
3. **Never invent a URL on a real domain to fill a citation gap.** Citation hallucination is the highest-severity failure mode of this skill.
4. **`[unverified]` is the bounded escape valve.** When a claim is informationally valuable but unsupported, mark it `[unverified]` in the markdown body and **omit it from the JSON envelope**. Caps: ≤ 10% of total claims; **forbidden in Strengths, Weaknesses, and the Alternatives table**. The synthesis-reviewer flags HIGH severity if either cap is breached.

These rules apply to every subagent and to the main agent's synthesis. Phase 7's qualitative checklist and Deep-tier numeric gates assume this contract holds.

## When to load this file

- Phase 3: Phase 3's invocation template pastes this entire reference
  (or its key sections) into every subagent prompt. The subagent reads
  the envelope shape from here.
- Phase 4–6: synthesis reads each subagent's envelope and aggregates by
  `findings[].source_tier`, `findings[].confidence`, and `gaps`.
