"""Artifact contract registry for validation and dashboard coverage."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


CLAIM_BOUNDARY = (
    "artifact contract registry for finite software validation; not empirical, clinical, neural, "
    "practice-efficacy, awakening, or physical qFEP evidence"
)


DASHBOARD_GROUPS = {
    "data": "data-artifacts",
    "report": "reports",
    "figure": "figures",
    "web": "dashboard",
}


@dataclass(frozen=True)
class ArtifactContract:
    """Machine-readable contract for a generated or declared artifact."""

    id: str
    path: str
    kind: str
    schema: str | None
    schema_path: str | None
    dashboard_group: str
    manuscript_role: str
    claim_boundary: str

    @property
    def has_schema(self) -> bool:
        return self.schema_path is not None


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _schema_path_for(project_root: Path, schema: str | None) -> str | None:
    if not schema:
        return None
    suffix = schema.removeprefix("realizing_emptiness.")
    suffix = re.sub(r"\.v\d+$", "", suffix)
    candidate = project_root / "schemas" / f"{suffix}.schema.json"
    return str(candidate.relative_to(project_root)) if candidate.exists() else None


def artifact_contracts(project_root: Path) -> list[ArtifactContract]:
    """Build contracts from the manifest instead of a parallel expected-output list."""
    manifest = _load_yaml(project_root / "artifact_manifest.yaml")
    contracts = []
    for artifact in manifest.get("artifacts", []):
        kind = artifact.get("kind", "data")
        path = artifact.get("path", "")
        schema = artifact.get("schema")
        if kind == "figure":
            role = "publication_visual"
        elif kind == "web":
            role = "static_reader_dashboard"
        elif "audit" in artifact.get("id", ""):
            role = "validator_audit"
        else:
            role = "generated_data"
        contracts.append(
            ArtifactContract(
                id=artifact["id"],
                path=path,
                kind=kind,
                schema=schema,
                schema_path=_schema_path_for(project_root, schema),
                dashboard_group=DASHBOARD_GROUPS.get(kind, kind),
                manuscript_role=role,
                claim_boundary=CLAIM_BOUNDARY,
            )
        )
    return contracts


def build_artifact_contract_registry(project_root: Path) -> dict[str, Any]:
    """Build a registry artifact for generated-output validation."""
    contracts = artifact_contracts(project_root)
    rows = [asdict(contract) | {"path_exists": (project_root / contract.path).exists()} for contract in contracts]
    duplicate_ids = sorted(contract_id for contract_id in {row["id"] for row in rows} if [row["id"] for row in rows].count(contract_id) > 1)
    missing_schema_paths = sorted(row["id"] for row in rows if row["schema"] and not row["schema_path"])
    figure_contracts = [row for row in rows if row["kind"] == "figure"]
    # Fail-closed: every generated JSON data/report artifact MUST declare a resolvable schema.
    # CSV side-cars legitimately carry no schema, so the rule is scoped to .json paths.
    schemaless_json_artifacts = sorted(
        row["id"]
        for row in rows
        if row["kind"] in {"data", "report"}
        and row["path"].endswith(".json")
        and (not row["schema"] or not row["schema_path"])
    )
    controls = {
        "ids_unique": not duplicate_ids,
        "schema_paths_resolve": not missing_schema_paths,
        "all_json_data_artifacts_have_schema": not schemaless_json_artifacts,
        "figures_have_dashboard_group": all(row["dashboard_group"] == "figures" for row in figure_contracts),
        "all_rows_have_claim_boundary": all("not empirical" in row["claim_boundary"] for row in rows),
    }
    return {
        "schema": "realizing_emptiness.artifact_contract_registry.v1",
        "contract_count": len(rows),
        "rows": rows,
        "duplicate_ids": duplicate_ids,
        "missing_schema_paths": missing_schema_paths,
        "schemaless_json_artifacts": schemaless_json_artifacts,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_artifact_contract_registry(project_root: Path) -> Path:
    """Write the contract registry artifact."""
    path = project_root / "output" / "data" / "artifact_contract_registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(build_artifact_contract_registry(project_root), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
