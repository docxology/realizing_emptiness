# RedTeam Audit

Target classification: structured artifact, with file-locatable source,
validator, manuscript, generated data, and rendered-output surfaces. Oracle
exists: `scripts/validate_outputs.py`, tests, schemas, and PDF render gates.

Execution mode: internal VectorSpecialists panel, verifier-first. No external
subagents were used.

Resolved findings:

1. Verifier incompleteness: schema files existed but could drift from real
   artifact contracts. Minimal fix: add `jsonschema` validation for source,
   artifact, formalism, and scholarship targets. Negative control: a source
   manifest with stale `local_path` and no `local_pdf` fails schema validation.

2. Scholarship thinness: the manuscript could pass with only a minimal
   bibliography while making claims across qFEP, QRFs, BMR, meditation,
   criticality, compassion, and Buddhist terminology. Minimal fix: add
   `data/sources/scholarship_manifest.yaml`, generated
   `output/data/scholarship_source_matrix.json`, and bibliography-key coverage
   checks.

2b. Citation-authority laundering: a stronger bibliography could still let
    foundation sources do too much work if QRF, Markov-blanket, FEP, criticality,
    or compassion citations appeared without adjacent limitation sources.
    Minimal fix: add the FEP critique/response pair, a contemporary bounded FEP
    framing source, and a direct cortical-criticality sufficiency caution to
    the scholarship ledger; consume them in the first-use QRF, boundary,
    criticality, and source-role sections; and update tests so these
    counterweight citations remain present. The allowed source role is
    interpretive hygiene and method scoping, not empirical, neural,
    ontological, practice-efficacy, or physical qFEP support.

3. Visualization incompleteness: the original figure set showed selected
   outputs but not the full BMR pruning region or scholarship coverage. Minimal
   fix: add `bmr_pruning_phase_diagram.png` and
   `scholarship_coverage_matrix.png`, both source-mapped.

4. Manuscript claim boundary: the prose needed a stronger distinction between
   primary-source formal recapitulation, implementation anchors, background
   scholarship, and proxy-only future empirical context. Minimal fix: add sheaf
   fragments for scholarship methods, results, and discussion.

5. Claim-ID laundering: scholarship rows could name support claims that were not
   public crosswalk claims, and public claims could be added without scoped
   source support. Minimal fix: add `output/data/claim_support_audit.json`,
   schemas for the crosswalk and audit, validator checks for claim artifacts,
   gates, and evidence ceilings, and `claim_support_matrix.png`. Negative
   control: a public `unsupported_claim` row makes the claim-support audit fail.

6. Manuscript-language false certification: the validators did not explicitly
   check that manuscript citations resolve, that public claim IDs are visible in
   manuscript prose, or that positive efficacy language is absent. Minimal fix:
   add `output/data/manuscript_claim_audit.json`, a schema, validator checks,
   `manuscript_claim_audit.png`, and negative controls for missing claim IDs and
   positive realization-efficacy wording.

7. Evidence-ceiling false certification: a public claim could be sourced,
   mentioned in the manuscript, and still omit what must not be inferred from
   it. Minimal fix: add prohibited-inference, future-evidence, and boundary
   stressor fields to the public claim crosswalk, generate
   `output/data/evidence_ceiling_audit.json`, validate it with a schema and
   local gate, and visualize it in `evidence_ceiling_stress_matrix.png`.
   Negative control: removing a prohibited-inference field or adding an unknown
   stressor makes the audit fail.

7b. Claim-context opacity: support counts and evidence ceilings could still
    leave readers unsure what a public claim means, which source role licenses
    its vocabulary, which gate checks it, and which stronger reading remains
    blocked. Minimal fix: add `output/data/claim_context_ledger.json`,
    `schemas/claim_context_ledger.schema.json`, `claim_context_ledger_ok`,
    dashboard coverage, dependency-graph coverage, and
    `claim_context_evidence_ladder.png`. Negative controls: missing
    reader-facing wording, missing future-evidence boundaries,
    role-incompatible support for a finite quantum claim, or proxy wording that
    implies empirical evidence now fails the claim-context build.

