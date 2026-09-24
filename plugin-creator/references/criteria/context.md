# Context Engineering Criteria

Generated from `../../assets/skill-quality-criteria.json`. Do not edit by hand.

Use this lane while writing SKILL.md and references so default-loaded context stays high value.

## Examples

- Good: SKILL.md contains workflow, safety, and routing. A reference file that covers 7 components is split into COMPONENTS.md (always read during component-fit) and components/*.md (read only for relevant components). Each level loads only what the agent needs.
- Bad: Load all 7 component field tables into SKILL.md or a single reference file. The agent reads thousands of tokens of hook event details when it only needs the MCP recipe.

- Good: For high-volume logs, diffs, search results, or eval outputs, provide compact defaults, filters, field allowlists, caps, or staged reference loading to control token usage with clear quality, safety, recall, or coverage justification.
- Bad: Dump every returned field, full transcript, complete search result, or broad exploration trace by default without filters, allowlists, caps, or staged loading.

- Good: Ship the config schema once as templates/config-template.yml and link to it from SKILL.md with a 'when configuring, copy templates/config-template.yml' trigger.
- Bad: Paste the full config schema inline in SKILL.md and also ship templates/config-template.yml, so the two copies drift apart.

## `surface.high-usage-skill-md` - SKILL.md contains high-usage context

Keep default-loaded SKILL.md context likely to help most invocations; move first-run setup, rare troubleshooting, full schemas, historical notes, and deep examples into referenced files.

## `surface.preflight-config-routing` - Config failures route to references

When setup or configuration is the likely fix, route agents from SKILL.md, preflight output, and config errors to the relevant reference instead of embedding full setup details in default context.

## `context.progressive-disclosure` - Details are progressively disclosed

Position content by reusability: how often it is needed relative to the number of times the skill is invoked. High-reuse content (workflow, safety rules, operation routing) belongs in SKILL.md. Lower-reuse content (full schemas, rare operations, setup depth) belongs in references/. Within references, split long files into a parent index and sub-files in a folder when sections have different reuse frequencies. Sub-files belong to their parent, not to SKILL.md. Every reference link in SKILL.md and in parent index files must include a 'when to read' trigger — write the link as a conditional ('when X, read Y') so the agent can skip irrelevant references.

## `context.token-economy` - Token-heavy paths are controlled or justified

For service, workflow, review, eval, exploration, and generated-output skills likely to consume high context through broad file reads, large diffs, logs, schemas, transcripts, search results, API responses, or eval artifacts, add token-control measures such as filters, allowlists, caps, compact formats, staged reference loading, grep/find patterns, summary-first output, explicit exploration boundaries, and stop conditions. If high token use is intentional because it improves quality, safety, recall, or coverage for this skill, state that trade-off and cite eval, benchmark, smoke-test, or creator-provided evidence when available.

## `context.no-duplicated-criteria` - Criteria are not duplicated by hand

Keep quality criteria in the canonical criteria source and generated references; hand-written docs may route to criteria but must not restate them as a second source.

## `context.single-source-content` - Shipped templates and references are the single source

When content is authored once as a shipped template, asset, or reference example, reference it by path (with a 'when to read' trigger) from SKILL.md and other docs instead of pasting a second copy, because duplicated content drifts as one copy is updated and the other is forgotten. This generalizes the no-duplicated-criteria rule to all shipped content. Cross-document references of this kind are citations, not dependency chains: mark the line `<!-- citation -->` so the check can tell them apart, and phrase the pointer as a condition for reading ("read this when you need the factor weighting"), never as a topic ("see hooks.md for more on hooks").

## `context.signal-noise-ratio` - Every instruction passes the signal-noise filter

For each section or instruction in SKILL.md and references, apply the four-question filter before keeping it: (1) Would the agent ask about this if it were missing? If no, it is noise — remove it. (2) Could the agent discover this by reading existing repo files? If yes, it is noise — the agent would pay twice and the instruction goes stale. (3) Does this change frequently? If yes, it is noise — stale context poisons more than no context. (4) Is this a standard convention the model already knows? If yes, it is noise — only document project-specific deviations. Apply the 3-zone layout to the final SKILL.md: top 15% for security constraints, NEVER/ALWAYS rules, and hard architectural decisions; middle 70% for patterns, examples, and stack definitions; bottom 15% for executable commands, workflow triggers, and verification checklists.

## `context.examples-are-effective` - Examples are effective

Use examples that are relevant to real use, diverse enough to avoid accidental overfitting, clearly delimited from instructions, and placed in references when they are deep, rare, or lengthy.
