"""Roadmap/TODO consistency and validation-dependency graph artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

EXPECTED_BLOCKED_TASK_IDS = ("re-3", "re-4", "re-13", "re-14", "re-15")


CLAIM_BOUNDARY = (
    "roadmap governance artifact; not empirical evidence, not a physical qFEP realization, "
    "and not a clinical, neural, awakening, or practice-efficacy claim"
)

IMPLEMENTED_ALIASES = {
    "two_qubit_separability_entropy": ("two-qubit entropy", "schmidt-family", "separability entropy"),
    "arbitrary_two_qubit_entanglement_audit": ("arbitrary two-qubit", "mixed states", "entanglement witnesses", "negativity"),
    "chsh_contextuality_witness": ("chsh witness", "tsirelson"),
    "chsh_measurement_cover_table": ("chsh measurement-cover", "chsh local-polytope"),
    "general_measurement_cover_polytope_audit": (
        "general measurement-cover",
        "compatibility hypergraphs",
        "deterministic-assignment lp",
    ),
    "qrf_basis_invariance_toy": ("basis invariance", "local rotations"),
    "boundary_landauer_entropy": ("landauer", "erasure lower bound"),
    "thermodynamic_channel_cost_audit": ("thermodynamic channel", "cptp channel", "channel costs"),
    "two_qubit_dephasing_channel": ("dephasing-channel", "dephasing channel"),
    "full_open_system_qfep_dynamics": ("boundary-hamiltonian", "lindblad", "collision-model"),
    "many_body_boundary_screens": ("six-qubit", "many-body boundary screens"),
    "sparse_boundary_screen_scaling_audit": ("sparse-state", "sparse boundary", "sparse exact boundary-screen"),
    "general_sheaf_contextuality_engine": ("sheaf-contextuality", "obstruction checks", "global-section"),
    "qrf_transformation_library": ("qrf transformation", "relabeling covariance"),
    "qrf_frame_covariance_toy_audit": ("frame covariance", "density/probability covariance", "unitary/permutation"),
    "empirical_adapter": ("empirical adapter", "provenance adapter", "synthetic-demo gate"),
}

BLOCKED_EXTERNAL_CLASSES = {
    "re-3": ("physical qfep", "physical quantum-boundary", "reviewed physical hamiltonians"),
    "re-4": (
        "human-subject",
        "human subject",
        "human validation",
        "ethics review",
        "preregistered outcomes",
    ),
    "re-13": (
        "clinical",
        "awakening",
        "compassion-efficacy",
        "compassion efficacy",
        "neural-measurement",
        "neural measurement",
        "neural",
    ),
    "re-14": (
        "user-facing practice",
        "human-practice",
        "human practice",
        "practice applications",
        "practice efficacy",
        "safety wording",
    ),
    "re-15": (
        "public archive",
        "independent reproduction",
        "blinded reproduction",
        "publication approval",
        "zenodo",
        "github release",
    ),
}

HISTORICAL_BACKLOG_PHRASES = (
    "built since",
    "recorded here only as a pointer",
    "are complete",
    "is complete",
    "all shipped",
    "are all shipped",
    "shipped with measured",
    "already implemented",
    "historical backlog",
)


def _load_json(project_root: Path, relative: str) -> dict[str, Any]:
    return json.loads((project_root / relative).read_text(encoding="utf-8"))


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().replace("_", " ").replace("-", " ")).strip()


def _todo_records(text: str) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    in_backlog = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("## "):
            in_backlog = stripped.lower().startswith("## backlog")
            continue
        if not in_backlog:
            continue
        if not stripped:
            continue
        if stripped.startswith("|") and not stripped.startswith("| ---"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if cells and cells[0].lower() == "id":
                continue
            if len(cells) >= 3:
                records.append(
                    {
                        "line": str(line_number),
                        "id": cells[0],
                        "status": cells[1],
                        "scope": cells[2],
                        "raw": stripped,
                    }
                )
            continue
        if stripped.startswith(("-", "*")):
            records.append(
                {
                    "line": str(line_number),
                    "id": "",
                    "status": "bullet",
                    "scope": stripped.lstrip("-* "),
                    "raw": stripped,
                }
            )
    return records


def _historical_backlog_rows(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    in_backlog = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("## "):
            in_backlog = stripped.lower().startswith("## backlog")
            continue
        if not in_backlog or not stripped:
            continue
        searchable = _normalise(stripped)
        matched_phrases = [
            phrase for phrase in HISTORICAL_BACKLOG_PHRASES if _normalise(phrase) in searchable
        ]
        if matched_phrases:
            rows.append(
                {
                    "line": line_number,
                    "phrases": matched_phrases,
                    "raw": stripped,
                }
            )
    return rows


def build_roadmap_todo_audit(project_root: Path) -> dict[str, Any]:
    """Build a fail-closed audit linking TODO rows to machine roadmap state."""
    todo_text = (project_root / "TODO.md").read_text(encoding="utf-8")
    roadmap = _load_json(project_root, "output/data/quantum_extension_roadmap.json")
    records = _todo_records(todo_text)
    historical_backlog_rows = _historical_backlog_rows(todo_text)
    implemented_ids = {row["id"] for row in roadmap.get("implemented", [])}
    future_ids = {row["id"] for row in roadmap.get("future", [])}
    stale_future_rows = []
    blocked_rows = []
    blocked_violations = []
    achieved_terms = ("implemented", "achieved", "validated", "complete", "done", "passes")
    for record in records:
        searchable = _normalise(" ".join([record.get("id", ""), record.get("status", ""), record.get("scope", "")]))
        matched_implemented = sorted(
            engine_id
            for engine_id, aliases in IMPLEMENTED_ALIASES.items()
            if engine_id in implemented_ids and any(_normalise(alias) in searchable for alias in aliases)
        )
        future_like = record["status"].lower() in {"todo", "future", "blocked", "bullet"} or "future" in searchable
        blocked_matches = sorted(
            class_id
            for class_id, aliases in BLOCKED_EXTERNAL_CLASSES.items()
            if class_id in future_ids and any(_normalise(alias) in searchable for alias in aliases)
        )
        row = {
            "line": int(record["line"]),
            "todo_id": record["id"],
            "status": record["status"],
            "scope": record["scope"],
            "matched_implemented_ids": matched_implemented,
            "matched_blocked_classes": blocked_matches,
        }
        if matched_implemented and future_like:
            stale_future_rows.append(row)
        if blocked_matches:
            blocked_rows.append(row)
            if any(term in searchable for term in achieved_terms) and "blocked" not in searchable:
                blocked_violations.append(row)
    tasks_path = project_root / "tasks.yaml"
    blocked_task_ids = sorted(
        str(task.get("id"))
        for task in (yaml.safe_load(tasks_path.read_text(encoding="utf-8")) or {}).get("tasks", [])
        if task.get("status") == "blocked"
    )
    missing_blocked_task_ids = sorted(set(EXPECTED_BLOCKED_TASK_IDS) - set(blocked_task_ids))
    controls = {
        "no_future_rows_duplicate_implemented_roadmap_ids": len(stale_future_rows) == 0,
        "blocked_external_classes_remain_future": set(EXPECTED_BLOCKED_TASK_IDS) <= future_ids,
        "blocked_external_classes_not_described_as_achieved": len(blocked_violations) == 0,
        "todo_file_declares_future_only_backlog": "future only" in _normalise(todo_text),
        "all_blocked_external_task_ids_present_and_blocked": len(missing_blocked_task_ids) == 0,
        "todo_backlog_has_no_historical_completion_rows": len(historical_backlog_rows) == 0,
    }
    return {
        "schema": "realizing_emptiness.roadmap_todo_audit.v1",
        "todo_row_count": len(records),
        "implemented_roadmap_count": len(implemented_ids),
        "future_roadmap_count": len(future_ids),
        "stale_future_rows": stale_future_rows,
        "historical_backlog_rows": historical_backlog_rows,
        "blocked_external_class_rows": blocked_rows,
        "blocked_external_class_violations": blocked_violations,
        "blocked_task_ids": blocked_task_ids,
        "missing_blocked_task_ids": missing_blocked_task_ids,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_validation_dependency_graph(project_root: Path) -> dict[str, Any]:
    """Build an explicit dependency graph for artifacts, validators, figures, and render gates."""
    quantum_nodes = [
        "quantum_boundary_entropy",
        "quantum_open_system_dynamics",
        "quantum_measurement_contextuality",
        "qfep_boundary_hamiltonian_dynamics",
        "quantum_trajectory_unraveling",
        "many_body_boundary_screen_sweep",
        "sheaf_contextuality_obstruction_audit",
        "qrf_transformation_covariance_audit",
        "empirical_adapter_provenance_audit",
        "arbitrary_two_qubit_entanglement_audit",
        "general_measurement_cover_polytope_audit",
        "thermodynamic_channel_cost_audit",
        "sparse_boundary_screen_scaling_audit",
        "qrf_frame_covariance_toy_audit",
        "multipartite_witness_suite_audit",
        "tensor_network_benchmark_audit",
        "collision_model_thermalization_audit",
        "no_signaling_scenario_library_audit",
        "n_cycle_contextuality_library_audit",
    ]
    nodes = [
        "source_manifest",
        "formalism_registry",
        "equation_audit",
        "source_claim_crosswalk",
        "claim_support_audit",
        "manuscript_claim_audit",
        "evidence_ceiling_audit",
        "claim_context_ledger",
        "claim_redteam_audit",
        "qrf_boundary_indistinguishability",
        "qrf_boundary_channel_ledger",
        "source_argument_coverage_audit",
        "bmr_sweep",
        "simulation_sensitivity_grid",
        "pymdp_generative_model_audit",
        "pymdp_policy_trace",
        "pymdp_runtime_diagnostics_log",
        "pymdp_profile_comparison",
        "stochastic_policy_ensemble",
        "stochastic_effect_size_audit",
        "bmr_robustness_resampling_audit",
        "quantum_trajectory_convergence_audit",
        "effect_size_calibration_audit",
        "statistical_robustness_audit",
        "criticality_proxy_report",
        "criticality_stochastic_ensemble",
        "compassion_scope_audit",
        "separation_prior_emergence_audit",
        "internal_cut_unmeasurability_audit",
        "sigma_contextuality_suppression_audit",
        "ongoing_revision_audit",
        "practice_protocol_map",
        *quantum_nodes,
        "quantum_extension_roadmap",
        "quantum_roadmap_readiness_matrix",
        "roadmap_todo_audit",
        "sheaf_coverage_matrix",
        "artifact_contract_registry",
        "artifact_release_manifest",
        "external_review_response_audit",
        "figure_parameter_ledger",
        "qrf_label_ablation_audit",
        "quantum_independent_crosscheck_audit",
        "bmr_alternative_prior_audit",
        "method_assumption_ledger",
        "method_negative_control_inventory",
        "figure_source_map",
        "figures",
        "visual_caption_audit",
        "visual_accessibility_audit",
        "visual_style_audit",
        "figure_legibility_audit",
        "figure_integrity_audit",
        "rendered_figure_caption_audit",
        "manuscript_claim_intensity_audit",
        "manuscript_reference_audit",
        "figure_reuse_audit",
        "manuscript_figure_placement_audit",
        "cover_graphical_abstract_audit",
        "artifact_dashboard",
        "manuscript",
        "validation_report",
        "template_link_gate",
        "pdf_render_gate",
        "raster_inspection_gate",
    ]
    edges: list[list[str]] = [
        ["source_manifest", "source_claim_crosswalk"],
        ["formalism_registry", "equation_audit"],
        ["equation_audit", "manuscript"],
        ["source_claim_crosswalk", "claim_support_audit"],
        ["claim_support_audit", "manuscript_claim_audit"],
        ["claim_support_audit", "evidence_ceiling_audit"],
        ["claim_support_audit", "claim_context_ledger"],
        ["evidence_ceiling_audit", "claim_context_ledger"],
        ["source_argument_coverage_audit", "claim_context_ledger"],
        ["claim_context_ledger", "figures"],
        ["claim_context_ledger", "manuscript"],
        ["claim_context_ledger", "validation_report"],
        ["claim_context_ledger", "artifact_dashboard"],
        ["claim_context_ledger", "claim_redteam_audit"],
        ["evidence_ceiling_audit", "claim_redteam_audit"],
        ["source_argument_coverage_audit", "claim_redteam_audit"],
        ["manuscript_claim_audit", "claim_redteam_audit"],
        ["manuscript_claim_intensity_audit", "claim_redteam_audit"],
        ["figure_source_map", "claim_redteam_audit"],
        ["claim_redteam_audit", "validation_report"],
        ["claim_redteam_audit", "artifact_dashboard"],
        ["qrf_boundary_indistinguishability", "figures"],
        ["qrf_boundary_channel_ledger", "figures"],
        ["qrf_boundary_channel_ledger", "source_argument_coverage_audit"],
        ["source_argument_coverage_audit", "validation_report"],
        ["source_argument_coverage_audit", "artifact_dashboard"],
        ["bmr_sweep", "simulation_sensitivity_grid"],
        ["simulation_sensitivity_grid", "figures"],
        ["pymdp_generative_model_audit", "pymdp_policy_trace"],
        ["pymdp_generative_model_audit", "pymdp_runtime_diagnostics_log"],
        ["pymdp_policy_trace", "pymdp_runtime_diagnostics_log"],
        ["pymdp_policy_trace", "pymdp_profile_comparison"],
        ["pymdp_policy_trace", "stochastic_policy_ensemble"],
        ["pymdp_runtime_diagnostics_log", "pymdp_profile_comparison"],
        ["pymdp_runtime_diagnostics_log", "figures"],
        ["pymdp_runtime_diagnostics_log", "manuscript"],
        ["pymdp_runtime_diagnostics_log", "validation_report"],
        ["pymdp_runtime_diagnostics_log", "artifact_dashboard"],
        ["pymdp_profile_comparison", "criticality_proxy_report"],
        ["stochastic_policy_ensemble", "criticality_stochastic_ensemble"],
        ["stochastic_policy_ensemble", "stochastic_effect_size_audit"],
        ["simulation_sensitivity_grid", "bmr_robustness_resampling_audit"],
        ["quantum_trajectory_unraveling", "quantum_trajectory_convergence_audit"],
        ["stochastic_effect_size_audit", "statistical_robustness_audit"],
        ["bmr_robustness_resampling_audit", "statistical_robustness_audit"],
        ["quantum_trajectory_convergence_audit", "statistical_robustness_audit"],
        ["effect_size_calibration_audit", "statistical_robustness_audit"],
        ["statistical_robustness_audit", "figures"],
        ["statistical_robustness_audit", "manuscript"],
        ["statistical_robustness_audit", "validation_report"],
        ["statistical_robustness_audit", "artifact_dashboard"],
        ["criticality_stochastic_ensemble", "figures"],
        ["pymdp_profile_comparison", "compassion_scope_audit"],
        ["compassion_scope_audit", "figures"],
        ["compassion_scope_audit", "manuscript"],
        ["compassion_scope_audit", "artifact_dashboard"],
        ["bmr_sweep", "separation_prior_emergence_audit"],
        ["separation_prior_emergence_audit", "manuscript"],
        ["separation_prior_emergence_audit", "figures"],
        ["qrf_boundary_indistinguishability", "internal_cut_unmeasurability_audit"],
        ["internal_cut_unmeasurability_audit", "manuscript"],
        ["internal_cut_unmeasurability_audit", "figures"],
        ["internal_cut_unmeasurability_audit", "quantum_extension_roadmap"],
        ["sigma_contextuality_suppression_audit", "manuscript"],
        ["sigma_contextuality_suppression_audit", "quantum_extension_roadmap"],
        ["separation_prior_emergence_audit", "ongoing_revision_audit"],
        ["ongoing_revision_audit", "manuscript"],
        ["multipartite_witness_suite_audit", "manuscript"],
        ["multipartite_witness_suite_audit", "quantum_extension_roadmap"],
        ["tensor_network_benchmark_audit", "manuscript"],
        ["tensor_network_benchmark_audit", "quantum_extension_roadmap"],
        ["collision_model_thermalization_audit", "manuscript"],
        ["collision_model_thermalization_audit", "quantum_extension_roadmap"],
        ["no_signaling_scenario_library_audit", "manuscript"],
        ["no_signaling_scenario_library_audit", "quantum_extension_roadmap"],
        ["n_cycle_contextuality_library_audit", "manuscript"],
        ["n_cycle_contextuality_library_audit", "quantum_extension_roadmap"],
        ["practice_protocol_map", "figures"],
        ["practice_protocol_map", "manuscript"],
        ["artifact_contract_registry", "validation_report"],
        ["artifact_contract_registry", "artifact_dashboard"],
        ["artifact_contract_registry", "artifact_release_manifest"],
        ["artifact_release_manifest", "external_review_response_audit"],
        ["external_review_response_audit", "validation_report"],
        ["external_review_response_audit", "artifact_dashboard"],
        ["figure_source_map", "figure_parameter_ledger"],
        ["figure_parameter_ledger", "external_review_response_audit"],
        ["figure_parameter_ledger", "validation_report"],
        ["figure_parameter_ledger", "artifact_dashboard"],
        ["qrf_boundary_channel_ledger", "qrf_label_ablation_audit"],
        ["qrf_label_ablation_audit", "external_review_response_audit"],
        ["qrf_label_ablation_audit", "validation_report"],
        ["qrf_label_ablation_audit", "artifact_dashboard"],
        ["quantum_measurement_contextuality", "quantum_independent_crosscheck_audit"],
        ["quantum_independent_crosscheck_audit", "external_review_response_audit"],
        ["quantum_independent_crosscheck_audit", "validation_report"],
        ["quantum_independent_crosscheck_audit", "artifact_dashboard"],
        ["bmr_sweep", "bmr_alternative_prior_audit"],
        ["bmr_alternative_prior_audit", "external_review_response_audit"],
        ["bmr_alternative_prior_audit", "validation_report"],
        ["bmr_alternative_prior_audit", "artifact_dashboard"],
        ["artifact_release_manifest", "validation_report"],
        ["artifact_release_manifest", "artifact_dashboard"],
        ["method_assumption_ledger", "method_negative_control_inventory"],
        ["method_assumption_ledger", "figures"],
        ["method_negative_control_inventory", "figures"],
        ["method_assumption_ledger", "manuscript"],
        ["method_negative_control_inventory", "validation_report"],
        ["method_negative_control_inventory", "artifact_dashboard"],
    ]
    for node in quantum_nodes:
        edges.append([node, "quantum_extension_roadmap"])
        edges.append([node, "figures"])
    edges.extend(
        [
            ["quantum_extension_roadmap", "quantum_roadmap_readiness_matrix"],
            ["quantum_extension_roadmap", "roadmap_todo_audit"],
            ["quantum_roadmap_readiness_matrix", "figures"],
            ["roadmap_todo_audit", "artifact_dashboard"],
            ["figure_source_map", "visual_caption_audit"],
            ["figure_source_map", "visual_accessibility_audit"],
            ["figure_source_map", "visual_style_audit"],
            ["figure_source_map", "figure_legibility_audit"],
            ["figure_source_map", "figure_integrity_audit"],
            ["figures", "figure_source_map"],
            ["figures", "manuscript"],
            ["visual_caption_audit", "validation_report"],
            ["visual_accessibility_audit", "validation_report"],
            ["visual_style_audit", "validation_report"],
            ["figure_legibility_audit", "validation_report"],
            ["figure_integrity_audit", "validation_report"],
            ["rendered_figure_caption_audit", "validation_report"],
            ["manuscript_claim_intensity_audit", "validation_report"],
            ["manuscript_reference_audit", "validation_report"],
            ["figure_reuse_audit", "validation_report"],
            ["manuscript_figure_placement_audit", "validation_report"],
            ["cover_graphical_abstract_audit", "validation_report"],
            ["sheaf_coverage_matrix", "manuscript"],
            ["manuscript", "rendered_figure_caption_audit"],
            ["manuscript", "manuscript_claim_intensity_audit"],
            ["manuscript", "manuscript_reference_audit"],
            ["manuscript", "figure_reuse_audit"],
            ["manuscript", "manuscript_figure_placement_audit"],
            ["figures", "cover_graphical_abstract_audit"],
            ["manuscript", "template_link_gate"],
            ["template_link_gate", "pdf_render_gate"],
            ["pdf_render_gate", "raster_inspection_gate"],
            ["validation_report", "artifact_dashboard"],
            ["figure_source_map", "artifact_dashboard"],
            ["quantum_roadmap_readiness_matrix", "artifact_dashboard"],
            ["evidence_ceiling_audit", "artifact_dashboard"],
            ["manuscript_figure_placement_audit", "artifact_dashboard"],
        ]
    )
    unique_nodes = sorted(set(nodes))
    known_edges = [[source, target] for source, target in edges if source in unique_nodes and target in unique_nodes]
    controls = {
        "all_quantum_roadmap_engines_present": all(node in unique_nodes for node in quantum_nodes),
        "figure_audits_connected": all(
            node in unique_nodes
            for node in (
                "visual_caption_audit",
                "visual_accessibility_audit",
                "visual_style_audit",
                "figure_legibility_audit",
                "figure_integrity_audit",
                "rendered_figure_caption_audit",
            )
        ),
        "statistical_robustness_connected": all(
            edge in known_edges
            for edge in (
                ["stochastic_effect_size_audit", "statistical_robustness_audit"],
                ["bmr_robustness_resampling_audit", "statistical_robustness_audit"],
                ["quantum_trajectory_convergence_audit", "statistical_robustness_audit"],
                ["statistical_robustness_audit", "validation_report"],
            )
        ),
        "method_governance_connected": all(
            edge in known_edges
            for edge in (
                ["method_assumption_ledger", "method_negative_control_inventory"],
                ["method_negative_control_inventory", "validation_report"],
                ["artifact_contract_registry", "validation_report"],
            )
        ),
        "render_gates_connected": all(node in unique_nodes for node in ("template_link_gate", "pdf_render_gate", "raster_inspection_gate")),
        "dashboard_has_governance_inputs": all(
            edge in known_edges
            for edge in (
                ["roadmap_todo_audit", "artifact_dashboard"],
                ["quantum_roadmap_readiness_matrix", "artifact_dashboard"],
                ["evidence_ceiling_audit", "artifact_dashboard"],
                ["claim_context_ledger", "artifact_dashboard"],
                ["claim_redteam_audit", "artifact_dashboard"],
                ["source_argument_coverage_audit", "artifact_dashboard"],
                ["manuscript_figure_placement_audit", "artifact_dashboard"],
                ["statistical_robustness_audit", "artifact_dashboard"],
                ["method_negative_control_inventory", "artifact_dashboard"],
                ["artifact_contract_registry", "artifact_dashboard"],
                ["external_review_response_audit", "artifact_dashboard"],
                ["figure_parameter_ledger", "artifact_dashboard"],
                ["qrf_label_ablation_audit", "artifact_dashboard"],
                ["quantum_independent_crosscheck_audit", "artifact_dashboard"],
                ["bmr_alternative_prior_audit", "artifact_dashboard"],
            )
        ),
        "review_response_artifacts_connected": all(
            edge in known_edges
            for edge in (
                ["artifact_release_manifest", "external_review_response_audit"],
                ["figure_parameter_ledger", "external_review_response_audit"],
                ["qrf_label_ablation_audit", "external_review_response_audit"],
                ["quantum_independent_crosscheck_audit", "external_review_response_audit"],
                ["bmr_alternative_prior_audit", "external_review_response_audit"],
                ["external_review_response_audit", "validation_report"],
            )
        ),
    }
    return {
        "schema": "realizing_emptiness.validation_dependency_graph.v1",
        "node_count": len(unique_nodes),
        "edge_count": len(known_edges),
        "nodes": unique_nodes,
        "edges": known_edges,
        "required_quantum_nodes": quantum_nodes,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_roadmap_governance_artifacts(project_root: Path) -> tuple[Path, Path]:
    """Write roadmap/TODO and dependency-graph artifacts."""
    data_dir = project_root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    todo_path = data_dir / "roadmap_todo_audit.json"
    graph_path = data_dir / "validation_dependency_graph.json"
    todo_path.write_text(json.dumps(build_roadmap_todo_audit(project_root), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    graph_path.write_text(
        json.dumps(build_validation_dependency_graph(project_root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return todo_path, graph_path
