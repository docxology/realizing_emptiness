# Visualization Contract

All figures are deterministic products of JSON or CSV artifacts under
`output/data/` or `output/reports/`. `src/visualizations/figures.py` writes
`output/data/figure_source_map.json`, which records the figure ID, output path,
source artifact paths, caption, alt text, visual encoding, render contract, and
renderer-layout telemetry.

Captions are part of the validation surface. They must name the software object
being visualized, the source artifact behind the figure, and the interpretive
boundary that prevents proxy plots from becoming empirical or practice-efficacy
claims.

`output/data/visual_caption_audit.json` checks that every figure has a
nontrivial caption, at least one source artifact, an explicit interpretive
boundary phrase, and a documented visual encoding.
`output/data/rendered_figure_caption_audit.json` separately checks the composed
manuscript captions that appear in the rendered paper; short Markdown alt text
cannot pass merely because `figures.yaml` contains a stronger source-map
caption.
`output/data/visual_accessibility_audit.json` checks that every figure has
alt text, a source-data alternative, non-color encodings, and axis or unit
language. `output/data/figure_integrity_audit.json`
records the SHA-256 hash, dimensions, pixel variance, nonblank status, byte
size, and source-artifact hashes for each figure. `scripts/validate_outputs.py`
recomputes these values from disk so a stale or overwritten PNG cannot pass
merely because the expected path exists.

The visual contract includes explicit render contracts. Every source-map row
declares semantic roles, panel count, legend count, colorbar count, and minimum
font metadata. `output/data/visual_style_audit.json` checks that the semantic
roles resolve to the shared palette, that semantic colors meet the 3:1
non-text contrast floor against white, and that every figure has a legend or
colorbar contract. `output/data/figure_legibility_audit.json` checks dimensions
against a 1200 by 600 pixel floor, nonblank pixels, source-data alternatives,
panel metadata, the 12.0 pt minimum readable-font metadata, and renderer-level
layout failures. The telemetry is deterministic: overlapping text, overlapping
panel titles, cropped labels, and legend/axis collisions are counted in the
source map, surfaced in the dashboard Visual QA block, and rejected by
validation when any count is nonzero. The shared palette fixes role semantics
across the manuscript: pass/fail, keep/prune, finite/blocked, stochastic/null,
quantum, QRF, source, and boundary colors cannot drift by figure.
Root `DESIGN.md` is the reader-facing visual contract for those tokens; the
source of truth remains `src/visualizations/style.py`, and the generated visual
audits verify that figures follow it.

The cover graphical abstract has an additional contract because it appears in
front matter rather than as a numbered result. It must be a hybrid symbolic
near-square schematic with a target aspect ratio between 1.15 and 1.25, at
least 1500 by 1200 pixels, large readable labels, a central finite-boundary/QRF
motif, and explicit source-to-artifact-to-claim-gate flow. The cover audit also
checks that the image is referenced in the title-page preamble, remains
unnumbered in manuscript prose, is source-mapped, and has nontrivial caption
and alt-text metadata.

Current figure classes:

- hybrid symbolic cover graphical abstract and a three-figure QRF lead
  sequence: boundary-screen geometry, `b0`-`b5` channel-relabeling ledger, and
  invariance/policy-flow audit. These figures encode the source-paper,
  equation-registry, QRF screen, unchanged channel ledger, stochastic, quantum,
  claim-gate, evidence-ceiling, manuscript, and dashboard flow through arrows,
  boxes, direct labels, legends, and source-map rows;
