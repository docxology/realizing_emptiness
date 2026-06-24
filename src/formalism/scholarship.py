"""Scholarship manifest checks and source-role matrix generation."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


MANIFEST = "data/sources/scholarship_manifest.yaml"


CLAIM_KINDS = {
    "artifact_release_readiness": "implementation_boundary",
    "bmr_prunes_sigma": "finite_sweep",
    "compassion_proxy_boundary": "proxy_boundary",
    "criticality_proxy_boundary": "proxy_boundary",
    "fep_background": "background_boundary",
    "habit_policy_precision": "background_boundary",
    "metacognitive_access_model": "implementation_boundary",
    "practice_protocol_boundary": "safety_boundary",
    "pymdp_runtime_canary": "runtime_canary",
    "quantum_contextuality_witness": "finite_quantum_simulation",
    "quantum_measurement_contextuality": "finite_quantum_simulation",
    "quantum_open_system_dephasing": "finite_quantum_simulation",
    "quantum_separability_entropy": "finite_quantum_simulation",
    "qfep_surrogate_scope": "formal_boundary",
    "qrf_background_only": "background_boundary",
    "self_evidencing_boundary": "background_boundary",
    "separation_prior_sigma": "implemented_model",
    "source_boundary_unevidenceable": "operational_surrogate",
}


REQUIRED_COUNTERWEIGHT_GROUPS = {
    "qrf_physical_boundary": {
        "giacomini2019qrf",
        "vanrietvelde2020perspective",
        "bartlett2007reference",
    },
    "fep_blanket_critique_response": {
        "aguilera2021particular",
        "biehl2021technical_fep",
        "heins2022sparse_coupling",
    },
    "criticality_false_positive_caution": {
        "touboul2017power_law_absence_criticality",
        "destexhe2021criticality_evidence",
        "wilting2019criticality",
    },
}


def load_scholarship_manifest(project_root: Path) -> dict[str, Any]:
    """Load the scholarship manifest."""
    with (project_root / MANIFEST).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def bibliography_keys(project_root: Path) -> set[str]:
    """Return citation keys declared in the manuscript bibliography."""
    text = (project_root / "manuscript" / "references.bib").read_text(encoding="utf-8")
    return set(re.findall(r"@\w+\{([^,\s]+)", text))


def validate_scholarship_manifest(project_root: Path) -> dict[str, Any]:
    """Validate uniqueness, bibliography coverage, and claim-boundary fields."""
    manifest = load_scholarship_manifest(project_root)
    entries = manifest.get("entries", [])
    ids = [entry.get("id") for entry in entries]
    citation_keys = [entry.get("citation_key") for entry in entries]
    bib_keys = bibliography_keys(project_root)
    missing_bib_keys = sorted(key for key in citation_keys if key not in bib_keys)
    citation_key_set = set(citation_keys)
    missing_counterweight_groups = {
        group: sorted(required - citation_key_set)
        for group, required in REQUIRED_COUNTERWEIGHT_GROUPS.items()
        if required - citation_key_set
    }
    missing_boundaries = sorted(entry.get("id", "") for entry in entries if not entry.get("evidence_status"))
    role_counts = Counter(entry.get("role", "unknown") for entry in entries)
    track_counts: Counter[str] = Counter()
    supported_claims: Counter[str] = Counter()
    for entry in entries:
        track_counts.update(entry.get("tracks", []))
        supported_claims.update(entry.get("supports_claims", []))
    unknown_claim_ids = sorted(claim_id for claim_id in supported_claims if claim_id not in CLAIM_KINDS)
    return {
        "schema": "realizing_emptiness.scholarship_validation.v1",
        "entry_count": len(entries),
        "unique_ids": len(ids) == len(set(ids)),
        "unique_citation_keys": len(citation_keys) == len(set(citation_keys)),
        "missing_bibliography_keys": missing_bib_keys,
        "required_counterweight_groups": {
            group: sorted(keys) for group, keys in sorted(REQUIRED_COUNTERWEIGHT_GROUPS.items())
        },
        "missing_counterweight_groups": missing_counterweight_groups,
        "missing_boundaries": missing_boundaries,
        "unknown_claim_ids": unknown_claim_ids,
        "role_counts": dict(sorted(role_counts.items())),
        "track_counts": dict(sorted(track_counts.items())),
        "supported_claim_counts": dict(sorted(supported_claims.items())),
        "ok": bool(entries)
        and len(ids) == len(set(ids))
        and len(citation_keys) == len(set(citation_keys))
        and not missing_bib_keys
        and not missing_counterweight_groups
        and not missing_boundaries
        and not unknown_claim_ids,
    }


def build_scholarship_source_matrix(project_root: Path) -> dict[str, Any]:
    """Build a track-by-source matrix for scholarship coverage."""
    manifest = load_scholarship_manifest(project_root)
    entries = manifest["entries"]
    tracks = sorted({track for entry in entries for track in entry.get("tracks", [])})
    rows = []
    for entry in entries:
        track_set = set(entry.get("tracks", []))
        rows.append(
            {
                "id": entry["id"],
                "citation_key": entry["citation_key"],
                "role": entry["role"],
                "evidence_status": entry["evidence_status"],
                "tracks": {track: track in track_set for track in tracks},
                "track_count": len(track_set),
                "claim_count": len(entry.get("supports_claims", [])),
            }
        )
    validation = validate_scholarship_manifest(project_root)
    return {
        "schema": "realizing_emptiness.scholarship_source_matrix.v1",
        "source_count": len(entries),
        "track_count": len(tracks),
        "tracks": tracks,
        "rows": rows,
        "validation": validation,
    }


def build_claim_support_audit(project_root: Path, crosswalk: dict[str, Any]) -> dict[str, Any]:
    """Build a claim-by-source support audit from the scholarship manifest."""
    manifest = load_scholarship_manifest(project_root)
    entries = manifest["entries"]
    public_claims = {claim["id"]: claim for claim in crosswalk.get("claims", [])}
    support_rows = []
    claim_to_sources: dict[str, list[str]] = {claim_id: [] for claim_id in CLAIM_KINDS}
    for entry in entries:
        for claim_id in entry.get("supports_claims", []):
            claim_to_sources.setdefault(claim_id, []).append(entry["citation_key"])
            support_rows.append(
                {
                    "claim_id": claim_id,
                    "claim_kind": CLAIM_KINDS.get(claim_id, "unknown"),
                    "citation_key": entry["citation_key"],
                    "source_id": entry["id"],
                    "evidence_status": entry["evidence_status"],
                    "role": entry["role"],
                    "public_crosswalk_claim": claim_id in public_claims,
                }
            )
    unknown_claim_ids = sorted(claim_id for claim_id in claim_to_sources if claim_id not in CLAIM_KINDS)
    unsupported_public_claims = sorted(claim_id for claim_id in public_claims if not claim_to_sources.get(claim_id))
    public_claims_without_gate = sorted(
        claim_id for claim_id, claim in public_claims.items() if not claim.get("gate") or not claim.get("artifact")
    )
    return {
        "schema": "realizing_emptiness.claim_support_audit.v1",
        "claim_registry": [{"id": key, "kind": value} for key, value in sorted(CLAIM_KINDS.items())],
        "registered_claim_count": len(CLAIM_KINDS),
        "public_claim_count": len(public_claims),
        "support_row_count": len(support_rows),
        "support_rows": sorted(support_rows, key=lambda row: (row["claim_id"], row["citation_key"])),
        "claim_to_sources": {claim_id: sorted(sources) for claim_id, sources in sorted(claim_to_sources.items()) if sources},
        "unknown_claim_ids": unknown_claim_ids,
        "unsupported_public_claims": unsupported_public_claims,
        "public_claims_without_gate": public_claims_without_gate,
        "ok": not unknown_claim_ids and not unsupported_public_claims and not public_claims_without_gate,
    }


def write_scholarship_source_matrix(project_root: Path) -> Path:
    """Write scholarship matrix JSON."""
    payload = build_scholarship_source_matrix(project_root)
    path = project_root / "output" / "data" / "scholarship_source_matrix.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_claim_support_audit(project_root: Path, crosswalk: dict[str, Any]) -> Path:
    """Write claim support audit JSON."""
    payload = build_claim_support_audit(project_root, crosswalk)
    path = project_root / "output" / "data" / "claim_support_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
