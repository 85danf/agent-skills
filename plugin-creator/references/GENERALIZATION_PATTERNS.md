# Generalization Patterns

The core rule: environment-specific values move into first-run setup prompts, config,
discovery scripts, or CLI arguments, while reusable logic stays in scripts.

When converting a specific script into a generic skill, replace project-specific facts with configuration, CLI args, or reference files.

| Hardcoded element | Generalization |
|---|---|
| API base URL | Config field, for example `"base_url": "https://..."` |
| Profile, account, tenant, environment, or region names | Config map keys, aliases, discovery output, or explicit CLI args |
| Service, app, job, queue, or index names | Config arrays, discovery commands, or user-supplied filters |
| File paths | CLI `--path` argument with sensible default, often cwd |
| Schema fields or custom fields | Config fields with portable defaults, discovery, or documented overrides |
| Workflow labels, routing terms, status service names, or team-specific acronyms | Configurable patterns or learned/discovered values |
| Output format | CLI `--output` flag, for example terminal/json/markdown |
| Hardcoded lists/mappings | Config arrays or reference files |
| Magic numbers | Named config fields with defaults |

## Six-Point Script Analysis

Run this before generalizing an existing script. It supplies most of the Step 1
intent answers, so ask the user only about what the code cannot show.

1. **Purpose**: What does the script do? What problem does it solve?
2. **Hardcoded values**: URLs, project keys, credentials, paths, field names,
   profile names, environment labels, service identities, workflow labels, routing
   keywords, tenant or account labels, and other instance-specific names — these
   become config, discovery, CLI args, or placeholders (see the table above).
3. **Dependencies**: Python packages, CLI tools, APIs, environment variables.
4. **Input/output**: What does it take in? What does it produce?
5. **Side effects**: Does it read, write, publish, deploy, restart, exec, or delete
   external resources? Classify each into no-approval, bounded-approval, and
   fresh-approval tiers.
6. **Error modes**: What can go wrong? How does it fail?

Keep a map of every function and data flow in the original script — it is what
proves in `Step 8 — Verify` that nothing was lost during generalization.

## Troubleshooting Patterns

| Problem | Fix |
|---|---|
| `<runtime>: command not found` | Install the required runtime: Python, Node, Go, etc. |
| `Module/Package missing` | Run the setup script or install dependencies manually |
| Config field not working | Run discovery script to auto-detect field IDs |

## Generalization Rules

1. Replace hardcoded URLs, project keys, credentials, paths, field names, usernames, profile names, environment labels, aliases, service identities, workflow labels, routing keywords, and IDs with config fields, discovery, CLI arguments, or placeholders.
2. Keep reusable business logic in scripts.
3. Keep environment-specific values out of `SKILL.md`, scripts, references, and assets unless they are obvious placeholders in examples.
4. Do not turn example labels into workflow branches, default profile choices, or natural-language inference rules; derive valid labels from config, discovery, or explicit user input.
5. Add discovery commands when valid values can be fetched from the external system.
6. Add dry-run previews for destructive operations.
7. Add verification commands that prove the generalized version preserves the original capability.

## Explicit Defaults Exception

Hidden instance-specific behavior fails review. Explicit defaults may pass when
all of these are true:

1. The user or target maintainer intentionally chose the default.
2. The default is documented as a default, not implied as universal behavior.
3. The default is configurable, overrideable, or discoverable.
4. The skill still works for another instance after changing config or setup.
5. The review coverage matrix records the portability impact.

Example:

- Bad: route all "urgent" tickets to a hardcoded team queue because the source
  script did that.
- Good: document `default_queue: urgent-support` as a sample config value,
  allow override, and explain how to discover valid queues.
