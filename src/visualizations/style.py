"""Shared semantic visual style contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
import numpy as np


SEMANTIC_COLORS = {
    "boundary": "#111827",
    "qrf_sector": "#2563eb",
    "pass": "#0f766e",
    "fail": "#92400e",
    "keep": "#6b7280",
    "prune": "#0f766e",
    "finite": "#2563eb",
    "blocked": "#92400e",
    "stochastic": "#7c3aed",
    "null": "#475569",
    "quantum": "#2563eb",
    "source": "#111827",
}

SEMANTIC_HATCHES = {
    "null": "//",
    "blocked": "..",
    "control": "//",
    "obstruction": "..",
    "finite": "",
}

MIN_READABLE_FONT_PT = 12.0
MIN_FIGURE_WIDTH_PX = 1200
MIN_FIGURE_HEIGHT_PX = 600
MIN_NON_TEXT_CONTRAST_RATIO = 3.0
MIN_TEXT_CONTRAST_RATIO = 4.5
STYLE_BACKGROUND_COLOR = "#ffffff"

FIGURE_RENDER_CONTRACTS = {
    "graphical_abstract_cover": {"roles": ["source", "finite", "stochastic", "blocked", "boundary"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "qrf_boundary_screen_geometry": {"roles": ["boundary", "qrf_sector", "finite"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "qrf_channel_relabeling_ledger": {"roles": ["boundary", "qrf_sector", "pass"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "qrf_invariance_policy_flow": {"roles": ["boundary", "pass", "fail", "qrf_sector"], "panel_count": 2, "legend_count": 2, "colorbar_count": 0, "min_font_pt": 12.0},
    "qrf_sectorisation_map": {"roles": ["qrf_sector"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "boundary_indistinguishability": {"roles": ["pass", "boundary"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "qrf_reference_frame_geometry": {"roles": ["boundary", "qrf_sector"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "bmr_free_energy_decomposition": {"roles": ["keep", "prune"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "bmr_pruning_phase_diagram": {"roles": ["keep", "prune"], "panel_count": 1, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "simulation_sensitivity_heatmap": {"roles": ["keep", "prune"], "panel_count": 1, "legend_count": 0, "colorbar_count": 1, "min_font_pt": 12.0},
    "finite_quantum_scope_summary": {"roles": ["quantum", "finite", "blocked"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "quantum_boundary_entropy_landscape": {"roles": ["quantum", "finite"], "panel_count": 4, "legend_count": 4, "colorbar_count": 0, "min_font_pt": 12.0},
    "quantum_contextuality_witness": {"roles": ["quantum", "finite"], "panel_count": 2, "legend_count": 2, "colorbar_count": 2, "min_font_pt": 12.0},
    "quantum_measurement_contextuality_table": {"roles": ["quantum", "null"], "panel_count": 2, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "quantum_local_polytope_audit": {"roles": ["quantum", "null"], "panel_count": 2, "legend_count": 2, "colorbar_count": 0, "min_font_pt": 12.0},
    "quantum_open_system_dynamics": {"roles": ["quantum"], "panel_count": 3, "legend_count": 3, "colorbar_count": 0, "min_font_pt": 12.0},
    "qfep_boundary_hamiltonian_dynamics": {"roles": ["quantum", "finite"], "panel_count": 3, "legend_count": 3, "colorbar_count": 0, "min_font_pt": 12.0},
    "quantum_trajectory_unraveling": {"roles": ["quantum", "stochastic", "blocked"], "panel_count": 3, "legend_count": 3, "colorbar_count": 0, "min_font_pt": 12.0},
    "many_body_boundary_screen_sweep": {"roles": ["quantum", "finite"], "panel_count": 1, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "sheaf_contextuality_obstruction_audit": {"roles": ["pass", "fail"], "panel_count": 2, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "qrf_transformation_covariance_audit": {"roles": ["qrf_sector", "pass", "fail"], "panel_count": 2, "legend_count": 0, "colorbar_count": 1, "min_font_pt": 12.0},
    "empirical_adapter_provenance_audit": {"roles": ["blocked", "pass"], "panel_count": 1, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "arbitrary_two_qubit_entanglement_audit": {"roles": ["quantum", "null"], "panel_count": 2, "legend_count": 2, "colorbar_count": 0, "min_font_pt": 12.0},
    "general_measurement_cover_polytope_audit": {"roles": ["pass", "fail"], "panel_count": 2, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "thermodynamic_channel_cost_audit": {"roles": ["quantum", "blocked"], "panel_count": 2, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "sparse_boundary_screen_scaling_audit": {"roles": ["quantum", "finite"], "panel_count": 2, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "qrf_frame_covariance_toy_audit": {"roles": ["qrf_sector", "pass", "fail"], "panel_count": 2, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "quantum_roadmap_readiness_matrix": {"roles": ["finite", "blocked"], "panel_count": 1, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "pymdp_profile_comparison": {"roles": ["finite", "qrf_sector"], "panel_count": 3, "legend_count": 3, "colorbar_count": 0, "min_font_pt": 12.0},
    "posterior_trajectory": {"roles": ["finite"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "pymdp_runtime_validation_dashboard": {"roles": ["finite", "pass", "fail", "stochastic", "null"], "panel_count": 4, "legend_count": 4, "colorbar_count": 0, "min_font_pt": 12.0},
    "criticality_proxy_panels": {"roles": ["finite"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "criticality_stochastic_ensemble": {"roles": ["stochastic", "null"], "panel_count": 2, "legend_count": 2, "colorbar_count": 0, "min_font_pt": 12.0},
    "criticality_signatures": {"roles": ["stochastic", "null", "finite"], "panel_count": 2, "legend_count": 2, "colorbar_count": 0, "min_font_pt": 12.0},
    "compassion_scope_widening": {"roles": ["finite", "null"], "panel_count": 2, "legend_count": 2, "colorbar_count": 0, "min_font_pt": 12.0},
    "separation_prior_emergence": {"roles": ["finite", "keep", "blocked"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "internal_cut_unmeasurability": {"roles": ["finite", "quantum", "boundary"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "practice_policy_scope_map": {"roles": ["finite", "blocked"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "claim_source_validation_graph": {"roles": ["source", "pass"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "scholarship_coverage_matrix": {"roles": ["source"], "panel_count": 1, "legend_count": 0, "colorbar_count": 1, "min_font_pt": 12.0},
    "claim_support_matrix": {"roles": ["source", "pass"], "panel_count": 1, "legend_count": 0, "colorbar_count": 1, "min_font_pt": 12.0},
    "manuscript_claim_audit": {"roles": ["pass", "fail"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "evidence_ceiling_stress_matrix": {"roles": ["blocked"], "panel_count": 1, "legend_count": 0, "colorbar_count": 1, "min_font_pt": 12.0},
    "claim_context_evidence_ladder": {"roles": ["source", "pass", "blocked", "finite"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "formalism_operation_map": {"roles": ["finite", "blocked"], "panel_count": 1, "legend_count": 0, "colorbar_count": 1, "min_font_pt": 12.0},
    "stochastic_effect_size_forest": {"roles": ["stochastic", "null"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "bmr_robustness_resampling": {"roles": ["keep", "prune"], "panel_count": 2, "legend_count": 1, "colorbar_count": 2, "min_font_pt": 12.0},
    "quantum_trajectory_convergence": {"roles": ["quantum", "stochastic", "blocked"], "panel_count": 2, "legend_count": 2, "colorbar_count": 0, "min_font_pt": 12.0},
    "visual_semantic_palette_ledger": {"roles": ["pass", "fail", "keep", "prune", "finite", "blocked", "stochastic", "quantum"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "method_assumption_failure_map": {"roles": ["finite", "blocked", "pass"], "panel_count": 1, "legend_count": 1, "colorbar_count": 1, "min_font_pt": 12.0},
    "qrf_sector_situation": {"roles": ["boundary", "qrf_sector", "pass"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "boundary_use_vs_ontology": {"roles": ["pass", "blocked", "boundary"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "separation_prior_net_value": {"roles": ["keep", "prune", "finite"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "multipartite_witness_negativity": {"roles": ["pass", "fail", "boundary"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "tensor_network_scaling": {"roles": ["finite", "keep", "fail", "pass"], "panel_count": 2, "legend_count": 2, "colorbar_count": 0, "min_font_pt": 12.0},
    "collision_model_relaxation": {"roles": ["keep", "prune", "boundary"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "n_cycle_contextuality_panel": {"roles": ["pass", "fail"], "panel_count": 1, "legend_count": 1, "colorbar_count": 0, "min_font_pt": 12.0},
    "data_processing_monotonicity": {"roles": ["finite", "stochastic", "null", "pass", "fail", "keep", "prune", "boundary"], "panel_count": 3, "legend_count": 3, "colorbar_count": 0, "min_font_pt": 12.0},
    "markov_blanket_discovery": {"roles": ["pass", "fail", "boundary"], "panel_count": 3, "legend_count": 1, "colorbar_count": 2, "min_font_pt": 12.0},
}


def semantic_colors() -> dict[str, str]:
    """Return shared semantic colors."""
    return dict(SEMANTIC_COLORS)


def render_contract_for(figure_id: str) -> dict[str, Any]:
    """Return render contract metadata for a figure."""
    contract = dict(FIGURE_RENDER_CONTRACTS[figure_id])
    contract["min_font_pt"] = max(float(contract.get("min_font_pt", 0.0)), MIN_READABLE_FONT_PT)
    return contract


def _hex_to_rgb(color: str) -> tuple[float, float, float]:
    color = color.lstrip("#")
    return tuple(int(color[index : index + 2], 16) / 255.0 for index in (0, 2, 4))


def _relative_luminance(color: str) -> float:
    def transform(channel: float) -> float:
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    r, g, b = (transform(channel) for channel in _hex_to_rgb(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color: str, background: str = STYLE_BACKGROUND_COLOR) -> float:
    first = _relative_luminance(color)
    second = _relative_luminance(background)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def _palette_contrast_rows() -> list[dict[str, Any]]:
    rows = []
    for role, color in SEMANTIC_COLORS.items():
        ratio = contrast_ratio(color)
        rows.append(
            {
                "role": role,
                "color": color,
                "contrast_against_white": round(ratio, 3),
                "passes_non_text_contrast": ratio >= MIN_NON_TEXT_CONTRAST_RATIO,
                "passes_text_contrast": ratio >= MIN_TEXT_CONTRAST_RATIO,
            }
        )
    return rows


def build_visual_style_audit(source_map: dict[str, Any]) -> dict[str, Any]:
    """Audit semantic roles and visual-contract metadata for figures."""
    rows = []
    palette_contrast = _palette_contrast_rows()
    low_contrast_roles = [row["role"] for row in palette_contrast if not row["passes_non_text_contrast"]]
    for figure in source_map.get("figures", []):
        contract = figure.get("render_contract", {})
        roles = contract.get("roles", [])
        missing_roles = sorted(role for role in roles if role not in SEMANTIC_COLORS)
        row = {
            "id": figure.get("id"),
            "roles": roles,
            "missing_roles": missing_roles,
            "legend_count": contract.get("legend_count", 0),
            "colorbar_count": contract.get("colorbar_count", 0),
            "has_legend_or_colorbar": contract.get("legend_count", 0) + contract.get("colorbar_count", 0) > 0,
            "ok": not missing_roles
            and bool(roles)
            and contract.get("panel_count", 0) >= 1
            and contract.get("legend_count", 0) + contract.get("colorbar_count", 0) > 0,
        }
        rows.append(row)
    return {
        "schema": "realizing_emptiness.visual_style_audit.v1",
        "semantic_role_count": len(SEMANTIC_COLORS),
        "figure_count": source_map.get("figure_count", len(rows)),
        "row_count": len(rows),
        "palette": SEMANTIC_COLORS,
        "hatches": SEMANTIC_HATCHES,
        "minimum_non_text_contrast_ratio": MIN_NON_TEXT_CONTRAST_RATIO,
        "minimum_text_contrast_ratio": MIN_TEXT_CONTRAST_RATIO,
        "palette_contrast": palette_contrast,
        "low_contrast_roles": low_contrast_roles,
        "rows": rows,
        "missing_roles": [row for row in rows if row["missing_roles"]],
        "missing_legend_or_colorbar": [row["id"] for row in rows if not row["has_legend_or_colorbar"]],
        "ok": all(row["ok"] for row in rows) and low_contrast_roles == [] and source_map.get("figure_count") == len(rows),
        "claim_boundary": "visual style audit only; not empirical evidence",
    }


def _image_metrics(project_root: Path, relative_path: str) -> dict[str, Any]:
    path = project_root / relative_path
    image = np.asarray(mpimg.imread(path), dtype=float)
    if image.ndim == 2:
        height, width = image.shape
    else:
        height, width = image.shape[:2]
    return {
        "width": int(width),
        "height": int(height),
        "pixel_variance": float(np.var(image[np.isfinite(image)])),
    }


def build_figure_legibility_audit(project_root: Path, source_map: dict[str, Any]) -> dict[str, Any]:
    """Audit image dimensions and declared render metadata for legibility."""
    rows = []
    for figure in source_map.get("figures", []):
        contract = figure.get("render_contract", {})
        metrics = _image_metrics(project_root, figure["path"])
        row = {
            "id": figure["id"],
            **metrics,
            "panel_count": contract.get("panel_count", 0),
            "min_font_pt": contract.get("min_font_pt", 0.0),
            "legend_count": contract.get("legend_count", 0),
            "colorbar_count": contract.get("colorbar_count", 0),
            "text_overlap_count": figure.get("text_overlap_count", 0),
            "title_overlap_count": figure.get("title_overlap_count", 0),
            "cropped_text_count": figure.get("cropped_text_count", 0),
            "legend_axis_overlap_count": figure.get("legend_axis_overlap_count", 0),
            "layout_ok": figure.get("layout_ok") is True,
            "source_data_alternative_count": len(figure.get("source_artifacts", [])),
        }
        row["ok"] = (
            row["width"] >= MIN_FIGURE_WIDTH_PX
            and row["height"] >= MIN_FIGURE_HEIGHT_PX
            and row["pixel_variance"] > 1e-10
            and row["panel_count"] >= 1
            and row["min_font_pt"] >= MIN_READABLE_FONT_PT
            and row["source_data_alternative_count"] >= 1
            and row["legend_count"] + row["colorbar_count"] >= 1
            and row["layout_ok"]
        )
        rows.append(row)
    return {
        "schema": "realizing_emptiness.figure_legibility_audit.v1",
        "minimum_width_px": MIN_FIGURE_WIDTH_PX,
        "minimum_height_px": MIN_FIGURE_HEIGHT_PX,
        "minimum_readable_font_pt": MIN_READABLE_FONT_PT,
        "figure_count": source_map.get("figure_count", len(rows)),
        "row_count": len(rows),
        "rows": rows,
        "undersized": [row["id"] for row in rows if row["width"] < MIN_FIGURE_WIDTH_PX or row["height"] < MIN_FIGURE_HEIGHT_PX],
        "undersized_text": [row["id"] for row in rows if row["min_font_pt"] < MIN_READABLE_FONT_PT],
        "missing_render_contract": [row["id"] for row in rows if row["panel_count"] < 1],
        "missing_legend_or_colorbar": [row["id"] for row in rows if row["legend_count"] + row["colorbar_count"] < 1],
        "missing_source_data_alternative": [row["id"] for row in rows if row["source_data_alternative_count"] < 1],
        "overlapping_text": [row["id"] for row in rows if row["text_overlap_count"] > 0],
        "overlapping_titles": [row["id"] for row in rows if row["title_overlap_count"] > 0],
        "cropped_text": [row["id"] for row in rows if row["cropped_text_count"] > 0],
        "legend_axis_overlaps": [row["id"] for row in rows if row["legend_axis_overlap_count"] > 0],
        "layout_failures": [row["id"] for row in rows if row["layout_ok"] is not True],
        "ok": all(row["ok"] for row in rows) and source_map.get("figure_count") == len(rows),
        "claim_boundary": "figure legibility audit only; not empirical evidence",
    }


def write_visual_style_audits(project_root: Path, source_map: dict[str, Any]) -> tuple[Path, Path]:
    """Write visual style and legibility audits."""
    data_dir = project_root / "output" / "data"
    style_path = data_dir / "visual_style_audit.json"
    legibility_path = data_dir / "figure_legibility_audit.json"
    style_path.write_text(json.dumps(build_visual_style_audit(source_map), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    legibility_path.write_text(
        json.dumps(build_figure_legibility_audit(project_root, source_map), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return style_path, legibility_path
