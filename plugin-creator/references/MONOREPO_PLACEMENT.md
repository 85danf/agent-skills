# am-pm monorepo placement

> **Claude Code plugin-specific — skip entirely if authoring a portable/Codex-only
> skill, or a skill outside the am-pm monorepo.** This file only applies inside the
> specific "am-pm" Claude Code plugin monorepo this methodology originated in. If
> you are not working inside that repo, skip straight to the plain global/workspace/
> shared-repo placement decision and do not read the rest of this file.

Plugin-creator is portable. Used **standalone**, it makes the "Where to store the
skill" design decision (global / workspace / shared repo) and this reference does
not apply. But when it runs **inside the am-pm plugin monorepo**, the new plugin
must land in the correct taxonomy slot —
`groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/` — instead of a default spot. This
is decided during `Step 3 — Design section`, where the new skill's location is
chosen.

## Detect the monorepo and get a placement recommendation

There is **no hardcoded path** — the helper walks up from the current directory
looking for the marker triple (`groups/` directory + `ci/` directory +
`pyproject.toml` with `name = "am-pm"`). Get a recommendation in one call:

```bash
python3 <skill_dir>/scripts/monorepo_placement.py \
  --group <group> --intent "<one-line purpose>" --json
```

- If the result is `{"in_monorepo": false}`, you are **standalone** — keep the
  normal global / workspace / shared decision. **Do not** consult where-does-it-fit
  (it is not available outside the monorepo); behavior is unchanged.
- If `in_monorepo` is true, consult the **where-does-it-fit** skill to choose the
  target group, then domain. The command above bridges to that skill for you — its
  `suggestion` carries `best_domain`, `recommend_new_domain`, and ranked `matches`;
  you may also invoke the where-does-it-fit skill directly.

## What each language costs at the gate

A plugin's shippable source may be Python, TypeScript, or **both** — the language
is a SET, not a choice. Whichever are present, all of these hold:

- **Every language present runs its own full toolchain.** Python source runs
  ruff, mypy, bandit, and pip-audit; TypeScript source runs biome, tsc, and
  npm-audit. Shipping both means running both.
- **The coverage floor is unconditional and per language.** Shipping source of a
  language with no tests of that language counts as 0% covered and FAILS, unless
  the group's config sets its floor to 0. A plugin's test languages must be a
  SUBSET of its source languages.
- **POSIX shell (`.sh` only) is a supplementary layer**, not a third language:
  ShellCheck and shfmt are mandatory and presence-gated, and shell tests carry the
  same group coverage floor.
- **No other code extension is accepted** — `.js`, `.rb`, `.go`, `.bash`,
  `.svelte`, `.vue` and the rest fail, case-insensitively, even inside a committed
  `dist/`. Non-code and markup assets (`.html`, `.css`, `.svg`) are fine.
- **Third-party dependencies are pinned at the DOMAIN level**, not in the plugin:
  Python packages go `==`-pinned in `groups/<group>/<domain>/pyproject.toml`, Node
  packages in `groups/<group>/<domain>/package.json`.

Two plugins joined by a bundle `dependencies` list remains the recommended
default; a single multi-language plugin is right only when the halves are one
capability that cannot be installed separately.

## Resolve the exact scaffold path

Pick the `lifecycle` tier separately (new work usually starts `alpha` or `beta`).
Then scaffold into `groups/<group>/<domain>/<lifecycle>/plugins/<plugin>/` with the repo's
conventions:

- the skill under `skills/<name>/`,
- co-located **lifecycle-level** siblings (NOT inside the plugin, so they travel
  with it in one `git mv` on promotion): tests in
  `groups/<group>/<domain>/<lifecycle>/tests/<plugin>/`, docs in
  `groups/<group>/<domain>/<lifecycle>/docs/<plugin>/public/` (the site-rendered
  `<plugin>-design.md` and any user-facing guide) with plans and notes in
  `groups/<group>/<domain>/<lifecycle>/docs/<plugin>/internal/`,
  and reviews (the skill-review-coverage matrix `coverage.yml`) in
  `groups/<group>/<domain>/<lifecycle>/reviews/<plugin>/`,
- path-derived metadata (no separate `plugins/` tree and no build step — the
  committed folder is what ships; CI regen picks it up).

Get the exact `init_skill.py --path` for the chosen coordinates with:

```bash
python3 <skill_dir>/scripts/monorepo_placement.py \
  --group <group> --domain <domain> --lifecycle <lifecycle> --plugin <plugin> --json
```

Its `scaffold_path` is the `skills/` directory to pass to `init_skill.py --path` in
`Step 5 — Implement`.

For a **brand-new plugin** (no `plugin.json` yet), add `--plugin-json` to that
`init_skill.py` call: it writes a bare `<plugin>/.claude-plugin/plugin.json`
(name derived from the plugin dir; placeholder `description`/`author.name`/
`author.email` for you to fill; no `[<domain>]`/`<group> -` prefixes — the
pre-commit stamp hook adds those). The placeholders deliberately FAIL the
mandatory `author-name` and `author-email` checks, so fill in a real full name
and a real `@proofpoint.com` address before you commit.
It never clobbers an existing manifest, so it is safe to pass when adding a skill
to an existing plugin too. Omit it only when the plugin already has a `plugin.json`.
