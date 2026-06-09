# Search Strategies

> **For spawned subagents:** if a tech-topic-research role file (`agents/<role>.md`) sent you here, read the section that matches your role:
>
> - `docs-searcher` → § Official Documentation
> - `community-searcher` → § Community Discussions
> - `tutorial-searcher` → § Tutorials
> - `integration-searcher` → § Official Documentation + § Tutorials (no dedicated section; integration-specific guidance is embedded in your role file)
> - `comparison-searcher` → § Comparison Content
> - `deep-analyst` → § Comparison Content + § Debugging and Issues

Include the relevant section in each search agent's prompt.

## Official Documentation

**Where:** Official project/product websites, GitHub READMEs/wikis/docs,
official blogs, release notes, API references.

**Query patterns:**

- `"{topic} documentation"`, `"{topic} official guide"`
- `"site:{known_official_domain} {topic}"`
- `"{topic} API reference"`, `"{topic} changelog latest version"`

**Quality signals:** Official domain, updated within 12 months, version numbers
present, maintained by core team.

**Red flags:** Community wikis, old version docs without an update notice,
auto-generated without explanation.

---

## Community Discussions

**Where:** Reddit (r/programming, r/webdev, r/devops, r/experienceddevs,
topic-specific subs), HN (hn.algolia.com), Dev.to, Hashnode, Lobsters,
Twitter/X.

**Query patterns:**

- `"{topic} site:reddit.com experience"` or `"worth it"`
- `"{topic} site:news.ycombinator.com"`
- `"{topic} frustrating" OR "love" OR "honest review"`
- `"{topic} in production experience {current_year} / {current_year + 1}"`

**Sentiment signals:** Repeated complaints = pain point, repeated praise =
strength, upvote patterns = agreement, "switched from X because…" = decision
factors.

**Recency:** Prioritise the last 12 months. Older threads are useful for
tracking sentiment evolution.

---

## Tutorials

**Where:** Official quickstarts (highest priority), Dev.to/Hashnode/Medium,
"Awesome {topic}" GitHub lists, YouTube companions, interactive platforms.

**Query patterns:**

- `"{topic} getting started tutorial {current_year} / {current_year + 1}"`,
  `"{topic} quickstart guide"`
- `"{topic} hello world example"`, `"{topic} beginner step by step"`
- `"awesome {topic}" site:github.com`

**Quality signals:** Runnable code, stated prerequisites/versions, recent,
expected output shown, builds something real.

**Assessment dimensions:** Difficulty, prerequisites, completeness
(full/partial/overview), recency.

---

## Comparison Content

**Where:** "X vs Y" blog posts, benchmark repos, migration guides, Reddit/HN
debates, official comparison pages.

**Query patterns:**

- `"{item1} vs {item2}"`, `"versus {current_year} / {current_year + 1}"`
- `"migrate from {item1} to {item2}"`, `"{item1} or {item2} for {use_case}"`
- `"{item1} {item2} benchmark"`, `"why I switched from {item1} to {item2}"`
  (both directions)

**Fairness evaluation:** Balanced treatment, same criteria for both, recent
data, affiliation disclosed, methodology shown for benchmarks.

**Dimensions:** Performance, ease of setup/learning curve, community size,
docs quality, production readiness, cost, extensibility.

---

## Debugging and Issues

**Where:** GitHub Issues (open and closed), Stack Overflow / Stack Exchange,
project-specific bug trackers, project Discord/Slack archives, mailing lists.

**Query patterns:**

- `"<exact error message>" site:github.com` (use double quotes around the
  message; truncate timestamps and PIDs)
- `"<error message>" site:stackoverflow.com`
- `<library name> "<error message>" closed` (closed issues hold the
  resolution patterns)
- `<library name> <version> regression` for version-specific bugs
- `<library name> "workaround" OR "work around"` to find practitioner fixes
  before official patches

**Quality signals:** A closed issue with a linked merged PR, a
reproducer-attached bug report, a maintainer's `wontfix` with a stated reason,
a Stack Overflow answer with code that currently runs.

**Red flags:** Generic "I have the same problem" comments, AI-generated answers
without citations, advice from before a major version bump.

**Recency:** For fast-moving projects, prioritise issues closed in the last six
months. Older threads are useful for tracking sentiment evolution but rarely
contain the current fix.

---

## Mid-Run Outline Refinement

When the initial fan-out (Phase 3) returns evidence that points at angles you
did not plan for in Phase 2, **adjust the search before drafting Phase 4**.
This is the WebWeaver pattern: prevent locked-in research when the territory
turns out to differ from the map.

**When to refine (any one of these triggers it):**

- Multiple subagents independently surface a topic that was not in the
  Phase 2 focus areas.
- A subagent's findings directly contradict the Phase 1 gist.
- A critical sub-topic emerges that the original plan did not name.
- The original question was scoped too broadly or too narrowly given what
  the evidence shows.

**When to keep the current plan:** the evidence aligns with the gist, and all
key angles have substantive findings.

**How to refine (time-boxed, 2–5 minutes):**

1. Note in one sentence what the evidence revealed that the plan missed.
2. Spawn 1–2 targeted searcher subagents (not a full re-run) for the new
   angle. Use the existing `agents/<role>.md` template, not a new one.
3. Run those subagents in parallel via the same Task / `run_in_background`
   pattern as Phase 3.
4. Wait for the targeted results, then proceed to Phase 4.

**Quality bounds:**

- No more than one refinement loop per run.
- Refinement may not change the original research question — only the angle
  emphasis or a missing sub-topic.
- The new angle must already have supporting evidence in hand from the first
  fan-out; do not refine on speculation.

**Anti-patterns:**

- Refining the outline because the new angle "would be interesting".
- Adding sections without evidence already gathered.
- Drifting into a different topic entirely.

Document the refinement in the Methodology Appendix of the final document
(what changed, why, and which extra subagents ran).
