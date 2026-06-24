# Method Inventory

| Path | Line | Kind | Name | Summary |
| --- | ---: | --- | --- | --- |
| src/formalism/claim_context.py | 76 | function | `_source_entries_by_key` | No docstring. |
| src/formalism/claim_context.py | 81 | function | `_support_rows_for_claim` | No docstring. |
| src/formalism/claim_context.py | 88 | function | `_sections_for_claim` | No docstring. |
| src/formalism/claim_context.py | 96 | function | `_role_rule` | No docstring. |
| src/formalism/claim_context.py | 165 | function | `_reader_claim_overclaims` | No docstring. |
| src/formalism/claim_context.py | 178 | function | `build_claim_context_ledger` | Build a reader-facing claim ledger from source, support, and ceiling artifacts. |
| src/formalism/claim_context.py | 319 | function | `write_claim_context_ledger` | Write claim context ledger JSON. |
| src/formalism/claim_redteam.py | 47 | function | `_load_json` | No docstring. |
| src/formalism/claim_redteam.py | 55 | function | `_composed_manuscript_anchors` | No docstring. |
| src/formalism/claim_redteam.py | 64 | function | `_figure_ids` | No docstring. |
| src/formalism/claim_redteam.py | 68 | function | `_source_themes_by_claim` | No docstring. |
| src/formalism/claim_redteam.py | 76 | function | `_binding_resolves` | No docstring. |
| src/formalism/claim_redteam.py | 80 | function | `_reader_overclaims` | No docstring. |
| src/formalism/claim_redteam.py | 92 | function | `build_claim_redteam_audit` | No docstring. |
| src/formalism/claim_redteam.py | 279 | function | `write_claim_redteam_audit` | No docstring. |
| src/formalism/equations.py | 38 | function | `_operational_status` | No docstring. |
| src/formalism/equations.py | 43 | class | `EquationSurrogate` | Metadata for one paper equation and its software status. |
| src/formalism/equations.py | 54 | function | `as_dict` | Serialize equation metadata. |
| src/formalism/equations.py | 74 | function | `equation_registry` | Return the complete equation registry for paper equations 1-14. |
| src/formalism/equations.py | 94 | function | `_softmax` | No docstring. |
| src/formalism/equations.py | 100 | function | `_deployment_free_energy` | Return a deterministic finite free energy F = complexity - accuracy for a deployment. |
| src/formalism/equations.py | 112 | function | `_strict_superset_witness` | Return whether some non-admissible deployment in ``roster`` beats every dual one. |
| src/formalism/equations.py | 131 | function | `_containment_audit` | Derive eqs 13-14 solution-set containment from measured free energy. |
| src/formalism/equations.py | 160 | function | `render_equation_crosswalk` | Render a paper-to-software equation crosswalk from the formalism registry. |
| src/formalism/equations.py | 209 | function | `evaluate_equation_surrogates` | Evaluate deterministic finite surrogates for all computable equations. |
| src/formalism/governance.py | 108 | function | `build_method_assumption_ledger` | Return the method assumption ledger. |
| src/formalism/governance.py | 122 | function | `build_method_negative_control_inventory` | Return method-to-negative-control coverage rows. |
| src/formalism/governance.py | 146 | function | `write_method_governance_artifacts` | Write method governance JSON artifacts. |
| src/formalism/manuscript.py | 151 | function | `manuscript_fragment_text` | Concatenate source manuscript fragments for audit. |
| src/formalism/manuscript.py | 160 | function | `citation_keys_in_text` | Extract Pandoc citation keys from manuscript Markdown text. |
| src/formalism/manuscript.py | 166 | function | `_forbidden_hits` | Find positive blocked-domain claims, exempting sentences that negate the claim. |
| src/formalism/manuscript.py | 190 | function | `_sentences_with_locations` | No docstring. |
| src/formalism/manuscript.py | 201 | function | `classify_sentence_intensity` | No docstring. |
| src/formalism/manuscript.py | 241 | function | `build_manuscript_claim_intensity_audit` | Audit strong claim verbs at sentence level. |
| src/formalism/manuscript.py | 261 | function | `build_manuscript_claim_audit` | Audit manuscript citations, public claim mentions, and positive-efficacy wording. |
| src/formalism/manuscript.py | 287 | function | `write_manuscript_claim_audit` | Write the manuscript claim audit artifact. |
| src/formalism/manuscript.py | 296 | function | `write_manuscript_claim_intensity_audit` | Write the sentence-level manuscript claim-intensity audit. |
| src/formalism/models.py | 13 | class | `BoundaryScreen` | Finite boundary screen carrying binary observation channels. |
| src/formalism/models.py | 20 | function | `default` | Create a named finite boundary screen. |
| src/formalism/models.py | 24 | function | `validate` | Reject malformed boundary screens. |
| src/formalism/models.py | 31 | function | `all_bitstrings` | Enumerate all binary strings over the boundary. |
| src/formalism/models.py | 43 | class | `QRFDeployment` | A QRF deployment as a semantic sector label per boundary channel. |
| src/formalism/models.py | 51 | function | `validate` | Check deployment dimensions and parameter ranges. |
| src/formalism/models.py | 62 | function | `is_dual` | Return whether the deployment preserves only self/env labels. |
| src/formalism/models.py | 67 | function | `flexibility` | Operational flexibility score used by the finite surrogate. |
| src/formalism/models.py | 72 | function | `as_dict` | Serialize deployment to JSON-compatible data. |
| src/formalism/models.py | 85 | class | `Sectorisation` | Grouped view of a QRF deployment. |
| src/formalism/models.py | 92 | function | `from_deployment` | Build sector-to-channel mapping from channel labels. |
| src/formalism/models.py | 99 | function | `as_dict` | Serialize grouped sectorisation. |
| src/formalism/models.py | 105 | class | `SeparationPrior` | Structural prior that restricts admissible deployments to dual sectorisations. |
| src/formalism/models.py | 111 | function | `complexity_cost` | Return a positive complexity cost for the structural prior. |
| src/formalism/models.py | 115 | function | `admissible` | Restrict deployments if the prior remains enforced. |
| src/formalism/models.py | 122 | function | `complexity_kl` | Return the categorical KL complexity D_KL[Q(s) || P(s|m)] for eq 11. |
| src/formalism/models.py | 146 | function | `vfe_noise_insufficient_learning` | Decompose a finite VFE-style surprise into noise and insufficient learning (eq 6). |
| src/formalism/models.py | 180 | class | `FreeEnergyTerms` | Finite free-energy decomposition used by the surrogate. |
| src/formalism/models.py | 188 | function | `from_distributions` | Build VFE terms from finite categorical distributions (eq 11 worked example). |
| src/formalism/models.py | 213 | function | `free_energy` | Compute F = complexity - accuracy + noise. |
| src/formalism/models.py | 217 | function | `as_dict` | Serialize terms. |
| src/formalism/models.py | 228 | class | `BMRComparison` | Bayesian model-reduction comparison between full and reduced models. |
| src/formalism/models.py | 235 | function | `delta_complexity` | Reduced-minus-full complexity. |
| src/formalism/models.py | 240 | function | `delta_accuracy` | Reduced-minus-full accuracy. |
| src/formalism/models.py | 245 | function | `delta_free_energy` | Delta F = Delta complexity - Delta accuracy, with noise folded into F. |
| src/formalism/models.py | 250 | function | `prunes_prior` | Return whether the reduced model is preferred. |
| src/formalism/models.py | 254 | function | `as_dict` | Serialize BMR comparison. |
| src/formalism/review_response_bmr.py | 11 | function | `bmr_comparison` | No docstring. |
| src/formalism/review_response_bmr.py | 37 | function | `crossing_for_prior` | No docstring. |
| src/formalism/review_response_bmr.py | 56 | function | `build_bmr_alternative_prior_audit` | No docstring. |
| src/formalism/review_response_common.py | 35 | function | `load_json` | No docstring. |
| src/formalism/review_response_common.py | 42 | function | `load_yaml` | No docstring. |
| src/formalism/review_response_common.py | 47 | function | `sha256` | No docstring. |
| src/formalism/review_response_common.py | 55 | function | `round_float` | No docstring. |
| src/formalism/review_response_common.py | 59 | function | `json_write` | No docstring. |
| src/formalism/review_response_common.py | 65 | function | `collect_numeric_results` | No docstring. |
| src/formalism/review_response_external.py | 9 | function | `review_response_rows` | No docstring. |
| src/formalism/review_response_external.py | 74 | function | `build_external_review_response_audit` | No docstring. |
| src/formalism/review_response_figures.py | 9 | function | `source_artifact_metadata` | No docstring. |
| src/formalism/review_response_figures.py | 61 | function | `build_figure_parameter_ledger` | No docstring. |
| src/formalism/review_response_qrf.py | 11 | function | `alias_labels` | No docstring. |
| src/formalism/review_response_qrf.py | 15 | function | `build_qrf_label_ablation_audit` | No docstring. |
| src/formalism/review_response_quantum.py | 13 | function | `context_signs` | No docstring. |
| src/formalism/review_response_quantum.py | 17 | function | `model_rows` | No docstring. |
| src/formalism/review_response_quantum.py | 21 | function | `expectation_from_rows` | No docstring. |
| src/formalism/review_response_quantum.py | 31 | function | `chsh_from_probabilities` | No docstring. |
| src/formalism/review_response_quantum.py | 35 | function | `independent_assignments` | No docstring. |
| src/formalism/review_response_quantum.py | 45 | function | `independent_probability_vector` | No docstring. |
| src/formalism/review_response_quantum.py | 56 | function | `independent_polytope_matrix` | No docstring. |
| src/formalism/review_response_quantum.py | 72 | function | `independent_polytope_fit` | No docstring. |
| src/formalism/review_response_quantum.py | 108 | function | `build_quantum_independent_crosscheck_audit` | No docstring. |
| src/formalism/review_response_release.py | 41 | function | `manifest_paths` | No docstring. |
| src/formalism/review_response_release.py | 46 | function | `release_support_paths` | No docstring. |
| src/formalism/review_response_release.py | 61 | function | `build_artifact_release_manifest` | No docstring. |
| src/formalism/review_response_release.py | 150 | function | `write_artifact_release_manifest` | No docstring. |
| src/formalism/review_response_writers.py | 14 | function | `write_review_response_artifacts` | No docstring. |
| src/formalism/scholarship.py | 58 | function | `load_scholarship_manifest` | Load the scholarship manifest. |
| src/formalism/scholarship.py | 64 | function | `bibliography_keys` | Return citation keys declared in the manuscript bibliography. |
| src/formalism/scholarship.py | 70 | function | `validate_scholarship_manifest` | Validate uniqueness, bibliography coverage, and claim-boundary fields. |
| src/formalism/scholarship.py | 117 | function | `build_scholarship_source_matrix` | Build a track-by-source matrix for scholarship coverage. |
| src/formalism/scholarship.py | 147 | function | `build_claim_support_audit` | Build a claim-by-source support audit from the scholarship manifest. |
| src/formalism/scholarship.py | 188 | function | `write_scholarship_source_matrix` | Write scholarship matrix JSON. |
| src/formalism/scholarship.py | 197 | function | `write_claim_support_audit` | Write claim support audit JSON. |
| src/formalism/source.py | 12 | function | `load_source_manifest` | Load the source manifest from the project. |
| src/formalism/source.py | 22 | function | `sha256_file` | Compute SHA-256 for a local file. |
| src/formalism/source.py | 31 | function | `verify_primary_source_hash` | Verify the attached PDF hash when the local source file is present. |
| src/formalism/source_fit.py | 182 | function | `_declared_section_anchors` | Return anchors declared by the sheaf manifest/tracks plus composed files. |
| src/formalism/source_fit.py | 205 | function | `build_source_argument_coverage_audit` | Build coverage rows tying source-paper themes to local sections, artifacts, and gates. |
| src/formalism/source_fit.py | 254 | function | `write_source_argument_coverage_audit` | Write the source-argument coverage audit artifact. |
| src/formalism/stress.py | 27 | function | `build_evidence_ceiling_audit` | Audit that every public claim declares limits, stressors, and future evidence. |
| src/formalism/stress.py | 89 | function | `write_evidence_ceiling_audit` | Write the evidence-ceiling stress audit. |
| src/gates/contracts.py | 29 | class | `ArtifactContract` | Machine-readable contract for a generated or declared artifact. |
| src/gates/contracts.py | 42 | function | `has_schema` | No docstring. |
| src/gates/contracts.py | 46 | function | `_load_yaml` | No docstring. |
| src/gates/contracts.py | 51 | function | `_schema_path_for` | No docstring. |
| src/gates/contracts.py | 60 | function | `artifact_contracts` | Build contracts from the manifest instead of a parallel expected-output list. |
| src/gates/contracts.py | 91 | function | `build_artifact_contract_registry` | Build a registry artifact for generated-output validation. |
| src/gates/contracts.py | 127 | function | `write_artifact_contract_registry` | Write the contract registry artifact. |
| src/gates/manuscript.py | 73 | function | `_png_dimensions` | No docstring. |
| src/gates/manuscript.py | 83 | function | `_manuscript_texts` | No docstring. |
| src/gates/manuscript.py | 91 | function | `_clean_ref` | No docstring. |
| src/gates/manuscript.py | 95 | function | `build_manuscript_reference_audit` | Audit composed manuscript section, figure, and equation references. |
| src/gates/manuscript.py | 140 | function | `_image_paths` | No docstring. |
| src/gates/manuscript.py | 147 | function | `build_figure_reuse_audit` | Audit that supplement figures do not duplicate main or cover visuals. |
| src/gates/manuscript.py | 176 | function | `build_figure_placement_audit` | Audit balanced main/supplement placement for technical and governance figures. |
| src/gates/manuscript.py | 228 | function | `build_cover_graphical_abstract_audit` | Audit the unnumbered graphical abstract cover image. |
| src/gates/manuscript.py | 283 | function | `write_manuscript_structure_audits` | Write manuscript reference, figure reuse, figure-placement, and cover graphic audits. |
| src/gates/roadmap.py | 92 | function | `_load_json` | No docstring. |
| src/gates/roadmap.py | 96 | function | `_normalise` | No docstring. |
| src/gates/roadmap.py | 100 | function | `_todo_records` | No docstring. |
| src/gates/roadmap.py | 140 | function | `_historical_backlog_rows` | No docstring. |
| src/gates/roadmap.py | 165 | function | `build_roadmap_todo_audit` | Build a fail-closed audit linking TODO rows to machine roadmap state. |
| src/gates/roadmap.py | 236 | function | `build_validation_dependency_graph` | Build an explicit dependency graph for artifacts, validators, figures, and render gates. |
| src/gates/roadmap.py | 559 | function | `write_roadmap_governance_artifacts` | Write roadmap/TODO and dependency-graph artifacts. |
| src/gates/validation.py | 365 | function | `_load_json` | No docstring. |
| src/gates/validation.py | 376 | function | `_exists` | No docstring. |
| src/gates/validation.py | 380 | function | `_release_file_fingerprints` | No docstring. |
| src/gates/validation.py | 392 | function | `_load_yaml` | No docstring. |
| src/gates/validation.py | 397 | function | `_model_from_audit_row` | No docstring. |
| src/gates/validation.py | 404 | function | `_pymdp_trace_math_ok` | No docstring. |
| src/gates/validation.py | 467 | function | `_pymdp_runtime_log_ok` | No docstring. |
| src/gates/validation.py | 500 | function | `_schema_check` | No docstring. |
| src/gates/validation.py | 509 | function | `_subsection_anchor_audit` | No docstring. |
| src/gates/validation.py | 562 | function | `validate_outputs` | Return named output checks. |
| src/gates/validation.py | 1813 | function | `write_validation_report` | Write validation report to output/reports. |
| src/gates/validation.py | 1829 | function | `_tracked_doc_paths` | Return the documentation files governed by the contract. |
| src/gates/validation.py | 1836 | function | `check_documentation_contract` | Check project docs for stale identity, machine paths, orphans, and broken links. |
| src/practice/protocols.py | 8 | function | `practice_protocol_map` | Return bounded practice protocol mappings for software interfaces. |
| src/simulation/blackwell_ordering.py | 37 | function | `_bayes_error` | Bayes risk of the optimal decision rule under 0-1 loss: 1 - sum_o max_state p(state) p(o|state). |
| src/simulation/blackwell_ordering.py | 43 | function | `_relabel` | Invertible relabeling: permute the outcome columns (a reversible post-processing). |
| src/simulation/blackwell_ordering.py | 48 | function | `_garble` | Row-stochastic post-processing G; A' = A @ G. Lossy unless G is a permutation. |
| src/simulation/blackwell_ordering.py | 54 | function | `build_blackwell_bayes_risk_audit` | Finite Blackwell ordering surrogate with relabel-preserves and garble-degrades controls. |
| src/simulation/bmr.py | 16 | function | `compare_models` | Compare full and reduced models at one point in the finite sweep. |
| src/simulation/bmr.py | 33 | function | `run_bmr_sweep` | Run deterministic BMR sweep over prior precision and metacognitive access. |
| src/simulation/bmr.py | 61 | function | `write_bmr_sweep` | Write BMR sweep JSON and CSV artifacts. |
| src/simulation/classical_data_processing.py | 35 | function | `_mutual_information` | I(X;Y) in bits from a 2D joint distribution. |
| src/simulation/classical_data_processing.py | 47 | function | `_chain_informations` | Return (I(interior;external), I(blanket;external)) for the chain external -> blanket -> interior. |
| src/simulation/classical_data_processing.py | 63 | function | `build_classical_data_processing_audit` | Finite classical data-processing surrogate with a sufficiency-saturation discriminating control. |
| src/simulation/compassion_scope.py | 54 | function | `compassion_boundary_stream` | Return a finite boundary stream with heterogeneous per-channel action-contingency. |
| src/simulation/compassion_scope.py | 92 | function | `channel_influence` | Return a per-channel realised action-influence score in [0, 1]. |
| src/simulation/compassion_scope.py | 122 | function | `_precision_weights` | Return per-channel concern precision under the separation prior. |
| src/simulation/compassion_scope.py | 140 | function | `compute_scope_of_concern` | Return the finite self/non-self concern split for one deployment. |
| src/simulation/compassion_scope.py | 188 | function | `_is_monotone_increasing` | No docstring. |
| src/simulation/compassion_scope.py | 192 | function | `build_compassion_scope_audit` | Audit scope-of-concern widening across profiles, with separable controls for the two |
| src/simulation/criticality.py | 16 | function | `_entropy` | No docstring. |
| src/simulation/criticality.py | 23 | function | `branching_ratio` | Return the finite branching ratio sigma = descendants per ancestor over an activity series. |
| src/simulation/criticality.py | 46 | function | `avalanche_size_distribution` | Extract avalanche sizes from supra-threshold runs of an activity series. |
| src/simulation/criticality.py | 79 | function | `_power_law_vs_exponential_llr` | Return a finite per-sample log-likelihood ratio favoring a power-law over an exponential. |
| src/simulation/criticality.py | 101 | function | `criticality_signatures` | Bundle the measured criticality signatures and a DERIVED criticality index. |
| src/simulation/criticality.py | 118 | function | `_planted_geometric_activity` | Return a geometric activity series whose exact branching ratio is ``sigma``. |
| src/simulation/criticality.py | 123 | function | `branching_estimator_calibration` | Positive control: the branching estimator recovers a planted branching ratio. |
| src/simulation/criticality.py | 144 | function | `_activity_series` | Return a per-step boundary-channel activity series (count of channel flips). |
| src/simulation/criticality.py | 154 | function | `build_criticality_report` | Build a single-trace diagnostic retained for source-boundary continuity. |
| src/simulation/criticality.py | 188 | function | `_interval` | No docstring. |
| src/simulation/criticality.py | 201 | function | `_branching_by_run` | Reconstruct each run's observation activity and return its measured branching ratio. |
| src/simulation/criticality.py | 214 | function | `build_criticality_stochastic_ensemble` | Summarize seeded active-inference ensembles as simulated criticality indicators. |
| src/simulation/criticality.py | 267 | function | `_ci_disjoint` | True iff the real and null 95% confidence intervals for ``metric`` do not overlap. |
| src/simulation/emergence.py | 33 | function | `emergence_trajectory` | Build a boundary stream where a fraction ``empowerment`` of channels track the action. |
| src/simulation/emergence.py | 68 | function | `_mode_predictor_error` | Return the mean bit error of a per-channel mode predictor. |
| src/simulation/emergence.py | 91 | function | `score_factored_vs_unfactored` | Return the measured prediction errors of the factored and unfactored predictors. |
| src/simulation/emergence.py | 116 | function | `_window_error` | Mean bit error when the channels in ``self_set`` are action-conditioned, the rest marginal. |
| src/simulation/emergence.py | 123 | function | `_best_self_set` | Post-dual revision: action-condition a channel only when that MATERIALLY lowers its error. |
| src/simulation/emergence.py | 140 | function | `_run_revision_stream` | Run one rigid-vs-revising comparison over a (possibly) non-stationary boundary stream. |
| src/simulation/emergence.py | 186 | function | `build_ongoing_revision_audit` | Operationalize the post-dual agent's ongoing revision under non-stationarity (5.2/5.3). |
| src/simulation/emergence.py | 218 | function | `_action_shuffled_factored_advantage` | Mean factored advantage after permuting the action sequence relative to the observations. |
| src/simulation/emergence.py | 241 | function | `build_separation_prior_emergence_audit` | Audit when a factored self/env model buys predictive accuracy over an unfactored model. |
| src/simulation/interaction_information.py | 37 | function | `_conditional_mutual_information` | I(I;E|B) in bits for a joint indexed [internal, blanket, external]. |
| src/simulation/interaction_information.py | 55 | function | `_marginal_mutual_information` | I(I;E) in bits, marginalising out the blanket. |
| src/simulation/interaction_information.py | 68 | function | `_synergistic_xor_joint` | B = I XOR E with I, E independent and uniform: marginal I(I;E) = 0 exactly, I(I;E|B) = 1 bit. |
| src/simulation/interaction_information.py | 77 | function | `_redundant_screen_joint` | Common cause: B uniform, I and E each track B independently, so I _||_ E | B (a clean screen). |
| src/simulation/interaction_information.py | 89 | function | `_independent_null_joint` | All three variables independent and uniform: no structure, so II = 0. |
| src/simulation/interaction_information.py | 94 | function | `build_interaction_information_boundary_audit` | Finite interaction-information surrogate with synergy, redundancy, and null regimes. |
| src/simulation/markov_blanket.py | 60 | function | `_precision_from_edges` | No docstring. |
| src/simulation/markov_blanket.py | 68 | function | `_correlation_from_precision` | No docstring. |
| src/simulation/markov_blanket.py | 74 | function | `_partial_correlation` | No docstring. |
| src/simulation/markov_blanket.py | 81 | function | `_neighbors` | Markov blanket of ``nodes``: graph neighbors of the node set, excluding the set itself. |
| src/simulation/markov_blanket.py | 92 | function | `_f1` | No docstring. |
| src/simulation/markov_blanket.py | 105 | function | `_support_adjacency` | No docstring. |
| src/simulation/markov_blanket.py | 111 | function | `_marginal_recovers_blanket` | True iff some marginal-correlation threshold recovers the blanket of INTERNAL exactly. |
| src/simulation/markov_blanket.py | 122 | function | `_perturbation_ensemble` | Perturb the planted edge weights (preserving the structural internal-external zeros) and measure |
| src/simulation/markov_blanket.py | 152 | function | `build_markov_blanket_discovery_audit` | Recover a planted Markov boundary from conditional independence, invisible to the marginal. |
| src/simulation/pymdp_profiles.py | 31 | function | `_shannon_entropy` | Return the natural-log Shannon entropy of a probability vector (0 for a point mass). |
| src/simulation/pymdp_profiles.py | 39 | class | `ProfileSpec` | Profile-specific active-inference generative-model parameters. |
| src/simulation/pymdp_profiles.py | 49 | function | `softmax_negative` | Return a normalized softmax over negative values for policy selection. |
| src/simulation/pymdp_profiles.py | 56 | function | `normalize_probability` | Normalize a nonnegative probability vector and fail on zero mass. |
| src/simulation/pymdp_profiles.py | 65 | function | `_normalise_columns` | Normalize every column of a likelihood or transition matrix. |
| src/simulation/pymdp_profiles.py | 70 | function | `profile_specs` | Return the public finite QRF profile specifications. |
| src/simulation/pymdp_profiles.py | 80 | function | `_likelihood_matrix` | Create A matrix mapping hidden QRF state to observation cue. |
| src/simulation/pymdp_profiles.py | 89 | function | `_transition_tensor` | Create B tensor for stabilize, inspect, and release actions. |
| src/simulation/pymdp_profiles.py | 121 | function | `build_profile_generative_model` | Build explicit A/B/C/D arrays for one QRF profile. |
| src/simulation/pymdp_profiles.py | 141 | function | `expected_free_energy_values` | Compute finite expected-free-energy surrogates for every action. |
| src/simulation/pymdp_profiles.py | 146 | function | `expected_free_energy_terms` | Return risk/ambiguity/expected-free-energy terms for each action. |
| src/simulation/pymdp_profiles.py | 174 | function | `_agent_from_model` | Construct the pinned pymdp Agent from one explicit A/B/C/D model. |
| src/simulation/pymdp_profiles.py | 190 | function | `_array_payload` | Serialize an array with shape and rounded values for audit JSON. |
| src/simulation/pymdp_profiles.py | 198 | function | `_model_hash` | Hash rounded A/B/C/D arrays so model drift is visible in diagnostics. |
| src/simulation/pymdp_profiles.py | 208 | function | `_package_version` | Return the installed package version or an explicit not-installed marker. |
| src/simulation/pymdp_profiles.py | 216 | function | `_term_residuals` | Compute maximum saved-vs-recomputed residuals for EFE term fields. |
| src/simulation/pymdp_profiles.py | 229 | function | `build_generative_model_audit` | Audit profile-specific A/B/C/D arrays and their normalization. |
| src/simulation/pymdp_profiles.py | 266 | function | `_extract_state_posterior` | Flatten the latest pymdp state posterior into a one-dimensional vector. |
| src/simulation/pymdp_profiles.py | 272 | function | `_simulate_profile` | Run one deterministic profile trace and summarize its action choices. |
| src/simulation/pymdp_profiles.py | 343 | function | `run_policy_trace` | Run a deterministic multi-profile pymdp policy trace. |
| src/simulation/pymdp_profiles.py | 367 | function | `pymdp_runtime_dependency_check` | Verify the pinned pymdp runtime surface without asserting model validity. |
| src/simulation/pymdp_profiles.py | 409 | function | `pymdp_version_canary` | Compatibility wrapper for the runtime dependency check artifact. |
| src/simulation/pymdp_profiles.py | 414 | function | `run_profile_comparison` | Compare QRF profiles using a deterministic pymdp policy trace. |
| src/simulation/pymdp_profiles.py | 466 | function | `build_pymdp_runtime_diagnostics_log` | Build the four-layer runtime/model/trace/replay diagnostics log. |
| src/simulation/qrf_env.py | 20 | function | `default_deployments` | Return the three v1 QRF profiles. |
| src/simulation/qrf_env.py | 35 | function | `simulate_boundary_trajectory` | Generate deterministic boundary observations for finite profile comparison. |
| src/simulation/qrf_env.py | 65 | function | `_uniform_boundary_distribution` | No docstring. |
| src/simulation/qrf_env.py | 71 | function | `boundary_indistinguishability_audit` | Check that admissible QRF labels do not change boundary probabilities. |
| src/simulation/qrf_env.py | 106 | function | `boundary_channel_ledger` | Return the b0-b5 QRF channel ledger used by the relabeling figure and source-fit audits. |
| src/simulation/qrf_env.py | 173 | function | `score_deployment` | Score a deployment by deterministic prediction, flexibility, and scope. |
| src/simulation/quantum_estimation.py | 38 | function | `_density` | No docstring. |
| src/simulation/quantum_estimation.py | 42 | function | `_d_density` | No docstring. |
| src/simulation/quantum_estimation.py | 46 | function | `_symmetric_logarithmic_derivative` | SLD operator L solving rho L + L rho = 2 d_rho, via the eigenbasis spectral formula. |
| src/simulation/quantum_estimation.py | 59 | function | `_quantum_fisher_information` | QFI = Tr[d_rho L] with L the symmetric logarithmic derivative. |
| src/simulation/quantum_estimation.py | 64 | function | `_sld_optimal_axis` | Bloch axis of the SLD-eigenbasis measurement, which saturates the quantum Cramer-Rao bound. |
| src/simulation/quantum_estimation.py | 76 | function | `_classical_fisher_information` | Classical Fisher information of the projective measurement along ``axis`` (Bloch direction). |
| src/simulation/quantum_estimation.py | 86 | function | `_coherent_bloch` | No docstring. |
| src/simulation/quantum_estimation.py | 90 | function | `_coherent_d_bloch` | No docstring. |
| src/simulation/quantum_estimation.py | 94 | function | `_classical_bloch` | No docstring. |
| src/simulation/quantum_estimation.py | 98 | function | `_classical_d_bloch` | No docstring. |
| src/simulation/quantum_estimation.py | 102 | function | `build_quantum_cramer_rao_estimation_audit` | Finite quantum Cramer-Rao estimation surrogate with a coherent-vs-classical discriminating control. |
| src/simulation/quantum_estimation.py | 118 | function | `family_rows` | No docstring. |
| src/simulation/quantum_surrogates.py | 93 | function | `_state` | No docstring. |
| src/simulation/quantum_surrogates.py | 100 | function | `_density` | No docstring. |
| src/simulation/quantum_surrogates.py | 104 | function | `_reduced_first_qubit` | No docstring. |
| src/simulation/quantum_surrogates.py | 109 | function | `_reduced_second_qubit` | No docstring. |
| src/simulation/quantum_surrogates.py | 114 | function | `_entropy_bits` | No docstring. |
| src/simulation/quantum_surrogates.py | 121 | function | `_shannon_bits` | No docstring. |
| src/simulation/quantum_surrogates.py | 127 | function | `_local_rotation` | No docstring. |
| src/simulation/quantum_surrogates.py | 133 | function | `_rotated_density` | No docstring. |
| src/simulation/quantum_surrogates.py | 139 | function | `_chsh_max` | No docstring. |
| src/simulation/quantum_surrogates.py | 143 | function | `_chsh_contexts` | No docstring. |
| src/simulation/quantum_surrogates.py | 152 | function | `_joint_probability_rows` | No docstring. |
| src/simulation/quantum_surrogates.py | 171 | function | `_chsh_rows_for_model` | No docstring. |
| src/simulation/quantum_surrogates.py | 196 | function | `_chsh_value` | No docstring. |
| src/simulation/quantum_surrogates.py | 200 | function | `_normalization_errors` | No docstring. |
| src/simulation/quantum_surrogates.py | 209 | function | `_marginal` | No docstring. |
| src/simulation/quantum_surrogates.py | 220 | function | `_no_signaling_errors` | No docstring. |
| src/simulation/quantum_surrogates.py | 247 | function | `_deterministic_assignments` | No docstring. |
| src/simulation/quantum_surrogates.py | 257 | function | `_probability_vector` | No docstring. |
| src/simulation/quantum_surrogates.py | 268 | function | `_local_polytope_matrix` | No docstring. |
| src/simulation/quantum_surrogates.py | 283 | function | `_local_polytope_fit` | No docstring. |
| src/simulation/quantum_surrogates.py | 342 | function | `_bell_dephased_density` | No docstring. |
| src/simulation/quantum_surrogates.py | 351 | function | `_product_density` | No docstring. |
| src/simulation/quantum_surrogates.py | 357 | function | `_bell_state_vector` | No docstring. |
| src/simulation/quantum_surrogates.py | 364 | function | `_matrix_is_hermitian` | No docstring. |
| src/simulation/quantum_surrogates.py | 368 | function | `_lindblad_superoperator` | Return a column-vectorized Lindblad generator superoperator. |
| src/simulation/quantum_surrogates.py | 381 | function | `_evolve_density_lindblad` | No docstring. |
| src/simulation/quantum_surrogates.py | 388 | function | `_density_metrics` | No docstring. |
| src/simulation/quantum_surrogates.py | 409 | function | `_density_validity` | No docstring. |
| src/simulation/quantum_surrogates.py | 426 | function | `_partial_transpose_second_qubit` | No docstring. |
| src/simulation/quantum_surrogates.py | 431 | function | `_negativity` | No docstring. |
| src/simulation/quantum_surrogates.py | 438 | function | `_werner_state` | No docstring. |
| src/simulation/quantum_surrogates.py | 443 | function | `_partial_trace_pure_state` | No docstring. |
| src/simulation/quantum_surrogates.py | 452 | function | `_many_body_bell_pair_state` | No docstring. |
| src/simulation/quantum_surrogates.py | 464 | function | `_many_body_product_state` | No docstring. |
| src/simulation/quantum_surrogates.py | 476 | function | `_von_neumann_entropy_bits` | Return the von Neumann entropy of a density matrix in bits. |
| src/simulation/quantum_surrogates.py | 483 | function | `_env_bipartitions` | Enumerate non-trivial bipartitions of the environment qubits (deduplicated by lowest index). |
| src/simulation/quantum_surrogates.py | 497 | function | `build_internal_cut_unmeasurability_audit` | Generalise the no-self-evidence result to arbitrary internal boundaries (section 3.3). |
| src/simulation/quantum_surrogates.py | 517 | function | `env_state` | No docstring. |
| src/simulation/quantum_surrogates.py | 571 | function | `_scenario_probability_vector` | No docstring. |
| src/simulation/quantum_surrogates.py | 576 | function | `_measurement_assignments` | No docstring. |
| src/simulation/quantum_surrogates.py | 583 | function | `_generic_polytope_fit` | No docstring. |
| src/simulation/quantum_surrogates.py | 634 | function | `_pair_context_rows` | No docstring. |
| src/simulation/quantum_surrogates.py | 656 | function | `_no_disturbance_error` | No docstring. |
| src/simulation/quantum_surrogates.py | 674 | function | `_normalise_probability` | No docstring. |
| src/simulation/quantum_surrogates.py | 682 | function | `_kraus_cptp_error` | No docstring. |
| src/simulation/quantum_surrogates.py | 692 | function | `_apply_kraus_channel` | No docstring. |
| src/simulation/quantum_surrogates.py | 699 | function | `_swap_unitary_two_qubit` | No docstring. |
| src/simulation/quantum_surrogates.py | 709 | function | `_basis_permutation_for_unitary` | No docstring. |
| src/simulation/quantum_surrogates.py | 716 | function | `_dephasing_metric_row` | No docstring. |
| src/simulation/quantum_surrogates.py | 745 | function | `_row` | No docstring. |
| src/simulation/quantum_surrogates.py | 771 | function | `_basis_invariance_rows` | No docstring. |
| src/simulation/quantum_surrogates.py | 791 | function | `build_quantum_boundary_entropy` | Build finite two-qubit entropy, CHSH, and basis-invariance artifacts. |
| src/simulation/quantum_surrogates.py | 829 | function | `build_quantum_open_system_dynamics` | Build finite dephasing-channel dynamics for Bell and product controls. |
| src/simulation/quantum_surrogates.py | 886 | function | `build_quantum_measurement_contextuality` | Build a finite CHSH measurement-cover empirical model and controls. |
| src/simulation/quantum_surrogates.py | 948 | function | `build_qfep_boundary_hamiltonian_dynamics` | Build finite boundary-Hamiltonian Lindblad dynamics for the roadmap qFEP engine. |
| src/simulation/quantum_surrogates.py | 1032 | function | `_trace_distance` | No docstring. |
| src/simulation/quantum_surrogates.py | 1037 | function | `build_quantum_trajectory_unraveling` | Build seeded Monte Carlo wave-function trajectories for the finite Lindblad audit. |
| src/simulation/quantum_surrogates.py | 1167 | function | `build_many_body_boundary_screen_sweep` | Build a finite many-body boundary-screen sweep over subsystem cuts. |
| src/simulation/quantum_surrogates.py | 1227 | function | `build_sheaf_contextuality_obstruction_audit` | Build a finite general measurement-cover obstruction audit beyond CHSH only. |
| src/simulation/quantum_surrogates.py | 1293 | function | `build_sigma_contextuality_suppression_audit` | Operationalize the paper's claim that the separation prior suppresses contextuality (6.1). |
| src/simulation/quantum_surrogates.py | 1361 | function | `build_qrf_transformation_covariance_audit` | Build a finite probability-preserving QRF transformation covariance audit. |
| src/simulation/quantum_surrogates.py | 1425 | function | `build_empirical_adapter_provenance_audit` | Build a fail-closed empirical-adapter provenance audit with synthetic controls. |
| src/simulation/quantum_surrogates.py | 1521 | function | `build_arbitrary_two_qubit_entanglement_audit` | Build a mixed-state two-qubit entanglement audit with PPT/negativity controls. |
| src/simulation/quantum_surrogates.py | 1618 | function | `_ghz_vector` | No docstring. |
| src/simulation/quantum_surrogates.py | 1625 | function | `_w_vector` | No docstring. |
| src/simulation/quantum_surrogates.py | 1632 | function | `_product_ground_vector` | No docstring. |
| src/simulation/quantum_surrogates.py | 1638 | function | `_qudit_max_entangled_vector` | No docstring. |
| src/simulation/quantum_surrogates.py | 1645 | function | `_bell_pair_plus_ground_vector` | Three-qubit Bell pair on qubits 0,1 tensored with |0> on qubit 2 (an asymmetric fixture). |
| src/simulation/quantum_surrogates.py | 1653 | function | `_partial_transpose_dims` | No docstring. |
| src/simulation/quantum_surrogates.py | 1664 | function | `_bipartition_negativity` | No docstring. |
| src/simulation/quantum_surrogates.py | 1670 | function | `_density_validity_general` | No docstring. |
| src/simulation/quantum_surrogates.py | 1683 | function | `build_multipartite_witness_suite_audit` | Finite multipartite and higher-dimensional entanglement-witness suite (roadmap re-10). |
| src/simulation/quantum_surrogates.py | 1729 | function | `family` | No docstring. |
| src/simulation/quantum_surrogates.py | 1776 | function | `_state_to_mps` | No docstring. |
| src/simulation/quantum_surrogates.py | 1795 | function | `_mps_to_state` | No docstring. |
| src/simulation/quantum_surrogates.py | 1802 | function | `_truncated_mps_error` | No docstring. |
| src/simulation/quantum_surrogates.py | 1820 | function | `build_tensor_network_benchmark_audit` | Finite exact matrix-product-state benchmark with scaling and truncation controls (roadmap re-11). |
| src/simulation/quantum_surrogates.py | 1873 | function | `_partial_swap_unitary` | No docstring. |
| src/simulation/quantum_surrogates.py | 1878 | function | `build_collision_model_thermalization_audit` | Finite collision-model relaxation surrogate with a zero-coupling control (roadmap re-12). |
| src/simulation/quantum_surrogates.py | 1931 | function | `_no_signaling_table` | No docstring. |
| src/simulation/quantum_surrogates.py | 1944 | function | `_max_marginal_drift` | No docstring. |
| src/simulation/quantum_surrogates.py | 1957 | function | `build_no_signaling_scenario_library_audit` | Finite no-signaling / no-disturbance audit over a scenario library (roadmap re-9). |
| src/simulation/quantum_surrogates.py | 2012 | function | `_n_cycle_behavior_rows` | Build a no-disturbing n-cycle behavior: unbiased marginals, edge correlation E_i = correlation. |
| src/simulation/quantum_surrogates.py | 2033 | function | `build_n_cycle_contextuality_library_audit` | Finite n-cycle contextuality scenario library via noncontextual-polytope LP (roadmap re-9). |
| src/simulation/quantum_surrogates.py | 2082 | function | `_generic_chsh_probability_rows` | No docstring. |
| src/simulation/quantum_surrogates.py | 2104 | function | `build_general_measurement_cover_polytope_audit` | Build a reusable finite measurement-cover parser and polytope audit. |
| src/simulation/quantum_surrogates.py | 2187 | function | `build_thermodynamic_channel_cost_audit` | Build finite CPTP channel checks with entropy-change and Landauer summaries. |
| src/simulation/quantum_surrogates.py | 2264 | function | `build_sparse_boundary_screen_scaling_audit` | Build sparse exact many-body boundary-screen scaling diagnostics. |
| src/simulation/quantum_surrogates.py | 2338 | function | `build_qrf_frame_covariance_toy_audit` | Build a finite density/probability frame-covariance audit for QRF toy transforms. |
| src/simulation/quantum_surrogates.py | 2409 | function | `build_quantum_extension_roadmap` | Build the scoped roadmap from finite simulations to fuller evidence classes. |
| src/simulation/quantum_surrogates.py | 2569 | function | `build_quantum_roadmap_readiness_matrix` | Build a fail-closed readiness matrix for roadmap claims. |
| src/simulation/quantum_surrogates.py | 2702 | function | `future_readiness_row` | No docstring. |
| src/simulation/quantum_surrogates.py | 2778 | function | `write_quantum_artifacts` | Write quantum-boundary simulation and roadmap artifacts. |
| src/simulation/quantum_surrogates.py | 2893 | function | `_bloch_density` | Single-qubit density from a Bloch vector; norm < 1 guarantees full rank (finite relative entropy). |
| src/simulation/quantum_surrogates.py | 2899 | function | `_hermitian_log2` | Base-2 matrix logarithm via Hermitian eigendecomposition (0 * log 0 = 0 convention). |
| src/simulation/quantum_surrogates.py | 2906 | function | `_relative_entropy_bits` | Quantum relative entropy S(rho||sigma) in bits; sigma must be full rank for a finite value. |
| src/simulation/quantum_surrogates.py | 2912 | function | `_qubit_channel_kraus` | Kraus operators for canonical qubit channels parameterized by strength in [0, 1]. |
| src/simulation/quantum_surrogates.py | 2934 | function | `_apply_kraus` | No docstring. |
| src/simulation/quantum_surrogates.py | 2938 | function | `_kraus_trace_preserving_error` | No docstring. |
| src/simulation/quantum_surrogates.py | 2943 | function | `_kraus_choi_min_eigenvalue` | Minimum eigenvalue of the (unnormalized) Choi matrix; >= 0 iff the map is completely positive. |
| src/simulation/quantum_surrogates.py | 2956 | function | `_transpose_map_choi_min_eigenvalue` | Choi matrix of the transpose map is the SWAP operator; its minimum eigenvalue is -1 (not CP). |
| src/simulation/quantum_surrogates.py | 2964 | function | `_post_selected_density` | No docstring. |
| src/simulation/quantum_surrogates.py | 2970 | function | `build_data_processing_monotonicity_audit` | Finite qubit data-processing (monotonicity) surrogate for opacification as forgetting (roadmap re-15). |
| src/simulation/sensitivity.py | 17 | function | `_binary_entropy` | Return binary entropy in nats for an observation-noise probability. |
| src/simulation/sensitivity.py | 24 | function | `compare_sensitivity_point` | Evaluate one finite sensitivity point for the separation-prior reduction. |
| src/simulation/sensitivity.py | 66 | function | `build_sensitivity_grid` | Run the finite sensitivity grid over access, precision, and observation noise. |
| src/simulation/sensitivity.py | 101 | function | `write_sensitivity_grid` | Write sensitivity grid JSON and CSV artifacts. |
| src/simulation/statistical_robustness.py | 21 | function | `_load_json` | No docstring. |
| src/simulation/statistical_robustness.py | 25 | function | `_finite` | No docstring. |
| src/simulation/statistical_robustness.py | 29 | function | `_bootstrap_ci` | No docstring. |
| src/simulation/statistical_robustness.py | 48 | function | `_permutation_p_value` | No docstring. |
| src/simulation/statistical_robustness.py | 66 | function | `_cliffs_delta` | No docstring. |
| src/simulation/statistical_robustness.py | 73 | function | `_holm_adjust` | No docstring. |
| src/simulation/statistical_robustness.py | 85 | function | `build_stochastic_effect_size_audit` | Compare profile ensembles to null controls with deterministic resampling. |
| src/simulation/statistical_robustness.py | 170 | function | `build_bmr_robustness_resampling_audit` | Summarize BMR pruning robustness over observation-noise rows. |
| src/simulation/statistical_robustness.py | 240 | function | `build_quantum_trajectory_convergence_audit` | Check finite quantum-trajectory residuals across ensemble sizes. |
| src/simulation/statistical_robustness.py | 307 | function | `_synthetic_arm` | Run the effect-size machinery on two seeded normal samples with a known shift. |
| src/simulation/statistical_robustness.py | 335 | function | `build_effect_size_test_calibration_audit` | Positive control: verify the effect-size machinery rejects a known injected effect. |
| src/simulation/statistical_robustness.py | 383 | function | `build_statistical_robustness_audit` | Aggregate statistical robustness controls into one reader-facing artifact. |
| src/simulation/statistical_robustness.py | 413 | function | `write_statistical_robustness_artifacts` | Write statistical robustness artifacts from generated simulation outputs. |
| src/simulation/stochastic.py | 29 | function | `_categorical_sample` | No docstring. |
| src/simulation/stochastic.py | 33 | function | `_entropy` | No docstring. |
| src/simulation/stochastic.py | 40 | function | `_run_profile_once` | No docstring. |
| src/simulation/stochastic.py | 127 | function | `_interval` | No docstring. |
| src/simulation/stochastic.py | 140 | function | `_summaries_by_profile` | No docstring. |
| src/simulation/stochastic.py | 168 | function | `build_stochastic_policy_ensemble` | Run seeded stochastic active-inference ensembles and null controls. |
| src/visualizations/captions.py | 80 | function | `build_visual_caption_audit` | Audit figure captions and visual-encoding descriptions. |
| src/visualizations/captions.py | 116 | function | `write_visual_caption_audit` | Write visual-caption audit JSON. |
| src/visualizations/captions.py | 125 | function | `build_visual_accessibility_audit` | Audit accessibility metadata for source-mapped figures. |
| src/visualizations/captions.py | 165 | function | `write_visual_accessibility_audit` | Write visual-accessibility audit JSON. |
| src/visualizations/dashboard.py | 19 | function | `_load_json` | No docstring. |
| src/visualizations/dashboard.py | 25 | function | `_load_yaml` | No docstring. |
| src/visualizations/dashboard.py | 30 | function | `_escape` | No docstring. |
| src/visualizations/dashboard.py | 34 | function | `build_artifact_dashboard_payload` | No docstring. |
| src/visualizations/dashboard.py | 285 | function | `_table` | No docstring. |
| src/visualizations/dashboard.py | 294 | function | `_figure_link` | No docstring. |
| src/visualizations/dashboard.py | 301 | function | `_argument_arc_table` | No docstring. |
| src/visualizations/dashboard.py | 317 | function | `render_artifact_dashboard_html` | No docstring. |
| src/visualizations/dashboard.py | 541 | function | `write_artifact_dashboard` | No docstring. |
| src/visualizations/figures.py | 36 | function | `_load_json` | No docstring. |
| src/visualizations/figures.py | 40 | function | `_load_style` | No docstring. |
| src/visualizations/figures.py | 45 | function | `_enforce_readable_text` | No docstring. |
| src/visualizations/figures.py | 53 | function | `_empty_layout_telemetry` | No docstring. |
| src/visualizations/figures.py | 63 | function | `_bbox_overlap_area` | No docstring. |
| src/visualizations/figures.py | 69 | function | `_bbox_outside` | No docstring. |
| src/visualizations/figures.py | 78 | function | `_text_layout_categories` | No docstring. |
| src/visualizations/figures.py | 102 | function | `_visible_text_boxes` | No docstring. |
| src/visualizations/figures.py | 124 | function | `_legend_boxes` | No docstring. |
| src/visualizations/figures.py | 136 | function | `_pairwise_overlap_count` | No docstring. |
| src/visualizations/figures.py | 145 | function | `_measure_layout` | No docstring. |
| src/visualizations/figures.py | 188 | function | `_record_layout_telemetry` | No docstring. |
| src/visualizations/figures.py | 192 | function | `_layout_rect_for` | No docstring. |
| src/visualizations/figures.py | 210 | function | `_lift_low_figure_text` | No docstring. |
| src/visualizations/figures.py | 225 | function | `_wrap_axis_titles` | No docstring. |
| src/visualizations/figures.py | 233 | function | `_save` | No docstring. |
| src/visualizations/figures.py | 248 | function | `_fig_path` | No docstring. |
| src/visualizations/figures.py | 252 | function | `_sectorisation_map` | No docstring. |
| src/visualizations/figures.py | 287 | function | `_save_return` | No docstring. |
| src/visualizations/figures.py | 292 | function | `_save_fixed_return` | No docstring. |
| src/visualizations/figures.py | 303 | function | `_panel_label` | No docstring. |
| src/visualizations/figures.py | 317 | function | `_zero_centered_norm` | No docstring. |
| src/visualizations/figures.py | 329 | function | `_heatmap_text_color` | No docstring. |
| src/visualizations/figures.py | 335 | function | `_add_heatmap_cell_grid` | No docstring. |
| src/visualizations/figures.py | 342 | function | `_semantic_colors` | No docstring. |
| src/visualizations/figures.py | 365 | function | `_profile_label` | No docstring. |
| src/visualizations/figures.py | 369 | function | `_compact_axis_label` | No docstring. |
| src/visualizations/figures.py | 375 | function | `_profile_color` | No docstring. |
| src/visualizations/figures.py | 379 | function | `_graphical_abstract_cover` | No docstring. |
| src/visualizations/figures.py | 398 | function | `box` | No docstring. |
| src/visualizations/figures.py | 687 | function | `_qrf_sector_colors` | No docstring. |
| src/visualizations/figures.py | 699 | function | `_qrf_boundary_screen_geometry` | No docstring. |
| src/visualizations/figures.py | 872 | function | `_qrf_channel_relabeling_ledger` | No docstring. |
| src/visualizations/figures.py | 1037 | function | `_qrf_invariance_policy_flow` | No docstring. |
| src/visualizations/figures.py | 1144 | function | `_finite_quantum_scope_summary` | No docstring. |
| src/visualizations/figures.py | 1264 | function | `_binary_colorbar` | No docstring. |
| src/visualizations/figures.py | 1271 | function | `_binary_colorbar_unlabeled` | No docstring. |
| src/visualizations/figures.py | 1277 | function | `_boundary_audit` | No docstring. |
| src/visualizations/figures.py | 1325 | function | `_qrf_reference_frame_geometry` | No docstring. |
| src/visualizations/figures.py | 1520 | function | `_bmr_decomposition` | No docstring. |
| src/visualizations/figures.py | 1580 | function | `_bmr_phase_diagram` | No docstring. |
| src/visualizations/figures.py | 1648 | function | `_simulation_sensitivity_heatmap` | No docstring. |
| src/visualizations/figures.py | 1714 | function | `_quantum_boundary_entropy_landscape` | No docstring. |
| src/visualizations/figures.py | 1793 | function | `_quantum_contextuality_witness` | No docstring. |
| src/visualizations/figures.py | 1895 | function | `_quantum_measurement_contextuality_table` | No docstring. |
| src/visualizations/figures.py | 1998 | function | `_quantum_local_polytope_audit` | No docstring. |
| src/visualizations/figures.py | 2100 | function | `_quantum_open_system_dynamics` | No docstring. |
| src/visualizations/figures.py | 2156 | function | `_qfep_boundary_hamiltonian_dynamics` | No docstring. |
| src/visualizations/figures.py | 2214 | function | `_many_body_boundary_screen_sweep` | No docstring. |
| src/visualizations/figures.py | 2278 | function | `_sheaf_contextuality_obstruction_audit` | No docstring. |
| src/visualizations/figures.py | 2371 | function | `_qrf_transformation_covariance_audit` | No docstring. |
| src/visualizations/figures.py | 2435 | function | `_empirical_adapter_provenance_audit` | No docstring. |
| src/visualizations/figures.py | 2498 | function | `_arbitrary_two_qubit_entanglement_audit` | No docstring. |
| src/visualizations/figures.py | 2596 | function | `_general_measurement_cover_polytope_audit` | No docstring. |
| src/visualizations/figures.py | 2690 | function | `_thermodynamic_channel_cost_audit` | No docstring. |
| src/visualizations/figures.py | 2766 | function | `_sparse_boundary_screen_scaling_audit` | No docstring. |
| src/visualizations/figures.py | 2851 | function | `_qrf_frame_covariance_toy_audit` | No docstring. |
| src/visualizations/figures.py | 2955 | function | `_profile_comparison` | No docstring. |
| src/visualizations/figures.py | 3064 | function | `_posterior_trajectory` | No docstring. |
| src/visualizations/figures.py | 3138 | function | `_pymdp_runtime_validation_dashboard` | No docstring. |
| src/visualizations/figures.py | 3339 | function | `_criticality` | No docstring. |
| src/visualizations/figures.py | 3365 | function | `_criticality_stochastic_ensemble` | No docstring. |
| src/visualizations/figures.py | 3482 | function | `_criticality_signatures` | Measured criticality signatures: branching ratio per profile and avalanche sizes. |
| src/visualizations/figures.py | 3593 | function | `_compassion_scope_widening` | Scope-of-concern widening (precision driver) plus the active per-channel action-influence. |
| src/visualizations/figures.py | 3674 | function | `_practice_policy_scope_map` | Render practice protocols as model-intervention deltas with on-figure safety boundaries. |
| src/visualizations/figures.py | 3733 | function | `_separation_prior_emergence` | Factored vs unfactored predictor error across the empowerment grid (section 4.1). |
| src/visualizations/figures.py | 3788 | function | `_internal_cut_unmeasurability` | Internal-cut entropy (god's-eye) versus A's invariant accessible marginal (section 3.3). |
| src/visualizations/figures.py | 3850 | function | `_quantum_trajectory_unraveling` | No docstring. |
| src/visualizations/figures.py | 3946 | function | `_stochastic_effect_size_forest` | No docstring. |
| src/visualizations/figures.py | 4056 | function | `_bmr_robustness_resampling` | No docstring. |
| src/visualizations/figures.py | 4155 | function | `_quantum_trajectory_convergence` | No docstring. |
| src/visualizations/figures.py | 4216 | function | `_visual_semantic_palette_ledger` | No docstring. |
| src/visualizations/figures.py | 4324 | function | `_method_assumption_failure_map` | No docstring. |
| src/visualizations/figures.py | 4419 | function | `_claim_graph` | No docstring. |
| src/visualizations/figures.py | 4485 | function | `_scholarship_coverage` | No docstring. |
| src/visualizations/figures.py | 4525 | function | `_claim_support_matrix` | No docstring. |
| src/visualizations/figures.py | 4650 | function | `_manuscript_claim_audit` | No docstring. |
| src/visualizations/figures.py | 4687 | function | `_evidence_ceiling_stress_matrix` | No docstring. |
| src/visualizations/figures.py | 4768 | function | `_claim_context_evidence_ladder` | No docstring. |
| src/visualizations/figures.py | 4936 | function | `_formalism_operation_map` | No docstring. |
| src/visualizations/figures.py | 4968 | function | `_quantum_roadmap_readiness_matrix` | No docstring. |
| src/visualizations/figures.py | 5053 | function | `boundary_use_ontology_verdicts` | Derive the use/ontology lane verdicts from the indistinguishability audit flags. |
| src/visualizations/figures.py | 5079 | function | `separation_prior_lifecycle` | Derive the separation-prior net-value lifecycle from the BMR sweep. |
| src/visualizations/figures.py | 5103 | function | `_crosses` | No docstring. |
| src/visualizations/figures.py | 5128 | function | `_qrf_sector_situation` | Early-section sector situation: one shared screen read through three QRF lenses. |
| src/visualizations/figures.py | 5297 | function | `_boundary_use_vs_ontology` | Conceptual permission diagram: boundary use is licensed, boundary ontology is not. |
| src/visualizations/figures.py | 5323 | function | `badge` | No docstring. |
| src/visualizations/figures.py | 5338 | function | `wrapped` | No docstring. |
| src/visualizations/figures.py | 5397 | function | `lane` | No docstring. |
| src/visualizations/figures.py | 5542 | function | `_separation_prior_net_value` | Lifecycle synthesis: the separation prior's net value vs. metacognitive access, per precision. |
| src/visualizations/figures.py | 5662 | function | `_multipartite_witness_negativity` | Minimum bipartition negativity per fixture; separable false-positive controls sit at zero. |
| src/visualizations/figures.py | 5722 | function | `_tensor_network_scaling` | Two panels: MPS bond-dimension scaling and the bond-one truncation control. |
| src/visualizations/figures.py | 5788 | function | `_collision_model_relaxation` | Initial vs final trace distance to the ancilla per coupling; zero-coupling control unchanged. |
| src/visualizations/figures.py | 5842 | function | `_data_processing_monotonicity` | Three panels: the data-processing inequality and its two firing discriminating controls. |
| src/visualizations/figures.py | 5979 | function | `_markov_blanket_discovery` | Three panels: sparse precision support, dense marginal covariance, and the F1 recovery contrast. |
| src/visualizations/figures.py | 6079 | function | `_markov_axis_ticks` | No docstring. |
| src/visualizations/figures.py | 6085 | function | `_n_cycle_contextuality_panel` | Feasibility matrix over n-cycle behaviors; odd cycles are contextual, cross-checked vs 2-colorability. |
| src/visualizations/figures.py | 6162 | function | `generate_all_figures` | Generate all registered figures and write the source map. |
| src/visualizations/figures.py | 6433 | function | `_source_artifacts_for` | No docstring. |
| src/visualizations/integrity.py | 19 | function | `file_sha256` | Return the SHA-256 digest for a file. |
| src/visualizations/integrity.py | 28 | function | `_image_metrics` | No docstring. |
| src/visualizations/integrity.py | 46 | function | `_load_json` | No docstring. |
| src/visualizations/integrity.py | 50 | function | `build_figure_integrity_audit` | Build current hashes, dimensions, and source hashes for source-mapped figures. |
| src/visualizations/integrity.py | 120 | function | `write_figure_integrity_audit` | Write figure integrity audit JSON. |
| src/visualizations/integrity.py | 128 | function | `compare_figure_integrity` | Compare saved figure integrity metadata against current files. |
| src/visualizations/rendered_captions.py | 18 | function | `_figure_lookup` | No docstring. |
| src/visualizations/rendered_captions.py | 30 | function | `expand_markdown_figure_captions` | Replace short Markdown figure captions with source-of-truth captions. |
| src/visualizations/rendered_captions.py | 34 | function | `replace` | No docstring. |
| src/visualizations/rendered_captions.py | 45 | function | `_source_map_by_filename` | No docstring. |
| src/visualizations/rendered_captions.py | 53 | function | `build_rendered_figure_caption_audit_from_texts` | Audit the captions that will appear in composed manuscript Markdown. |
| src/visualizations/rendered_captions.py | 117 | function | `build_rendered_figure_caption_audit` | Build an audit over composed manuscript figure captions. |
| src/visualizations/rendered_captions.py | 128 | function | `write_rendered_figure_caption_audit` | Write rendered-caption audit JSON. |
| src/visualizations/style.py | 106 | function | `semantic_colors` | Return shared semantic colors. |
| src/visualizations/style.py | 111 | function | `render_contract_for` | Return render contract metadata for a figure. |
| src/visualizations/style.py | 118 | function | `_hex_to_rgb` | No docstring. |
| src/visualizations/style.py | 123 | function | `_relative_luminance` | No docstring. |
| src/visualizations/style.py | 124 | function | `transform` | No docstring. |
| src/visualizations/style.py | 131 | function | `contrast_ratio` | No docstring. |
| src/visualizations/style.py | 138 | function | `_palette_contrast_rows` | No docstring. |
| src/visualizations/style.py | 154 | function | `build_visual_style_audit` | Audit semantic roles and visual-contract metadata for figures. |
| src/visualizations/style.py | 195 | function | `_image_metrics` | No docstring. |
| src/visualizations/style.py | 209 | function | `build_figure_legibility_audit` | Audit image dimensions and declared render metadata for legibility. |
| src/visualizations/style.py | 263 | function | `write_visual_style_audits` | Write visual style and legibility audits. |
