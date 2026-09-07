# Section Fragment Agent Invariants

Rules for editing fragments under `sections/`.

This file owns shared fragment mechanics only. Section-local `AGENTS.md` and
`README.md` files route local roles; update them only when their manifest
membership or local contract changes.

## One fragment per manifest pair

- Maintain exactly one `sections/<section>/<track>.md` for each `(section,
  track)` pair declared in `sheaf/manifest.yaml`. A missing fragment fails
  `compose_manuscript.py --strict`.
- Do not add fragment files that no section in the manifest references.

## Fragment content

- Write only the prose for the one track. Do not add a `## Title` heading;
  compose adds it from `sheaf/tracks.yaml`. Add a leading `#` only when the
  fragment must supply its own heading.
- Abstract fragments are plain prose: no headings, no inline formulas. They
  compose into one paragraph.
- Paraphrase; never paste long copied source passages.

## Claim ceiling and acronyms

Make no empirical, clinical, neural, ontological, awakening, practice-efficacy,
or physical qFEP claims. Define every acronym at first use.

## Figures and cross-references

- Embed figures as `![short](../output/figures/<id>.png){#fig:<id>}`; the
  canonical caption replaces the short one at compose time.
- Use `@fig:`, `@sec:`, `@eq:` cross-references. Never write a hardcoded
  "Figure 3".
- Respect figure placement: QRF lead figures in the main sections before the
  compact quantum summary; technical-quantum and governance figures in the
  supplement only.

## _lead.md

Keep `_lead.md` a short signpost for the section. Recompose after any change.

## Recompose and no machine paths

After editing, run `uv run python scripts/compose_manuscript.py --strict`.
Use repository-relative paths only; no absolute home-directory paths.
