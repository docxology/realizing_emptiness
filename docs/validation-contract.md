# Validation Contract

`scripts/validate_outputs.py` is fail-closed for the v1 artifact surface. It
checks source integrity, output existence, schema validity, scholarship coverage,
claim-support bindings, evidence-ceiling stressors, joined claim RedTeam
controls, equation mapping, QRF negative controls, reader-facing claim-context
controls, QRF `b0`-`b5` boundary-channel ledger controls,
source-argument coverage controls, finite quantum-information controls, mixed-state
PPT/negativity controls, generic measurement-cover LP controls, CPTP
channel-cost controls, boundary-Hamiltonian Lindblad controls, seeded
quantum-trajectory controls, exact and sparse many-body boundary-screen
controls, sheaf obstruction controls, QRF transformation and frame-covariance
controls, empirical-adapter provenance controls, roadmap/TODO consistency,
dependency-graph coverage, manifest coverage, contract-registry coverage,
local release-manifest coverage, review-response coverage, figure-parameter
traceability, neutral QRF label ablation, independent quantum cross-checks,
BMR alternative-prior checks,
method-assumption and negative-control coverage, statistical robustness audits,
static dashboard generation, BMR pruning edges, simulation sensitivity
boundaries, `pymdp` package diagnostics, explicit `A`/`B`/`C`/`D`
generative-model normalization, policy-trace posterior normalization, seeded
active-inference ensemble controls, practice-safety wording, criticality-style
stochastic ensemble boundaries, figure source counts, caption visual-encoding
coverage, visual accessibility metadata, semantic-palette consistency,
legibility metadata, figure hashes and nonblank image checks, manuscript
subsection anchors, manuscript reference resolution, figure-reuse checks,
balanced main/supplement quantum figure-placement checks, cover-graphic checks,
manuscript variable hydration, rendered-manuscript figure
captions, manuscript claim-intensity boundaries, and artifact-manifest path
resolution.

The validator intentionally attacks false certification:

- schema files are validated against their actual target artifacts;
- `data/sources/source_manifest.yaml` must use the current `local_pdf` contract;
- `output/data/formalism_registry.json` must expose the current equation schema;
- scholarship manifests cannot cite missing bibliography keys;
- scholarship coverage must retain paired boundary sources for high-risk
  interpretive zones: FEP/Markov-blanket framing needs critique plus qualified
  response sources, QRF language needs physical-QRF boundary sources, and
  criticality proxy language needs false-positive and evidential-sufficiency
  cautions;
- source-supported claim IDs cannot be unknown to the local claim registry;
- public claim rows must resolve to existing artifacts, passing gates, and
  explicit evidence ceilings;
- public claim rows must declare a prohibited inference, future evidence
  requirement, and allowed boundary stressor;
- `output/data/claim_context_ledger.json` must give every public claim a
  reader-facing sentence, paper locator, source-role rationale, source keys,
  artifact, validation gate, evidence class, allowed interpretation, prohibited
  inference, future-evidence boundary, manuscript-section bindings, and figure
  bindings;
- claim-context role compatibility is fail-closed: primary-source formal
  claims may be primary-only, finite quantum/qFEP claims require quantum or
  contextuality/open-system method sources, runtime claims require
  implementation/runtime support, and proxy or practice-boundary claims require
  caution, provenance, practice-interface, or boundary sources;
- claim-context checks must reject missing reader-facing wording, missing
  future-evidence boundaries, unresolved source keys, missing artifacts or
  gates, role-incompatible support, and proxy claims whose reader-facing
  wording implies empirical, clinical, neural, practice-efficacy, awakening, or
  physical qFEP evidence;
- `output/data/claim_redteam_audit.json` must join the public claim crosswalk,
  claim-context ledger, evidence ceilings, source-argument coverage,
  manuscript-claim audit, claim-intensity audit, and figure source map into one
  row per public claim; every row must resolve its manuscript `sec:` anchors,
  resolve figure bindings to source-mapped figure IDs, retain source roles,
  artifacts, gates, prohibited inferences, and future-evidence requirements,
  and carry no reader-facing overclaim wording or unscoped strong-verb sentence;
- sensitivity-grid rows must preserve the QRF indistinguishability boundary and
  explicitly state that the grid is not empirical evidence;
- finite quantum rows must pass product-state, Bell-state, CHSH, basis
  invariance, contextual-fraction, measurement-cover normalization,
  no-signaling, product-control, local-polytope feasibility,
  dephasing-channel, multipartite-witness false-positive, tensor-network
  truncation, collision-model zero-coupling, no-signaling-library disturbance,
  n-cycle two-colorability, and roadmap checks before any direct quantum claim
  is public;
- `source_argument_coverage_audit.json` must map the source paper's core
  no-self-evidence, QRF sectorisation, sigma-prior, opacification, BMR,
  post-dual, contextuality, compassion, and criticality themes to manuscript
  anchors, artifacts, validation gates, and evidence ceilings; QRF, BMR, and
  opacification themes cannot be covered only by supplemental quantum artifacts;
