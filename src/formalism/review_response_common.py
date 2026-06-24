from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


CLAIM_BOUNDARY = (
    "review-response accounting for finite deterministic or seeded software validation only; "
    "not empirical, not public independent reproduction, not clinical, not neural, "
    "not practice-efficacy, not contemplative-attainment, and not physical qFEP evidence"
)

LOCAL_RELEASE_BOUNDARY = (
    "local private artifact package only, not public independent reproduction; "
    "not empirical, clinical, neural, practice-efficacy, contemplative-attainment, "
    "or physical qFEP evidence"
)

NEUTRAL_ALIAS_MAP = {
    "self": "sector_s",
    "env": "sector_e",
    "environment": "sector_e",
    "body": "sector_b",
    "action": "sector_a",
    "world": "sector_w",
    "other": "sector_o",
    "care": "sector_c",
}


def load_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else default or {}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def round_float(value: float, digits: int = 12) -> float:
    return round(float(value), digits)


def json_write(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def collect_numeric_results(payload: dict[str, Any], prefix: str = "") -> dict[str, int | float]:
    rows: dict[str, int | float] = {}
    for key, value in payload.items():
        label = f"{prefix}.{key}" if prefix else key
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            if key.endswith("_count") or key in {
                "row_count",
                "profile_count",
                "trajectory_count",
                "case_count",
                "source_count",
                "claim_count",
                "branching_ratio",
                "criticality_index",
                "near_critical_score",
                "switch_rate",
                "variance",
                "entropy_nats",
            }:
                rows[label] = value
        elif isinstance(value, dict):
            rows.update(collect_numeric_results(value, label))
    return rows
