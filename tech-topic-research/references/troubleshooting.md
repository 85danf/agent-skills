# Troubleshooting Reference

Triage tables for the tech-topic-research skill. SKILL.md links here when the
agent encounters one of these conditions; the contents do not need to
sit in the agent's primary context window during normal operation.

## Error handling

| Error                                                 | Cause                                  | Fix                                                                                                                |
| ----------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `No topic provided`                                   | User invoked the skill without a topic | Ask the user for a topic, then restart at Phase 0.                                                                 |
| `WebSearch unavailable`                               | Host does not expose web search        | Stop and report — deep research cannot run without web search.                                                     |
| `Task tool / run_in_background unavailable`           | Host lacks parallel subagents          | Restrict to Quick depth and explain the limitation in the gist response.                                           |
| `WebFetch returned 4xx/5xx for a candidate source`    | URL broken or rate-limited             | Drop the URL from the result set; do not paste it into the study guide. Do not substitute, do not `[broken]`-mark. |
| `Subagent returned empty findings`                    | Topic is niche or query was too narrow | Re-spawn the affected agent with a wider query, or note the gap in the final document's Methodology section.       |
| `Subagent timed out (>15 min Standard, >25 min Deep)` | Slow web or rate-limited search        | Drop the subagent from the result set and note the gap in Methodology. Do not retry.                               |

## Troubleshooting

| Problem                                                | Fix                                                                                                                                                                                    |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Subagent results arrive slowly                         | Continue drafting Phase 4 from main-agent knowledge while waiting; check subagent output files when each finishes. Use the FFS rule (Phase 3) to proceed without the slowest subagent. |
| Comparison mode treats items unequally                 | Re-spawn the lighter side of the comparison and rerun Phase 4–6 for that side. See `references/comparison-mode.md` equal-treatment rule.                                               |
| Final document mixes confidence levels for Deep claims | Re-tag each claim against the Confidence Criteria in `references/analysis-tools.md`; mark anything you cannot back as `SPECULATIVE`.                                                   |
| User asked for Quick but wants more after the gist     | Offer to escalate to Standard depth, run the token-cost approval gate, and continue from Phase 2.                                                                                      |
| Mid-run refinement triggered twice in one run          | Refinement is capped at one loop per run (`research-plan-template.md` `refinement_state.used`). Stop refining; proceed to Phase 4 with current evidence.                               |

## Anti-patterns

| Don't                                                                              | Do instead                                                                                                                                                 |
| ---------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Ask generic questions before any research                                          | Deliver the gist first (Phase 1), then ask informed questions in Phase 2.                                                                                  |
| Spawn subagents for Quick depth                                                    | Quick is gist only — zero subagents.                                                                                                                       |
| Wait for all subagents before talking                                              | Deliver the gist immediately, layer in depth as results arrive.                                                                                            |
| Skip the token-cost approval gate because the user said "do deep research"         | Always run the gate (Phase 1 step 4); explicit invocation is consent only to consider the skill, not to spend Deep-tier tokens.                            |
| Paste URLs without verifying them                                                  | Apply [`output-envelope.md` § Anti-fabrication](output-envelope.md#anti-fabrication-mandatory) — WebFetch every URL; drop on 4xx/5xx without substitution. |
| Fabricate a plausible URL to fill a citation gap                                   | Apply the canonical anti-fabrication contract; mark the claim `[unverified]` (subject to the 10% cap) and move on.                                         |
| Soften genuine weaknesses to sound balanced                                        | Red-team: actively search for reasons NOT to use the topic.                                                                                                |
| Treat one comparison item as the default                                           | Each item gets equal research and equal treatment per `references/comparison-mode.md`.                                                                     |
| Use the user's private dashboards to "discover" facts about the user's own systems | Restrict to public sources; report what an external investigator could verify.                                                                             |

## When to load this file

- On error: when the workflow hits a condition matching the Error handling table.
- On confusion: when the agent is unsure whether a behavior matches the spec — check the Anti-patterns table.
- During Phase 7 quality assurance, scan the Anti-patterns column to verify
  the document does not exhibit any of those patterns.
