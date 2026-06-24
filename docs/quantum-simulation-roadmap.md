# Quantum Extension Governance

This page defines what the project simulates directly and what remains a future
evidence class. It reserves "roadmap" for TODO/governance rows and prevents "quantum surrogate" from collapsing finite
quantum-information controls into claims about the source paper's full qFEP
interpretation.

## Direct Finite Simulations

`src/simulation/quantum_surrogates.py` writes the direct finite quantum and
implemented-extension artifacts:

- `quantum_boundary_entropy.json`: Schmidt-family two-qubit reduced entropy,
  mutual information, purity, CHSH witness, contextual fraction, basis
  invariance, and Landauer lower-bound controls.
- `quantum_measurement_contextuality.json`: finite CHSH measurement-cover
  probabilities, no-signaling checks, Tsirelson/local controls, and
  local-hidden-variable polytope feasibility.
- `quantum_open_system_dynamics.json`: trace-preserving two-qubit dephasing
  controls over entropy, mutual information, and CHSH decay.
- `qfep_boundary_hamiltonian_dynamics.json`: finite boundary-Hamiltonian
  Lindblad dynamics with trace, positivity, entropy-production,
  mutual-information contraction, and invalid-dynamics negative controls.
- `quantum_trajectory_unraveling.json`: seeded Monte Carlo wave-function
  trajectories for the two-qubit Lindblad surrogate, grounded in the
  quantum-jump and quantum-measurement/control literature, with norm checks,
  ensemble trace and PSD checks, exact-Lindblad reconstruction residuals,
  jump-count distributions, gamma-zero controls, and invalid-operator rejection.
- `many_body_boundary_screen_sweep.json`: exact six-qubit subsystem-cut sweep
  with separable and random-cut negative controls.
- `sheaf_contextuality_obstruction_audit.json`: finite measurement-cover LP
  that accepts a noncontextual global-section control and rejects a parity
  obstruction while preserving no-disturbance marginals.
- `qrf_transformation_covariance_audit.json`: probability-preserving QRF
  relabeling covariance audit with nonadmissible mass-gain and negative-entry
  controls.
- `empirical_adapter_provenance_audit.json`: fail-closed provenance interface
  that blocks unsourced human/practice data and allows synthetic fixtures only
  as software demonstrations.
- `arbitrary_two_qubit_entanglement_audit.json`: mixed-state density-matrix
  audit with PPT/negativity controls for separable, Bell, and Werner-family
  cases plus invalid-density negative controls.
- `general_measurement_cover_polytope_audit.json`: reusable measurement-cover
  parser and deterministic-assignment LP for triangle, parity, CHSH-product,
  and CHSH-Bell scenarios.
- `thermodynamic_channel_cost_audit.json`: finite CPTP channel checks with
  entropy-change and Landauer lower-bound summaries plus non-CPTP rejection
  controls.
- `sparse_boundary_screen_scaling_audit.json`: exact sparse state-vector
  screens across six, eight, and ten qubits with separable and random-cut
  controls.
- `qrf_frame_covariance_toy_audit.json`: finite unitary/permutation frame
  transforms over density matrices and probability vectors, scoped by QRF and
  perspective-neutral frame scholarship, with nonunitary and trace-breaking
  controls.
- `multipartite_witness_suite_audit.json`: negativity/PPT entanglement witness
  over GHZ (two-, three-, four-qubit), W, and a maximally entangled qutrit pair
  across every single-subsystem-versus-rest bipartition, with separable-product
  false-positive controls and an asymmetric Bell-pair-plus-spectator fixture
  whose per-cut pattern catches wrong-axis transpose regressions.
- `tensor_network_benchmark_audit.json`: exact matrix-product-state
  decomposition by sequential SVD with bond-dimension scaling (GHZ stays bond
  two, products bond one) beyond exact state-vector enumeration and a bond-one
  truncation control that is lossy on entangled states and lossless on products.
- `collision_model_thermalization_audit.json`: finite collision-model
  relaxation of a system qubit toward a fixed ancilla through repeated
  partial-SWAP interactions, trace-preserving and positive per step, with a
  zero-coupling control that leaves the system unchanged.
- `no_signaling_scenario_library_audit.json`: no-signaling / no-disturbance
  audit over a scenario library, satisfied by quantum CHSH-Bell and product
  behaviors and flagging a deliberately disturbing table as signaling.
