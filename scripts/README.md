# scripts/

Thin-orchestrator entry points for the Realizing Emptiness artifact chain. These
scripts coordinate I/O only; all logic lives in `src/`. They build the finite,
deterministic software surrogates of the Sandved-Smith et al. 2026 "There is no
self-evidence" paper. Nothing here claims empirical, clinical, neural,
ontological, awakening, practice-efficacy, or physical-qFEP evidence.

## Inventory

| Script | Purpose | Delegates to | Command |
| --- | --- | --- | --- |
| `run_full_chain.py` | Orchestrator; runs the 16 chain steps in order, stops on first non-zero exit. | all step scripts below | `uv run python scripts/run_full_chain.py` |
| `generate_formalisms.py` | Formalism registry, equation audit, source-hash check, claim crosswalk, governance + contract artifacts. | `formalism.claim_crosswalk`, `formalism.equations`, `formalism.governance`, `formalism.manuscript`, `formalism.scholarship`, `formalism.source`, `formalism.stress`, `gates.contracts` | `uv run python scripts/generate_formalisms.py` |
| `simulate_boundary_agents.py` | QRF boundary audits/ledger, pymdp profile comparison + policy trace, stochastic ensemble, compassion-scope audit. | `formalism.models`, `simulation.pymdp_profiles`, `simulation.qrf_env`, `simulation.stochastic`, `simulation.compassion_scope` | `uv run python scripts/simulate_boundary_agents.py` |
| `generate_quantum_surrogates.py` | Finite quantum-information surrogate artifacts. | `simulation.quantum_surrogates` | `uv run python scripts/generate_quantum_surrogates.py` |
| `generate_extended_surrogates.py` | Extended source-fidelity surrogates (paper sections 3.3, 4.1, 5.3, 6.1). | `simulation.emergence`, `simulation.blackwell_ordering`, `simulation.classical_data_processing`, `simulation.interaction_information`, `simulation.markov_blanket`, `simulation.quantum_estimation`, `simulation.quantum_surrogates` | `uv run python scripts/generate_extended_surrogates.py` |
| `run_bmr_sweep.py` | Bayesian model-reduction sweep artifacts. | `simulation.bmr` | `uv run python scripts/run_bmr_sweep.py` |
| `generate_statistics.py` | Statistical robustness audits. | `simulation.statistical_robustness` | `uv run python scripts/generate_statistics.py` |
| `generate_sheaf_tracks.py` | Criticality, practice-protocol, sensitivity, claim-context, roadmap-governance artifacts. | `simulation.criticality`, `simulation.sensitivity`, `practice.protocols`, `formalism.claim_context`, `formalism.source_fit`, `gates.roadmap` | `uv run python scripts/generate_sheaf_tracks.py` |
| `generate_figures.py` | All project figures + figure source map. | `visualizations.figures` | `uv run python scripts/generate_figures.py` |
| `compose_manuscript.py` | Composes top-level manuscript files from sheaf fragments; writes coverage + structure audits. | `formalism.compose` | `uv run python scripts/compose_manuscript.py` |
| `generate_method_inventory.py` | Generator for `docs/method-inventory.md` (`--check` drift guard). | `gates.method_inventory` | `uv run python scripts/generate_method_inventory.py [--check]` |
| `generate_equation_crosswalk.py` | Generator for `docs/equation-crosswalk.md` from the formalism registry (`--check` drift guard). | `formalism.equations` | `uv run python scripts/generate_equation_crosswalk.py [--check]` |
| `z_generate_manuscript_variables.py` | Computes manuscript variables, hydrates `output/manuscript/`. | `gates.manuscript_variables` | `uv run python scripts/z_generate_manuscript_variables.py` |
| `generate_dashboard.py` | Refreshes the static artifact dashboard from the figure source map. | `visualizations.dashboard` | `uv run python scripts/generate_dashboard.py` |
| `generate_review_response_artifacts.py` | Review-response hardening artifacts (run twice in the chain; second pass refreshes hashes). | `formalism.claim_redteam`, `formalism.review_response`, `visualizations.dashboard` | `uv run python scripts/generate_review_response_artifacts.py` |
| `validate_outputs.py` | Runs all output gates; writes `output/reports/validation_report.json`. | `gates.validation` | `uv run python scripts/validate_outputs.py` |
| `check_documentation_contract.py` | Checks the local documentation contract (`--check`). | `gates.validation` | `uv run python scripts/check_documentation_contract.py --check` |

Shared helper: `_bootstrap.py` defines `PROJECT_ROOT` and puts `src/` on
`sys.path`; it carries no logic.

## Pipeline fit

`run_full_chain.py` is the single deterministic entry point: it produces every
JSON/CSV artifact under `output/data`, the figures, the composed manuscript, the
generated docs, dashboard/review hardening artifacts, the hydrated manuscript,
refreshed artifact hashes, and finally the validation report. Each artifact is
consumed downstream by a JSON-Schema gate (see `../schemas/`) and exercised by
`../tests/`. Run from the project root with the project venv.
