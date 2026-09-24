# Pre-Screen Criteria

Generated from `../../assets/skill-quality-criteria.json`. Do not edit by hand.

Use this lane before authoring or updating a skill to verify none of the six critical-fail conditions are present.

## Examples

- Good: Description names a specific action and trigger scenario; all side-effecting operations require explicit user approval; scripts run non-interactively; all non-standard dependencies are documented; consequential operations have concrete verification commands; SKILL.md is inside its character budget and every reference is a leaf or an index over its own subdirectory.
- Bad: Description says 'Helps with database stuff'; skill auto-triggers and deletes records without an approval gate; a required Python package is not mentioned anywhere; no way to confirm a deployed change succeeded; SKILL.md runs past 25,000 characters and a reference sends the reader sideways to a sibling for a required step.

## `pre_screen.undiscoverable-description` - Description is specific and discoverable

MUST write a description that answers all three: what does this skill do (specific action, not a domain label), when should the agent invoke it (concrete trigger scenario), and what keywords would a user naturally say. A vague description makes the skill undiscoverable — no other quality dimension matters if the skill never activates.

## `pre_screen.side-effecting-auto-trigger` - Side-effecting skills have explicit approval gates

If the skill performs destructive or irreversible actions (deploys, file overwrites, sends messages, deletes resources), OR actions that accept risk on the user's behalf or weaken a safety or security control (suppressing scanner findings, disabling or bypassing a CI gate, adding an allow/ignore entry, loosening permissions), AND is auto-invocable (no disable-model-invocation: true), it MUST have at least one explicit user-approval gate before each such action. Otherwise, mark the skill manual-only via disable-model-invocation. When the skill's core purpose is to grant such an exception, prefer disable-model-invocation: that decision needs deliberate human intent.

## `pre_screen.interactive-scripts` - Scripts are non-interactive

Scripts in scripts/ MUST NOT require TTY interaction — no stdin prompts, interactive menus, or password prompts without a non-interactive fallback. Agents cannot interact with TTY prompts. Provide --yes, --non-interactive, or equivalent flags for any step that would block.

## `pre_screen.implicit-dependencies` - Required dependencies are documented

Every non-standard dependency (Python packages, CLI tools, API keys, running services) MUST be documented in prerequisites or the preflight script. Standard OS utilities (git, curl, python, node, npm, pip) do not need documentation. A missing dependency that crashes silently on a clean machine is a critical failure.

## `pre_screen.no-verification` - Consequential operations have verification

If the skill generates code, modifies configs, deploys, or creates infrastructure, it MUST include at least one concrete verification command or check that confirms the output is correct. 'Make sure it looks right' does not count — verification must be operational (a command to run, an assertion to check, a file to inspect).

## `pre_screen.bloated-body` - SKILL.md is within its size limit and references do not chain

SKILL.md size is authoritative in CHARACTERS (see references/SKILL_SPEC.md) and is the ONLY size budget — reference files have none, in lines or characters. A reference MUST NOT depend on a sibling reference as a dependency chain — "read A to learn you must then read B to do the work" takes two decisions to reach the content, so the odds it arrives are squared. Two sibling links ARE legal: a citation, which only says where a fact lives and is marked `<!-- citation -->` on its line, and an index link, where a parent links down into its own subdirectory. When a reference grows too long to read in one pass it becomes an index over leaves; it does not link sideways.
