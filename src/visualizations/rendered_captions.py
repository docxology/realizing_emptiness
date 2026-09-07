"""Reader-facing manuscript figure-caption synchronization and audit."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

from visualizations.captions import BOUNDARY_TERMS, ENCODING_TERMS


FIGURE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)(\{[^}]*\})?")


def _figure_lookup(project_root: Path) -> dict[str, dict[str, str]]:
    payload = yaml.safe_load((project_root / "figures.yaml").read_text(encoding="utf-8"))
    lookup = {}
    for figure_id, figure in payload.get("figures", {}).items():
        lookup[figure.get("filename", "")] = {
            "id": figure_id,
            "caption": figure.get("caption", ""),
            "visual_encoding": figure.get("visual_encoding", ""),
        }
    return lookup


def expand_markdown_figure_captions(text: str, project_root: Path) -> str:
    """Replace short Markdown figure captions with source-of-truth captions."""
    lookup = _figure_lookup(project_root)

    def replace(match: re.Match[str]) -> str:
        path = match.group(2)
        attrs = match.group(3) or ""
        figure = lookup.get(Path(path).name)
        if figure is None:
            return match.group(0)
        return f"![{figure['caption']}]({path}){attrs}"

    return FIGURE_RE.sub(replace, text)


def _source_map_by_filename(project_root: Path) -> dict[str, dict[str, Any]]:
    path = project_root / "output" / "data" / "figure_source_map.json"
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {Path(row.get("path", "")).name: row for row in payload.get("figures", [])}


def build_rendered_figure_caption_audit_from_texts(
    texts: dict[str, str],
    project_root: Path,
) -> dict[str, Any]:
    """Audit the captions that will appear in composed manuscript Markdown."""
    source_map = _source_map_by_filename(project_root)
    rows = []
    for manuscript_name, text in texts.items():
        for match in FIGURE_RE.finditer(text):
            caption = match.group(1).strip()
            figure_path = match.group(2)
            filename = Path(figure_path).name
            source_row = source_map.get(filename, {})
            caption_lower = caption.lower()
            visual_encoding = source_row.get("visual_encoding", "")
            row = {
                "manuscript": manuscript_name,
                "figure_id": source_row.get("id", Path(filename).stem),
                "figure_path": figure_path,
                "caption_length": len(caption),
                "source_artifact_count": len(source_row.get("source_artifacts", [])),
                "has_source_artifact": bool(source_row.get("source_artifacts")),
                "has_interpretive_boundary": any(term in caption_lower for term in BOUNDARY_TERMS),
                "has_visual_encoding_language": any(term in caption_lower for term in ENCODING_TERMS),
                "source_map_caption_length": len(source_row.get("caption", "")),
                "visual_encoding": visual_encoding,
            }
            row["ok"] = (
                row["caption_length"] >= 120
                and row["has_source_artifact"]
                and row["has_interpretive_boundary"]
                and row["has_visual_encoding_language"]
            )
            rows.append(row)
    return {
        "schema": "realizing_emptiness.rendered_figure_caption_audit.v1",
        "manuscript_count": len(texts),
        "figure_reference_count": len(rows),
        "unique_figure_count": len({row["figure_id"] for row in rows}),
        "rows": rows,
        "missing_or_weak_captions": [
            f"{row['manuscript']}::{row['figure_id']}"
            for row in rows
            if row["caption_length"] < 120
        ],
        "missing_source_artifacts": [
            f"{row['manuscript']}::{row['figure_id']}"
            for row in rows
            if not row["has_source_artifact"]
        ],
        "missing_interpretive_boundaries": [
            f"{row['manuscript']}::{row['figure_id']}"
            for row in rows
            if not row["has_interpretive_boundary"]
        ],
        "missing_visual_encoding_language": [
            f"{row['manuscript']}::{row['figure_id']}"
            for row in rows
            if not row["has_visual_encoding_language"]
        ],
        "ok": bool(rows) and all(row["ok"] for row in rows),
    }


def build_rendered_figure_caption_audit(project_root: Path) -> dict[str, Any]:
    """Build an audit over composed manuscript figure captions."""
    manuscript_dir = project_root / "docs" / "manuscript"
    texts = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(manuscript_dir.glob("*.md"))
        if path.name[:2].isdigit()
    }
    return build_rendered_figure_caption_audit_from_texts(texts, project_root)


def write_rendered_figure_caption_audit(project_root: Path) -> Path:
    """Write rendered-caption audit JSON."""
    payload = build_rendered_figure_caption_audit(project_root)
    path = project_root / "output" / "data" / "rendered_figure_caption_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
