from __future__ import annotations

from pathlib import Path
from typing import Any

from formalism.review_response_common import CLAIM_BOUNDARY, LOCAL_RELEASE_BOUNDARY


def review_response_rows() -> list[dict[str, Any]]:
    return [
        {
            "recommendation_id": "local_artifact_release_manifest",
            "reviewer_concern": "Account for release-readiness without implying public publication.",
            "response_status": "implemented_local_delta",
            "evidence_paths": ["output/data/artifact_release_manifest.json", "artifact_manifest.yaml"],
            "gate": "artifact_release_manifest_ok",
            "boundary": LOCAL_RELEASE_BOUNDARY,
        },
        {
            "recommendation_id": "parameter_result_traceability",
            "reviewer_concern": "Make figure parameters, result counts, controls, and source artifacts explicit.",
            "response_status": "implemented_local_delta",
            "evidence_paths": ["output/data/figure_parameter_ledger.json", "output/data/figure_source_map.json"],
            "gate": "figure_parameter_ledger_ok",
            "boundary": CLAIM_BOUNDARY,
        },
        {
            "recommendation_id": "neutral_qrf_label_ablation",
            "reviewer_concern": "Show that loaded labels do not carry the QRF result.",
            "response_status": "implemented_local_delta",
            "evidence_paths": ["output/data/qrf_label_ablation_audit.json", "output/data/qrf_boundary_channel_ledger.json"],
            "gate": "qrf_label_ablation_audit_ok",
            "boundary": CLAIM_BOUNDARY,
        },
        {
            "recommendation_id": "independent_quantum_crosscheck",
            "reviewer_concern": "Recompute CHSH, Tsirelson, product locality, and local-polytope status independently.",
            "response_status": "implemented_local_delta",
            "evidence_paths": ["output/data/quantum_independent_crosscheck_audit.json"],
            "gate": "quantum_independent_crosscheck_audit_ok",
            "boundary": CLAIM_BOUNDARY,
        },
        {
            "recommendation_id": "bmr_alternative_prior_families",
            "reviewer_concern": "Check the BMR pruning result against comparator prior families.",
            "response_status": "implemented_local_delta",
            "evidence_paths": ["output/data/bmr_alternative_prior_audit.json"],
            "gate": "bmr_alternative_prior_audit_ok",
            "boundary": CLAIM_BOUNDARY,
        },
        {
            "recommendation_id": "bibliography_additions",
            "reviewer_concern": "Add CHSH/local-polytope, Bayesian workflow, SBC, artifact-release, FEP critique/response, and criticality-caution sources.",
            "response_status": "implemented_local_delta",
            "evidence_paths": [
                "data/sources/scholarship_manifest.yaml",
                "manuscript/references.bib",
                "manuscript/sections/supplement/scholarship.md",
            ],
            "gate": "scholarship_manifest_ok",
            "boundary": CLAIM_BOUNDARY,
        },
        {
            "recommendation_id": "public_independent_reproduction",
            "reviewer_concern": "Do not represent local private readiness as public independent reproduction.",
            "response_status": "blocked_external_publication",
            "evidence_paths": ["TODO.md", "tasks.yaml"],
            "gate": "future_public_archive_and_independent_reproduction_blocked",
            "boundary": "future public archive and blinded or independent reproduction require explicit publication approval; not empirical and not completed locally",
        },
    ]


def build_external_review_response_audit(project_root: Path) -> dict[str, Any]:
    rows = review_response_rows()
    missing_evidence = []
    for row in rows:
        if row["response_status"] == "blocked_external_publication":
            continue
        for relative in row["evidence_paths"]:
            if not (project_root / relative).exists():
                missing_evidence.append({"recommendation_id": row["recommendation_id"], "path": relative})
    implemented_ids = {row["recommendation_id"] for row in rows if row["response_status"] == "implemented_local_delta"}
    required_implemented = {
        "local_artifact_release_manifest",
        "parameter_result_traceability",
        "neutral_qrf_label_ablation",
        "independent_quantum_crosscheck",
        "bmr_alternative_prior_families",
        "bibliography_additions",
    }
    controls = {
        "all_local_delta_rows_have_evidence": not missing_evidence,
        "required_local_deltas_present": required_implemented <= implemented_ids,
        "public_reproduction_blocked_not_completed": any(row["response_status"] == "blocked_external_publication" for row in rows),
        "all_rows_have_gates": all(row.get("gate") for row in rows),
        "all_boundaries_declared": all("not empirical" in row.get("boundary", "") for row in rows),
    }
    return {
        "schema": "realizing_emptiness.external_review_response_audit.v1",
        "row_count": len(rows),
        "rows": rows,
        "missing_evidence": missing_evidence,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
