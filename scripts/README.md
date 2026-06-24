# scripts/

Thin-orchestrator entry points for the Realizing Emptiness artifact chain. These
scripts coordinate I/O only; all logic lives in `src/`. They build the finite,
deterministic software surrogates of the Sandved-Smith et al. 2026 "There is no
self-evidence" paper. Nothing here claims empirical, clinical, neural,
ontological, awakening, practice-efficacy, or physical-qFEP evidence.

## Files

| Script | Role |
| --- | --- |
| `_bootstrap.py` | Shared bootstrap; defines `PROJECT_ROOT` and puts `src/` on `sys.path`. |
| `run_full_chain.py` | Orchestrator. Runs the 16 chain steps in order; stops on first non-zero exit. |
| `generate_formalisms.py` | Formalism registry, equation audit, primary-source hash check, claim crosswalk, governance + contract artifacts. |
| `simulate_boundary_agents.py` | QRF boundary audits/ledger, pymdp profile comparison + policy trace, stochastic ensemble, compassion-scope audit. |
| `generate_quantum_surrogates.py` | Finite quantum-information surrogate artifacts. |
| `generate_extended_surrogates.py` | Extended source-fidelity surrogates (paper sections 3.3, 4.1, 5.3, 6.1). |
| `run_bmr_sweep.py` | Bayesian model-reduction sweep artifacts. |
| `generate_statistics.py` | Statistical robustness audits. |
| `generate_sheaf_tracks.py` | Criticality, practice-protocol, sensitivity, claim-context, roadmap-governance artifacts. |
| `generate_figures.py` | All project figures + figure source map. |
| `compose_manuscript.py` | Composes top-level manuscript files from sheaf fragments; writes coverage + structure audits. |
| `generate_method_inventory.py` | Generator -> `docs/method-inventory.md` (`--check` drift guard). |
| `generate_equation_crosswalk.py` | Generator -> `docs/equation-crosswalk.md` from the formalism registry (`--check` drift guard). |
| `z_generate_manuscript_variables.py` | Computes manuscript variables, hydrates `output/manuscript/`. |
| `generate_dashboard.py` | Refreshes the static artifact dashboard from the figure source map. |
| `validate_outputs.py` | Runs all output gates; writes `output/reports/validation_report.json`. |
| `check_documentation_contract.py` | Checks the local documentation contract (`--check`). |

## Pipeline fit

`run_full_chain.py` is the single deterministic entry point: it produces every
JSON/CSV artifact under `output/data`, the figures, the composed manuscript, the
generated docs, dashboard/review hardening artifacts, the hydrated manuscript,
refreshed artifact hashes, and finally the validation report. Each artifact is
consumed downstream by a JSON-Schema gate (see `../schemas/`) and exercised by
`../tests/`. Run from the project root with the project venv.
