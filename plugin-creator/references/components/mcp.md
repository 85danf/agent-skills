# MCP Component

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only
> skill.** This component and its runtime mechanics (frontmatter fields, JSON
> schema, `am-pm validate` command) exist only in Claude Code plugins; there is no
> equivalent in the portable Agent Skills standard or in Codex.


## What It Does

An MCP component connects the agent to an MCP server packaged or declared by
the plugin. It can expose tools, resources, or prompts that are useful at
runtime.

## Capabilities

- Registers one or more MCP servers that can expose runtime tools, resources,
  or prompts to the agent.
- The file is JSON with a top-level `mcpServers` object keyed by server name.
- Servers can be local `stdio` processes or remote `http`, `sse`, or `ws`
  endpoints. `streamable-http` is an alias for `http`. Prefer `http` for remote
  servers; `sse` exists for compatibility.
- Local stdio servers declare the executable `command`. Optional `args` pass
  command-line arguments. Optional `env` provides string environment variables.
  Optional `cwd` sets the working directory for the process.
- Remote servers declare `type` and `url`. Optional `headers` provide static
  request headers, `headersHelper` generates dynamic headers, and `oauth`
  configures OAuth fields such as `clientId`, `callbackPort`,
  `authServerMetadataUrl`, and `scopes`.
- `timeout` sets per-server tool execution timeout in milliseconds.
  `alwaysLoad` can require eager connection on supported Claude Code versions.
- Plugin MCP servers connect automatically at session startup. Use
  `/reload-plugins` to reconnect after enabling or disabling a plugin.

Minimal local shape:

```json
{
  "mcpServers": {
    "example": {
      "type": "stdio",
      "command": "node",
      "args": ["scripts/example-mcp.js"],
      "env": {
        "EXAMPLE_TOKEN_ENV": "EXAMPLE_TOKEN"
      }
    }
  }
}
```

Minimal remote shape:

```json
{
  "mcpServers": {
    "example-remote": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${EXAMPLE_TOKEN}"
      }
    }
  }
}
```

## Runtime Approval

Claude Code prompts the user for approval before using MCP servers declared in
project-scoped `.mcp.json` files. Plugin MCP servers also require per-server
approval for project-scope plugins.

## Scope Precedence

When multiple scopes define MCP servers, the effective configuration follows
this precedence (highest wins): local > project > user > plugin.

## Reconnection

HTTP and SSE transports auto-reconnect with exponential backoff (up to 5
attempts). Stdio servers do NOT reconnect automatically; a crash requires
restarting the session or running `/reload-plugins`.

## Plugin Variables

For stdio servers that bundle scripts inside the plugin, use
`${CLAUDE_PLUGIN_ROOT}/scripts/<name>` in `command` or `args` to reference the
plugin directory. Use `${CLAUDE_PLUGIN_DATA}` to reference the plugin's
writable data directory. Relative paths do not resolve correctly when the plugin
is installed outside the project root.

## Cost

An MCP server buys what a local script cannot: a live, typed tool surface backed by state
that survives across calls — a running browser, a warm index, an authenticated session.

It costs a connection made at session startup whether or not the capability is used, and a
line per tool in the model's tool list whether or not the tool is ever called. It costs an
approval posture you have to design rather than inherit: project-scope servers are approved
per server (see Runtime Approval above), so a server nobody approves is a capability nobody
has, and the skill needs a path for that case. And it costs a dependency and a security
review, and gives up portability a script would keep.

## Use When

- The user explicitly asks for MCP or the integration is already approved and
  maintained as an MCP server.
- The server provides capabilities that are hard to express as direct API
  scripts or local CLIs.
- The review artifact can record explicit user attestation that the MCP server
  is security-approved for company use.

## Do Not Use When

- A direct API script or existing CLI can interact with the third-party SaaS,
  website, or service clearly and safely.
- The user cannot attest that the MCP server is security-approved for company
  use.
- The integration would require broad secrets or permissions without a clear
  approval and audit story.

## Monorepo Path

- Plugin file: `groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/.mcp.json`

## Best Practices

- Prefer direct API scripts or CLIs for third-party SaaS, websites, and
  services unless the user overrides that default.
- When MCP is included, record why direct API usage was not chosen.
- Record the user's security approval in the `component-fit.mcp-approval` row of
  `coverage.yml`: status `pass`, evidence naming the server, approver, and date.
  The CI gate reads that row when `.mcp.json` changes; the schema is closed, so a
  separate section has nowhere to live.
- Keep MCP server permissions as narrow as the workflow allows.

## Validation

- Run `am-pm validate mcp-bundle .mcp.json`.
- Confirm every stdio server has `command`.
- Confirm every remote server has `type` and `url`.
- Confirm `args` is a string list and `env` values are strings when present.
- Confirm `headers` values are strings and OAuth scope/metadata fields match
  the security-approved grant.
- Run the MCP server's own health or list-tools check when available.
- Run review coverage validation with MCP approval required whenever a
  plugin includes `.mcp.json`.
