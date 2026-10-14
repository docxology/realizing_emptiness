"""Compose top-level manuscript files from sheaf fragments."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from gates.manuscript import build_manuscript_reference_audit, write_manuscript_structure_audits
from visualizations.rendered_captions import expand_markdown_figure_captions, write_rendered_figure_caption_audit


def _load_manifest(project_root: Path) -> dict:
    with (project_root / "docs" / "manuscript" / "sheaf" / "manifest.yaml").open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_tracks(project_root: Path) -> dict:
    with (project_root / "docs" / "manuscript" / "sheaf" / "tracks.yaml").open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    return payload


def _track_heading(track_payload: dict, section_id: str, track_id: str, fragment_text: str) -> str:
    if section_id == "abstract" or fragment_text.lstrip().startswith("#"):
        return ""
    title = track_payload.get("section_titles", {}).get(section_id, {}).get(track_id)
    if not title:
        title = next(row["label"] for row in track_payload["tracks"] if row["id"] == track_id)
    anchor = track_payload.get("section_anchors", {}).get(section_id, {}).get(track_id, f"sec:{section_id}-{track_id.replace('_', '-')}")
    return f"## {title} {{#{anchor}}}\n"


def _cover_graphical_abstract_block() -> str:
    alt = (
        "Graphical abstract showing Sandved-Smith source formalism flowing through equation registry, "
        "finite QRF boundary screen, stochastic active-inference and quantum engines, claim gates, "
        "evidence ceilings, manuscript, and dashboard outputs."
    )
    return f"""```{{=html}}
<figure class="graphical-abstract"><img src="../output/figures/graphical_abstract_cover.png" alt="{alt}" style="max-width:100%;height:auto;"></figure>
```
"""


def compose(project_root: Path, validate_only: bool = False, strict: bool = False) -> dict:
    manifest = _load_manifest(project_root)
    track_payload = _load_tracks(project_root)
    track_ids = {row["id"] for row in track_payload["tracks"]}
    sections = manifest["sections"]
    coverage_rows = []
    issues = []
    for section in sections:
        output = project_root / "docs" / "manuscript" / section["output"]
        section_dir = project_root / "docs" / "manuscript" / "sections" / section["id"]
        body_parts = [f"# {section['title']} {{#sec:{section['id']}}}\n"]
        lead_path = section_dir / "_lead.md"
        if section["id"] != "abstract" and lead_path.exists():
            body_parts.append(lead_path.read_text(encoding="utf-8").strip() + "\n")
        row = {"section": section["id"], "tracks": {}}
        abstract_fragments = []
        for track in section["tracks"]:
            if track not in track_ids:
                issues.append(f"unknown track {track} in section {section['id']}")
            fragment = section_dir / f"{track}.md"
            exists = fragment.exists()
            row["tracks"][track] = exists
            if exists:
                fragment_text = fragment.read_text(encoding="utf-8").strip()
                if section["id"] == "abstract":
                    abstract_fragments.append(fragment_text)
                else:
                    heading = _track_heading(track_payload, section["id"], track, fragment_text)
                    body_parts.append((heading + fragment_text).strip() + "\n")
            else:
                issues.append(f"missing fragment {fragment.relative_to(project_root)}")
        if section["id"] == "abstract":
            paragraph = " ".join(" ".join(fragment.split()) for fragment in abstract_fragments if fragment.strip())
            body_parts.append(_cover_graphical_abstract_block().strip() + "\n")
            body_parts.append(paragraph.strip() + "\n")
        coverage_rows.append(row)
        body = "\n".join(body_parts).rstrip() + "\n"
        body = expand_markdown_figure_captions(body, project_root)
        body = body.replace("(../output/figures/", "(../../output/figures/")
        body = body.replace('src="../output/figures/', 'src="../../output/figures/')
        if validate_only:
            if not output.exists() or output.read_text(encoding="utf-8") != body:
                issues.append(f"stale composed manuscript {output.relative_to(project_root)}")
        else:
            output.write_text(body, encoding="utf-8")
    data_dir = project_root / "output" / "data"
    coverage = {
        "schema": "realizing_emptiness.sheaf_coverage_matrix.v1",
        "section_count": len(sections),
        "track_count": len(track_ids),
        "rows": coverage_rows,
        "missing_count": len(issues),
        "ok": not issues,
    }
    if not validate_only:
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "sheaf_coverage_matrix.json").write_text(
            json.dumps(coverage, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        write_rendered_figure_caption_audit(project_root)
        write_manuscript_structure_audits(project_root)
    if validate_only:
        reference_audit = build_manuscript_reference_audit(project_root)
        if not reference_audit["ok"]:
            issues.append(f"manuscript references invalid: {reference_audit}")
        coverage["missing_count"] = len(issues)
        coverage["ok"] = not issues
    if strict and issues:
        raise SystemExit("\n".join(issues))
    return coverage
