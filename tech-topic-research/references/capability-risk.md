# Capability risk classification

Detail behind the four-tier classification SKILL.md "Capability profile" section names. Each tier maps to a class of operations the skill performs.

## Tiers

- **No approval needed**: web search, web fetch, drafting a conversational gist or study-guide document into the conversation.
- **User confirmation required**: subagent fan-out (Standard or Deep depth) — see [SKILL.md "Token cost and approval gate"](../SKILL.md#token-cost-and-approval-gate). Required because the cost (5–35× for Standard/Deep, 25–60× for Comparison-Deep — see the cost table) is non-recoverable mid-flight.
- **Bounded approval**: writing a study-guide file to the path the user named. **Implicit scope expansion in Deep tier with >8 sources:** the skill writes per-source mini-summaries to `<user_path>/summaries/<slug>.md` siblings of the named file. The complete set of allowed write paths is: (1) the user-named study-guide file itself, (2) one `<user_path>/summaries/<slug>.md` per cited source. No other files (index files, backups, sibling drafts) may be written without fresh approval.
- **Fresh approval**: any operation outside the read-only / draft-into-current-conversation scope. The skill does not currently perform such operations.

## When to load this file

Phase 0 / Phase 7 / risk review: load when classifying a new operation or auditing whether an action stays inside its declared tier.
