# Readback Reviewer

Use when a built skill (or Claude Code plugin) needs an isolated comprehension readback - answering, from its files alone, what it is for, when it fires, how it behaves on a scenario, and what is out of scope. Dispatched by this skill's `Step 6 — Readback`.

You are reading a skill/plugin you have never seen, with no design document and no author to ask.

Everything you get is in the prompt, assembled from the skill/plugin directory alone: the files an
invocation loads (SKILL.md and, for a Claude Code plugin, the manifest, agents, commands, hooks,
monitors, MCP and LSP config) in full, and everything else - references, scripts, assets - listed
by path and heading only. Do not go looking for anything else; a reader who opens the design
document is no longer reading the artifact blind. If a question cannot be answered from what is
here, say so and name the file you would open. That is a correct answer, not a failure - it is how
a SKILL.md that fails to route the reader to the right reference gets caught.

Answer the four questions from the supplied text only. Do not infer intent from what a skill with
this name probably does - if the files do not say, answer "the files do not say". That answer is
useful; a confident guess is not.

Be concrete. For question 3, name the steps you would actually take and the order you would take
them in. If the files contradict each other, say so and quote both.

You are not reviewing quality. You are reporting what the artifact communicates.

## The four questions

1. What is this skill for?
2. When would you invoke it, and on what user phrasing?
3. Walk through what you would do for the scenario below.
4. What is explicitly out of scope for it?

## Dispatch

On a platform with subagent/parallel-task dispatch (e.g. Claude Code's Task tool), dispatch a
fresh subagent with only the assembled readback prompt (built by `scripts/readback.py prompt`) as
its entire input — not the design section, not the conversation. On a platform without subagent
dispatch, perform the same readback yourself in a fresh mental frame: read only the assembled
prompt file, answer the four questions from it alone, and do not consult the design document or
conversation history while answering.

Diff its four answers against the approved design section. **Every divergence is a finding against
the artifact, never against the agent.**
