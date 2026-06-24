# src/simulation

Finite, seeded, deterministic simulation engines and active-inference surrogates.
Every engine is a software diagnostic that makes the paper's formal predictions
inspectable; none is a neural, empirical, or physical-qFEP measurement. Each
producer pairs its result with a discriminating negative control and a
`claim_boundary`.

## Modules

| File | Key API | Role |
| --- | --- | --- |
| `qrf_env.py` | `default_deployments`, `simulate_boundary_trajectory`, `boundary_indistinguishability_audit`, `boundary_channel_ledger`, `score_deployment` | Finite boundary-channel environment; label-invariance audit + b0-b5 channel ledger |
| `bmr.py` | `compare_models`, `run_bmr_sweep`, `write_bmr_sweep` | Bayesian model-reduction sweep over the separation prior (JSON + CSV) |
| `sensitivity.py` | `compare_sensitivity_point`, `build_sensitivity_grid`, `write_sensitivity_grid` | Deterministic grid over prior precision, metacognitive access, observation noise |
| `quantum_surrogates.py` | entropy/CHSH/local-polytope/dephasing/Lindblad/trajectory builders | Finite two-qubit and roadmap quantum-information surrogates (separability entropy, contextuality witnesses, open-system dynamics) |
| `pymdp_profiles.py` | `profile_specs`, `build_profile_generative_model`, `expected_free_energy_terms`, `run_policy_trace`, `run_profile_comparison`, `pymdp_runtime_dependency_check`, `build_pymdp_runtime_diagnostics_log` | Discrete active-inference profiles with explicit `A/B/C/D` arrays, runtime dependency diagnostics, model hashes, replay metadata |
| `stochastic.py` | `build_stochastic_policy_ensemble` | Seeded stochastic ensembles with null controls, CIs, replayable seeds |
| `criticality.py` | `branching_ratio`, `avalanche_size_distribution`, `criticality_signatures`, `branching_estimator_calibration`, `build_criticality_report`, `build_criticality_stochastic_ensemble` | Measured branching/avalanche signatures vs shuffled null + planted-ratio positive control |
| `compassion_scope.py` | `compassion_boundary_stream`, `channel_influence`, `compute_scope_of_concern`, `build_compassion_scope_audit` | Self-vs-non-self policy-scope asymmetry blending an active per-channel action-influence (action-shuffle + zero-controllability controls) with a precision-ablation control + dose-response |
| `emergence.py` | `emergence_trajectory`, `score_factored_vs_unfactored`, `build_separation_prior_emergence_audit`, `build_ongoing_revision_audit` | Separation-prior emergence surrogate (factored vs unfactored) |
| `statistical_robustness.py` | `build_stochastic_effect_size_audit`, `build_bmr_robustness_resampling_audit`, `build_quantum_trajectory_convergence_audit`, `build_effect_size_test_calibration_audit`, `build_statistical_robustness_audit` | Bootstrap CIs, permutation p-values, Cliff's delta, Holm adjustment, positive-control calibration |

## Pipeline fit

Producers are invoked by `scripts/` orchestrators (`simulate_boundary_agents.py`,
`run_bmr_sweep.py`, `generate_quantum_surrogates.py`, `generate_extended_surrogates.py`)
and write JSON/CSV to `output/data/` and `output/reports/`. `visualizations/`
reads these artifacts to render figures; `gates/validation.py` reads them for
named pass/fail checks. `expected_free_energy_terms` is also imported directly by
the gate to recompute and verify the saved `pymdp` trace.

## pymdp simulation contract

`pymdp_profiles.py` separates four checks that are easy to confuse:

1. `pymdp_runtime_dependency_check` verifies only the pinned dependency surface:
   package version, imports, agent construction, state inference, and normalized
   policy posterior. The compatibility wrapper `pymdp_version_canary` remains so
   existing schema keys and tests do not churn.
2. `build_generative_model_audit` records the profile-specific `A`, `B`, `C`,
   and `D` arrays. `A` maps hidden QRF state to observation cue, `B` stores the
   action-conditioned transition tensor, `C` stores preferences, and `D` stores
   the initial state prior.
3. `run_policy_trace` runs the deterministic profile loop over the action
   vocabulary `stabilize_dual`, `inspect_boundary`, and `release_prior`, saving
   posterior beliefs, policy posteriors, expected-free-energy terms, selected
   actions, perturbation flags, and replay metadata.
4. `build_pymdp_runtime_diagnostics_log` recomputes the saved trace from the
   stored arrays, hashes each profile model, compares the manual temporal-prior
   update with `pymdp`'s `update_empirical_prior`, and preserves the finite
   non-empirical claim boundary.

Profile action differences enter through the arrays, not through hidden
hand-tuned branches: profile-specific priors (`D`), preferences (`C`),
likelihood confidence (`A`), and transition relaxation (`B`) make different
policies cheaper or costlier under expected free energy.
