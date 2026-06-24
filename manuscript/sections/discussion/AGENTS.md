# AGENTS: Discussion fragments

- Edit the per-track `*.md` fragments here; never edit the composed `manuscript/04_discussion.md`.
- Each fragment maps to a `(section=discussion, track)` row in `manuscript/sheaf/manifest.yaml`;
  the filename is the track id.
- Subsection headings and anchors come from `manuscript/sheaf/tracks.yaml` (`section_titles`,
  `section_anchors`); do not hardcode them in the fragment body.
- Hold the strict claim ceiling: no empirical, clinical, neural, ontological, awakening, or
  practice-efficacy claims; interpretation stays inside the declared evidence ceilings.
- Expand each acronym (QRF, BMR, qFEP) at first use within the composed section.
- Figure embeds use the canonical-caption mechanism (`{#fig:...}` + source-map caption audit).
- Recompose with `scripts/compose_manuscript.py --strict`.
- See `../README.md` for fragment roles and `../../sheaf/` for the full track/manifest contract.
