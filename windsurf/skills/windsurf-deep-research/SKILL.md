---
name: windsurf-deep-research
description: Use when the user wants to learn about, understand, or evaluate a technology, tool, framework, concept, or methodology — or compare two or more of them.
---

# Deep Research

Structured teaching flow: gist, informed questions, research, progressive explanation.

## Overview

Teach any topic through progressive disclosure. Deliver value immediately with a preliminary gist, then deepen research based on user needs.

**Two modes:** Single topic (default) or Comparison (when 2+ items detected).

**Three depth tiers:**

| Tier     | Phases          | Research Tracks | Deliverable              |
|----------|-----------------|-----------------|--------------------------|
| Quick    | 0-1-2           | 0               | Conversational gist      |
| Standard | 0-1-2-3-4-5+QA  | 4               | Gist + study guide       |
| Deep     | All phases + QA | 5-6 + review    | Gist + comprehensive doc |

## Skill Directory

Supporting files are in the same directory as this SKILL.md. They are **not** auto-loaded — read them explicitly and only when needed (progressive disclosure) to avoid context bloat. Use absolute paths with Cascade's read_file tool.

- `agents/` — Research guides for each research track.
- `reference/` — Search strategies, teaching tone, analysis tools (read only when needed).
- `templates/` — Output document templates (read when composing final output).

## Phase 0: Topic Input

Parse topic from the user’s request. If invoked via `@deep-research`, treat the remaining text as the topic.

- No topic provided: ask for one.
- Comparison detected ("vs", "versus", "compared to", "or" between named items, 2+ items listed): confirm comparison mode.

## Phase 1: Preliminary Assessment & Gist

Runs BEFORE asking any clarification questions.

1. Run 1-2 web searches for a current overview of the topic using Cascade's search_web tool. Read the top results with read_url_content to ground the gist.
2. Deliver gist conversationally to the user:
   - **What it is** — 2-3 sentences
   - **Why it matters** — the problem it solves
   - **Where it fits** — ecosystem context
   - **Mental model** — one-liner analogy ("Think of it as...")
3. Internally note key dimensions for Phase 2:
   - Main subtopics/areas
   - Recent developments or controversies
   - Common use cases
   - Related/competing technologies

**Comparison mode:** Brief gist of EACH item + the key differentiator.

## Phase 2: Informed Clarification

Ask the user 4 questions informed by Phase 1 findings using Cascade's ask_user_question tool:

1. **Depth**: Quick / Standard (Recommended) / Deep
2. **Familiarity**: new to this / heard of it / tried it / used it regularly
3. **Goal**: evaluate for adoption / learn to use / understand concepts
4. **Focus areas** (multiSelect, options derived from Phase 1 dimensions): "I found these key areas of {topic}: [dim1], [dim2], [dim3], [dim4]. Which interest you most?"

**If depth = Quick:** STOP here. Offer to go deeper later.

**Comparison mode:** Focus area options derived from comparison dimensions (performance, ecosystem, ease of use, etc.).

## Phase 3: Research Plan & Research Execution

1. Formulate research plan based on gist + user answers.
2. Read `reference/search-strategies.md` using the read_file tool and extract the relevant sections for each research track.
3. Read `reference/analysis-tools.md` using the read_file tool and use the **Source Quality Ratings** (A–E) for every source you collect.
4. Read `reference/teaching-tone.md` using the read_file tool to determine tone adaptation.
5. Execute research tracks sequentially. Use Cascade's todo_list tool to track progress.

**Standard depth — 4 research tracks:**

- `agents/docs-searcher.md`
- `agents/community-searcher.md`
- `agents/tutorial-searcher.md`
- `agents/integration-searcher.md`

**Deep depth — add 1-2 more:**

- `agents/deep-analyst.md` — always for Deep
- `agents/comparison-searcher.md` — if alternatives are a focus, or always in comparison mode

**For each research track:**

1. Read the agent file using the read_file tool
2. Read the relevant section of `reference/search-strategies.md`
3. Execute the searches and analysis described, adapted for:
   - Topic: {topic}
   - Focus areas: {focus_areas}
   - Context from preliminary assessment: {gist_summary}
   - User familiarity: {familiarity}
   - User goal: {goal}
4. Collect findings in the output format specified in the agent file, including source quality ratings (A-E)

6. Proceed to Phase 4 after completing docs-searcher and community-searcher tracks.

## Phase 4: Practical Explanation

Use the docs-searcher and community-searcher findings gathered in Phase 3.

Read `reference/teaching-tone.md` for tone. Read the "So What? Engine" section of `reference/analysis-tools.md`.

Compile and deliver conversationally:

- Core concepts and terminology with plain-language explanations
- How it works (simplified mental model, not implementation details)
- Key use cases with concrete examples
- Apply "So What?" engine to 3-5 most important concepts
- Common misconceptions

**Comparison mode:** Side-by-side concept comparison.

## Phase 5: Getting Started / Integration

Use the tutorial-searcher and integration-searcher findings gathered in Phase 3.

Compile and deliver:

- Step-by-step getting started (install, hello world, first real use)
- Integration patterns (ecosystem connections)
- Common pitfalls and how to avoid them

- "If you only remember 3 things" — key takeaways

Read the template you will use before writing:

- Standard depth: read `templates/study-guide.md`
- Comparison mode: read `templates/comparison-guide.md`

**If depth = Standard:** Write final document using `templates/study-guide.md`. Run QA from `reference/analysis-tools.md`. STOP.

**Comparison mode:** "Which one for your situation" decision framework. Use `templates/comparison-guide.md`.

## Phase 6: Deep Dive (Deep tier only)

Use the deep-analyst findings gathered in Phase 3.

Compile:

- Strengths with confidence levels (see `reference/analysis-tools.md`)
- Weaknesses and limitations
- Alternatives comparison table
- Community sentiment summary
- Caveats and edge cases
- "When to use / When NOT to use" decision guide

- Further reading (curated, annotated links)

Read the template you will use before writing:

- Single topic: read `templates/study-guide.md`
- Comparison mode: read `templates/comparison-guide.md`

Write comprehensive document using `templates/study-guide.md` (or `templates/comparison-guide.md` for comparison mode).

## Phase 7: Quality Assurance

Read `reference/analysis-tools.md`, then run the Quality Checklist section.

**Deep tier only:** Read `agents/synthesis-reviewer.md` and apply the reviewer checklist yourself. Address HIGH severity issues before delivery.

## Anti-Patterns

| Don't                                            | Do Instead                                                 |
|--------------------------------------------------|------------------------------------------------------------|
| Ask generic questions before research            | Research first (Phase 1), then ask informed questions      |
| Execute multiple research tracks for Quick depth | Quick = focus on gist only                                 |
| Wait to complete all research before talking     | Deliver gist immediately, add depth as research progresses |
| Include broken URLs                              | Verify every URL by opening the page                       |
| Soften genuine weaknesses                        | Red-team: actively search for reasons NOT to use           |
| Treat comparison items unequally                 | Each item gets its own research, equal treatment           |
