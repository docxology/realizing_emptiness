# AGENTS.md - src/visualizations

Deterministic figures and visual-governance audits. Read the root
[`AGENTS.md`](../../AGENTS.md) Source Contract and root [`DESIGN.md`](../../DESIGN.md)
first.

## Adding a figure (touch every call site)

1. `figures.py`: write a `_renderer(project_root, style, <artifact>) -> Path`,
   register it in the `produced` dict inside `generate_all_figures`, and add its
   source artifacts to `_source_artifacts_for`.
2. `style.py`: add a `FIGURE_RENDER_CONTRACTS` entry (roles drawn from
   `SEMANTIC_COLORS`, `panel_count >= 1`, at least one of legend/colorbar,
   `min_font_pt` at or above the shared readable floor). If the semantic role
   or visual pattern is new, update root `DESIGN.md` in the same change.
3. `figures.yaml`: add `filename`, `caption`, `visual_encoding`, `alt_text`.
   Caption must be >=120 chars and contain a boundary term (`not empirical`,
   `surrogate`, `proxy`, `source`, `claim`, `boundary`, `finite`) and an encoding
   term (`legend`, `color`, `panel`, ...).
4. `gates/validation.py`: add the PNG to `EXPECTED_FIGURES`.
5. Update the three `figure_count` assertions in
   `../tests/test_practice_and_chain.py` (source map, integrity, dashboard) — all
   must match `generate_all_figures` / `EXPECTED_FIGURES`.
6. `artifact_manifest.yaml`: register the figure path; add the supplement/main
   embed under the placement audit.

## Do NOT

- Do NOT render a figure from anything other than a JSON artifact in
  `output/data` / `output/reports`; figures must bind to source artifacts that
  get hashed by `integrity.py`.
- Do NOT use a semantic role absent from `SEMANTIC_COLORS`, or skip the
  legend/colorbar (style audit fails closed).
- Do NOT use tiny label text. The source-map contract normalizes every figure to
  the shared readable minimum, and the legibility audit fails below that floor.
- Do NOT write absolute `/Users/` paths into captions, alt text, or the dashboard.
