# src/gates

Fail-closed validators. The gates read every produced artifact and return named
pass/fail checks; a missing or unparseable gated artifact yields an empty payload
so the check evaluates to `False` instead of crashing the run. Gates assert the
finite-surrogate discipline (schemas, controls, claim boundaries) but never assert
empirical truth.

## Modules

| File | Key API | Role |
| --- | --- | --- |
| `validation.py` | `validate_outputs`, `check_documentation_contract`; `EXPECTED_DATA`/`EXPECTED_REPORTS`/`EXPECTED_FIGURES`/`EXPECTED_WEB`/`EXPECTED_SCHEMAS`, `SCHEMA_TARGETS`, `_load_json` | Existence, schema validity, source hash, per-artifact control checks, manifest coverage; doc contract checks stale identity, machine paths, orphan/broken links |
| `contracts.py` | `ArtifactContract`, `artifact_contracts`, `build_artifact_contract_registry`, `write_artifact_contract_registry` | Derives the artifact-contract registry from `artifact_manifest.yaml` for validation + dashboard coverage |
| `manuscript.py` | `build_manuscript_reference_audit`, `build_figure_reuse_audit`, `build_figure_placement_audit`, `build_cover_graphical_abstract_audit`, `write_manuscript_structure_audits` | Citation resolution, figure reuse, main-vs-supplement placement, cover graphical-abstract dimension/aspect audits |
| `roadmap.py` | `build_roadmap_todo_audit`, `build_validation_dependency_graph`, `write_roadmap_governance_artifacts` | Fails on stale future-work rows once an engine is implemented; builds the validation dependency graph |

## Pipeline fit

`scripts/validate_outputs.py` calls `validate_outputs(project_root)` and prints the
named-check results; `scripts/check_documentation_contract.py` calls
`check_documentation_contract`. The manuscript and roadmap builders write their
JSON artifacts (validated by schemas, listed in `EXPECTED_DATA`) which
`validate_outputs` then re-checks. Gates import producers from `formalism/`,
`simulation/`, and `visualizations/` to recompute and compare saved artifacts.
