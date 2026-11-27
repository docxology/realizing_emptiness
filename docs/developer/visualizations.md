# src/visualizations

Deterministic figure generation plus the visual-governance audits. Every figure
binds to the JSON artifact(s) it was rendered from, carries a semantic-role
contract, and is hashed for integrity. Figures are software diagnostics, never
empirical evidence.

## Modules

| File | Key API | Role |
| --- | --- | --- |
| `figures.py` | `generate_all_figures`, `_source_artifacts_for`, per-figure `_*` renderers | Renders the figure set registered by `generate_all_figures` / `EXPECTED_FIGURES` from `output/data` artifacts, writes `figure_source_map.json`, and fans out to the caption/accessibility/style/integrity/dashboard writers |
| `style.py` | `FIGURE_RENDER_CONTRACTS`, `SEMANTIC_COLORS`, `render_contract_for`, `build_visual_style_audit`, `build_figure_legibility_audit`, `write_visual_style_audits` | Per-figure role/panel/legend/colorbar/min-font contract; semantic palette, contrast, and legibility audits with a shared 12 pt readable floor |
| `captions.py` | `build_visual_caption_audit`, `build_visual_accessibility_audit` | Caption (>=120 chars, boundary + encoding terms), legend/colorbar, alt-text, source-alternative, non-color-encoding, and units/axis audits |
| `integrity.py` | `build_figure_integrity_audit`, `compare_figure_integrity`, `file_sha256` | SHA256, dimensions, nonblank checks for each figure plus source-artifact hashes |
| `dashboard.py` | `build_artifact_dashboard_payload`, `render_artifact_dashboard_html`, `write_artifact_dashboard` | Static `output/dashboard/index.html` over roadmap/claim/figure/manifest/dependency status |
| `rendered_captions.py` | `expand_markdown_figure_captions`, `build_rendered_figure_caption_audit` | Syncs and audits the captions readers see in the composed manuscript |

## Pipeline fit

`scripts/generate_figures.py` calls `generate_all_figures`, which reads
`figures.yaml` (via `_load_style`) for filenames/captions/encodings/alt-text and
reads every producer artifact in `output/data/`. It writes
`output/figures/*.png`, `figure_source_map.json`, and the caption/accessibility/
style/legibility/integrity audits, then the dashboard. `gates/validation.py`
re-runs `compare_figure_integrity` and checks each audit; the composed manuscript
embeds figures (main text vs supplement) under the placement audit.
