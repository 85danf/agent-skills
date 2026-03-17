# Analysis Tools

## Confidence Criteria

For deep-analyst when rating claims.

| Level           | Definition                                                                | Example                                                                 |
|-----------------|---------------------------------------------------------------------------|-------------------------------------------------------------------------|
| **HIGH**        | Multiple independent authoritative sources agree; verified with data      | "Redis stores data in memory" — docs + universal experience             |
| **MEDIUM**      | 2+ sources (some non-authoritative); OR single authoritative unconfirmed  | "Redis faster than PG for caching" — generally true, workload-dependent |
| **LOW**         | Single non-authoritative; OR community consensus without official backing | "Redis Cluster is hard to operate" — some agree, others don't           |
| **SPECULATIVE** | Extrapolation, single opinion, forward-looking                            | "Redis will add vector search" — trajectory, not announced              |

---

## "So What?" Engine

Apply to the 3-5 most important concepts in Phase 4.

| Question         | Purpose                      | Example ("Pods are ephemeral")                                                    |
|------------------|------------------------------|-----------------------------------------------------------------------------------|
| **SO WHAT?**     | Why this matters in practice | Store data in pod -> lose on restart. Design stateless or use persistent volumes. |
| **NOW WHAT?**    | Concrete next step           | Use Deployments for lifecycle, PVCs for data.                                     |
| **WHAT IF?**     | Consequences of ignoring     | Lose data during rolling updates, scaling, node failures.                         |
| **COMPARED TO?** | Compare to something known   | Unlike a VM that persists, a pod is like a process — start, stop, replace.        |

Apply selectively — not every concept needs all four questions.

---

## Source Quality Ratings

For all agents when rating sources.

| Rating | Definition                                                    |
|--------|---------------------------------------------------------------|
| **A**  | Official documentation, peer-reviewed, primary source         |
| **B**  | Reputable industry reports, maintained community resources    |
| **C**  | Expert blogs, technical writing from recognized practitioners |
| **D**  | General community content, forum posts, preliminary sources   |
| **E**  | Anecdotal, speculative, potentially biased or outdated        |

---

## Quality Checklist

Run in Phase 7 before delivering the final document.

- [ ] Gist was delivered before research results (Phase 1 speed)
- [ ] All key concepts have plain-language explanations (no unexplained jargon)
- [ ] Getting Started steps are concrete and actionable (not just "install it")
- [ ] Claims in Strengths/Weaknesses have confidence levels (Deep tier)
- [ ] "When NOT to use" contains real scenarios, not strawmen (Deep tier)
- [ ] All source URLs included in Sources section
- [ ] Document follows the template structure
- [ ] Content matches user's stated familiarity level and goal
- [ ] Comparison mode: both items get equal treatment (if applicable)

**Deep tier:** Read `agents/synthesis-reviewer.md` and apply the reviewer checklist. Address HIGH severity issues before delivery.
