---
name: review-plan-team-mode
description: Use when reviewing plan documents against their source design or brainstorm documents to verify alignment, completeness, and correctness. Triggers when user wants to validate a plan before executing it, check plan-design alignment, verify nothing from the design is missing in the plan, or ensure plan code/pseudocode matches the design intent. Use this skill whenever the user mentions reviewing, validating, or checking plans against designs, architectures, specs, brainstorms, or requirements documents.
---

# Reviewing Plan Against Design

Verify that implementation plans are correctly derived from their source design documents using a team of parallel reviewer agents.

**Prerequisite:** Requires experimental agent teams. Enable `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` in settings.json or environment.

## Workflow

### Step 1: Classify Input Files

Examine every `@`-referenced file. Classify each as **design** or **plan**:

| Signal            | Design doc                                                            | Plan doc                                                  |
| ----------------- | --------------------------------------------------------------------- | --------------------------------------------------------- |
| Filename contains | `architecture`, `design`, `brainstorm`, `spec`, `rfc`, `requirements` | `plan`, `implementation`, `task`, `phase`, `batch`        |
| Content structure | Goals, principles, decisions, tradeoffs, diagrams                     | Steps, tasks, acceptance criteria, pseudocode, file paths |
| Tone              | "We should...", "The system will...", "Key decision:"                 | "Create file X", "Add method Y", "Step 1: implement..."   |

If classification is ambiguous for any file, ask the user. Do not guess.

### Step 2: Determine Mapping Strategy

| Scenario            | Strategy                                          |
| ------------------- | ------------------------------------------------- |
| 1 design + 1 plan   | Direct. One review pair.                          |
| 1 design + N plans  | Auto-map all plans to the single design. N pairs. |
| N designs + M plans | Ask the user to map them explicitly.              |

For N:M, prompt the user:

```
I found multiple design and plan docs. Which design verifies which plan(s)?

Design docs: design-auth.md, design-api.md
Plan docs: plan-auth.md, plan-api.md, plan-integration.md

Example: "design-auth -> plan-auth, design-api -> plan-api + plan-integration"
```

### Step 3: Create Team and Spawn Reviewers

#### 3a. Create the team

```
TeamCreate:
  team_name: "design-plan-review"
  description: "Review plan documents against design documents for alignment and correctness"
```

#### 3b. Create tasks

For each (design, plan) pair, create a task:

```
TaskCreate:
  subject: "Review '{plan_filename}' against '{design_filename}'"
  description: |
    Design document: {absolute_path_to_design_doc}
    Plan document: {absolute_path_to_plan_doc}

    Follow the review protocol in agents/design-reviewer.md.
    Read both documents in full. Execute all 6 review checks.
    Report structured findings to the team lead via SendMessage.
  activeForm: "Reviewing {plan_filename} against {design_filename}"
```

#### 3c. Spawn reviewer teammates

Spawn ALL teammates in a single message for parallel execution. For each pair (indexed from 1):

```
Task:
  team_name: "design-plan-review"
  name: "reviewer-{index}"
  subagent_type: "general-purpose"
  description: "Review plan against design"
  prompt: |
    You are a reviewer on the `design-plan-review` team.

    1. Read agents/design-reviewer.md — your complete review protocol.
    2. Use TaskList to find available tasks. Claim one with TaskUpdate
       (set owner to your name, status to in_progress).
    3. Read BOTH documents in your task fully before writing findings.
    4. Perform all 6 review checks from agents/design-reviewer.md.
    5. Produce structured output per agents/design-reviewer.md format.
    6. Mark task completed with TaskUpdate.
    7. Send full findings to team lead via SendMessage (type: "message").

    Rules:
    - Do NOT skip any review check.
    - Every finding MUST cite specific text from both documents.
    - If you receive a shutdown_request, respond with shutdown_response.
```

### Step 4: Aggregate Results

1. Wait for messages from every spawned reviewer.
2. If a reviewer goes idle without sending results, message it to check status (idle is normal — it just means the reviewer is waiting).
3. Merge findings into the summary format below. Deduplicate if multiple reviewers flag the same issue.

### Step 5: Shutdown and Cleanup

After presenting the summary to the user:

1. Send `shutdown_request` to each reviewer via SendMessage.
2. Wait for `shutdown_response` from each.
3. Run `TeamDelete` to clean up team resources.
4. Confirm to the user that the review team has been disbanded.

## Aggregated Output Format

```markdown
# Design-Plan Review Summary

## Review Pairs

| #   | Design Document | Plan Document | Assessment                                |
| --- | --------------- | ------------- | ----------------------------------------- |
| 1   | `{design_doc}`  | `{plan_doc}`  | Aligned / Aligned with Fixes / Misaligned |

## Overall Assessment: [Aligned / Aligned with Fixes / Misaligned]

- **Aligned**: Zero critical, zero or few important issues
- **Aligned with Fixes**: Important issues exist, or 1-2 straightforward critical issues
- **Misaligned**: Multiple critical issues or fundamental disconnect

## Critical Issues (X found)

- [Pair #N]: {description} [{design}:{section} -> {plan}:{section}]

## Important Issues (X found)

- [Pair #N]: {description} [{design}:{section} -> {plan}:{section}]

## Minor Issues (X found)

- [Pair #N]: {description}

## Strengths

- What is well-aligned

## Recommended Actions

1. Fix critical issues first
2. Address important issues
3. Consider minor improvements
```

## Error Handling

- **No files provided:** Ask user for both design and plan documents via `@` references.
- **Only one type:** Tell user which type is missing.
- **Ambiguous classification:** Ask user to clarify.
- **N:M mapping unclear:** Ask user to specify. Do not guess.
- **Reviewer unresponsive:** Message it for status. If still silent after a second attempt, note the gap and proceed.
- **TeamDelete fails:** Inform user that manual cleanup may be needed.
