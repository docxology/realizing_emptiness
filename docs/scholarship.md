# Scholarship Source Matrix

`data/sources/scholarship_manifest.yaml` is the source-of-truth bibliography
ledger. It does not merely list references; it assigns each source a role,
evidence status, supported tracks, and supported claim IDs.

The generated artifact `output/data/scholarship_source_matrix.json` makes the
source ledger executable:

- citation keys must be unique;
- every citation key must appear in `docs/manuscript/references.bib`;
- every source must declare an `evidence_status`;
- required tracks must have at least one source role;
- recent arXiv additions for QRF, Markov-blanket/FEP, and contemplative-AI
  context must remain role-scoped background and cannot create empirical,
  clinical, neural, full-qFEP, or practice-efficacy evidence;
- discrete active-inference and expected-free-energy sources must support the
  `pymdp` profile loop without becoming evidence for empirical realization;
- Markov-blanket and QRF boundary sources must support boundary vocabulary while
  preserving the no-ontology-from-bitstream limit; Bruineberg et al.'s
  Pearl/Friston-blanket distinction, Rovelli's relational quantum mechanics,
  and Varela/Thompson/Rosch's enactive neurophenomenology are background
  guardrails, not evidence that the finite screen is an ontological, empirical,
  or physical QRF boundary;
- finite quantum-information, PPT/separability, Werner-state, Bell, CHSH,
  contextuality, quantum-operation/CPTP, decoherence, Landauer, GKSL/Lindblad,
  Monte Carlo wave-function, quantum-measurement/control, QRF-transformation,
  tensor-network, Fine local-polytope, FEP critique/response, Bayesian workflow, simulation-calibration,
  reproducibility-checklist, bootstrap, Holm correction, dominance-effect-size, FAIR data,
  compassion-measurement, criticality-false-positive, Madhyamaka, enaction,
  advanced computational-phenomenology, selfing/identification, phenomenological-selfhood,
  and preregistration sources must support only the two-qubit entropy,
  mixed-state entanglement, witness, measurement-cover, local-polytope,
  channel-cost, dephasing-channel, boundary-Hamiltonian, quantum-trajectory,
  many-body cut, sheaf-obstruction, QRF-covariance, multipartite-witness,
  tensor-network, collision-model, no-signaling, n-cycle-contextuality,
  BMR comparator-family, statistical-robustness, local private artifact-release,
  provenance, care/compassion proxy boundaries, emptiness/no-self terminology,
  organismic-versus-identified-with-self vocabulary, minimal-self caveats, and
  roadmap vocabulary;
- the matrix is visualized in the supplemental reproducibility/source-map
  section through `output/figures/scholarship_coverage_matrix.png`, not as a
  main Results figure.

The generated artifact `output/data/claim_support_audit.json` makes the claim
ledger executable:

- every public claim in `output/data/source_claim_crosswalk.json` must have at
  least one supporting scholarship row;
- every scholarship `supports_claims` ID must exist in the local claim registry;
- every public claim must carry a gate, an artifact, and an evidence ceiling;
- claim-level source support is visualized in
  `output/figures/claim_support_matrix.png` as a supplemental governance QA
  figure.

The generated artifact `output/data/claim_context_ledger.json` turns those
support rows into reader-facing claim semantics. Each public claim must have a
readable claim sentence, scoped source roles, bibliography keys, an artifact, a
validation gate, an evidence class, an allowed interpretation, a prohibited
inference, a future-evidence boundary, manuscript-section bindings, and figure
bindings. Role compatibility is deliberately typed: a primary formal claim can
be supported by the Sandved-Smith source when the local claim is a
recapitulation, whereas quantum claims require quantum or contextuality method
support, runtime claims require implementation support, and proxy/practice
claims require caution, provenance, boundary, or practice-interface support.
The main Results figure `output/figures/claim_context_evidence_ladder.png`
summarizes this reader-facing layer; longer support bars mean broader
source-role context, not stronger empirical status.

The generated artifact `output/data/manuscript_claim_audit.json` binds the
claim ledger back to manuscript prose. It verifies citation-key resolution,
requires every public claim ID to appear in the manuscript, and rejects positive
efficacy or attainment wording that would exceed the project evidence ceiling.

The generated artifact `output/data/evidence_ceiling_audit.json` binds each
public claim to three adversarial fields: what the claim must not be read as,
what future evidence would be needed to make a stronger claim, and which
stressors constrain the claim. The corresponding
`output/figures/evidence_ceiling_stress_matrix.png` makes those stressors
inspectable by claim ID and claim class.

