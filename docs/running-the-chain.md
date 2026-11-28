# Running the Chain

`scripts/run_full_chain.py` regenerates every artifact this project ships:
equation registries and ledgers, seeded surrogate simulations, figures, the
composed manuscript, the method inventory, the equation crosswalk, the static
dashboard, the review-response hardening artifacts, and the validation report.
The analysis chain uses fixed seeds and stable JSON. Byte-for-byte figure
replay additionally requires the same Python, locked dependencies, fonts, and
rendering backend. PDF, HTML, and EPUB are produced by the separate template
render step below; the analysis chain does not regenerate them. Nothing under
`output/` is hand-edited; it is all regeneratable. For the concepts behind the
artifacts, read
[the QRF introduction](qrf-introduction.md) and
[the architecture map](architecture.md) first.

## Setup

Python 3.11-3.14 is supported; dependencies are managed with `uv`.
The default development version is 3.14. The frozen lock includes GNN at its
pinned upstream revision and Python-specific `pymdp` versions. Python 3.11 uses
PyMDP 1.0.4 and Python 3.12 through 3.14 uses PyMDP 1.0.5. See [GNN modeling](gnn-modeling.md) for provenance,
packaged resources, and model-authoring instructions.

```bash
uv sync --frozen --extra dev
```

Run all subsequent commands from the project root with `uv run`.

## Run the full chain

Run the full-chain command in [AGENTS.md](../AGENTS.md).

The numerical stages read admitted GNN specifications rather than duplicated
YAML model defaults. The chain also records the model provenance and execution
audit at `output/data/gnn_model_audit.json`; malformed specifications stop
execution before they can be treated as numerical inputs.

The runner first writes an explicitly provisional, non-passing release-manifest
placeholder. This gives claim-context producers a declared artifact path on a
fresh source tree; only the final populated manifest and gates can establish
readiness. It then runs thin orchestrators in this order; each imports computation from
`src/` and writes only into `output/` (or the composed `docs/manuscript/`):

0. `scripts/generate_gnn_models.py` admits the checked-in model declarations
   with the pinned parser and writes `output/data/gnn_model_audit.json`.
1. `scripts/generate_formalisms.py` — writes the equation registry, claim
   ledgers, source-hash check, and artifact contract registry to
   `output/data/*.json` (including `formalism_registry.json`, `equation_audit.json`).
2. `scripts/simulate_boundary_agents.py` — writes the QRF boundary audit,
   profile-specific `pymdp` comparison, generative-model audit, policy trace,
   runtime diagnostics log, and related QRF JSON. The `pymdp` runtime dependency
   check verifies the pinned package/import/agent surface only; the saved
   `A/B/C/D` arrays and trace recomputation carry the paper-specific checks.
3. `scripts/generate_quantum_surrogates.py` — writes the finite two-qubit
   quantum-information surrogate artifacts to `output/data/*.json`.
4. `scripts/generate_extended_surrogates.py` — writes the four extended
   source-fidelity surrogate audits (separation-prior emergence, internal-cut
   unmeasurability, sigma contextuality suppression, ongoing revision) to
   `output/data/*.json`.
5. `scripts/run_bmr_sweep.py` — writes the Bayesian model-reduction sweep over
   the separation prior to `output/data/bmr_sweep.json`, plus the sensitivity
   grid needed by the statistics stage.
6. `scripts/generate_statistics.py` — writes the statistical robustness audits
   (effect sizes, resampling, convergence, positive-control calibration) to
   `output/data/*.json`.
7. `scripts/generate_sheaf_tracks.py` — writes the compact sheaf-track,
   practice, criticality, compassion, and dependency artifacts to
   `output/data/*.json` and `output/reports/*.json`.
8. `scripts/generate_figures.py` — renders every figure to `output/figures/*.png`
   and writes `output/data/figure_source_map.json` plus the figure audits.
9. `scripts/compose_manuscript.py` — composes the top-level `docs/manuscript/0X_*.md`
   files from the per-track sheaf fragments and writes the manuscript audits.
10. `scripts/generate_method_inventory.py` — regenerates
    `docs/method-inventory.md` from the source tree.
11. `scripts/generate_equation_crosswalk.py` — regenerates
    `docs/equation-crosswalk.md` from `output/data/formalism_registry.json`
    so the crosswalk cannot drift from the registry.