- early-section conceptual figures that set up the QRF sector situation before
  the results: `qrf_sector_situation` (one shared boundary screen read through
  three sector lenses with vertical same-bit ties), `boundary_use_vs_ontology`
  (a stepwise permission diagram whose shared-bitstream, use, and blocked-ontology
  verdicts are bound to the indistinguishability audit's control flags), and `separation_prior_net_value`
  (the per-precision Bayesian-model-reduction lifecycle whose useful-to-dispensable
  crossing is derived from the sweep, not asserted);
- QRF sectorisation, reference-frame geometry, and
  boundary-indistinguishability panels retained as generated source-map support
  artifacts rather than repeated numbered manuscript figures;
- compact finite quantum scope summary in the main Results, with the technical
  quantum boundary-entropy landscape, CHSH contextuality witness, mixed-state
  entanglement audit, measurement-cover probability table, local-polytope
  audit, generic cover-polytope audit, CPTP channel-cost audit, dephasing
  panels, boundary-Hamiltonian qFEP dynamics, seeded quantum-trajectory
  unraveling and convergence, exact and sparse many-body boundary-screen
  sweeps, sheaf obstruction audit, QRF transformation and frame-covariance
  audits, empirical adapter provenance audit, and roadmap-readiness matrix
  restricted to the supplement by `manuscript_figure_placement_audit.json`;
- BMR free-energy decomposition and pruning phase diagram;
- simulation sensitivity heatmap over metacognitive access, prior precision, and
  observation noise;
- `pymdp` profile comparison with short labels, full-name profile legend, lower
  free-energy sign annotation, external action legend, posterior trajectory
  with perturbation markers, and a supplemental runtime-validation dashboard
  summarizing model normalization, trace recomputation, replay, runtime dependency, and
  profile-null robustness checks;
- single-trace criticality diagnostic and seeded stochastic criticality ensemble
  with null-control hatches and interval error bars;
- stochastic effect-size forest with bootstrap intervals, permutation/Holm
  metadata, and Cliff's-delta direction markers;
- BMR robustness resampling panels for free-energy sign stability and pruning
  intervals over observation-noise rows;
- quantum-trajectory convergence panels showing residuals across trajectory
  counts and a too-few-trajectories negative control;
- method assumption/failure map in the main Results as a falsification surface
  for model behavior, hard constraints, and evidence ceilings;
- claim-context evidence ladder in the main Results, grouping public claims by
  evidence class with scoped source-role bars, validation-gate markers, and
  blocked stronger-reading markers so support breadth is not mistaken for
  empirical strength;
- supplemental-only governance QA figures: scholarship coverage matrix,
  claim-support matrix, claim-source-validation graph, and visual semantic
  palette ledger. These audit support, validation, and color semantics; they do
  not add model behavior or empirical evidence, and
  `manuscript_figure_placement_audit.json` keeps them out of the main Results
  while requiring exactly one supplement embed for each;
- manuscript claim-audit panel;
- evidence-ceiling stress matrix grouped by claim class.
- formalism operation map for equations 1-14;
- static artifact dashboard under `output/dashboard/index.html` summarizing
  roadmap status, stochastic-engine status, manuscript-reference audits, claim
  ceilings, source maps, manifest coverage, and the validation dependency graph.
  The dashboard also renders an Argument Arc section that walks the no-self-evidence
  narrative from boundary screen to active-inference profile execution with each stage
  linked to its lead figure, presents the Visual QA counts from the style and
  legibility audits, and shows the figure list as a clickable gallery of
  `../figures/<id>.png` links rather than a static table.

The supplement must not reprint any PNG already used on the cover or in the
main paper. It may include supplemental-only audit visuals such as the equation
operation map and manuscript claim audit, plus source-map prose and tables.
The balanced quantum-placement rule is stricter: technical quantum/control PNGs
must be absent from the main Results, must appear in the supplemental quantum
audit section, and the main Results must use only
`finite_quantum_scope_summary.png` for that visual family.
The governance-placement rule is likewise strict: the scholarship coverage
matrix, claim-support matrix, claim-source-validation graph, and visual semantic
palette ledger are supplemental reproducibility/source-map figures, not main
Results figures.

Figures should not introduce unsupported claims. If a visual encodes a proxy,
the caption and manuscript prose must preserve that proxy boundary. Every
publication figure must include either an on-figure legend/colorbar or a
caption-level explanation of the color, line, marker, or edge encoding. Every
figure must also provide alt text and a source artifact that functions as a
machine-readable data-table alternative.
