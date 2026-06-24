"""Caption and visual-encoding audit for generated figures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BOUNDARY_TERMS = (
    "not evidence",
    "not empirical",
    "surrogate",
    "proxy",
    "source",
    "claim",
    "boundary",
    "finite",
)

ENCODING_TERMS = (
    "legend",
    "color",
    "colorbar",
    "panel",
    "line",
    "bar",
    "matrix",
    "node",
    "edge",
    "heatmap",
)

NON_COLOR_TERMS = (
    "axis",
    "axes",
    "bar",
    "cell",
    "columns",
    "contour",
    "dashed",
    "edge",
    "line",
    "marker",
    "matrix",
    "node",
    "panel",
    "rows",
    "text",
)

UNIT_TERMS = (
    "bits",
    "channel",
    "chsh",
    "citation",
    "claim",
    "delta",
    "entropy",
    "equation",
    "free energy",
    "gate",
    "kbt",
    "mass",
    "method",
    "probability",
    "profile",
    "rate",
    "sector",
    "source",
    "state",
    "status",
    "step",
    "support",
    "time",
    "value",
)


def build_visual_caption_audit(source_map: dict[str, Any]) -> dict[str, Any]:
    """Audit figure captions and visual-encoding descriptions."""
    rows = []
    for figure in source_map.get("figures", []):
        caption = figure.get("caption", "")
        encoding = figure.get("visual_encoding", "")
        caption_lower = caption.lower()
        encoding_lower = encoding.lower()
        row = {
            "id": figure.get("id"),
            "caption_length": len(caption),
            "source_artifact_count": len(figure.get("source_artifacts", [])),
            "has_source_artifact": bool(figure.get("source_artifacts")),
            "has_interpretive_boundary": any(term in caption_lower for term in BOUNDARY_TERMS),
            "has_visual_encoding": bool(encoding) and any(term in encoding_lower for term in ENCODING_TERMS),
            "visual_encoding": encoding,
            "ok": bool(figure.get("source_artifacts"))
            and len(caption) >= 120
            and any(term in caption_lower for term in BOUNDARY_TERMS)
            and bool(encoding)
            and any(term in encoding_lower for term in ENCODING_TERMS),
        }
        rows.append(row)
    return {
        "schema": "realizing_emptiness.visual_caption_audit.v1",
        "figure_count": source_map.get("figure_count", len(rows)),
        "row_count": len(rows),
        "rows": rows,
        "missing_or_weak_captions": [row["id"] for row in rows if row["caption_length"] < 120],
        "missing_source_artifacts": [row["id"] for row in rows if not row["has_source_artifact"]],
        "missing_interpretive_boundaries": [row["id"] for row in rows if not row["has_interpretive_boundary"]],
        "missing_visual_encodings": [row["id"] for row in rows if not row["has_visual_encoding"]],
        "ok": all(row["ok"] for row in rows) and source_map.get("figure_count") == len(rows),
    }


def write_visual_caption_audit(project_root: Path, source_map: dict[str, Any]) -> Path:
    """Write visual-caption audit JSON."""
    payload = build_visual_caption_audit(source_map)
    path = project_root / "output" / "data" / "visual_caption_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def build_visual_accessibility_audit(source_map: dict[str, Any]) -> dict[str, Any]:
    """Audit accessibility metadata for source-mapped figures."""
    rows = []
    for figure in source_map.get("figures", []):
        alt_text = figure.get("alt_text", "")
        encoding = figure.get("visual_encoding", "")
        caption = figure.get("caption", "")
        render_contract = figure.get("render_contract", {})
        legend_count = render_contract.get("legend_count", 0)
        colorbar_count = render_contract.get("colorbar_count", 0)
        combined = f"{encoding} {caption} {alt_text}".lower()
        row = {
            "id": figure.get("id"),
            "alt_text_length": len(alt_text),
            "has_alt_text": len(alt_text) >= 80,
            "has_data_table_alternative": bool(figure.get("source_artifacts")),
            "has_non_color_encoding": any(term in combined for term in NON_COLOR_TERMS),
            "has_units_or_axes": any(term in combined for term in UNIT_TERMS),
            "has_legend_or_colorbar": legend_count + colorbar_count >= 1,
            "ok": len(alt_text) >= 80
            and bool(figure.get("source_artifacts"))
            and any(term in combined for term in NON_COLOR_TERMS)
            and any(term in combined for term in UNIT_TERMS)
            and legend_count + colorbar_count >= 1,
        }
        rows.append(row)
    return {
        "schema": "realizing_emptiness.visual_accessibility_audit.v1",
        "figure_count": source_map.get("figure_count", len(rows)),
        "row_count": len(rows),
        "rows": rows,
        "missing_alt_text": [row["id"] for row in rows if not row["has_alt_text"]],
        "missing_data_table_alternative": [row["id"] for row in rows if not row["has_data_table_alternative"]],
        "missing_non_color_encoding": [row["id"] for row in rows if not row["has_non_color_encoding"]],
        "missing_units_or_axes": [row["id"] for row in rows if not row["has_units_or_axes"]],
        "missing_legend_or_colorbar": [row["id"] for row in rows if not row["has_legend_or_colorbar"]],
        "ok": all(row["ok"] for row in rows) and source_map.get("figure_count") == len(rows),
    }


def write_visual_accessibility_audit(project_root: Path, source_map: dict[str, Any]) -> Path:
    """Write visual-accessibility audit JSON."""
    payload = build_visual_accessibility_audit(source_map)
    path = project_root / "output" / "data" / "visual_accessibility_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
