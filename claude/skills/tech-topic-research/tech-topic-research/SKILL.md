---
name: tech-topic-research
description: >
  Research a technology, tool, framework, concept, or methodology — or
  compare two or more of them — through a progressive flow: preliminary gist
  delivered immediately from web search, informed clarifying questions, then
  parallel subagent research synthesised into a conversational explanation or
  a written study guide. Use when the user wants to learn about, evaluate, or
  compare technologies, products, libraries, services, or methodologies.
metadata:
  author: Dan Feldman
  version: "1.0"
disable-model-invocation: true
compatibility: >
  Requires a Claude Code-style host that exposes WebSearch, WebFetch, the Task
  tool with native subagent registration (each `agents/<role>.md` is registered
  as `subagent_type: "<role-name>"`), run_in_background subagents, and
  AskUserQuestion. The skill is read-only: it issues web searches and reads web
  pages, never writes to remote services. No config file or credentials are
  required.
---

# Deep Research

Teach or evaluate a topic through progressive disclosure. Deliver a useful gist
within seconds, then deepen the answer with parallel web research and a written
study guide when the user wants more.

## When to use this skill

Use this skill when the user explicitly invokes it with a topic, or when the
user asks to:

- Learn about, understand, or evaluate a technology, tool, framework, library,
  service, concept, or methodology.
- Compare two or more such items ("X vs Y", "X or Y for {use case}",
  "compared to Z").
- Decide whether to adopt a tool, prepare for an interview on a topic, build a
  mental model, or get a curated reading list.

**This skill is invoked only by explicit user request — never autonomously.** The frontmatter flag `disable-model-invocation: true` blocks auto-matching; hosts that don't honor it MUST still refuse without an explicit user request. Explicit invocation is consent to _consider_ running the skill; the [Token cost and approval gate](#token-cost-and-approval-gate) (Phase 1 step 5) still applies.

## When NOT to use this skill

Skip this skill — it is the wrong tool — when:

- The user wants a single-fact lookup ("what version of X ships JSONB?", "who
  is the CEO of Y?"). One WebSearch call answers it.
- The user is debugging a specific error and wants a fix. Use a debugging
  workflow, not a research one.
- The user wants a quick sanity check or a yes/no answer.
- The user already has a clear opinion and just wants confirmation.
- The user explicitly asks for "a quick answer" or "in one sentence".

If you are not sure whether the request is research or a lookup, default to
the lookup — research is opt-in, see the next section.

## Token cost and approval gate

> ⚠️ **This skill is heavy on token usage.** A Standard run spawns four
> parallel haiku subagents, each issuing 4–6 web searches and several
> WebFetch calls. A Deep run adds an Opus subagent and a Sonnet reviewer.
> Total cost is typically **5–30× a normal turn**, and the subagent fan-out
> cannot be cancelled mid-flight.

### Estimated cost per run

| Tier                  | Subagents                                                | Typical token cost     | Typical wall-clock |
| --------------------- | -------------------------------------------------------- | ---------------------- | ------------------ |
| **Quick**             | 0 (gist only)                                            | ~1× a normal turn      | <1 minute          |
| **Standard**          | 4 × Haiku searchers                                      | ~5–12× a normal turn¹  | 2–5 minutes        |
| **Deep**              | 4–6 searchers + Opus analyst + Sonnet reviewer           | ~15–35× a normal turn¹ | 5–15 minutes       |
| **Comparison (Deep)** | Standard's pool, ×2 (one per item) + comparison-searcher | ~25–60× a normal turn¹ | 10–20 minutes      |

¹ Per-call prompts ~200–400 tokens. Niche topics retrying queries run 1.5–2× higher. Hosts without main-loop WebSearch add **+1 haiku** (`docs-searcher` in gist mode for Phase 1) — Quick → ~2× a normal turn; other tiers shift up one haiku.

### Confirm cost before continuing

After Phase 1's gist and **before** the Phase 2 questions, run the gate as **two ordered steps**:

**Step A — render the "Estimated cost per run" table above as a visible chat message** (include the comparison-mode rows in comparison mode). This is the cost-disclosure moment; it MUST be its own scannable message, not folded into the gate options.

**Step B — the gate** as an `AskUserQuestion` with these options:

- **Standard** — 4 Haiku searchers in parallel, ~5–12× tokens, 2–5 min.
- **Deep** — Standard's pool + Opus analyst + Sonnet reviewer, ~15–35× tokens, 5–15 min.
- **Stop here** — keep just the gist (Quick depth — no additional tokens).

In **comparison mode** (Phase 0 detected `vs` / `versus` / `compared to` / `or`), the multipliers double — use these options instead:

- **Standard (Comparison)** — 8 Haiku searchers, ~10–25× tokens, 5–10 min.
- **Deep (Comparison)** — 8 Haiku + Opus analyst×2 + comparison-searcher + Sonnet reviewer, ~25–60× tokens, 10–20 min.
- **Stop here** — keep the per-item gists (Quick depth).

Wait for the user's answer before invoking `AskUserQuestion` for the Phase 2 questions. If the user picks "stop", the gist (or per-item gists in comparison mode) is the final answer — do not run Phase 2.

This gate is mandatory: explicit invocation is consent to _consider_ the skill, not to spend Deep-tier tokens. Auto-mode and YOLO-mode hosts MUST still halt, render the table (Step A), and surface the gate rather than auto-selecting a tier.

If `AskUserQuestion` is unavailable in this host, fall back to a plain conversational prompt — still lead with the rendered cost table (Step A), then ask the option set in chat — and do not call any subsequent tool until the user replies.

## Capability profile

This is a **local-only research skill**. Capabilities split by enforcement source:

### Host-enforced (the host should withhold these tools when invoking this skill)

- Touching credentials, customer data, production data, or external mutable APIs.
- Persistent state between invocations.
- Reading or writing secrets directories.

If your host does not withhold these tools, the agent self-restricts — but you have weaker isolation than the skill's design assumes.

### Agent-enforced (the skill self-restricts even when the host grants the tool)

- The skill MAY have Bash and Read available on permissive hosts (Claude Code default). It MUST NOT use them to read user repository files outside this skill directory, run shell commands beyond `date +%Y-%m-%d` for the AS_OF anchor, or persist any output beyond the user-named study-guide file path.
- If the user is the subject of the research, the skill MUST restrict to public sources and report what an external investigator could verify. Using the user's private dashboards or accounts is circular reasoning, not research. (Refuse a request that would breach this.)

### What it CAN do (no approval / public-web only)

- Issue WebSearch and WebFetch calls against public sources.
- Spawn parallel `Task`-tool subagents that also use WebSearch and WebFetch.
- Ask the user clarifying questions through the host's question UI (`AskUserQuestion`).
- Write or print a study guide into the current conversation or to the user-named file path.

Risk classification (no-approval / user-confirmation / bounded / fresh): see [`references/capability-risk.md`](references/capability-risk.md). Bounded approval allows writing the user-named study-guide file plus `<user_path>/summaries/<slug>.md` siblings (Phase 6 with >8 sources); fresh approval is unsupported. Subagent fan-out requires user confirmation via the Token cost gate.

## Prerequisites

1. The host runtime exposes the tools listed in `compatibility:` above. If
   `Task` / `run_in_background` is unavailable, the skill falls back to
   sequential WebSearch from the main agent (Quick depth only).
2. The user has supplied a topic. If not, ask for one before any web search.
3. No configuration file or credentials are required.

## Configuration

This skill has no separate config file. All knobs are inputs collected during
the workflow: topic, depth tier, familiarity level, goal, and focus areas.

## Pre-flight checks

No script-based preflight is required because the skill calls only host-provided
tools. Before starting Phase 1, confirm in this order:

1. A topic is present. If not, ask the user for one.
2. The host advertises WebSearch and WebFetch. If neither is available, stop
   and report that deep research cannot run on this host.
3. The host advertises the Task tool with native subagent registration (each
   `agents/<role>.md` is registered as `subagent_type: "<role-name>"`) and
   `run_in_background`. If not, restrict the run to **Quick depth** (gist
   only) and tell the user why.

## Skill Directory

Supporting files split across two locations:

- `agents/<role>.md` lives at the **plugin root**
  (`plugins/tech-topic-research/agents/`) — required so Claude Code registers
  them as native subagents (`subagent_type: "<role-name>"`). The body is
  the spawned subagent's full system prompt; no paste at fan-out.
- `references/` (alongside this SKILL.md) — search strategies, teaching
  tone, analysis tools, source-quality tiers, comparison-mode rules,
  synthesis engine.
- `assets/` (alongside this SKILL.md) — output and plan templates.

## Workflow

Always follow this sequence. Never skip Phase 1 or Phase 2 — Phase 1 informs
the questions Phase 2 asks.

### Phase 0 — Topic input

Parse the topic from the user's message.

- If no topic was provided, ask for one and stop.
- If two or more named items appear with `vs`, `versus`, `compared to`, or `or`
  between them, confirm comparison mode before proceeding.

### Phase 1 — Preliminary assessment and gist

**Main agent only. No subagents.** This phase runs **before** any clarifying
questions.

1. **Step 1: Anchor the current date.** Before any WebSearch, retrieve today's
   date with `date +%Y-%m-%d` (host shell). If Bash is unavailable, read it
   from the host's system message. Otherwise **ask the user** — never guess
   from training data. Save as `{current_date}` and `{current_year}`; pass
   them into per-call subagent prompts that need a freshness anchor.
2. **Get a current overview from the live web. Mandatory — never
   gist from training data alone.** Try main-agent WebSearch; if it
   returns "tool not available", spawn one `docs-searcher` subagent
   in gist mode (`Mode: gist` → 5-bullet gist, +1 haiku, footnote ¹).
   If both fail, stop and tell the user the host has neither live-web
   nor `docs-searcher`. Do NOT fall back to training data.
3. Deliver the gist conversationally:
   - **What it is** — 2–3 sentences.
   - **Why it matters** — the problem it solves.
   - **Where it fits** — ecosystem context.
   - **Mental model** — one analogy ("Think of it as…").
   - **Confidence:** HIGH / MEDIUM / LOW based on how much the WebSearch
     results agreed with each other and how recent they were
     (see [`references/analysis-tools.md`](references/analysis-tools.md)
     Confidence Criteria for definitions).
4. Internally note the key dimensions Phase 2 will offer as focus-area
   options: main subtopics, recent developments or controversies, common use
   cases, related/competing technologies.
5. **Stop. Run the [token-cost approval gate](#token-cost-and-approval-gate)**
   — render the cost table (Step A), then the gate (Step B). Do not proceed to
   Phase 2 until the user has explicitly picked Standard, Deep, or stop.

**Comparison mode (Phase 1):** see [`references/comparison-mode.md`](references/comparison-mode.md).

### Phase 2 — Informed clarification

Phase 2 only runs after the user picked **Standard** or **Deep** at the
[token-cost approval gate](#token-cost-and-approval-gate) (Phase 1 step 5).
If the user picked "stop", the gist is the final answer — do not run Phase 2.

Depth is already established by the gate. Use `AskUserQuestion` (or the
host's equivalent) for the three remaining questions, informed by Phase 1:

1. **Familiarity**: new to this / heard of it / tried it / use it regularly.
2. **Goal**: evaluate for adoption / learn to use / understand concepts /
   prepare for interview.
3. **Focus areas** (multi-select; options derived from the Phase 1 dimensions).

**Comparison mode (Phase 2):** see [`references/comparison-mode.md`](references/comparison-mode.md).

### Phase 3 — Research plan and subagent fan-out

1. Formulate the plan from the gist plus the user's answers. Use the
   skeleton in
   [`assets/research-plan-template.md`](assets/research-plan-template.md).
   Show the filled plan to the user before fanning out — if the user
   redirects (different focus, narrower scope, new angle), update the plan
   and confirm before any subagent is spawned. **When filling the plan,
   explicitly initialize `refinement_state.used = false`,
   `refinement_state.what = ""`, `refinement_state.subagents_added = []`.
   This reset is mandatory before fan-out.**
2. Read `references/teaching-tone.md` and use it to shape the explanation
   style.
3. Spawn subagents. **All in a single message**, all with
   `run_in_background: true`, so they run in parallel.

**Standard depth** spawns four searcher subagents (haiku): `agents/docs-searcher.md` (`subagent_type: "docs-searcher"`), `agents/community-searcher.md` (`"community-searcher"`), `agents/tutorial-searcher.md` (`"tutorial-searcher"`), `agents/integration-searcher.md` (`"integration-searcher"`).

**Deep depth** adds `agents/deep-analyst.md` (`"deep-analyst"`, opus, always) and `agents/comparison-searcher.md` (`"comparison-searcher"`, haiku, when alternatives are a focus area or always in comparison mode).

**Comparison mode** doubles each searcher pool — spawn each role **twice**, once per item. The `comparison-searcher` is single-instance and receives both items. See [`references/comparison-mode.md`](references/comparison-mode.md) for equal-treatment rules.

### Subagent invocation pattern (native registration)

Each `agents/<role>.md` is a registered Claude Code subagent. Spawn via Task tool with `subagent_type: "<role-name>"`; the role body becomes the spawned subagent's system prompt — no paste step. The worker reads its assignment from `prompt:` and loads canonical references via `Read`.

```text
Task tool parameters:
  subagent_type: "docs-searcher"   # from agents/<role>.md frontmatter
  description: "docs-searcher for {topic}"
  run_in_background: true
  prompt: |
    Topic: {topic}
    Focus areas: {focus_areas}
    Gist summary: {gist_summary}
    User familiarity: {familiarity}
    User goal: {goal}
```

Do not pass `model:` or paste the role body — both come from `agents/<role>.md`. For `comparison-searcher`, the topic field carries both items plus a `comparison_mode: true` line. Spawn the wave in one multi-tool message. Structured output envelope contract canonical in [`references/output-envelope.md`](references/output-envelope.md); spawned subagents `Read` it themselves.

While subagents run, draft Phase 4 from your own knowledge plus Phase 1 findings.

#### First-finish-search early exit

Do not block waiting for the slowest subagent. As soon as you have:

- For Standard: docs-searcher **and** community-searcher **and** tutorial-searcher **and** integration-searcher results.
- For Deep: the above plus deep-analyst results.

…proceed to Phase 4 even if a refinement-loop subagent (see below) is still running. Its results merge into Phase 5 / Phase 6 as it finishes.

In **comparison mode**, the FFS rule applies **per item**: each item must have all four searcher results before Phase 4 starts. If item A is complete and item B is not, do not start Phase 4.

If any required subagent has not returned by its timeout (see "Timeout thresholds" below), the run fails. Tell the user explicitly which role timed out and stop. Do not synthesize on incomplete data.

**Deep tier deep-analyst exception.** **This exception overrides the preceding fail-on-timeout rule for the `deep-analyst` role only.** If `deep-analyst` (Opus) has not returned by its 25-minute timeout while every other Deep-required subagent has, do not silently downgrade. Stop, surface the timeout to the user, and ask whether to (a) wait an additional 10 minutes, (b) downgrade to Standard delivery and write the final document without the red-team / strengths-and-weaknesses sections, or (c) abort. Default to (c).

**Timeout thresholds.** A subagent that has not returned **15 minutes from its
own spawn time** (Standard) or **25 minutes from its own spawn time** (Deep)
is considered timed out. The budget is **per-subagent**, not aggregate;
comparison mode keeps the same per-subagent budget (the doubled pool does not
get a doubled budget). Drop the timed-out subagent from the result set, fail
the run if a required FFS subagent is missing (see FFS rule above), and note
the gap in the final document's Methodology Appendix. Do not retry; proceed
with the subagents that did return only when FFS is satisfied.

#### Mid-run outline refinement (optional, time-boxed)

When the first wave of findings reveals an angle the Phase 2 plan did not name, see [`references/search-strategies.md`](references/search-strategies.md) § "Mid-Run Outline Refinement" for the full protocol. Capped at **one** refinement loop per run (Standard/Deep only); forbidden on Quick depth. Refinement state is tracked in the research-plan template's `refinement_state` field.

#### AS_OF freshness gate

For time-sensitive topics every cited source must carry a publication date and the final document must record an `AS_OF` value (anchored in Phase 1 Step 1). Stale sources downgrade or disqualify per [`references/freshness-gate.md`](references/freshness-gate.md). Apply these rules before drafting Phase 4.

### Phase 4 — Practical explanation

By the FFS rule, all four searcher results are present at this point. Read
[`references/synthesis-engine.md`](references/synthesis-engine.md) for the
triangulate → patterns → fact-to-insight → red-team protocol, then
[`references/teaching-tone.md`](references/teaching-tone.md) for tone
adaptation, then the **So What? Engine** section of
[`references/analysis-tools.md`](references/analysis-tools.md). Deliver
conversationally:

- Core concepts and terminology, in plain language.
- A simplified mental model of how it works (not implementation details).
- Key use cases with concrete examples.
- "So What?" applied to 3–5 of the most important concepts.
- Common misconceptions.

**Comparison mode (Phase 4):** see [`references/comparison-mode.md`](references/comparison-mode.md).

### Phase 5 — Getting started / integration

Tutorial-searcher and integration-searcher results are guaranteed present at this point per the FFS rule. Deliver:

- Step-by-step getting started: install, hello world, first real use.
- Integration patterns and ecosystem connections.
- Common pitfalls and how to avoid them.
- "If you only remember 3 things" — key takeaways.

If depth is **Standard**, write the final document using
[`assets/study-guide-template.md`](assets/study-guide-template.md) (or
[`assets/comparison-guide-template.md`](assets/comparison-guide-template.md)
for comparison mode), then proceed to Phase 7. Standard tier skips Phase 6
(Deep dive) and runs Phase 7's qualitative Quality Checklist before delivery.

**Comparison mode (Phase 5):** see [`references/comparison-mode.md`](references/comparison-mode.md).

### Phase 6 — Deep dive (Deep tier only)

Wait for the deep-analyst result. Re-load
[`references/synthesis-engine.md`](references/synthesis-engine.md) — the
red-team subsection is mandatory in Deep tier. Compile:

- Strengths with confidence levels (see `references/analysis-tools.md`).
- Weaknesses and limitations.
- Alternatives comparison table.
- Community sentiment summary.
- Caveats and edge cases.
- "When to use / When NOT to use" decision guide.
- Further reading: curated, annotated links.

Write the comprehensive document using
[`assets/study-guide-template.md`](assets/study-guide-template.md) (or
[`assets/comparison-guide-template.md`](assets/comparison-guide-template.md)
for comparison mode). Cite every source by tier per
[`references/source-quality.md`](references/source-quality.md). When the
final document cites more than eight sources, also write a per-source
mini-summary for each one using
[`assets/source-summary-template.md`](assets/source-summary-template.md),
saved alongside the study guide under `summaries/<slug>.md`, so a reviewer
can verify any single claim by opening one summary.

**Comparison mode (Phase 6):** see [`references/comparison-mode.md`](references/comparison-mode.md).

### Phase 7 — Quality assurance (all tiers)

Phase 7 runs for both Standard and Deep tiers. Run the qualitative
Quality Checklist from
[`references/analysis-tools.md`](references/analysis-tools.md) before
delivering any document.

**For the Deep tier additionally**, run the **Deep-tier numeric gates**
subsection of the same reference. If any gate fails, return to Phase 6 —
do not ship a Deep document that fails the canonical list.

**For the Deep tier additionally**, spawn
[`agents/synthesis-reviewer.md`](../../agents/synthesis-reviewer.md) (model: sonnet)
as a final reviewer. The reviewer reads the drafted Deep document and emits
issues at HIGH / MEDIUM / LOW severity.

**Loop-back contract on HIGH issues.** Address every HIGH issue before delivery:

- Issues in **What it is / Key concepts / How it works / Common patterns** → return to **Phase 4** and re-synthesize the affected section using the existing subagent envelopes (no fresh fan-out).
- Issues in **Strengths / Weaknesses / Alternatives / Community sentiment / When to use vs not** → return to **Phase 6** and re-compile the affected section.
- Issues that span both classes → return to the earlier of Phase 4 or Phase 6, then re-run Phase 7.

Cap loop-backs at **one** per Deep run. The numeric-gate loop-back above (Phase 7 Deep-tier numeric gates) counts toward this cap; a Deep run executes at most **one** Phase 4-or-Phase 6 retry across both gate failures and reviewer HIGH issues. If a second loop-back would be required, surface the residual HIGH issues to the user and ship the document with those issues marked at the top under "Known limitations after review".

**Comparison mode (Phase 7):** see [`references/comparison-mode.md`](references/comparison-mode.md).

**Run ledger.** Before delivery, populate the Methodology Appendix's `run_ledger` block in the final document. The ledger is required even when nothing went wrong (this lets a reviewer verify the actual run shape matched the declared tier). For comparison mode, also fill `tier_a_b_count_per_item` from the equal-treatment audit (see `references/comparison-mode.md` Phase 7 numeric audit).

## Operations

This skill has one operation, the staged research workflow above. There are no
scripts, no CLI commands, no destructive actions, and no `--dry-run` modes —
everything happens through host-provided tools.

## Important rules

1. **Deliver the gist before asking questions.** Phase 1 must complete before
   Phase 2; the user gets value within seconds.
2. **Quick depth uses zero subagents.** Do not fan out for a Quick request.
3. **Spawn all subagents in a single message** with `run_in_background: true`
   so they run in parallel.
4. **WebFetch every URL before including it; drop URLs that 4xx/5xx without substitution.** Canonical contract in [`references/output-envelope.md` § Anti-fabrication](references/output-envelope.md).
5. **Red-team with hard counts in Deep tier.** Before delivering a Deep
   document, every Deep-tier numeric gate in
   [`references/analysis-tools.md`](references/analysis-tools.md) must
   pass. If any gate fails, return to Phase 6 and fix it before delivery.
6. **Treat comparison items equally.** Each item gets its own research and
   the same depth.
7. **Read-only by default.** Never write to remote services. If the user asks
   the skill to save the study guide to a file path, treat that as a bounded
   approval — write only to the path the user named.
8. **Hardcoded subagent contract.** This skill assumes Claude Code's Task
   tool with **native subagent registration** (each `agents/<role>.md` as
   `subagent_type: "<role-name>"`) and `run_in_background: true` for the
   parallel fan-out. On hosts lacking either, restrict the run to Quick
   depth and tell the user — do not attempt a paste-based fallback.
9. **Never fabricate a citation.** If you cannot find a supporting source for a claim, mark it `[unverified]` (subject to the 10% cap and forbidden-zones rule). Canonical: see [`references/output-envelope.md` § Anti-fabrication](references/output-envelope.md).
10. **`[unverified]` is the bounded escape valve.** When a claim is informationally
    valuable but unsupported by the gathered sources, keep the claim and
    mark it `[unverified]`. Apply these caps to prevent abuse:
    - At most **10%** of total claims in any delivered document may be `[unverified]`.
    - `[unverified]` is **forbidden in Strengths, Weaknesses, and the Alternatives table** — those sections require sourced confidence levels (HIGH / MEDIUM / LOW / SPECULATIVE per `references/analysis-tools.md`).
    - The synthesis-reviewer flags HIGH severity if either cap is breached.

    The user can then triage `[unverified]` claims. This is preferable to
    dropping useful information silently or to inventing a citation.

## Error handling, troubleshooting, anti-patterns

Triage tables (Error handling, Troubleshooting, Anti-patterns) live in
[`references/troubleshooting.md`](references/troubleshooting.md). Load
that reference when the workflow hits an error condition, when a
behavior seems off, or during Phase 7 to check the document does not
exhibit any anti-pattern.