8. Figure staleness false certification: `figure_source_map.json` could name the
   correct source artifacts while an old or overwritten PNG still passed
   existence checks. Minimal fix: add `output/data/figure_integrity_audit.json`
   with figure hashes, source hashes, dimensions, pixel variance, and nonblank
   checks; make `validate_outputs.py` recompute and compare those values.
   Negative control: a saved audit row with a stale figure hash now fails
   `compare_figure_integrity`.

9. Single-run simulation overclaim: the BMR and `pymdp` panels could make a
   parameter-local result look more general than the finite surrogate supports.
   Minimal fix: add `output/data/simulation_sensitivity_grid.json` and `.csv`
   over metacognitive access, prior precision, and observation noise; add the
   `simulation_sensitivity_grid_ok` gate; source-map
   `simulation_sensitivity_heatmap.png`; and route the public
   `metacognitive_access_model` claim to this stricter artifact.

10. Reproducibility crowding the main argument: validation details in the main
    Methods, Results, and Conclusion could distract from the formal recapitulation
    while still being load-bearing. Minimal fix: move detailed gate, source-map,
    artifact, and command documentation into the supplemental sheaf section and
    leave the main manuscript focused on formalism, simulation behavior, and
    limitations.

11. Caption false certification: a rendered figure could contain color-coded
    panels while the manuscript never explains the visual encoding or claim
    boundary. Minimal fix: add `output/data/visual_caption_audit.json`,
    `schemas/visual_caption_audit.schema.json`, per-figure `visual_encoding`
    rows in `figures.yaml`, and validator coverage for nontrivial captions,
    source artifacts, visual encodings, and boundary phrases. Negative control:
    removing a figure caption's boundary phrase or visual-encoding text now
    fails the visual-caption audit.

12. `pymdp` canary overtrust: a live import and normalized one-step posterior
    could pass while the paper-specific agent remained a local score table.
    Minimal fix: add profile-specific `A`, `B`, `C`, and `D` arrays,
    `output/data/pymdp_generative_model_audit.json`,
    `output/data/pymdp_policy_trace.json`,
    `output/data/pymdp_runtime_diagnostics_log.json`, and tests for model
    normalization, row-level expected-free-energy recomputation, policy
    posterior normalization, label resolution, captured runtime warnings,
    deterministic replay, and profile-specific action differences. Negative
    control: an unnormalized transition column, mismatched weighted
    expected-free-energy row, missing canary-warning capture, or unresolved
    action/observation label fails before figure generation can certify the
    profile comparison.

13. QRF visual underspecification: separate sector maps, boundary bars, and
    geometry diagrams could force readers to mentally reconstruct the finite QRF
    model and could make color-coded labels look ontological. A weaker lead
    figure also made `b0`-`b5` look like vague colored blocks rather than the
    same evidenced bitstream under different QRF labels. Minimal fix: add
    `output/data/qrf_boundary_channel_ledger.json`, split the previous
    composite into `qrf_boundary_screen_geometry.png`,
    `qrf_channel_relabeling_ledger.png`, and
    `qrf_invariance_policy_flow.png`, require the channel-ledger source-map
    metadata to declare `channel_labels = b0..b5`, retire the old composite
    from the manuscript figure contract, retain the single-purpose QRF panels
    as generated source-map support artifacts, and update
    `docs/qrf-formalism.md` with equations 7-10, admissible
    relabeling, negative controls, and non-quantum-dynamical boundaries.
    Negative controls: the ledger must contain exactly `b0`-`b5`, each profile
    must relabel every channel without changing the evidenced object, the
    negative-control relabeling must fail, and the figure source map must
    include both QRF boundary artifacts and the ledger so an unsourced
    standalone diagram fails validation.

