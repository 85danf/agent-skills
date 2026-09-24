# Research Plan Template

Fill this template at the start of Phase 3, after Phase 2 clarification answers
are in. The plan stays in conversation context; the user can redirect it before
any subagent fan-out.

```yaml
core_question: "<one sentence stating exactly what we're trying to understand>"
depth: "<quick | standard | deep>"
familiarity: "<new | heard | tried | regular>"
goal: "<evaluate | learn | concepts | interview>"
focus_areas:
  - "<focus 1, derived from Phase 1 dimensions and Phase 2 answers>"
  - "<focus 2>"
  - "<focus 3>"
research_angles:
  - "<angle 1: one-line description>"
  - "<angle 2>"
  - "<angle 3>"
source_strategy:
  primary: "<which source types carry the most weight here — see references/source-quality.md>"
  secondary: "<supporting source types>"
  exclude: "<source types we will not cite for this topic>"
known_unknowns:
  - "<what we know we do not know>"
expected_subagents:
  - "<role 1, e.g. docs-searcher>"
  - "<role 2>"
  - "<role 3>"
refinement_state:
  used: false # set true after one mid-run outline refinement
  what: "" # one-line note describing what triggered refinement
  subagents_added: [] # role names of subagents spawned in the refinement loop
```

## How to use it

1. Fill the template. **Always set `refinement_state.used = false` at fill time** — do not carry state across runs. Show the template to the user before fanning out.
2. If the user redirects (different focus, narrower scope, additional angle),
   update the plan and confirm before spawning subagents.
3. Keep the filled plan in conversation context — Phase 4–7 reference it.
4. Before invoking the Mid-run outline refinement loop (Phase 3), check
   `refinement_state.used`. If `true`, the run already used its single
   refinement loop — do not refine again. If `false`, run the loop, set
   `used: true`, fill `what` and `subagents_added`, and continue.
