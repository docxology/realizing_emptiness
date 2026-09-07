# Sheaf Agent Invariants

Rules for editing `manifest.yaml` and `tracks.yaml`.

## Keep manifest and tracks consistent

- Every track listed in a section's `manifest.yaml` `tracks` must have a
  matching `id` in `tracks.yaml` `tracks`. Compose records an unknown-track
  issue otherwise.
- Every `(section, track)` pair in the manifest must have a fragment at
  `sections/<section>/<track>.md`. Under `--strict`, a missing fragment fails
  the compose.

## Titles and anchors

- For each non-abstract `(section, track)`, add a `section_titles` entry. Titles
  must be at least four words and must not be generic (the subsection-title
  audit rejects generic titles such as "Results" or "Validation").
- Add a `section_anchors` entry for each `(section, track)`. Anchors must be
  unique across the whole manuscript (the reference audit fails on duplicate
  anchors) and use the `sec:` prefix.
- The abstract takes no per-track titles or anchors: its fragments compose into
  one plain-prose paragraph.

## After any change

Recompose and let the audits run:

```
uv run python scripts/compose_manuscript.py --strict
```

## No machine paths

Repository-relative paths only. No absolute home-directory paths.
