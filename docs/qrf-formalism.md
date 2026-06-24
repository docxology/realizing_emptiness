# QRF Formalism Contract

This project implements a finite operational surrogate for the paper's QRF
argument and now pairs it with a scoped finite quantum-information layer. The
QRF boundary-screen model still does not simulate quantum reference-frame
dynamics. Its purpose is to make the paper's inferential roles inspectable: a
boundary channel can be used for prediction while the sector label assigned to
that channel remains unevidenceable by the bitstream alone. QRF and
perspective-neutral frame sources support the transformation vocabulary; they
do not license treating this six-channel screen as a full physical QRF model.

## Finite Boundary Screen

`src/formalism/models.py` defines `BoundaryScreen` as a fixed number of binary
boundary channels. In figures and artifacts, these channels are rendered as
`b0`, `b1`, ..., `b5`. A channel is a software observation coordinate, not an
ontological partition. The environment in `src/simulation/qrf_env.py` emits
deterministic bitstream trajectories over the screen so that QRF labels can be
varied without changing the observation distribution.

`output/data/qrf_boundary_channel_ledger.json` is the executable ledger for
that distinction. It records exactly six rows, one for each `b_i`, with a
finite surrogate role, an invariant evidence-object string, the sector label
assigned by the separation-constrained, opacified, and post-dual profiles, and
links to equations 7-10. The controls require the channel IDs to be exactly
`b0`-`b5`, require all three profiles to assign sector labels, require the
evidenced channel identity to remain invariant under relabeling, and require a
negative-control relabeling to fail. This is the contract behind the standalone
channel-ledger figure:
the same boundary bit can be labeled differently by different QRF deployments,
but the software does not treat any label as evidence for an ontological
self/world partition.

## Sectorisation Maps

`QRFDeployment` assigns one semantic sector label to each boundary channel. The
current profiles are:

- `separation_constrained`: a dual self/environment sectorisation with high
  separation-prior precision;
- `opacified`: a mixed sectorisation that keeps dual labels visible while
  introducing contextual labels;
- `post_dual`: a richer contextual sectorisation over body, action, world,
  other, and care.

These labels are finite interpretive tags. They are useful because the BMR and
`pymdp` profiles can condition priors, preferences, and transition structure on
them. They are not evidence that the world is actually divided into those
sectors.

## Equation Mapping

Equations 7-10 are the QRF core in the software registry:

- Equation 7 maps QRF sectorisation to a function from boundary channels to
  semantic sectors.
- Equation 8 maps conditional model evidence to profile-conditioned scores.
- Equation 9 maps the unevidenceability claim to a finite
  boundary-indistinguishability audit.
- Equation 10 maps the separation prior to an admissible subspace of
  self/environment sectorisations.

`output/data/formalism_registry.json` records these rows as computable finite
surrogates with an explicit non-quantum-dynamical boundary. The lead QRF visual
sequence now uses three generated manuscript figures:
`output/figures/qrf_boundary_screen_geometry.png` for the finite screen and
action-observation flow, `output/figures/qrf_channel_relabeling_ledger.png` for
the `b0`-`b5` channel ledger and equations 7-10, and
`output/figures/qrf_invariance_policy_flow.png` for the normalized probability
mass audit, failing perturbation control, and active-inference action counts.
The retired four-panel composite is not generated as a manuscript figure, and
the single-purpose QRF support panels remain generated source-map artifacts but
are not repeated as numbered main Results figures.

## Admissible Relabeling And Negative Controls

An admissible relabeling changes sector labels while preserving the marginal
boundary-observation distribution. The audit in
`output/data/qrf_boundary_indistinguishability.json` therefore checks two
conditions:

- all admissible deployments preserve normalized marginal probability mass;
- a perturbed negative-control deployment fails the invariant.

This is the critical negative-control check. Without the negative control, a figure could
certify only that all displayed rows are normalized, not that the validator can
detect a wrong boundary distribution.

## pymdp Coupling

`src/simulation/pymdp_profiles.py` builds a profile-specific discrete
active-inference model with explicit arrays:

- `A`: likelihood from hidden QRF state to boundary cue;
- `B`: transition tensor over actions `stabilize_dual`, `inspect_boundary`, and
  `release_prior`;
- `C`: preference vector over observation cues;
- `D`: initial state prior.

The generated artifacts form four linked contracts. First,
`output/data/pymdp_profile_comparison.json` carries the profile-level comparison
plus the limited runtime dependency check: pinned package version, imports,
agent construction, state inference, and policy-posterior normalization. Second,
`output/data/pymdp_generative_model_audit.json` stores the explicit normalized
`A`, `B`, `C`, and `D` arrays. Third,
`output/data/pymdp_policy_trace.json` and
`output/data/pymdp_runtime_diagnostics_log.json` store the deterministic trace,
model hashes, package/JAX versions, action and observation labels, perturbation
flags, posterior and policy normalization residuals, row-level
expected-free-energy recomputation, and deterministic replay metadata. Fourth,
`output/data/stochastic_policy_ensemble.json` and the robustness audits validate
seeded trajectory ensembles, null controls, confidence intervals, and
profile-null effect sizes. These artifacts operationalize the QRF surrogate as
an active-inference loop while keeping the paper boundary intact: the loop ranks
finite software deployments, not ontologies.

## Figure Contract

The lead QRF visual sequence is split into three source-mapped figures with a
fixed sector legend and shared typography: `qrf_boundary_screen_geometry.png`
defines the boundary screen and action-observation flow,
`qrf_channel_relabeling_ledger.png` makes the b0-b5 relabeling ledger readable
as the conceptual anchor, and `qrf_invariance_policy_flow.png` combines the
invariant probability audit with the profile-specific policy-flow summary.
Their captions, source-map rows, and `visual_caption_audit.json` entries must
state that the figures are finite surrogates and not empirical, clinical,
awakening, neural, ontological, biological-sensor, or quantum-dynamical
evidence.