Evidence statuses are intentionally conservative. A quantum-information,
PPT/separability, Werner-state, Bell/CHSH, sheaf-contextuality, quantum-channel,
decoherence, GKSL/Lindblad, Monte Carlo wave-function, quantum-measurement,
QRF-transformation, or tensor-network source supports a finite entropy,
mixed-state entanglement, CHSH, measurement-cover, local-polytope,
channel-cost, dephasing-channel, boundary-Hamiltonian, quantum-trajectory,
many-body cut, sheaf-obstruction, or QRF-covariance calculation, not the full
qFEP thesis.
Bootstrap, Holm, and Cliff sources support simulation-robustness summaries over
generated rows; they do not make any profile/null contrast empirical, clinical,
neural, or practice-efficacy evidence.
Fine supports the local-polytope reading of the CHSH measurement-cover audit.
Talts and Gelman support Bayesian workflow and simulation-checking boundaries
for the BMR alternative-prior audit, not real-subject power. Pineau supports
artifact-release checklist practice for local private release readiness, not a
public archive or independent reproduction claim.
FAIR and preregistration sources support empirical-adapter provenance
requirements, not empirical results. Criticality sources support the vocabulary
for a toy proxy and future empirical adapter, including the warning that
power-law-like scaling alone can be a false positive and that cortical-criticality
evidence remains method-sensitive, not a claim that the simulation measures
neural criticality. FEP critique, sparse-coupling response, and Pearl/Friston
blanket sources support the boundary against unqualified Markov-blanket or
ontology readings; they do not make the finite b0-b5 screen an empirical or
physical boundary. Relational quantum mechanics and enactive
neurophenomenology support observer-relative and enacted-interface vocabulary;
they do not turn the local relabeling audit into a physical QRF theory. Care and compassion sources support
care-salience and compassion-proxy boundary language, not affective,
psychometric, moral, or clinical outcomes. Meditation, Buddhist-studies,
computational-phenomenology, selfing/identification, and
phenomenological-selfhood sources support interface vocabulary and conceptual
boundary conditions, not practice efficacy, attainment, or proof against
minimal selfhood.
Discrete
active-inference sources support the `A`/`B`/`C`/`D` runtime contract,
deterministic trace, expected-free-energy policy vocabulary, and structured
runtime-diagnostics log, not the truth of any QRF ontology.
Markov-blanket sources support boundary-formalism context, not a claim that the
finite boundary screen is an empirical or quantum boundary.

## Estimands, nulls, and calibration

The [targeted scholarship expansion](scholarship-expansion.md) records 32
additional sources verified on 2026-10-14, including the primary records and
the operational reason for each addition. This is a targeted methodological
curation, not a systematic review or an estimate of disciplinary consensus.
The ledger now contains 125 entries. Publication dates use the journal issue
year when it differs from online-first publication; the minimal active-inference
agent remains explicitly a preprint.

The statistical sources sharpen three different questions. First, what is the
estimand: a profile mean, a difference between profiles, a dominance effect, or
a paired difference between an original trajectory and its shuffled control?
Second, what is resampled: independent runs, intact pairs, stationary blocks,
or time order conditional on a fixed trajectory? Third, what uncertainty is
reported: variation across generated runs, an interval for the contrast, or
Monte Carlo error from a finite resampling budget? Morris and Burton motivate
explicit simulation design; Kunsch and Politis-Romano constrain dependent-data
resampling; Phipson-Smyth, Hemerik-Goeman, and Winkler constrain permutation
validity. Theiler and Schreiber-Schmitz make the preserved and destroyed
features of a surrogate null part of the scientific question. Romano-Wolf
provides a comparison for multiplicity methods without implying that the
local Holm procedure implements a dependence-adaptive stepdown algorithm.

Cook, Modrak, and Sailynoja distinguish computational calibration from model
adequacy. A rank or coverage check can miss errors to which its chosen test
quantity is insensitive; conditioning a check on a dataset answers a narrower
question than averaging over the prior predictive distribution. Flegal
motivates reporting simulation error, while Gneiting-Raftery motivates scoring
the predictive distribution rather than equating low entropy with predictive
success. These are design constraints and comparisons: their presence in the
ledger does not certify that every cited method has been implemented.

## Physical and experiential interpretation boundaries

The added active-inference literature distinguishes the implemented objective
from an interpretation of the modeled system. Buckley makes assumptions
inspectable; Millidge questions an automatic identification of expected and
variational free energy; Friston and McGregor provide process and minimal-agent
comparators. Van Es supplies a further counterweight: a scientist's model and
a model attributed to an organism are different claims. Existing FEP critiques
and qualified responses remain mandatory.

Quantum no-cloning, no-broadcasting, and asymmetry-resource sources separate
software operations on stored arrays from physically admissible operations on
unknown states. Frame covariance under relabeling alone does not specify a
symmetry group, admissible channels, or a consumable reference-frame resource.
The existing physical-QRF counterweights remain mandatory.

Phenomenological interview methods and first-person-data research motivate
careful elicitation and analysis of reports, while meditation measurement and
adverse-experience studies motivate construct validity, comparison conditions,
and explicit safety monitoring for any future human study. They supply no
human observations to this repository. Profile names, precision parameters,
and care-scope quantities remain model interfaces; none is a validated measure
of mindfulness, compassion, attainment, clinical benefit, or neural activity.
