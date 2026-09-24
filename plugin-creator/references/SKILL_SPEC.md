# Agent Skills Specification Reference

Summary of the Agent Skills open standard from [agentskills.io/specification](https://agentskills.io/specification).

## Directory structure

```text
skill-name/
└── SKILL.md          # Required
```

Optional additional directories:

```text
skill-name/
├── SKILL.md          # Required
├── scripts/          # Executable code the agent can run
├── references/       # Detailed technical docs loaded on demand
└── assets/           # Templates, images, data files, schemas
```

## SKILL.md format

### Frontmatter (required)

```yaml
---
name: skill-name
description: >
  A description of what this skill does and when to use it.
  Include action verbs and domain keywords for agent matching.
metadata:
  author: org-or-user
  version: "1.0"
compatibility: >
  Runtime requirements (Python 3.10+, Node.js, etc.)
---
```

#### Field rules

| Field | Required | Constraints |
|---|---|---|
| `name` | Yes | 1-64 chars, lowercase alphanumeric + hyphens, must match parent directory name, no leading/trailing/consecutive hyphens |
| `description` | Yes | 1-1024 chars, describe what the skill does AND when to use it, include trigger keywords |
| `compatibility` | No | 1-500 chars, only if specific environment requirements exist |
| `metadata` | No | Map of string keys to string values for additional properties |
| `allowed-tools` | No | Space-delimited list of pre-approved tools (experimental) |
| `disallowed-tools` | No | Space-delimited list or YAML array of tools the skill must not use |
| `model` | No | Model preference (e.g. `opus`, `sonnet`, `haiku`) |
| `effort` | No | Reasoning effort: `low`, `medium`, `high`, or `max` |
| `context` | No | How the skill loads: `fork`, `inject`, or `none` |
| `agent` | No | Subagent name to run in when `context: fork` |
| `when_to_use` | No | Alternative trigger description |
| `argument-hint` | No | Hint text shown when the user types the skill name |
| `arguments` | No | Map of named arguments the skill accepts |
| `disable-model-invocation` | No | Boolean: prevent model from auto-invoking |
| `user-invocable` | No | Boolean: allow direct user invocation |
| `hooks` | No | Inline hook definitions scoped to this skill |
| `paths` | No | File path patterns the skill operates on |
| `shell` | No | Preferred shell: `bash`, `zsh`, `fish`, `powershell`, or `cmd` |

#### Name validation examples

- `pdf-processing` — valid
- `data-analysis` — valid
- `code-review` — valid
- `PDF-Processing` — invalid (uppercase)
- `-pdf` — invalid (leading hyphen)
- `pdf--processing` — invalid (consecutive hyphens)

### Body content

The body follows the frontmatter and contains markdown instructions. Recommended sections:

1. Step-by-step instructions
2. Examples of inputs and outputs
3. Common edge cases

## Progressive disclosure

Agents load skills in three stages:

1. **Metadata** (~100 tokens): `name` and `description` fields loaded at startup for all skills
2. **Instructions**: the full SKILL.md body, loaded when the skill is activated.
   Size is authoritative in **characters**: `quick_validate.py` WARNS above 20,000 and
   FAILS above 25,000. A line count is a *smell test only* — lines move with wrapping,
   tables, and code fences without changing what the model reads. These are the only
   body-size numbers; do not restate them.
3. **Resources** (as needed): Files in `scripts/`, `references/`, `assets/` loaded only when required

This means the `description` field is critical — it determines whether the agent activates the skill at all.

A skill's constraints are **soft and invisible**, which is the flip side of it being cheap
to build: the description competes for attention inside roughly a 1% context-window budget
under a 1,536-char per-entry cap, and on overflow descriptions are dropped least-used-first
— which can strip keywords a *different* skill needed. A skill degrades silently under
pressure; a hook, monitor, or LSP fails hard and loudly.

## File references

Reference supporting files from SKILL.md using relative paths:

```markdown
See [the config reference](references/CONFIG.md) for the full schema.
Run the setup script: `python3 <skill_dir>/scripts/setup_env.py`
```

## Optional directories

### scripts/

- Be self-contained or clearly document dependencies
- Include helpful error messages
- Handle edge cases gracefully

### references/

- `CONFIG.md` — Detailed config schema reference
- `FORMAT.md` — Input/output format specifications
- Domain-specific files (field mappings, plan formats, etc.)

### assets/

- Templates (document templates, configuration templates)
- Images (diagrams, examples)
- Data files (lookup tables, schemas, default configs)

## Skill scopes (Windsurf-specific)

| Scope | Location | Availability |
|---|---|---|
| Workspace | `.windsurf/skills/<name>/` | Current project only |
| Global | `~/.codeium/windsurf/skills/<name>/` | All projects |
| Agent Skills standard | `.agents/skills/<name>/` | Cross-agent portable |

## Claude Code Runtime Behavior

These details affect skill authoring decisions.

### Naming

The invocation name comes from the directory name, not `name` frontmatter.
`name` is a display label only. Choose the directory name carefully.

### Content budget

On invocation the full SKILL.md body enters the conversation and stays for the
session. Auto-compaction keeps the first ~5 000 tokens per skill, ~25 000
combined across all loaded skills. Design the body to front-load the most
important content.

### String substitutions

The body supports dynamic placeholders resolved at load time:

| Placeholder | Expands to |
|---|---|
| `$ARGUMENTS` | Full argument string the user typed after the skill name. |
| `$ARGUMENTS[N]` | Nth positional argument (0-indexed). |
| `$name` | Named argument value (from `arguments` frontmatter). |
| `${CLAUDE_SESSION_ID}` | Current session identifier. |
| `${CLAUDE_EFFORT}` | Current effort level. |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the skill directory. |
| `` !`command` `` | Runs the shell command at load time and injects its stdout. |

### Frontmatter: am-pm vs Claude Code

am-pm validation requires `name` and `description`. Claude Code treats all
frontmatter as optional. The combined `description` + `when_to_use` text is
truncated at 1 536 characters in skill listings.

`allowed-tools` is a **grant list** — it permits listed tools without
prompting. It does not restrict which tools are available; every tool remains
callable.

### Additional Claude Code fields

| Field | Type | Values / Notes |
|---|---|---|
| `when_to_use` | string | Trigger phrase; combined with `description`, truncated at 1 536 chars. |
| `argument-hint` | string | Hint shown when user types the skill name. |
| `arguments` | object | Named arguments (key → description). Values substituted via `$name`. |
| `user-invocable` | boolean | Whether skill appears in `/` listing. Default `true`. |
| `disable-model-invocation` | boolean | When `true`, model cannot auto-invoke this skill. |
| `disallowed-tools` | string or string[] | Blocks these tools during execution. |
| `model` | string | Override session model, e.g. `claude-sonnet-4-5`. |
| `effort` | enum | `low`, `medium`, `high`, `xhigh`, `max`. |
| `context` | enum | `fork` runs in a subagent fork. |
| `agent` | string | Subagent name when `context: fork`. |
| `hooks` | object | Inline hook definitions scoped to this skill. |
| `paths` | string or string[] | File-path globs the skill operates on. |
| `shell` | enum | `bash`, `powershell`. |

## Validation

Use the `skills-ref` CLI to validate a skill:

```bash
skills-ref validate ./my-skill
```

Checks: frontmatter present and valid, name matches directory, description within length limits.