14. Quantum-underclaim and overclaim collision: treating boundary entropy and
    contextuality as simply "not simulated" underused the software surface, but
    simulating them without new boundaries would overstate the qFEP result.
    Minimal fix: add `src/simulation/quantum_surrogates.py`,
    `output/data/quantum_boundary_entropy.json`,
    `output/data/quantum_open_system_dynamics.json`,
    `output/data/quantum_extension_roadmap.json`, schemas, validator gates,
    `quantum_boundary_entropy_landscape.png`,
    `quantum_contextuality_witness.png`, and
    `quantum_open_system_dynamics.png`. Negative controls: product states must
    have zero reduced entropy and no Bell violation, Bell endpoints must reach
    one bit and the Tsirelson value, local-basis rotations must preserve
    reduced entropy, dephasing channels must preserve trace and positivity, and
    full qFEP/empirical claims must stay in roadmap status.

15. Contextuality scalar false certification: the CHSH witness could pass as a
    single scalar curve while omitting the explicit measurement-cover
    probability table and local-polytope feasibility audit that contextuality
    readers expect to inspect. Minimal fix:
    add `output/data/quantum_measurement_contextuality.json`,
    `schemas/quantum_measurement_contextuality.schema.json`,
    `quantum_measurement_contextuality_ok`, and
    `quantum_measurement_contextuality_table.png`. Second-pass hardening adds
    `quantum_local_polytope_audit.png` and LP fields for feasibility against
    the 16 deterministic CHSH assignments. Negative controls: every context
    distribution must normalize, no-signaling marginals must match across
    context overlaps, the product control must stay within the local CHSH
    bound and fit the local polytope exactly, and the Bell empirical model must
    reach the Tsirelson value while remaining infeasible in that finite
    polytope without being described as a full sheaf-obstruction proof.

15b. Quantum visual dominance: technically rich finite quantum/control figures
     could overwhelm the source paper's no-self-evidence, QRF sectorisation,
     sigma-prior, opacification, and BMR argument in the main Results. Minimal
     fix: add `output/figures/finite_quantum_scope_summary.png` for the main
     paper, move detailed technical quantum/control figures to a supplemental
     quantum/contextuality section, and add
     `output/data/manuscript_figure_placement_audit.json`. Negative control:
     any technical quantum PNG in the main Results, any missing technical
     quantum PNG in the supplement, or any duplicated cover/main/supplement PNG
     fails validation.

15c. Governance visual dominance: scholarship coverage, claim-support,
     claim-source-validation, and palette-ledger figures could make the main
     Results read like an audit report instead of a model-behavior report.
     Minimal fix: keep the four governance QA figures in the supplemental
     reproducibility/source-map section and let the main Results summarize the
     governance finding in prose. Negative control: any one of the four
     governance PNG paths in the main Results, any missing supplemental embed,
     or any repeated supplemental embed fails
     `output/data/manuscript_figure_placement_audit.json`.

16. Visual accessibility false certification: the figure validator could pass
    a plot with a caption, source map, and nonblank pixels while omitting alt
    text or any machine-readable data alternative. Minimal fix: add
    per-figure `alt_text` rows in `figures.yaml`,
    `output/data/visual_accessibility_audit.json`,
    `schemas/visual_accessibility_audit.schema.json`, and validator checks for
    alt text, source-data alternatives, non-color encodings, and unit or axis
    language. Negative control: removing alt text or relying only on color
    makes the accessibility gate fail even if the caption and PNG hash pass.

17. Reader-facing caption false certification: the source-map caption audit
    could pass because `figures.yaml` contains full captions while the composed
    manuscript still renders short Markdown alt-text captions. Minimal fix:
    expand composed manuscript captions from `figures.yaml`, add
    `output/data/rendered_figure_caption_audit.json`,
    `schemas/rendered_figure_caption_audit.schema.json`, and
    `rendered_figure_caption_audit_ok`. Negative control: a composed figure
    reference such as `![Short caption.](../output/figures/qrf_sectorisation_map.png)`
    must fail for weak caption length, missing interpretive boundary, and
    missing visual-encoding language even though the source-map caption exists.

