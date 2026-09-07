# scripts/ - agent conventions

- Thin orchestrators only. Coordinate I/O, paths, and ordering. No business
  logic: every computation imports from `src/`. If you reach for a formula here,
  it belongs in `src/`.
- Import `PROJECT_ROOT` from `_bootstrap`, which also wires `src/` onto
  `sys.path`. Never hard-code paths; resolve relative to `PROJECT_ROOT`.
- Run from the project root with the project venv. `run_full_chain.py` invokes
  each step as `sys.executable scripts/<name>.py`.

## Script inventory

| Script | Delegates to | Primary outputs |
| --- | --- | --- |
| `generate_formalisms.py` | `formalism.claim_crosswalk`, `formalism.equations`, `formalism.governance`, `formalism.manuscript`, `formalism.scholarship`, `formalism.source`, `formalism.stress`, `gates.contracts` | `output/data/formalism_registry.json`, `equation_audit.json`, `source_claim_crosswalk.json`, governance/contract artifacts |
| `simulate_boundary_agents.py` | `simulation.pymdp_profiles`, `simulation.qrf_env`, `simulation.stochastic`, `simulation.compassion_scope` | QRF boundary/ledger, pymdp profile + policy trace, stochastic ensemble, compassion-scope artifacts |
| `generate_quantum_surrogates.py` | `simulation.quantum_surrogates` | finite quantum-information artifacts |
| `generate_extended_surrogates.py` | `simulation.emergence`, `simulation.blackwell_ordering`, `simulation.classical_data_processing`, `simulation.interaction_information`, `simulation.markov_blanket`, `simulation.quantum_estimation`, `simulation.quantum_surrogates` | extended source-fidelity artifacts |
| `run_bmr_sweep.py` | `simulation.bmr` | `output/data/bmr_sweep.json` |
| `generate_statistics.py` | `simulation.statistical_robustness` | statistical robustness artifacts |
| `generate_sheaf_tracks.py` | `simulation.criticality`, `simulation.sensitivity`, `practice.protocols`, `formalism.claim_context`, `formalism.source_fit`, `gates.roadmap` | criticality/practice/sensitivity/claim-context/roadmap artifacts |
| `generate_figures.py` | `visualizations.figures` | `output/figures/*` + figure source map |
| `compose_manuscript.py` | `formalism.compose` | `docs/manuscript/*.md` + `output/data/sheaf_coverage_matrix.json` + structure audits |
| `generate_method_inventory.py` | `gates.method_inventory` | `docs/method-inventory.md` |
| `generate_equation_crosswalk.py` | `formalism.equations` | `docs/equation-crosswalk.md` |
| `z_generate_manuscript_variables.py` | `gates.manuscript_variables` | `output/data/manuscript_variables.json` + hydrated `output/manuscript/*` |
| `generate_dashboard.py` | `visualizations.dashboard` | static artifact dashboard |
| `generate_review_response_artifacts.py` | `formalism.claim_redteam`, `formalism.review_response`, `visualizations.dashboard` | review-response + release-manifest artifacts |
| `validate_outputs.py` | `gates.validation` | `output/reports/validation_report.json` |
| `check_documentation_contract.py` | `gates.validation` | documentation-contract check |

## Chain order (run_full_chain.py)

1. `generate_formalisms.py`
2. `simulate_boundary_agents.py`
3. `generate_quantum_surrogates.py`
4. `generate_extended_surrogates.py`
5. `run_bmr_sweep.py`
6. `generate_statistics.py`
7. `generate_sheaf_tracks.py`
8. `generate_figures.py`
9. `compose_manuscript.py`
10. `generate_method_inventory.py`
11. `generate_equation_crosswalk.py`
12. `generate_dashboard.py`
13. `generate_review_response_artifacts.py`
14. `z_generate_manuscript_variables.py`
15. `generate_review_response_artifacts.py`
16. `validate_outputs.py`

Respect ordering: later steps read artifacts produced by earlier ones
(`generate_equation_crosswalk.py` requires `formalism_registry.json`; sheaf
tracks read the pymdp profile/stochastic outputs; variable hydration reads the
dashboard/review-response validation surface; the final review-response pass
refreshes hashes after hydrated manuscript variables are written).

## Generators with drift guards

`generate_method_inventory.py` and `generate_equation_crosswalk.py` write into
`docs/` and accept `--check`, which fails non-zero when the committed doc is
stale. After changing `src/` symbols or the equation registry, re-run them
without `--check` to refresh, then commit the regenerated docs.

## Claim ceiling

Surrogates are finite and deterministic. Never add output or wording that claims
empirical, clinical, neural, ontological, awakening, practice-efficacy, or
physical-qFEP evidence.
