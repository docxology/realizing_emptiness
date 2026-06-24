"""Project validation gates."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import yaml
import numpy as np
from jsonschema import Draft202012Validator

from formalism.review_response import build_artifact_release_manifest
from formalism.scholarship import validate_scholarship_manifest
from formalism.source import verify_primary_source_hash
from gates.contracts import build_artifact_contract_registry
from simulation.pymdp_profiles import expected_free_energy_terms
from visualizations.integrity import compare_figure_integrity


EXPECTED_DATA = [
    "output/data/formalism_registry.json",
    "output/data/equation_audit.json",
    "output/data/source_claim_crosswalk.json",
    "output/data/source_argument_coverage_audit.json",
    "output/data/qrf_boundary_indistinguishability.json",
    "output/data/qrf_boundary_channel_ledger.json",
    "output/data/bmr_sweep.json",
    "output/data/bmr_sweep.csv",
    "output/data/simulation_sensitivity_grid.json",
    "output/data/simulation_sensitivity_grid.csv",
    "output/data/quantum_boundary_entropy.json",
    "output/data/quantum_open_system_dynamics.json",
    "output/data/quantum_measurement_contextuality.json",
    "output/data/qfep_boundary_hamiltonian_dynamics.json",
    "output/data/quantum_trajectory_unraveling.json",
    "output/data/many_body_boundary_screen_sweep.json",
    "output/data/sheaf_contextuality_obstruction_audit.json",
    "output/data/qrf_transformation_covariance_audit.json",
    "output/data/empirical_adapter_provenance_audit.json",
    "output/data/arbitrary_two_qubit_entanglement_audit.json",
    "output/data/general_measurement_cover_polytope_audit.json",
    "output/data/thermodynamic_channel_cost_audit.json",
    "output/data/sparse_boundary_screen_scaling_audit.json",
    "output/data/qrf_frame_covariance_toy_audit.json",
    "output/data/quantum_extension_roadmap.json",
    "output/data/quantum_roadmap_readiness_matrix.json",
    "output/data/roadmap_todo_audit.json",
    "output/data/validation_dependency_graph.json",
    "output/data/artifact_contract_registry.json",
    "output/data/artifact_release_manifest.json",
    "output/data/external_review_response_audit.json",
    "output/data/figure_parameter_ledger.json",
    "output/data/qrf_label_ablation_audit.json",
    "output/data/quantum_independent_crosscheck_audit.json",
    "output/data/bmr_alternative_prior_audit.json",
    "output/data/sheaf_coverage_matrix.json",
    "output/data/method_assumption_ledger.json",
    "output/data/method_negative_control_inventory.json",
    "output/data/pymdp_profile_comparison.json",
    "output/data/pymdp_policy_trace.json",
    "output/data/pymdp_generative_model_audit.json",
    "output/data/pymdp_runtime_diagnostics_log.json",
    "output/data/stochastic_policy_ensemble.json",
    "output/data/criticality_stochastic_ensemble.json",
    "output/data/stochastic_effect_size_audit.json",
    "output/data/bmr_robustness_resampling_audit.json",
    "output/data/quantum_trajectory_convergence_audit.json",
    "output/data/effect_size_calibration_audit.json",
    "output/data/statistical_robustness_audit.json",
    "output/data/compassion_scope_audit.json",
    "output/data/separation_prior_emergence_audit.json",
    "output/data/internal_cut_unmeasurability_audit.json",
    "output/data/sigma_contextuality_suppression_audit.json",
    "output/data/ongoing_revision_audit.json",
    "output/data/multipartite_witness_suite_audit.json",
    "output/data/tensor_network_benchmark_audit.json",
    "output/data/collision_model_thermalization_audit.json",
    "output/data/no_signaling_scenario_library_audit.json",
    "output/data/n_cycle_contextuality_library_audit.json",
    "output/data/data_processing_monotonicity_audit.json",
    "output/data/markov_blanket_discovery_audit.json",
    "output/data/quantum_cramer_rao_estimation_audit.json",
    "output/data/interaction_information_boundary_audit.json",
    "output/data/blackwell_bayes_risk_audit.json",
    "output/data/classical_data_processing_audit.json",
    "output/data/practice_protocol_map.json",
    "output/data/figure_source_map.json",
    "output/data/figure_integrity_audit.json",
    "output/data/visual_caption_audit.json",
    "output/data/rendered_figure_caption_audit.json",
    "output/data/visual_accessibility_audit.json",
    "output/data/visual_style_audit.json",
    "output/data/figure_legibility_audit.json",
    "output/data/manuscript_reference_audit.json",
    "output/data/figure_reuse_audit.json",
    "output/data/manuscript_figure_placement_audit.json",
    "output/data/cover_graphical_abstract_audit.json",
    "output/data/manuscript_variables.json",
    "output/data/manuscript_claim_audit.json",
    "output/data/manuscript_claim_intensity_audit.json",
    "output/data/evidence_ceiling_audit.json",
    "output/data/scholarship_source_matrix.json",
    "output/data/claim_support_audit.json",
    "output/data/claim_context_ledger.json",
    "output/data/claim_redteam_audit.json",
    "output/data/artifact_dashboard_payload.json",
]

EXPECTED_REPORTS = [
    "output/reports/criticality_proxy_report.json",
]

EXPECTED_FIGURES = [
    "output/figures/graphical_abstract_cover.png",
    "output/figures/qrf_boundary_screen_geometry.png",
    "output/figures/qrf_channel_relabeling_ledger.png",
    "output/figures/qrf_invariance_policy_flow.png",
    "output/figures/qrf_sectorisation_map.png",
    "output/figures/boundary_indistinguishability.png",
    "output/figures/qrf_reference_frame_geometry.png",
    "output/figures/bmr_free_energy_decomposition.png",
    "output/figures/bmr_pruning_phase_diagram.png",
    "output/figures/simulation_sensitivity_heatmap.png",
    "output/figures/finite_quantum_scope_summary.png",
    "output/figures/quantum_boundary_entropy_landscape.png",
    "output/figures/quantum_contextuality_witness.png",
    "output/figures/quantum_measurement_contextuality_table.png",
    "output/figures/quantum_local_polytope_audit.png",
    "output/figures/quantum_open_system_dynamics.png",
    "output/figures/qfep_boundary_hamiltonian_dynamics.png",
    "output/figures/quantum_trajectory_unraveling.png",
    "output/figures/many_body_boundary_screen_sweep.png",
    "output/figures/sheaf_contextuality_obstruction_audit.png",
    "output/figures/qrf_transformation_covariance_audit.png",
    "output/figures/empirical_adapter_provenance_audit.png",
    "output/figures/arbitrary_two_qubit_entanglement_audit.png",
    "output/figures/general_measurement_cover_polytope_audit.png",
    "output/figures/thermodynamic_channel_cost_audit.png",
    "output/figures/sparse_boundary_screen_scaling_audit.png",
    "output/figures/qrf_frame_covariance_toy_audit.png",
    "output/figures/quantum_roadmap_readiness_matrix.png",
    "output/figures/pymdp_profile_comparison.png",
    "output/figures/posterior_trajectory.png",
    "output/figures/pymdp_runtime_validation_dashboard.png",
    "output/figures/criticality_proxy_panels.png",
    "output/figures/criticality_stochastic_ensemble.png",
    "output/figures/criticality_signatures.png",
    "output/figures/compassion_scope_widening.png",
    "output/figures/separation_prior_emergence.png",
    "output/figures/internal_cut_unmeasurability.png",
    "output/figures/practice_policy_scope_map.png",
    "output/figures/stochastic_effect_size_forest.png",
    "output/figures/bmr_robustness_resampling.png",
    "output/figures/quantum_trajectory_convergence.png",
    "output/figures/visual_semantic_palette_ledger.png",
    "output/figures/method_assumption_failure_map.png",
    "output/figures/claim_source_validation_graph.png",
    "output/figures/scholarship_coverage_matrix.png",
    "output/figures/claim_support_matrix.png",
    "output/figures/manuscript_claim_audit.png",
    "output/figures/evidence_ceiling_stress_matrix.png",
    "output/figures/claim_context_evidence_ladder.png",
    "output/figures/formalism_operation_map.png",
    "output/figures/qrf_sector_situation.png",
    "output/figures/boundary_use_vs_ontology.png",
    "output/figures/separation_prior_net_value.png",
    "output/figures/multipartite_witness_negativity.png",
    "output/figures/tensor_network_scaling.png",
    "output/figures/collision_model_relaxation.png",
    "output/figures/n_cycle_contextuality_panel.png",
    "output/figures/data_processing_monotonicity.png",
    "output/figures/markov_blanket_discovery.png",
]

EXPECTED_WEB = [
    "output/dashboard/index.html",
]

EXPECTED_SCHEMAS = [
    "schemas/artifact_manifest.schema.json",
    "schemas/source_manifest.schema.json",
    "schemas/formalism_registry.schema.json",
    "schemas/equation_audit.schema.json",
    "schemas/scholarship_manifest.schema.json",
    "schemas/scholarship_source_matrix.schema.json",
    "schemas/source_claim_crosswalk.schema.json",
    "schemas/source_argument_coverage_audit.schema.json",
    "schemas/qrf_boundary_indistinguishability.schema.json",
    "schemas/qrf_boundary_channel_ledger.schema.json",
    "schemas/bmr_sweep.schema.json",
    "schemas/claim_support_audit.schema.json",
    "schemas/manuscript_claim_audit.schema.json",
    "schemas/evidence_ceiling_audit.schema.json",
    "schemas/claim_context_ledger.schema.json",
    "schemas/claim_redteam_audit.schema.json",
    "schemas/figure_integrity_audit.schema.json",
    "schemas/visual_caption_audit.schema.json",
    "schemas/rendered_figure_caption_audit.schema.json",
    "schemas/visual_accessibility_audit.schema.json",
    "schemas/figure_source_map.schema.json",
    "schemas/simulation_sensitivity_grid.schema.json",
    "schemas/quantum_boundary_entropy.schema.json",
    "schemas/quantum_open_system_dynamics.schema.json",
    "schemas/quantum_measurement_contextuality.schema.json",
    "schemas/qfep_boundary_hamiltonian_dynamics.schema.json",
    "schemas/quantum_trajectory_unraveling.schema.json",
    "schemas/many_body_boundary_screen_sweep.schema.json",
    "schemas/sheaf_contextuality_obstruction_audit.schema.json",
    "schemas/qrf_transformation_covariance_audit.schema.json",
    "schemas/empirical_adapter_provenance_audit.schema.json",
    "schemas/arbitrary_two_qubit_entanglement_audit.schema.json",
    "schemas/general_measurement_cover_polytope_audit.schema.json",
    "schemas/thermodynamic_channel_cost_audit.schema.json",
    "schemas/sparse_boundary_screen_scaling_audit.schema.json",
    "schemas/qrf_frame_covariance_toy_audit.schema.json",
    "schemas/quantum_extension_roadmap.schema.json",
    "schemas/quantum_roadmap_readiness_matrix.schema.json",
    "schemas/roadmap_todo_audit.schema.json",
    "schemas/validation_dependency_graph.schema.json",
    "schemas/artifact_contract_registry.schema.json",
    "schemas/artifact_release_manifest.schema.json",
    "schemas/external_review_response_audit.schema.json",
    "schemas/figure_parameter_ledger.schema.json",
    "schemas/qrf_label_ablation_audit.schema.json",
    "schemas/quantum_independent_crosscheck_audit.schema.json",
    "schemas/bmr_alternative_prior_audit.schema.json",
    "schemas/sheaf_coverage_matrix.schema.json",
    "schemas/method_assumption_ledger.schema.json",
    "schemas/method_negative_control_inventory.schema.json",
    "schemas/artifact_dashboard_payload.schema.json",
    "schemas/pymdp_profile_comparison.schema.json",
    "schemas/pymdp_policy_trace.schema.json",
    "schemas/pymdp_generative_model_audit.schema.json",
    "schemas/pymdp_runtime_diagnostics_log.schema.json",
    "schemas/stochastic_policy_ensemble.schema.json",
    "schemas/criticality_stochastic_ensemble.schema.json",
    "schemas/stochastic_effect_size_audit.schema.json",
    "schemas/bmr_robustness_resampling_audit.schema.json",
    "schemas/quantum_trajectory_convergence_audit.schema.json",
    "schemas/effect_size_calibration_audit.schema.json",
    "schemas/statistical_robustness_audit.schema.json",
    "schemas/compassion_scope_audit.schema.json",
    "schemas/separation_prior_emergence_audit.schema.json",
    "schemas/internal_cut_unmeasurability_audit.schema.json",
    "schemas/sigma_contextuality_suppression_audit.schema.json",
    "schemas/ongoing_revision_audit.schema.json",
    "schemas/multipartite_witness_suite_audit.schema.json",
    "schemas/tensor_network_benchmark_audit.schema.json",
    "schemas/collision_model_thermalization_audit.schema.json",
    "schemas/no_signaling_scenario_library_audit.schema.json",
    "schemas/n_cycle_contextuality_library_audit.schema.json",
    "schemas/data_processing_monotonicity_audit.schema.json",
    "schemas/markov_blanket_discovery_audit.schema.json",
    "schemas/quantum_cramer_rao_estimation_audit.schema.json",
    "schemas/interaction_information_boundary_audit.schema.json",
    "schemas/blackwell_bayes_risk_audit.schema.json",
    "schemas/classical_data_processing_audit.schema.json",
    "schemas/manuscript_reference_audit.schema.json",
    "schemas/figure_reuse_audit.schema.json",
    "schemas/manuscript_figure_placement_audit.schema.json",
    "schemas/cover_graphical_abstract_audit.schema.json",
    "schemas/visual_style_audit.schema.json",
    "schemas/figure_legibility_audit.schema.json",
    "schemas/manuscript_claim_intensity_audit.schema.json",
    "schemas/practice_protocol_map.schema.json",
    "schemas/manuscript_variables.schema.json",
    "schemas/criticality_proxy_report.schema.json",
]

SCHEMA_TARGETS = [
    ("schemas/artifact_manifest.schema.json", "artifact_manifest.yaml", "yaml"),
    ("schemas/source_manifest.schema.json", "data/sources/source_manifest.yaml", "yaml"),
    ("schemas/formalism_registry.schema.json", "output/data/formalism_registry.json", "json"),
    ("schemas/equation_audit.schema.json", "output/data/equation_audit.json", "json"),
    ("schemas/scholarship_manifest.schema.json", "data/sources/scholarship_manifest.yaml", "yaml"),
    ("schemas/scholarship_source_matrix.schema.json", "output/data/scholarship_source_matrix.json", "json"),
    ("schemas/source_claim_crosswalk.schema.json", "output/data/source_claim_crosswalk.json", "json"),
    ("schemas/source_argument_coverage_audit.schema.json", "output/data/source_argument_coverage_audit.json", "json"),
    ("schemas/qrf_boundary_indistinguishability.schema.json", "output/data/qrf_boundary_indistinguishability.json", "json"),
    ("schemas/qrf_boundary_channel_ledger.schema.json", "output/data/qrf_boundary_channel_ledger.json", "json"),
    ("schemas/bmr_sweep.schema.json", "output/data/bmr_sweep.json", "json"),
    ("schemas/claim_support_audit.schema.json", "output/data/claim_support_audit.json", "json"),
    ("schemas/manuscript_claim_audit.schema.json", "output/data/manuscript_claim_audit.json", "json"),
    ("schemas/evidence_ceiling_audit.schema.json", "output/data/evidence_ceiling_audit.json", "json"),
    ("schemas/claim_context_ledger.schema.json", "output/data/claim_context_ledger.json", "json"),
    ("schemas/claim_redteam_audit.schema.json", "output/data/claim_redteam_audit.json", "json"),
    ("schemas/figure_integrity_audit.schema.json", "output/data/figure_integrity_audit.json", "json"),
    ("schemas/visual_caption_audit.schema.json", "output/data/visual_caption_audit.json", "json"),
    ("schemas/rendered_figure_caption_audit.schema.json", "output/data/rendered_figure_caption_audit.json", "json"),
    ("schemas/visual_accessibility_audit.schema.json", "output/data/visual_accessibility_audit.json", "json"),
    ("schemas/figure_source_map.schema.json", "output/data/figure_source_map.json", "json"),
    ("schemas/simulation_sensitivity_grid.schema.json", "output/data/simulation_sensitivity_grid.json", "json"),
    ("schemas/quantum_boundary_entropy.schema.json", "output/data/quantum_boundary_entropy.json", "json"),
    ("schemas/quantum_open_system_dynamics.schema.json", "output/data/quantum_open_system_dynamics.json", "json"),
    ("schemas/quantum_measurement_contextuality.schema.json", "output/data/quantum_measurement_contextuality.json", "json"),
    ("schemas/qfep_boundary_hamiltonian_dynamics.schema.json", "output/data/qfep_boundary_hamiltonian_dynamics.json", "json"),
    ("schemas/quantum_trajectory_unraveling.schema.json", "output/data/quantum_trajectory_unraveling.json", "json"),
    ("schemas/many_body_boundary_screen_sweep.schema.json", "output/data/many_body_boundary_screen_sweep.json", "json"),
    ("schemas/sheaf_contextuality_obstruction_audit.schema.json", "output/data/sheaf_contextuality_obstruction_audit.json", "json"),
    ("schemas/qrf_transformation_covariance_audit.schema.json", "output/data/qrf_transformation_covariance_audit.json", "json"),
    ("schemas/empirical_adapter_provenance_audit.schema.json", "output/data/empirical_adapter_provenance_audit.json", "json"),
    ("schemas/arbitrary_two_qubit_entanglement_audit.schema.json", "output/data/arbitrary_two_qubit_entanglement_audit.json", "json"),
    ("schemas/general_measurement_cover_polytope_audit.schema.json", "output/data/general_measurement_cover_polytope_audit.json", "json"),
    ("schemas/thermodynamic_channel_cost_audit.schema.json", "output/data/thermodynamic_channel_cost_audit.json", "json"),
    ("schemas/sparse_boundary_screen_scaling_audit.schema.json", "output/data/sparse_boundary_screen_scaling_audit.json", "json"),
    ("schemas/qrf_frame_covariance_toy_audit.schema.json", "output/data/qrf_frame_covariance_toy_audit.json", "json"),
    ("schemas/quantum_extension_roadmap.schema.json", "output/data/quantum_extension_roadmap.json", "json"),
    ("schemas/quantum_roadmap_readiness_matrix.schema.json", "output/data/quantum_roadmap_readiness_matrix.json", "json"),
    ("schemas/roadmap_todo_audit.schema.json", "output/data/roadmap_todo_audit.json", "json"),
    ("schemas/validation_dependency_graph.schema.json", "output/data/validation_dependency_graph.json", "json"),
    ("schemas/artifact_contract_registry.schema.json", "output/data/artifact_contract_registry.json", "json"),
    ("schemas/artifact_release_manifest.schema.json", "output/data/artifact_release_manifest.json", "json"),
    ("schemas/external_review_response_audit.schema.json", "output/data/external_review_response_audit.json", "json"),
    ("schemas/figure_parameter_ledger.schema.json", "output/data/figure_parameter_ledger.json", "json"),
    ("schemas/qrf_label_ablation_audit.schema.json", "output/data/qrf_label_ablation_audit.json", "json"),
    ("schemas/quantum_independent_crosscheck_audit.schema.json", "output/data/quantum_independent_crosscheck_audit.json", "json"),
    ("schemas/bmr_alternative_prior_audit.schema.json", "output/data/bmr_alternative_prior_audit.json", "json"),
    ("schemas/sheaf_coverage_matrix.schema.json", "output/data/sheaf_coverage_matrix.json", "json"),
    ("schemas/method_assumption_ledger.schema.json", "output/data/method_assumption_ledger.json", "json"),
    ("schemas/method_negative_control_inventory.schema.json", "output/data/method_negative_control_inventory.json", "json"),
    ("schemas/artifact_dashboard_payload.schema.json", "output/data/artifact_dashboard_payload.json", "json"),
    ("schemas/pymdp_profile_comparison.schema.json", "output/data/pymdp_profile_comparison.json", "json"),
    ("schemas/pymdp_policy_trace.schema.json", "output/data/pymdp_policy_trace.json", "json"),
    ("schemas/pymdp_generative_model_audit.schema.json", "output/data/pymdp_generative_model_audit.json", "json"),
    ("schemas/pymdp_runtime_diagnostics_log.schema.json", "output/data/pymdp_runtime_diagnostics_log.json", "json"),
    ("schemas/stochastic_policy_ensemble.schema.json", "output/data/stochastic_policy_ensemble.json", "json"),
    ("schemas/criticality_stochastic_ensemble.schema.json", "output/data/criticality_stochastic_ensemble.json", "json"),
    ("schemas/stochastic_effect_size_audit.schema.json", "output/data/stochastic_effect_size_audit.json", "json"),
    ("schemas/bmr_robustness_resampling_audit.schema.json", "output/data/bmr_robustness_resampling_audit.json", "json"),
    ("schemas/quantum_trajectory_convergence_audit.schema.json", "output/data/quantum_trajectory_convergence_audit.json", "json"),
    ("schemas/effect_size_calibration_audit.schema.json", "output/data/effect_size_calibration_audit.json", "json"),
    ("schemas/statistical_robustness_audit.schema.json", "output/data/statistical_robustness_audit.json", "json"),
    ("schemas/compassion_scope_audit.schema.json", "output/data/compassion_scope_audit.json", "json"),
    ("schemas/separation_prior_emergence_audit.schema.json", "output/data/separation_prior_emergence_audit.json", "json"),
    ("schemas/internal_cut_unmeasurability_audit.schema.json", "output/data/internal_cut_unmeasurability_audit.json", "json"),
    ("schemas/sigma_contextuality_suppression_audit.schema.json", "output/data/sigma_contextuality_suppression_audit.json", "json"),
    ("schemas/ongoing_revision_audit.schema.json", "output/data/ongoing_revision_audit.json", "json"),
    ("schemas/multipartite_witness_suite_audit.schema.json", "output/data/multipartite_witness_suite_audit.json", "json"),
    ("schemas/tensor_network_benchmark_audit.schema.json", "output/data/tensor_network_benchmark_audit.json", "json"),
    ("schemas/collision_model_thermalization_audit.schema.json", "output/data/collision_model_thermalization_audit.json", "json"),
    ("schemas/no_signaling_scenario_library_audit.schema.json", "output/data/no_signaling_scenario_library_audit.json", "json"),
    ("schemas/n_cycle_contextuality_library_audit.schema.json", "output/data/n_cycle_contextuality_library_audit.json", "json"),
    ("schemas/data_processing_monotonicity_audit.schema.json", "output/data/data_processing_monotonicity_audit.json", "json"),
    ("schemas/markov_blanket_discovery_audit.schema.json", "output/data/markov_blanket_discovery_audit.json", "json"),
    ("schemas/quantum_cramer_rao_estimation_audit.schema.json", "output/data/quantum_cramer_rao_estimation_audit.json", "json"),
    ("schemas/interaction_information_boundary_audit.schema.json", "output/data/interaction_information_boundary_audit.json", "json"),
    ("schemas/blackwell_bayes_risk_audit.schema.json", "output/data/blackwell_bayes_risk_audit.json", "json"),
    ("schemas/classical_data_processing_audit.schema.json", "output/data/classical_data_processing_audit.json", "json"),
    ("schemas/manuscript_reference_audit.schema.json", "output/data/manuscript_reference_audit.json", "json"),
    ("schemas/figure_reuse_audit.schema.json", "output/data/figure_reuse_audit.json", "json"),
    ("schemas/manuscript_figure_placement_audit.schema.json", "output/data/manuscript_figure_placement_audit.json", "json"),
    ("schemas/cover_graphical_abstract_audit.schema.json", "output/data/cover_graphical_abstract_audit.json", "json"),
    ("schemas/visual_style_audit.schema.json", "output/data/visual_style_audit.json", "json"),
    ("schemas/figure_legibility_audit.schema.json", "output/data/figure_legibility_audit.json", "json"),
    ("schemas/manuscript_claim_intensity_audit.schema.json", "output/data/manuscript_claim_intensity_audit.json", "json"),
    ("schemas/practice_protocol_map.schema.json", "output/data/practice_protocol_map.json", "json"),
    ("schemas/manuscript_variables.schema.json", "output/data/manuscript_variables.json", "json"),
    ("schemas/criticality_proxy_report.schema.json", "output/reports/criticality_proxy_report.json", "json"),
]


def _load_json(project_root: Path, relative: str) -> dict[str, Any]:
    # Fail-closed: a missing or unparseable gated artifact yields an empty payload so the gate
    # that reads it evaluates to False, rather than crashing the whole validator. The artifact's
    # own `exists:` / `schema_valid:` checks still report the underlying problem.
    try:
        payload = json.loads((project_root / relative).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _exists(project_root: Path, relative: str) -> bool:
    return (project_root / relative).exists()


def _release_file_fingerprints(payload: dict[str, Any]) -> dict[str, tuple[bool, str | None, int | None]]:
    return {
        str(row.get("path", "")): (
            bool(row.get("exists")),
            row.get("sha256") if isinstance(row.get("sha256"), str) else None,
            row.get("bytes") if isinstance(row.get("bytes"), int) else None,
        )
        for row in payload.get("files", [])
        if row.get("path")
    }


def _load_yaml(project_root: Path, relative: str) -> dict[str, Any]:
    with (project_root / relative).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _model_from_audit_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: np.asarray(row[key]["values"], dtype=float)
        for key in ("A", "B", "C", "D")
    }


def _pymdp_trace_math_ok(policy_trace: dict[str, Any], model_audit: dict[str, Any], *, tolerance: float = 5e-5) -> bool:
    models = {
        row["profile"]: _model_from_audit_row(row)
        for row in model_audit.get("rows", [])
    }
    state_labels = set(policy_trace.get("state_labels", []))
    observation_labels = set(policy_trace.get("observation_labels", []))
    action_labels = list(policy_trace.get("action_labels", []))
    action_label_set = set(action_labels)
    if not models or len(action_labels) < 3:
        return False
    for row in policy_trace.get("rows", []):
        model = models.get(row.get("profile"))
        if model is None:
            return False
        posterior = np.asarray(row.get("state_posterior", []), dtype=float)
        policy = np.asarray(row.get("policy_posterior", []), dtype=float)
        expected_free_energy = np.asarray(row.get("expected_free_energy", []), dtype=float)
        if posterior.shape != (3,) or policy.shape != (3,) or expected_free_energy.shape != (3,):
            return False
        if row.get("true_state") not in state_labels or row.get("observation_label") not in observation_labels:
            return False
        if row.get("selected_action") not in action_label_set:
            return False
        selected_index = int(row.get("selected_action_index", -1))
        if selected_index < 0 or selected_index >= len(action_labels) or action_labels[selected_index] != row.get("selected_action"):
            return False
        weighted = float(policy @ expected_free_energy)
        if abs(weighted - float(row.get("weighted_expected_free_energy", math.inf))) > 1e-7:
            return False
        computed_terms = expected_free_energy_terms(model, posterior)
        saved_terms = row.get("efe_terms", [])
        if len(saved_terms) != len(computed_terms):
            return False
        for saved_term, computed_term in zip(saved_terms, computed_terms, strict=True):
            for key in ("risk_proxy", "ambiguity_proxy", "efe_proxy"):
                if abs(float(saved_term[key]) - float(computed_term[key])) > tolerance:
                    return False
    return True


_REQUIRED_PYMDP_CONTROLS = frozenset(
    {
        "canary_ok",
        "canary_warnings_captured",
        "all_model_hashes_present",
        "all_models_normalized",
        "deterministic_replay_equal",
        "all_state_posteriors_normalized",
        "all_policy_posteriors_normalized",
        "weighted_expected_free_energy_recomputed",
        "efe_terms_rederived",
        "all_trace_labels_resolve",
        "all_selected_action_indices_match",
        "all_numeric_fields_finite",
        "perturbation_flags_present",
        "all_vfe_finite",
        "all_entropies_in_bounds",
        "empirical_prior_matches_library",
    }
)


def _pymdp_runtime_log_ok(runtime_log: dict[str, Any], policy_trace: dict[str, Any]) -> bool:
    controls = runtime_log.get("controls", {})
    summary = runtime_log.get("summary", {})
    replay = runtime_log.get("replay", {})
    row_count = len(runtime_log.get("rows", []))
    return (
        runtime_log.get("schema") == "realizing_emptiness.pymdp_runtime_diagnostics_log.v1"
        and runtime_log.get("all_controls_pass") is True
        and runtime_log.get("trace_row_count") == policy_trace.get("row_count") == row_count
        and runtime_log.get("runtime_versions", {}).get("inferactively_pymdp") == "1.0.3"
        and runtime_log.get("canary", {}).get("ok") is True
        and len(runtime_log.get("canary", {}).get("warnings", [])) >= 1
        and runtime_log.get("model_profile_count") == 3
        and len({row.get("sha256") for row in runtime_log.get("model_hashes", [])}) == 3
        and all(len(row.get("sha256", "")) == 64 for row in runtime_log.get("model_hashes", []))
        and replay.get("trace_rows_equal") is True
        and replay.get("profile_summaries_equal") is True
        and summary.get("max_state_posterior_norm_residual", 1.0) < 1e-5
        and summary.get("max_policy_posterior_norm_residual", 1.0) < 1e-5
        and summary.get("max_weighted_expected_free_energy_residual", 1.0) < 1e-7
        and summary.get("max_efe_term_residual", 1.0) < 1e-7
        and summary.get("perturbed_step_count", 0) > 0
        and _REQUIRED_PYMDP_CONTROLS <= set(controls)
        and all(controls.get(key) is True for key in controls)
        and all(controls.get(key) is True for key in _REQUIRED_PYMDP_CONTROLS)
        and all(row.get("trace_labels_resolve") is True for row in runtime_log.get("rows", []))
        and all(row.get("selected_action_index_matches") is True for row in runtime_log.get("rows", []))
        and all(row.get("posteriors_finite") is True for row in runtime_log.get("rows", []))
        and all(row.get("expected_free_energy_finite") is True for row in runtime_log.get("rows", []))
        and "not empirical" in runtime_log.get("claim_boundary", "")
    )


def _schema_check(project_root: Path, schema_relative: str, target_relative: str, kind: str) -> bool:
    if not _exists(project_root, schema_relative) or not _exists(project_root, target_relative):
        return False
    schema = _load_json(project_root, schema_relative)
    target = _load_json(project_root, target_relative) if kind == "json" else _load_yaml(project_root, target_relative)
    validator = Draft202012Validator(schema)
    return not list(validator.iter_errors(target))


def _subsection_anchor_audit(project_root: Path) -> dict[str, Any]:
    section_files = [
        "manuscript/01_introduction.md",
        "manuscript/02_methods.md",
        "manuscript/03_results.md",
        "manuscript/04_discussion.md",
        "manuscript/05_conclusion.md",
    ]
    generic_titles = {"qrf deployment", "validation", "visual evidence", "limitations", "results", "methods"}
    rows = []
    anchors = []
    weak_titles = []
    missing_anchors = []
    for relative in section_files:
        path = project_root / relative
        if not path.exists():
            continue
        for match in re.finditer(r"^##\s+(.+?)\s+\{#([^}]+)\}", path.read_text(encoding="utf-8"), flags=re.MULTILINE):
            title = match.group(1).strip()
            anchor = match.group(2).strip()
            words = re.findall(r"[A-Za-z0-9]+", title)
            row = {"file": relative, "title": title, "anchor": anchor, "word_count": len(words)}
            rows.append(row)
            anchors.append(anchor)
            if len(words) < 4 or title.lower() in generic_titles:
                weak_titles.append(row)
            if not anchor.startswith("sec:"):
                missing_anchors.append(row)
    duplicate_anchors = sorted(anchor for anchor in set(anchors) if anchors.count(anchor) > 1)
    required_reference_anchors = {
        "sec:methods-finite-qrf-boundary-screen",
        "sec:methods-roadmap-quantum-engines",
        "sec:results-finite-quantum-scope",
        "sec:supplement-finite-quantum-contextuality-audits",
        "sec:discussion-evidence-ceilings",
    }
    composed_text = "\n".join(
        (project_root / relative).read_text(encoding="utf-8")
        for relative in section_files
        if (project_root / relative).exists()
    )
    missing_references = sorted(anchor for anchor in required_reference_anchors if f"@{anchor}" not in composed_text)
    return {
        "row_count": len(rows),
        "rows": rows,
        "duplicate_anchors": duplicate_anchors,
        "weak_titles": weak_titles,
        "missing_anchors": missing_anchors,
        "missing_references": missing_references,
        "ok": bool(rows) and not duplicate_anchors and not weak_titles and not missing_anchors and not missing_references,
    }


def validate_outputs(project_root: Path) -> dict[str, bool]:
    """Return named output checks."""
    checks: dict[str, bool] = {}
    checks["source_hash"] = verify_primary_source_hash(project_root)["ok"]
    for relative in EXPECTED_DATA + EXPECTED_REPORTS + EXPECTED_FIGURES + EXPECTED_WEB + EXPECTED_SCHEMAS:
        checks[f"exists:{relative}"] = _exists(project_root, relative)
    artifact_manifest = _load_yaml(project_root, "artifact_manifest.yaml")
    artifacts = artifact_manifest.get("artifacts", [])
    artifact_ids = [artifact.get("id") for artifact in artifacts]
    checks["artifact_manifest_schema"] = artifact_manifest.get("schema") == "realizing_emptiness.artifact_manifest.v1"
    checks["artifact_ids_unique"] = len(artifact_ids) == len(set(artifact_ids)) and all(isinstance(item, str) for item in artifact_ids)
    checks["artifact_paths_exist"] = all(_exists(project_root, artifact.get("path", "")) for artifact in artifacts)
    manifest_paths = {artifact.get("path", "") for artifact in artifacts}
    expected_paths = set(EXPECTED_DATA + EXPECTED_REPORTS + EXPECTED_FIGURES + EXPECTED_WEB)
    checks["artifact_manifest_covers_expected_outputs"] = expected_paths <= manifest_paths
    generated_paths = {
        str(path.relative_to(project_root))
        for folder in (project_root / "output" / "data", project_root / "output" / "reports", project_root / "output" / "figures")
        if folder.exists()
        for path in folder.iterdir()
        if path.is_file()
    }
    generated_paths.discard("output/reports/validation_report.json")
    generated_paths.discard("output/reports/output_statistics.json")
    generated_paths.discard("output/reports/output_statistics.txt")
    checks["generated_outputs_manifested"] = generated_paths <= manifest_paths
    for schema_relative, target_relative, kind in SCHEMA_TARGETS:
        checks[f"schema_valid:{target_relative}"] = _schema_check(project_root, schema_relative, target_relative, kind)
    saved_contract_registry = _load_json(project_root, "output/data/artifact_contract_registry.json")
    current_contract_registry = build_artifact_contract_registry(project_root)
    checks["artifact_contract_registry_ok"] = (
        saved_contract_registry.get("schema") == "realizing_emptiness.artifact_contract_registry.v1"
        and saved_contract_registry.get("all_controls_pass") is True
        and current_contract_registry.get("all_controls_pass") is True
        and saved_contract_registry.get("contract_count") == len(artifacts) == current_contract_registry.get("contract_count")
        and {row.get("path") for row in saved_contract_registry.get("rows", [])} == manifest_paths
        and {row.get("schema_path") for row in saved_contract_registry.get("rows", []) if row.get("schema_path")} <= set(EXPECTED_SCHEMAS)
        and "not empirical" in saved_contract_registry.get("claim_boundary", "")
    )
    release_manifest = _load_json(project_root, "output/data/artifact_release_manifest.json")
    current_release_manifest = build_artifact_release_manifest(project_root)
    release_controls = release_manifest.get("controls", {})
    current_release_controls = current_release_manifest.get("controls", {})
    checks["artifact_release_manifest_hashes_current"] = (
        release_manifest.get("artifact_count") == current_release_manifest.get("artifact_count")
        and release_manifest.get("file_count") == current_release_manifest.get("file_count")
        and _release_file_fingerprints(release_manifest) == _release_file_fingerprints(current_release_manifest)
    )
    checks["artifact_release_manifest_ok"] = (
        release_manifest.get("schema") == "realizing_emptiness.artifact_release_manifest.v1"
        and release_manifest.get("release_scope") == "local_private_artifact_bundle_not_public_release"
        and release_manifest.get("public_publication_performed") is False
        and release_manifest.get("all_controls_pass") is True
        and current_release_manifest.get("all_controls_pass") is True
        and release_controls.get("all_files_exist") is True
        and current_release_controls.get("all_files_exist") is True
        and release_controls.get("all_hashes_present") is True
        and release_controls.get("uv_lock_included") is True
        and release_controls.get("source_manifests_included") is True
        and release_controls.get("source_tree_included") is True
        and release_controls.get("schemas_included") is True
        and release_controls.get("tests_included") is True
        and release_controls.get("manuscript_sources_included") is True
        and release_controls.get("docs_included") is True
        and release_controls.get("rerun_scripts_included") is True
        and release_controls.get("public_publication_not_claimed") is True
        and checks["artifact_release_manifest_hashes_current"] is True
        and "output/data/artifact_release_manifest.json" in release_manifest.get("excluded_self_from_hashes", [])
        and "not public independent reproduction" in release_manifest.get("claim_boundary", "")
    )
    review_response = _load_json(project_root, "output/data/external_review_response_audit.json")
    review_controls = review_response.get("controls", {})
    review_statuses = {row.get("recommendation_id"): row.get("response_status") for row in review_response.get("rows", [])}
    checks["external_review_response_audit_ok"] = (
        review_response.get("schema") == "realizing_emptiness.external_review_response_audit.v1"
        and review_response.get("all_controls_pass") is True
        and review_controls.get("all_local_delta_rows_have_evidence") is True
        and review_controls.get("required_local_deltas_present") is True
        and review_controls.get("public_reproduction_blocked_not_completed") is True
        and review_response.get("missing_evidence") == []
        and review_statuses.get("public_independent_reproduction") == "blocked_external_publication"
        and "not empirical" in review_response.get("claim_boundary", "")
    )
    scholarship = validate_scholarship_manifest(project_root)
    checks["scholarship_manifest_ok"] = scholarship.get("ok") is True and scholarship.get("entry_count", 0) >= 12
    required_tracks = {"paper_source", "qfep", "qrf", "bmr", "pymdp", "criticality", "compassion_proxy", "practice_protocols"}
    checks["scholarship_track_coverage"] = required_tracks <= set(scholarship.get("track_counts", {}))
    equation = _load_json(project_root, "output/data/equation_audit.json")
    checks["equation_count_14"] = equation.get("equation_count") == 14 and equation.get("all_equations_mapped") is True
    qrf = _load_json(project_root, "output/data/qrf_boundary_indistinguishability.json")
    checks["qrf_indistinguishable"] = qrf.get("all_admissible_distributions_equal") is True
    checks["qrf_negative_control"] = qrf.get("negative_control_fails") is True
    qrf_ledger = _load_json(project_root, "output/data/qrf_boundary_channel_ledger.json")
    qrf_ledger_rows = qrf_ledger.get("rows", [])
    checks["qrf_boundary_channel_ledger_ok"] = (
        qrf_ledger.get("schema") == "realizing_emptiness.qrf_boundary_channel_ledger.v1"
        and qrf_ledger.get("channel_count") == 6
        and qrf_ledger.get("profile_count") == 3
        and [row.get("channel_id") for row in qrf_ledger_rows] == [f"b{index}" for index in range(6)]
        and qrf_ledger.get("all_controls_pass") is True
        and qrf_ledger.get("controls", {}).get("all_evidence_objects_invariant") is True
        and qrf_ledger.get("controls", {}).get("all_profiles_have_sector_labels") is True
        and qrf_ledger.get("controls", {}).get("source_equations_7_to_10_declared") is True
        and qrf_ledger.get("controls", {}).get("negative_control_fails") is True
        and all(row.get("source_equation_links") == ["eq:7", "eq:8", "eq:9", "eq:10"] for row in qrf_ledger_rows)
        and all("b" in row.get("invariant_evidence_object", "") for row in qrf_ledger_rows)
        and "not empirical" in qrf_ledger.get("claim_boundary", "")
        and "not ontological" in qrf_ledger.get("claim_boundary", "")
    )
    qrf_label_ablation = _load_json(project_root, "output/data/qrf_label_ablation_audit.json")
    qrf_label_controls = qrf_label_ablation.get("controls", {})
    checks["qrf_label_ablation_audit_ok"] = (
        qrf_label_ablation.get("schema") == "realizing_emptiness.qrf_label_ablation_audit.v1"
        and qrf_label_ablation.get("channel_count") == 6
        and qrf_label_ablation.get("all_controls_pass") is True
        and qrf_label_controls.get("neutral_alias_map_declared") is True
        and qrf_label_controls.get("neutral_renaming_preserves_structure") is True
        and qrf_label_controls.get("structure_changing_control_fails") is True
        and qrf_label_ablation.get("structure_changing_control", {}).get("preserved") is False
        and {"self", "env", "body", "world", "other", "care"} <= set(qrf_label_ablation.get("alias_map", {}))
        and "not empirical" in qrf_label_ablation.get("claim_boundary", "")
    )
    bmr = _load_json(project_root, "output/data/bmr_sweep.json")
    checks["bmr_pruning_edges"] = bmr.get("any_pruning") is True and bmr.get("high_access_prunes") is True
    bmr_alternative = _load_json(project_root, "output/data/bmr_alternative_prior_audit.json")
    bmr_alternative_controls = bmr_alternative.get("controls", {})
    checks["bmr_alternative_prior_audit_ok"] = (
        bmr_alternative.get("schema") == "realizing_emptiness.bmr_alternative_prior_audit.v1"
        and bmr_alternative.get("all_controls_pass") is True
        and bmr_alternative_controls.get("baseline_family_included") is True
        and bmr_alternative_controls.get("log_compressed_family_included") is True
        and bmr_alternative_controls.get("convex_access_family_included") is True
        and bmr_alternative_controls.get("all_verdicts_measured") is True
        and bmr_alternative_controls.get("high_access_pruning_remains_bounded") is True
        and bmr_alternative_controls.get("weakest_prior_crossings_measured") is True
        and bmr_alternative_controls.get("at_least_one_crossing_shifts_vs_baseline") is True
        and all(row.get("verdict") in {"prune", "keep"} for row in bmr_alternative.get("rows", []))
        and "not empirical" in bmr_alternative.get("claim_boundary", "")
    )
    sensitivity = _load_json(project_root, "output/data/simulation_sensitivity_grid.json")
    checks["simulation_sensitivity_grid_ok"] = (
        sensitivity.get("schema") == "realizing_emptiness.simulation_sensitivity_grid.v1"
        and sensitivity.get("row_count") == len(sensitivity.get("access_grid", []))
        * len(sensitivity.get("precision_grid", []))
        * len(sensitivity.get("noise_grid", []))
        and sensitivity.get("all_rows_boundary_safe") is True
        and "not empirical" in sensitivity.get("claim_boundary", "")
        and all(row.get("qrf_indistinguishability_holds") is True for row in sensitivity.get("rows", []))
        and 0.0 <= sensitivity.get("pruning_rate", -1.0) <= 1.0
    )
    quantum = _load_json(project_root, "output/data/quantum_boundary_entropy.json")
    quantum_rows = quantum.get("rows", [])
    quantum_controls = quantum.get("controls", {})
    checks["quantum_boundary_entropy_ok"] = (
        quantum.get("schema") == "realizing_emptiness.quantum_boundary_entropy.v1"
        and quantum.get("row_count") == len(quantum.get("theta_grid", [])) == len(quantum_rows)
        and quantum.get("basis_invariance_row_count") == len(quantum.get("theta_grid", [])) * len(quantum.get("rotation_grid", []))
        and quantum.get("all_controls_pass") is True
        and quantum_controls.get("product_entropy_zero") is True
        and quantum_controls.get("bell_entropy_one") is True
        and quantum_controls.get("basis_entropy_invariant") is True
        and quantum.get("max_basis_entropy_drift_bits", 1.0) < 1e-9
        and "not empirical" in quantum.get("claim_boundary", "")
        and "not a full qFEP" in quantum.get("claim_boundary", "")
    )
    checks["quantum_contextuality_witness_ok"] = (
        quantum.get("local_chsh_bound") == 2.0
        and abs(quantum.get("tsirelson_bound", 0.0) - 2.0 * math.sqrt(2.0)) < 1e-9
        and quantum.get("max_observed_chsh", 0.0) > 2.8
        and quantum.get("max_contextual_fraction", 0.0) > 0.99
        and quantum_controls.get("product_chsh_local") is True
        and quantum_controls.get("bell_chsh_toward_tsirelson") is True
        and quantum_rows[0].get("bell_violation_predicate") is False
        and quantum_rows[-1].get("bell_violation_predicate") is True
    )
    contextuality = _load_json(project_root, "output/data/quantum_measurement_contextuality.json")
    contextuality_controls = contextuality.get("controls", {})
    local_polytope = {
        row.get("model"): row
        for row in contextuality.get("local_polytope", {}).get("fits", [])
    }
    checks["quantum_measurement_contextuality_ok"] = (
        contextuality.get("schema") == "realizing_emptiness.quantum_measurement_contextuality.v1"
        and contextuality.get("row_count") == 32
        and contextuality.get("context_count") == 4
        and contextuality.get("model_count") == 2
        and contextuality.get("all_controls_pass") is True
        and contextuality.get("max_normalization_error", 1.0) < 1e-10
        and contextuality.get("max_no_signaling_error", 1.0) < 1e-10
        and contextuality.get("bell_chsh", 0.0) > 2.8
        and abs(contextuality.get("bell_chsh", 0.0) - contextuality.get("tsirelson_bound", 1.0)) < 1e-9
        and contextuality.get("product_control_chsh", 3.0) <= contextuality.get("local_chsh_bound", 2.0) + 1e-9
        and contextuality.get("contextual_fraction", 0.0) > 0.99
        and contextuality_controls.get("joint_probabilities_normalized") is True
        and contextuality_controls.get("joint_probabilities_nonnegative") is True
        and contextuality_controls.get("no_signaling_marginals_match") is True
        and contextuality_controls.get("bell_chsh_exceeds_local_bound") is True
        and contextuality_controls.get("product_control_respects_local_bound") is True
        and contextuality_controls.get("product_control_local_polytope_feasible") is True
        and contextuality_controls.get("bell_model_local_polytope_infeasible") is True
        and contextuality_controls.get("bell_model_positive_polytope_residual") is True
        and contextuality.get("local_polytope", {}).get("assignment_count") == 16
        and local_polytope.get("product_control", {}).get("feasible") is True
        and local_polytope.get("product_control", {}).get("min_l1_residual", 1.0) < 1e-8
        and local_polytope.get("bell_measurement_cover", {}).get("feasible") is False
        and local_polytope.get("bell_measurement_cover", {}).get("min_l1_residual", 0.0) > 0.1
        and "not empirical" in contextuality.get("claim_boundary", "")
        and "not a full sheaf-obstruction proof" in contextuality.get("claim_boundary", "")
    )
    quantum_crosscheck = _load_json(project_root, "output/data/quantum_independent_crosscheck_audit.json")
    quantum_crosscheck_controls = quantum_crosscheck.get("controls", {})
    checks["quantum_independent_crosscheck_audit_ok"] = (
        quantum_crosscheck.get("schema") == "realizing_emptiness.quantum_independent_crosscheck_audit.v1"
        and quantum_crosscheck.get("all_controls_pass") is True
        and quantum_crosscheck_controls.get("product_local_crosscheck") is True
        and quantum_crosscheck_controls.get("bell_tsirelson_crosscheck") is True
        and quantum_crosscheck_controls.get("product_polytope_feasible_independent") is True
        and quantum_crosscheck_controls.get("bell_polytope_infeasible_independent") is True
        and quantum_crosscheck_controls.get("perturbed_expected_value_control_fails") is True
        and quantum_crosscheck_controls.get("independent_assignment_count_16") is True
        and abs(quantum_crosscheck.get("computed", {}).get("tsirelson_bound", 0.0) - 2.0 * math.sqrt(2.0)) < 1e-9
        and "not empirical" in quantum_crosscheck.get("claim_boundary", "")
    )
    dynamics = _load_json(project_root, "output/data/quantum_open_system_dynamics.json")
    dynamics_rows = dynamics.get("rows", [])
    dynamics_controls = dynamics.get("controls", {})
    bell_rows = [row for row in dynamics_rows if row.get("state_label") == "bell_dephased"]
    product_rows = [row for row in dynamics_rows if row.get("state_label") == "product_control"]
    checks["quantum_open_system_dynamics_ok"] = (
        dynamics.get("schema") == "realizing_emptiness.quantum_open_system_dynamics.v1"
        and dynamics.get("row_count") == 2 * len(dynamics.get("time_grid", [])) * len(dynamics.get("decoherence_rate_grid", []))
        and dynamics.get("all_controls_pass") is True
        and dynamics.get("max_trace_error", 1.0) < 1e-10
        and dynamics.get("min_eigenvalue", -1.0) > -1e-10
        and dynamics.get("max_global_entropy_bits", 0.0) > 0.95
        and dynamics.get("max_observed_chsh", 0.0) > 2.8
        and dynamics.get("min_observed_chsh", 0.0) == 2.0
        and dynamics_controls.get("trace_preserved") is True
        and dynamics_controls.get("positive_semidefinite") is True
        and dynamics_controls.get("product_control_stable") is True
        and dynamics_controls.get("bell_entropy_non_decreasing_under_dephasing") is True
        and dynamics_controls.get("bell_chsh_decays_under_dephasing") is True
        and dynamics_controls.get("bell_mutual_information_non_increasing") is True
        and bool(bell_rows)
        and bool(product_rows)
        and "not empirical" in dynamics.get("claim_boundary", "")
        and "not a full qFEP" in dynamics.get("claim_boundary", "")
    )
    qfep_dynamics = _load_json(project_root, "output/data/qfep_boundary_hamiltonian_dynamics.json")
    qfep_controls = qfep_dynamics.get("controls", {})
    strongest_rate = max(qfep_dynamics.get("decoherence_rate_grid", [0.0]))
    qfep_strong_rows = [
        row for row in qfep_dynamics.get("rows", []) if abs(row.get("decoherence_rate", 0.0) - strongest_rate) < 1e-8
    ]
    checks["qfep_boundary_hamiltonian_dynamics_ok"] = (
        qfep_dynamics.get("schema") == "realizing_emptiness.qfep_boundary_hamiltonian_dynamics.v1"
        and qfep_dynamics.get("row_count") == len(qfep_dynamics.get("time_grid", [])) * len(qfep_dynamics.get("decoherence_rate_grid", []))
        and qfep_dynamics.get("all_controls_pass") is True
        and qfep_dynamics.get("max_trace_error", 1.0) < 1e-9
        and qfep_dynamics.get("min_eigenvalue", -1.0) > -1e-9
        and qfep_dynamics.get("max_entropy_production_bits", 0.0) > 0.5
        and qfep_controls.get("hamiltonian_hermitian") is True
        and qfep_controls.get("trace_preserved") is True
        and qfep_controls.get("positive_semidefinite") is True
        and qfep_controls.get("strongest_rate_entropy_non_decreasing") is True
        and qfep_controls.get("strongest_rate_mutual_information_contracts") is True
        and qfep_controls.get("all_negative_controls_fail_safely") is True
        and bool(qfep_strong_rows)
        and qfep_strong_rows[0].get("global_entropy_bits", 0.0) < qfep_strong_rows[-1].get("global_entropy_bits", 0.0)
        and qfep_strong_rows[0].get("mutual_information_bits", 0.0) > qfep_strong_rows[-1].get("mutual_information_bits", 0.0)
        and "not empirical" in qfep_dynamics.get("claim_boundary", "")
        and "not a physical qFEP" in qfep_dynamics.get("claim_boundary", "")
    )
    trajectory_unraveling = _load_json(project_root, "output/data/quantum_trajectory_unraveling.json")
    trajectory_controls = trajectory_unraveling.get("controls", {})
    gamma_zero_jumps = [
        row.get("jump_count", -1)
        for row in trajectory_unraveling.get("jump_count_rows", [])
        if abs(row.get("decoherence_rate", 1.0)) < 1e-12
    ]
    checks["quantum_trajectory_unraveling_ok"] = (
        trajectory_unraveling.get("schema") == "realizing_emptiness.quantum_trajectory_unraveling.v1"
        and trajectory_unraveling.get("all_controls_pass") is True
        and trajectory_unraveling.get("row_count") == len(trajectory_unraveling.get("time_grid", [])) * len(trajectory_unraveling.get("decoherence_rate_grid", []))
        and trajectory_unraveling.get("jump_count_row_count") == trajectory_unraveling.get("trajectory_count") * len(trajectory_unraveling.get("decoherence_rate_grid", []))
        and trajectory_unraveling.get("max_norm_drift", 1.0) < 1e-10
        and trajectory_unraveling.get("max_trace_error", 1.0) < 1e-10
        and trajectory_unraveling.get("min_eigenvalue", -1.0) > -1e-10
        and trajectory_unraveling.get("max_trace_distance_to_exact", 1.0) < 0.16
        and trajectory_controls.get("norm_preserved") is True
        and trajectory_controls.get("ensemble_trace_preserved") is True
        and trajectory_controls.get("ensemble_positive_semidefinite") is True
        and trajectory_controls.get("gamma_zero_has_no_jumps") is True
        and trajectory_controls.get("reconstructs_exact_lindblad_within_tolerance") is True
        and trajectory_controls.get("invalid_controls_fail_safely") is True
        and gamma_zero_jumps
        and all(count == 0 for count in gamma_zero_jumps)
        and all(row.get("passes") is True for row in trajectory_unraveling.get("invalid_controls", []))
        and "not empirical" in trajectory_unraveling.get("claim_boundary", "")
        and "not a physical qFEP" in trajectory_unraveling.get("claim_boundary", "")
    )
    many_body = _load_json(project_root, "output/data/many_body_boundary_screen_sweep.json")
    many_body_controls = many_body.get("controls", {})
    entangled_cut_rows = [row for row in many_body.get("rows", []) if row.get("state_label") == "cross_boundary_bell_pairs"]
    separable_cut_rows = [row for row in many_body.get("rows", []) if row.get("state_label") == "separable_product_control"]
    checks["many_body_boundary_screen_sweep_ok"] = (
        many_body.get("schema") == "realizing_emptiness.many_body_boundary_screen_sweep.v1"
        and many_body.get("row_count") == many_body.get("cut_count") * many_body.get("state_count")
        and many_body.get("all_controls_pass") is True
        and many_body_controls.get("observer_cut_has_max_entropy") is True
        and many_body_controls.get("partition_sensitivity_present") is True
        and many_body_controls.get("separable_controls_zero_entropy") is True
        and many_body_controls.get("random_cut_not_labeled_observer_evidence") is True
        and max(row.get("reduced_entropy_bits", 0.0) for row in entangled_cut_rows) >= 3.0
        and max(row.get("reduced_entropy_bits", 0.0) for row in separable_cut_rows) < 1e-9
        and not any(row.get("observer_boundary_candidate") for row in many_body.get("rows", []) if row.get("cut_class") == "negative_control_random_cut")
        and "not empirical" in many_body.get("claim_boundary", "")
    )
    sheaf = _load_json(project_root, "output/data/sheaf_contextuality_obstruction_audit.json")
    sheaf_rows = {row.get("id"): row for row in sheaf.get("rows", [])}
    sheaf_controls = sheaf.get("controls", {})
    checks["sheaf_contextuality_obstruction_audit_ok"] = (
        sheaf.get("schema") == "realizing_emptiness.sheaf_contextuality_obstruction_audit.v1"
        and sheaf.get("scenario_count", 0) >= 2
        and sheaf.get("all_controls_pass") is True
        and sheaf_controls.get("noncontextual_control_has_global_section") is True
        and sheaf_controls.get("parity_obstruction_has_no_global_section") is True
        and sheaf_controls.get("all_models_no_disturbing") is True
        and sheaf_controls.get("negative_control_returns_feasible") is True
        and sheaf_rows.get("noncontextual_triangle_control", {}).get("global_section_feasible") is True
        and sheaf_rows.get("parity_obstruction", {}).get("global_section_feasible") is False
        and sheaf_rows.get("parity_obstruction", {}).get("min_l1_residual", 0.0) > 0.5
        and "not empirical" in sheaf.get("claim_boundary", "")
    )
    qrf_transform = _load_json(project_root, "output/data/qrf_transformation_covariance_audit.json")
    qrf_transform_controls = qrf_transform.get("controls", {})
    transform_rows = qrf_transform.get("rows", [])
    checks["qrf_transformation_covariance_audit_ok"] = (
        qrf_transform.get("schema") == "realizing_emptiness.qrf_transformation_covariance_audit.v1"
        and qrf_transform.get("all_controls_pass") is True
        and qrf_transform_controls.get("all_admissible_probability_preserving") is True
        and qrf_transform_controls.get("all_admissible_covariant") is True
        and qrf_transform_controls.get("nonadmissible_maps_rejected") is True
        and all(row.get("accepted") is True and (row.get("expectation_covariance_error") or 0.0) < 1e-10 for row in transform_rows if row.get("admissible"))
        and all(row.get("accepted") is False for row in transform_rows if not row.get("admissible"))
        and "not empirical" in qrf_transform.get("claim_boundary", "")
    )
    empirical_adapter = _load_json(project_root, "output/data/empirical_adapter_provenance_audit.json")
    empirical_controls = empirical_adapter.get("controls", {})
    empirical_rows = empirical_adapter.get("rows", [])
    checks["empirical_adapter_provenance_audit_ok"] = (
        empirical_adapter.get("schema") == "realizing_emptiness.empirical_adapter_provenance_audit.v1"
        and empirical_adapter.get("all_controls_pass") is True
        and empirical_controls.get("unsourced_human_data_blocked") is True
        and empirical_controls.get("synthetic_demo_not_empirical_claim") is True
        and empirical_controls.get("placeholder_without_preprocessing_blocked") is True
        and empirical_controls.get("no_empirical_claims_allowed") is True
        and not any(row.get("allowed_for_empirical_claim") for row in empirical_rows)
        and any(row.get("allowed_for_software_demo") for row in empirical_rows if row.get("synthetic"))
        and all(row.get("decision") in {"blocked", "demo_only"} for row in empirical_rows)
        and "not empirical" in empirical_adapter.get("claim_boundary", "")
    )
    entanglement = _load_json(project_root, "output/data/arbitrary_two_qubit_entanglement_audit.json")
    entanglement_rows = {row.get("id"): row for row in entanglement.get("rows", [])}
    werner_rows = [row for row in entanglement.get("rows", []) if row.get("family") == "werner"]
    checks["arbitrary_two_qubit_entanglement_audit_ok"] = (
        entanglement.get("schema") == "realizing_emptiness.arbitrary_two_qubit_entanglement_audit.v1"
        and entanglement.get("all_controls_pass") is True
        and entanglement.get("case_count") == entanglement.get("row_count") == len(entanglement.get("rows", []))
        and entanglement.get("controls", {}).get("invalid_density_controls_rejected") is True
        and entanglement.get("controls", {}).get("werner_threshold_matches_ppt") is True
        and entanglement_rows.get("bell_state", {}).get("negativity", 0.0) > 0.49
        and all(row.get("negativity", 1.0) < 1e-10 for row in entanglement.get("rows", []) if row.get("family") == "separable_control")
        and any(row.get("entangled_by_ppt") for row in werner_rows)
        and any(not row.get("entangled_by_ppt") for row in werner_rows)
        and all(row.get("passes") is True for row in entanglement.get("invalid_density_controls", []))
        and "not empirical" in entanglement.get("claim_boundary", "")
    )
    cover_polytope = _load_json(project_root, "output/data/general_measurement_cover_polytope_audit.json")
    cover_rows = {row.get("id"): row for row in cover_polytope.get("rows", [])}
    checks["general_measurement_cover_polytope_audit_ok"] = (
        cover_polytope.get("schema") == "realizing_emptiness.general_measurement_cover_polytope_audit.v1"
        and cover_polytope.get("scenario_count") == 4
        and cover_polytope.get("all_controls_pass") is True
        and cover_rows.get("triangle_feasible_control", {}).get("global_section_feasible") is True
        and cover_rows.get("triangle_parity_obstruction", {}).get("global_section_feasible") is False
        and cover_rows.get("chsh_product_control", {}).get("global_section_feasible") is True
        and cover_rows.get("chsh_bell_obstruction", {}).get("global_section_feasible") is False
        and cover_polytope.get("controls", {}).get("all_rows_no_disturbing") is True
        and cover_rows.get("chsh_bell_obstruction", {}).get("min_l1_residual", 0.0) > 0.1
        and "not empirical" in cover_polytope.get("claim_boundary", "")
    )
    channel_cost = _load_json(project_root, "output/data/thermodynamic_channel_cost_audit.json")
    channel_rows = channel_cost.get("rows", [])
    erasure_mixed = [
        row for row in channel_rows if row.get("channel_id") == "erasure_to_zero" and row.get("state_id") != "pure_zero"
    ]
    checks["thermodynamic_channel_cost_audit_ok"] = (
        channel_cost.get("schema") == "realizing_emptiness.thermodynamic_channel_cost_audit.v1"
        and channel_cost.get("all_controls_pass") is True
        and channel_cost.get("row_count") == channel_cost.get("channel_count") * channel_cost.get("state_count")
        and channel_cost.get("controls", {}).get("all_declared_channels_cptp") is True
        and channel_cost.get("controls", {}).get("non_cptp_controls_rejected") is True
        and all(row.get("cptp_error", 1.0) < 1e-10 for row in channel_rows)
        and all(row.get("landauer_lower_bound_kbt", 0.0) > 0.0 for row in erasure_mixed)
        and all(row.get("passes") is True for row in channel_cost.get("invalid_channel_controls", []))
        and "not empirical" in channel_cost.get("claim_boundary", "")
    )
    sparse_screen = _load_json(project_root, "output/data/sparse_boundary_screen_scaling_audit.json")
    sparse_rows = sparse_screen.get("rows", [])
    observer_sparse = [
        row for row in sparse_rows if row.get("state_label") == "sparse_cross_boundary_bell_pairs" and row.get("cut_id") == "observer_half_cut"
    ]
    checks["sparse_boundary_screen_scaling_audit_ok"] = (
        sparse_screen.get("schema") == "realizing_emptiness.sparse_boundary_screen_scaling_audit.v1"
        and sparse_screen.get("all_controls_pass") is True
        and max(sparse_screen.get("qubit_counts", [0])) > 6
        and sparse_screen.get("controls", {}).get("observer_entropy_scales_with_qubit_count") is True
        and sparse_screen.get("controls", {}).get("separable_controls_zero_entropy") is True
        and sparse_screen.get("controls", {}).get("random_cuts_not_labeled_observer_evidence") is True
        and observer_sparse[0].get("reduced_entropy_bits", 0.0) < observer_sparse[-1].get("reduced_entropy_bits", 0.0)
        and observer_sparse[0].get("amplitude_density", 0.0) > observer_sparse[-1].get("amplitude_density", 1.0)
        and not any(row.get("observer_boundary_candidate") for row in sparse_rows if row.get("cut_class") == "negative_control_random_cut")
        and "not empirical" in sparse_screen.get("claim_boundary", "")
    )
    qrf_frame = _load_json(project_root, "output/data/qrf_frame_covariance_toy_audit.json")
    qrf_frame_rows = qrf_frame.get("rows", [])
    checks["qrf_frame_covariance_toy_audit_ok"] = (
        qrf_frame.get("schema") == "realizing_emptiness.qrf_frame_covariance_toy_audit.v1"
        and qrf_frame.get("all_controls_pass") is True
        and qrf_frame.get("base_density_validity", {}).get("valid_density_matrix") is True
        and all(row.get("accepted") is True for row in qrf_frame_rows if row.get("admissible"))
        and all(row.get("accepted") is False for row in qrf_frame_rows if not row.get("admissible"))
        and all(row.get("spectrum_drift", 1.0) < 1e-10 for row in qrf_frame_rows if row.get("admissible"))
        and all(row.get("reduced_entropy_multiset_drift_bits", 1.0) < 1e-10 for row in qrf_frame_rows if row.get("admissible"))
        and all(row.get("probability_spectrum_drift", 1.0) < 1e-10 for row in qrf_frame_rows if row.get("admissible"))
        and "not empirical" in qrf_frame.get("claim_boundary", "")
    )
    roadmap = _load_json(project_root, "output/data/quantum_extension_roadmap.json")
    blocked_future_ids = {"re-3", "re-4", "re-13", "re-14", "re-15"}
    roadmap_future_ids = {row.get("id") for row in roadmap.get("future", [])}
    checks["quantum_extension_roadmap_ok"] = (
        roadmap.get("schema") == "realizing_emptiness.quantum_extension_roadmap.v1"
        and roadmap.get("implemented_count") == len(roadmap.get("implemented", []))
        and roadmap.get("future_count") == len(roadmap.get("future", []))
        and roadmap_future_ids == blocked_future_ids
        and {row.get("blocked_task_id") for row in roadmap.get("future", [])} == blocked_future_ids
        and roadmap.get("all_implemented_have_artifacts") is True
        and all(_exists(project_root, row.get("artifact", "")) for row in roadmap.get("implemented", []))
        and all(row.get("validation_gate") in checks and checks[row["validation_gate"]] for row in roadmap.get("implemented", []))
        and all(row.get("status", "").startswith("roadmap_requires_") for row in roadmap.get("future", []))
        and all(row.get("required_next_gate", "").endswith("_ok") for row in roadmap.get("future", []))
        and all(row.get("required_negative_control") for row in roadmap.get("future", []))
        and "not empirical" in roadmap.get("claim_boundary", "")
    )
    expected_quantum_engine_ids = {
        "two_qubit_separability_entropy",
        "arbitrary_two_qubit_entanglement_audit",
        "chsh_contextuality_witness",
        "chsh_measurement_cover_table",
        "general_measurement_cover_polytope_audit",
        "qrf_basis_invariance_toy",
        "boundary_landauer_entropy",
        "thermodynamic_channel_cost_audit",
        "two_qubit_dephasing_channel",
        "full_open_system_qfep_dynamics",
        "quantum_trajectory_unraveling",
        "many_body_boundary_screens",
        "sparse_boundary_screen_scaling_audit",
        "general_sheaf_contextuality_engine",
        "qrf_transformation_library",
        "qrf_frame_covariance_toy_audit",
        "empirical_adapter",
    }
    checks["quantum_extension_roadmap_has_next_pass_engines"] = expected_quantum_engine_ids <= {
        row.get("id") for row in roadmap.get("implemented", [])
    }
    readiness = _load_json(project_root, "output/data/quantum_roadmap_readiness_matrix.json")
    readiness_rows = readiness.get("rows", [])
    implemented_readiness = [row for row in readiness_rows if row.get("roadmap_class") == "implemented"]
    future_readiness = [row for row in readiness_rows if row.get("roadmap_class") == "future"]
    checks["quantum_roadmap_readiness_ok"] = (
        readiness.get("schema") == "realizing_emptiness.quantum_roadmap_readiness_matrix.v1"
        and readiness.get("row_count") == len(readiness_rows)
        and readiness.get("implemented_count") == roadmap.get("implemented_count") == len(implemented_readiness)
        and readiness.get("future_count") == roadmap.get("future_count") == len(future_readiness)
        and {row.get("id") for row in future_readiness} == blocked_future_ids
        and {row.get("blocked_task_id") for row in future_readiness} == blocked_future_ids
        and readiness.get("all_controls_pass") is True
        and readiness.get("controls", {}).get("all_implemented_validated") is True
        and readiness.get("controls", {}).get("all_future_blocked") is True
        and readiness.get("controls", {}).get("every_future_has_next_gate") is True
        and readiness.get("controls", {}).get("every_row_has_negative_control") is True
        and readiness.get("controls", {}).get("every_row_has_boundary") is True
        and readiness.get("controls", {}).get("forged_completed_future_row_rejected") is True
        and readiness.get("forged_completed_future_row_control", {}).get("manuscript_claim_allowed") is False
        and readiness.get("forged_completed_future_row_control", {}).get("readiness_score") == 0.0
        and all(row.get("readiness_score") == 1.0 and row.get("manuscript_claim_allowed") is True for row in implemented_readiness)
        and all(row.get("readiness_score") == 0.0 and row.get("manuscript_claim_allowed") is False for row in future_readiness)
        and all(row.get("has_artifact") and row.get("has_schema") and row.get("has_validator") for row in implemented_readiness)
        and not any(row.get("has_artifact") or row.get("has_schema") or row.get("has_validator") for row in future_readiness)
        and "not empirical" in readiness.get("claim_boundary", "")
    )
    todo_audit = _load_json(project_root, "output/data/roadmap_todo_audit.json")
    checks["roadmap_todo_audit_ok"] = (
        todo_audit.get("schema") == "realizing_emptiness.roadmap_todo_audit.v1"
        and todo_audit.get("all_controls_pass") is True
        and todo_audit.get("implemented_roadmap_count") == roadmap.get("implemented_count")
        and todo_audit.get("future_roadmap_count") == roadmap.get("future_count")
        and todo_audit.get("stale_future_rows") == []
        and todo_audit.get("historical_backlog_rows") == []
        and todo_audit.get("blocked_external_class_violations") == []
        and todo_audit.get("controls", {}).get("no_future_rows_duplicate_implemented_roadmap_ids") is True
        and todo_audit.get("controls", {}).get("blocked_external_classes_not_described_as_achieved") is True
        and todo_audit.get("controls", {}).get("todo_backlog_has_no_historical_completion_rows") is True
        and "not empirical" in todo_audit.get("claim_boundary", "")
    )
    checks["future_public_archive_and_independent_reproduction_blocked"] = (
        "re-15" in set(todo_audit.get("blocked_task_ids", []))
        and todo_audit.get("controls", {}).get("all_blocked_external_task_ids_present_and_blocked") is True
        and any("re-15" in row.get("matched_blocked_classes", []) for row in todo_audit.get("blocked_external_class_rows", []))
    )
    dependency_graph = _load_json(project_root, "output/data/validation_dependency_graph.json")
    checks["validation_dependency_graph_ok"] = (
        dependency_graph.get("schema") == "realizing_emptiness.validation_dependency_graph.v1"
        and dependency_graph.get("all_controls_pass") is True
        and dependency_graph.get("node_count") == len(dependency_graph.get("nodes", []))
        and dependency_graph.get("edge_count") == len(dependency_graph.get("edges", []))
        and {
            "arbitrary_two_qubit_entanglement_audit",
            "general_measurement_cover_polytope_audit",
            "thermodynamic_channel_cost_audit",
            "sparse_boundary_screen_scaling_audit",
            "qrf_frame_covariance_toy_audit",
            "quantum_trajectory_unraveling",
            "pymdp_runtime_diagnostics_log",
            "stochastic_policy_ensemble",
            "criticality_stochastic_ensemble",
            "stochastic_effect_size_audit",
            "bmr_robustness_resampling_audit",
            "quantum_trajectory_convergence_audit",
            "statistical_robustness_audit",
            "artifact_contract_registry",
            "artifact_release_manifest",
            "external_review_response_audit",
            "figure_parameter_ledger",
            "qrf_label_ablation_audit",
            "quantum_independent_crosscheck_audit",
            "bmr_alternative_prior_audit",
            "method_assumption_ledger",
            "method_negative_control_inventory",
            "visual_style_audit",
            "figure_legibility_audit",
            "claim_context_ledger",
            "claim_redteam_audit",
            "manuscript_claim_intensity_audit",
            "manuscript_reference_audit",
            "figure_reuse_audit",
            "cover_graphical_abstract_audit",
            "roadmap_todo_audit",
            "artifact_dashboard",
            "pdf_render_gate",
        }
        <= set(dependency_graph.get("nodes", []))
        and set(dependency_graph.get("required_quantum_nodes", []))
        <= set(dependency_graph.get("nodes", []))
        and "not empirical" in dependency_graph.get("claim_boundary", "")
    )
    sheaf_coverage = _load_json(project_root, "output/data/sheaf_coverage_matrix.json")
    checks["sheaf_coverage_matrix_ok"] = (
        sheaf_coverage.get("schema") == "realizing_emptiness.sheaf_coverage_matrix.v1"
        and sheaf_coverage.get("ok") is True
        and sheaf_coverage.get("missing_count") == 0
        and sheaf_coverage.get("section_count", 0) >= 6
        and sheaf_coverage.get("track_count", 0) >= 10
    )
    method_ledger = _load_json(project_root, "output/data/method_assumption_ledger.json")
    checks["method_assumption_ledger_ok"] = (
        method_ledger.get("schema") == "realizing_emptiness.method_assumption_ledger.v1"
        and method_ledger.get("method_count", 0) >= 8
        and method_ledger.get("all_methods_have_hard_constraints") is True
        and method_ledger.get("all_methods_have_assumptions") is True
        and method_ledger.get("all_methods_have_evidence_ceiling") is True
        and all(row.get("falsification_controls") for row in method_ledger.get("rows", []))
        and "not empirical" in method_ledger.get("claim_boundary", "")
    )
    method_controls = _load_json(project_root, "output/data/method_negative_control_inventory.json")
    checks["method_negative_control_inventory_ok"] = (
        method_controls.get("schema") == "realizing_emptiness.method_negative_control_inventory.v1"
        and method_controls.get("method_count") == method_ledger.get("method_count")
        and method_controls.get("control_count", 0) >= method_ledger.get("method_count", 0)
        and method_controls.get("all_methods_have_controls") is True
        and "not empirical" in method_controls.get("claim_boundary", "")
    )
    profile = _load_json(project_root, "output/data/pymdp_profile_comparison.json")
    checks["pymdp_canary"] = profile.get("pymdp_canary", {}).get("ok") is True
    checks["posterior_normalized"] = profile.get("posterior_normalized") is True
    policy_trace = _load_json(project_root, "output/data/pymdp_policy_trace.json")
    model_audit = _load_json(project_root, "output/data/pymdp_generative_model_audit.json")
    runtime_log = _load_json(project_root, "output/data/pymdp_runtime_diagnostics_log.json")
    checks["pymdp_policy_trace_ok"] = (
        policy_trace.get("schema") == "realizing_emptiness.pymdp_policy_trace.v1"
        and policy_trace.get("row_count") == policy_trace.get("steps") * len(policy_trace.get("profile_summaries", []))
        and policy_trace.get("all_posteriors_normalized") is True
        and all(abs(row.get("state_posterior_sum", 0.0) - 1.0) < 1e-5 for row in policy_trace.get("rows", []))
        and all(abs(row.get("policy_posterior_sum", 0.0) - 1.0) < 1e-5 for row in policy_trace.get("rows", []))
        and len({row.get("selected_action") for row in policy_trace.get("rows", [])}) >= 2
        and _pymdp_trace_math_ok(policy_trace, model_audit)
        and "not empirical" in policy_trace.get("claim_boundary", "")
    )
    checks["pymdp_generative_model_ok"] = (
        model_audit.get("schema") == "realizing_emptiness.pymdp_generative_model_audit.v1"
        and model_audit.get("profile_count") == 3
        and model_audit.get("all_models_normalized") is True
        and all(row.get("A", {}).get("shape") == [3, 3] for row in model_audit.get("rows", []))
        and all(row.get("B", {}).get("shape") == [3, 3, 3] for row in model_audit.get("rows", []))
        and all(abs(row.get("D_sum", 0.0) - 1.0) < 1e-8 for row in model_audit.get("rows", []))
        and "not empirical" in model_audit.get("claim_boundary", "")
    )
    checks["pymdp_runtime_diagnostics_log_ok"] = _pymdp_runtime_log_ok(runtime_log, policy_trace)
    stochastic_policy = _load_json(project_root, "output/data/stochastic_policy_ensemble.json")
    checks["stochastic_policy_ensemble_ok"] = (
        stochastic_policy.get("schema") == "realizing_emptiness.stochastic_policy_ensemble.v1"
        and stochastic_policy.get("all_controls_pass") is True
        and stochastic_policy.get("profile_count") == 3
        and stochastic_policy.get("row_count")
        == stochastic_policy.get("runs_per_profile") * stochastic_policy.get("steps") * stochastic_policy.get("profile_count") * 2
        and stochastic_policy.get("run_summary_count") == stochastic_policy.get("runs_per_profile") * stochastic_policy.get("profile_count") * 2
        and stochastic_policy.get("controls", {}).get("all_posteriors_normalized") is True
        and stochastic_policy.get("controls", {}).get("all_intervals_finite") is True
        and stochastic_policy.get("controls", {}).get("profiles_differ_from_null_controls") is True
        and stochastic_policy.get("controls", {}).get("seeded_replay_declared") is True
        and all(abs(row.get("state_posterior_sum", 0.0) - 1.0) < 1e-8 for row in stochastic_policy.get("rows", []))
        and all(abs(row.get("policy_posterior_sum", 0.0) - 1.0) < 1e-8 for row in stochastic_policy.get("rows", []))
        and any(row.get("null_control") is True for row in stochastic_policy.get("rows", []))
        and "not empirical" in stochastic_policy.get("claim_boundary", "")
        and "not a neural measurement" in stochastic_policy.get("claim_boundary", "")
    )
    practice = _load_json(project_root, "output/data/practice_protocol_map.json")
    checks["practice_boundaries"] = practice.get("allow_user_facing_claims") is False and practice.get("all_have_safety_boundaries") is True
    criticality = _load_json(project_root, "output/reports/criticality_proxy_report.json")
    checks["criticality_boundary"] = (
        criticality.get("schema") == "realizing_emptiness.criticality_proxy_report.v1"
        and criticality.get("label") == "single_trace_diagnostic_not_empirical_neural_measure"
        and "not evidence" in criticality.get("claim_boundary", "")
    )
    criticality_stochastic = _load_json(project_root, "output/data/criticality_stochastic_ensemble.json")
    checks["criticality_stochastic_ensemble_ok"] = (
        criticality_stochastic.get("schema") == "realizing_emptiness.criticality_stochastic_ensemble.v1"
        and criticality_stochastic.get("label") == "seeded_stochastic_simulation_not_empirical_neural_measure"
        and criticality_stochastic.get("all_controls_pass") is True
        and criticality_stochastic.get("controls", {}).get("seeded_policy_source") is True
        and criticality_stochastic.get("controls", {}).get("all_intervals_finite") is True
        and criticality_stochastic.get("controls", {}).get("null_controls_present") is True
        and criticality_stochastic.get("controls", {}).get("profiles_differ_from_null_controls") is True
        and criticality_stochastic.get("summary_row_count", 0) >= 6
        and "not empirical" in criticality_stochastic.get("claim_boundary", "")
        and "not empirical neural-criticality" in criticality_stochastic.get("claim_boundary", "")
    )
    stochastic_effects = _load_json(project_root, "output/data/stochastic_effect_size_audit.json")
    checks["stochastic_effect_size_audit_ok"] = (
        stochastic_effects.get("schema") == "realizing_emptiness.stochastic_effect_size_audit.v1"
        and stochastic_effects.get("all_controls_pass") is True
        and stochastic_effects.get("metric_count", 0) >= 6
        and stochastic_effects.get("row_count") == len(stochastic_effects.get("rows", []))
        and stochastic_effects.get("controls", {}).get("all_intervals_finite") is True
        and stochastic_effects.get("controls", {}).get("all_p_values_bounded") is True
        and all(0.0 <= row.get("permutation_p", -1.0) <= 1.0 for row in stochastic_effects.get("rows", []))
        and all(0.0 <= row.get("holm_p", -1.0) <= 1.0 for row in stochastic_effects.get("rows", []))
        and any(abs(row.get("cliffs_delta", 0.0)) > 0.1 for row in stochastic_effects.get("rows", []))
        and "not empirical" in stochastic_effects.get("claim_boundary", "")
    )
    bmr_resampling = _load_json(project_root, "output/data/bmr_robustness_resampling_audit.json")
    checks["bmr_robustness_resampling_audit_ok"] = (
        bmr_resampling.get("schema") == "realizing_emptiness.bmr_robustness_resampling_audit.v1"
        and bmr_resampling.get("all_controls_pass") is True
        and bmr_resampling.get("row_count") == len(bmr_resampling.get("rows", []))
        and bmr_resampling.get("controls", {}).get("all_intervals_finite") is True
        and bmr_resampling.get("controls", {}).get("all_pruning_rates_bounded") is True
        and any(row.get("sign_stable") is True for row in bmr_resampling.get("rows", []))
        and all(0.0 <= row.get("pruning_rate", -1.0) <= 1.0 for row in bmr_resampling.get("rows", []))
        and "not empirical" in bmr_resampling.get("claim_boundary", "")
    )
    trajectory_convergence = _load_json(project_root, "output/data/quantum_trajectory_convergence_audit.json")
    checks["quantum_trajectory_convergence_audit_ok"] = (
        trajectory_convergence.get("schema") == "realizing_emptiness.quantum_trajectory_convergence_audit.v1"
        and trajectory_convergence.get("all_controls_pass") is True
        and trajectory_convergence.get("row_count") == len(trajectory_convergence.get("rows", []))
        and trajectory_convergence.get("controls", {}).get("residuals_finite") is True
        and trajectory_convergence.get("controls", {}).get("log_log_slope_negative") is True
        and trajectory_convergence.get("controls", {}).get("too_few_trajectory_control_fails") is True
        and trajectory_convergence.get("too_few_trajectory_control", {}).get("all_controls_pass") is False
        and trajectory_convergence.get("rows", [{}])[-1].get("max_trace_distance_to_exact", 1.0) < 0.08
        and "not empirical" in trajectory_convergence.get("claim_boundary", "")
    )
    effect_size_calibration = _load_json(project_root, "output/data/effect_size_calibration_audit.json")
    checks["effect_size_calibration_audit_ok"] = (
        effect_size_calibration.get("schema") == "realizing_emptiness.effect_size_calibration_audit.v1"
        and effect_size_calibration.get("all_controls_pass") is True
        and effect_size_calibration.get("controls", {}).get("null_not_rejected") is True
        and effect_size_calibration.get("controls", {}).get("positive_effect_rejected") is True
        and effect_size_calibration.get("controls", {}).get("cliffs_delta_sign_matches_injection") is True
        and effect_size_calibration.get("controls", {}).get("positive_effect_magnitude_recovered") is True
        and effect_size_calibration.get("positive_arm", {}).get("permutation_p", 1.0)
        <= effect_size_calibration.get("alpha", 0.05)
        and effect_size_calibration.get("null_arm", {}).get("permutation_p", 0.0)
        > effect_size_calibration.get("alpha", 0.05)
        and "not empirical statistical power" in effect_size_calibration.get("claim_boundary", "")
    )
    statistical_robustness = _load_json(project_root, "output/data/statistical_robustness_audit.json")
    checks["statistical_robustness_audit_ok"] = (
        statistical_robustness.get("schema") == "realizing_emptiness.statistical_robustness_audit.v1"
        and statistical_robustness.get("all_controls_pass") is True
        and statistical_robustness.get("controls", {}).get("stochastic_effects_pass") is True
        and statistical_robustness.get("controls", {}).get("bmr_resampling_pass") is True
        and statistical_robustness.get("controls", {}).get("trajectory_convergence_pass") is True
        and statistical_robustness.get("controls", {}).get("effect_size_calibration_pass") is True
        and "not empirical" in statistical_robustness.get("claim_boundary", "")
    )
    compassion_scope = _load_json(project_root, "output/data/compassion_scope_audit.json")
    checks["compassion_scope_audit_ok"] = (
        compassion_scope.get("schema") == "realizing_emptiness.compassion_scope_audit.v1"
        and compassion_scope.get("all_controls_pass") is True
        and compassion_scope.get("deployment_count", 0) >= 3
        and compassion_scope.get("controls", {}).get("real_widening_monotone") is True
        and compassion_scope.get("controls", {}).get("prior_precision_drives_self_scoping") is True
        and compassion_scope.get("controls", {}).get("widening_amplified_by_prior") is True
        and compassion_scope.get("real_spread", 0.0) > compassion_scope.get("ablated_spread", 1.0)
        and "not a measure of compassion" in compassion_scope.get("claim_boundary", "")
    )
    emergence = _load_json(project_root, "output/data/separation_prior_emergence_audit.json")
    checks["separation_prior_emergence_audit_ok"] = (
        emergence.get("schema") == "realizing_emptiness.separation_prior_emergence_audit.v1"
        and emergence.get("all_controls_pass") is True
        and emergence.get("controls", {}).get("factored_beats_unfactored_at_high_empowerment") is True
        and emergence.get("controls", {}).get("factored_does_not_beat_unfactored_at_zero_empowerment") is True
        and emergence.get("controls", {}).get("accuracy_gain_monotone_in_empowerment") is True
        and emergence.get("controls", {}).get("planted_full_contingency_detected") is True
        and emergence.get("controls", {}).get("action_shuffle_collapses_factored_advantage") is True
        and abs(emergence.get("zero_empowerment_advantage", 1.0)) < 1e-9
        and emergence.get("full_empowerment_advantage", 0.0) > 0.2
        and emergence.get("mean_action_shuffled_advantage", 1.0) < 0.25 * emergence.get("full_empowerment_advantage", 0.0)
        and "not a developmental" in emergence.get("claim_boundary", "")
    )
    internal_cut = _load_json(project_root, "output/data/internal_cut_unmeasurability_audit.json")
    checks["internal_cut_unmeasurability_audit_ok"] = (
        internal_cut.get("schema") == "realizing_emptiness.internal_cut_unmeasurability_audit.v1"
        and internal_cut.get("all_controls_pass") is True
        and internal_cut.get("bipartition_count", 0) >= 3
        and internal_cut.get("controls", {}).get("accessible_marginal_invariant_across_internal_cuts") is True
        and internal_cut.get("controls", {}).get("god_eye_entropy_actually_differs") is True
        and internal_cut.get("controls", {}).get("separability_unrecoverable_from_marginal") is True
        and all(row.get("accessible_marginal_drift", 1.0) < 1e-9 for row in internal_cut.get("rows", []))
        and "not empirical" in internal_cut.get("claim_boundary", "")
    )
    contextuality_suppression = _load_json(project_root, "output/data/sigma_contextuality_suppression_audit.json")
    checks["sigma_contextuality_suppression_audit_ok"] = (
        contextuality_suppression.get("schema") == "realizing_emptiness.sigma_contextuality_suppression_audit.v1"
        and contextuality_suppression.get("all_controls_pass") is True
        and contextuality_suppression.get("controls", {}).get("unconstrained_exhibits_contextuality") is True
        and contextuality_suppression.get("controls", {}).get("sigma_suppresses_contextuality") is True
        and contextuality_suppression.get("controls", {}).get("noncontextual_control_no_suppression") is True
        and contextuality_suppression.get("controls", {}).get("constrained_always_feasible") is True
        and "not empirical" in contextuality_suppression.get("claim_boundary", "")
    )
    ongoing_revision = _load_json(project_root, "output/data/ongoing_revision_audit.json")
    checks["ongoing_revision_audit_ok"] = (
        ongoing_revision.get("schema") == "realizing_emptiness.ongoing_revision_audit.v1"
        and ongoing_revision.get("all_controls_pass") is True
        and ongoing_revision.get("controls", {}).get("post_dual_outperforms_after_regime_change") is True
        and ongoing_revision.get("controls", {}).get("revision_gain_concentrated_at_regime_change") is True
        and ongoing_revision.get("controls", {}).get("stationary_stream_shows_no_revision_jump") is True
        and ongoing_revision.get("controls", {}).get("nonstationary_jump_exceeds_stationary") is True
        and "not a claim of realized awakening" in ongoing_revision.get("claim_boundary", "")
    )
    multipartite_witness = _load_json(project_root, "output/data/multipartite_witness_suite_audit.json")
    checks["multipartite_witness_suite_audit_ok"] = (
        multipartite_witness.get("schema") == "realizing_emptiness.multipartite_witness_suite_audit.v1"
        and multipartite_witness.get("all_controls_pass") is True
        and multipartite_witness.get("controls", {}).get("ghz_entangled_across_every_bipartition") is True
        and multipartite_witness.get("controls", {}).get("qudit_entangled_detected") is True
        and multipartite_witness.get("controls", {}).get("separable_controls_not_detected") is True
        and multipartite_witness.get("controls", {}).get("detection_matches_expectation") is True
        and multipartite_witness.get("controls", {}).get("asymmetric_cuts_match_expected_pattern") is True
        and "not empirical" in multipartite_witness.get("claim_boundary", "")
    )
    tensor_network = _load_json(project_root, "output/data/tensor_network_benchmark_audit.json")
    checks["tensor_network_benchmark_audit_ok"] = (
        tensor_network.get("schema") == "realizing_emptiness.tensor_network_benchmark_audit.v1"
        and tensor_network.get("all_controls_pass") is True
        and tensor_network.get("controls", {}).get("exact_mps_reconstructs_every_state") is True
        and tensor_network.get("controls", {}).get("truncation_to_one_hurts_entangled") is True
        and tensor_network.get("controls", {}).get("truncation_to_one_lossless_for_product") is True
        and "not empirical" in tensor_network.get("claim_boundary", "")
    )
    collision_model = _load_json(project_root, "output/data/collision_model_thermalization_audit.json")
    checks["collision_model_thermalization_audit_ok"] = (
        collision_model.get("schema") == "realizing_emptiness.collision_model_thermalization_audit.v1"
        and collision_model.get("all_controls_pass") is True
        and collision_model.get("controls", {}).get("coupled_collisions_relax_toward_ancilla") is True
        and collision_model.get("controls", {}).get("zero_coupling_leaves_system_unchanged") is True
        and "not empirical" in collision_model.get("claim_boundary", "")
    )
    no_signaling = _load_json(project_root, "output/data/no_signaling_scenario_library_audit.json")
    checks["no_signaling_scenario_library_audit_ok"] = (
        no_signaling.get("schema") == "realizing_emptiness.no_signaling_scenario_library_audit.v1"
        and no_signaling.get("all_controls_pass") is True
        and no_signaling.get("controls", {}).get("no_signaling_matches_expectation") is True
        and no_signaling.get("controls", {}).get("disturbing_control_signals") is True
        and "not empirical" in no_signaling.get("claim_boundary", "")
    )
    n_cycle = _load_json(project_root, "output/data/n_cycle_contextuality_library_audit.json")
    checks["n_cycle_contextuality_library_audit_ok"] = (
        n_cycle.get("schema") == "realizing_emptiness.n_cycle_contextuality_library_audit.v1"
        and n_cycle.get("all_controls_pass") is True
        and n_cycle.get("controls", {}).get("perfect_anticorrelation_matches_two_colorability") is True
        and n_cycle.get("controls", {}).get("odd_cycles_contextual_at_quantum_correlation") is True
        and n_cycle.get("controls", {}).get("even_cycles_noncontextual_at_quantum_correlation") is True
        and "not empirical" in n_cycle.get("claim_boundary", "")
    )
    markov_blanket = _load_json(project_root, "output/data/markov_blanket_discovery_audit.json")
    checks["markov_blanket_discovery_audit_ok"] = (
        markov_blanket.get("schema") == "realizing_emptiness.markov_blanket_discovery_audit.v1"
        and markov_blanket.get("all_controls_pass") is True
        and markov_blanket.get("controls", {}).get("precision_support_recovers_blanket") is True
        and markov_blanket.get("controls", {}).get("partial_correlation_threshold_also_recovers_blanket") is True
        and markov_blanket.get("controls", {}).get("marginal_covariance_threshold_cannot_recover_blanket") is True
        and markov_blanket.get("controls", {}).get("dense_precision_has_no_nontrivial_blanket") is True
        and markov_blanket.get("controls", {}).get("epsilon_coupling_breaks_exact_separation") is True
        and markov_blanket.get("controls", {}).get("precision_recovers_more_reliably_than_marginal_in_ensemble") is True
        and markov_blanket.get("marginal_correlation_best_f1", 1.0) < 1.0
        and markov_blanket.get("perturbation_ensemble", {}).get("precision_recovery_fraction") == 1.0
        and "not empirical" in markov_blanket.get("claim_boundary", "")
    )
    cramer_rao = _load_json(project_root, "output/data/quantum_cramer_rao_estimation_audit.json")
    checks["quantum_cramer_rao_estimation_audit_ok"] = (
        cramer_rao.get("schema") == "realizing_emptiness.quantum_cramer_rao_estimation_audit.v1"
        and cramer_rao.get("all_controls_pass") is True
        and cramer_rao.get("controls", {}).get("quantum_cramer_rao_bound_never_violated") is True
        and cramer_rao.get("controls", {}).get("optimal_measurement_saturates_qfi") is True
        and cramer_rao.get("controls", {}).get("coherent_pointer_measurement_strictly_loses_information") is True
        and cramer_rao.get("controls", {}).get("classical_encoding_pointer_is_already_optimal") is True
        and "not empirical" in cramer_rao.get("claim_boundary", "")
    )
    interaction_information = _load_json(project_root, "output/data/interaction_information_boundary_audit.json")
    checks["interaction_information_boundary_audit_ok"] = (
        interaction_information.get("schema") == "realizing_emptiness.interaction_information_boundary_audit.v1"
        and interaction_information.get("all_controls_pass") is True
        and interaction_information.get("controls", {}).get("synergistic_boundary_marginal_is_exactly_zero") is True
        and interaction_information.get("controls", {}).get("synergistic_boundary_conditional_is_a_full_bit") is True
        and interaction_information.get("controls", {}).get("interaction_information_sign_discriminates_regimes") is True
        and interaction_information.get("controls", {}).get("redundant_screen_is_conditionally_independent") is True
        and "not empirical" in interaction_information.get("claim_boundary", "")
    )
    blackwell = _load_json(project_root, "output/data/blackwell_bayes_risk_audit.json")
    checks["blackwell_bayes_risk_audit_ok"] = (
        blackwell.get("schema") == "realizing_emptiness.blackwell_bayes_risk_audit.v1"
        and blackwell.get("all_controls_pass") is True
        and blackwell.get("controls", {}).get("invertible_relabeling_preserves_bayes_risk") is True
        and blackwell.get("controls", {}).get("nontrivial_garbling_strictly_increases_bayes_risk") is True
        and blackwell.get("controls", {}).get("bayes_risk_never_below_original_under_garbling") is True
        and "not empirical" in blackwell.get("claim_boundary", "")
    )
    classical_dp = _load_json(project_root, "output/data/classical_data_processing_audit.json")
    checks["classical_data_processing_audit_ok"] = (
        classical_dp.get("schema") == "realizing_emptiness.classical_data_processing_audit.v1"
        and classical_dp.get("all_controls_pass") is True
        and classical_dp.get("controls", {}).get("data_processing_inequality_holds_for_every_readout") is True
        and classical_dp.get("controls", {}).get("sufficient_readout_saturates_bound") is True
        and classical_dp.get("controls", {}).get("lossy_readout_strictly_loses_information") is True
        and "not empirical" in classical_dp.get("claim_boundary", "")
    )
    data_processing = _load_json(project_root, "output/data/data_processing_monotonicity_audit.json")
    checks["data_processing_monotonicity_audit_ok"] = (
        data_processing.get("schema") == "realizing_emptiness.data_processing_monotonicity_audit.v1"
        and data_processing.get("all_controls_pass") is True
        and data_processing.get("controls", {}).get("cptp_channels_are_completely_positive") is True
        and data_processing.get("controls", {}).get("transpose_map_is_not_completely_positive") is True
        and data_processing.get("controls", {}).get("cptp_channels_do_not_increase_trace_distance") is True
        and data_processing.get("controls", {}).get("cptp_channels_do_not_increase_relative_entropy") is True
        and data_processing.get("controls", {}).get("selective_postselection_can_increase_trace_distance") is True
        and "not empirical" in data_processing.get("claim_boundary", "")
    )
    crosswalk = _load_json(project_root, "output/data/source_claim_crosswalk.json")
    source_coverage = _load_json(project_root, "output/data/source_argument_coverage_audit.json")
    source_coverage_rows = {row.get("theme_id"): row for row in source_coverage.get("rows", [])}
    checks["source_argument_coverage_audit_ok"] = (
        source_coverage.get("schema") == "realizing_emptiness.source_argument_coverage_audit.v1"
        and source_coverage.get("all_controls_pass") is True
        and source_coverage.get("theme_count", 0) >= 9
        and source_coverage.get("controls", {}).get("all_core_themes_mapped") is True
        and source_coverage.get("controls", {}).get("all_local_sections_resolve") is True
        and all(row.get("unresolved_local_sections") == [] for row in source_coverage.get("rows", []))
        and source_coverage.get("controls", {}).get("qrf_bmr_opacification_not_quantum_only") is True
        and {"no_self_evidence_boundary", "qrf_sectorisation_equations_7_to_10", "bmr_pruning_of_sigma"} <= set(source_coverage_rows)
        and source_coverage_rows.get("qrf_sectorisation_equations_7_to_10", {}).get("source_equations") == [7, 8, 9, 10]
        and source_coverage_rows.get("bmr_pruning_of_sigma", {}).get("primary_coverage_class") == "active_inference_bmr_argument"
        and "not empirical" in source_coverage.get("claim_boundary", "")
    )
    claim_support = _load_json(project_root, "output/data/claim_support_audit.json")
    claims = crosswalk.get("claims", [])
    checks["claim_support_audit_ok"] = (
        claim_support.get("ok") is True
        and claim_support.get("public_claim_count") == crosswalk.get("claim_count")
        and claim_support.get("unsupported_public_claims") == []
        and claim_support.get("unknown_claim_ids") == []
    )
    checks["claim_artifacts_exist"] = all(_exists(project_root, claim.get("artifact", "")) for claim in claims)
    checks["claim_ceiling_present"] = all(
        bool(claim.get(field))
        for claim in claims
        for field in ("evidence_ceiling", "prohibited_inference", "future_evidence_required", "stressors")
    )
    checks["claim_crosswalk_gates_resolve"] = all(claim.get("gate") in checks and checks[claim["gate"]] for claim in claims)
    manuscript_claim_audit = _load_json(project_root, "output/data/manuscript_claim_audit.json")
    checks["manuscript_claim_audit_ok"] = (
        manuscript_claim_audit.get("ok") is True
        and manuscript_claim_audit.get("missing_bibliography_keys") == []
        and manuscript_claim_audit.get("missing_claim_mentions") == []
        and manuscript_claim_audit.get("forbidden_positive_claims") == []
        and manuscript_claim_audit.get("public_claim_count") == crosswalk.get("claim_count")
    )
    claim_intensity = _load_json(project_root, "output/data/manuscript_claim_intensity_audit.json")
    checks["manuscript_claim_intensity_audit_ok"] = (
        claim_intensity.get("schema") == "realizing_emptiness.manuscript_claim_intensity_audit.v1"
        and claim_intensity.get("ok") is True
        and claim_intensity.get("risky_rows") == []
        and claim_intensity.get("sentence_count", 0) >= 50
        and "not empirical" in claim_intensity.get("claim_boundary", "")
    )
    evidence_ceiling_audit = _load_json(project_root, "output/data/evidence_ceiling_audit.json")
    checks["evidence_ceiling_audit_ok"] = (
        evidence_ceiling_audit.get("ok") is True
        and evidence_ceiling_audit.get("claim_count") == crosswalk.get("claim_count")
        and evidence_ceiling_audit.get("missing_boundary_fields") == []
        and evidence_ceiling_audit.get("invalid_stressors") == []
        and evidence_ceiling_audit.get("status_mismatches") == []
        and evidence_ceiling_audit.get("claims_without_support") == []
        and all(row.get("support_count", 0) > 0 for row in evidence_ceiling_audit.get("rows", []))
    )
    claim_context = _load_json(project_root, "output/data/claim_context_ledger.json")
    claim_context_rows = claim_context.get("rows", [])
    checks["claim_context_ledger_ok"] = (
        claim_context.get("schema") == "realizing_emptiness.claim_context_ledger.v1"
        and claim_context.get("claim_count") == crosswalk.get("claim_count") == len(claim_context_rows)
        and claim_context.get("all_controls_pass") is True
        and claim_context.get("missing_reader_claims") == []
        and claim_context.get("missing_source_roles") == []
        and claim_context.get("unresolved_source_keys") == []
        and claim_context.get("missing_artifacts") == []
        and claim_context.get("missing_gates") == []
        and claim_context.get("missing_allowed_interpretations") == []
        and claim_context.get("missing_prohibited_interpretations") == []
        and claim_context.get("missing_future_evidence") == []
        and claim_context.get("missing_manuscript_sections") == []
        and claim_context.get("missing_figure_bindings") == []
        and claim_context.get("role_compatibility_failures") == []
        and claim_context.get("proxy_overclaiming_reader_claims") == []
        and all((project_root / row.get("artifact", "")).exists() for row in claim_context_rows)
        and all(row.get("validation_gate") in checks and checks[row["validation_gate"]] for row in claim_context_rows)
        and all(row.get("allowed_interpretation") and row.get("prohibited_inference") for row in claim_context_rows)
        and all(row.get("role_compatibility", {}).get("ok") is True for row in claim_context_rows)
        and "not empirical" in claim_context.get("claim_boundary", "")
    )
    figure_map = _load_json(project_root, "output/data/figure_source_map.json")
    figure_ids = {row.get("id") for row in figure_map.get("figures", [])}
    claim_redteam = _load_json(project_root, "output/data/claim_redteam_audit.json")
    claim_redteam_rows = claim_redteam.get("rows", [])
    checks["claim_redteam_audit_ok"] = (
        claim_redteam.get("schema") == "realizing_emptiness.claim_redteam_audit.v1"
        and claim_redteam.get("claim_count") == crosswalk.get("claim_count") == len(claim_redteam_rows)
        and claim_redteam.get("all_controls_pass") is True
        and claim_redteam.get("missing_sections") == []
        and claim_redteam.get("unresolved_sections") == []
        and claim_redteam.get("missing_figure_bindings") == []
        and claim_redteam.get("unresolved_figure_bindings") == []
        and claim_redteam.get("missing_boundaries") == []
        and claim_redteam.get("missing_source_roles") == []
        and claim_redteam.get("missing_artifacts_or_gates") == []
        and claim_redteam.get("reader_overclaims") == []
        and claim_redteam.get("risky_claim_sentences") == []
        and all(row.get("row_controls_pass") is True for row in claim_redteam_rows)
        and all(row.get("section_anchors_resolve") is True for row in claim_redteam_rows)
        and all(row.get("figure_bindings_resolve") is True for row in claim_redteam_rows)
        and all(set(row.get("figure_bindings", [])) <= figure_ids for row in claim_redteam_rows)
        and all(row.get("prohibited_inference") and row.get("future_evidence_required") for row in claim_redteam_rows)
        and "not empirical" in claim_redteam.get("claim_boundary", "")
    )
    checks["figure_source_count"] = figure_map.get("figure_count") == len(EXPECTED_FIGURES)
    checks["new_engine_figures_source_mapped"] = {
        "graphical_abstract_cover",
        "qrf_boundary_screen_geometry",
        "qrf_channel_relabeling_ledger",
        "qrf_invariance_policy_flow",
        "finite_quantum_scope_summary",
        "arbitrary_two_qubit_entanglement_audit",
        "general_measurement_cover_polytope_audit",
        "thermodynamic_channel_cost_audit",
        "sparse_boundary_screen_scaling_audit",
        "qrf_frame_covariance_toy_audit",
        "criticality_stochastic_ensemble",
        "quantum_trajectory_unraveling",
        "pymdp_runtime_validation_dashboard",
        "stochastic_effect_size_forest",
        "bmr_robustness_resampling",
        "quantum_trajectory_convergence",
        "visual_semantic_palette_ledger",
        "method_assumption_failure_map",
        "claim_context_evidence_ladder",
    } <= {row.get("id") for row in figure_map.get("figures", [])}
    figure_parameter_ledger = _load_json(project_root, "output/data/figure_parameter_ledger.json")
    figure_parameter_controls = figure_parameter_ledger.get("controls", {})
    checks["figure_parameter_ledger_ok"] = (
        figure_parameter_ledger.get("schema") == "realizing_emptiness.figure_parameter_ledger.v1"
        and figure_parameter_ledger.get("row_count") == figure_map.get("figure_count") == len(figure_parameter_ledger.get("rows", []))
        and figure_parameter_ledger.get("all_controls_pass") is True
        and figure_parameter_controls.get("one_row_per_manifest_figure") is True
        and figure_parameter_controls.get("all_rows_have_source_artifacts") is True
        and figure_parameter_controls.get("all_source_artifacts_exist") is True
        and figure_parameter_ledger.get("missing_rows") == []
        and figure_parameter_ledger.get("rows_without_sources") == []
        and figure_parameter_ledger.get("missing_source_artifacts") == []
        and all(row.get("traceable") is True for row in figure_parameter_ledger.get("rows", []))
        and "not empirical" in figure_parameter_ledger.get("claim_boundary", "")
    )
    figure_rows_by_id = {row.get("id"): row for row in figure_map.get("figures", [])}
    qrf_figure_rows = [figure_rows_by_id.get(figure_id) for figure_id in (
        "qrf_boundary_screen_geometry",
        "qrf_channel_relabeling_ledger",
        "qrf_invariance_policy_flow",
    )]
    qrf_ledger_row = figure_rows_by_id.get("qrf_channel_relabeling_ledger", {})
    checks["qrf_figure_uses_channel_ledger"] = (
        all(qrf_figure_rows)
        and "output/data/qrf_boundary_channel_ledger.json" in qrf_ledger_row.get("source_artifacts", [])
        and qrf_ledger_row.get("channel_labels") == [f"b{index}" for index in range(6)]
        and "equations 7-10" in qrf_ledger_row.get("caption", "").lower()
        and "ontological" in qrf_ledger_row.get("caption", "")
        and "qrf_boundary_graphical_model" not in figure_rows_by_id
    )
    caption_audit = _load_json(project_root, "output/data/visual_caption_audit.json")
    checks["visual_caption_audit_ok"] = (
        caption_audit.get("schema") == "realizing_emptiness.visual_caption_audit.v1"
        and caption_audit.get("figure_count") == len(EXPECTED_FIGURES)
        and caption_audit.get("row_count") == len(EXPECTED_FIGURES)
        and caption_audit.get("missing_or_weak_captions") == []
        and caption_audit.get("missing_source_artifacts") == []
        and caption_audit.get("missing_interpretive_boundaries") == []
        and caption_audit.get("missing_visual_encodings") == []
        and caption_audit.get("ok") is True
    )
    rendered_caption_audit = _load_json(project_root, "output/data/rendered_figure_caption_audit.json")
    checks["rendered_figure_caption_audit_ok"] = (
        rendered_caption_audit.get("schema") == "realizing_emptiness.rendered_figure_caption_audit.v1"
        and rendered_caption_audit.get("figure_reference_count", 0) >= 20
        and rendered_caption_audit.get("unique_figure_count", 0) >= 20
        and rendered_caption_audit.get("missing_or_weak_captions") == []
        and rendered_caption_audit.get("missing_source_artifacts") == []
        and rendered_caption_audit.get("missing_interpretive_boundaries") == []
        and rendered_caption_audit.get("missing_visual_encoding_language") == []
        and rendered_caption_audit.get("ok") is True
    )
    required_rendered_figures = {
        "qrf_boundary_screen_geometry",
        "qrf_channel_relabeling_ledger",
        "qrf_invariance_policy_flow",
        "finite_quantum_scope_summary",
        "bmr_pruning_phase_diagram",
        "criticality_stochastic_ensemble",
        "quantum_trajectory_unraveling",
        "claim_context_evidence_ladder",
    }
    checks["required_numbered_figures_rendered"] = required_rendered_figures <= {
        row.get("figure_id") for row in rendered_caption_audit.get("rows", [])
    }
    accessibility_audit = _load_json(project_root, "output/data/visual_accessibility_audit.json")
    checks["visual_accessibility_audit_ok"] = (
        accessibility_audit.get("schema") == "realizing_emptiness.visual_accessibility_audit.v1"
        and accessibility_audit.get("figure_count") == len(EXPECTED_FIGURES)
        and accessibility_audit.get("row_count") == len(EXPECTED_FIGURES)
        and accessibility_audit.get("missing_alt_text") == []
        and accessibility_audit.get("missing_data_table_alternative") == []
        and accessibility_audit.get("missing_non_color_encoding") == []
        and accessibility_audit.get("missing_units_or_axes") == []
        and accessibility_audit.get("missing_legend_or_colorbar") == []
        and accessibility_audit.get("ok") is True
    )
    visual_style = _load_json(project_root, "output/data/visual_style_audit.json")
    checks["visual_style_audit_ok"] = (
        visual_style.get("schema") == "realizing_emptiness.visual_style_audit.v1"
        and visual_style.get("figure_count") == len(EXPECTED_FIGURES)
        and visual_style.get("row_count") == len(EXPECTED_FIGURES)
        and visual_style.get("missing_roles") == []
        and visual_style.get("missing_legend_or_colorbar") == []
        and visual_style.get("low_contrast_roles") == []
        and {"pass", "fail", "keep", "prune", "finite", "blocked", "stochastic", "quantum"} <= set(visual_style.get("palette", {}))
        and visual_style.get("ok") is True
        and "not empirical" in visual_style.get("claim_boundary", "")
    )
    legibility = _load_json(project_root, "output/data/figure_legibility_audit.json")
    checks["figure_legibility_audit_ok"] = (
        legibility.get("schema") == "realizing_emptiness.figure_legibility_audit.v1"
        and legibility.get("minimum_width_px", 0) >= 1200
        and legibility.get("minimum_height_px", 0) >= 600
        and legibility.get("minimum_readable_font_pt", 0.0) >= 12.0
        and legibility.get("figure_count") == len(EXPECTED_FIGURES)
        and legibility.get("row_count") == len(EXPECTED_FIGURES)
        and legibility.get("undersized") == []
        and legibility.get("undersized_text") == []
        and legibility.get("missing_render_contract") == []
        and legibility.get("missing_legend_or_colorbar") == []
        and legibility.get("missing_source_data_alternative") == []
        and legibility.get("overlapping_text") == []
        and legibility.get("overlapping_titles") == []
        and legibility.get("cropped_text") == []
        and legibility.get("legend_axis_overlaps") == []
        and legibility.get("layout_failures") == []
        and legibility.get("ok") is True
        and "not empirical" in legibility.get("claim_boundary", "")
    )
    figure_integrity = compare_figure_integrity(project_root)
    checks["figure_integrity_audit_ok"] = (
        figure_integrity.get("ok") is True
        and figure_integrity.get("figure_hash_mismatches") == []
        and figure_integrity.get("source_hash_mismatches") == []
        and figure_integrity.get("dimension_mismatches") == []
        and figure_integrity.get("current_blank_figures") == []
        and figure_integrity.get("current_undersized_figures") == []
        and figure_integrity.get("current_missing_sources") == []
    )
    dashboard_payload = _load_json(project_root, "output/data/artifact_dashboard_payload.json")
    checks["artifact_dashboard_ok"] = (
        dashboard_payload.get("schema") == "realizing_emptiness.artifact_dashboard_payload.v1"
        and dashboard_payload.get("roadmap", {}).get("implemented_count") == roadmap.get("implemented_count")
        and dashboard_payload.get("readiness", {}).get("future_blocked") is True
        and dashboard_payload.get("todo_audit", {}).get("all_controls_pass") is True
        and dashboard_payload.get("figures", {}).get("figure_count") == len(EXPECTED_FIGURES)
        and dashboard_payload.get("dependency_graph", {}).get("all_controls_pass") is True
        and dashboard_payload.get("pymdp_runtime", {}).get("all_controls_pass") is True
        and dashboard_payload.get("pymdp_runtime", {}).get("replay_equal") is True
        and dashboard_payload.get("pymdp_runtime", {}).get("canary_warning_count", 0) >= 1
        and dashboard_payload.get("pymdp_runtime", {}).get("max_weighted_expected_free_energy_residual", 1.0) < 1e-7
        and dashboard_payload.get("stochastic_engines", {}).get("active_inference_ensemble_ok") is True
        and dashboard_payload.get("stochastic_engines", {}).get("criticality_ensemble_ok") is True
        and dashboard_payload.get("stochastic_engines", {}).get("quantum_trajectory_ok") is True
        and dashboard_payload.get("manuscript_audits", {}).get("references_ok") is True
        and dashboard_payload.get("manuscript_audits", {}).get("figure_reuse_ok") is True
        and dashboard_payload.get("manuscript_audits", {}).get("cover_graphic_ok") is True
        and dashboard_payload.get("manuscript_audits", {}).get("claim_intensity_ok") is True
        and dashboard_payload.get("statistical_robustness", {}).get("all_controls_pass") is True
        and dashboard_payload.get("visual_quality", {}).get("style_ok") is True
        and dashboard_payload.get("visual_quality", {}).get("legibility_ok") is True
        and dashboard_payload.get("method_governance", {}).get("all_methods_have_controls") is True
        and dashboard_payload.get("source_fit", {}).get("all_controls_pass") is True
        and dashboard_payload.get("source_fit", {}).get("qrf_bmr_opacification_not_quantum_only") is True
        and dashboard_payload.get("claim_context", {}).get("all_controls_pass") is True
        and dashboard_payload.get("claim_context", {}).get("claim_count") == crosswalk.get("claim_count")
        and dashboard_payload.get("claim_redteam", {}).get("all_controls_pass") is True
        and dashboard_payload.get("claim_redteam", {}).get("claim_count") == crosswalk.get("claim_count")
        and dashboard_payload.get("claim_redteam", {}).get("unresolved_sections") == []
        and dashboard_payload.get("claim_redteam", {}).get("unresolved_figure_bindings") == []
        and dashboard_payload.get("contract_registry", {}).get("all_controls_pass") is True
        and dashboard_payload.get("review_hardening", {}).get("artifact_release_ok") is True
        and dashboard_payload.get("review_hardening", {}).get("review_response_ok") is True
        and dashboard_payload.get("review_hardening", {}).get("figure_parameter_ledger_ok") is True
        and dashboard_payload.get("review_hardening", {}).get("qrf_label_ablation_ok") is True
        and dashboard_payload.get("review_hardening", {}).get("quantum_crosscheck_ok") is True
        and dashboard_payload.get("review_hardening", {}).get("bmr_alternative_ok") is True
        and dashboard_payload.get("review_hardening", {}).get("public_reproduction_status") == "blocked_external_publication"
        and dashboard_payload.get("manuscript_audits", {}).get("figure_placement_ok") is True
        and _exists(project_root, "output/dashboard/index.html")
        and "not empirical" in dashboard_payload.get("claim_boundary", "")
    )
    reference_audit = _load_json(project_root, "output/data/manuscript_reference_audit.json")
    checks["manuscript_reference_audit_ok"] = (
        reference_audit.get("schema") == "realizing_emptiness.manuscript_reference_audit.v1"
        and reference_audit.get("ok") is True
        and reference_audit.get("unresolved_references") == []
        and reference_audit.get("duplicate_anchors") == []
        and reference_audit.get("hardcoded_figure_numbers") == []
        and reference_audit.get("section_reference_count", 0) >= 4
        and reference_audit.get("figure_reference_count", 0) >= 10
        and reference_audit.get("equation_reference_count", 0) >= 4
    )
    figure_reuse = _load_json(project_root, "output/data/figure_reuse_audit.json")
    checks["figure_reuse_audit_ok"] = (
        figure_reuse.get("schema") == "realizing_emptiness.figure_reuse_audit.v1"
        and figure_reuse.get("ok") is True
        and figure_reuse.get("duplicate_supplement_paths") == []
    )
    placement = _load_json(project_root, "output/data/manuscript_figure_placement_audit.json")
    checks["manuscript_figure_placement_audit_ok"] = (
        placement.get("schema") == "realizing_emptiness.manuscript_figure_placement_audit.v1"
        and placement.get("ok") is True
        and placement.get("technical_quantum_figures_in_main") == []
        and placement.get("technical_quantum_figures_missing_from_supplement") == []
        and placement.get("governance_figures_in_main") == []
        and placement.get("governance_figures_missing_from_supplement") == []
        and placement.get("governance_figures_repeated_in_supplement") == []
        and placement.get("controls", {}).get("compact_quantum_summary_in_main") is True
        and placement.get("controls", {}).get("compact_quantum_summary_not_in_supplement") is True
        and placement.get("controls", {}).get("technical_quantum_figures_absent_from_main") is True
        and placement.get("controls", {}).get("technical_quantum_figures_present_in_supplement") is True
        and placement.get("controls", {}).get("governance_figures_absent_from_main") is True
        and placement.get("controls", {}).get("governance_figures_present_once_in_supplement") is True
        and placement.get("controls", {}).get("qrf_lead_figures_present_in_main") is True
        and placement.get("controls", {}).get("qrf_lead_figures_ordered") is True
        and placement.get("controls", {}).get("qrf_figures_precede_quantum_summary") is True
        and placement.get("controls", {}).get("retired_qrf_composite_absent") is True
        and "not empirical" in placement.get("claim_boundary", "")
    )
    cover_audit = _load_json(project_root, "output/data/cover_graphical_abstract_audit.json")
    checks["cover_graphical_abstract_audit_ok"] = (
        cover_audit.get("schema") == "realizing_emptiness.cover_graphical_abstract_audit.v1"
        and cover_audit.get("ok") is True
        and cover_audit.get("figure_exists") is True
        and cover_audit.get("aspect_ratio_ok") is True
        and cover_audit.get("dimensions_ok") is True
        and cover_audit.get("referenced_in_abstract") is True
        and cover_audit.get("referenced_in_title_preamble") is True
        and cover_audit.get("numbered_as_figure") is False
        and cover_audit.get("source_mapped") is True
        and cover_audit.get("cover_style") == "hybrid_symbolic_near_square_large_type"
    )
    variables_path = project_root / "output" / "data" / "manuscript_variables.json"
    variables = json.loads(variables_path.read_text(encoding="utf-8")) if variables_path.exists() else {}
    checks["variables_validation_counts"] = variables.get("VALIDATION_TOTAL_COUNT", 0) >= 10
    hydrated = project_root / "output" / "manuscript"
    unresolved = []
    if hydrated.exists():
        for path in hydrated.glob("*.md"):
            if "{{" in path.read_text(encoding="utf-8"):
                unresolved.append(path.name)
    checks["hydrated_tokens_resolved"] = not unresolved
    subsection_audit = _subsection_anchor_audit(project_root)
    checks["manuscript_subsection_titles_ok"] = subsection_audit.get("ok") is True and subsection_audit.get("row_count", 0) >= 20
    review_gates = [
        row.get("gate", "")
        for row in review_response.get("rows", [])
        if row.get("response_status") in {"implemented_local_delta", "blocked_external_publication"}
    ]
    checks["external_review_response_gates_resolve"] = bool(review_gates) and all(
        gate in checks and checks[gate] for gate in review_gates
    )
    checks["external_review_response_audit_ok"] = (
        checks.get("external_review_response_audit_ok") is True
        and checks["external_review_response_gates_resolve"] is True
    )
    return checks


def write_validation_report(project_root: Path) -> Path:
    """Write validation report to output/reports."""
    checks = validate_outputs(project_root)
    payload = {
        "schema": "realizing_emptiness.validation_report.v1",
        "checks": checks,
        "passed": sum(1 for value in checks.values() if value),
        "total": len(checks),
        "all_passed": all(checks.values()),
    }
    path = project_root / "output" / "reports" / "validation_report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _tracked_doc_paths(project_root: Path) -> list[Path]:
    """Return the documentation files governed by the contract."""
    docs = [project_root / name for name in ("README.md", "AGENTS.md", "ISA.md", "TODO.md")]
    docs.extend(sorted((project_root / "docs").rglob("*.md")))
    return [path for path in docs if path.exists()]


def check_documentation_contract(project_root: Path) -> list[str]:
    """Check project docs for stale identity, machine paths, orphans, and broken links."""
    issues: list[str] = []
    for relative in ("README.md", "AGENTS.md", "TODO.md"):
        text = (project_root / relative).read_text(encoding="utf-8")
        if "template_active_inference" in text:
            issues.append(f"{relative} contains stale template_active_inference text")

    # Fail-closed machine-path guard: no absolute /Users/ path may leak into any
    # tracked doc (confidentiality + portability). Use <template-checkout> instead.
    for path in _tracked_doc_paths(project_root):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "/Users/" in line:
                issues.append(
                    f"{path.relative_to(project_root)}:{lineno} leaks an absolute /Users/ machine path; "
                    "use <template-checkout> or a relative path"
                )

    # No-orphan guard: every reference doc must be linked from a navigation hub so
    # added docs cannot silently become undiscoverable.
    docs_dir = project_root / "docs"
    if docs_dir.exists():
        hub_texts = []
        for hub in (project_root / "README.md", docs_dir / "README.md"):
            if hub.exists():
                hub_texts.append(hub.read_text(encoding="utf-8"))
        hub_blob = "\n".join(hub_texts)
        for doc in sorted(docs_dir.glob("*.md")):
            if doc.name in {"README.md", "AGENTS.md"}:
                continue
            # Match the file inside a Markdown link target, not as a bare substring, so a doc named
            # `inventory.md` is not considered linked merely because `method-inventory.md` appears.
            if f"({doc.name})" not in hub_blob and f"/{doc.name})" not in hub_blob:
                issues.append(
                    f"docs/{doc.name} is orphaned: link it from README.md or docs/README.md"
                )

    markdown_link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in [project_root / "README.md", project_root / "AGENTS.md", docs_dir / "README.md"]:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for raw in markdown_link.findall(text):
            if raw.startswith(("http://", "https://", "#")):
                continue
            target = raw.split("#", 1)[0]
            if target and not (path.parent / target).exists():
                issues.append(f"{path.name} has broken local link: {raw}")
    return issues
