# src

Project-specific business logic for **Realizing Emptiness** — a finite,
deterministic *software surrogate* for Sandved-Smith et al. (2026) *There is no
self-evidence*. All computation lives here (and in `infrastructure/`); scripts in
`scripts/` are thin orchestrators that import these modules and only handle I/O.
Nothing in this tree is empirical, clinical, neural, ontological, awakening,
practice-efficacy, or physical-qFEP evidence; every audit ships negative/positive
controls and a `claim_boundary`.

## Subpackages

| Package | Role |
| --- | --- |
| [`formalism/`](formalism/README.md) | Paper-source registry, equation 1-14 surrogates, QRF/BMR/free-energy data models, scholarship matrix, claim ledgers, evidence-ceiling stress, source-argument coverage |
| [`simulation/`](simulation/README.md) | Boundary-channel environment, BMR sweeps, sensitivity grid, finite quantum surrogates, `pymdp` profiles with explicit `A/B/C/D` arrays and runtime dependency diagnostics, seeded stochastic ensembles, criticality/compassion/emergence surrogates, statistical robustness |
| [`visualizations/`](visualizations/README.md) | Deterministic figure generation, figure source map, semantic-style/caption/legibility/accessibility audits, figure-integrity hashing, static dashboard, rendered-caption sync |
| [`gates/`](gates/README.md) | Fail-closed output/manuscript/source/documentation validators, artifact-contract registry, roadmap-TODO and validation-dependency-graph audits |
| [`practice/`](practice/README.md) | Practice protocol specs mapped to model interventions, with `allow_user_facing_claims=false` |

`__init__.py` exports the five subpackages as `__all__`.

## Pipeline fit

Each `build_*` / `run_*` / `generate_*` producer writes a JSON artifact under
`output/data/` (or `output/reports/`, `output/figures/`, `output/dashboard/`),
validated against a schema in `schemas/` and registered in
`artifact_manifest.yaml`. `gates/` reads every artifact and returns named
pass/fail checks; `scripts/run_full_chain.py` sequences the producers and runs the
gates. Tests live in `../tests/` (no mocks; real numerical examples; 90% coverage
floor).
