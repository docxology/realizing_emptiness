"""Tests for practice maps, script chain, and validators."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import yaml

from gates.roadmap import build_roadmap_todo_audit, build_validation_dependency_graph
from gates.contracts import build_artifact_contract_registry
from gates.manuscript import build_cover_graphical_abstract_audit, build_figure_placement_audit, build_figure_reuse_audit, build_manuscript_reference_audit
from gates.validation import check_documentation_contract, validate_outputs
from practice.protocols import practice_protocol_map
from visualizations.dashboard import build_artifact_dashboard_payload, write_artifact_dashboard
from visualizations.figures import _measure_layout, boundary_use_ontology_verdicts, generate_all_figures, separation_prior_lifecycle
from visualizations.integrity import build_figure_integrity_audit, compare_figure_integrity
from visualizations.rendered_captions import (
    build_rendered_figure_caption_audit,
    build_rendered_figure_caption_audit_from_texts,
    expand_markdown_figure_captions,
    write_rendered_figure_caption_audit,
)
from visualizations.style import MIN_READABLE_FONT_PT, SEMANTIC_COLORS, semantic_colors


def _manifest_section_table(root: Path) -> dict[str, dict[str, object]]:
    manifest = yaml.safe_load((root / "docs" / "manuscript" / "sheaf" / "manifest.yaml").read_text(encoding="utf-8"))
    return {
        row["output"]: {"section": row["title"], "tracks": row["tracks"]}
        for row in manifest["sections"]
    }


def _readme_section_table(root: Path) -> dict[str, dict[str, object]]:
    readme = (root / "docs" / "manuscript" / "README.md").read_text(encoding="utf-8")
    rows: dict[str, dict[str, object]] = {}
    in_table = False
    for line in readme.splitlines():
        if line.startswith("| Output file | Section | Tracks"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells[0] == "---":
            continue
        output = cells[0].strip("`")
        rows[output] = {
            "section": cells[1],
            "tracks": [track.strip() for track in cells[2].split(",") if track.strip()],
        }
    return rows


def test_practice_protocols_are_bounded() -> None:
    payload = practice_protocol_map()
    assert payload["allow_user_facing_claims"] is False
    assert payload["all_have_safety_boundaries"] is True
    assert payload["protocol_count"] == 3


def test_full_chain_and_output_validation(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    result = subprocess.run([sys.executable, "scripts/run_full_chain.py"], cwd=root, check=False, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    checks = validate_outputs(root)
    assert checks
    assert all(checks.values())
    bmr = json.loads((root / "output" / "data" / "bmr_sweep.json").read_text(encoding="utf-8"))
    sensitivity = json.loads((root / "output" / "data" / "simulation_sensitivity_grid.json").read_text(encoding="utf-8"))
    stochastic = json.loads((root / "output" / "data" / "stochastic_policy_ensemble.json").read_text(encoding="utf-8"))
    trajectory = json.loads((root / "output" / "data" / "quantum_trajectory_convergence_audit.json").read_text(encoding="utf-8"))
    variables = json.loads((root / "output" / "data" / "manuscript_variables.json").read_text(encoding="utf-8"))
    manuscript_tokens = [
        f"{path.name}:{match.group(0)}"
        for path in sorted((root / "output" / "manuscript").glob("*.md"))
        for match in re.finditer(r"\{\{[A-Z0-9_]+\}\}", path.read_text(encoding="utf-8"))
    ]
    assert bmr["row_count"] >= 45
    assert sensitivity["row_count"] >= 315
    assert stochastic["runs_per_profile"] >= 128
    assert stochastic["steps"] >= 48
    assert stochastic["row_count"] == stochastic["runs_per_profile"] * stochastic["steps"] * stochastic["profile_count"] * 2
    assert max(trajectory["trajectory_counts"]) >= 2048
    assert variables["VALIDATION_PASS_COUNT"] == variables["VALIDATION_TOTAL_COUNT"] == len(checks)
    assert manuscript_tokens == []
    assert (root / "output" / "reports" / "validation_report.json").exists()


def test_figures_deterministic_under_rcparam_pollution(pytestconfig) -> None:
    """``generate_all_figures`` must reset matplotlib rcParams so in-process
    regeneration is byte-identical to a clean subprocess run.

    Regression: without ``plt.rcdefaults()`` at the start of generation, rcParams
    leaked by other code/tests in the same interpreter changed the rendered PNG
    bytes, invalidating the figure hashes pinned in the release manifest and
    intermittently failing the manifest/figure-integrity gates.
    """
    root: Path = pytestconfig.realizing_emptiness_root
    sample = root / "output" / "figures" / "criticality_signatures.png"
    plt.rcdefaults()
    generate_all_figures(root)
    reference = sample.read_bytes()
    plt.rcParams.update(
        {
            "font.size": 99.0,
            "axes.titlesize": 3.0,
            "lines.linewidth": 8.0,
            "axes.grid": True,
            "figure.dpi": 200.0,
        }
    )
    generate_all_figures(root)
    assert sample.read_bytes() == reference, (
        "figure bytes drift under rcParam pollution; generate_all_figures must "
        "reset rcParams (plt.rcdefaults) before rendering"
    )


def test_figure_source_map_can_regenerate(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    source_map = generate_all_figures(root)
    assert source_map["figure_count"] == 59
    figure_ids = {row["id"] for row in source_map["figures"]}
    assert "data_processing_monotonicity" in figure_ids
    assert "graphical_abstract_cover" in figure_ids
    assert "qrf_boundary_graphical_model" not in figure_ids
    assert [row["id"] for row in source_map["figures"][1:4]] == [
        "qrf_boundary_screen_geometry",
        "qrf_channel_relabeling_ledger",
        "qrf_invariance_policy_flow",
    ]
    qrf_row = next(row for row in source_map["figures"] if row["id"] == "qrf_channel_relabeling_ledger")
    assert qrf_row["channel_labels"] == [f"b{index}" for index in range(6)]
    assert "output/data/qrf_boundary_channel_ledger.json" in qrf_row["source_artifacts"]
    assert "equations 7-10" in qrf_row["caption"].lower()
    assert "ontological" in qrf_row["caption"]
    assert "finite_quantum_scope_summary" in figure_ids
    assert "qrf_reference_frame_geometry" in figure_ids
    assert "quantum_boundary_entropy_landscape" in figure_ids
    assert "quantum_contextuality_witness" in figure_ids
    assert "quantum_measurement_contextuality_table" in figure_ids
    assert "quantum_local_polytope_audit" in figure_ids
    assert "quantum_open_system_dynamics" in figure_ids
    assert "qfep_boundary_hamiltonian_dynamics" in figure_ids
    assert "many_body_boundary_screen_sweep" in figure_ids
    assert "sheaf_contextuality_obstruction_audit" in figure_ids
    assert "qrf_transformation_covariance_audit" in figure_ids
    assert "empirical_adapter_provenance_audit" in figure_ids
    assert "arbitrary_two_qubit_entanglement_audit" in figure_ids
    assert "general_measurement_cover_polytope_audit" in figure_ids
    assert "thermodynamic_channel_cost_audit" in figure_ids
    assert "sparse_boundary_screen_scaling_audit" in figure_ids
    assert "qrf_frame_covariance_toy_audit" in figure_ids
    assert "criticality_stochastic_ensemble" in figure_ids
    assert "stochastic_effect_size_forest" in figure_ids
    assert "bmr_robustness_resampling" in figure_ids
    assert "quantum_trajectory_convergence" in figure_ids
    assert "visual_semantic_palette_ledger" in figure_ids
    assert "method_assumption_failure_map" in figure_ids
    assert "quantum_trajectory_unraveling" in figure_ids
    assert "quantum_roadmap_readiness_matrix" in figure_ids
    assert "pymdp_runtime_validation_dashboard" in figure_ids
    assert "claim_context_evidence_ladder" in figure_ids
    for row in source_map["figures"]:
        assert (root / row["path"]).exists()
        assert row["visual_encoding"]
        assert len(row["alt_text"]) >= 80
        assert row["render_contract"]["panel_count"] >= 1
        assert row["render_contract"]["legend_count"] + row["render_contract"]["colorbar_count"] >= 1
        assert row["render_contract"]["min_font_pt"] >= MIN_READABLE_FONT_PT
        assert row["layout_ok"] is True
        assert row["text_overlap_count"] == 0
        assert row["title_overlap_count"] == 0
        assert row["cropped_text_count"] == 0
        assert row["legend_axis_overlap_count"] == 0
    integrity = build_figure_integrity_audit(root, source_map)
    assert integrity["ok"] is True
    assert integrity["figure_count"] == 59
    assert integrity["blank_figures"] == []
    caption_audit = json.loads((root / "output" / "data" / "visual_caption_audit.json").read_text(encoding="utf-8"))
    assert caption_audit["ok"] is True
    assert caption_audit["missing_visual_encodings"] == []
    rendered_caption_audit = json.loads((root / "output" / "data" / "rendered_figure_caption_audit.json").read_text(encoding="utf-8"))
    assert rendered_caption_audit["ok"] is True
    assert rendered_caption_audit["missing_or_weak_captions"] == []
    assert rendered_caption_audit["missing_interpretive_boundaries"] == []
    negative = build_rendered_figure_caption_audit_from_texts(
        {
            "03_results.md": "![Short caption.](../output/figures/qrf_sectorisation_map.png){#fig:bad width=90%}",
        },
        root,
    )
    assert negative["ok"] is False
    assert negative["missing_or_weak_captions"] == ["03_results.md::qrf_sectorisation_map"]
    assert negative["missing_interpretive_boundaries"] == ["03_results.md::qrf_sectorisation_map"]
    accessibility_audit = json.loads((root / "output" / "data" / "visual_accessibility_audit.json").read_text(encoding="utf-8"))
    assert accessibility_audit["ok"] is True
    assert accessibility_audit["missing_alt_text"] == []
    assert accessibility_audit["missing_non_color_encoding"] == []
    assert accessibility_audit["missing_legend_or_colorbar"] == []
    visual_style = json.loads((root / "output" / "data" / "visual_style_audit.json").read_text(encoding="utf-8"))
    assert visual_style["ok"] is True
    assert visual_style["missing_roles"] == []
    assert visual_style["missing_legend_or_colorbar"] == []
    assert visual_style["low_contrast_roles"] == []
    legibility = json.loads((root / "output" / "data" / "figure_legibility_audit.json").read_text(encoding="utf-8"))
    assert legibility["ok"] is True
    assert legibility["minimum_width_px"] >= 1200
    assert legibility["minimum_height_px"] >= 600
    assert legibility["minimum_readable_font_pt"] >= MIN_READABLE_FONT_PT
    assert legibility["undersized"] == []
    assert legibility["undersized_text"] == []
    assert legibility["missing_legend_or_colorbar"] == []
    assert legibility["overlapping_text"] == []
    assert legibility["overlapping_titles"] == []
    assert legibility["cropped_text"] == []
    assert legibility["legend_axis_overlaps"] == []
    assert legibility["layout_failures"] == []
    dashboard_payload = build_artifact_dashboard_payload(root, source_map)
    assert dashboard_payload["figures"]["figure_count"] == 59
    assert dashboard_payload["pymdp_runtime"]["all_controls_pass"] is True
    assert dashboard_payload["pymdp_runtime"]["replay_equal"] is True
    assert dashboard_payload["pymdp_runtime"]["canary_warning_count"] >= 1
    assert dashboard_payload["pymdp_runtime"]["max_weighted_expected_free_energy_residual"] < 1e-7
    assert dashboard_payload["roadmap"]["implemented_count"] >= 17
    assert set(dashboard_payload["roadmap"]["future_ids"]) == {"re-3", "re-4", "re-13", "re-14", "re-15"}
    assert set(dashboard_payload["roadmap"]["blocked_task_ids"]) == {"re-3", "re-4", "re-13", "re-14", "re-15"}
    assert set(dashboard_payload["readiness"]["future_ids"]) == {"re-3", "re-4", "re-13", "re-14", "re-15"}
    assert dashboard_payload["readiness"]["forged_completed_future_row_rejected"] is True
    assert dashboard_payload["todo_audit"]["historical_backlog_rows"] == []
    assert dashboard_payload["stochastic_engines"]["active_inference_ensemble_ok"] is True
    assert dashboard_payload["stochastic_engines"]["criticality_ensemble_ok"] is True
    assert dashboard_payload["stochastic_engines"]["quantum_trajectory_ok"] is True
    assert dashboard_payload["manuscript_audits"]["references_ok"] is True
    assert dashboard_payload["manuscript_audits"]["figure_reuse_ok"] is True
    assert dashboard_payload["manuscript_audits"]["cover_graphic_ok"] is True
    assert dashboard_payload["manuscript_audits"]["claim_intensity_ok"] is True
    assert dashboard_payload["statistical_robustness"]["all_controls_pass"] is True
    assert dashboard_payload["visual_quality"]["style_ok"] is True
    assert dashboard_payload["visual_quality"]["legibility_ok"] is True
    assert dashboard_payload["visual_quality"]["layout_failures"] == []
    assert dashboard_payload["method_governance"]["all_methods_have_controls"] is True
    assert dashboard_payload["source_fit"]["all_controls_pass"] is True
    assert dashboard_payload["source_fit"]["qrf_bmr_opacification_not_quantum_only"] is True
    assert dashboard_payload["claim_context"]["all_controls_pass"] is True
    assert dashboard_payload["claim_context"]["claim_count"] == 15
    assert dashboard_payload["claim_context"]["role_compatibility_failures"] == []
    assert dashboard_payload["claim_context"]["proxy_overclaiming_reader_claims"] == []
    assert dashboard_payload["claim_context"]["missing_future_evidence"] == []
    assert dashboard_payload["contract_registry"]["all_controls_pass"] is True
    assert dashboard_payload["review_hardening"]["artifact_release_ok"] is True
    assert dashboard_payload["review_hardening"]["review_response_ok"] is True
    assert dashboard_payload["review_hardening"]["figure_parameter_ledger_ok"] is True
    assert dashboard_payload["review_hardening"]["qrf_label_ablation_ok"] is True
    assert dashboard_payload["review_hardening"]["quantum_crosscheck_ok"] is True
    assert dashboard_payload["review_hardening"]["bmr_alternative_ok"] is True
    assert dashboard_payload["review_hardening"]["public_reproduction_status"] == "blocked_external_publication"
    assert dashboard_payload["manuscript_audits"]["figure_placement_ok"] is True
    assert dashboard_payload["manuscript_audits"]["governance_figures_in_main"] == []
    assert dashboard_payload["manuscript_audits"]["governance_figures_missing_from_supplement"] == []
    assert dashboard_payload["manuscript_audits"]["governance_figures_repeated_in_supplement"] == []
    arc = dashboard_payload["argument_arc"]
    assert len(arc) == 7
    assert [item["stage"] for item in arc][0] == "Boundary screen"
    assert all(item["figure_present"] for item in arc), "every argument-arc stage must point at a real figure"
    write_artifact_dashboard(root, source_map)
    dashboard_html = (root / "output" / "dashboard" / "index.html").read_text(encoding="utf-8")
    assert "Argument Arc" in dashboard_html
    assert "Review Hardening" in dashboard_html
    assert '<a href="../figures/qrf_sector_situation.png">' in dashboard_html  # figures are a clickable gallery


def test_layout_oracle_accepts_clean_matplotlib_layout() -> None:
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    ax.plot([0, 1, 2], [0.1, 0.3, 0.2], label="finite trajectory")
    ax.set_title("Clean finite trajectory")
    ax.set_xlabel("step")
    ax.set_ylabel("diagnostic")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))
    fig.tight_layout()
    telemetry = _measure_layout(fig)
    plt.close(fig)
    assert telemetry["layout_ok"] is True
    assert telemetry["text_overlap_count"] == 0
    assert telemetry["cropped_text_count"] == 0


def test_layout_oracle_rejects_overlapping_text() -> None:
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot([0, 1], [0, 1])
    fig.text(0.5, 0.5, "overlap", ha="center", va="center")
    fig.text(0.5, 0.5, "overlap", ha="center", va="center")
    telemetry = _measure_layout(fig)
    plt.close(fig)
    assert telemetry["layout_ok"] is False
    assert telemetry["text_overlap_count"] >= 1


def test_layout_oracle_rejects_cropped_text() -> None:
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot([0, 1], [0, 1])
    fig.text(-0.12, 0.5, "cropped label", ha="left", va="center")
    telemetry = _measure_layout(fig)
    plt.close(fig)
    assert telemetry["layout_ok"] is False
    assert telemetry["cropped_text_count"] >= 1


def test_layout_oracle_rejects_legend_axis_collision() -> None:
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot([0, 1, 2], [1, 2, 1], label="diagnostic")
    ax.set_xlabel("axis label under collision")
    fig.legend(*ax.get_legend_handles_labels(), loc="center", bbox_to_anchor=(0.5, 0.05))
    telemetry = _measure_layout(fig)
    plt.close(fig)
    assert telemetry["layout_ok"] is False
    assert telemetry["legend_axis_overlap_count"] >= 1


def test_root_design_contract_tracks_visual_semantics(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    design_path = root / "DESIGN.md"
    assert design_path.exists()
    design = design_path.read_text(encoding="utf-8")
    assert "Realizing Emptiness Design Contract" in design
    assert "not empirical evidence" in design
    assert f"Minimum readable font: {MIN_READABLE_FONT_PT:.1f} pt" in design
    for role, color in semantic_colors().items():
        assert f"`{role}`" in design
        assert color in design
    assert len(SEMANTIC_COLORS) >= 10


def test_figure_integrity_rejects_stale_hash(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    saved = build_figure_integrity_audit(root)
    broken_rows = [{**row, "sha256": "0" * 64} if index == 0 else row for index, row in enumerate(saved["rows"])]
    comparison = compare_figure_integrity(root, {**saved, "rows": broken_rows})
    assert comparison["ok"] is False
    assert comparison["figure_hash_mismatches"] == [saved["rows"][0]["id"]]


def test_documentation_contract_and_method_inventory(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    assert check_documentation_contract(root) == []
    assert _readme_section_table(root) == _manifest_section_table(root)
    inventory = root / "docs" / "method-inventory.md"
    assert inventory.exists()
    assert "BoundaryScreen" in inventory.read_text(encoding="utf-8")
    variables = json.loads((root / "output" / "data" / "manuscript_variables.json").read_text(encoding="utf-8"))
    assert variables["VALIDATION_TOTAL_COUNT"] >= 10
    assert variables["VALIDATION_PASS_COUNT"] == variables["VALIDATION_TOTAL_COUNT"]


def test_reproducibility_material_stays_supplemental(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    main_text = "\n".join((root / "docs" / "manuscript" / name).read_text(encoding="utf-8") for name in ("02_methods.md", "03_results.md", "05_conclusion.md"))
    supplement_text = (root / "docs" / "manuscript" / "06_supplement.md").read_text(encoding="utf-8")
    assert "Reproducibility Gates" not in main_text
    assert "The validation report records" not in main_text
    assert "# Supplementary Audits and Reproducibility {#sec:supplement}" in supplement_text
    assert "## Reproducibility Gates and Meta-Manuscript Record {#sec:supplement-meta-manuscript-record}" in supplement_text
    assert "### Reproducibility Gates {#sec:supplement-reproducibility-gates}" in supplement_text
    assert "The validation report records" in supplement_text
    top_level = re.findall(r"^## .+$", supplement_text, flags=re.MULTILINE)
    assert top_level[-1] == "## Reproducibility Gates and Meta-Manuscript Record {#sec:supplement-meta-manuscript-record}"
    assert not re.search(
        r"^## Reproducibility Gates \{#sec:supplement-reproducibility-gates\}$",
        supplement_text,
        flags=re.MULTILINE,
    )
    for retired_top_level in (
        "Claim Reading Guide and Evidence Ceilings",
        "Figure Source Maps and Visual QA",
        "Supplemental Limitations",
    ):
        assert not re.search(rf"^## {re.escape(retired_top_level)}(?: |\n|$)", supplement_text, flags=re.MULTILINE)
    for nested_anchor in (
        "### Claim Reading Guide and Evidence Ceilings {#sec:supplement-claim-evidence-ceilings}",
        "### Figure Source Maps and Visual QA {#sec:supplement-visualization}",
        "### Release, Review Response, and Limits {#sec:supplement-release-review-response}",
    ):
        assert nested_anchor in supplement_text
    assert "### Supplemental Limitations {#sec:supplemental-limitations}" not in supplement_text
    assert "[]{#sec:supplemental-limitations}" in supplement_text
    assert "[]{#sec:supplement-limitations}" in supplement_text
    final_section = supplement_text.split("## Reproducibility Gates and Meta-Manuscript Record", 1)[1]
    assert len(re.findall(r"^### ", final_section, flags=re.MULTILINE)) == 4


def test_manuscript_subsection_titles_and_references(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    methods = (root / "docs" / "manuscript" / "02_methods.md").read_text(encoding="utf-8")
    results = (root / "docs" / "manuscript" / "03_results.md").read_text(encoding="utf-8")
    discussion = (root / "docs" / "manuscript" / "04_discussion.md").read_text(encoding="utf-8")
    conclusion = (root / "docs" / "manuscript" / "05_conclusion.md").read_text(encoding="utf-8")
    supplement = (root / "docs" / "manuscript" / "06_supplement.md").read_text(encoding="utf-8")
    assert "## Equation Registry and Finite qFEP Engines {#sec:methods-roadmap-quantum-engines}" in methods
    assert "## Finite QRF Boundary Screen and Relabeling Rules {#sec:methods-finite-qrf-boundary-screen}" in methods
    assert "## Separation Prior as a Restricted QRF Subspace {#sec:methods-separation-prior-subspace}" in methods
    assert "## Boundary Geometry and QRF Indistinguishability {#sec:results-qrf-boundary-geometry}" in results
    assert "## Finite Quantum Scope and Blocked Claims {#sec:results-finite-quantum-scope}" in results
    assert "## pymdp Profiles and Policy Trace {#sec:results-pymdp-policy-trace}" in results
    # Governance/proxy content is partitioned out of the main Results into the supplement.
    assert "{#sec:results-evidence-ceiling-stress}" not in results
    assert "### Claim Reading Guide and Evidence Ceilings {#sec:supplement-claim-evidence-ceilings}" in supplement
    assert "## Reproducibility Gates and Meta-Manuscript Record {#sec:supplement-meta-manuscript-record}" in supplement
    assert "## What the Software Boundary Establishes {#sec:discussion-no-self-evidence-boundary}" in discussion
    assert "## Evidence Required for Stronger Claims {#sec:discussion-evidence-ceilings}" in discussion
    assert "## Source-Faithful Platform for Future Evidence {#sec:conclusion-source-faithful-platform}" in conclusion
    assert "# Supplementary Audits and Reproducibility {#sec:supplement}" in supplement
    assert "## Criticality Signatures with Null Controls {#sec:supplement-criticality-indicators}" in supplement
    assert "### Figure Source Maps and Visual QA {#sec:supplement-visualization}" in supplement
    assert "### Release, Review Response, and Limits {#sec:supplement-release-review-response}" in supplement
    combined = "\n".join([methods, results, discussion])
    for anchor in (
        "@sec:methods-finite-qrf-boundary-screen",
        "@sec:methods-roadmap-quantum-engines",
        "@sec:results-finite-quantum-scope",
        "@sec:supplement-finite-quantum-contextuality-audits",
        "@sec:discussion-evidence-ceilings",
    ):
        assert anchor in combined


def test_manuscript_prose_and_visual_reference_contract(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    abstract = (root / "docs" / "manuscript" / "00_abstract.md").read_text(encoding="utf-8")
    intro = (root / "docs" / "manuscript" / "01_introduction.md").read_text(encoding="utf-8")
    results = (root / "docs" / "manuscript" / "03_results.md").read_text(encoding="utf-8")
    supplement = (root / "docs" / "manuscript" / "06_supplement.md").read_text(encoding="utf-8")
    source_fragment_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (root / "docs" / "manuscript" / "sections").rglob("*.md")
    )

    abstract_lines = [line.strip() for line in abstract.splitlines() if line.strip()]
    abstract_paragraphs = [
        line
        for line in abstract_lines
        if not line.startswith("#")
        and not line.startswith("```")
        and "graphical_abstract_cover.png" not in line
        and not line.startswith("\\")
        and not line.startswith("<figure")
    ]
    assert len(abstract_paragraphs) == 1
    abstract_paragraph = abstract_paragraphs[0]
    assert "[@sandvedsmith2026noself]" in abstract_paragraph
    # Acronyms are spelled out at first use in the standalone abstract.
    assert "quantum free-energy principle (qFEP)" in abstract_paragraph
    assert "quantum reference frame (QRF)" in abstract_paragraph
    # The abstract is plain standalone prose: no inline formula notation.
    assert "Delta F = F_reduced - F_full" not in abstract_paragraph
    assert "F_reduced" not in abstract_paragraph
    assert "Bayesian model reduction" in abstract_paragraph
    assert "seeded stochastic" in abstract_paragraph
    assert "quantum-trajectory" in abstract_paragraph
    assert "This pass" not in abstract_paragraph
    assert "draft" not in abstract_paragraph.lower()
    assert "runtime canary" not in abstract_paragraph

    first_intro_body = next(line.strip() for line in intro.splitlines() if line.strip() and not line.startswith("#"))
    assert first_intro_body.startswith("Sandved-Smith et al. [@sandvedsmith2026noself]")
    assert "`B = {b0, b1, b2, b3, b4, b5}`" in intro
    assert "A quantum reference frame (QRF), as used here, is a frame-dependent sector labeling" in intro
    assert "six-channel screen is the smallest current surrogate" in intro
    assert "not six ontological sectors" in intro
    for role in (
        "body-controllability",
        "action-contingency",
        "distal-world",
        "contextual-world",
        "other-agent",
        "care-salience",
    ):
        assert role in intro
    for sector_definition in (
        "Self marks channels treated as belonging to the modeled agent",
        "Action marks a channel whose changes are conditioned by selected policy",
        "Body marks controllability without making a biological-body claim",
        "Environment or env marks the residual non-self field",
        "World marks contextual non-self structure",
        "Other marks a non-self agent-like cue",
        "Care marks a salience cue used by the bounded compassion-scope proxy",
    ):
        assert sector_definition in intro
    for partition in (
        "`b0,b1,b5 -> self`",
        "`b2,b3,b4 -> env`",
        "`b0 -> self`",
        "`b1 -> action`",
        "`b2,b3 -> env`",
        "`b4 -> other`",
        "`b5 -> care`",
        "`b0 -> body`",
        "`b2,b3 -> world`",
    ):
        assert partition in intro
    assert "not a discovered biological sensor, physical boundary qubit, or ontological sector" in intro
    assert "cannot by itself certify an ontological self/world boundary" in intro
    assert "@fig:qrf_boundary_screen_geometry" in intro
    assert "{#fig:qrf_boundary_screen_geometry" in intro
    assert "../output/figures/qrf_boundary_screen_geometry.png" in intro
    assert "../output/figures/qrf_boundary_screen_geometry.png" not in results
    assert "{#fig:qrf_boundary_screen_geometry" not in results
    assert "@fig:qrf_boundary_screen_geometry" in results
    assert "@fig:qrf_channel_relabeling_ledger" in results
    assert "@fig:qrf_invariance_policy_flow" in results
    assert "{#fig:qrf_channel_relabeling_ledger" in results
    assert "{#fig:qrf_invariance_policy_flow" in results
    assert "../output/figures/qrf_boundary_graphical_model.png" not in results
    qrf_paths = [
        "../output/figures/qrf_channel_relabeling_ledger.png",
        "../output/figures/qrf_invariance_policy_flow.png",
    ]
    assert [results.find(path) for path in qrf_paths] == sorted(results.find(path) for path in qrf_paths)
    methods = (root / "docs" / "manuscript" / "02_methods.md").read_text(encoding="utf-8")
    for path in (
        "../output/figures/separation_prior_emergence.png",
        "../output/figures/separation_prior_net_value.png",
    ):
        assert path not in methods
        assert path in results
    assert results.find("../output/figures/separation_prior_emergence.png") < results.find("../output/figures/separation_prior_net_value.png")
    assert results.find("../output/figures/separation_prior_net_value.png") < results.find("../output/figures/bmr_free_energy_decomposition.png")
    discussion = (root / "docs" / "manuscript" / "04_discussion.md").read_text(encoding="utf-8")
    conclusion = (root / "docs" / "manuscript" / "05_conclusion.md").read_text(encoding="utf-8")
    for phrase in (
        "boundary use, QRF relabeling, separation-prior emergence, BMR pruning, and post-dual revision",
        "finite success changes model organization, not the evidence class",
        "what the software establishes is narrower than the vocabulary it makes inspectable",
    ):
        assert phrase in discussion
    for phrase in (
        "The manuscript's contribution is therefore a disciplined chain",
        "The uncrossed boundary is part of the result",
        "future evidence classes remain explicit work packages",
    ):
        assert phrase in conclusion
    assert "@fig:finite_quantum_scope_summary" in results
    assert "{#fig:finite_quantum_scope_summary" in results
    assert "@fig:pymdp_runtime_validation_dashboard" in results
    assert "../output/figures/pymdp_runtime_validation_dashboard.png" in supplement
    assert "This section adapts the source paper's \"contemplative inquiry as progressive opacification\"" in supplement
    assert "This section riffs" not in supplement
    for slogan in (
        "Use the boundary; do not promote it.",
        "Same bits, different frames.",
        "The cut is drawn, not found.",
        "Inspect the channel you look through.",
        "A prior earns its keep or leaves.",
        "Relabel the sector; keep the stream fixed.",
        "Undecided by the data is a disciplined result.",
        "A gauge is not a goal.",
        "No channel owns \"me.\"",
        "What organizes the screen is also inspectable.",
        "A useful frame is not an ontological verdict.",
        "Hold the cut lightly; audit it strictly.",
    ):
        assert slogan in supplement
    # The claim-context evidence ladder and its governance prose moved to the supplement.
    assert "@fig:claim_context_evidence_ladder" in supplement
    assert "{#fig:claim_context_evidence_ladder" in supplement
    assert "../output/figures/claim_context_evidence_ladder.png" in supplement
    assert "A longer bar therefore means broader source-role context, not a higher evidence class" in supplement
    assert "../output/figures/qrf_sectorisation_map.png" not in results
    assert "../output/figures/boundary_indistinguishability.png" not in results
    assert "../output/figures/qrf_reference_frame_geometry.png" not in results
    technical_quantum_paths = [
        "../output/figures/quantum_boundary_entropy_landscape.png",
        "../output/figures/arbitrary_two_qubit_entanglement_audit.png",
        "../output/figures/quantum_contextuality_witness.png",
        "../output/figures/quantum_measurement_contextuality_table.png",
        "../output/figures/quantum_local_polytope_audit.png",
        "../output/figures/general_measurement_cover_polytope_audit.png",
        "../output/figures/quantum_open_system_dynamics.png",
        "../output/figures/quantum_trajectory_unraveling.png",
        "../output/figures/quantum_trajectory_convergence.png",
        "../output/figures/thermodynamic_channel_cost_audit.png",
        "../output/figures/qfep_boundary_hamiltonian_dynamics.png",
        "../output/figures/many_body_boundary_screen_sweep.png",
        "../output/figures/sparse_boundary_screen_scaling_audit.png",
        "../output/figures/sheaf_contextuality_obstruction_audit.png",
        "../output/figures/qrf_transformation_covariance_audit.png",
        "../output/figures/qrf_frame_covariance_toy_audit.png",
        "../output/figures/empirical_adapter_provenance_audit.png",
        "../output/figures/quantum_roadmap_readiness_matrix.png",
    ]
    for path in technical_quantum_paths:
        assert path not in results
        assert path in supplement
    governance_paths = [
        "../output/figures/scholarship_coverage_matrix.png",
        "../output/figures/claim_support_matrix.png",
        "../output/figures/claim_source_validation_graph.png",
        "../output/figures/visual_semantic_palette_ledger.png",
    ]
    for path in governance_paths:
        assert path not in results
        assert path in supplement
        assert supplement.count(path) == 1
    assert "Pruning decisions across the BMR grid" not in results
    assert "deterministic proxy summaries" not in results
    assert "pinned pymdp runtime" not in results
    assert "constructive finite demonstrations" not in abstract
    assert "constructive demonstration rather than a falsifiable test" not in source_fragment_text
    assert "pymdp policy traces realize the profiles" not in results
    assert "realizing each licensed sector frame" not in results
    for placeholder in (
        "![pymdp profile comparison.]",
        "![Posterior trajectory across QRF profiles.]",
        "![Criticality stochastic ensemble.]",
        "![Stochastic effect-size forest.]",
        "![Unified QRF boundary graphical model.]",
    ):
        assert placeholder not in source_fragment_text
    assert "graphical_abstract_cover.png" in abstract
    assert "#fig:graphical_abstract_cover" not in abstract

    image_re = re.compile(r"(?:!\[[^\]]*\]\(|\\includegraphics(?:\[[^\]]*\])?\{)([^)}]+)")
    main_pngs = set()
    for text in [
        abstract,
        intro,
        (root / "docs" / "manuscript" / "02_methods.md").read_text(encoding="utf-8"),
        results,
        (root / "docs" / "manuscript" / "04_discussion.md").read_text(encoding="utf-8"),
        (root / "docs" / "manuscript" / "05_conclusion.md").read_text(encoding="utf-8"),
    ]:
        main_pngs.update(path for path in image_re.findall(text) if path.endswith(".png"))
    for path in main_pngs:
        assert path not in supplement

    reference = build_manuscript_reference_audit(root)
    reuse = build_figure_reuse_audit(root)
    placement = build_figure_placement_audit(root)
    cover = build_cover_graphical_abstract_audit(root)
    assert reference["ok"] is True
    assert reference["hardcoded_figure_numbers"] == []
    assert reference["equation_reference_count"] >= 4
    assert reuse["ok"] is True
    assert placement["ok"] is True
    assert placement["technical_quantum_figures_in_main"] == []
    assert placement["governance_figures_in_main"] == []
    assert placement["governance_figures_missing_from_supplement"] == []
    assert placement["governance_figures_repeated_in_supplement"] == []
    assert placement["controls"]["qrf_lead_figures_present_in_main"] is True
    assert placement["controls"]["qrf_lead_figures_ordered"] is True
    assert placement["controls"]["qrf_figures_precede_quantum_summary"] is True
    assert placement["controls"]["retired_qrf_composite_absent"] is True
    assert cover["ok"] is True
    assert cover["cover_style"] == "hybrid_symbolic_near_square_large_type"
    assert cover["aspect_ratio_ok"] is True
    assert 1.15 <= cover["aspect_ratio"] <= 1.25
    assert cover["dimensions_ok"] is True
    assert cover["referenced_in_title_preamble"] is True


def test_roadmap_todo_and_dependency_graph_contracts(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    todo_audit = build_roadmap_todo_audit(root)
    assert todo_audit["all_controls_pass"] is True
    assert todo_audit["stale_future_rows"] == []
    assert todo_audit["historical_backlog_rows"] == []
    assert todo_audit["blocked_external_class_violations"] == []
    assert todo_audit["controls"]["todo_backlog_has_no_historical_completion_rows"] is True
    assert todo_audit["controls"]["all_blocked_external_task_ids_present_and_blocked"] is True
    assert set(todo_audit["blocked_task_ids"]) >= {"re-3", "re-4", "re-13", "re-14", "re-15"}
    dependency = build_validation_dependency_graph(root)
    assert dependency["all_controls_pass"] is True
    nodes = set(dependency["nodes"])
    for node in (
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
        "qrf_boundary_channel_ledger",
        "source_argument_coverage_audit",
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
        "manuscript_figure_placement_audit",
        "cover_graphical_abstract_audit",
        "roadmap_todo_audit",
        "artifact_dashboard",
        "pdf_render_gate",
    ):
        assert node in nodes
    contracts = build_artifact_contract_registry(root)
    assert contracts["all_controls_pass"] is True
    assert contracts["missing_schema_paths"] == []
    assert contracts["duplicate_ids"] == []
    manifest_paths = {row["path"] for row in contracts["rows"]}
    assert "output/data/statistical_robustness_audit.json" in manifest_paths
    assert "output/data/pymdp_runtime_diagnostics_log.json" in manifest_paths
    assert "output/figures/pymdp_runtime_validation_dashboard.png" in manifest_paths
    assert "output/data/claim_context_ledger.json" in manifest_paths
    assert "output/data/claim_redteam_audit.json" in manifest_paths
    assert "output/data/artifact_release_manifest.json" in manifest_paths
    assert "output/data/external_review_response_audit.json" in manifest_paths
    assert "output/data/figure_parameter_ledger.json" in manifest_paths
    assert "output/data/qrf_label_ablation_audit.json" in manifest_paths
    assert "output/data/quantum_independent_crosscheck_audit.json" in manifest_paths
    assert "output/data/bmr_alternative_prior_audit.json" in manifest_paths
    assert "output/figures/method_assumption_failure_map.png" in manifest_paths
    assert "output/figures/claim_context_evidence_ladder.png" in manifest_paths


def test_roadmap_blocked_class_coverage_control_has_teeth(pytestconfig, tmp_path) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    # Real no-mocks fixture: mirror the three files the audit reads into a temp project.
    (tmp_path / "output" / "data").mkdir(parents=True)
    (tmp_path / "TODO.md").write_text((root / "TODO.md").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "output" / "data" / "quantum_extension_roadmap.json").write_text(
        (root / "output" / "data" / "quantum_extension_roadmap.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    tasks = yaml.safe_load((root / "tasks.yaml").read_text(encoding="utf-8"))
    (tmp_path / "tasks.yaml").write_text(yaml.safe_dump(tasks), encoding="utf-8")
    assert build_roadmap_todo_audit(tmp_path)["controls"]["all_blocked_external_task_ids_present_and_blocked"] is True
    pruned = {**tasks, "tasks": [task for task in tasks["tasks"] if task.get("id") != "re-13"]}
    (tmp_path / "tasks.yaml").write_text(yaml.safe_dump(pruned), encoding="utf-8")
    pruned_audit = build_roadmap_todo_audit(tmp_path)
    assert pruned_audit["controls"]["all_blocked_external_task_ids_present_and_blocked"] is False
    assert "re-13" in pruned_audit["missing_blocked_task_ids"]
    assert pruned_audit["all_controls_pass"] is False
    historical_todo = (root / "TODO.md").read_text(encoding="utf-8").replace(
        "### Blocked external-evidence classes",
        "Built since the review: historical backlog row.\\n\\n### Blocked external-evidence classes",
        1,
    )
    (tmp_path / "TODO.md").write_text(historical_todo, encoding="utf-8")
    (tmp_path / "tasks.yaml").write_text(yaml.safe_dump(tasks), encoding="utf-8")
    historical_audit = build_roadmap_todo_audit(tmp_path)
    assert historical_audit["controls"]["todo_backlog_has_no_historical_completion_rows"] is False
    assert historical_audit["historical_backlog_rows"][0]["phrases"] == ["built since", "historical backlog"]
    assert historical_audit["all_controls_pass"] is False


def test_rendered_figure_caption_audit_reads_real_manuscript(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    audit = build_rendered_figure_caption_audit(root)
    assert audit["schema"] == "realizing_emptiness.rendered_figure_caption_audit.v1"
    assert audit["figure_reference_count"] >= 1
    assert audit["ok"] is True
    assert audit["missing_interpretive_boundaries"] == []
    assert audit["missing_visual_encoding_language"] == []
    # Round-trip the writer.
    path = write_rendered_figure_caption_audit(root)
    assert json.loads(path.read_text())["ok"] is True
    # The composer expands a short Markdown caption to the source-of-truth caption.
    short = "![x](../output/figures/practice_policy_scope_map.png){#fig:practice_policy_scope_map}"
    expanded = expand_markdown_figure_captions(short, root)
    assert "Practice protocols" in expanded
    assert len(expanded) > len(short)
    # An unknown figure path is left untouched.
    unknown = "![y](../output/figures/does_not_exist.png)"
    assert expand_markdown_figure_captions(unknown, root) == unknown


def test_method_assumption_failure_map_handles_empty_contract_cell(pytestconfig, tmp_path) -> None:
    # Regression: an empty contract field renders an "N" cell whose text colour reads `colors`,
    # which used to be undefined (NameError). A method with an empty assumptions list exercises
    # that previously-dark else-branch; the figure must render rather than raise.
    from visualizations.figures import _load_style, _method_assumption_failure_map

    root: Path = pytestconfig.realizing_emptiness_root
    style = _load_style(root)
    ledger = {
        "rows": [
            {
                "method_id": "empty_contract_method",
                "hard_constraints": ["x"],
                "modeling_choices": ["y"],
                "assumptions": [],  # empty -> N cell -> exercises the else colour branch
                "evidence_ceiling": "finite",
            }
        ]
    }
    controls = {"rows": []}  # no negative controls -> N cell + zero count
    output_dir = tmp_path / "output" / "figures"
    output_dir.mkdir(parents=True)
    # Render into tmp by pointing the style filename through the real fig-path helper.
    path = _method_assumption_failure_map(tmp_path, style, ledger, controls)
    assert path.exists()
    assert path.stat().st_size > 0


def test_validate_outputs_flips_specific_check_on_targeted_corruption(pytestconfig, tmp_path) -> None:
    import shutil

    root: Path = pytestconfig.realizing_emptiness_root
    work = tmp_path / "tree"
    shutil.copytree(
        root,
        work,
        ignore=shutil.ignore_patterns(".venv", ".git", ".pytest_cache", "__pycache__", ".coverage"),
    )
    baseline = validate_outputs(work)
    assert all(baseline.values()), [name for name, ok in baseline.items() if not ok]

    # (a) Delete one expected figure (existence-only checked) -> exactly its existence check flips.
    target = "output/figures/criticality_signatures.png"
    (work / target).unlink()
    after_delete = validate_outputs(work)
    assert after_delete[f"exists:{target}"] is False
    flipped = [name for name, ok in after_delete.items() if not ok and baseline[name]]
    # The figure's existence check must flip; deleting it also trips integrity/contract checks that
    # enumerate it, but no unrelated check class should collapse en masse.
    assert f"exists:{target}" in flipped
    assert set(flipped) <= {
        f"exists:{target}",
        "artifact_paths_exist",
        "artifact_release_manifest_hashes_current",
        "artifact_release_manifest_ok",
        "claim_context_ledger_ok",
        "claim_crosswalk_gates_resolve",
        "external_review_response_audit_ok",
        "external_review_response_gates_resolve",
        "figure_integrity_audit_ok",
    }
    shutil.copy2(root / target, work / target)  # restore

    # (b) Corrupt a schema-bound JSON artifact -> its schema_valid check flips.
    bmr = work / "output" / "data" / "bmr_sweep.json"
    bmr.write_text('{"schema": "wrong"}', encoding="utf-8")
    after_schema = validate_outputs(work)
    assert after_schema["schema_valid:output/data/bmr_sweep.json"] is False
    shutil.copy2(root / "output" / "data" / "bmr_sweep.json", bmr)

    # (c) Corrupt a gated audit's control -> its named gate flips, baseline otherwise intact.
    compassion = work / "output" / "data" / "compassion_scope_audit.json"
    payload = json.loads(compassion.read_text())
    payload["all_controls_pass"] = False
    compassion.write_text(json.dumps(payload), encoding="utf-8")
    after_gate = validate_outputs(work)
    assert after_gate["compassion_scope_audit_ok"] is False
    shutil.copy2(root / "output" / "data" / "compassion_scope_audit.json", compassion)

    support_source = work / "src" / "formalism" / "models.py"
    support_source.write_text(support_source.read_text(encoding="utf-8") + "\n# stale release negative control\n", encoding="utf-8")
    after_stale_release = validate_outputs(work)
    assert after_stale_release["artifact_release_manifest_hashes_current"] is False
    assert after_stale_release["artifact_release_manifest_ok"] is False
    shutil.copy2(root / "src" / "formalism" / "models.py", support_source)

    review_response = work / "output" / "data" / "external_review_response_audit.json"
    review_payload = json.loads(review_response.read_text(encoding="utf-8"))
    review_payload["rows"][0]["gate"] = "not_a_real_validation_gate"
    review_response.write_text(json.dumps(review_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    after_bogus_gate = validate_outputs(work)
    assert after_bogus_gate["external_review_response_gates_resolve"] is False
    assert after_bogus_gate["external_review_response_audit_ok"] is False
    shutil.copy2(root / "output" / "data" / "external_review_response_audit.json", review_response)

    (work / "output" / "data" / "compassion_scope_audit.json").unlink()
    after_missing = validate_outputs(work)
    assert after_missing["compassion_scope_audit_ok"] is False
    assert after_missing["exists:output/data/compassion_scope_audit.json"] is False


def test_boundary_use_ontology_verdicts_bind_to_audit_flags(pytestconfig) -> None:
    """The use/ontology figure's headline verdict is derived from the audit flags, not asserted.

    Locks the cross-vendor fix: a flipped flag must flip the headline, not just a footnote.
    """
    root: Path = pytestconfig.realizing_emptiness_root
    real = json.loads((root / "output" / "data" / "qrf_boundary_indistinguishability.json").read_text())
    healthy = boundary_use_ontology_verdicts(real)
    assert healthy["use"]["ok"] is True and healthy["use"]["mark"] == "OK"
    assert healthy["ontology"]["ok"] is True and healthy["ontology"]["mark"] == "NO"
    assert "licensed" in healthy["use"]["head"] and "not licensed" in healthy["ontology"]["head"]

    # Negative controls: flipping either audit flag flips the headline verdict.
    use_broken = boundary_use_ontology_verdicts(
        {"all_admissible_distributions_equal": False, "negative_control_fails": True}
    )
    assert use_broken["use"]["ok"] is False and use_broken["use"]["mark"] == "??"
    assert "not confirmed" in use_broken["use"]["head"]
    ont_broken = boundary_use_ontology_verdicts(
        {"all_admissible_distributions_equal": True, "negative_control_fails": False}
    )
    assert ont_broken["ontology"]["ok"] is False and ont_broken["ontology"]["mark"] == "??"
    assert "incomplete" in ont_broken["ontology"]["head"]


def test_separation_prior_lifecycle_is_derived_not_assumed(pytestconfig) -> None:
    """The net-value figure's lifecycle arc is derived from the sweep, not hardcoded to the weakest prior.

    Locks the cross-vendor fix against green-by-construction: the bolded crossing precision must
    track the data, and the grid guard must fail closed.
    """
    root: Path = pytestconfig.realizing_emptiness_root
    real = json.loads((root / "output" / "data" / "bmr_sweep.json").read_text())
    life = separation_prior_lifecycle(real)
    assert life["arc_precision"] == min(life["precisions"])
    assert life["crossing_precisions"] == [min(life["precisions"])]
    assert life["others_pruned"] is True
    assert life["crossing"] is not None and 0.0 < life["crossing"] < 1.0

    def cell(precision: float, access: float, df: float) -> dict:
        return {"prior_precision": precision, "metacognitive_access": access, "delta_free_energy": df, "prunes_prior": df < 0}

    # Derivation, not assumption: when ONLY a stronger precision crosses, it is bolded.
    synthetic = {"rows": [
        cell(0.2, 0.0, -1.0), cell(0.2, 1.0, -2.0),
        cell(4.0, 0.0, 0.5), cell(4.0, 1.0, -0.5),
    ]}
    crossed = separation_prior_lifecycle(synthetic)
    assert crossed["crossing_precisions"] == [crossed["arc_precision"]] == [4.0]
    assert crossed["arc_precision"] == 4.0
    assert crossed["others_pruned"] is True
    assert abs(crossed["crossing"] - 0.5) < 1e-9

    # No crossing anywhere -> no arc claim and no crossing marker.
    flat = {"rows": [cell(0.2, 0.0, -0.1), cell(0.2, 1.0, -0.2), cell(4.0, 0.0, -0.3), cell(4.0, 1.0, -0.4)]}
    nocross = separation_prior_lifecycle(flat)
    assert nocross["crossing_precisions"] == []
    assert nocross["crossing"] is None

    # Ragged sweep grid fails closed.
    raised = False
    try:
        separation_prior_lifecycle({"rows": [cell(0.2, 0.0, 0.1), cell(4.0, 1.0, -0.1)]})
    except ValueError:
        raised = True
    assert raised


def test_reference_audit_catches_hardcoded_numbers(pytestconfig, tmp_path) -> None:
    """Recall + precision for the hardened reference gate: it must go RED on this-manuscript
    hard-coded figure/table/anchored-equation numbers, while leaving source/registry numbering
    and the test-pinned 'equations 7-10' caption label alone."""
    from gates.manuscript import MANUSCRIPT_FILES, build_manuscript_reference_audit

    target = tmp_path / MANUSCRIPT_FILES[0]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "$$x$$ {#eq:7}\n"
        "See Figure 3 and Table 1. As equation 7 shows here. "
        "But equation 7 of the source paper differs, and equations 1-6 map to the registry. "
        "See the equations 7-10 caption.\n",
        encoding="utf-8",
    )
    audit = build_manuscript_reference_audit(tmp_path)
    matches = [row["match"] for row in audit["hardcoded_figure_numbers"]]
    # Recall: hard-coded this-manuscript numbers are caught and the audit fails.
    assert "Figure 3" in matches
    assert "Table 1" in matches
    assert sum(1 for match in matches if match.lower() == "equation 7") == 1
    assert audit["ok"] is False
    # Precision: source/registry numbering and the whitelisted caption label are NOT flagged.
    assert not any("1-6" in match for match in matches)
    assert not any(match.replace(" ", "") == "equations7-10" for match in matches)

    # And the real composed manuscript stays clean (zero false positives).
    real = build_manuscript_reference_audit(pytestconfig.realizing_emptiness_root)
    assert real["hardcoded_figure_numbers"] == []