- `qrf_boundary_channel_ledger.json` must contain exactly `b0`-`b5`, assign
  sector labels for all separation-constrained, opacified, and post-dual
  profiles, keep each evidenced channel identity invariant under relabeling,
  link rows to equations 7-10, and include a failing negative-control relabeling;
- implemented finite extension engines must pass boundary-Hamiltonian Lindblad, mixed-state
  entanglement, measurement-cover polytope, CPTP channel-cost, seeded
  quantum-trajectory, exact/sparse many-body cut-sensitivity,
  sheaf-obstruction, QRF covariance, multipartite/higher-dimensional witness,
  tensor-network MPS benchmark, collision-model thermalization, no-signaling
  scenario library, n-cycle contextuality library, and provenance controls
  before the governance ledger can mark them implemented;
- `TODO.md` must remain future-only: a row cannot describe an already
  implemented extension engine as future work, and blocked external evidence
  classes cannot be described as achieved. Its blocker table may point readers
  to governance docs, but those links are explanatory signposts, not evidence
  that a blocker has been satisfied;
- `validation_dependency_graph.json` must include all implemented quantum extension engines,
  visual audits, claim audits, claim-context ledger, claim RedTeam audit,
  manuscript, dashboard, and render-gate nodes;
- every current generated data/report/figure output must either be represented
  in `artifact_manifest.yaml` or be an explicitly ignored post-validation or
  template-render report;
- `output/data/artifact_contract_registry.json` must derive from
  `artifact_manifest.yaml`, resolve every declared schema path, reject duplicate
  artifact IDs, assign dashboard and manuscript roles, and carry a boundary
  statement that keeps the registry itself inside finite software validation;
- `output/data/artifact_release_manifest.json` must hash manifest-listed outputs
  and reproduction-support files for local private release readiness, including
  the source tree, schemas, tests, manuscript fragments, docs, `uv.lock`, and
  source manifests; `validate_outputs.py` recomputes those fingerprints so a
  stale release manifest fails, excludes the release manifest's own hash, and
  requires that no public publication or independent reproduction has been
  performed;
- `output/data/external_review_response_audit.json` must account for every
  implemented review delta, bind each response row to a real passing
  `validate_outputs.py` gate, and keep public archive plus independent or
  blinded reproduction blocked until explicit publication approval and external
  reproduction exist;
- `output/data/figure_parameter_ledger.json` must give every source-mapped
  figure one traceable row with source artifacts, result counts, parameters or
  controls where available, and a non-empirical claim boundary;
- `output/data/qrf_label_ablation_audit.json` must preserve ledger structure
  under neutral aliases for `self`, `env`, `body`, `action`, `world`, `other`,
  and `care`, while a structure-changing collapse control fails;
- `output/data/quantum_independent_crosscheck_audit.json` must rederive CHSH,
  Tsirelson, product locality, and local-polytope feasibility through
  independent closed-form and LP paths, with a perturbed expected-value control
  that fails;
- `output/data/bmr_alternative_prior_audit.json` must measure baseline,
  log-compressed sigma-complexity, and convex access-dependent sigma-accuracy
  families, record keep/prune verdicts, and show that at least one weakest-prior
  crossing shifts while high-access rows stay numerically bounded;
- `output/data/method_assumption_ledger.json` and
  `output/data/method_negative_control_inventory.json` must give every method
  hard constraints, modeling choices, assumptions, evidence ceilings, and
  falsification controls, and no method may enter the manuscript as an
  unsupported empirical, neural, clinical, awakening, practice-efficacy, or
  physical qFEP claim;
- `output/dashboard/index.html` and
  `output/data/artifact_dashboard_payload.json` must exist and report the same
  roadmap, figure, TODO-audit, dependency-graph, contract-registry,
  method-governance, claim-context, claim RedTeam, statistical-robustness,
  visual-quality, and manuscript audit counts as the source artifacts;
- the quantum roadmap readiness matrix must keep the five blocked external
  classes (`re-3` physical qFEP realization, `re-4` human-subject validation,
  `re-13` clinical/awakening/compassion-efficacy/neural-measurement claims,
  `re-14` user-facing practice applications, and `re-15` public archive plus
  independent or blinded reproduction) at readiness score zero and claim
  permission false until a concrete artifact, schema, validator, and negative
  control are added; a forged-completed future-row control must also show that
  self-asserted completion cannot enable manuscript claims;
- `pymdp_profile_comparison.json` must include the limited runtime dependency
  check for the pinned `inferactively-pymdp` version, imports, agent
  construction, state inference, and policy-posterior normalization; this check
  does not certify active-inference optimality or scientific validity;
