#!/usr/bin/env python3
"""Compose top-level manuscript files from sheaf fragments."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from _bootstrap import PROJECT_ROOT
from gates.manuscript import write_manuscript_structure_audits
from visualizations.rendered_captions import expand_markdown_figure_captions, write_rendered_figure_caption_audit


def _load_manifest() -> dict:
    with (PROJECT_ROOT / "manuscript" / "sheaf" / "manifest.yaml").open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_tracks() -> dict:
    with (PROJECT_ROOT / "manuscript" / "sheaf" / "tracks.yaml").open("r", encoding="utf-8") as handle:
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


def compose(validate_only: bool = False, strict: bool = False) -> dict:
    manifest = _load_manifest()
    track_payload = _load_tracks()
    track_ids = {row["id"] for row in track_payload["tracks"]}
    sections = manifest["sections"]
    coverage_rows = []
    issues = []
    for section in sections:
        output = PROJECT_ROOT / "manuscript" / section["output"]
        section_dir = PROJECT_ROOT / "manuscript" / "sections" / section["id"]
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
                issues.append(f"missing fragment {fragment.relative_to(PROJECT_ROOT)}")
        if section["id"] == "abstract":
            paragraph = " ".join(" ".join(fragment.split()) for fragment in abstract_fragments if fragment.strip())
            body_parts.append(_cover_graphical_abstract_block().strip() + "\n")
            body_parts.append(paragraph.strip() + "\n")
        coverage_rows.append(row)
        if not validate_only:
            body = "\n".join(body_parts).rstrip() + "\n"
            output.write_text(expand_markdown_figure_captions(body, PROJECT_ROOT), encoding="utf-8")
    data_dir = PROJECT_ROOT / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    coverage = {
        "schema": "realizing_emptiness.sheaf_coverage_matrix.v1",
        "section_count": len(sections),
        "track_count": len(track_ids),
        "rows": coverage_rows,
        "missing_count": len(issues),
        "ok": not issues,
    }
    (data_dir / "sheaf_coverage_matrix.json").write_text(
        json.dumps(coverage, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if not validate_only:
        write_rendered_figure_caption_audit(PROJECT_ROOT)
        write_manuscript_structure_audits(PROJECT_ROOT)
    if strict and issues:
        raise SystemExit("\n".join(issues))
    return coverage


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    compose(validate_only=args.validate_only, strict=args.strict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
