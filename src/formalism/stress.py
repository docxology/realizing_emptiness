"""Evidence-ceiling stress audits for public claim boundaries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from formalism.scholarship import CLAIM_KINDS, build_claim_support_audit


ALLOWED_STRESSORS = {
    "empirical_gap": "Requires empirical data before empirical claims are permitted.",
    "neural_measurement_boundary": "Prevents toy criticality proxies from becoming neural-measurement claims.",
    "normative_boundary": "Prevents model-scope quantities from becoming moral or compassion claims.",
    "practice_boundary": "Prevents protocol mappings from becoming practice efficacy claims.",
    "quantum_gap": "Prevents finite surrogates from becoming direct quantum-dynamics simulations.",
    "runtime_dependency": "Requires pinned runtime diagnostics before software claims are trusted.",
    "source_role_boundary": "Keeps background or terminology sources from supporting stronger claims.",
    "surrogate_scope": "Keeps finite toy calculations inside their operational-surrogate scope.",
}


REQUIRED_BOUNDARY_FIELDS = ("evidence_ceiling", "prohibited_inference", "future_evidence_required")


def build_evidence_ceiling_audit(project_root: Path, crosswalk: dict[str, Any]) -> dict[str, Any]:
    """Audit that every public claim declares limits, stressors, and future evidence."""
    claim_support = build_claim_support_audit(project_root, crosswalk)
    claim_to_sources = claim_support.get("claim_to_sources", {})
    rows = []
    missing_boundary_fields = []
    invalid_stressors = []
    status_mismatches = []
    claims_without_support = []

    for claim in crosswalk.get("claims", []):
        claim_id = claim.get("id", "")
        for field in REQUIRED_BOUNDARY_FIELDS:
            if not claim.get(field):
                missing_boundary_fields.append({"claim_id": claim_id, "field": field})

        stressors = claim.get("stressors", [])
        unknown = sorted(stressor for stressor in stressors if stressor not in ALLOWED_STRESSORS)
        if not stressors or unknown:
            invalid_stressors.append({"claim_id": claim_id, "stressors": unknown or stressors})

        expected_status = CLAIM_KINDS.get(claim_id)
        if expected_status and claim.get("claim_status") != expected_status:
            status_mismatches.append(
                {
                    "claim_id": claim_id,
                    "expected": expected_status,
                    "observed": claim.get("claim_status"),
                }
            )

        support_count = len(claim_to_sources.get(claim_id, []))
        if support_count == 0:
            claims_without_support.append(claim_id)

        rows.append(
            {
                "claim_id": claim_id,
                "claim_status": claim.get("claim_status", ""),
                "evidence_ceiling": claim.get("evidence_ceiling", ""),
                "prohibited_inference": claim.get("prohibited_inference", ""),
                "future_evidence_required": claim.get("future_evidence_required", ""),
                "stressors": {stressor: stressor in stressors for stressor in sorted(ALLOWED_STRESSORS)},
                "support_count": support_count,
                "artifact": claim.get("artifact", ""),
                "gate": claim.get("gate", ""),
            }
        )

    return {
        "schema": "realizing_emptiness.evidence_ceiling_audit.v1",
        "claim_count": len(rows),
        "stressors": [{"id": key, "description": value} for key, value in sorted(ALLOWED_STRESSORS.items())],
        "rows": sorted(rows, key=lambda row: row["claim_id"]),
        "missing_boundary_fields": sorted(missing_boundary_fields, key=lambda row: (row["claim_id"], row["field"])),
        "invalid_stressors": sorted(invalid_stressors, key=lambda row: row["claim_id"]),
        "status_mismatches": sorted(status_mismatches, key=lambda row: row["claim_id"]),
        "claims_without_support": sorted(claims_without_support),
        "ok": not missing_boundary_fields and not invalid_stressors and not status_mismatches and not claims_without_support,
    }


def write_evidence_ceiling_audit(project_root: Path, crosswalk: dict[str, Any]) -> Path:
    """Write the evidence-ceiling stress audit."""
    payload = build_evidence_ceiling_audit(project_root, crosswalk)
    path = project_root / "output" / "data" / "evidence_ceiling_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