18. Future-evidence ambition false certification: future quantum/QRF, human,
    practice, and release work could be described as "ambitious" while no
    structured artifact records which future rows are blocked and what evidence
    would unblock them. Minimal fix: add
    `output/data/quantum_roadmap_readiness_matrix.json`,
    `schemas/quantum_roadmap_readiness_matrix.schema.json`,
    `quantum_roadmap_readiness_ok`, and
    `quantum_roadmap_readiness_matrix.png`. The future rows must remain split
    into `re-3`, `re-4`, `re-13`, `re-14`, and `re-15`, not collapsed into
    broad physical/human/release buckets. Negative controls: a future row with
    manuscript-claim permission set to true, readiness score above zero, no
    next gate, or forged self-asserted completion must fail validation.

19. Roadmap/TODO truth drift: `TODO.md` could continue to describe already
    implemented finite engines as future work while
    `quantum_extension_roadmap.json` marks them implemented. Minimal fix: add
    `output/data/roadmap_todo_audit.json`,
    `schemas/roadmap_todo_audit.schema.json`, and validator checks that reject
    future-only TODO rows matching implemented extension IDs or blocked external
    evidence classes described as achieved. Negative control: the former
    mixed-state, boundary-Hamiltonian, sheaf, and sparse-screen TODO rows fail
    the audit.

20. Extension-method underimplementation: after the first extension pass, the
    project still lacked arbitrary mixed-state entanglement controls, generic
    measurement-cover parser coverage, finite channel-cost accounting, sparse
    boundary-screen scaling beyond six qubits, and density/probability QRF
    frame covariance. Minimal fix: add
    `arbitrary_two_qubit_entanglement_audit.json`,
    `general_measurement_cover_polytope_audit.json`,
    `thermodynamic_channel_cost_audit.json`,
    `sparse_boundary_screen_scaling_audit.json`, and
    `qrf_frame_covariance_toy_audit.json`, each with schema, validator gate,
    negative controls, source-mapped figure, and manuscript boundary language.
    Negative controls: invalid density matrices, infeasible measurement covers,
    non-CPTP maps, random/separable cut controls, and nonunitary or
    trace-breaking frame maps all fail safely.

21. Manifest/dependency false certification: generated artifacts could appear
    under `output/` without manifest entries or dependency-graph nodes. Minimal
    fix: promote `sheaf_coverage_matrix.json`,
    `validation_dependency_graph.json`, and the new roadmap artifacts to
    manifest-listed schema-validated outputs, add generated-output manifest
    coverage checks, and generate a static dashboard at
    `output/dashboard/index.html`. Negative control: an unmanifested generated
    JSON or missing quantum roadmap node fails validation.

22. Stochastic-simulation false certification: single-trace summary panels
    could be mistaken for robustness evidence, while stochastic simulations could
    be mistaken for empirical data. Minimal fix: add
    `output/data/stochastic_policy_ensemble.json`,
    `output/data/criticality_stochastic_ensemble.json`,
    `output/data/quantum_trajectory_unraveling.json`, schemas, source-mapped
    figures, dashboard status rows, and validator checks for replayable seeds,
    posterior normalization, null controls, finite intervals, norm/trace/PSD
    preservation, exact-Lindblad reconstruction tolerance, gamma-zero controls,
    and invalid-operator rejection. Negative control: changing the seed changes
    sampled rows while replaying the same seed reproduces them; gamma-zero
    trajectories must have no jumps; and no stochastic artifact may claim neural,
    clinical, practice-efficacy, empirical quantum, or physical qFEP evidence.

