# Sheaf Configuration

The sheaf layer defines how per-track fragments compose into the top-level
manuscript files. `scripts/compose_manuscript.py` reads these two files.

## manifest.yaml: sections to tracks

`manifest.yaml` (schema `realizing_emptiness.sheaf_manifest.v1`) lists each
section in document order. Every section entry carries:

- `id` — the section folder name under `sections/`.
- `output` — the generated top-level file (for example `02_methods.md`).
- `title` — the `# Section {#sec:<id>}` heading.
- `tracks` — the ordered list of tracks to compose for that section. Compose
  walks tracks in this order and expects one `sections/<id>/<track>.md`
  fragment per track.

## tracks.yaml: labels, titles, anchors

`tracks.yaml` (schema `realizing_emptiness.sheaf_tracks.v1`) holds:

- `tracks` — every track `id` with its human `label` and `order`. The label is
  the fallback subsection heading when no per-section title is given.
- `section_titles` — `section_id -> track_id -> title`. This title becomes the
  `## Title {#anchor}` rendered above the fragment.
- `section_anchors` — `section_id -> track_id -> anchor`. When absent, compose
  falls back to `sec:<section>-<track-with-dashes>`.

A fragment that begins with `#` supplies its own heading; compose then skips
the per-track title. The abstract never gets per-track headings: its fragments
are joined into a single plain-prose paragraph.

## Add a track

1. Add the track `id`, `label`, and `order` under `tracks` in `tracks.yaml`.
2. Add the track `id` to the `tracks` list of each section in `manifest.yaml`
   that should render it.
3. For each of those sections, add a `section_titles` entry (>= four words,
   non-generic) and a `section_anchors` entry.
4. Create the fragment file `sections/<section>/<track>.md`.
5. Recompose: `uv run python scripts/compose_manuscript.py --strict`.

## Add a section

1. Add a section entry to `manifest.yaml` with `id`, `output`, `title`, and
   `tracks`.
2. Create the `sections/<id>/` folder with one fragment per listed track and an
   optional `_lead.md` signpost.
3. Add `section_titles` and `section_anchors` for every track in the new
   section in `tracks.yaml`.
4. Recompose with `--strict`.

`fragments.yaml` records the fragment-root and the paraphrase-only policy; it is
informational and not consumed by compose.

See `AGENTS.md` in this folder for the editing invariants.
