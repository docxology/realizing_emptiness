"""Source-argument coverage audit for the Sandved-Smith no-self-evidence paper."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


CLAIM_BOUNDARY = (
    "source-argument coverage audit for manuscript relevance; not empirical, clinical, neural, "
    "practice-efficacy, awakening, or physical qFEP evidence"
)


CORE_ROWS: tuple[dict[str, Any], ...] = (
    {
        "theme_id": "no_self_evidence_boundary",
        "source_locator": "Sections 3.1-3.2",
        "source_equations": [],
        "local_sections": [
            "sec:methods-finite-qrf-boundary-screen",
            "sec:results-qrf-boundary-geometry",
            "sec:discussion-no-self-evidence-boundary",
        ],
        "artifact_paths": [
            "output/data/source_claim_crosswalk.json",
            "output/data/qrf_boundary_indistinguishability.json",
            "output/data/qrf_boundary_channel_ledger.json",
        ],
        "validation_gates": ["claim_support_audit_ok", "qrf_indistinguishable", "qrf_boundary_channel_ledger_ok"],
        "evidence_ceiling_claims": ["source_boundary_unevidenceable"],
        "primary_coverage_class": "qrf_boundary_argument",
    },
    {
        "theme_id": "qrf_sectorisation_equations_7_to_10",
        "source_locator": "Section 3.2, equations 7-10",
        "source_equations": [7, 8, 9, 10],
        "local_sections": [
            "sec:methods-finite-qrf-boundary-screen",
            "sec:methods-separation-prior-subspace",
            "sec:results-qrf-boundary-geometry",
        ],
        "artifact_paths": [
            "output/data/formalism_registry.json",
            "output/data/equation_audit.json",
            "output/data/qrf_boundary_channel_ledger.json",
        ],
        "validation_gates": ["equation_count_14", "qrf_boundary_channel_ledger_ok"],
        "evidence_ceiling_claims": ["source_boundary_unevidenceable", "separation_prior_sigma"],
        "primary_coverage_class": "qrf_boundary_argument",
    },
    {
        "theme_id": "separation_prior_sigma",
        "source_locator": "Equation 10 and Section 4.1",
        "source_equations": [10],
        "local_sections": [
            "sec:methods-separation-prior-subspace",
            "sec:methods-bmr-separation-prior",
            "sec:results-bmr-sensitivity",
        ],
        "artifact_paths": [
            "output/data/formalism_registry.json",
            "output/data/bmr_sweep.json",
            "output/data/simulation_sensitivity_grid.json",
        ],
        "validation_gates": ["equation_count_14", "bmr_pruning_edges", "simulation_sensitivity_grid_ok"],
        "evidence_ceiling_claims": ["separation_prior_sigma", "metacognitive_access_model"],
        "primary_coverage_class": "active_inference_bmr_argument",
    },
    {
        "theme_id": "opacification_and_metacognitive_access",
        "source_locator": "Section 4.2",
        "source_equations": [],
        "local_sections": [
            "sec:methods-pymdp-generative-models",
            "sec:results-pymdp-policy-trace",
            "sec:discussion-practice-interface-boundaries",
        ],
        "artifact_paths": [
            "output/data/pymdp_profile_comparison.json",
            "output/data/stochastic_policy_ensemble.json",
            "output/data/simulation_sensitivity_grid.json",
        ],
        "validation_gates": ["pymdp_profiles", "stochastic_policy_ensemble_ok", "simulation_sensitivity_grid_ok"],
        "evidence_ceiling_claims": ["metacognitive_access_model", "practice_protocol_boundary"],
        "primary_coverage_class": "active_inference_bmr_argument",
    },
    {
        "theme_id": "bmr_pruning_of_sigma",
        "source_locator": "Section 4.3, equations 11-12",
        "source_equations": [11, 12],
        "local_sections": [
            "sec:methods-bmr-separation-prior",
            "sec:results-bmr-sensitivity",
            "sec:discussion-evidence-ceilings",
        ],
        "artifact_paths": [
            "output/data/bmr_sweep.json",
            "output/data/bmr_robustness_resampling_audit.json",
        ],
        "validation_gates": ["bmr_pruning_edges", "bmr_robustness_resampling_audit_ok"],
        "evidence_ceiling_claims": ["bmr_prunes_sigma"],
        "primary_coverage_class": "active_inference_bmr_argument",
    },
    {
        "theme_id": "post_dual_unconstrained_qrf_space",
        "source_locator": "Section 5.1, equations 13-14",
        "source_equations": [13, 14],
        "local_sections": [
            "sec:methods-pymdp-generative-models",
            "sec:results-pymdp-policy-trace",
            "sec:discussion-no-self-evidence-boundary",
        ],
        "artifact_paths": [
            "output/data/pymdp_profile_comparison.json",
            "output/data/pymdp_policy_trace.json",
            "output/data/qrf_boundary_channel_ledger.json",
        ],
        "validation_gates": ["pymdp_profiles", "pymdp_policy_trace_ok", "qrf_boundary_channel_ledger_ok"],
        "evidence_ceiling_claims": ["source_boundary_unevidenceable", "pymdp_runtime_canary"],
        "primary_coverage_class": "active_inference_bmr_argument",
    },
    {
        "theme_id": "contextuality_of_boundary",
        "source_locator": "Section 6.1",
        "source_equations": [],
        "local_sections": [
            "sec:results-finite-quantum-scope",
            "sec:supplement-finite-quantum-contextuality-audits",
            "sec:discussion-finite-engine-limits",
        ],
        "artifact_paths": [
            "output/data/quantum_measurement_contextuality.json",
            "output/data/sheaf_contextuality_obstruction_audit.json",
            "output/data/general_measurement_cover_polytope_audit.json",
        ],
        "validation_gates": [
            "quantum_measurement_contextuality_ok",
            "sheaf_contextuality_obstruction_audit_ok",
            "general_measurement_cover_polytope_audit_ok",
        ],
        "evidence_ceiling_claims": ["quantum_contextuality_witness", "quantum_measurement_contextuality"],
        "primary_coverage_class": "supplemental_quantum_contextuality_support",
    },
    {
        "theme_id": "compassion_as_policy_scope",
        "source_locator": "Section 6.2",
        "source_equations": [],
        "local_sections": [
            "sec:supplement-bounded-practice-protocols",
            "sec:supplement-compassion-policy-scope",
            "sec:discussion-compassion-boundary",
        ],
        "artifact_paths": ["output/data/practice_protocol_map.json"],
        "validation_gates": ["practice_boundaries"],
        "evidence_ceiling_claims": ["compassion_proxy_boundary", "practice_protocol_boundary"],
        "primary_coverage_class": "bounded_proxy_argument",
    },
    {
        "theme_id": "criticality_prediction_boundary",
        "source_locator": "Section 6.3",
        "source_equations": [],
        "local_sections": [
            "sec:supplement-criticality-proxies",
            "sec:discussion-criticality-proxy-boundary",
            "sec:supplement-meta-manuscript-record",
        ],
        "artifact_paths": [
            "output/data/criticality_stochastic_ensemble.json",
            "output/data/stochastic_effect_size_audit.json",
        ],
        "validation_gates": ["criticality_stochastic_ensemble_ok", "stochastic_effect_size_audit_ok"],
        "evidence_ceiling_claims": ["criticality_proxy_boundary"],
        "primary_coverage_class": "bounded_proxy_argument",
    },
)


def _declared_section_anchors(project_root: Path) -> set[str]:
    """Return anchors declared by the sheaf manifest/tracks plus composed files."""
    anchors: set[str] = set()
    tracks_path = project_root / "manuscript" / "sheaf" / "tracks.yaml"
    manifest_path = project_root / "manuscript" / "sheaf" / "manifest.yaml"
    if tracks_path.exists() and manifest_path.exists():
        tracks_payload = yaml.safe_load(tracks_path.read_text(encoding="utf-8"))
        manifest_payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        declared = tracks_payload.get("section_anchors", {})
        for section in manifest_payload.get("sections", []):
            section_id = section.get("id", "")
            anchors.add(f"sec:{section_id}")
            for track_id in section.get("tracks", []):
                anchors.add(
                    declared.get(section_id, {}).get(track_id, f"sec:{section_id}-{track_id.replace('_', '-')}")
                )
    for manuscript_path in (project_root / "manuscript").glob("*.md"):
        if manuscript_path.name[:2].isdigit():
            text = manuscript_path.read_text(encoding="utf-8")
            anchors.update(match.split("}", 1)[0] for match in text.split("{#")[1:])
    return anchors


def build_source_argument_coverage_audit(project_root: Path) -> dict[str, Any]:
    """Build coverage rows tying source-paper themes to local sections, artifacts, and gates."""
    rows = []
    declared_anchors = _declared_section_anchors(project_root)
    for row in CORE_ROWS:
        artifact_paths = row["artifact_paths"]
        local_sections = row["local_sections"]
        unresolved_local_sections = sorted(section for section in local_sections if section not in declared_anchors)
        rows.append(
            {
                **row,
                "artifact_paths_exist": all((project_root / path).exists() for path in artifact_paths),
                "local_sections_resolve": not unresolved_local_sections,
                "unresolved_local_sections": unresolved_local_sections,
                "has_evidence_ceiling_claim": bool(row["evidence_ceiling_claims"]),
                "not_quantum_only_for_core_argument": not (
                    row["theme_id"]
                    in {
                        "no_self_evidence_boundary",
                        "qrf_sectorisation_equations_7_to_10",
                        "separation_prior_sigma",
                        "opacification_and_metacognitive_access",
                        "bmr_pruning_of_sigma",
                        "post_dual_unconstrained_qrf_space",
                    }
                    and row["primary_coverage_class"].startswith("supplemental_quantum")
                ),
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    controls = {
        "all_core_themes_mapped": len(rows) == len(CORE_ROWS),
        "all_rows_have_artifacts": all(row["artifact_paths_exist"] for row in rows),
        "all_rows_have_sections": all(bool(row["local_sections"]) for row in rows),
        "all_local_sections_resolve": all(row["local_sections_resolve"] for row in rows),
        "all_rows_have_validation_gates": all(bool(row["validation_gates"]) for row in rows),
        "all_rows_have_evidence_ceiling_claims": all(row["has_evidence_ceiling_claim"] for row in rows),
        "qrf_bmr_opacification_not_quantum_only": all(row["not_quantum_only_for_core_argument"] for row in rows),
    }
    return {
        "schema": "realizing_emptiness.source_argument_coverage_audit.v1",
        "theme_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_source_argument_coverage_audit(project_root: Path) -> Path:
    """Write the source-argument coverage audit artifact."""
    path = project_root / "output" / "data" / "source_argument_coverage_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(build_source_argument_coverage_audit(project_root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path
