---
name: review-pr
description: Comprehensive PR/diff review across code quality, tests, comments, error handling, and type design, using six specialist checklists (references/specialists/) dispatched as subagents or worked through sequentially; also offers to simplify code after a passing review. Trigger when the user asks to review a pull request or diff, wants a pre-commit/pre-PR quality check, or asks about test coverage, comment accuracy, silent failures/error handling, or type design on recent changes.
---

# Comprehensive PR Review

Run a comprehensive pull request review using multiple specialist checklists, each focusing on a different aspect of code quality.

The user may optionally name specific review aspects to run (e.g. "tests", "errors", "comments", "types", "code", "simplify", or "all"). If they don't, run all applicable reviews.

## Review Workflow

### 1. Determine Review Scope

- Check git status to identify changed files
- Parse any user-specified review aspects
- Default: run all applicable reviews

### 2. Available Review Aspects

- **comments** - Analyze code comment accuracy and maintainability
- **tests** - Review test coverage quality and completeness
- **errors** - Check error handling for silent failures
- **types** - Analyze type design and invariants (if new types added)
- **code** - General code review for project guidelines
- **simplify** - Simplify code for clarity and maintainability
- **all** - Run all applicable reviews (default)

### 3. Identify Changed Files

- Run `git diff --name-only` to see modified files
- Check if a PR already exists (e.g. `gh pr view`)
- Identify file types and which reviews apply

### 4. Determine Applicable Reviews

Based on changes:
- **Always applicable**: code-reviewer (general quality)
- **If test files changed**: pr-test-analyzer
- **If comments/docs added**: comment-analyzer
- **If error handling changed**: silent-failure-hunter
- **If types added/modified**: type-design-analyzer
- **After passing review**: code-simplifier (polish and refine)

### 5. Launch Review Agents

Each specialist's full checklist lives in `references/specialists/`:
`code-reviewer.md`, `pr-test-analyzer.md`, `comment-analyzer.md`, `silent-failure-hunter.md`, `type-design-analyzer.md`, `code-simplifier.md`.

- **On a platform with subagent/parallel-task dispatch** (e.g. Claude Code's Task tool): dispatch each applicable specialist (`references/specialists/*.md`) as its own subagent — in parallel if the user asked for a fast comprehensive review, or sequentially if not.
- **On a platform without subagent dispatch**: work through each applicable specialist's checklist yourself in the same order, one at a time, noting its findings before moving to the next.

Sequential is easier to understand and act on — each report is complete before the next starts, which suits interactive review. Parallel is faster for a comprehensive one-shot review, with all results coming back together; use it when the user asks for speed or explicitly requests a parallel/full review.

### 6. Aggregate Results

After all applicable reviews complete, summarize:
- **Critical Issues** (must fix before merge)
- **Important Issues** (should fix)
- **Suggestions** (nice to have)
- **Positive Observations** (what's good)

### 7. Provide Action Plan

Organize findings:

```markdown
# PR Review Summary

## Critical Issues (X found)
- [specialist-name]: Issue description [file:line]

## Important Issues (X found)
- [specialist-name]: Issue description [file:line]

## Suggestions (X found)
- [specialist-name]: Suggestion [file:line]

## Strengths
- What's well-done in this PR

## Recommended Action
1. Fix critical issues first
2. Address important issues
3. Consider suggestions
4. Re-run review after fixes
```

## Usage Examples

**Full review (default):** Review the current diff (or PR) using all applicable specialists.

**Specific aspects:** The user may ask for just a subset, e.g. "review tests and error handling" (runs only pr-test-analyzer and silent-failure-hunter), or "review comments" (runs only comment-analyzer), or "simplify this" (runs code-simplifier after a passing review).

**Fast/parallel review:** If the user asks for a fast or comprehensive review, dispatch all applicable specialists in parallel (where the platform supports it) rather than one at a time.

## Specialist Summaries

**comment-analyzer** (`references/specialists/comment-analyzer.md`):
- Verifies comment accuracy vs code
- Identifies comment rot
- Checks documentation completeness

**pr-test-analyzer** (`references/specialists/pr-test-analyzer.md`):
- Reviews behavioral test coverage
- Identifies critical gaps
- Evaluates test quality

**silent-failure-hunter** (`references/specialists/silent-failure-hunter.md`):
- Finds silent failures
- Reviews catch blocks
- Checks error logging

**type-design-analyzer** (`references/specialists/type-design-analyzer.md`):
- Analyzes type encapsulation
- Reviews invariant expression
- Rates type design quality

**code-reviewer** (`references/specialists/code-reviewer.md`):
- Checks CLAUDE.md (or equivalent project-guideline) compliance
- Detects bugs and issues
- Reviews general code quality

**code-simplifier** (`references/specialists/code-simplifier.md`):
- Simplifies complex code
- Improves clarity and readability
- Applies project standards
- Preserves functionality

## Tips

- **Run early**: Before creating a PR, not after
- **Focus on changes**: Analyze the git diff by default
- **Address critical first**: Fix high-priority issues before lower priority
- **Re-run after fixes**: Verify issues are resolved
- **Use specific reviews**: Target specific aspects when you know the concern

## Workflow Integration

**Before committing:**
1. Write code
2. Run a review focused on code quality and error handling
3. Fix any critical issues
4. Commit

**Before creating a PR:**
1. Stage all changes
2. Run the full review (all aspects)
3. Address all critical and important issues
4. Run specific reviews again to verify
5. Create the PR

**After PR feedback:**
1. Make requested changes
2. Run targeted reviews based on feedback
3. Verify issues are resolved
4. Push updates

## Notes

- Each specialist focuses on its specialty for deep analysis
- Results are actionable with specific file:line references
- Findings should be reported with confidence/severity levels per specialist as documented in `references/specialists/*.md`