12. `scripts/generate_dashboard.py` — refreshes the static artifact dashboard at
    `output/dashboard/index.html` from the existing source maps.
13. `scripts/generate_review_response_artifacts.py` — writes the local artifact
    release manifest, external review-response audit, figure parameter ledger,
    neutral QRF label-ablation audit, independent quantum cross-check, and BMR
    alternative-prior audit, then refreshes the dashboard with those rows.
14. `scripts/z_generate_manuscript_variables.py` — writes hydrated manuscript
    variables/copies derived from the final generated audit, sweep, dashboard,
    and review-response JSON.
15. `scripts/generate_review_response_artifacts.py` — refreshes the release
    manifest and review-response hashes after the hydrated manuscript variables
    are written.
16. `scripts/validate_outputs.py` — runs PASS/FAIL gates over every artifact and
    audit; a non-zero exit fails the chain.
17. `scripts/z_generate_manuscript_variables.py` — hydrates the completed
    validation counts, including on a source tree with no previous outputs.
18. `scripts/generate_dashboard.py` — refreshes the reader dashboard with the
    completed validation result.
19. `scripts/generate_review_response_artifacts.py` — binds the refreshed
    dashboard into the artifact hashes.
20. `scripts/validate_outputs.py` — verifies the final saved state.

The runner stops at the first non-zero exit code, so a failing stage halts the
run.

## Output layout

```
output/
  data/        Generated JSON: equation registry, claim/source ledgers, QRF and
               pymdp audits, BMR sweep, statistics, criticality/compassion,
               quantum surrogates, figure_source_map.json, and review-response
               hardening artifacts.
  figures/     Rendered figures (PNG), one per registered figure id.
  reports/     Per-audit JSON reports (e.g. criticality proxy report).
  dashboard/   Static artifact dashboard (index.html) summarizing status.
```

Generated analysis files can be recreated by the full chain. Preserve unfinished
renders and unmanaged files before regeneration. Template render receipts
(`manuscript_composition.json`, `output_statistics.json`, and
`output_statistics.txt`) are render metadata outside the scientific artifact
manifest; arbitrary extra analysis files still fail manifest coverage.

## Verify / gates

Run after the full chain (or after a targeted regeneration):

Use the canonical verification commands in [AGENTS.md](../AGENTS.md).

- `check_release_manifest.py` — read-only; fails if the committed
  `output/data/artifact_release_manifest.json` no longer matches the files on
  disk. Run it before anything regenerates outputs, because the chain and the
  tests rewrite the manifest in place.
- `pytest tests/ --cov=src --cov-fail-under=90` — re-runs the real chain against
  real artifacts (no mocks) and enforces the 90% source-coverage floor.
- `check_documentation_contract.py --check` — fails on documentation-contract
  violations: machine paths, orphaned docs, and broken links.
- `generate_method_inventory.py --check` — fails if the committed
  `method-inventory.md` has drifted from the source tree (regenerate without
  `--check` to fix).
- `generate_equation_crosswalk.py --check` — fails if `equation-crosswalk.md` has
  drifted from `output/data/formalism_registry.json`.
- `compose_manuscript.py --validate-only --strict` — validates the composed
  manuscript (citation resolution, cross-references, no hardcoded figure numbers)
  without rewriting it.
- `validate_outputs.py` — PASS/FAIL over every generated artifact and audit.

## Render and manual QA

