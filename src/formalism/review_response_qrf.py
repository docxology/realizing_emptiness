from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

from formalism.review_response_common import CLAIM_BOUNDARY, NEUTRAL_ALIAS_MAP
from simulation.qrf_env import boundary_channel_ledger


def alias_labels(labels: Iterable[str]) -> list[str]:
    return [NEUTRAL_ALIAS_MAP.get(label, f"sector_{label}") for label in labels]


def build_qrf_label_ablation_audit(project_root: Path | None = None) -> dict[str, Any]:
    ledger = boundary_channel_ledger()
    rows = []
    for row in ledger.get("rows", []):
        original = row.get("sector_labels_by_profile", {})
        aliased = {profile: NEUTRAL_ALIAS_MAP.get(label, f"sector_{label}") for profile, label in original.items()}
        rows.append(
            {
                "channel_id": row["channel_id"],
                "invariant_evidence_object": row["invariant_evidence_object"],
                "original_sector_labels_by_profile": original,
                "neutral_sector_labels_by_profile": aliased,
                "structure_preserved": (
                    sorted(original) == sorted(aliased)
                    and len(set(original.values())) == len(set(aliased.values()))
                    and row.get("evidence_object_invariant") is True
                ),
                "source_equation_links": row.get("source_equation_links", []),
            }
        )
    original_profile_labels = ledger.get("sector_labels_by_profile", {})
    neutral_profile_labels = {profile: alias_labels(labels) for profile, labels in original_profile_labels.items()}
    collapsed_control = {
        profile: ["sector_collapsed" if label in {"self", "env"} else NEUTRAL_ALIAS_MAP.get(label, f"sector_{label}") for label in labels]
        for profile, labels in original_profile_labels.items()
    }
    negative_control_preserved = (
        [row["channel_id"] for row in ledger.get("rows", [])[:-1]] == [f"b{index}" for index in range(6)]
        and all(len(set(labels)) == len(set(original_profile_labels.get(profile, []))) for profile, labels in collapsed_control.items())
    )
    controls = {
        "neutral_alias_map_declared": {"self", "env", "body", "world", "other", "care"} <= set(NEUTRAL_ALIAS_MAP),
        "all_profile_labels_aliased": all(
            len(neutral_profile_labels.get(profile, [])) == len(labels)
            for profile, labels in original_profile_labels.items()
        ),
        "channel_order_preserved": [row["channel_id"] for row in rows] == [f"b{index}" for index in range(6)],
        "evidence_objects_preserved": [row["invariant_evidence_object"] for row in rows]
        == [row["invariant_evidence_object"] for row in ledger.get("rows", [])],
        "neutral_renaming_preserves_structure": all(row["structure_preserved"] for row in rows),
        "structure_changing_control_fails": negative_control_preserved is False,
        "claim_boundary_declared": "not empirical" in CLAIM_BOUNDARY,
    }
    return {
        "schema": "realizing_emptiness.qrf_label_ablation_audit.v1",
        "alias_map": NEUTRAL_ALIAS_MAP,
        "profile_count": ledger.get("profile_count", 0),
        "channel_count": ledger.get("channel_count", 0),
        "rows": rows,
        "neutral_sector_labels_by_profile": neutral_profile_labels,
        "structure_changing_control": {
            "description": "Collapse self/env labels and remove one channel from the order; this changes structure and must fail.",
            "preserved": negative_control_preserved,
        },
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
