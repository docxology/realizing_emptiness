from __future__ import annotations

from pathlib import Path
from typing import Any

from formalism.review_response_common import CLAIM_BOUNDARY, collect_numeric_results, load_json, load_yaml


def source_artifact_metadata(project_root: Path, relative: str) -> dict[str, Any]:
    path = project_root / relative
    if not path.exists():
        return {
            "source_artifact": relative,
            "exists": False,
            "parameter_fields": [],
            "result_counts": {},
            "control_fields": [],
        }
    if path.suffix.lower() in {".yaml", ".yml"}:
        payload = load_yaml(path)
        figures = payload.get("figures", {}) if isinstance(payload, dict) else {}
        palette = payload.get("palette", {}) if isinstance(payload, dict) else {}
        return {
            "source_artifact": relative,
            "exists": True,
            "parameter_fields": sorted(key for key in ("dpi", "font_scale", "palette") if key in payload),
            "result_counts": {"figure_config_count": len(figures), "palette_role_count": len(palette)},
            "control_fields": ["figure_caption_metadata", "visual_encoding_metadata", "alt_text_metadata"],
        }
    if path.suffix.lower() != ".json":
        return {
            "source_artifact": relative,
            "exists": True,
            "parameter_fields": [],
            "result_counts": {"file_bytes": path.stat().st_size},
            "control_fields": [],
        }
    payload = load_json(path)
    parameter_fields = sorted(
        key
        for key, value in payload.items()
        if key.endswith("_grid") or "seed" in key or key in {"runs_per_profile", "trajectory_count"}
        if isinstance(value, (list, int, float, str))
    )
    result_counts = collect_numeric_results(payload)
    top_level_controls = [
        key
        for key, value in payload.items()
        if isinstance(value, bool) and key in {"ok", "all_controls_pass", "negative_control_fails", "high_access_prunes"}
    ]
    control_fields = sorted([*payload.get("controls", {}).keys(), *top_level_controls])
    return {
        "source_artifact": relative,
        "exists": True,
        "parameter_fields": parameter_fields,
        "result_counts": result_counts,
        "control_fields": control_fields,
    }


def build_figure_parameter_ledger(project_root: Path) -> dict[str, Any]:
    figure_map = load_json(project_root / "output" / "data" / "figure_source_map.json")
    rows = []
    for figure in figure_map.get("figures", []):
        source_artifacts = list(figure.get("source_artifacts", []))
        source_metadata = [source_artifact_metadata(project_root, relative) for relative in source_artifacts]
        parameter_fields = sorted(
            {
                f"{metadata['source_artifact']}::{field}"
                for metadata in source_metadata
                for field in metadata.get("parameter_fields", [])
            }
        )
        control_fields = sorted(
            {
                f"{metadata['source_artifact']}::{field}"
                for metadata in source_metadata
                for field in metadata.get("control_fields", [])
            }
        )
        result_counts = {
            metadata["source_artifact"]: metadata.get("result_counts", {})
            for metadata in source_metadata
            if metadata.get("result_counts")
        }
        rows.append(
            {
                "figure_id": figure.get("id", ""),
                "path": figure.get("path", ""),
                "source_artifacts": source_artifacts,
                "source_artifact_count": len(source_artifacts),
                "parameter_fields": parameter_fields,
                "result_counts": result_counts,
                "control_fields": control_fields,
                "source_metadata": source_metadata,
                "traceable": bool(source_artifacts) and all(metadata.get("exists") for metadata in source_metadata),
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    missing_rows = sorted(
        figure.get("id", "")
        for figure in figure_map.get("figures", [])
        if figure.get("id", "") not in {row["figure_id"] for row in rows}
    )
    rows_without_sources = sorted(row["figure_id"] for row in rows if not row["source_artifacts"])
    missing_source_artifacts = [
        {"figure_id": row["figure_id"], "source_artifact": metadata["source_artifact"]}
        for row in rows
        for metadata in row["source_metadata"]
        if not metadata.get("exists")
    ]
    missing_source_artifacts = sorted(missing_source_artifacts, key=lambda item: (item["figure_id"], item["source_artifact"]))
    controls = {
        "one_row_per_manifest_figure": len(rows) == figure_map.get("figure_count", 0) and not missing_rows,
        "all_rows_have_source_artifacts": not rows_without_sources,
        "all_source_artifacts_exist": not missing_source_artifacts,
        "all_rows_have_claim_boundary": all("not empirical" in row["claim_boundary"] for row in rows),
        "parameters_or_controls_present_where_available": all(
            row["parameter_fields"] or row["control_fields"] or row["result_counts"] for row in rows
        ),
    }
    return {
        "schema": "realizing_emptiness.figure_parameter_ledger.v1",
        "figure_count": figure_map.get("figure_count", 0),
        "row_count": len(rows),
        "rows": rows,
        "missing_rows": missing_rows,
        "rows_without_sources": rows_without_sources,
        "missing_source_artifacts": missing_source_artifacts,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
