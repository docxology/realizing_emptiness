"""Manuscript cross-reference, reuse, and cover-graphic audits."""

from __future__ import annotations

import json
import re
import struct
from pathlib import Path
from typing import Any

import yaml


MANUSCRIPT_FILES = tuple(f"manuscript/{index:02d}_{name}.md" for index, name in (
    (0, "abstract"),
    (1, "introduction"),
    (2, "methods"),
    (3, "results"),
    (4, "discussion"),
    (5, "conclusion"),
    (6, "supplement"),
))

ANCHOR_RE = re.compile(r"#((?:sec|fig|eq):[A-Za-z0-9_.:-]+)")
REF_RE = re.compile(r"@((?:sec|fig|eq):[A-Za-z0-9_.:-]+)")
MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)(\{[^}]*\})?")
LATEX_IMAGE_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
HTML_IMAGE_RE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"']", re.IGNORECASE)
# Hard-coded references to THIS manuscript's figures/tables must use @fig:/@tbl: auto-references.
# Case-insensitive; covers "Figure 3", "figure 3", "fig. 2", "Table 1" (no legitimate numbered
# figure/table reference to this manuscript exists — every figure is referenced via @fig:).
HARDCODED_FIGURE_RE = re.compile(r"(?i)\b(?:figure|fig\.|table)\s+\d+\b")
# Bare references to this manuscript's own anchored equations (only 7-10 have {#eq:} anchors).
# Source/registry/paper equation numbering is legitimately textual and is excluded by a qualifier
# guard; the test-pinned figure-caption range label "equations 7-10" is whitelisted.
EQUATION_TEXT_RE = re.compile(r"(?i)\bequations?\s+(\d+)(?:\s*[-–]\s*(\d+))?\b")
EQUATION_SOURCE_QUALIFIERS = ("source", "registry", "paper", "sandved")
COMPACT_MAIN_QUANTUM_FIGURE = "../output/figures/finite_quantum_scope_summary.png"
QRF_LEAD_FIGURES = (
    "../output/figures/qrf_boundary_screen_geometry.png",
    "../output/figures/qrf_channel_relabeling_ledger.png",
    "../output/figures/qrf_invariance_policy_flow.png",
)
RETIRED_QRF_COMPOSITE_FIGURE = "../output/figures/qrf_boundary_graphical_model.png"
TECHNICAL_QUANTUM_FIGURES = (
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
)
SUPPLEMENTAL_GOVERNANCE_FIGURES = (
    "../output/figures/scholarship_coverage_matrix.png",
    "../output/figures/claim_support_matrix.png",
    "../output/figures/claim_source_validation_graph.png",
    "../output/figures/visual_semantic_palette_ledger.png",
)


def _png_dimensions(path: Path) -> tuple[int, int]:
    if not path.exists():
        return (0, 0)
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) < 24 or not header.startswith(b"\x89PNG\r\n\x1a\n"):
        return (0, 0)
    return struct.unpack(">II", header[16:24])


def _manuscript_texts(project_root: Path) -> dict[str, str]:
    return {
        relative: (project_root / relative).read_text(encoding="utf-8")
        for relative in MANUSCRIPT_FILES
        if (project_root / relative).exists()
    }


def _clean_ref(raw: str) -> str:
    return raw.rstrip(".,;:)]}")


def build_manuscript_reference_audit(project_root: Path) -> dict[str, Any]:
    """Audit composed manuscript section, figure, and equation references."""
    texts = _manuscript_texts(project_root)
    anchors: dict[str, list[str]] = {}
    refs: dict[str, list[str]] = {}
    hardcoded_rows = []
    for relative, text in texts.items():
        for anchor in ANCHOR_RE.findall(text):
            anchors.setdefault(anchor, []).append(relative)
        for ref in REF_RE.findall(text):
            refs.setdefault(_clean_ref(ref), []).append(relative)
        for match in HARDCODED_FIGURE_RE.finditer(text):
            hardcoded_rows.append({"file": relative, "match": match.group(0)})
    anchored_eq_numbers = {anchor.split(":", 1)[1] for anchor in anchors if anchor.startswith("eq:")}
    for relative, text in texts.items():
        for match in EQUATION_TEXT_RE.finditer(text):
            phrase = match.group(0)
            context = text[max(0, match.start() - 32) : match.end() + 40].lower()
            if any(qualifier in context for qualifier in EQUATION_SOURCE_QUALIFIERS):
                continue
            if "".join(phrase.lower().split()) == "equations7-10":
                continue
            numbers = [match.group(1)] + ([match.group(2)] if match.group(2) else [])
            if any(number in anchored_eq_numbers for number in numbers):
                hardcoded_rows.append({"file": relative, "match": phrase})
    duplicate_anchors = sorted(anchor for anchor, files in anchors.items() if len(files) > 1)
    unresolved_refs = sorted(ref for ref in refs if ref not in anchors)
    figure_refs = sorted(ref for ref in refs if ref.startswith("fig:"))
    section_refs = sorted(ref for ref in refs if ref.startswith("sec:"))
    equation_refs = sorted(ref for ref in refs if ref.startswith("eq:"))
    return {
        "schema": "realizing_emptiness.manuscript_reference_audit.v1",
        "file_count": len(texts),
        "anchor_count": len(anchors),
        "reference_count": len(refs),
        "section_reference_count": len(section_refs),
        "figure_reference_count": len(figure_refs),
        "equation_reference_count": len(equation_refs),
        "duplicate_anchors": duplicate_anchors,
        "unresolved_references": unresolved_refs,
        "hardcoded_figure_numbers": hardcoded_rows,
        "ok": not duplicate_anchors and not unresolved_refs and not hardcoded_rows,
    }


