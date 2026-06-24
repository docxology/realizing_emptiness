# AGENTS: Supplement fragments

- Edit the per-track `*.md` fragments here; never edit the composed `manuscript/06_supplement.md`.
- Each fragment maps to a `(section=supplement, track)` row in `manuscript/sheaf/manifest.yaml`;
  the filename is the track id.
- Subsection heading/anchor for the qfep track come from `manuscript/sheaf/tracks.yaml`; other
  fragments here carry their own in-body headings - keep them stable.
- Hold the strict claim ceiling: command logs, render gates, source maps, and reproducibility
  counts are audit material only, not argumentative evidence; no empirical, clinical, neural,
  ontological, awakening, or practice-efficacy claims.
- Expand each acronym (qFEP, QRF, BMR) at first use within the composed section.
- Figure embeds use the canonical-caption mechanism (`{#fig:...}` + source-map caption audit);
  validation tokens such as `{{VALIDATION_PASS_COUNT}}` are hydrated, not hand-edited.
- Recompose with `scripts/compose_manuscript.py --strict`.
- See `../README.md` for fragment roles and `../../sheaf/` for the full track/manifest contract.
