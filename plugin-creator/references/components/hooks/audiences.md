# Hook Audiences

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only skill.** Hooks are a Claude Code plugin component with no Codex/Agent-Skills-standard equivalent; see `../hooks.md`.


Deep reference for the AUDIENCE and WORTH steps in
[hooks.md](../hooks.md): the full payload table per audience, which worth
factors bite for each, what each audience is paid in, and the weighting
matrix behind WORTH's four factors.

## AUDIENCE — payload and worked example, per role

| Audience | Payload | Worked example |
|---|---|---|
| **The agent** | `additionalContext`; on `Stop`/`SubagentStop`, `decision: "block"` + `reason` becomes Claude's next input | `plan-layers` nudges a finished `writing-plans` skill toward its delivery step |
| **The tool call** | `permissionDecision` (`PreToolUse`, `PreModelSwitch`); `updatedInput` (`PreToolUse`, `PermissionRequest`) | `rtk-rewrite.sh` rewrites `git status` → `rtk git status` with `allow` + `updatedInput`, invisibly |
| **A person** | `systemMessage` — a visible warning banner; also `terminalSequence` (bell, window title) and `displayContent` | am-pm-support's conflict check prints a one-line human summary beside a detailed machine payload |
| **The permission classifier** | `classifierContext` — a note about the tool call's *result*. The classifier never sees tool results, so this is the only channel to it | none in this corpus — see the Claude Code hooks reference |
| **The session** | `reloadSkills`, `sessionTitle`, `watchPaths`, `initialUserMessage`. Without `reloadSkills`, skills a hook installs stay invisible until the next session | none in this corpus — see the Claude Code hooks reference |
| **Nobody** | pure side effect: logging, cleanup, an external write | am-pm-support emits a metric on ~29 events and returns nothing |

**The trap this spine exists to catch:** `UserPromptSubmit`'s `reason` goes to the **user,
never Claude**. Using it to instruct the agent silently does nothing. Check the audience of
the field, not just its name.

### Which worth factors bite, by audience

A lookup — consult it once you know your audience, not before.

| Audience | Alignment | Distance | Consequence | Honesty |
|---|---|---|---|---|
| The agent | medium — a tax per near-miss | **critical — bridging the gap IS the point** | medium | high |
| The tool call | **critical** | irrelevant | **critical** — weighed against risk prevented | **critical** |
| A person | **high** — people notice spam faster than a model does | low | medium | medium |
| The classifier | medium | low | medium | high |
| The session | **high** — spurious reconfiguration is disruptive | n/a | high | high |
| Nobody | **low — poor alignment is genuinely fine** | n/a | low | low |

Two results that are not obvious:

- **Distance matters only for the agent.** It is the strongest argument for a context hook
  and irrelevant everywhere else — a guardrail does not care how long ago the rule was set.
- **Honesty peaks exactly where alignment peaks**, both on the tool call, because that is
  the only audience where being wrong destroys work rather than merely wasting some.

So a poorly-aligned **side effect** can be worth shipping while a poorly-aligned
**guardrail** is dangerous: same event, same imprecision, opposite verdict, decided by who
is listening.

> **Evidence note.** The extremes are corpus-backed — tool-call payloads are the ones this
> repo's authors hedge hardest (`approve-read-commands.sh` rejects `;`, `&&`, `||`, `|`,
> `$()`, a backtick or a newline *before* matching), and the pure-recorder end genuinely is
> loose. The human row is backed by both `systemMessage` emitters gating themselves behind
> a sentinel file. The **classifier and session rows are reasoned, not measured**: neither
> payload appears anywhere in this corpus.

### What each audience is paid in

| Audience | Paid in | Justified against |
|---|---|---|
| The agent | tokens, on every fire | the value of the reminder |
| The tool call | **false positives — blocked or silently rewritten legitimate work** | **the risk prevented** |
| A person | attention, which is spent faster than context | the warning being worth an interruption |
| Nobody | latency | ≈ free with `async: true` |

A guardrail justified on context economy is a category error; so is a context hook
justified on risk.

**Guardrails carry one more caveat, and it is the most important in this file: they fail
open, loudly-but-ignorably.** A wrong path, a non-executable script, or a missing
interpreter means the guard silently does not exist while appearing configured. Inspection
cannot verify it — ship every guard with a documented negative test and run it live.

## WORTH — the weighting matrix

| Factor | Ask | Argues FOR a hook when |
|---|---|---|
| **Alignment** | how often does this event fire when my moment is NOT happening? | high — the event is a near-perfect proxy. Perfect alignment also buys you a bigger payload; loose alignment forces two lines |
| **Distance** | how far is "the rule was loaded" from "the rule matters"? | **a long flow** — the skill that set the rule is far back in context and attention has drifted. Short interaction → the skill is right there and a hook adds nothing |
| **Consequence** | what actually breaks if it never fires? | something does. "The agent would probably do it anyway" → skip |
| **Honesty** | is this genuinely expressible deterministically? | yes. If encoding it means approximating a judgement call, the skill description WAS the honest encoding |

**Complexity cuts both ways.** *Mechanically* complex — several conditions, all decidable
from the payload and the filesystem — is a **good** hook: exactly the work you want done
deterministically once instead of re-judged correctly every time. *Semantically* complex —
needs judgement about intent — is a **bad** hook however precisely you can name the moment.
Complexity of the predicate favours a hook; complexity of the judgement rules it out.

Two older filters live here rather than as gates on naming the event: **static content** is
a Consequence/Honesty failure (a subprocess approximating a file — use `CLAUDE.md` or a
skill), and **a predicate needing judgement** is the Honesty row.