def _image_paths(text: str) -> list[str]:
    paths = [match.group(1) for match in MARKDOWN_IMAGE_RE.finditer(text)]
    paths.extend(match.group(1) for match in LATEX_IMAGE_RE.finditer(text))
    paths.extend(match.group(1) for match in HTML_IMAGE_RE.finditer(text))
    return [path for path in paths if path.endswith((".png", ".jpg", ".jpeg", ".pdf", ".svg"))]


def build_figure_reuse_audit(project_root: Path) -> dict[str, Any]:
    """Audit that supplement figures do not duplicate main or cover visuals."""
    texts = _manuscript_texts(project_root)
    rows = []
    usage_by_path: dict[str, list[str]] = {}
    for relative, text in texts.items():
        section_class = "supplement" if relative.endswith("06_supplement.md") else "cover_or_main"
        for figure_path in _image_paths(text):
            row = {"file": relative, "section_class": section_class, "path": figure_path}
            rows.append(row)
            usage_by_path.setdefault(figure_path, []).append(relative)
    main_or_cover_paths = {row["path"] for row in rows if row["section_class"] == "cover_or_main"}
    duplicate_supplement_paths = sorted(
        {
            row["path"]
            for row in rows
            if row["section_class"] == "supplement" and row["path"] in main_or_cover_paths
        }
    )
    return {
        "schema": "realizing_emptiness.figure_reuse_audit.v1",
        "image_reference_count": len(rows),
        "unique_image_path_count": len(usage_by_path),
        "rows": rows,
        "duplicate_supplement_paths": duplicate_supplement_paths,
        "ok": not duplicate_supplement_paths,
    }


def build_figure_placement_audit(project_root: Path) -> dict[str, Any]:
    """Audit balanced main/supplement placement for technical and governance figures."""
    texts = _manuscript_texts(project_root)
    main_text = "\n".join(
        text for relative, text in texts.items() if not relative.endswith("06_supplement.md")
    )
    supplement_text = texts.get("manuscript/06_supplement.md", "")
    technical_in_main = sorted(path for path in TECHNICAL_QUANTUM_FIGURES if path in main_text)
    technical_missing_from_supplement = sorted(path for path in TECHNICAL_QUANTUM_FIGURES if path not in supplement_text)
    governance_in_main = sorted(path for path in SUPPLEMENTAL_GOVERNANCE_FIGURES if path in main_text)
    governance_missing_from_supplement = sorted(path for path in SUPPLEMENTAL_GOVERNANCE_FIGURES if path not in supplement_text)
    governance_repeated_in_supplement = sorted(
        path for path in SUPPLEMENTAL_GOVERNANCE_FIGURES if supplement_text.count(path) != 1
    )
    compact_in_main = COMPACT_MAIN_QUANTUM_FIGURE in main_text
    compact_in_supplement = COMPACT_MAIN_QUANTUM_FIGURE in supplement_text
    qrf_indices = [main_text.find(path) for path in QRF_LEAD_FIGURES]
    compact_index = main_text.find(COMPACT_MAIN_QUANTUM_FIGURE)
    retired_qrf_absent = RETIRED_QRF_COMPOSITE_FIGURE not in main_text and RETIRED_QRF_COMPOSITE_FIGURE not in supplement_text
    controls = {
        "compact_quantum_summary_in_main": compact_in_main,
        "compact_quantum_summary_not_in_supplement": not compact_in_supplement,
        "technical_quantum_figures_absent_from_main": not technical_in_main,
        "technical_quantum_figures_present_in_supplement": not technical_missing_from_supplement,
        "governance_figures_absent_from_main": not governance_in_main,
        "governance_figures_present_once_in_supplement": not governance_missing_from_supplement
        and not governance_repeated_in_supplement,
        "qrf_lead_figures_present_in_main": all(index >= 0 for index in qrf_indices),
        "qrf_lead_figures_ordered": qrf_indices == sorted(qrf_indices) and len(set(qrf_indices)) == len(qrf_indices),
        "qrf_figures_precede_quantum_summary": all(index >= 0 and compact_index > index for index in qrf_indices),
        "retired_qrf_composite_absent": retired_qrf_absent,
    }
    return {
        "schema": "realizing_emptiness.manuscript_figure_placement_audit.v1",
        "technical_quantum_figure_count": len(TECHNICAL_QUANTUM_FIGURES),
        "technical_quantum_figures": list(TECHNICAL_QUANTUM_FIGURES),
        "technical_quantum_figures_in_main": technical_in_main,
        "technical_quantum_figures_missing_from_supplement": technical_missing_from_supplement,
        "governance_figure_count": len(SUPPLEMENTAL_GOVERNANCE_FIGURES),
        "governance_figures": list(SUPPLEMENTAL_GOVERNANCE_FIGURES),
        "governance_figures_in_main": governance_in_main,
        "governance_figures_missing_from_supplement": governance_missing_from_supplement,
        "governance_figures_repeated_in_supplement": governance_repeated_in_supplement,
        "compact_main_quantum_figure": COMPACT_MAIN_QUANTUM_FIGURE,
        "qrf_lead_figures": list(QRF_LEAD_FIGURES),
        "retired_qrf_composite_figure": RETIRED_QRF_COMPOSITE_FIGURE,
        "controls": controls,
        "ok": all(controls.values()),
        "claim_boundary": "manuscript figure-placement audit only; not empirical, clinical, neural, practice-efficacy, awakening, or physical qFEP evidence",
    }


