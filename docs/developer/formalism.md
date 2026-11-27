# src/formalism

Typed finite data models, the paper equation registry (1-14), and the
provenance/claim governance layer. This package turns the Sandved-Smith paper's
formal commitments into inspectable, source-mapped artifacts and ledgers — never
into empirical evidence.

## Modules

| File | Key API | Role |
| --- | --- | --- |
| `models.py` | `BoundaryScreen`, `QRFDeployment`, `Sectorisation`, `SeparationPrior`, `FreeEnergyTerms`, `BMRComparison`; `complexity_kl`, `vfe_noise_insufficient_learning` | Frozen finite surrogates for boundary/QRF/separation-prior/free-energy concepts |
| `equations.py` | `EquationSurrogate`, `equation_registry`, `evaluate_equation_surrogates`, `render_equation_crosswalk` | Registry of all 14 paper equations with computable/structural status, paper-to-software bridge, eq 13/14 containment witness |
| `source.py` | `load_source_manifest`, `sha256_file`, `verify_primary_source_hash` | Loads source manifest; fail-closed primary-PDF hash check |
| `scholarship.py` | `load_scholarship_manifest`, `validate_scholarship_manifest`, `build_scholarship_source_matrix`, `build_claim_support_audit` | Citation-key/bib coverage, source-role matrix, claim-support audit |
| `claim_context.py` | `build_claim_context_ledger`, `write_claim_context_ledger` | Per-claim reader sentence, allowed reading, prohibited inference, gate, artifact, evidence boundary |
| `claim_redteam.py` | `build_claim_redteam_audit`, `write_claim_redteam_audit` | Joined adversarial audit for claim sections, figures, gates, boundaries, and intensity |
| `manuscript.py` | `build_manuscript_claim_audit`, `build_manuscript_claim_intensity_audit`, `classify_sentence_intensity` | Citation resolution, claim-ID mentions, unscoped strong-verb intensity flags |
| `source_fit.py` | `build_source_argument_coverage_audit` | Maps paper themes (no-self-evidence, QRF, sigma prior, opacification, BMR, contextuality, compassion, criticality) to anchors/artifacts/gates/ceilings |
| `stress.py` | `build_evidence_ceiling_audit` | Requires prohibited inference + future-evidence requirement + boundary stressors per public claim |
| `governance.py` | `build_method_assumption_ledger`, `build_method_negative_control_inventory` | Hard-constraint/assumption and falsification-control ledgers |

## Pipeline fit

`equation_registry`/`evaluate_equation_surrogates` feed `output/data/equation_audit.json`
(gate `equation_count_14`). The scholarship, claim-support, claim-context,
manuscript, source-fit, stress, and governance builders write their JSON artifacts
under `output/data/`, each validated against a `schemas/*.schema.json` file and read
back by `gates/`. `source.py` is the trust root: every gate run calls
`verify_primary_source_hash`.
