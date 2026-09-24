---
name: plugin-creator
description: >
  Create, refactor, review, and improve Agent Skills — portable skills for Claude Code, OpenAI
  Codex, or any other agent host, plus the Claude Code plugin components around them when
  authoring specifically for Claude Code. Use when the user wants to: turn a script into a
  reusable skill, create a skill from scratch, refactor or split an existing skill, review skill
  quality, or (Claude Code only) decide whether a capability should be a skill, command, hook,
  subagent, MCP server, LSP, or monitor. Covers local-only skills and external-resource skills
  needing API config, credentials, approval gates, and risk documentation. Portable by default:
  the core methodology (creation-cost vs proof-cost, the 10-section SKILL.md body, context
  engineering, script-first authoring) applies to any host; Claude Code plugin-specific sections
  (hooks/commands/MCP/LSP components, the am-pm monorepo placement step) are marked and skippable.
metadata:
  author: Sagy Ashlag, Israel Abudi (original); ported for portable/Codex use
  version: "1.2-portable"
  lifecycle: stable
  standalone: true
compatibility: >
  Requires Python 3.10+ and PyYAML (`pip install PyYAML==6.0.3`). The `claude` CLI is optional,
  needed only for `Step 6b`'s Claude Code-only live invocation check.
---

# Plugin Creator

Create, update, review, and validate Agent Skills for any host — Claude Code, Codex, or
elsewhere. Stronger requirements apply to skills touching APIs, credentials, customer/
production data, or destructive operations.

**Portability note.** Originally written for authoring Claude Code plugins inside the "am-pm"
plugin monorepo. Its core methodology — creation-cost/proof-cost, when a skill is the right tool
at all, the 10-section SKILL.md body, context engineering, script-first authoring — is
platform-agnostic. Genuinely Claude Code plugin-specific steps (optional plugin components:
hooks, commands, subagents, MCP, LSP, monitors; the am-pm placement/duplication-check step;
`.claude-plugin/plugin.json` authoring) are marked **"Claude Code plugin-specific — skip for a
portable/Codex-only skill"**. Never skip a step without that marking; always skip one that carries
it when not authoring a Claude Code plugin (or not inside am-pm, for the monorepo-only step).

## Principles

These bind on every skill creation, any host. Doctrine for a single Claude Code plugin component
lives under `references/components/` (Claude Code-specific throughout).

**Approval boundary.** Scope approval authorizes one target-aware plan artifact; target skill
source stays gated until the saved plan reaches `plan-approved` at the second gate.

### The core trade — creation cost against proof cost

A skill is cheap to build and expensive to trust on any host: a description and some markdown —
almost nothing constrains it, which is why it works immediately and why you can never prove it
fires. **Claude Code-specific:** every *other* plugin component (hook, subagent, MCP, LSP,
monitor, command) earns its reliability by restricting itself to what a machine can decide, so the
question there is never *which component is best*, but **is what I am encoding genuinely
expressible deterministically?** Yes and it matters → pay the creation cost, buying provability.
No → do not force it. On a portable/Codex-only skill this collapses to: the skill is what you
have, so write its trigger and behavior as unambiguous as prose can make them.

### Do not force components, do not over-engineer

Skill-only is the **expected** outcome, never a gap. **Claude Code-specific:** the failure to
avoid is not "too few hooks" but **a hook that approximates a judgement call** — harder to build
than the skill it replaces and still only an approximation. Record deliberately omitted
components and why in `## 12. Key Design Decisions` of `references/PLAN_TEMPLATE.md` — on a
portable skill this is simply "skill only — no other components exist on this host."

### Popularity is not correctness

Adoption is not evidence of fit. Never rank components by how often they appear in a repo, or
reject one because nothing there uses it. Rank by the core trade's question.

### Every component states aim, advantage, cost, and when NOT to use it (Claude Code-specific)

A component whose cost you cannot name is one nobody weighed. Before proposing one, state what it
is for, what it buys, what it costs, and when it is wrong. Not applicable to a portable skill,
which has no components to propose.

### Context engineering — the cost is correctness, not tokens

