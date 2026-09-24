# Cache layout, CFR pin, and version-resolution fallback

Read this when you need to know exactly where extracted/decompiled source lives on disk,
why a version resolved a particular way, or why the CFR decompiler behaves as it does.

## Cache layout

```
~/.cache/mvn-source-explorer/
├── tools/
│   └── cfr-0.152.jar                  # downloaded once, sha256-verified before every use
└── <group-path>/<artifact>/<version>/
    ├── sources/...                    # full extraction of the -sources.jar, mirrors its tree
    └── decompiled/...                 # CFR output, one subtree per class ever requested
```

- `sources/` is populated in full (the whole jar) the first time `get` is called for that GAV, regardless of which class was asked for -- sources jars are small and this makes every later class lookup for that dependency free.
- `decompiled/` only ever contains the specific classes that were explicitly requested via `get ... --class`, never the whole jar -- decompiling an entire large jar eagerly would be slow and mostly wasted.
- The cache key is the GAV only (no jar hash/mtime check). If a `SNAPSHOT`-style jar changes contents without a version bump, or a class looks stale after the jar was updated, delete the specific `~/.cache/mvn-source-explorer/<group>/<artifact>/<version>/` directory to force re-extraction.

## CFR decompiler pin

- Version: `0.152`
- Source: `https://repo1.maven.org/maven2/org/benf/cfr/0.152/cfr-0.152.jar`
- Pinned sha256: `f686e8f3ded377d7bc87d216a90e9e9512df4156e75b06c655a16648ae8765b2`
- The script recomputes this hash against the cached jar on every use (not just at download time) and re-downloads if it doesn't match -- a corrupted or tampered cache file never silently gets executed.
- Invocation: `java -jar cfr-0.152.jar <regularJarPath> --jarfilter '^<escaped-FQCN>(\$.*)?$' --outputdir <decompiled-cache-dir>`. `--jarfilter` is a regex CFR uses to select which classes _inside_ the jar it processes -- scoping it to the target class (plus its inner/anonymous classes via the `\$.*` alternative) keeps CFR from processing the rest of the jar.
- Known limitation: CFR is run without the dependency's transitive classpath, so fields/params typed as classes from _other_ jars may print as raw or partially-erased signatures. The target class's own method bodies, control flow, and string/constant literals decompile accurately regardless -- that's what matters for tracing behavior.
- Possible future improvement (not implemented -- would need `mvn dependency:build-classpath` to assemble the full transitive classpath and pass it via CFR's `--extraclasspath`): sharper cross-class type resolution in decompiled output. Skipped for now; the target class's own logic is already accurate without it.

## Maven version-resolution fallback

`list`/`resolve` first parse the pom.xml chain directly (the current module's pom + every `<parent>` above it, via `<relativePath>`, default `../pom.xml`). This resolves:

- Direct `<version>` on a `<dependency>`
- `${property}` placeholders defined in any `<properties>` block in the chain
- Versions pinned via a plain `<dependencyManagement>` entry in the chain

It does **not** resolve versions that only come from an imported BOM (`<dependencyManagement><dependencies><dependency><type>pom</type><scope>import</scope>`), since that would require fetching and parsing another remote POM. When any dependency's version is still unresolved after the local pass, the tool makes exactly one fallback call:

```
mvn -q -B dependency:list -Dsort=false -DoutputFile=<tempfile>
```

run from the directory of the nearest pom.xml (not `-q`'d to stdout -- `-DoutputFile` is used because `dependency:list`'s output is an `[INFO]` log line that `-q` would otherwise swallow). Each output line is `groupId:artifactId:packaging[:classifier]:version:scope[ -- module ...]`; the tool takes fields `[0]`, `[1]`, and the second-to-last field as groupId/artifactId/version. This single call resolves every still-unresolved dependency at once, not one `mvn` invocation per artifact -- expect roughly the cost of one `mvn` startup + dependency resolution (typically a few seconds once the local repo is warm).

If `mvn` itself isn't on PATH, or the call fails or times out (180s), affected dependencies simply keep `version: null` rather than erroring the whole `list` call -- everything else still resolves normally.

## Sources-jar download fallback

Before decompiling with CFR, `get` tries once to fetch a sources jar from the configured
Maven repositories:

```
mvn -q -B dependency:resolve-sources -DincludeArtifact=<groupId>:<artifactId>:<version> \
        dependency:resolve -Dclassifier=javadoc -DincludeArtifacts=<groupId>:<artifactId>:<version>
```

run from `--project-dir`, with a 180s timeout. `dependency:resolve-sources` pulls the
`-sources.jar` into `~/.m2/repository`; the extra `dependency:resolve -Dclassifier=javadoc`
call also fetches the javadoc jar for completeness, though nothing in this skill reads it
today. After the call, the tool just re-checks whether the sources jar now exists on disk
-- it doesn't parse `mvn`'s output, so a partial success (e.g. javadoc resolved but sources
didn't, because the artifact was never published with one) is still detected correctly.

If `mvn` isn't on PATH, or the call fails, times out, or the artifact simply has no sources
jar published, `hasSources` stays false and `get` falls through to the CFR decompile path
same as before -- this is a pure best-effort addition, never a hard dependency.

## Citation fields

Each dependency in `list`'s output carries up to four location fields, because a version and the fact of depending on something can live in different files in a multi-module build:

- `declaredIn` / `declaredAtLine` -- the `<dependency>` block that actually pulls the artifact into _this_ module's classpath (found via a best-effort text scan for a `<dependency>` block containing matching `<groupId>`/`<artifactId>` text; not namespace-aware, so it can mis-cite if the exact same groupId+artifactId pair appears more than once in one file, e.g. across Maven profiles).
- `versionManagedIn` / `versionManagedAtLine` -- present only when the version came from a `<dependencyManagement>` entry rather than the dependency's own `<version>` tag; points at that separate pin (often the parent/root pom).
