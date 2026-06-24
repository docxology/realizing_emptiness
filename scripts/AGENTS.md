# scripts/ - agent conventions

- Thin orchestrators only. Coordinate I/O, paths, and ordering. No business
  logic: every computation imports from `src/`. If you reach for a formula here,
  it belongs in `src/`.
- Import `PROJECT_ROOT` from `_bootstrap`, which also wires `src/` onto
  `sys.path`. Never hard-code paths; resolve relative to `PROJECT_ROOT`.
- Run from the project root with the project venv. `run_full_chain.py` invokes
  each step as `sys.executable scripts/<name>.py`.

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