Irrelevant context degrades judgment: the model misreads intent and anchors on the wrong details.
That cost is correctness, not tokens — hard size caps, progressive disclosure, and single-source
content all follow from it. Carry only what is needed at each surface; put the rest behind a
pointer that says when to follow it. Applies on every host.

### Script-first

Every added agent step is a reasoning decision that can go wrong; a script is deterministic,
testable, debuggable. Script repeatable logic with known inputs; merge redundant script calls —
but not past where the script gets harder to read than the step it replaces. Every host.

### Track state explicitly

In-prompt checklists (or a Task-tool equivalent) for small in-session work; committed state files
for multi-step workflows and plans — the review coverage matrix is the example. Every host; a
hook is one Claude Code way to enforce it.

## Quality criteria routing

This skill owns Agent Skill quality standards, applicable on any host. Source of truth:
`assets/skill-quality-criteria.json`; `references/lanes/*.md` are derived from it. To change
standards, edit the JSON and run `scripts/generate_quality_artifacts.py`.

Lanes serve both phases — author guidance while creating, review prompts while completing the
coverage matrix. Explicitly open and read the lane files; content is not auto-populated.

While creating a skill, open only the relevant lane reference:

<!-- skill-creator-lane-routing:start -->
Resolve the active lane set for the current repo before opening criteria:

```bash
python3 <skill_dir>/scripts/skill_review_coverage.py active-lanes --repo-root . --format references
```

Open only the lane reference files printed by that command. If no repo policy is configured, the resolver uses the generic plugin profile.
<!-- skill-creator-lane-routing:end -->

That command prints paths, not what each lane covers. Route by what you are writing:

| Writing | Lane |
|---|---|
| defaults, setup, discovery, local vocabulary, installed use, compatibility | `genericity`, `installed-use` |
| external actions, sensitive data, approval behavior, enforcement | `risk` |
| CLI contracts, output formats, preflight behavior, tests, agent-step economy | `runtime` |
| **Claude Code plugin components only** — commands, subagents, hooks, MCP, LSP, monitors | `component-fit` |
| detailed schemas, checklists, format specs, examples | none — belongs in a reference, not `SKILL.md` |

