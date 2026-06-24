"""Static artifact dashboard for roadmap and claim-governance outputs."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import yaml


CLAIM_BOUNDARY = (
    "static artifact dashboard; not empirical evidence, not a physical qFEP realization, "
    "and not a clinical, neural, awakening, or practice-efficacy claim"
)


def _load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _escape(value: object) -> str:
    return html.escape(str(value))


def build_artifact_dashboard_payload(project_root: Path, source_map: dict[str, Any]) -> dict[str, Any]:
    data_dir = project_root / "output" / "data"
    reports_dir = project_root / "output" / "reports"
    roadmap = _load_json(data_dir / "quantum_extension_roadmap.json")
    readiness = _load_json(data_dir / "quantum_roadmap_readiness_matrix.json")
    todo_audit = _load_json(data_dir / "roadmap_todo_audit.json")
    dependency = _load_json(data_dir / "validation_dependency_graph.json")
    ceiling = _load_json(data_dir / "evidence_ceiling_audit.json")
    stochastic_policy = _load_json(data_dir / "stochastic_policy_ensemble.json")
    pymdp_runtime = _load_json(data_dir / "pymdp_runtime_diagnostics_log.json")
    criticality_stochastic = _load_json(data_dir / "criticality_stochastic_ensemble.json")
    quantum_trajectory = _load_json(data_dir / "quantum_trajectory_unraveling.json")
    stochastic_effects = _load_json(data_dir / "stochastic_effect_size_audit.json")
    bmr_resampling = _load_json(data_dir / "bmr_robustness_resampling_audit.json")
    trajectory_convergence = _load_json(data_dir / "quantum_trajectory_convergence_audit.json")
    statistical_robustness = _load_json(data_dir / "statistical_robustness_audit.json")
    visual_style = _load_json(data_dir / "visual_style_audit.json")
    legibility = _load_json(data_dir / "figure_legibility_audit.json")
    method_ledger = _load_json(data_dir / "method_assumption_ledger.json")
    method_controls = _load_json(data_dir / "method_negative_control_inventory.json")
    contract_registry = _load_json(data_dir / "artifact_contract_registry.json")
    artifact_release = _load_json(data_dir / "artifact_release_manifest.json")
    review_response = _load_json(data_dir / "external_review_response_audit.json")
    figure_parameter_ledger = _load_json(data_dir / "figure_parameter_ledger.json")
    qrf_label_ablation = _load_json(data_dir / "qrf_label_ablation_audit.json")
    quantum_crosscheck = _load_json(data_dir / "quantum_independent_crosscheck_audit.json")
    bmr_alternative = _load_json(data_dir / "bmr_alternative_prior_audit.json")
    source_coverage = _load_json(data_dir / "source_argument_coverage_audit.json")
    claim_context = _load_json(data_dir / "claim_context_ledger.json")
    claim_redteam = _load_json(data_dir / "claim_redteam_audit.json")
    reference_audit = _load_json(data_dir / "manuscript_reference_audit.json")
    figure_reuse_audit = _load_json(data_dir / "figure_reuse_audit.json")
    figure_placement_audit = _load_json(data_dir / "manuscript_figure_placement_audit.json")
    cover_audit = _load_json(data_dir / "cover_graphical_abstract_audit.json")
    claim_intensity = _load_json(data_dir / "manuscript_claim_intensity_audit.json")
    validation = _load_json(reports_dir / "validation_report.json", default={"all_passed": None, "passed": 0, "total": 0})
    artifact_manifest = _load_yaml(project_root / "artifact_manifest.yaml")
    manifest_paths = {artifact["path"] for artifact in artifact_manifest.get("artifacts", [])}
    generated_paths = {
        str(path.relative_to(project_root))
        for folder in (project_root / "output" / "data", project_root / "output" / "reports", project_root / "output" / "figures")
        if folder.exists()
        for path in folder.iterdir()
        if path.is_file()
    }
    for ignored in (
        "output/reports/validation_report.json",
        "output/reports/output_statistics.json",
        "output/reports/output_statistics.txt",
    ):
        generated_paths.discard(ignored)
    manifest_coverage = {
        "generated_count": len(generated_paths),
        "manifest_count": len(manifest_paths),
        "unmanifested_generated_paths": sorted(generated_paths - manifest_paths),
        "missing_manifest_paths": sorted(path for path in manifest_paths if not (project_root / path).exists()),
    }
    claim_ceiling_rows = [
        {
            "claim_id": row.get("claim_id", ""),
            "support_count": row.get("support_count", 0),
            "status": row.get("status", ""),
            "stressors": row.get("stressors", []),
        }
        for row in ceiling.get("rows", [])
    ]
    arc_figure_ids = {row["id"] for row in source_map.get("figures", [])}
    argument_arc = [
        {"stage": stage, "description": description, "figure_id": figure_id, "figure_present": figure_id in arc_figure_ids}
        for stage, description, figure_id in (
            ("Boundary screen", "Six software channels b0-b5 carry the evidenced bitstream.", "qrf_sector_situation"),
            ("Three sector frames", "The same bits read under separation-constrained, opacified, and post-dual QRF lenses.", "qrf_channel_relabeling_ledger"),
            ("Indistinguishability / permission", "Boundary use is licensed; boundary ontology is not, with a failing perturbation control.", "boundary_use_vs_ontology"),
            ("Separation-prior emergence", "The prior earns accuracy only when boundary channels are action-contingent.", "separation_prior_emergence"),
            ("BMR lifecycle", "Useful then dispensable: pruned at high metacognitive access at the weakest precision.", "separation_prior_net_value"),
            ("Active-inference profile execution", "Each frame is run as an explicit profile-specific pymdp generative model.", "pymdp_profile_comparison"),
            ("Finite quantum scope", "Implemented extension engines stay finite-software, with blocked external classes.", "finite_quantum_scope_summary"),
        )
    ]
    return {
        "schema": "realizing_emptiness.artifact_dashboard_payload.v1",
        "roadmap": {
            "implemented_count": roadmap.get("implemented_count", 0),
            "future_count": roadmap.get("future_count", 0),
            "implemented_ids": [row["id"] for row in roadmap.get("implemented", [])],
            "future_ids": [row["id"] for row in roadmap.get("future", [])],
            "blocked_task_ids": [row.get("blocked_task_id", row.get("id", "")) for row in roadmap.get("future", [])],
        },
        "readiness": {
            "row_count": readiness.get("row_count", 0),
            "all_controls_pass": readiness.get("all_controls_pass") is True,
            "future_blocked": readiness.get("controls", {}).get("all_future_blocked") is True,
            "future_ids": [row.get("id", "") for row in readiness.get("rows", []) if row.get("roadmap_class") == "future"],
            "forged_completed_future_row_rejected": readiness.get("controls", {}).get("forged_completed_future_row_rejected") is True,
        },
        "todo_audit": {
            "all_controls_pass": todo_audit.get("all_controls_pass") is True,
            "stale_future_rows": todo_audit.get("stale_future_rows", []),
            "historical_backlog_rows": todo_audit.get("historical_backlog_rows", []),
            "blocked_external_class_violations": todo_audit.get("blocked_external_class_violations", []),
        },
        "figures": {
            "figure_count": source_map.get("figure_count", 0),
            "figure_ids": [row["id"] for row in source_map.get("figures", [])],
        },
        "argument_arc": argument_arc,
        "dependency_graph": {
            "node_count": dependency.get("node_count", 0),
            "edge_count": dependency.get("edge_count", 0),
            "all_controls_pass": dependency.get("all_controls_pass") is True,
            "required_quantum_nodes": dependency.get("required_quantum_nodes", []),
        },
        "pymdp_runtime": {
            "all_controls_pass": pymdp_runtime.get("all_controls_pass") is True,
            "trace_row_count": pymdp_runtime.get("trace_row_count", 0),
            "model_profile_count": pymdp_runtime.get("model_profile_count", 0),
            "replay_equal": pymdp_runtime.get("replay", {}).get("trace_rows_equal") is True
            and pymdp_runtime.get("replay", {}).get("profile_summaries_equal") is True,
            "canary_warning_count": len(pymdp_runtime.get("canary", {}).get("warnings", [])),
            "max_policy_posterior_norm_residual": pymdp_runtime.get("summary", {}).get(
                "max_policy_posterior_norm_residual", 1.0
            ),
            "max_weighted_expected_free_energy_residual": pymdp_runtime.get("summary", {}).get(
                "max_weighted_expected_free_energy_residual", 1.0
            ),
            "claim_boundary": pymdp_runtime.get("claim_boundary", ""),
        },
        "stochastic_engines": {
            "active_inference_ensemble_ok": stochastic_policy.get("all_controls_pass") is True,
            "criticality_ensemble_ok": criticality_stochastic.get("all_controls_pass") is True,
            "quantum_trajectory_ok": quantum_trajectory.get("all_controls_pass") is True,
            "runs_per_profile": stochastic_policy.get("runs_per_profile", 0),
            "trajectory_count": quantum_trajectory.get("trajectory_count", 0),
            "claim_boundary": "seeded stochastic simulations only; not empirical, neural, clinical, practice-efficacy, or physical qFEP evidence",
        },
        "statistical_robustness": {
            "all_controls_pass": statistical_robustness.get("all_controls_pass") is True,
            "stochastic_effects_pass": stochastic_effects.get("all_controls_pass") is True,
            "bmr_resampling_pass": bmr_resampling.get("all_controls_pass") is True,
            "trajectory_convergence_pass": trajectory_convergence.get("all_controls_pass") is True,
            "effect_size_rows": stochastic_effects.get("row_count", 0),
            "bmr_resampling_rows": bmr_resampling.get("row_count", 0),
            "trajectory_counts": trajectory_convergence.get("trajectory_counts", []),
            "claim_boundary": "finite seeded simulation robustness only; not empirical inference",
        },
        "visual_quality": {
            "style_ok": visual_style.get("ok") is True,
            "legibility_ok": legibility.get("ok") is True,
            "style_row_count": visual_style.get("row_count", 0),
            "legibility_row_count": legibility.get("row_count", 0),
            "missing_roles": visual_style.get("missing_roles", []),
            "low_contrast_roles": visual_style.get("low_contrast_roles", []),
            "undersized": legibility.get("undersized", []),
            "undersized_text": legibility.get("undersized_text", []),
            "missing_legend_or_colorbar": legibility.get("missing_legend_or_colorbar", []),
            "overlapping_text": legibility.get("overlapping_text", []),
            "overlapping_titles": legibility.get("overlapping_titles", []),
            "cropped_text": legibility.get("cropped_text", []),
            "legend_axis_overlaps": legibility.get("legend_axis_overlaps", []),
            "layout_failures": legibility.get("layout_failures", []),
        },
        "method_governance": {
            "method_count": method_ledger.get("method_count", 0),
            "control_count": method_controls.get("control_count", 0),
            "all_methods_have_controls": method_controls.get("all_methods_have_controls") is True,
            "all_methods_have_hard_constraints": method_ledger.get("all_methods_have_hard_constraints") is True,
            "claim_boundary": method_ledger.get("claim_boundary", ""),
        },
        "source_fit": {
            "all_controls_pass": source_coverage.get("all_controls_pass") is True,
            "theme_count": source_coverage.get("theme_count", 0),
            "qrf_bmr_opacification_not_quantum_only": source_coverage.get("controls", {}).get("qrf_bmr_opacification_not_quantum_only") is True,
            "claim_boundary": source_coverage.get("claim_boundary", ""),
        },
        "claim_context": {
            "all_controls_pass": claim_context.get("all_controls_pass") is True,
            "claim_count": claim_context.get("claim_count", 0),
            "role_compatibility_failures": claim_context.get("role_compatibility_failures", []),
            "proxy_overclaiming_reader_claims": claim_context.get("proxy_overclaiming_reader_claims", []),
            "missing_future_evidence": claim_context.get("missing_future_evidence", []),
            "missing_manuscript_sections": claim_context.get("missing_manuscript_sections", []),
            "missing_figure_bindings": claim_context.get("missing_figure_bindings", []),
            "claim_boundary": claim_context.get("claim_boundary", ""),
        },
        "claim_redteam": {
            "all_controls_pass": claim_redteam.get("all_controls_pass") is True,
            "claim_count": claim_redteam.get("claim_count", 0),
            "unresolved_sections": claim_redteam.get("unresolved_sections", []),
            "unresolved_figure_bindings": claim_redteam.get("unresolved_figure_bindings", []),
            "missing_boundaries": claim_redteam.get("missing_boundaries", []),
            "reader_overclaims": claim_redteam.get("reader_overclaims", []),
            "risky_claim_sentences": claim_redteam.get("risky_claim_sentences", []),
            "claim_boundary": claim_redteam.get("claim_boundary", ""),
        },
        "contract_registry": {
            "contract_count": contract_registry.get("contract_count", 0),
            "all_controls_pass": contract_registry.get("all_controls_pass") is True,
            "missing_schema_paths": contract_registry.get("missing_schema_paths", []),
            "duplicate_ids": contract_registry.get("duplicate_ids", []),
        },
        "review_hardening": {
            "artifact_release_ok": artifact_release.get("all_controls_pass") is True,
            "release_scope": artifact_release.get("release_scope", ""),
            "public_publication_performed": artifact_release.get("public_publication_performed"),
            "release_file_count": artifact_release.get("file_count", 0),
            "review_response_ok": review_response.get("all_controls_pass") is True,
            "review_response_rows": review_response.get("row_count", 0),
            "public_reproduction_status": next(
                (
                    row.get("response_status", "")
                    for row in review_response.get("rows", [])
                    if row.get("recommendation_id") == "public_independent_reproduction"
                ),
                "",
            ),
            "figure_parameter_ledger_ok": figure_parameter_ledger.get("all_controls_pass") is True,
            "figure_parameter_rows": figure_parameter_ledger.get("row_count", 0),
            "qrf_label_ablation_ok": qrf_label_ablation.get("all_controls_pass") is True,
            "quantum_crosscheck_ok": quantum_crosscheck.get("all_controls_pass") is True,
            "bmr_alternative_ok": bmr_alternative.get("all_controls_pass") is True,
            "claim_boundary": artifact_release.get("claim_boundary", CLAIM_BOUNDARY),
        },
        "manuscript_audits": {
            "references_ok": reference_audit.get("ok") is True,
            "figure_reuse_ok": figure_reuse_audit.get("ok") is True,
            "figure_placement_ok": figure_placement_audit.get("ok") is True,
            "cover_graphic_ok": cover_audit.get("ok") is True,
            "claim_intensity_ok": claim_intensity.get("ok") is True,
            "unresolved_references": reference_audit.get("unresolved_references", []),
            "duplicate_supplement_paths": figure_reuse_audit.get("duplicate_supplement_paths", []),
            "technical_quantum_figures_in_main": figure_placement_audit.get("technical_quantum_figures_in_main", []),
            "governance_figures_in_main": figure_placement_audit.get("governance_figures_in_main", []),
            "governance_figures_missing_from_supplement": figure_placement_audit.get(
                "governance_figures_missing_from_supplement", []
            ),
            "governance_figures_repeated_in_supplement": figure_placement_audit.get(
                "governance_figures_repeated_in_supplement", []
            ),
            "risky_claim_sentences": claim_intensity.get("risky_rows", []),
        },
        "claim_ceiling_rows": claim_ceiling_rows,
        "manifest_coverage": manifest_coverage,
        "validation_report": {
            "all_passed": validation.get("all_passed"),
            "passed": validation.get("passed", 0),
            "total": validation.get("total", 0),
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _table(headers: list[str], rows: list[list[object]]) -> str:
    header_html = "".join(f"<th>{_escape(header)}</th>" for header in headers)
    body_html = "\n".join(
        "<tr>" + "".join(f"<td>{_escape(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"<table><thead><tr>{header_html}</tr></thead><tbody>{body_html}</tbody></table>"


def _figure_link(figure_id: str, present: bool) -> str:
    safe = _escape(figure_id)
    if not present:
        return f"{safe} (missing)"
    return f'<a href="../figures/{safe}.png">{safe}</a>'


def _argument_arc_table(arc: list[dict[str, Any]]) -> str:
    rows_html = "\n".join(
        "<tr>"
        f"<td>{index + 1}</td>"
        f"<td>{_escape(item['stage'])}</td>"
        f"<td>{_escape(item['description'])}</td>"
        f"<td>{_figure_link(item['figure_id'], item.get('figure_present', False))}</td>"
        "</tr>"
        for index, item in enumerate(arc)
    )
    return (
        "<table><thead><tr><th>#</th><th>stage</th><th>what it shows</th><th>lead figure</th></tr></thead>"
        f"<tbody>{rows_html}</tbody></table>"
    )


def render_artifact_dashboard_html(payload: dict[str, Any]) -> str:
    roadmap_rows = [
        ["implemented finite engines", payload["roadmap"]["implemented_count"], ", ".join(payload["roadmap"]["implemented_ids"])],
        ["blocked future classes", payload["roadmap"]["future_count"], ", ".join(payload["roadmap"]["future_ids"])],
    ]
    figure_gallery = " &middot; ".join(_figure_link(figure_id, True) for figure_id in payload["figures"]["figure_ids"])
    claim_rows = [
        [row["claim_id"], row["support_count"], row["status"], ", ".join(row["stressors"])]
        for row in payload["claim_ceiling_rows"]
    ]
    coverage = payload["manifest_coverage"]
    manifest_rows = [
        ["generated artifacts", coverage["generated_count"]],
        ["manifest entries", coverage["manifest_count"]],
        ["unmanifested generated paths", len(coverage["unmanifested_generated_paths"])],
        ["missing manifest paths", len(coverage["missing_manifest_paths"])],
    ]
    stochastic = payload["stochastic_engines"]
    pymdp_runtime = payload["pymdp_runtime"]
    robustness = payload["statistical_robustness"]
    visual_quality = payload["visual_quality"]
    method_governance = payload["method_governance"]
    source_fit = payload["source_fit"]
    claim_context = payload["claim_context"]
    claim_redteam = payload["claim_redteam"]
    contracts = payload["contract_registry"]
    review_hardening = payload["review_hardening"]
    manuscript_audits = payload["manuscript_audits"]
    validation = payload["validation_report"]
    validation_status = (
        "pending first validation run after dashboard generation"
        if validation["all_passed"] is None
        else "all passed" if validation["all_passed"] else "has failing checks"
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Realizing Emptiness Artifact Dashboard</title>
  <style>
    :root {{ color-scheme: light; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: #f8fafc; color: #111827; font-size: 16px; }}
    main {{ max-width: 1240px; margin: 0 auto; padding: 32px 24px 52px; }}
    h1 {{ font-size: 34px; margin: 0 0 10px; line-height: 1.12; }}
    h2 {{ font-size: 22px; margin: 34px 0 12px; line-height: 1.2; }}
    p {{ max-width: 1040px; line-height: 1.58; }}
    a {{ color: #1d4ed8; text-underline-offset: 3px; }}
    a:focus-visible {{ outline: 3px solid #92400e; outline-offset: 3px; border-radius: 3px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 14px; margin: 20px 0; }}
    .metric {{ background: white; border: 1px solid #d4d4d8; border-radius: 8px; padding: 16px; }}
    .metric strong {{ display: block; font-size: 30px; color: #0f766e; line-height: 1.2; }}
    .cover-preview {{ margin: 26px 0 32px; }}
    .cover-preview a {{ display: block; }}
    .cover-preview img {{ display: block; width: min(100%, 1160px); margin: 0 auto; background: white; border: 1px solid #d4d4d8; border-radius: 8px; box-shadow: 0 12px 34px rgb(15 23 42 / 0.12); }}
    .cover-preview figcaption {{ margin-top: 9px; color: #475569; font-size: 14px; line-height: 1.45; text-align: center; }}
    table {{ width: 100%; table-layout: fixed; border-collapse: collapse; background: white; border: 1px solid rgb(212 212 216); margin: 8px 0 16px; }}
    th, td {{ text-align: left; vertical-align: top; border-bottom: 1px solid rgb(229 231 235); padding: 10px 12px; font-size: 15px; line-height: 1.45; overflow-wrap: anywhere; word-break: break-word; }}
    th {{ background: #eef2ff; font-weight: 700; }}
    code {{ background: #e5e7eb; padding: 1px 4px; border-radius: 4px; }}
    .boundary {{ border-left: 4px solid #92400e; padding-left: 12px; }}
    .figure-gallery {{ line-height: 1.75; overflow-wrap: anywhere; }}
    @media (max-width: 640px) {{
      main {{ padding: 28px 16px 44px; }}
      h1 {{ font-size: 31px; }}
      th, td {{ padding: 8px 8px; font-size: 14px; }}
    }}
  </style>
</head>
<body>
<main>
  <h1>Realizing Emptiness Artifact Dashboard</h1>
  <p class="boundary">{_escape(payload["claim_boundary"])}</p>
  <div class="grid">
    <div class="metric"><span>Governance rows</span><strong>{payload["roadmap"]["implemented_count"] + payload["roadmap"]["future_count"]}</strong></div>
    <div class="metric"><span>Figures</span><strong>{payload["figures"]["figure_count"]}</strong></div>
    <div class="metric"><span>Dependency nodes</span><strong>{payload["dependency_graph"]["node_count"]}</strong></div>
    <div class="metric"><span>Validation</span><strong>{_escape(validation_status)}</strong><span>{validation["passed"]}/{validation["total"]} checks recorded</span></div>
  </div>
  <figure class="cover-preview">
    <a href="../figures/graphical_abstract_cover.png"><img src="../figures/graphical_abstract_cover.png" alt="Graphical abstract cover for the static Realizing Emptiness software artifact package."></a>
    <figcaption>Cover graphical abstract for the local finite-software evidence package; not empirical, clinical, neural, awakening, practice-efficacy, or physical qFEP evidence.</figcaption>
  </figure>
  <h2>Argument Arc</h2>
  <p>The no-self-evidence argument as a navigable sequence from boundary screen to active-inference profile execution; each stage links to its lead figure. This is a reading aid over finite-software artifacts, not an empirical or ontological claim.</p>
  {_argument_arc_table(payload["argument_arc"])}
  <h2>Roadmap/TODO Governance</h2>
  {_table(["class", "count", "ids"], roadmap_rows)}
  <h2>TODO And Claim Governance</h2>
  {_table(["check", "value"], [
      ["readiness controls pass", payload["readiness"]["all_controls_pass"]],
      ["future rows blocked", payload["readiness"]["future_blocked"]],
      ["TODO audit controls pass", payload["todo_audit"]["all_controls_pass"]],
      ["stale TODO rows", len(payload["todo_audit"]["stale_future_rows"])],
      ["historical backlog rows", len(payload["todo_audit"]["historical_backlog_rows"])],
      ["blocked-class violations", len(payload["todo_audit"]["blocked_external_class_violations"])],
  ])}
  <h2>Manifest Coverage</h2>
  {_table(["metric", "value"], manifest_rows)}
	  <h2>Dependency Graph</h2>
	  {_table(["metric", "value"], [
	      ["node count", payload["dependency_graph"]["node_count"]],
	      ["edge count", payload["dependency_graph"]["edge_count"]],
	      ["quantum nodes present", payload["dependency_graph"]["all_controls_pass"]],
	      ["required quantum nodes", ", ".join(payload["dependency_graph"]["required_quantum_nodes"])],
	  ])}
	  <h2>pymdp Runtime Diagnostics</h2>
	  {_table(["metric", "value"], [
	      ["runtime controls pass", pymdp_runtime["all_controls_pass"]],
	      ["trace rows", pymdp_runtime["trace_row_count"]],
	      ["profile models hashed", pymdp_runtime["model_profile_count"]],
	      ["deterministic replay equal", pymdp_runtime["replay_equal"]],
	      ["captured runtime dependency warnings", pymdp_runtime["canary_warning_count"]],
	      ["max policy posterior residual", f"{pymdp_runtime['max_policy_posterior_norm_residual']:.2e}"],
	      ["max weighted EFE residual", f"{pymdp_runtime['max_weighted_expected_free_energy_residual']:.2e}"],
	      ["claim boundary", pymdp_runtime["claim_boundary"]],
	  ])}
	  <h2>Stochastic Simulation Engines</h2>
	  {_table(["engine", "status"], [
	      ["active-inference ensemble", stochastic["active_inference_ensemble_ok"]],
	      ["criticality ensemble", stochastic["criticality_ensemble_ok"]],
	      ["quantum trajectory unraveling", stochastic["quantum_trajectory_ok"]],
	      ["runs per profile", stochastic["runs_per_profile"]],
	      ["quantum trajectories per rate", stochastic["trajectory_count"]],
	      ["claim boundary", stochastic["claim_boundary"]],
	  ])}
	  <h2>Statistical Robustness</h2>
	  {_table(["audit", "status"], [
	      ["aggregate controls", robustness["all_controls_pass"]],
	      ["stochastic effect sizes", robustness["stochastic_effects_pass"]],
	      ["BMR resampling", robustness["bmr_resampling_pass"]],
	      ["quantum trajectory convergence", robustness["trajectory_convergence_pass"]],
	      ["effect-size rows", robustness["effect_size_rows"]],
	      ["BMR resampling rows", robustness["bmr_resampling_rows"]],
	      ["trajectory counts", ", ".join(str(item) for item in robustness["trajectory_counts"])],
	      ["claim boundary", robustness["claim_boundary"]],
	  ])}
	  <h2>Method And Contract Governance</h2>
	  {_table(["gate", "value"], [
	      ["source-fit controls", source_fit["all_controls_pass"]],
	      ["source themes covered", source_fit["theme_count"]],
	      ["QRF/BMR not quantum-only", source_fit["qrf_bmr_opacification_not_quantum_only"]],
	      ["claim-context controls", claim_context["all_controls_pass"]],
	      ["claim-context rows", claim_context["claim_count"]],
	      ["role compatibility failures", len(claim_context["role_compatibility_failures"])],
	      ["proxy reader overclaims", len(claim_context["proxy_overclaiming_reader_claims"])],
	      ["missing future-evidence boundaries", len(claim_context["missing_future_evidence"])],
	      ["missing manuscript section bindings", len(claim_context["missing_manuscript_sections"])],
	      ["missing figure bindings", len(claim_context["missing_figure_bindings"])],
	      ["claim RedTeam controls", claim_redteam["all_controls_pass"]],
	      ["claim RedTeam rows", claim_redteam["claim_count"]],
	      ["unresolved claim sections", len(claim_redteam["unresolved_sections"])],
	      ["unresolved claim figures", len(claim_redteam["unresolved_figure_bindings"])],
	      ["missing claim RedTeam boundaries", len(claim_redteam["missing_boundaries"])],
	      ["claim RedTeam reader overclaims", len(claim_redteam["reader_overclaims"])],
	      ["claim RedTeam risky sentences", len(claim_redteam["risky_claim_sentences"])],
	      ["method count", method_governance["method_count"]],
	      ["negative-control count", method_governance["control_count"]],
	      ["all methods have controls", method_governance["all_methods_have_controls"]],
	      ["all methods have hard constraints", method_governance["all_methods_have_hard_constraints"]],
	      ["artifact contracts", contracts["contract_count"]],
	      ["contract controls pass", contracts["all_controls_pass"]],
	      ["missing schema paths", len(contracts["missing_schema_paths"])],
	      ["duplicate contract ids", len(contracts["duplicate_ids"])],
	  ])}
	  <h2>Review Hardening</h2>
	  {_table(["artifact", "value"], [
	      ["local release manifest", review_hardening["artifact_release_ok"]],
	      ["release scope", review_hardening["release_scope"]],
	      ["public publication performed", review_hardening["public_publication_performed"]],
	      ["hashed release files", review_hardening["release_file_count"]],
	      ["external review response audit", review_hardening["review_response_ok"]],
	      ["review response rows", review_hardening["review_response_rows"]],
	      ["public independent reproduction", review_hardening["public_reproduction_status"]],
	      ["figure parameter ledger", review_hardening["figure_parameter_ledger_ok"]],
	      ["figure parameter rows", review_hardening["figure_parameter_rows"]],
	      ["neutral QRF label ablation", review_hardening["qrf_label_ablation_ok"]],
	      ["independent quantum cross-check", review_hardening["quantum_crosscheck_ok"]],
	      ["BMR alternative priors", review_hardening["bmr_alternative_ok"]],
	      ["claim boundary", review_hardening["claim_boundary"]],
	  ])}
	  <h2>Visual QA</h2>
	  {_table(["check", "value"], [
	      ["semantic style audit", visual_quality["style_ok"]],
	      ["legibility audit", visual_quality["legibility_ok"]],
	      ["style rows", visual_quality["style_row_count"]],
	      ["legibility rows", visual_quality["legibility_row_count"]],
	      ["missing roles", len(visual_quality["missing_roles"])],
	      ["low-contrast semantic roles", len(visual_quality["low_contrast_roles"])],
	      ["undersized figures", len(visual_quality["undersized"])],
	      ["below-floor text contracts", len(visual_quality["undersized_text"])],
	      ["missing legends or colorbars", len(visual_quality["missing_legend_or_colorbar"])],
	      ["overlapping text layouts", len(visual_quality["overlapping_text"])],
	      ["overlapping panel titles", len(visual_quality["overlapping_titles"])],
	      ["cropped text labels", len(visual_quality["cropped_text"])],
	      ["legend/axis collisions", len(visual_quality["legend_axis_overlaps"])],
	      ["layout failures", len(visual_quality["layout_failures"])],
	  ])}
	  <h2>Manuscript And Figure Audits</h2>
	  {_table(["check", "value"], [
	      ["references resolve", manuscript_audits["references_ok"]],
	      ["no supplement figure duplication", manuscript_audits["figure_reuse_ok"]],
	      ["balanced quantum figure placement", manuscript_audits["figure_placement_ok"]],
	      ["cover graphic unnumbered/source-mapped", manuscript_audits["cover_graphic_ok"]],
	      ["claim intensity scoped", manuscript_audits["claim_intensity_ok"]],
	      ["unresolved references", len(manuscript_audits["unresolved_references"])],
	      ["duplicate supplement images", len(manuscript_audits["duplicate_supplement_paths"])],
	      ["technical quantum figures in main", len(manuscript_audits["technical_quantum_figures_in_main"])],
	      ["governance figures in main", len(manuscript_audits["governance_figures_in_main"])],
	      ["governance figures missing from supplement", len(manuscript_audits["governance_figures_missing_from_supplement"])],
	      ["governance figures repeated in supplement", len(manuscript_audits["governance_figures_repeated_in_supplement"])],
	      ["risky claim sentences", len(manuscript_audits["risky_claim_sentences"])],
	  ])}
	  <h2>Figures</h2>
  <p class="figure-gallery">{figure_gallery}</p>
  <h2>Claim Ceilings</h2>
  {_table(["claim", "support count", "status", "stressors"], claim_rows)}
</main>
</body>
</html>
"""


def write_artifact_dashboard(project_root: Path, source_map: dict[str, Any]) -> tuple[Path, Path]:
    payload = build_artifact_dashboard_payload(project_root, source_map)
    data_path = project_root / "output" / "data" / "artifact_dashboard_payload.json"
    html_path = project_root / "output" / "dashboard" / "index.html"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    html_path.write_text(render_artifact_dashboard_html(payload), encoding="utf-8")
    return data_path, html_path
