# Genericity Criteria

Generated from `../../assets/skill-quality-criteria.json`. Do not edit by hand.

Use this lane while making generic/shared plugins work across repos and organizations.

## Examples

- Good: Configure service URLs, profile names, environments, queues, and credential environment variables in a project config file; scripts accept explicit profile arguments and discover available labels when possible.
- Bad: Default to one workplace's production profile, read a user-specific absolute path, or assume one release branch.

## `genericity.runtime-vocabulary` - Runtime vocabulary is generic

Make profile names, environments, queues, teams, tenants, workflow labels, field names, URLs, credential names, and other runtime vocabulary configurable, discoverable, CLI-provided, or obvious placeholders.

## `genericity.no-local-assumptions` - No local assumptions leak into behavior

Do not bake organization-specific identifiers, paths, naming conventions, status services, repository hosts, branches, projects, dashboards, or workflow rules into behavior.