The QRF visual contract now also inherits the shared semantic palette and
render-contract audits. QRF-sector colors, pass/fail markers, finite/blocked
status, stochastic/null hatches, and boundary/source colors must be declared in
the source map and checked by `visual_style_audit.json`; figure dimensions,
source-data alternatives, panel counts, and minimum-font metadata must be
checked by `figure_legibility_audit.json`. This prevents a QRF panel from
making a relabeling or covariance result appear stronger than its source
artifact permits.

## Method-Governance Contract

QRF methods appear in `method_assumption_ledger.json` and
`method_negative_control_inventory.json`. The finite boundary-screen method is
allowed to claim only probability-preserving relabeling invariance over the
declared bitstream; the transformation-covariance method is allowed to claim
only stochastic-map covariance over declared probability vectors; and the
frame-covariance toy audit is allowed to claim only invariant spectra and
reduced-entropy multisets under the declared unitary/permutation transforms.
Each method must name hard constraints, modeling choices, assumptions, evidence
ceilings, and falsification controls before the manuscript can use it as a
claim-bearing QRF result.

## Quantum-Information Extension Boundary

`src/simulation/quantum_surrogates.py` is intentionally separate from the QRF
boundary-screen code. It simulates a two-qubit Schmidt-family control surface:
reduced von Neumann entropy, mutual information, CHSH witness strength,
contextual-fraction scaling, local-basis entropy invariance, and a
Landauer-scaled erasure lower bound. It also simulates mixed-state PPT and
negativity controls for separable, Bell, and Werner-family density matrices;
finite CHSH and generic measurement-cover empirical models with normalization,
no-signaling, and deterministic-assignment polytope checks; finite CPTP
channel-cost accounting; and a finite two-qubit dephasing channel with trace,
positivity, entropy, mutual-information, and CHSH-decay controls. These are
direct finite calculations that support `quantum_separability_entropy`,
`quantum_contextuality_witness`, `quantum_measurement_contextuality`, and
`quantum_open_system_dephasing`.

They do not make the QRF surrogate quantum-dynamical. The bridge to equations
7-10 is conceptual and validated only at the finite software boundary: QRF
relabelings preserve a classical boundary-observation distribution, while the
finite quantum layer tests small Hilbert-space entropy, mixed-state
separability, measurement-cover contextuality, local-polytope infeasibility,
CPTP channel accounting, open-system dephasing controls, and seeded
quantum-trajectory reconstruction against exact Lindblad densities. The current
implemented extension engines extend this finite boundary with additional audits, but stronger
claims about physical qFEP realization, human practice effects, neural
measurements, or full quantum-reference-frame covariance still require external
evidence classes.

## Implemented Extension Engine Coupling

The implemented extension layer adds finite audits around that QRF core:

- boundary-Hamiltonian Lindblad dynamics test trace, positivity, entropy
  production, mutual-information contraction, and invalid-dynamics negative
  controls for a small open-system surrogate;
- seeded quantum-trajectory unraveling tests Monte Carlo jump/no-jump paths,
  norm preservation, density reconstruction, gamma-zero controls, and invalid
  operator rejection, using the Monte Carlo wave-function literature as method
  background rather than as physical qFEP evidence;
- mixed-state two-qubit entanglement tests PPT/negativity controls and rejects
  invalid density matrices;
- generic measurement-cover polytopes test feasible and infeasible parsed
  scenarios beyond the fixed CHSH table;
- thermodynamic channel-cost audits test finite CPTP maps and reject non-CPTP
  entropy-cost inputs;
- exact six-qubit boundary-screen sweeps test subsystem-cut sensitivity and
  reject separable or random-cut controls as observer-boundary evidence;
- sparse exact boundary-screen sweeps extend the same controls to six, eight,
  and ten qubits while tracking amplitude density;
- a general measurement-cover LP tests global-section feasibility and parity
  obstruction beyond the fixed CHSH table;
- QRF transformation covariance tests probability-preserving relabelings and
  rejects nonadmissible maps;
- QRF frame covariance tests finite density-matrix and probability-vector
  invariants under admissible unitary/permutation transforms and remains a toy
  perspective-change audit rather than a full perspective-neutral QRF theory;
- the empirical adapter tests provenance and blocks synthetic or unsourced
  human/practice records from empirical claim permission;
- a multipartite and higher-dimensional witness suite tests negativity/PPT over
  GHZ, W, and qutrit fixtures with separable-product false-positive controls and
  an asymmetric fixture that catches wrong-axis transpose regressions;
- a tensor-network (matrix-product-state) benchmark tests exact reconstruction,
  bond-dimension scaling beyond exact enumeration, and a truncation control;
- a collision-model surrogate tests partial-SWAP relaxation toward an ancilla
  with a zero-coupling control;
- a no-signaling scenario library tests marginal independence and flags a
  disturbing table, and an n-cycle contextuality library tests noncontextual
  polytope feasibility cross-checked against graph two-colorability.

These additions make equations 7-10 more technically inspectable, but they do
not establish physical qFEP realization, full quantum-reference-frame
covariance, human practice efficacy, or neural evidence.

See also: [QRF introduction](qrf-introduction.md) for the conceptual on-ramp,
the [equation crosswalk](equation-crosswalk.md) and generated
[method inventory](method-inventory.md) for the full equation-to-artifact and
code-to-engine catalogs, and the [glossary](glossary.md) for terminology.
