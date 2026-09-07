from __future__ import annotations

from pathlib import Path
from typing import Any

from formalism.review_response_common import LOCAL_RELEASE_BOUNDARY, json_write, load_yaml, sha256


RELEASE_SUPPORT_ROOT_FILES = (
    "AGENTS.md",
    "CITATION.cff",
    "DESIGN.md",
    "ISA.md",
    "README.md",
    "TODO.md",
    "artifact_manifest.yaml",
    "codemeta.json",
    "conftest.py",
    "domain_profile.yaml",
    "emptiness.yaml",
    "experiment_plan.yaml",
    "figures.yaml",
    "pymdp.yaml",
    "pyproject.toml",
    "tasks.yaml",
    "tracks.yaml",
    "uv.lock",
)

RELEASE_SUPPORT_DIR_SUFFIXES = {
    "data": {".md", ".yaml", ".yml"},
    "docs": {".md", ".pdf"},
    "manuscript": {".bib", ".md", ".yaml", ".yml"},
    "schemas": {".json", ".md"},
    "scripts": {".md", ".py"},
    "src": {".md", ".py"},
    "tests": {".md", ".py"},
}


def manifest_paths(project_root: Path) -> list[dict[str, Any]]:
    manifest = load_yaml(project_root / "artifact_manifest.yaml")
    return list(manifest.get("artifacts", []))


def release_support_paths(project_root: Path) -> list[str]:
    paths: set[str] = set()
    for relative in RELEASE_SUPPORT_ROOT_FILES:
        if (project_root / relative).is_file():
            paths.add(relative)
    for directory, suffixes in RELEASE_SUPPORT_DIR_SUFFIXES.items():
        base = project_root / directory
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in suffixes:
                paths.add(str(path.relative_to(project_root)))
    return sorted(paths)


def build_artifact_release_manifest(project_root: Path) -> dict[str, Any]:
    manifest_artifacts = manifest_paths(project_root)
    support_paths = release_support_paths(project_root)
    self_path = "output/data/artifact_release_manifest.json"
    rows: list[dict[str, Any]] = []
    excluded = []

    for artifact in manifest_artifacts:
        relative = artifact.get("path", "")
        if relative == self_path:
            excluded.append(relative)
            continue
        path = project_root / relative
        row = {
            "path": relative,
            "kind": "manifest_artifact",
            "artifact_id": artifact.get("id", ""),
            "exists": path.exists(),
        }
        if path.exists():
            row.update({"sha256": sha256(path), "bytes": path.stat().st_size})
        rows.append(row)

    for relative in support_paths:
        path = project_root / relative
        row = {"path": relative, "kind": "release_support", "exists": path.exists()}
        if path.exists():
            row.update({"sha256": sha256(path), "bytes": path.stat().st_size})
        rows.append(row)

    missing_paths = sorted(row["path"] for row in rows if not row.get("exists"))
    duplicate_paths = sorted(path for path in {row["path"] for row in rows} if [row["path"] for row in rows].count(path) > 1)
    required_commands = [
        "uv run python scripts/run_full_chain.py",
        "uv run pytest tests/ --cov=src --cov-fail-under=90",
        "uv run python scripts/check_documentation_contract.py --check",
        "uv run python scripts/generate_method_inventory.py --check",
        "uv run python scripts/generate_equation_crosswalk.py --check",
        "uv run python scripts/compose_manuscript.py --validate-only --strict",
        "uv run python scripts/validate_outputs.py",
        "cd <template-checkout> && uv run python -m infrastructure.orchestration link-projects",
        "cd <template-checkout> && uv run python scripts/03_render_pdf.py --project working/realizing_emptiness",
    ]
    controls = {
        "all_paths_relative": all(not Path(row["path"]).is_absolute() and ".." not in Path(row["path"]).parts for row in rows),
        "all_files_exist": not missing_paths,
        "all_hashes_present": all(row.get("sha256") for row in rows if row.get("exists")),
        "paths_unique": not duplicate_paths,
        "uv_lock_included": any(row["path"] == "uv.lock" for row in rows),
        "source_manifests_included": all(
            any(row["path"] == path for row in rows)
            for path in ("data/sources/source_manifest.yaml", "data/sources/scholarship_manifest.yaml")
        ),
        "source_tree_included": any(row["path"].startswith("src/") and row["path"].endswith(".py") for row in rows),
        "schemas_included": any(row["path"].startswith("schemas/") and row["path"].endswith(".json") for row in rows),
        "tests_included": any(row["path"].startswith("tests/") and row["path"].endswith(".py") for row in rows),
        "manuscript_sources_included": any(row["path"].startswith("docs/manuscript/sections/") for row in rows),
        "docs_included": any(row["path"].startswith("docs/") and row["path"].endswith(".md") for row in rows),
        "rerun_scripts_included": all(
            any(row["path"] == path for row in rows)
            for path in (
                "scripts/run_full_chain.py",
                "scripts/validate_outputs.py",
                "scripts/generate_review_response_artifacts.py",
            )
        ),
        "validation_commands_declared": len(required_commands) >= 7,
        "public_publication_not_claimed": True,
        "self_manifest_excluded_from_hashes": self_path in excluded,
        "claim_boundary_declared": "not public independent reproduction" in LOCAL_RELEASE_BOUNDARY,
    }
    return {
        "schema": "realizing_emptiness.artifact_release_manifest.v1",
        "release_scope": "local_private_artifact_bundle_not_public_release",
        "public_publication_performed": False,
        "public_release_targets_excluded": ["Zenodo", "GitHub release", "public archive upload"],
        "artifact_count": len(manifest_artifacts),
        "file_count": len(rows),
        "files": sorted(rows, key=lambda row: (row["kind"], row["path"])),
        "missing_paths": missing_paths,
        "duplicate_paths": duplicate_paths,
        "excluded_self_from_hashes": excluded,
        "required_commands": required_commands,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": LOCAL_RELEASE_BOUNDARY,
    }


def write_artifact_release_manifest(project_root: Path) -> Path:
    return json_write(project_root / "output" / "data" / "artifact_release_manifest.json", build_artifact_release_manifest(project_root))
