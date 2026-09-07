# AGENTS: Methods fragments

- Edit the per-track `*.md` fragments here; never edit the composed `docs/manuscript/02_methods.md`.
- Each fragment maps to a `(section=methods, track)` row in `docs/manuscript/sheaf/manifest.yaml`;
  the filename is the track id. `_lead.md` is the pre-subsection signpost, not a track.
- Subsection headings and anchors come from `docs/manuscript/sheaf/tracks.yaml` (`section_titles`,
  `section_anchors`); do not hardcode them in the fragment body.
- Hold the strict claim ceiling: no empirical, clinical, neural, ontological, awakening, or
  practice-efficacy claims; keep finite-surrogate language.
- Expand each acronym (qFEP, QRF, BMR) at first use within the composed section.
- Figure embeds use the canonical-caption mechanism (`{#fig:...}` + source-map caption audit).
- Recompose with `scripts/compose_manuscript.py --strict`.
- See `../README.md` for fragment roles and `../../sheaf/` for the full track/manifest contract.
