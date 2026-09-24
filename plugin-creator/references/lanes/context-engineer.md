# Context Engineering Reviewer

Use when reviewing the context-engineering lane of skill quality reviews.

Review context utility, hot-path density, progressive disclosure, reference routing, token economy, operation granularity, and duplicated or conflicting instructions.

Use the criteria below as your complete checklist for this lane. Do not invent
extra criteria and do not edit shared files. If dispatched as a subagent, the
host agent will merge your lane result into the review coverage matrix; if
worked through directly, merge the result into the matrix yourself.

## Review Protocol

1. Review only this lane and the supplied diff or files.
2. Stay diff-bounded unless a nearby file is necessary to understand blast radius.
3. Mark each criterion `pass`, `fail`, or `na`.
4. Include concrete evidence for every row.
5. Return only the requested lane result table unless asked for analysis.

## Lane Criteria

- `surface.high-usage-skill-md` - SKILL.md contains high-usage context
  - Review: Check that the main SKILL.md contains only context likely to be used in most skill invocations. Move first-run setup, rare troubleshooting, full schemas, historical notes, and deep examples into referenced files.
- `surface.preflight-config-routing` - Config failures route to references
  - Review: Check that SKILL.md and preflight/config error output point to the relevant configuration reference when setup or configuration is the likely fix.
- `context.progressive-disclosure` - Details are progressively disclosed
  - Review: Check that content is positioned by reusability: high-reuse in SKILL.md, lower-reuse in references/. Check that long reference files are split into parent + sub-files when sections have different reuse frequencies. Check that every reference link includes a 'when to read' trigger so the agent knows when to skip it. Flag links that say 'see X' without stating when X is relevant.
- `context.token-economy` - Token-heavy paths are controlled or justified
  - Review: Check whether anticipated or observed high-token paths across service, workflow, review, eval, exploration, and generated-output skills have token-control measures such as filters, allowlists, caps, compact formats, staged reference loading, grep/find patterns, summary-first output, explicit exploration boundaries, or stop conditions. If they do not, check that the creator explicitly justifies the token cost with a quality, safety, recall, or coverage benefit and includes eval, benchmark, smoke-test, or creator-provided evidence when available.
- `context.no-duplicated-criteria` - Criteria are not duplicated by hand
  - Review: Check that quality criteria are not duplicated by hand across SKILL.md, checklists, verification docs, generated agents, or review prompts.
- `context.single-source-content` - Shipped templates and references are the single source
  - Review: Check that content shipped as a template, asset, or reference file is referenced by path rather than duplicated inline in SKILL.md or other docs. Flag inline copies of a bundled template or reference block; the shipped file should be the single source.
- `context.signal-noise-ratio` - Every instruction passes the signal-noise filter
  - Review: Check whether instructions in SKILL.md and references pass the four-question signal-noise filter: (1) Would the agent ask about this if missing? (2) Could the agent discover this from repo files? (3) Does this change frequently? (4) Is this a standard convention the model already knows? Flag sections that are noise by these tests. Also check that critical constraints and NEVER/ALWAYS rules are in the top 15% of the file, not buried in the middle.
- `context.examples-are-effective` - Examples are effective
  - Review: Check that examples are relevant, diverse enough to avoid accidental overfitting, clearly delimited from instructions, and placed in references when deep, rare, or lengthy.
