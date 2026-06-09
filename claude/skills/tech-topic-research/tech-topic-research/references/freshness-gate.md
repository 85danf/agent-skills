# AS_OF freshness gate

The AS_OF freshness gate enforces date-tagging on time-sensitive citations and downgrades stale sources during Phase 3→4 transition.

## When the gate fires

For time-sensitive topics — software versions, market data, regulatory state, security advisories, anything where "current" matters — every cited source must carry a publication date and the document must record an `AS_OF` value (the date you anchored in Phase 1 Step 1).

Topics that are _not_ time-sensitive (foundational concepts, historical events, mathematical results) skip the freshness gate but still record publication dates.

## Rules (apply before drafting Phase 4)

- Tag every source with `as_of: YYYY-MM` (or `YYYY` when month is unknown).
- Sources older than 12 months: downgrade by one tier per [`source-quality.md`](source-quality.md).
- Sources older than 36 months: do not cite for "current state" claims; they are background only.
- Note `AS_OF: <date>` near the top of any saved study-guide document.

## When to load this file

Phase 3 → Phase 4 transition: load when applying source-tier downgrades and writing the AS_OF date in the study-guide frontmatter.
