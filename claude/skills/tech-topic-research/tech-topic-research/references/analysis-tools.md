# Analysis Tools

> **For spawned subagents:**
>
> - `deep-analyst` → § Confidence Criteria (the HIGH/MEDIUM/LOW/SPECULATIVE rubric you apply to every claim).
> - `synthesis-reviewer` → § Quality Checklist (Phase 7 qualitative checks) and § Deep-tier numeric gates (the must-pass list before Deep delivery).

## Confidence Criteria

For deep-analyst when rating claims.

| Level           | Definition                                                                | Example                                                                 |
| --------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **HIGH**        | Multiple independent authoritative sources agree; verified with data      | "Redis stores data in memory" — docs + universal experience             |
| **MEDIUM**      | 2+ sources (some non-authoritative); OR single authoritative unconfirmed  | "Redis faster than PG for caching" — generally true, workload-dependent |
| **LOW**         | Single non-authoritative; OR community consensus without official backing | "Redis Cluster is hard to operate" — some agree, others don't           |
| **SPECULATIVE** | Extrapolation, single opinion, forward-looking                            | "Redis will add vector search" — trajectory, not announced              |

### Negative, superlative, and bundled claims (verify before asserting)

Three claim shapes routinely get over-rated. Apply these caps:

- **Negative / absence claims** ("X does NOT support Y", "there is no Z", "no API
  workaround exists"). A negative is only as strong as the source you checked it
  against. **Do not assert a negative at HIGH/MEDIUM unless you WebFetched the
  primary doc (vendor API reference, official changelog) and confirmed the
  absence in the relevant section.** A search that simply didn't surface the
  feature is LOW at best — mark it `[unverified]` and say "not found in <source>",
  never "does not exist". Beware truncated/paginated docs: a feature absent from
  the fetched portion is not absent from the product.
- **Superlatives / comparatives** ("best", "only", "strongest", "better than X",
  "the leading"). These are claims about the whole comparison class. Cap at
  MEDIUM unless you actually enumerated the alternatives and verified the
  ranking; if you checked only some, downgrade to LOW and name which you
  compared.
- **Bundled claims** ("A and B are both the strongest"). Split and rate each
  sub-claim separately — A may be HIGH while B is LOW. One confidence label must
  not cover sub-claims with different support.

---

## "So What?" Engine

Apply to the 3–5 most important concepts in Phase 4.

| Question         | Purpose                      | Example ("Pods are ephemeral")                                                   |
| ---------------- | ---------------------------- | -------------------------------------------------------------------------------- |
| **SO WHAT?**     | Why this matters in practice | Store data in pod → lose on restart. Design stateless or use persistent volumes. |
| **NOW WHAT?**    | Concrete next step           | Use Deployments for lifecycle, PVCs for data.                                    |
| **WHAT IF?**     | Consequences of ignoring     | Lose data during rolling updates, scaling, node failures.                        |
| **COMPARED TO?** | Compare to something known   | Unlike a VM that persists, a pod is like a process — start, stop, replace.       |

Apply selectively — not every concept needs all four questions.

---

## Source Quality Ratings

For all agents when rating sources.

| Rating | Definition                                                    |
| ------ | ------------------------------------------------------------- |
| **A**  | Official documentation, peer-reviewed, primary source         |
| **B**  | Reputable industry reports, maintained community resources    |
| **C**  | Expert blogs, technical writing from recognised practitioners |
| **D**  | General community content, forum posts, preliminary sources   |
| **E**  | Anecdotal, speculative, potentially biased or outdated        |

---

## Quality Checklist

Run in Phase 7 before delivering the final document.

- [ ] Gist was delivered before any subagent results (Phase 1 speed).
- [ ] All key concepts have plain-language explanations (no unexplained jargon).
- [ ] Getting Started steps are concrete and actionable (not just "install it").
- [ ] Claims in Strengths/Weaknesses have confidence levels (Deep tier).
- [ ] "When NOT to use" contains real scenarios, not strawmen (Deep tier).
- [ ] All source URLs included in the Sources section.
- [ ] Document follows the template structure.
- [ ] Content matches the user's stated familiarity level and goal.
- [ ] Comparison mode: both items get equal treatment (if applicable).

**Deep tier:** Spawn synthesis-reviewer for critical review. Address every
HIGH-severity issue before delivery.

### Deep-tier numeric gates

The qualitative checklist above applies to every tier. The Deep tier additionally
fails if any of these gates are missed:

- [ ] \>= 8 sources cited in the document.
- [ ] \>= 3 sources per major claim (independent sources, not three blog posts
      that cite each other).
- [ ] \>= 2 confidence-tagged weaknesses, with confidence levels from the table
      above. "It might not scale" is not a weakness; "Cluster operations
      require dedicated SRE time per the v3.4 release notes [synthetic example, HIGH]" is.
- [ ] \>= 1 "do NOT use" scenario in the When to Use / When NOT to Use section,
      naming real alternatives.
- [ ] \>= 1 alternative comparison row in the alternatives table.
- [ ] AS_OF date present on every time-sensitive citation; sources older than
      12 months downgraded by one tier (see `source-quality.md`).
- [ ] \>= 80% of paragraphs are prose (bullets only for genuine lists).

If any Deep-tier gate fails, return to Phase 6 and fix it. Do not deliver.
