---
name: deep-research
description: Use when the user wants to learn about, understand, or evaluate a technology, tool, framework, concept, or methodology — or compare two or more of them. Triggers on "what is X", "teach me X", "X vs Y", "help me understand X", "should I use X", "study X"
---

# Study Topic

Structured teaching flow: gist, informed questions, research, progressive explanation.

## Overview

Teach any topic through progressive disclosure. Deliver value immediately with a preliminary gist, then deepen research based on user needs.

**Two modes:** Single topic (default) or Comparison (when 2+ items detected).

**Three depth tiers:**

| Tier     | Phases          | Subagents      | Deliverable              |
|----------|-----------------|----------------|--------------------------|
| Quick    | 0-1-2           | 0              | Conversational gist      |
| Standard | 0-1-2-3-4-5+QA  | 4 (Haiku)      | Gist + study guide       |
| Deep     | All phases + QA | 5-6 + reviewer | Gist + comprehensive doc |

## Skill Directory

Supporting files are in the same directory as this SKILL.md. Read them on-demand at the phases indicated below.

- `agents/` — Agent prompt templates (read and paste into Task tool prompts)
- `reference/` — Search strategies, teaching tone, analysis tools
- `templates/` — Output document templates

## Phase 0: Topic Input

Parse topic from `/deep-research [topic]`.

- No topic provided: ask for one.
- Comparison detected ("vs", "versus", "compared to", "or" between named items, 2+ items listed): confirm comparison mode.

## Phase 1: Preliminary Assessment & Gist

**Main agent only. No subagents.** Runs BEFORE asking any clarification questions.

1. Run 1-2 `WebSearch` calls for a current overview of the topic.
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

Use `AskUserQuestion` with 4 questions informed by Phase 1 findings:

1. **Depth**: Quick / Standard (Recommended) / Deep
2. **Familiarity**: new to this / heard of it / tried it / used it regularly
3. **Goal**: evaluate for adoption / learn to use / understand concepts / prepare for interview
4. **Focus areas** (multiSelect, options derived from Phase 1 dimensions): "I found these key areas of {topic}: [dim1], [dim2], [dim3], [dim4]. Which interest you most?"

**If depth = Quick:** STOP here. Offer to go deeper later.

**Comparison mode:** Focus area options derived from comparison dimensions (performance, ecosystem, ease of use, etc.).

## Phase 3: Research Plan & Subagent Spawning

1. Formulate research plan based on gist + user answers.
2. Read `reference/teaching-tone.md` to determine tone adaptation.
3. Spawn subagents — ALL in a **single message** for parallel execution, ALL with `run_in_background: true`.

**Standard depth — spawn 4 subagents.** Read these agent files and paste their contents into the Task tool prompt:

- `agents/docs-searcher.md` (model: haiku)
- `agents/community-searcher.md` (model: haiku)
- `agents/tutorial-searcher.md` (model: haiku)
- `agents/integration-searcher.md` (model: haiku)

**Deep depth — add 1-2 more:**

- `agents/deep-analyst.md` (model: opus) — always for Deep
- `agents/comparison-searcher.md` (model: haiku) — if alternatives are a focus, or always in comparison mode

For each agent, also read the relevant section of `reference/search-strategies.md` and include it in the prompt.

**Subagent invocation template:**

```
Task tool parameters:
  subagent_type: "general-purpose"
  model: "{model}"
  run_in_background: true
  description: "{agent_role} for {topic}"
  prompt: |
    You are executing the {agent_role} role for a deep-research research task.

    ## Your Instructions
    {paste full content from agents/*.md}

    ## Search Strategy
    {paste relevant section from reference/search-strategies.md}

    ## Assignment
    - Topic: {topic}
    - Focus areas: {focus_areas}
    - Context from preliminary assessment: {gist_summary}
    - User familiarity: {familiarity}
    - User goal: {goal}

    ## Output
    Deliver findings in the format specified in your instructions.
```

4. Proceed to Phase 4 — begin drafting with own knowledge + Phase 1 findings while subagents run.

## Phase 4: Practical Explanation

Wait for docs-searcher and community-searcher results (check output files via Read).

Read `reference/teaching-tone.md` for tone. Read the "So What? Engine" section of `reference/analysis-tools.md`.

Compile and deliver conversationally:

- Core concepts and terminology with plain-language explanations
- How it works (simplified mental model, not implementation details)
- Key use cases with concrete examples
- Apply "So What?" engine to 3-5 most important concepts
- Common misconceptions

**Comparison mode:** Side-by-side concept comparison.

## Phase 5: Getting Started / Integration

Wait for tutorial-searcher and integration-searcher results.

Compile and deliver:

- Step-by-step getting started (install, hello world, first real use)
- Integration patterns (ecosystem connections)
- Common pitfalls and how to avoid them
- "If you only remember 3 things" — key takeaways

**If depth = Standard:** Write final document using `templates/study-guide.md`. Run QA from `reference/analysis-tools.md`. STOP.

**Comparison mode:** "Which one for your situation" decision framework. Use `templates/comparison-guide.md`.

## Phase 6: Deep Dive (Deep tier only)

Wait for deep-analyst results.

Compile:

- Strengths with confidence levels (see `reference/analysis-tools.md`)
- Weaknesses and limitations
- Alternatives comparison table
- Community sentiment summary
- Caveats and edge cases
- "When to use / When NOT to use" decision guide
- Further reading (curated, annotated links)

Write comprehensive document using `templates/study-guide.md` (or `templates/comparison-guide.md` for comparison mode).

## Phase 7: Quality Assurance

Run the Quality Checklist from `reference/analysis-tools.md`.

**Deep tier only:** Spawn synthesis-reviewer using `agents/synthesis-reviewer.md` (model: sonnet). Address HIGH severity issues before delivery.

## Anti-Patterns

| Don't                                 | Do Instead                                            |
|---------------------------------------|-------------------------------------------------------|
| Ask generic questions before research | Research first (Phase 1), then ask informed questions |
| Spawn subagents for Quick depth       | Quick = 0 subagents, gist only                        |
| Wait for all subagents before talking | Deliver gist immediately, add depth as results arrive |
| Include broken URLs                   | Verify every URL with WebFetch                        |
| Soften genuine weaknesses             | Red-team: actively search for reasons NOT to use      |
| Treat comparison items unequally      | Each item gets its own research, equal treatment      |
