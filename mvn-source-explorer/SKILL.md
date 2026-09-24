---
name: mvn-source-explorer
description: >
  Resolves a Maven dependency coordinate, artifact name, or class name to real, readable
  Java source pulled from the local ~/.m2/repository -- extracting its -sources.jar when
  one exists, or decompiling just the needed class with CFR when it doesn't -- so a library's
  actual internals can be traced instead of guessed at. Use when asked to explain, trace, or
  reverse-engineer what a Java/Maven dependency does internally (e.g. "what HTTP call does this
  SDK make", "reconstruct the curl this client sends", "how does this library build its
  request"), when following an import statement or a pom.xml dependency into library code, or
  when a question needs a third-party/internal Java library's real implementation rather than
  its public API surface. Works on any Maven project, not just one repo.
metadata:
  author: Dan Feldman
  version: "1.0"
---

# mvn-source-explorer

Resolve a Maven dependency to the real Java source behind it, then read and trace it like any other file in the repo.

**Never state what a library does without having actually read the relevant class through this skill (or already-open code) -- no inferring behavior from method/class names.** When source came from `get`'s decompile path, always say so and note the accuracy caveat (types from outside the jar may show as raw/erased signatures) -- never present decompiled output as if it were the original source.

## When to use this skill

- Tracing what a library actually does internally (call chains, HTTP requests it builds, retry/caching behavior) instead of inferring from its public method names
- Following an `import` in project code back into the dependency that defines it
- Answering "reconstruct the exact request/curl this client sends" or similar reverse-engineering questions about a dependency
- Finding which declared dependency a class name belongs to
- Any of the above for a dependency that lacks a `-sources.jar` (falls back to decompiling just that class)

Not for: Gradle/sbt-resolved dependencies (Maven-only), editing library code, or dependencies that were never downloaded to `~/.m2/repository` (run a build first).

## Prerequisites

1. `python3` (stdlib only -- no pip installs).
2. `mvn` on PATH, optional -- when a dependency has no sources jar locally, `get` first tries `mvn dependency:resolve-sources`/`resolve -Dclassifier=javadoc` to fetch one before falling back to decompiling. Skipped silently if `mvn` isn't on PATH or the download fails.
3. `java` on PATH, but only needed the first time a dependency still lacking a sources jar (after the download attempt above) is decompiled. Any Java/Maven project already requires this.
4. Network access, but only for the CFR decompiler jar download (~2MB, from Maven Central, sha256-pinned, one-time) and the optional `mvn`-based sources download above. Never required for a dependency that already has a sources jar locally.
5. No config file, no credentials, no API keys.

## Configuration

None. No config file, no credentials, no API keys -- `--project-dir` (default: current directory) is the only thing that points the tool at a specific Maven project.

## Pre-flight checks

None needed as a separate step: `list` or `resolve` against `--project-dir` immediately surfaces a clear error if it isn't inside a Maven project (see Error handling below), and the decompile fallback checks for `java` on PATH itself before running.

## How it works

One script, four subcommands, always run from (or pointed at, via `--project-dir`) a directory inside the Maven project you're investigating:

```bash
python3 <skill_dir>/scripts/source_explorer.py list [--project-dir DIR]
python3 <skill_dir>/scripts/source_explorer.py resolve <coordinate> [--project-dir DIR]
python3 <skill_dir>/scripts/source_explorer.py get <coordinate> [--class FQCN] [--project-dir DIR]
python3 <skill_dir>/scripts/source_explorer.py find-class <name> [--project-dir DIR]
```

`<coordinate>` is `group:artifact:version` (works standalone, no pom.xml needed), `group:artifact`, or a bare `artifact` name (both resolved against the current project's pom.xml chain). Every subcommand prints one JSON object to stdout; exit code 0 on success, 1 on error (the JSON still has an `"error"` key -- always check the exit code, don't just grep for "error").

Extracted/decompiled source is written to a persistent cache at `~/.cache/mvn-source-explorer/<group-path>/<artifact>/<version>/{sources,decompiled}/...`, keyed by GAV so repeat lookups (even from a different project on the same machine) are instant. See [references/CACHE_AND_TOOLS.md](references/CACHE_AND_TOOLS.md) for the exact layout, the CFR pin, and the `mvn`-based version-resolution fallback.

## Workflow

1. **Identify the coordinate.** From a pom.xml dependency, an import statement's package prefix, or a class name you already know.
2. **`resolve`** it to confirm the GAV and see whether a sources jar exists locally (`hasSources`). If you only have a class name and don't know which dependency it's in, use `find-class` first.
3. **`get`** the source: sources-jar path if `hasSources` is true. If not, `get` first tries an automatic `mvn dependency:resolve-sources` download -- pass `--class <FQCN>` too so it has a class to decompile if that download fails. Read the `classFile` path it prints with your normal Read tool.
4. **Trace across classes** by repeating step 3 for each class the chain leads through (same dependency or a different one) -- this is manual reasoning over real code, not a script step.
5. **Ground every claim in what was actually read.** If a question needs a class you haven't fetched yet, fetch it before answering; never infer library behavior from naming alone.

## Operations

### List declared dependencies

```bash
python3 <skill_dir>/scripts/source_explorer.py list --project-dir /path/to/module
```

Walks the pom.xml chain (the module's own pom + every `<parent>` above it) and returns every declared dependency with its resolved version, the file:line where it's declared, and -- when the version comes from `<dependencyManagement>` rather than the dependency's own `<version>` -- `versionManagedIn`/`versionManagedAtLine` pointing at that separate pin. Use this when you only know an artifact name, not its full coordinate.

### Resolve a coordinate

```bash
python3 <skill_dir>/scripts/source_explorer.py resolve some-sdk --project-dir /path/to/module
python3 <skill_dir>/scripts/source_explorer.py resolve com.example:some-sdk:1.2.3
```

Returns `jarPath`, `sourcesJarPath`, `hasJar`, `hasSources` -- no extraction yet. A full `group:artifact:version` needs no `--project-dir`/pom.xml at all.

### Get the source for a class

```bash
python3 <skill_dir>/scripts/source_explorer.py get com.example:some-sdk:1.2.3 \
  --class com.example.client.SomeClientImpl
```

If a sources jar exists, extracts the whole jar to the cache (once) and returns `classFile` for the requested class. If not, `get` first tries `mvn dependency:resolve-sources -DincludeArtifact=<gav> dependency:resolve -Dclassifier=javadoc -DincludeArtifacts=<gav>` to download one -- if that succeeds, it's used exactly like an already-present sources jar (no caveat needed, it's real source). Only if that download also fails (or `mvn` isn't on PATH) does it require `--class` and decompile just that class (plus its inner/anonymous classes) with CFR into the cache, returning the same shape plus a `note` about decompiled-code limitations (types from classes outside the jar may show raw/erased signatures; the class's own logic and control flow are accurate). Omit `--class` against a sources-jar dependency to just get `cacheDir` and browse/grep it directly.

### Find which dependency has a class

```bash
python3 <skill_dir>/scripts/source_explorer.py find-class SomeClientImpl --project-dir /path/to/module
```

Checks only the project's _declared_ dependencies (via jar file-listing, no extraction) -- not all of `~/.m2`. Returns every matching `{gav, entry, hasSources}`; feed the `gav` into `get`.

## Important rules

1. `list`/`find-class` only see dependencies that are actually declared in the visible pom.xml chain and present under `~/.m2/repository` -- a dependency that was never built/resolved on this machine won't show up; that's a "run a build first" situation, not a bug.
2. The CFR download only ever happens once per machine and is checksum-verified before use; if you see the one-time download message, that's expected on a fresh cache, not an error.
3. This skill is generic -- it never assumes any specific project's module layout. `--project-dir` (default: cwd) is how it points at whichever Maven project you're in.

## Error handling

| Error                                                  | Cause                                                              | Fix                                                                                       |
| ------------------------------------------------------ | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------- |
| `No pom.xml found at or above <dir>`                   | `--project-dir` isn't inside a Maven project                       | Point `--project-dir` at (or run from within) the module you're investigating             |
| `'<x>' not found among dependencies declared...`       | Bare artifact/class name doesn't match any declared dependency     | Run `list` to see what's actually declared, or use the full `group:artifact:version` form |
| `'<x>' is ambiguous, found in multiple groups`         | Same artifactId under two different groupIds                       | Qualify with `group:artifact`                                                             |
| `Neither the jar nor a sources jar is present locally` | Dependency (jar itself) was never downloaded to `~/.m2/repository` | Run a build (e.g. `mvn dependency:resolve`) in that project first                         |
| `No sources jar available... Pass --class`             | `get` called without `--class` on a no-sources dependency          | Re-run with `--class <FullyQualifiedClassName>`                                           |
| Downloaded CFR jar failed checksum verification        | Corrupted download or a tampered/mirrored artifact                 | Delete `~/.cache/mvn-source-explorer/tools/` and retry; investigate if it recurs          |

## Troubleshooting

Version-resolution edge cases, decompiled-output limitations, and cache-staleness fixes are all covered in [references/CACHE_AND_TOOLS.md](references/CACHE_AND_TOOLS.md) (Maven version-resolution fallback, CFR decompiler pin, and cache layout sections) rather than repeated here.
