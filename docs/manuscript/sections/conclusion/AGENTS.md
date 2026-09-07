# AGENTS: Conclusion fragments

- Edit the per-track `*.md` fragment here; never edit the composed `docs/manuscript/05_conclusion.md`.
- Each fragment maps to a `(section=conclusion, track)` row in
  `docs/manuscript/sheaf/manifest.yaml`; filenames are the track ids
  (`paper_source`, `qfep`, `evidence_ceiling`, `limitations`).
- Subsection heading and anchor come from `docs/manuscript/sheaf/tracks.yaml` (`section_titles`,
  `section_anchors`); do not hardcode them in the fragment body.
- Hold the strict claim ceiling: no empirical, clinical, neural, ontological, awakening, or
  practice-efficacy claims; keep finite-surrogate language.
- Expand each acronym (QRF, BMR) at first use within the composed section.
- Figure references use the canonical-caption mechanism (`{#fig:...}` + source-map caption audit).
- Recompose with `scripts/compose_manuscript.py --strict`.
- See `../README.md` for the fragment role and `../../sheaf/` for the full track/manifest contract.
