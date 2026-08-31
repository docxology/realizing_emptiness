# AGENTS.md - realizing_emptiness

Private working project: **Realizing Emptiness**.

This project is a normal sidecar directory, not a nested Git repo. If you are
working through the template checkout mirror
(`template/projects/ongoing/ActiveInference/realizing_emptiness`), also read the
sidecar guidance at the template repo's `projects/AGENTS.md`; that path does not
exist from this standalone checkout.

## Source Contract

- The primary source artifact is the attached local PDF recorded in
  `data/sources/source_manifest.yaml`.
- Scholarship sources live in `data/sources/scholarship_manifest.yaml`; every
  citation key listed there must exist in `docs/manuscript/references.bib`.
- Public claims live in `output/data/source_claim_crosswalk.json` and are
  audited through `output/data/claim_support_audit.json`; do not add a claim ID
  without a source role, gate, artifact, and evidence ceiling.
- Manuscript claim language is audited through
  `output/data/manuscript_claim_audit.json`; do not introduce positive efficacy,
  attainment, clinical, or neural-measurement claims without a new empirical
  gate.
- Evidence ceilings are audited through
  `output/data/evidence_ceiling_audit.json`; every public claim must retain a
  prohibited inference, future evidence requirement, and at least one boundary
  stressor.
- Figure integrity is audited through `output/data/figure_integrity_audit.json`;
  do not add or modify figures without regenerating the source map and integrity
  audit.
- Visual design is governed by root `DESIGN.md` and
  `src/visualizations/style.py`; do not introduce colors, tiny labels, figure
  layouts, or dashboard patterns that bypass the semantic palette, render
  contracts, visual-style audit, and legibility audit.
- Simulation sensitivity is audited through
  `output/data/simulation_sensitivity_grid.json`; it is a deterministic
  surrogate over prior precision, metacognitive access, and observation noise,
  not empirical evidence.
- The compassion scope-of-concern surrogate is audited through
  `output/data/compassion_scope_audit.json` (gate `compassion_scope_audit_ok`);
  it is a finite policy-scope quantity with a precision-ablation negative
  control, not a measure of compassion, well-being, or any affective outcome.
- The seeded effect-size machinery is calibrated through
  `output/data/effect_size_calibration_audit.json` (gate
  `effect_size_calibration_audit_ok`); it is a synthetic positive control, not
  empirical statistical power over real subjects.
- Criticality branching/avalanche signatures live in
  `output/reports/criticality_proxy_report.json` and
  `output/data/criticality_stochastic_ensemble.json`; the measured branching
  must separate from the shuffled null, and these are software-trajectory
  diagnostics, not neural-criticality measurements.
- The source hash must remain
  `94e2335c3a4a37b8d49039b11b45ccda25bad65d4b80aa15428b84abfba699ac`.
- Claim ledgers use paraphrased paper locators and section/page references; do
  not paste long passages from the paper.
- Publication claims must stay within deterministic software validation unless a
  separate empirical source and gate supports them.

## Project Surface

| Path | Role |
| --- | --- |
| `src/formalism/` | Paper-source registry, equation surrogates, QRF/BMR data models |
| `src/simulation/` | Boundary-channel environment, pymdp canary, profile comparison, BMR, criticality proxies |
| `src/practice/` | Practice protocol specifications mapped to model interventions |
| `src/visualizations/` | Deterministic figure generation, source map, semantic design contracts, and integrity audit |
| `src/gates/` | Output, manuscript, source, and documentation validators |
| `docs/` | Human-readable contracts and guides (flat): QRF intro, glossary, architecture, formalism, validation, visualization, scholarship, roadmap, method inventory, RedTeam audit; index in `docs/README.md` |
| `scripts/` | Thin orchestrators only |
| `docs/manuscript/sheaf/` | Track registry and IMRAD manifest |

## Commands (canonical command list — other docs link here, they do not copy it)

```bash
uv run python scripts/run_full_chain.py
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run python scripts/check_documentation_contract.py --check
uv run python scripts/generate_method_inventory.py --check
uv run python scripts/generate_equation_crosswalk.py --check
uv run python scripts/compose_manuscript.py --validate-only --strict
uv run python scripts/validate_outputs.py
```

Render from the sibling template checkout:

```bash
cd <template-checkout>
uv run python -m infrastructure.orchestration link-projects
uv run python scripts/03_render_pdf.py --project <qualifier>
# <qualifier> is working/ or archive/ depending on the sidecar lifecycle folder —
# determine it per docs/running-the-chain.md (canonical render instructions).
```