23. Manuscript visual-reference drift: a composed manuscript could hard-code
    figure numbers, leave unresolved `fig:` or `sec:` references, or duplicate a
    main figure in the supplement after source-map validation already passed.
    Minimal fix: add `output/data/manuscript_reference_audit.json`,
    `output/data/figure_reuse_audit.json`,
    `output/data/cover_graphical_abstract_audit.json`, schemas, validators, and
    tests for one-paragraph abstract content, the Sandved-Smith first
    introduction citation, unnumbered cover graphical abstract, ordered QRF lead
    figures, no duplicate supplement PNGs, and no hard-coded manuscript figure
    numbers. Negative control: reprinting a main-text PNG in the supplement,
    embedding the retired QRF composite, or writing "Figure 1" in manuscript
    prose fails validation.

24. Cover-art regression: the graphical abstract could satisfy path and caption
    checks while reverting to a compressed wide strip with small type, making the
    title page visually weak and hard to read. Minimal fix: redesign
    `graphical_abstract_cover.png` as a hybrid symbolic near-square schematic
    with large labels, central finite-boundary/QRF motif, source-to-artifact-to-
    claim-gate flow, and explicit front-matter placement. Negative control: a
    cover outside the 1.15-1.25 aspect-ratio band, below minimum dimensions,
    missing title-page preamble placement, or lacking strong caption/alt text now
    fails `cover_graphical_abstract_audit`.

25. Targeted-scholarship leakage: adding quantum-trajectory or QRF-transform
    citations could make the manuscript sound as though physical qFEP or full
    quantum-reference-frame realization had been established. Minimal fix: bind
    Dalibard-Castin-Molmer, Molmer-Castin-Dalibard, Wiseman-Milburn, and
    Vanrietvelde-Hohn-Giacomini-Castro-Ruiz to scoped source roles in the
    scholarship manifest and reuse existing claim IDs with conservative evidence
    statuses. Negative control: the bibliography can support finite trajectory
    and covariance methods, but manuscript claim gates still block empirical,
    neural, practice-efficacy, and physical qFEP readings.

26. Hand-coded validator drift: manifest entries, schema targets, dashboard
    rows, and validator lists could diverge while all visible artifacts still
    looked current. Minimal fix: add
    `output/data/artifact_contract_registry.json`, derive contract rows from
    `artifact_manifest.yaml`, require all declared schemas to resolve, and bind
    every contract to dashboard group, manuscript role, and claim boundary.
    Negative control: a missing schema path, duplicate artifact ID, or
    unmanifested generated output now fails validation before the dashboard can
    present the project as current.

27. Keyword-only claim and method audits: a method could pass because prose used
    the right words, not because its assumptions and failure modes were
    declared. Minimal fix: add `method_assumption_ledger.json`,
    `method_negative_control_inventory.json`, the method assumption/failure-map
    figure, and validator checks requiring hard constraints, modeling choices,
    assumptions, evidence ceilings, and falsification controls for every method.
    Negative control: a method without falsification controls or boundary
    language cannot become a passing claim-bearing artifact.

28. Statistical robustness overclaim: stochastic ensembles, BMR sensitivity
    grids, or quantum trajectories could be reported as robust without effect
    sizes, null contrasts, multiplicity handling, or convergence checks.
    Minimal fix: add stochastic effect-size, BMR resampling, quantum-trajectory
    convergence, and aggregate statistical-robustness audits using bootstrap
    intervals, permutation contrasts, Holm adjustment, Cliff's delta, and a
    too-few-trajectories negative control. Negative control: nonfinite
    intervals, out-of-range p-values, vanished profile/null contrasts, unstable
    BMR signs, or a passing too-few trajectory run fails validation.