- `n_cycle_contextuality_library_audit.json`: noncontextual-polytope LP
  feasibility over n-cycle compatibility graphs (n=3..7), with the odd-versus-even
  contextuality dichotomy cross-checked against graph two-colorability (perfect
  anti-correlation feasible iff the cycle is even) and the KCBS pentagon as the
  canonical odd cycle.
- `roadmap_todo_audit.json`: fail-closed check that future-only TODO rows do
  not duplicate implemented extension engines and that blocked external evidence
  classes are not described as achieved.

These are real finite calculations, not rhetorical placeholders. Their claim
boundary is still narrow: physical qFEP realization, human practice efficacy,
and neural measurement remain future evidence classes.

The targeted bibliography is intentionally methodological. Monte Carlo
wave-function and quantum-measurement/control sources justify the sampled
trajectory algorithm and ensemble-density comparison; QRF transformation
sources justify the covariance vocabulary. None of these sources changes the
claim ceiling for the finite surrogate.

## Validation Gates

The validator requires each finite engine to pass both schema and semantic
controls.

`quantum_boundary_entropy_ok` checks product/Bell entropy endpoints, CHSH
local/Tsirelson controls, basis-invariance drift, contextual-fraction endpoint,
and finite non-empirical boundary language.

`quantum_measurement_contextuality_ok` checks normalized nonnegative joint
probabilities, no-signaling marginals, product-control locality, Bell
Tsirelson saturation, exact local-polytope feasibility for the product control,
and local-polytope infeasibility for the Bell table.

`quantum_open_system_dynamics_ok` checks trace preservation, positive
semidefiniteness, product-control stability, Bell-state entropy increase, CHSH
decay, and mutual-information contraction under dephasing.

`qfep_boundary_hamiltonian_dynamics_ok` checks Hermitian Hamiltonian structure,
Lindblad trace preservation, positive semidefiniteness, nonnegative entropy
production, mutual-information contraction, and safe rejection of
non-Hermitian, trace-breaking, and non-positive negative controls.

`many_body_boundary_screen_sweep_ok` checks that the candidate observer-boundary
cut reaches maximum finite entropy in the entangled sweep, that cut sensitivity
is present, that separable controls remain entropy-zero, and that random cuts
are not labeled as observer-boundary evidence.

`sheaf_contextuality_obstruction_audit_ok` checks that a noncontextual triangle
control has a feasible global section, that a parity obstruction has no global
section and positive residual, and that all scenario marginals remain
no-disturbing.

`qrf_transformation_covariance_audit_ok` checks that admissible maps preserve
probability mass and expectation under relabeling, while nonadmissible mass-gain
and negative-entry maps are rejected.

`empirical_adapter_provenance_audit_ok` checks that unsourced human/practice
data are blocked, synthetic fixtures are demo-only, provenance-incomplete
placeholders remain blocked, and no row is allowed to support an empirical
claim.

`arbitrary_two_qubit_entanglement_audit_ok` checks density-matrix validity,
separable-control negativity, Bell-state negativity, Werner-family PPT
threshold behavior, and invalid-density rejection.

`general_measurement_cover_polytope_audit_ok` checks feasible and infeasible
measurement-cover scenarios, no-disturbance preservation, and positive
residuals for obstruction cases.

`thermodynamic_channel_cost_audit_ok` checks CPTP structure, valid output
density matrices, zero identity cost, positive erasure costs for mixed inputs,
and non-CPTP rejection.

`sparse_boundary_screen_scaling_audit_ok` checks that observer-cut entropy
scales with qubit count, separable controls stay zero, random cuts are not
observer evidence, and sparse amplitude density decreases with size.

`qrf_frame_covariance_toy_audit_ok` checks unitary acceptance, invariant spectra,
covariant reduced-entropy multisets, probability-vector covariance, and
nonunitary/trace-breaking rejection.

`quantum_extension_roadmap_ok` and `quantum_roadmap_readiness_ok` then verify
that implemented finite rows have artifacts, schemas, validators, and negative
controls, while five ledger-aligned blocked classes remain future-only:
physical qFEP realization (`re-3`), human-subject validation (`re-4`),
clinical/awakening/compassion-efficacy/neural-measurement claims (`re-13`),
user-facing practice applications (`re-14`), and public archive plus
independent or blinded reproduction (`re-15`). The readiness matrix also
includes a forged-completed future-row control, so a row cannot self-assert
completion and enable manuscript claims without a real artifact, schema,
validator, gate, and negative control.

