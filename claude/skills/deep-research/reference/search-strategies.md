# Search Strategies

Include the relevant section in each search agent's prompt.

## Official Documentation

**Where:** Official project/product websites, GitHub READMEs/wikis/docs, official blogs, release notes, API references.

**Query patterns:**
- `"{topic} documentation"`, `"{topic} official guide"`
- `"site:{known_official_domain} {topic}"`
- `"{topic} API reference"`, `"{topic} changelog latest version"`

**Quality signals:** Official domain, updated within 12 months, version numbers present, maintained by core team.

**Red flags:** Community wikis, old version docs without update notice, auto-generated without explanation.

---

## Community Discussions

**Where:** Reddit (r/programming, r/webdev, r/devops, r/experienceddevs, topic-specific subs), HN (hn.algolia.com), Dev.to, Hashnode, Lobsters, Twitter/X.

**Query patterns:**
- `"{topic} site:reddit.com experience"` or `"worth it"`
- `"{topic} site:news.ycombinator.com"`
- `"{topic} frustrating" OR "love" OR "honest review"`
- `"{topic} in production experience {current_year}  / {current_year + 1}"`

**Sentiment signals:** Repeated complaints = pain point, repeated praise = strength, upvote patterns = agreement, "switched from X because..." = decision factors.

**Recency:** Prioritize last 12 months. Older threads useful for tracking sentiment evolution.

---

## Tutorials

**Where:** Official quickstarts (highest priority), Dev.to/Hashnode/Medium, "Awesome {topic}" GitHub lists, YouTube companions, interactive platforms.

**Query patterns:**
- `"{topic} getting started tutorial {current_year} / {current_year + 1}"`, `"{topic} quickstart guide"`
- `"{topic} hello world example"`, `"{topic} beginner step by step"`
- `"awesome {topic}" site:github.com`

**Quality signals:** Runnable code, stated prerequisites/versions, recent, expected output shown, builds something real.

**Assessment dimensions:** Difficulty, prerequisites, completeness (full/partial/overview), recency.

---

## Comparison Content

**Where:** "X vs Y" blog posts, benchmark repos, migration guides, Reddit/HN debates, official comparison pages.

**Query patterns:**
- `"{item1} vs {item2}"`, `"versus {current_year} / {current_year + 1}"`
- `"migrate from {item1} to {item2}"`, `"{item1} or {item2} for {use_case}"`
- `"{item1} {item2} benchmark"`, `"why I switched from {item1} to {item2}"` (both directions)

**Fairness evaluation:** Balanced treatment, same criteria for both, recent data, affiliation disclosed, methodology shown for benchmarks.

**Dimensions:** Performance, ease of setup/learning curve, community size, docs quality, production readiness, cost, extensibility.