29. Visual semantic drift: figures could reuse colors inconsistently so that
    blocked rows, null controls, keep/prune decisions, and pass/fail states
    implied different meanings in different panels. Minimal fix: centralize the
    semantic palette in `src/visualizations/style.py`, add per-figure render
    contracts, generate `visual_style_audit.json` and
    `figure_legibility_audit.json`, and render the visual semantic palette
    ledger. Negative control: undeclared semantic roles, missing legends or
    colorbars, undersized figures, blank figures, or missing source-data
    alternatives now fail validation.

30. Strong-verb manuscript creep: a sentence could use words such as establish,
    prove, confirm, validate, or demonstrate near blocked domains and thereby
    exceed the evidence ceiling without triggering the original claim ledger.
    Minimal fix: add `manuscript_claim_intensity_audit.json`, scan source
    fragments sentence by sentence, and require finite-software or boundary
    scope around strong verbs. Negative control: an unscoped sentence claiming
    realization, neural measurement, clinical impact, practice efficacy, or
    physical qFEP success now fails validation.

31. Non-rejection uninterpretability and under-operationalized discussion
    sections: the seeded effect-size machinery had only negative controls, so a
    profile-vs-null non-rejection was uninterpretable without a positive control;
    the section 6.2 compassion and section 6.3 criticality tracks were the thinnest
    operationalizations (a one-line label ratio and a hand-built near-critical
    score), and equation 11 was registered as a KL complexity term that the
    scalar `FreeEnergyTerms` never computed. Minimal fix: add
    `output/data/effect_size_calibration_audit.json` with null, positive, and
    sign-flip synthetic arms wired into `effect_size_calibration_audit_ok`;
    replace the compassion ratio with `compassion_scope.py` scope-of-concern plus
    a precision-ablation control in `output/data/compassion_scope_audit.json`;
    replace the criticality near-critical score with measured branching-ratio and
    avalanche-size signatures and require the measured branching to separate from
    the shuffled null; compute a worked categorical KL for equation 11 and derive
    the equation 13-14 minima and strict-superset witness from measured free
    energy. Negative controls: a zeroed injected shift flips
    `positive_effect_rejected` False; ablating the separation prior collapses the
    constrained profile's self-concentration (and a size-preserving label shuffle
    is documented as non-discriminative, so precision ablation is the falsifier);
    a constant observation series flips the branching null-separation control
    False; and restricting the deployment roster to the dual set removes the
    eq 13-14 strict-superset witness. The compassion, criticality, and calibration
    artifacts carry verbatim evidence ceilings forbidding compassion, neural,
    practice-efficacy, and empirical-power readings.

32. Symmetric-fixture witness blind spot: the multipartite entanglement-witness
    suite first used only permutation-symmetric fixtures (GHZ, W, product), so a
    wrong-axis partial transpose would compute the same per-cut numbers and no
    control would flip. Resolution: add an asymmetric Bell-pair-plus-spectator
    fixture whose expected per-cut detection pattern is `[entangled, entangled,
    separable]`; the `asymmetric_cuts_match_expected_pattern` control fails under
    a wrong-axis transpose (verified by a cross-vendor mutation), while the
    separable-product fixtures remain the false-positive controls. The witness is
    a finite PPT/negativity surrogate, not a genuine-multipartite-entanglement
    certificate.

33. Silent helper shadowing: a second module-level `_trace_distance` added for the
    collision-model engine shadowed the existing singular-value definition for all
    callers, including the quantum-trajectory engine, under Python late binding.
    The two were mathematically identical for density matrices, but the shadow was
    a real maintenance hazard. Resolution: delete the duplicate and reuse the
    canonical definition, so no caller is silently rebound.

