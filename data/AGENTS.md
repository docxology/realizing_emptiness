# data/ - agent conventions

- Committed input data only, kept small and text. Provenance and citation
  context, never generated artifacts. Generated outputs belong in `output/data/`
  (disposable); do not write them here.
- Do not commit large binaries, the source PDF itself, or any secret. The source
  PDF is referenced by pinned hash in `sources/source_manifest.yaml`, not stored.
- Every committed manifest must validate against its schema in `../schemas/` and
  is checked by `validate_outputs`. Keep `schema` version strings in sync with the
  schema `const`.
- Use repo-relative or external references; do not embed machine-specific
  absolute paths in new content. (The existing `local_pdf` entry is a known
  per-machine pointer; the hash is the authority.)
- Claim ceiling holds here too: provenance/citation only, no empirical, clinical,
  neural, ontological, awakening, practice-efficacy, or physical-qFEP claims.