Render a clean project checkout with [docxology/template at the pinned
revision](https://github.com/docxology/template/tree/87704feae0a4490ef7dad9c931d268e8c30273c2).
Install the template environment using its locked setup and put Pandoc,
a matching pandoc-crossref, and XeLaTeX on PATH. Run the native analysis
chain first when generating fresh research inputs. It composes the canonical
`docs/manuscript/` sources and writes the data, figures, and hydrated render
copies under `output/`.

Use a dedicated checkout in a physical directory named `realizing_emptiness` to regenerate
outputs without changing the archived copies in your primary checkout. From
that checkout, register it once and verify the resolved path:

```bash
export PROJECT_ROOT="$(pwd -P)"
export TEMPLATE_ROOT=/path/to/template
git -C "$TEMPLATE_ROOT" rev-parse HEAD
mkdir -p "$TEMPLATE_ROOT/projects/working"
ln -s "$PROJECT_ROOT" "$TEMPLATE_ROOT/projects/working/realizing_emptiness"

cd "$TEMPLATE_ROOT"
uv run --no-sync python -c 'from pathlib import Path; from infrastructure.core.project_paths import resolve_project_root; print(resolve_project_root(Path.cwd(), "working/realizing_emptiness"))'
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/realizing_emptiness
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/realizing_emptiness
```

The template revision and resolved project path should match the pin and the
dedicated checkout above. This checkout should have its own locked project
environment from the setup step so Template can run the project hydrator.
To render from the checked-in release inputs, first verify their manifest
with `scripts/check_release_manifest.py`. Then run
`uv run python scripts/z_generate_manuscript_variables.py --retained-variables`
from the project root. It refreshes `output/manuscript/` using saved values and
writes the Template figure registry from `figures.yaml`. Pass
`--skip-manuscript-hydration` to Stage 03 for that route. Stage 04 writes `output/reports/validation_report.json`
and `output/reports/rendered_provenance.json` in that checkout. The native
validator writes its own report at the same validation-report path, so retain
the native receipt before running Template.

After rendering, inspect the actual surfaces that readers see:

- `output/pdf/realizing_emptiness_combined.pdf` — use `pdftotext` or a PDF
  viewer to confirm the table of contents, section order, captions, and figure
  placement.
- `output/web/index.html` and `output/web/manuscript__06_supplement.html` —
  confirm the web ToC and anchors match the composed manuscript.
- `output/dashboard/index.html` — confirm the Visual QA block reports zero
  overlapping text layouts, title collisions, cropped labels, legend/axis
  collisions, and layout failures.
- `output/epub/` — inspect archive structure, spine order, figure resources, and
  unresolved manuscript tokens when EPUB is enabled in the manuscript config.

The renderer belongs to the sibling template repository. Its version, fonts,
Pandoc, and TeX installation must be recorded alongside a release render; they
are not pinned by this repository's Python lockfile. See the
[release validation record](release-validation.md).

## Reproducing a single result

You do not need the full chain to regenerate one downstream artifact, as long as
its inputs already exist under `output/data/`.

Regenerate only the figures:

```bash
uv run python scripts/generate_figures.py
```

Regenerate only the composed manuscript:

```bash
uv run python scripts/compose_manuscript.py
```

Figures read their data from `output/data/*.json`, and the manuscript and
crosswalk read the same generated JSON. The relevant upstream generate step must
have run first — if `output/data/` is empty or stale, run the full chain (or the
specific generate script that writes the JSON a stage consumes) before the
downstream step. The architecture map shows which script writes which JSON; see
[architecture.md](architecture.md).

## When a gate fails

- **GNN admission or `gnn_model_audit_ok` fails**: inspect the named
  specification, its source hash, declared dimensions, backend, and consumer.
  Repair the declaration or adapter and rerun the real consumer plus the
  negative control; do not replace the upstream validation with a success
  flag. Follow the [authoring workflow](gnn-modeling.md#authoring-and-validation).
- **Figure audit fails** (caption, accessibility, style, legibility, integrity,
  or rendered-caption): inspect `output/data/figure_source_map.json` and the
  failing figure under `output/figures/`, then re-run `generate_figures.py`. The
  audit rules and required figure-site set are in
  [visualization-contract.md](visualization-contract.md).
- **`validate_outputs.py` check fails**: read its PASS/FAIL output to find the
  failing artifact, then inspect the named JSON under `output/data/` or
  `output/reports/`. The gates and what each asserts are listed in
  [validation-contract.md](validation-contract.md).
- **Documentation contract fails** (machine path / orphan / broken link): the
  `--check` output names the offending file and reason. Machine paths must be
  repo-relative; orphaned docs need a link from an index; broken links must point
  at an existing sibling under `docs/`. See
  [README.md](README.md) for the reference-doc index.
- **Method-inventory or crosswalk `--check` fails**: the committed doc drifted
  from its source. Re-run the same script without `--check` to regenerate, then
  re-run the chain.
- **Coverage or manuscript-strict fails**: see the layer responsibilities and
  recipes in [architecture.md](architecture.md) for where computation, figures,
  and claims must live.