34. Synthesis-figure caption drift and asserted-constant risk: a redesigned
    separation-prior lifecycle figure left a stale `figures.yaml` caption ("mean
    across precisions", "a single line") describing the old design, and the new
    finite engines risked asserting unverified quantum constants. Resolution:
    rewrite the caption to match the rendered per-precision curves; bind the
    use/ontology figure's headline verdicts and the lifecycle crossing precision
    to the data rather than to literals (regression-tested); and implement the
    n-cycle contextuality library as measured noncontextual-polytope LP
    feasibility cross-checked against graph two-colorability, so every verdict is
    measured, never a stapled bound.

35. Release-readiness false certification: the local artifact-release manifest
    hashed generated outputs and a few runner files, but not the implementation
    sources, schemas, tests, manuscript fragments, or docs that reproduce and
    explain those outputs; it also did not check that review-response `gate`
    strings named real passing checks. Resolution: expand release support
    coverage to source/reproduction files, make `validate_outputs.py` recompute
    release-manifest fingerprints from disk, and require every review-response
    row to resolve to a real passing gate, including the blocked public archive
    and independent-reproduction gate. Negative controls: editing a source file
    after release-manifest generation flips
    `artifact_release_manifest_hashes_current` and
    `artifact_release_manifest_ok`, and replacing a review-response gate with a
    bogus name flips `external_review_response_gates_resolve`.

36. Supplement ToC overflow by audit fragmentation: the final supplement
    carried release/review-response hardening and limitations as adjacent
    third-level headings, which made the rendered table of contents spill one
    extra line while also implying that limitations were separate from the
    release record. Resolution: merge those materials into
    `Release, Review Response, and Limits`, preserve the old limitations
    anchors as inline aliases, and add tests that assert the final
    meta-manuscript section has four third-level headings, no standalone
    `Supplemental Limitations` heading, and the revised title set. Manual
    control: `pdftotext` over the rendered PDF must show the ToC ending at
    `7.8.4 Release, Review Response, and Limits`, with no `7.8.5` line.

37. Claim-oracle false certification: the claim-support, evidence-ceiling, and
    claim-context gates could all pass while a public claim pointed to an
    unresolved manuscript anchor, named a non-source-mapped figure, or used a
    locally scoped strong verb in wording that still invited empirical,
    clinical, neural, practice-efficacy, awakening, ontological, or physical
    qFEP over-reading. Resolution: add `output/data/claim_redteam_audit.json`
    as a joined row-per-claim audit over the crosswalk, context ledger,
    evidence ceilings, source-argument coverage, manuscript-claim audit,
    claim-intensity audit, and figure source map; require every public claim to
    resolve section and figure bindings, retain source roles, gates,
    prohibited inferences, and future-evidence boundaries, and expose the
    result in validation plus the dashboard. Negative controls: unresolved
    `sec:` anchors, unknown figure IDs, missing prohibited/future boundaries,
    and an unscoped sentence such as "The software establishes no-self" now
    fail tests and validation.

Remaining risk:

- The finite quantum-information layer now directly simulates selected
  two-qubit entropy, mixed-state entanglement, CHSH, finite local-polytope,
  generic measurement-cover, CPTP channel-cost, dephasing-channel, and seeded
  quantum-trajectory controls, and the implemented extension layer adds boundary-Hamiltonian
  Lindblad, exact/sparse many-body cut-sweep, sheaf obstruction, QRF
  relabeling/frame covariance, multipartite/higher-dimensional witness,
  tensor-network MPS benchmark, collision-model thermalization, no-signaling
  scenario library, n-cycle contextuality library, and empirical-provenance
  controls. These still
  cannot instantiate physical qFEP, human practice efficacy, neural measurement,
  or a real many-body observer boundary. This is intentional and must remain
  labeled as finite simulation plus blocked future evidence classes.
- Practice and criticality outputs remain future-facing interfaces and simulated
  indicators, not efficacy or empirical-neural evidence.
- The expanded sensitivity grid and seeded stochastic ensembles widen internal
  validation but do not add human-subject, neural, or physical quantum evidence.
- The richer `pymdp` loop is still a finite discrete surrogate. It validates
  posterior and policy mechanics for the QRF profiles; it does not establish the
  source paper's quantum result or any empirical practice outcome.
