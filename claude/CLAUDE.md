## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- First think through the problem, read the codebase for relevant files.
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask; Acknowledge uncertainty rather than guessing.
- Break problems into smaller, manageable steps and help me think through them.
- Do not make assumptions or speculate about code you have not read; If the user references a specific file, you MUST read the file before answering.
- Make sure to investigate and read relevant files BEFORE answering questions about the codebase - give grounded and hallucination-free answers.
- When dealing with code from external libraries, make sure to read (or ask to be pointed to) their documentation and understand how they work. Never make assumptions about the library's behavior or code.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked; Follow requirements carefully and precisely, don't overthink and don't make assumptions.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.
- Every change should impact as little code as possible (without compromising on correctness and functionality) and should be as simple as possible.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Before you make any major changes, check in with me and I will verify the plan.
- On every step, give me a high level explanation of what changes you made.
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it; Pay attention to preserving existing structures.
- Always consider and handle potential edge cases.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

Make a best effort to keep files small:

- If plan files you made are too big (up to 400 lines) - split them into logical phases/batches so that each file contains logically-connected items and that the file won't take up a lot of the context window.
- If summary document files you made are too big (up to 600 lines) - split them into logical phases/batches so that each file contains logically-connected items and that the file won't take up a lot of the context window.
- If code files are becoming too big (up to 600 lines) try to group methods that fit together logically and suggest to split them to another file.
- If test files are becoming too big (up to 500 lines) try to group methods that fit together logically and suggest to split them to another file.
- Threshold for taking action: do not split existing files you see unless adding content will make them big. Do not act on documents up to 30% larger then recommendation.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## Multi-Agent Workflows

- When working in multi-agent teams, always check the task list for unclaimed tasks before starting work. Never duplicate another agent's assigned task without explicit reassignment from the team lead.
- Before starting any task, first run TaskList to see all tasks and their assignments. Only work on tasks explicitly assigned to you or unclaimed tasks. If all your assigned tasks are complete, report back to the team lead instead of picking up someone else's task.

## Testing

- Always run the full test suite after making code changes. 
  - For Python projects, run `uv run pytest`
  - For Java projects, run `mvn test`
- Ensure all tests pass before committing. If tests fail, fix them before reporting completion.

## 5. General Guidelines

- Prefer using tools from the `serena` MCP server when navigating, searching, reading and editing code (i.e. `find_symbol`, `get_symbols_overview`, `insert_at_line`, `list_dir`, `read_file`, `replace_lines` etc.).
- **CRITICAL**: NEVER EVER DIRECTLY MODIFY FILES IN A `.git` folder - that is STRICTLY FORBIDDEN. Only use standard `git` commands, if any command fails ask me what to do or retry **THIS IS A CRUCIAL NON-NEGOTIABLE CONSTRAINT YOU MUST FOLLOW ALWAYS**. If git add/commit commands fail you may notify me and skip them.

---

## Using tools and running commands

- Use `uv` for all Python related package, install, run etc. actions.
- Use `mvn` for java.
- Use `sbt` for scala.
- Use `npm` for node.
