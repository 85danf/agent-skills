# LSP Component

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only
> skill.** This component and its runtime mechanics (frontmatter fields, JSON
> schema, `am-pm validate` command) exist only in Claude Code plugins; there is no
> equivalent in the portable Agent Skills standard or in Codex.


## What It Does

An LSP component declares language-server support that can improve code
navigation, diagnostics, and edits for skills or plugins that work with a
specific language or file format.

## Marketplace First

Before creating a custom LSP component, check the marketplace for pre-built LSP
plugins (e.g. pyright-lsp, typescript-lsp, rust-analyzer-lsp). These are
already tested and maintained.

## Capabilities

- Registers one or more language servers so the plugin can provide diagnostics,
  navigation, and language-aware editing support for specific file types.
- The file is a JSON object keyed by server name.
- Each server declares the executable `command` and maps file extensions to
  language IDs with `extensionToLanguage`.
- Optional `args` pass command-line arguments. Optional `env` provides string
  environment variables.
- Do not wrap servers in another object; `.lsp.json` starts directly with the
  server names.

Minimal shape:

```json
{
  "python": {
    "command": "pyright-langserver",
    "args": ["--stdio"],
    "extensionToLanguage": {
      ".py": "python"
    }
  }
}
```

## Additional Fields

Beyond the required `command` and `extensionToLanguage`, each LSP server entry
supports these optional fields:

- `transport` -- transport protocol: `stdio` (default) or `socket`.
- `initializationOptions` -- LSP initialization options (arbitrary object).
- `settings` -- LSP server settings (arbitrary object).
- `workspaceFolder` -- workspace folder path.
- `startupTimeout` -- startup timeout in milliseconds (integer).
- `maxRestarts` -- maximum automatic restarts (integer). The server
  auto-restarts up to this many times on crash, then gives up.

## Trust Gating

Project-scope plugins' LSP servers start only after workspace trust is granted.
Until the user accepts trust, the language server will not launch.

## Crash Behavior

If a language server crashes, Claude Code automatically restarts it up to
`maxRestarts` times. After exhausting restarts the server stays down for the
rest of the session.

## Common Pitfall: Executable Not Found

The plugin does not bundle the server binary. If the language server executable
is not found in `$PATH`, the server fails to start. Document any required
runtime or package manager in the skill prerequisites so users install it first.

## Cost

An LSP applies a broad family of deterministic code operations — diagnostics, definitions,
references, symbols, rename — **in real time, as code is edited**, decided by a language
server instead of inferred from text. The timing is the advantage: the agent learns it broke
something while making the edit, not at a build later on.

The same property is a cost. `diagnostics` defaults to `true`, so the server injects into
context after every edit — continuous value bought with continuous context.

Three more costs are unrelated to the timing. **LSP does not run in cloud sessions at all**,
and the plugin does not ship the binary (see Common Pitfall above), so any guarantee you rest
on an LSP holds only where a language server is actually running — decide what the skill does
when none is. The first server registered for an extension also wins it, so shipping one
changes behaviour for every other plugin the user has installed.

## Use When

- The skill routinely edits or reviews a language where LSP diagnostics reduce
  drift or mistakes.
- The language server is portable, documented, and reasonable for the target
  users to install or run.
- LSP feedback complements tests, validators, or formatter checks.

## Do Not Use When

- The skill does not operate on code or structured files with useful LSP
  support.
- The language server setup is heavy, brittle, or environment-specific.
- Existing repo tooling already gives the needed diagnostics.

## Monorepo Path

- Plugin file: `groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/.lsp.json`

## Best Practices

- Keep server declarations portable and avoid local absolute paths.
- For plugin-bundled language server binaries or wrappers, use
  `${CLAUDE_PLUGIN_ROOT}/scripts/<name>` in `command`. Relative paths do
  not resolve when the plugin is installed outside the project root.
- Document any required runtime or package manager in the skill prerequisites.
- Treat LSP as assistance, not the only validation path.
- Pair LSP guidance with deterministic tests or validators where possible.

## Validation

- Run `am-pm validate lsp-bundle .lsp.json`.
- Confirm each server has `command` and `extensionToLanguage`.
- Confirm `args` is a string list and `env` values are strings when present.
- Run a language-server startup or diagnostics smoke test when practical.
- Confirm fallback behavior is documented when LSP is unavailable.
