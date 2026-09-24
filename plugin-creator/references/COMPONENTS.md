# Optional Plugin Components

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only
> skill.** Hooks, subagents, monitors, MCP, LSP, and commands are all Claude Code
> plugin components with no equivalent in the portable Agent Skills standard or in
> Codex. A portable/Codex-only skill is a SKILL.md plus `scripts/`, `references/`,
> `assets/` — full stop; there is no "component fit" decision to make, because none
> of these other components exist to choose from. Read this file (and the
> `components/*.md` recipes it points to) only when authoring or reviewing an
> actual Claude Code plugin — inside the am-pm monorepo or otherwise.

The component-fit entry point. The skill is always the core; these are the **optional**
components. Open a recipe only for one you are actually considering.

## Skills fail silently; everything else fails loudly

The creation-cost-against-proof-cost trade that decides every row below is in `SKILL.md`'s
`## Principles`, already in context; it is not restated here.

What belongs on this page: skills are not merely "less restricted". Their limits are **soft
and invisible**, so a skill degrades silently while every other component fails loudly. A
skill that appears to work is not evidence that it works — that is what `eval` is for.

## Choosing

Every component answers **what initiates it** and **what it costs**; the cost column is the
anti-over-engineering guard. Ordered by what initiates it, default first.

| Component | Essence · initiated by | You gain | You pay | Reach for it when | Do NOT when |
|---|---|---|---|---|---|
| **Skill** | a **semantic** trigger — the model decides from the description; probabilistic *by design*, right when the moment is vague | zero infrastructure; loads on relevance | a description competing for attention under the character caps in `SKILL_SPEC.md` | the moment is vague; only a reader can spot it | — the default |
| **Hook** | a **deterministic, event** trigger — an event decides | a moment that cannot be missed | fails open loudly-but-ignorably; latency per matching call; unverifiable by inspection | you can name the event and missing it is the failure | content is static (→ `CLAUDE.md`), the predicate needs judgement, or the event cannot act |
| **Subagent** | **a boundary** — restricted tools, isolated context, parallelism; you delegate | work that cannot wander outside its tools, cannot pollute your context, runs N-wide | steerability — you see only the report, and **Claude rewrites the delegation message every time**; that message is the lossy channel | the work needs a tool boundary, or N of it at once | you must see and steer each step, or it must run identically every time (`context: fork`) |
| **Monitor** | **know when, without asking repeatedly** — something external happens. It *notices*; it does not act | no polling loop burning a turn per check | **every emitted line becomes context — no rate limit, no auto-stop.** The filter is the only governor | something outside the session changes and you want telling | you need ONE notification (a backgrounded command — a monitor stays armed), or repeated *action* (a cron) |
| **MCP** | **capability from an external server** holding live state or an amortized index | what no local script can do: a live browser, a warm symbol index | a dependency, a security review, portability | the capability needs live state or a warm index | a script or CLI would do — a REST wrapper fails that test |
| **LSP** | a broad set of **deterministic code operations in real time as code is edited** — diagnostics, definitions, references, rename — decided by a language server, not inferred from text | exactness where text matching guesses, at the moment the mistake is made | the plugin does **not** ship the binary; **no cloud sessions at all**; `diagnostics` defaults `true`, injecting after every edit; first server registered wins an extension | you need exact code facts as the edit lands | the language is already served, the binary cannot be assumed, or the work runs in cloud |

**Only hooks buy reliability of trigger.** A subagent buys a boundary and is arguably
*less* predictable than inline work; a monitor buys noticing-without-polling; MCP buys
capability; LSP buys precision. Reaching for a subagent when you wanted determinism is the
mistake this table exists to prevent.

> **Prior art, not a ranking.** Across 102 plugins here: skills 96 · agents 54 · hooks 10 ·
> commands 10 · monitors 1 · `.mcp.json` 0 · `.lsp.json` 0. `docs/en/monitors.md` and
> `docs/en/lsp.md` are **404** upstream — low adoption reflects how little those are
> documented, not how useful they are. Consequence: for the rare three, few examples to copy
> and undocumented edges.

## Discriminators authors get wrong

1. **Skill vs hook** — both trigger; they differ in *who decides the moment*: the model
   guesses from a description, or an event states it. Vague moment → skill.
2. **Monitor vs hook vs just checking** — all three "notice". A hook fires on a
   session-*internal* event; a monitor watches something *external* on its own schedule; an
   on-demand check is right for a **single** look.
3. **MCP vs a script** — prefer a script. **Win condition:** does the capability hold live
   state or an amortized index across many calls? A live browser passes; a REST wrapper does
   not.
4. **LSP vs hook** — write the analysis → LSP; write the policy → hook.
5. **Subagent vs forked skill** — `context: fork` means **you** write the task, fixed; a
   subagent means **Claude** rewrites the delegation each time. Same way every time → forked
   skill ([subagents](components/subagents.md)).

## Multi-Skill Primitives

Every component above lives at the **plugin** root, not inside a skill, so a plugin's
skills all share one set of them.

## Per-Component Recipes

Each recipe carries its own path and `am-pm validate <kind>`; skill runtime behaviour is in
[SKILL_SPEC.md](SKILL_SPEC.md). Do not restate either here. <!-- citation -->

- [Hooks](components/hooks.md) — REACH/AUDIENCE/WORTH, who each payload reaches, the
  weighting lookup, the capability matrix, patterns, pitfalls.
- [Subagents](components/subagents.md) · [Monitors](components/monitors.md) ·
  [MCP](components/mcp.md) · [LSP](components/lsp.md)
- [Commands](components/commands.md) — merged into skills; invocation control lives here.
