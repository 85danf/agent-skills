# Pre-Screen Reviewer

Use when reviewing any skill change to check for critical-fail conditions that make a skill undiscoverable, unsafe, or unreliable regardless of other quality dimensions. Always run this lane first, before other review lanes.

Check the six critical-fail conditions: undiscoverable description, side-effecting auto-trigger without gates, interactive scripts, implicit required dependencies, no verification for consequential operations, and bloated or deeply nested body. Halt all other review if any condition fires.

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

- `pre_screen.undiscoverable-description` - Description is specific and discoverable
  - Review: Check that the description answers all three: (1) what does this skill do — a specific action, not a domain label; (2) when should the agent invoke it — a concrete trigger scenario; (3) what keywords would a user naturally say. Fail if any answer is unclear. This is a blocking condition.
- `pre_screen.side-effecting-auto-trigger` - Side-effecting skills have explicit approval gates
  - Review: Check whether the skill performs writes, deletes, deploys, sends, other side effects, OR actions that accept risk or weaken a safety/security control (suppressing scanner findings, disabling a gate, adding an allow/ignore entry, loosening permissions). If it does and it is auto-invocable, verify there is at least one explicit approval gate before each such action, or that the skill is marked disable-model-invocation. Fail if such an auto-trigger skill lacks gates. This is a blocking condition.
- `pre_screen.interactive-scripts` - Scripts are non-interactive
  - Review: Check each script for input(), read -p, select, interactive menus, or password prompts without a --yes or --non-interactive fallback. Fail if any script blocks on TTY input. This is a blocking condition.
- `pre_screen.implicit-dependencies` - Required dependencies are documented
  - Review: Check whether the skill requires non-standard packages, CLI tools, API keys, or running services that are not documented in prerequisites or preflight. Standard utilities (git, curl, python, node, npm, pip) are exempt. Fail if any required non-standard dependency is undocumented. This is a blocking condition.
- `pre_screen.no-verification` - Consequential operations have verification
  - Review: Check whether the skill performs consequential operations (generates code, modifies configs, deploys, creates infrastructure). If so, verify at least one concrete command or check confirms the output is correct. 'Review the output' is not sufficient. Fail if consequential operations have no operational verification. This is a blocking condition.
- `pre_screen.bloated-body` - SKILL.md is within its size limit and references do not chain
  - Review: Check SKILL.md is within the character limits in references/SKILL_SPEC.md; reference files have no size budget, so do not judge one by its length. Check no reference DEPENDS on a sibling: a sibling link is legal only as a marked citation (`<!-- citation -->`, stating where a fact lives) or as a parent indexing down into its own subdirectory. Apply the test: if the agent never follows this link, does the work still complete? Yes means citation; no means dependency, which fails. `scripts/quick_validate.py` decides all of this mechanically — run it rather than judging by eye.