- `pymdp_generative_model_audit.json` must show normalized `A`, `B`, `C`, and `D`
  arrays for all three QRF profiles;
- `pymdp_policy_trace.json` must normalize state and policy posteriors at every
  time step and preserve deterministic replay metadata;
- `pymdp_runtime_diagnostics_log.json` must record package/JAX/runtime
  diagnostics, captured runtime dependency warnings, profile model hashes, per-step
  posterior and policy normalization residuals, expected-free-energy terms,
  selected action and observation labels, perturbation flags, replay metadata,
  and a claim boundary; validation rederives expected-free-energy terms from the
  saved `A`/`B`/`C`/`D` arrays, checks
  `policy_posterior @ expected_free_energy`, verifies label resolution, and
  requires deterministic replay equality;
- `stochastic_policy_ensemble.json` must replay by seed, normalize state and
  policy posteriors at every sampled step, include null controls, and report
  finite intervals;
- `criticality_stochastic_ensemble.json` must derive simulated criticality-style
  indicators from the stochastic policy ensemble, include null contrasts, and
  state that these are not neural measurements;
- `stochastic_effect_size_audit.json` must report finite profile-versus-null
  intervals, permutation p-values, Holm-adjusted p-values, and Cliff's-delta
  directions over seeded software rows;
- `bmr_robustness_resampling_audit.json` must report finite bootstrap intervals,
  bounded pruning rates, and at least one stable sign cell over the sensitivity
  grid;
- `quantum_trajectory_unraveling.json` must preserve trajectory norms, preserve
  ensemble trace, remain positive semidefinite, reconstruct exact Lindblad
  densities within tolerance, pass a gamma-zero no-jump control, and reject
  invalid rates or operators;
- `quantum_trajectory_convergence_audit.json` must show finite residuals,
  negative log-log residual slope, largest-count tolerance, improvement over
  the smallest audited count, and a too-few-trajectories negative control that
  fails;
- manuscript citations must resolve to `docs/manuscript/references.bib`;
- every public claim ID must appear in manuscript prose;
- unsupported positive efficacy, attainment, clinical, or neural-measurement
  wording must be absent from manuscript fragments;
- the figure count must agree with `src/gates/validation.py`, including the
  cover graphical abstract, the three ordered QRF lead figures, stochastic criticality
  ensemble, supplemental `pymdp` runtime-validation dashboard,
  quantum-trajectory figure, quantum entropy/contextuality/local-polytope
  figures, sensitivity heatmap, claim-context evidence ladder, and formalism
  operation map;
- the visual caption audit must reject missing source artifacts, trivial
  captions, missing boundary phrases, and undocumented visual encodings;
- the rendered-caption audit must reject short reader-facing manuscript
  captions even when the source-map caption metadata is valid;
- the visual accessibility audit must reject missing alt text, missing
  source-data alternatives, color-only encodings, and missing unit or axis
  language;
- the visual style audit must reject undeclared semantic roles and figures that
  lack a legend or colorbar contract;
- the figure legibility audit must reject undersized or blank figures, missing
  render contracts, missing source-data alternatives, and too-small declared
  fonts;
- figure integrity hashes, source-artifact hashes, dimensions, and nonblank
  checks are recomputed from disk and compared with
  `output/data/figure_integrity_audit.json`;
- hydrated manuscript files must not contain unresolved `{{TOKENS}}`.
- manuscript subsection headings must carry informative titles and stable
  `sec:` anchors, high-value method/result/discussion anchors must be
  referenced in prose, and the final supplement must keep reproducibility,
  release, review-response, visual-QA, and limitation material inside
  `sec:supplement-meta-manuscript-record` rather than reopening standalone
  gate or limitation sections.
- manuscript `sec:`, `fig:`, and `eq:` references must resolve, duplicate
  anchors must be absent, hard-coded manuscript figure numbers must be absent,
  and supplement images must not duplicate cover or main-text images.
- `manuscript_figure_placement_audit.json` must keep technical quantum/control
  figures out of the main Results, require the compact finite quantum scope
  summary in the main Results, and require the technical quantum figures in the
  supplemental quantum/contextuality audit section. It must also keep the
  scholarship coverage matrix, claim-support matrix, claim-source-validation
  graph, and visual semantic palette ledger out of the main Results while
  requiring each governance QA figure exactly once in the supplemental
  reproducibility/source-map section.
- the manuscript claim-intensity audit must flag strong verbs such as prove,
  establish, confirm, validate, or demonstrate when they appear without finite
  software scope or explicit boundary language.
- the cover graphical abstract must remain a source-mapped, unnumbered,
  title-page/front-matter graphic with near-square aspect ratio, minimum
  dimensions, hybrid symbolic style metadata, and nontrivial caption and alt
  text.

If future work adds empirical data, the validation contract must grow before the
manuscript is allowed to claim empirical support. At minimum, add source identity,
preprocessing provenance, negative controls, and artifact hashes.
