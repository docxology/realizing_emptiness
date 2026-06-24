"""Figure integrity hashing and nonblank-image checks."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib.image as mpimg
import numpy as np


MIN_WIDTH = 200
MIN_HEIGHT = 150
MIN_VARIANCE = 1e-10


def file_sha256(path: Path) -> str:
    """Return the SHA-256 digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _image_metrics(path: Path) -> dict[str, Any]:
    image = np.asarray(mpimg.imread(path), dtype=float)
    if image.ndim == 2:
        height, width = image.shape
        channels = 1
    else:
        height, width, channels = image.shape
    finite_image = image[np.isfinite(image)]
    variance = float(np.var(finite_image)) if finite_image.size else 0.0
    return {
        "width": int(width),
        "height": int(height),
        "channels": int(channels),
        "pixel_variance": variance,
        "nonblank": variance > MIN_VARIANCE,
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_figure_integrity_audit(project_root: Path, source_map: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build current hashes, dimensions, and source hashes for source-mapped figures."""
    source_map_path = project_root / "output" / "data" / "figure_source_map.json"
    source_map = source_map or _load_json(source_map_path)
    rows = []
    for figure in source_map.get("figures", []):
        figure_path = project_root / figure["path"]
        source_rows = []
        for source in figure.get("source_artifacts", []):
            source_path = project_root / source
            source_rows.append(
                {
                    "path": source,
                    "exists": source_path.exists(),
                    "sha256": file_sha256(source_path) if source_path.exists() else "",
                    "byte_size": source_path.stat().st_size if source_path.exists() else 0,
                }
            )
        metrics = _image_metrics(figure_path) if figure_path.exists() else {}
        rows.append(
            {
                "id": figure["id"],
                "path": figure["path"],
                "exists": figure_path.exists(),
                "sha256": file_sha256(figure_path) if figure_path.exists() else "",
                "byte_size": figure_path.stat().st_size if figure_path.exists() else 0,
                "caption": figure.get("caption", ""),
                "source_artifacts": source_rows,
                **metrics,
            }
        )

    missing_figures = sorted(row["id"] for row in rows if not row["exists"])
    blank_figures = sorted(row["id"] for row in rows if not row.get("nonblank", False))
    undersized_figures = sorted(
        row["id"] for row in rows if row.get("width", 0) < MIN_WIDTH or row.get("height", 0) < MIN_HEIGHT
    )
    missing_sources = sorted(
        [
            {"figure_id": row["id"], "source": source["path"]}
            for row in rows
            for source in row["source_artifacts"]
            if not source["exists"]
        ],
        key=lambda item: (item["figure_id"], item["source"]),
    )
    ok = (
        source_map.get("figure_count") == len(rows)
        and not missing_figures
        and not blank_figures
        and not undersized_figures
        and not missing_sources
    )
    return {
        "schema": "realizing_emptiness.figure_integrity_audit.v1",
        "source_map_path": "output/data/figure_source_map.json",
        "source_map_sha256": file_sha256(source_map_path) if source_map_path.exists() else "",
        "figure_count": len(rows),
        "source_map_figure_count": source_map.get("figure_count"),
        "rows": rows,
        "missing_figures": missing_figures,
        "blank_figures": blank_figures,
        "undersized_figures": undersized_figures,
        "missing_sources": missing_sources,
        "all_figures_nonblank": not blank_figures,
        "all_sources_hashed": not missing_sources,
        "ok": ok,
    }


def write_figure_integrity_audit(project_root: Path, source_map: dict[str, Any] | None = None) -> Path:
    """Write figure integrity audit JSON."""
    payload = build_figure_integrity_audit(project_root, source_map)
    path = project_root / "output" / "data" / "figure_integrity_audit.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def compare_figure_integrity(project_root: Path, saved_audit: dict[str, Any] | None = None) -> dict[str, Any]:
    """Compare saved figure integrity metadata against current files."""
    audit_path = project_root / "output" / "data" / "figure_integrity_audit.json"
    saved = saved_audit or _load_json(audit_path)
    current = build_figure_integrity_audit(project_root)
    saved_rows = {row["id"]: row for row in saved.get("rows", [])}
    current_rows = {row["id"]: row for row in current.get("rows", [])}
    missing_saved_rows = sorted(set(current_rows) - set(saved_rows))
    stale_saved_rows = sorted(set(saved_rows) - set(current_rows))
    figure_hash_mismatches = sorted(
        figure_id
        for figure_id in current_rows.keys() & saved_rows.keys()
        if current_rows[figure_id].get("sha256") != saved_rows[figure_id].get("sha256")
    )
    dimension_mismatches = sorted(
        figure_id
        for figure_id in current_rows.keys() & saved_rows.keys()
        if (
            current_rows[figure_id].get("width"),
            current_rows[figure_id].get("height"),
            current_rows[figure_id].get("channels"),
        )
        != (
            saved_rows[figure_id].get("width"),
            saved_rows[figure_id].get("height"),
            saved_rows[figure_id].get("channels"),
        )
    )

    source_hash_mismatches = []
    for figure_id in current_rows.keys() & saved_rows.keys():
        current_sources = {row["path"]: row.get("sha256") for row in current_rows[figure_id].get("source_artifacts", [])}
        saved_sources = {row["path"]: row.get("sha256") for row in saved_rows[figure_id].get("source_artifacts", [])}
        for source in sorted(set(current_sources) | set(saved_sources)):
            if current_sources.get(source) != saved_sources.get(source):
                source_hash_mismatches.append({"figure_id": figure_id, "source": source})

    ok = (
        saved.get("ok") is True
        and current.get("ok") is True
        and saved.get("figure_count") == current.get("figure_count")
        and not missing_saved_rows
        and not stale_saved_rows
        and not figure_hash_mismatches
        and not dimension_mismatches
        and not source_hash_mismatches
    )
    return {
        "schema": "realizing_emptiness.figure_integrity_comparison.v1",
        "ok": ok,
        "saved_ok": saved.get("ok") is True,
        "current_ok": current.get("ok") is True,
        "missing_saved_rows": missing_saved_rows,
        "stale_saved_rows": stale_saved_rows,
        "figure_hash_mismatches": figure_hash_mismatches,
        "dimension_mismatches": dimension_mismatches,
        "source_hash_mismatches": source_hash_mismatches,
        "current_blank_figures": current.get("blank_figures", []),
        "current_undersized_figures": current.get("undersized_figures", []),
        "current_missing_sources": current.get("missing_sources", []),
    }