def build_cover_graphical_abstract_audit(project_root: Path) -> dict[str, Any]:
    """Audit the unnumbered graphical abstract cover image."""
    abstract = (project_root / "manuscript" / "00_abstract.md").read_text(encoding="utf-8")
    preamble = (project_root / "manuscript" / "preamble.md").read_text(encoding="utf-8")
    figure_path = project_root / "output" / "figures" / "graphical_abstract_cover.png"
    figures_yaml = yaml.safe_load((project_root / "figures.yaml").read_text(encoding="utf-8"))
    cover_meta = figures_yaml.get("figures", {}).get("graphical_abstract_cover", {})
    source_map_path = project_root / "output" / "data" / "figure_source_map.json"
    source_ids: set[str] = set()
    if source_map_path.exists():
        source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
        source_ids = {row.get("id", "") for row in source_map.get("figures", [])}
    referenced = "graphical_abstract_cover.png" in abstract
    referenced_in_preamble = (
        "graphical_abstract_cover.png" in preamble
        and r"\AtEndEnvironment{titlepage}" in preamble
        and r"\includegraphics" in preamble
    )
    numbered = "#fig:graphical_abstract_cover" in abstract
    width, height = _png_dimensions(figure_path)
    aspect_ratio = round(width / height, 4) if height else 0.0
    aspect_ratio_ok = 1.15 <= aspect_ratio <= 1.25
    dimensions_ok = width >= 1500 and height >= 1200
    caption_length = len(cover_meta.get("caption", ""))
    alt_text_length = len(cover_meta.get("alt_text", ""))
    return {
        "schema": "realizing_emptiness.cover_graphical_abstract_audit.v1",
        "figure_path": "output/figures/graphical_abstract_cover.png",
        "figure_exists": figure_path.exists(),
        "figure_byte_size": figure_path.stat().st_size if figure_path.exists() else 0,
        "width": width,
        "height": height,
        "aspect_ratio": aspect_ratio,
        "aspect_ratio_ok": aspect_ratio_ok,
        "dimensions_ok": dimensions_ok,
        "referenced_in_abstract": referenced,
        "referenced_in_title_preamble": referenced_in_preamble,
        "numbered_as_figure": numbered,
        "source_mapped": "graphical_abstract_cover" in source_ids,
        "caption_length": caption_length,
        "alt_text_length": alt_text_length,
        "cover_style": "hybrid_symbolic_near_square_large_type",
        "ok": figure_path.exists()
        and figure_path.stat().st_size > 10_000
        and aspect_ratio_ok
        and dimensions_ok
        and referenced
        and referenced_in_preamble
        and not numbered
        and caption_length >= 220
        and alt_text_length >= 140
        and "graphical_abstract_cover" in source_ids,
    }


def write_manuscript_structure_audits(project_root: Path) -> tuple[Path, Path, Path, Path]:
    """Write manuscript reference, figure reuse, figure-placement, and cover graphic audits."""
    data_dir = project_root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    reference_path = data_dir / "manuscript_reference_audit.json"
    reuse_path = data_dir / "figure_reuse_audit.json"
    placement_path = data_dir / "manuscript_figure_placement_audit.json"
    cover_path = data_dir / "cover_graphical_abstract_audit.json"
    reference_path.write_text(
        json.dumps(build_manuscript_reference_audit(project_root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    reuse_path.write_text(
        json.dumps(build_figure_reuse_audit(project_root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    placement_path.write_text(
        json.dumps(build_figure_placement_audit(project_root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    cover_path.write_text(
        json.dumps(build_cover_graphical_abstract_audit(project_root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return reference_path, reuse_path, placement_path, cover_path