`roadmap_todo_audit_ok` checks that `TODO.md` is future-only and contains no
future-work row that duplicates an implemented extension ID or claims a blocked
external evidence class has been achieved.

## Visual Surface

The main paper uses `finite_quantum_scope_summary.png` as the compact visual
for finite quantum scope. That summary matrix records which finite engines,
negative controls, and blocked stronger claims are present without letting the
quantum/control layer displace the QRF/BMR/no-self-evidence argument.

The detailed quantum and roadmap figures are supplemental. They are generated
from these artifacts and must include legends or colorbars plus explicit
boundary language:

- `finite_quantum_scope_summary.png`
- `quantum_boundary_entropy_landscape.png`
- `quantum_contextuality_witness.png`
- `quantum_measurement_contextuality_table.png`
- `quantum_local_polytope_audit.png`
- `quantum_open_system_dynamics.png`
- `qfep_boundary_hamiltonian_dynamics.png`
- `quantum_trajectory_unraveling.png`
- `quantum_trajectory_convergence.png`
- `many_body_boundary_screen_sweep.png`
- `sheaf_contextuality_obstruction_audit.png`
- `qrf_transformation_covariance_audit.png`
- `arbitrary_two_qubit_entanglement_audit.png`
- `general_measurement_cover_polytope_audit.png`
- `thermodynamic_channel_cost_audit.png`
- `sparse_boundary_screen_scaling_audit.png`
- `qrf_frame_covariance_toy_audit.png`
- `empirical_adapter_provenance_audit.png`
- `quantum_roadmap_readiness_matrix.png`

## Future Evidence Classes

The roadmap separates implemented finite software engines from stronger
evidence classes. Each row below is present in
`output/data/quantum_extension_roadmap.json`,
`output/data/quantum_roadmap_readiness_matrix.json`, `tasks.yaml`, and
`TODO.md`. Each row has readiness score `0.0`, `manuscript_claim_allowed:
false`, no current artifact/schema/validator credit, and a required next
artifact plus gate. The listed negative-control role describes what the future
gate must reject before the row can support any stronger claim.

| ID | Blocked class | Required next artifact and gate | Negative-control role |
| --- | --- | --- | --- |
| `re-3` | Physical qFEP realization. Reviewed physical Hamiltonians, thermodynamic accounting, and independent quantum-information replication are required before finite quantum software can be read as physical qFEP evidence. | `output/data/physical_qfep_realization_audit.json`; `physical_qfep_realization_audit_ok`. | Reject finite Lindblad, stochastic trajectory, many-body, or channel-cost surrogates as physical qFEP realization evidence. |
| `re-4` | Human-subject validation. Ethics review, preregistered outcomes, source identity, preprocessing provenance, null models, and safety review are required before any human-data claim is allowed. | `output/data/human_subject_validation_audit.json`; `human_subject_validation_audit_ok`. | Reject synthetic, unsourced, or ethics-incomplete human data as empirical claim support. |
| `re-13` | Clinical, awakening, compassion-efficacy, and neural-measurement claims. Reviewed external outcome or measurement evidence with independent controls is required before any such claim is allowed. | `output/data/clinical_awakening_compassion_neural_audit.json`; `clinical_awakening_compassion_neural_audit_ok`. | Reject finite compassion, criticality, practice, or protocol surrogates as clinical, awakening, compassion-efficacy, or neural-measurement evidence. |
| `re-14` | User-facing practice applications. Human review, safety wording, explicit non-efficacy language, and release governance are required before any practice-facing application can be released. | `output/data/user_facing_practice_safety_audit.json`; `user_facing_practice_safety_audit_ok`. | Reject practice protocol maps as user-facing instructions or efficacy claims without human safety review. |
| `re-15` | Public archive release and independent or blinded reproduction. Explicit publication approval, public deposition, and external reproduction of the artifact bundle are required before public-release or independent-reproduction claims are allowed. | `output/data/public_archive_independent_reproduction_audit.json`; `public_archive_independent_reproduction_audit_ok`. | Reject local private hashes, manifests, validations, and renders as proof of public release or independent reproduction. |

No future evidence class may be described as achieved until it has a source
artifact, schema, validator gate, figure-source map entry, negative control,
and manuscript evidence ceiling. Local software gates can keep the blockers
visible and fail-closed, but they do not satisfy the external evidence each
blocker names.