Use `references/SKILL_QUALITY_CRITERIA.md` only as an index for every lane together. Each lane's
checklist is also in `references/lanes/<lane>.md` (see [Step 7 — Review](#step-7--review)).

## Capability profile

This skill reads local skill source, criteria JSON, Markdown references, changelog fragments,
review matrices, and git diffs supplied by the user. It writes local skill files, generated
references, review-lane result tables, review matrices, and verification artifacts. Generator
cleanup is scoped to `references/criteria/*.md`. `Step 6 — Readback` sends the target skill's
agent-facing surface to the model API in full (the rest listed by path/heading) and — Claude Code
plugin-specific only — can spawn an unsandboxed `claude -p` running commands in `<workdir>`.
Review dispatch can place full diffs in prompt/result files and call a subagent or backend
command, so inspect diffs for secrets first.

## When to use this skill

Use this skill when the user wants to:

- Convert a working script into a reusable, generic Agent Skill
- Create a new Agent Skill from scratch (with or without existing code)
- Refactor or improve an existing SKILL.md, or generate its frontmatter/body content
- Review a skill change for quality, runtime contracts, repo integration, risk, and review completeness
- Apply prompt engineering best practices to skill instructions
- (Claude Code plugin-specific) Decide whether a capability should be a skill, command, hook, subagent, MCP server, LSP, or monitor, and author that component

## Pre-flight checks

Run the preflight script before first use:

```bash
python3 <skill_dir>/scripts/sc_preflight.py
```

One pass over Python version (3.10+), PyYAML, the `claude` CLI, scripts, reference docs, and
quality artifacts. Exit 0 = passed, 1 = at least one `[FAIL]`. A standalone install `[WARN]`s that
plugin-level review agent files are unavailable — the skill still works, using
`references/lanes/*.md` directly. Missing PyYAML: `pip install PyYAML==6.0.3`. A missing `claude`
CLI blocks only `Step 6b` (Claude Code-specific).

## Review coverage

A shared-repo change needs a committed review coverage matrix, every row decided, at a
`reviews/<skill>/coverage.yml` path (Claude Code plugin-specific default:
`groups/<g>/<d>/<lifecycle>/reviews/<plugin>/coverage.yml`; use your own repo's equivalent outside
that monorepo). **Read [references/REVIEW_COVERAGE.md](references/REVIEW_COVERAGE.md) before you
run anything** — command sequence and the secret-scrubbing rule for a diff reaching a sub-agent.

## Workflow

Always follow this sequence; never skip the analysis or plan steps — only the Step 0 table drops
one. There are no modes: the path comes from the diff, not what you call the work.

### Step 0 — Declare the path

Step 0 precedes every path. Run the classifier on the target before you start, and again on the
real diff before you verify — the second answer is binding, and earns a change the cheap path
rather than inheriting one on an empty diff. The user may override; you may not decide silently.

```bash
python3 <skill_dir>/scripts/classify_change.py --plugin-dir <target> --base-ref <merge-target> --repo-root .
```

(For a portable skill with no `.claude-plugin/plugin.json`, `--plugin-dir` still works — it
classifies on `SKILL.md`/`references/`/`scripts/`/`assets/` changes; plugin.json fields never fire.)

| Path | Trigger | Runs | Dropped |
|---|---|---|---|
| **New** | target skill doesn't exist at the base ref | every step, both gates, readback, live invocation | — |
| **Behavior change** | diff touches `SKILL.md`, or (Claude Code plugin-specific) `agents/`, `hooks/`, `commands/`, `monitors/`, `.mcp.json`, `.lsp.json`, or a `plugin.json` field beyond version/author/license/repository/homepage | design gate, implementation gate, readback, live invocation, active lanes | scope confirmation |
| **Mechanical** | diff touches only scripts, tests, assets or reference wording | `pre_screen`, readback, active lanes, verify | design/implementation gates, live invocation |
| **Package/export** | ship or install an existing skill | portability/install checks, active lanes, verify, **the floor** | design/implementation gates, live invocation |

**The floor, on every path, no exceptions:** the `pre_screen` blocking lane, and the comprehension
readback — they catch an undiscoverable description and a skill no fresh agent can follow. **On
the lane column:** every path runs the same active lane set; what differs is the gates and the
live invocation, not which lanes run. **`references/` routes Mechanical on purpose** — the
readback is the compensating control; declare Behavior change yourself when a reference edit
changes doctrine, not wording.

**Every path needs current verification intent before source edits.** On Mechanical or
Package/export paths, record plan sections 4.1 and 10 for affected operations in the existing
plan, or create a concise plan if none exists — this adds no approval gate to those paths.

Whether a large edit is a rewrite is the one judgement the classifier does not make. Decide on the
shape of the agent-facing diff, say which way you decided, and let the user overrule you.

### Step 1 — Understand intent

Understand the WHY before the WHAT, and cut ruthlessly: a capability nobody asked for is one you
maintain forever on a guess.

#### 1a. Read before you ask

- **Existing code** — run the six-point script analysis in
  [references/GENERALIZATION_PATTERNS.md](references/GENERALIZATION_PATTERNS.md) before asking
  anything; it answers most of the interview below.
- **An idea or a prompt** — explore openly. Do not jump to structure.
- **An existing skill to change** — read its SKILL.md and every supporting file, and identify
  gaps against [references/QUALITY_CHECKLIST.md](references/QUALITY_CHECKLIST.md).

#### 1b. Interview, one question per message

Before any detail question, decide whether this is one skill at all. When the request names
capabilities that share no trigger, no audience and no logic, say so now, ask which to build
first, and give each its own pass.

Then ask one question and wait for the answer. Five questions in one message get you one answer,
to whichever was easiest. Offer named options whenever you can — faster and more precise than an
open prompt; ask openly only when the options would be a guess. Skip anything already told to you.

1. What problem does this solve? (not "what should it do")
2. Who is the audience? (solo dev, team, CI, installed users)
3. What does success look like?
4. What are the constraints? (credentials, approvals, portability)
5. What is explicitly out of scope?

#### 1c. Classify capability profile

Classify external resources, data sensitivity, and risk tier (no-approval, bounded-approval,
fresh-approval). Feeds `Step 2` component fit (Claude Code) and the `Step 7` risk lane (any host).

#### 1d. Scope confirmation

Present a brief summary and wait for approval before designing:

- **In scope:** `<what this skill will do>`
- **Out of scope:** `<what it will not do>`
- **Audience:** `<who uses it>`
- **Risk tier:** `<no-approval / bounded / fresh-approval>`
- **Plan artifact:** `<target-aware path rule>`; scope approval authorizes only its creation or update

#### 1e. Duplication check + placement — Claude Code plugin-specific (am-pm monorepo only)

**Skip entirely outside the am-pm monorepo.** Detect it with
`python scripts/monorepo_placement.py` (walks up for the group/ci/pyproject marker triple), then
delegate the pre-scaffold check to the **where-does-it-fit** skill with the name + description
already gathered. It runs the marketplace **duplication scan** (`am-pm duplicate-scan`) and, on
proceed, group/domain placement. On a HIGH/MED-confidence duplicate, confirm with the user first.

### Step 2 — Doctrine, component fit, and structure

**Claude Code plugin-specific component-fit sub-step — skip entirely for a portable/Codex-only
skill**, which has no commands/hooks/subagents/MCP/LSP/monitors to weigh: read
[references/COMPONENTS.md](references/COMPONENTS.md) unconditionally, then open only the
`references/components/` recipes it surfaces — even expecting a skill-only design, since that
reading is what decides it. Record deliberately omitted components
(`component-fit.intentional-omissions`). For a hook candidate, read
[references/components/hooks.md](references/components/hooks.md) first.

**The structure decision below applies on every host.** Decide, in this order:

1. **Single skill** — the default.
2. **N skills sharing a scaffold** — weigh the split/merge signals and apply the capability test
   in [references/MULTI_SKILL_SPLIT.md](references/MULTI_SKILL_SPLIT.md). (On Claude Code, N
   skills packaged together form "a plugin"; on a portable install each skill gets its own
   directory — only that reference's shared-components note is Claude Code-specific.)
3. **Multi-phase within one skill** — read
   [references/MULTI_PHASE_PATTERNS.md](references/MULTI_PHASE_PATTERNS.md) only if at least two
   of its four warranting signals hold.

Present the structure you chose and wait for the user to confirm it.

**Research facts the design depends on before implementation.** When an operation relies on an
external CLI, API, library or host behavior, establish its contract from versioned primary sources
or reproducible observations, and record evidence and unresolved assumptions in plan section 4.1.
Imported scripts and copied docs need the same proof as new code. Resolve unsupported contracts
before implementing affected operations.

### Step 3 — Design section → approval gate

Write sections 1-4, 6-8, 11 and 12 of [references/PLAN_TEMPLATE.md](references/PLAN_TEMPLATE.md).
**Claude Code plugin-specific (am-pm monorepo) — skip outside that monorepo:** also write, unless
the skill is a bundle, the undated `.../docs/<plugin>/public/<plugin>-design.md` that `am-pm
validate repo` gates on. Write the plan before requesting approval, following the template's
target-aware path rules — the plan (and that design doc, on Claude Code) are the only pre-approval
writes. Present the saved path; on approval, update status to `design-approved`.

When more than one design would work, present two or three with trade-offs, leading with your
recommendation.

Then, for a relevance signal (**Claude Code plugin-specific — skip for a portable skill**, which
has no proactive-suggestion mechanism), read [references/RELEVANCE.md](references/RELEVANCE.md) first.

#### Where the skill lands

**Portable/Codex-only skill, or outside the am-pm monorepo:** decide global/workspace/shared-repo
installation directly and stop.

**Claude Code plugin-specific (am-pm monorepo only):** run
`python3 <skill_dir>/scripts/monorepo_placement.py --group <group> --intent "<purpose>" --json`.
`{"in_monorepo": false}` means standalone. `true` means read
[references/MONOREPO_PLACEMENT.md](references/MONOREPO_PLACEMENT.md) for the placement bridge and
`scaffold_path` for `init_skill.py --path` in `Step 5`.

### Step 4 — Implementation section → approval gate

Only after the design gate clears, write sections 5, 9 and 10 of the template — file structure,
parallel work items, verification plan — and present them for the second approval. On approval,
plan status goes `design-approved` → `plan-approved`. Target skill source stays gated until then.
Applies on every host.

### Step 5 — Implement

Before the first source edit in a shared repo, run the non-destructive `begin` sequence in
[references/REVIEW_COVERAGE.md](references/REVIEW_COVERAGE.md) to record provenance.

Write all files. When the target already exists, propose bounded edits — the smallest diff that
answers the feedback or eval failure, not a rewrite. For plans with independent work items,
dispatch sub-agents in parallel where the platform supports it, or work through them sequentially
otherwise. Review cross-file alignment after all work items complete.

**Claude Code plugin-specific, multi-skill primitives only:** implement each skill's SKILL.md,
scripts, references, and assets under its own `skills/<name>/` directory; primitive-level
components (agents, commands, hooks, MCP, LSP, monitors) go at the primitive root. A portable
install with N related skills has no shared primitive root — each skill installs on its own.

Implement section 10's checks alongside each operation, including independently grounded contract
tests for external dependencies. **Claude Code plugin-specific (am-pm monorepo):** write tests at
the lifecycle sibling `groups/<g>/<d>/<lifecycle>/tests/<plugin>/`, at or above the group's
`coverage_min`. Outside that monorepo, write tests per your own repo's convention, scaled to risk
per `references/PLAN_TEMPLATE.md` section 10.

Follow [references/SKILL_SPEC.md](references/SKILL_SPEC.md),
[references/PROMPT_ENGINEERING.md](references/PROMPT_ENGINEERING.md), and
[references/SKILL_TEMPLATE.md](references/SKILL_TEMPLATE.md) — all platform-agnostic. Before
writing `SKILL.md`, resolve the active criteria lanes and apply only the matching lane references.
Read [references/AUTHORING.md](references/AUTHORING.md) before writing SKILL.md content
(frontmatter rules, skill type, reusability positioning, the 10-section body structure —
platform-agnostic except its one Claude Code-specific field, `hooks:`, marked inline) and again
for scripts, config, references, and repo integration files.

If `Step 3` chose a relevance block (**Claude Code plugin-specific — skip for a portable skill**),
write `relevance/<plugin>.json` and validate it with the `relevance` check.

### Step 6 — Readback

Readback runs before review, on every host: an artifact a fresh agent misreads wastes every lane
on the wrong thing.

**6a. Comprehension readback — every path, every host.**

```bash
python3 <skill_dir>/scripts/readback.py prompt --plugin-dir <target> \
  --scenario "<a realistic scenario from the design section>" --out <workdir>/readback.md
```

`<workdir>` is a scratch dir outside the skill — 6b's session is not sandboxed and runs commands
there. The prompt carries the agent-facing surface in full — `SKILL.md`, and for a Claude Code
plugin `plugin.json`/`agents/`/`commands/`/`hooks/`/`monitors/`/`.mcp.json`/`.lsp.json` — and
lists everything else by path/heading, exactly what a real invocation loads. "The files do not
say, I would open `references/X.md`" is a **correct** answer here, not a divergence.

Follow the checklist in [references/lanes/readback.md](references/lanes/readback.md): with
subagent/parallel-task dispatch (e.g. Claude Code's Task tool), dispatch a fresh subagent with
that file as its entire input — not the design section, not the conversation. Otherwise, perform
the same readback yourself in a fresh mental frame, using only the assembled prompt. Diff its
answers against the approved design section. **Every divergence is a finding against the
artifact, never the agent.**

**6b. Live invocation — Claude Code plugin-specific, New and Behavior-change paths only. Skip for
a portable/Codex-only skill or any host without a `claude -p` CLI.**

```bash
python3 <skill_dir>/scripts/readback.py invoke --plugin-dir <target> \
  --prompt "<a realistic user phrasing from the design section>" \
  --skill-name <skill> --workdir <workdir>
```

Exit 0 means the skill fired, exit 1 that it did not; a non-zero `claude` exit raises. This is the
only check that tests discoverability — `pre_screen`'s first critical-fail condition. With no
equivalent headless-invocation CLI, skip this check and rely on comprehension readback plus manual
smoke-testing instead.

**The loop.** Readback → diff → fix the artifact → one re-read. **Cap: two rounds**, then report
what is still divergent as a decision for the user.

### Step 7 — Review

Every lane below applies on any host except `component-fit`, which is Claude Code plugin-specific.
Full checklists live in `references/lanes/`: `pre-screen.md`, `genericity.md`, `installed-use.md`,
`context-engineer.md`, `component-fit.md` (Claude Code-specific), `runtime-contracts.md`,
`repo-integration.md`, `risk.md`, `review-process.md`.

- **On a platform with subagent/parallel-task dispatch** (e.g. Claude Code's Task tool): dispatch
  each active lane as its own subagent, reviewing the entire skill (all files, not just SKILL.md).
  The review coverage matrix is written here too when the target lands in a shared repo.
- **On a platform without subagent dispatch**: work through each active lane's checklist yourself
  sequentially, noting its findings before moving to the next lane.

**Dispatch (or work through) the `pre_screen` lane first, on every host.** It is blocking — if any
critical-fail condition fires, fix it before the remaining lanes. `skill_review_orchestrate.py
prepare`'s manifest marks `pre_screen` `"blocking": "true"` so `run` enforces this automatically.

### Step 8 — Verify

The coverage matrix `pr-check` gates on exists by now because `Step 7 — Review` wrote it.

**Claude Code plugin-specific (am-pm monorepo) — skip below for a portable/Codex-only skill:** run
`just bump-plugin-version <plugin-name> patch`, and pin any new dependency with `==` in the
domain's `pyproject.toml` (Node: `package.json`), **before** `pr-check`.

Shipping into a shared repository? Run its own pre-PR checklist first. **Claude Code plugin-specific
(am-pm) example — substitute your own repo's pre-PR command outside it:** `pre-commit run
--all-files` then `am-pm ci pr-check --base-ref <merge-target>` (exit 0), then `am-pm
changelog-gate --base-ref <merge-target>`, which says whether a fragment is owed, or nothing.
**Never add a changelog fragment it did not ask for.**

Before presenting the skill as complete, open [references/VERIFICATION.md](references/VERIFICATION.md)
and run every applicable check. A discoverability invocation (Claude Code-specific), a mocked
preflight, and a live integration test establish different things — do not substitute one for
another. Report results as a checklist; explain and get explicit user approval for any removed or
materially changed capability.

### Step 9 — Report

Present the final report:

- **Summary:** what was created or changed, which components, which skills.
- **Review coverage:** matrix status (all rows pass/fail/na with evidence).
- **Changelog:** none owed, or the fragment asked for (Claude Code-specific am-pm gate; "not
  applicable" outside that monorepo).
- **Next steps:** install location, PR instructions, deferred items.
- **Install location:** ask where — workspace, global, or a shared repo/plugin monorepo.

Report the eval decision and actual evidence from plan section 10; planning or declining an eval
is not an executed eval. For shared repo installs, complete the checklist in
[references/VERIFICATION.md](references/VERIFICATION.md).

**Claude Code plugin-specific (am-pm monorepo):** the folder *is* the plugin — install at the path
`Step 3` resolved through the where-does-it-fit bridge. No separate generated tree, no build step.

**Portable/Codex-only skill:** install at the chosen global/workspace/shared-repo skills directory
(e.g. `~/.claude/skills/<name>/`, `~/.codex/skills/<name>/`) — one directory with `SKILL.md` plus
`scripts/`, `references/`, `assets/` as applicable.
