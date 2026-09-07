# Manuscript Section Fragments

The hand-edited source of the manuscript. Each subfolder is one manuscript
section; each Markdown file inside it is one per-track fragment. The top-level
`docs/manuscript/0X_*.md` files are composed from these fragments by
`scripts/compose_manuscript.py` and must never be hand-edited.

## Layout

```
sections/
  <section>/
    _lead.md            (optional section signpost)
    <track>.md          (one fragment per track in the manifest)
```

`<section>` matches a section `id` in `sheaf/manifest.yaml`; `<track>.md`
matches a track `id` listed for that section. There must be exactly one
fragment per `(section, track)` pair in the manifest. Current sections:
`abstract`, `introduction`, `methods`, `results`, `discussion`, `conclusion`,
`supplement`.

## Fragment convention

- A fragment holds only the prose for its one track. Compose prepends the
  per-track `## Title {#anchor}` from `sheaf/tracks.yaml` automatically, so a
  fragment normally does not start with its own heading. If a fragment does
  start with `#`, it supplies its own heading and compose skips the per-track
  title.
- Abstract fragments are plain prose with no headings and no inline formulas;
  compose joins them into a single paragraph.
- Fragments are paraphrased project prose, never long copied source passages
  (see `sheaf/fragments.yaml`).

## _lead.md is the section signpost

A section's `_lead.md`, when present, renders between the section title and its
first subsection. It signposts the section's structure. The abstract has no
lead. Currently `methods/` and `results/` carry a `_lead.md`.

## Editing and recomposing

Edit the fragment (or `_lead.md`), then from the project root run:

```
uv run python scripts/compose_manuscript.py --strict
```

See `AGENTS.md` in this folder for the invariants.
