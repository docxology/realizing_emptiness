# AGENTS: Abstract fragments

- Edit the per-track `*.md` fragments here; never edit the composed `docs/manuscript/00_abstract.md`.
- Each fragment maps to a `(section=abstract, track)` row in `docs/manuscript/sheaf/manifest.yaml`;
  the filename is the track id (`paper_source`, `qfep`, `qrf`, `bmr`, `pymdp`, `limitations`).
- Hold the strict claim ceiling: no empirical, clinical, neural, ontological, awakening, or
  practice-efficacy claims; keep finite-surrogate language.
- Expand each acronym (qFEP, QRF, BMR) at first use within the composed section.
- Figure embeds (if any) use the canonical-caption mechanism (`{#fig:...}` + source-map caption audit).
- Recompose with `scripts/compose_manuscript.py --strict`.
- See `../README.md` for fragment roles and `../../sheaf/` for the full track/manifest contract.
