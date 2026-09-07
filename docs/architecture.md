# Project Architecture: How the Pieces Connect

How `docs/manuscript/`, `src/`, `scripts/`, `tests/`, and the generated artifacts fit
together, and the exact recipe for extending each. This is the map a maintainer
needs before adding a figure, a surrogate, or a claim. For the concepts, read
[the QRF introduction](qrf-introduction.md) first.

## The chain at a glance

`scripts/run_full_chain.py` runs thin orchestrators in order; all computation
lives in `src/`, all outputs land under `output/`.

```
src/formalism/   --(generate_formalisms.py)-->      output/data/*.json   (equation registry, claim ledgers, contract registry)
src/simulation/  --(simulate_boundary_agents.py,    output/data/*.json   (QRF audits, pymdp, bmr, criticality, compassion, quantum)
                    run_bmr_sweep.py, generate_*_surrogates.py,
                    generate_statistics.py)
src/visualizations/ --(generate_figures.py)-->      output/figures/*.png + output/data/figure_source_map.json + figure audits
docs/manuscript/sections/ --(compose_manuscript.py)-->   docs/manuscript/0X_*.md   (composed) + manuscript audits
src/gates/       --(validate_outputs.py)-->          PASS/FAIL over every artifact and audit
```

Determinism is a contract: fixed seeds, no wall-clock, byte-stable JSON. Tests in
`tests/` re-run this chain against real artifacts with **no mocks**.

## Layer responsibilities

| Layer | Holds | Never holds |
| --- | --- | --- |
| `src/formalism/` | equation registry, data models, claim/source/scholarship ledgers | rendering, orchestration |
| `src/simulation/` | deterministic + seeded surrogates (QRF, pymdp, BMR, criticality, compassion, quantum, and the implemented finite-quantum extension engines — see [method-inventory.md](method-inventory.md)) | I/O beyond returning data |
| `src/visualizations/` | one `_<id>()` renderer per figure, style contracts, caption/integrity audits | business logic (read JSON, draw) |
| `src/gates/` | output, manuscript, source, and documentation validators | computation that produces claims |
| `scripts/` | thin orchestrators only (import from `src/`, write `output/`) | algorithms |
| `docs/manuscript/sections/` | per-track prose fragments | hand-edited composed `0X_*.md` (those are generated) |

The `pymdp` simulation follows that same module boundary. `qrf_env.py` supplies
the finite QRF deployments and boundary trajectory, `pymdp_profiles.py` builds
profile-specific `A/B/C/D` arrays and deterministic policy traces, `stochastic.py`
samples seeded ensembles from those same normalized models, and
`src/gates/validation.py` recomputes the saved trace and runtime diagnostics.
The modules share artifacts and schemas, not hidden cross-module state.

## The manuscript sheaf

The top-level `docs/manuscript/0X_*.md` files are **generated** by
`scripts/compose_manuscript.py` from per-track fragments under
`docs/manuscript/sections/<section>/<track>.md`. Edit fragments, never the composed
files. The manifest (`docs/manuscript/sheaf/manifest.yaml`) lists which tracks each
section uses; `docs/manuscript/sheaf/tracks.yaml` holds each track's heading and
anchor. For the abstract, fragments are joined into one paragraph; for other
sections, each track gets a `## heading {#anchor}`.

Figure references in fragments use
`![short caption](../output/figures/<id>.png){#fig:<id> width=NN%}`; at compose
time the short caption is replaced by the source-of-truth caption from
`figures.yaml`. Cross-reference with `@fig:<id>`, `@sec:<anchor>`, `@eq:<n>` —
never a hardcoded "Figure 3" (the reference audit rejects hardcoded numbers).

## Recipe: add a figure

Every figure is bound to a real artifact and fail-closed audited. Touch these
sites as a set (a count mismatch fails the suite):

1. **Renderer** — add `_<id>(project_root, style, data) -> Path` in
   `src/visualizations/figures.py`; read JSON, draw with matplotlib, return
   `_save_return(fig, _fig_path(project_root, style, "<id>"), style["dpi"])`.
2. **Register** — add `"<id>": _<id>(...)` to `generate_all_figures()` and an
   entry to `_source_artifacts_for()` (>= 1 real `output/data/*.json` path).
3. **Render contract** — add `<id>` to `FIGURE_RENDER_CONTRACTS` in
   `src/visualizations/style.py` (roles must be keys of `SEMANTIC_COLORS`;
   `panel_count >= 1`; `legend_count + colorbar_count >= 1`; `min_font_pt >= 12`).
4. **Caption metadata** — add `<id>` to `figures.yaml` with `caption` (>= 120
   chars, including an interpretive-boundary term and an encoding term such as
   `legend`/`color`/`bar`/`line`/`matrix`), `visual_encoding`, and `alt_text`
   (>= 80 chars with a non-color encoding term and a unit term).
5. **Expected set** — add the PNG path to `EXPECTED_FIGURES` in
   `src/gates/validation.py`, and bump the `figure_count` assertions in
   `tests/test_practice_and_chain.py`.
6. **Manifest** — add `id`/`path`/`kind: figure` to `artifact_manifest.yaml`.
7. **Place it** — embed it once in a `docs/manuscript/sections/**` fragment so its
   `@fig:` reference resolves; then `compose_manuscript.py`.
8. Run `generate_figures.py`, `compose_manuscript.py --strict`,
   `validate_outputs.py`, and `pytest tests/`.

The fail-closed audits that gate a figure: `visual_caption_audit`,
`visual_accessibility_audit`, `visual_style_audit`, `figure_legibility_audit`,
`figure_integrity_audit`, `rendered_figure_caption_audit`, and the
manuscript reference/placement/reuse audits. See
[visualization contract](visualization-contract.md).

## Recipe: add a claim

A reader-facing claim must declare its ceiling. Add a row to the claim ledger
(`src/formalism/claim_context.py`) with reader claim, source role, artifact,
validation gate, prohibited inference, and future evidence required; bind it to
the manuscript section and (optionally) a figure. The
[validation contract](validation-contract.md) lists the gates that then check it,
and [surrogate methodology](surrogate-methodology.md) explains why measured
verdicts and negative controls are mandatory.

## Tests

`tests/` runs the real chain: `test_formalism.py` (registry, claims,
scholarship, governance), `test_simulation.py` (QRF/pymdp/BMR/criticality/
quantum surrogates with their negative controls), and
`test_practice_and_chain.py` (full chain, figure source map, manuscript
prose/visual contracts, documentation contract). No mocks; use `pytest-httpserver`
for HTTP and real temp files for I/O. Run a single test with
`pytest tests/test_simulation.py::<name> -v`.
