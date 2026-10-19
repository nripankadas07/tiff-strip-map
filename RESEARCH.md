# Research —19 October2026

User: Image ingestion maintainers investigating a small grayscale TIFF.

Pain: Offset/count arrays and inline fields can conceal metadata/strip collisions before pixel decoding.

MVP: Map classic TIFF IFD metadata and grayscale strip ownership, including aliases and out-of-file evidence.

Acceptance: Both endians, inline/out-of-line arrays, partial strips, exact aliases, metadata collisions, IFD cycles, bad counts/bounds and explicit unsupported format refusal.

Demand is inferred from workflows and adjacent discussions, not verified requests. Discovery path: descriptive GitHub topics, runnable invented examples and chronological project index. No unsolicited outreach or artificial activity.

## Alternatives

Live GitHub search sorted Most stars: `TIFF image`. Highest-star relevant comparable found: **lovell/sharp**. This is bounded search/reference-follow coverage, not an exhaustive global ranking. Broad/unrelated keyword matches were excluded.

| Repository | Stars observed | Last push UTC | API license |
| --- | ---: | --- | --- |
| [lovell/sharp](https://github.com/lovell/sharp) | 32775 | 2026-10-15T07:10:34Z | Apache-2.0 |
| [libvips/libvips](https://github.com/libvips/libvips) | 11744 | 2026-10-18T10:12:35Z | LGPL-2.1 |
| [cgohlke/tifffile](https://github.com/cgohlke/tifffile) | 671 | 2026-10-16T00:33:22Z | BSD-3-Clause |

Sharp and libvips are broader processing/conversion libraries. Tifffile already exposes data offsets/bytecounts and supports far more TIFF variants. Issue333 about inline ASCII offsets informed careful field storage tests; it is adjacent evidence, not verified demand or a claim that current alternatives lack this capability.

Current READMEs, selected relevant source and up to five issue/PR records were read; exact observations and source identities are in [provenance](RESEARCH_PROVENANCE.json). Our clean-install example establishes our behavior only. Established alternatives provide broader capability, docs, examples and communities. Competitor installability, time to first useful result, reliability, support response and performance were not measured. No feature-absence claim. Stars are discovery evidence, not quality/performance. Unclassified licenses are not permission to copy. No competitor code, prose, branding or fixtures are bundled.

Primary technical reference: https://www.itu.int/itudoc/itu-t/com16/tiff-fx/docs/tiff6.pdf. NASA's current FITS4 PDF fetch timed out; the official standard landing page and NASA CFITSIO primer were readable. ELF reference is explicitly a draft generic ABI; processor-specific behavior remains outside scope. No technical performance benchmark was conducted.

Portfolio distinction: Owned png-metadata-scrub edits PNG ancillary chunks. This TIFF project reads IFD/strip ownership under a different binary contract and does not edit files.

Original capability is the bounded implementation/evidence workflow, not a claim to invent the file format or standard algorithm.
