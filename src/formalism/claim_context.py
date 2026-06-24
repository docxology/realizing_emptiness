"""Reader-facing claim-context ledger generation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .scholarship import bibliography_keys, build_claim_support_audit, load_scholarship_manifest
from .source_fit import build_source_argument_coverage_audit
from .stress import build_evidence_ceiling_audit


CLAIM_BOUNDARY = (
    "claim-context ledger for source-role explanation; not empirical evidence, "
    "not a physical qFEP realization, and not a clinical, neural, awakening, "
    "or practice-efficacy claim"
)

PROXY_OR_SAFETY_STATUSES = {
    "proxy_boundary",
    "safety_boundary",
    "runtime_canary",
    "background_boundary",
    "implementation_boundary",
}

FORBIDDEN_READER_PHRASES = (
    "empirical evidence",
    "clinical evidence",
    "neural measurement",
    "practice efficacy",
    "proves awakening",
    "proves realization",
    "proves realisation",
    "physical qfep realization",
)

SECTION_DEFAULTS = {
    "quantum_separability_entropy": ["sec:results-finite-quantum-scope", "sec:supplement-finite-quantum-contextuality-audits"],
    "quantum_open_system_dephasing": ["sec:results-finite-quantum-scope", "sec:supplement-finite-quantum-contextuality-audits"],
    "qfep_surrogate_scope": ["sec:methods-roadmap-quantum-engines", "sec:results-finite-quantum-scope"],
    "self_evidencing_boundary": ["sec:introduction-paper-source", "sec:discussion-no-self-evidence-boundary"],
    "artifact_release_readiness": ["sec:supplement-reproducibility-gates", "sec:discussion-source-role-boundaries"],
}

FIGURE_BINDINGS = {
    "source_boundary_unevidenceable": [
        "qrf_boundary_screen_geometry",
        "qrf_channel_relabeling_ledger",
        "qrf_invariance_policy_flow",
        "claim_context_evidence_ladder",
    ],
    "separation_prior_sigma": [
        "qrf_channel_relabeling_ledger",
        "qrf_invariance_policy_flow",
        "claim_context_evidence_ladder",
    ],
    "bmr_prunes_sigma": ["bmr_pruning_phase_diagram", "evidence_ceiling_stress_matrix", "claim_context_evidence_ladder"],
    "practice_protocol_boundary": ["evidence_ceiling_stress_matrix", "claim_context_evidence_ladder"],
    "qfep_surrogate_scope": ["finite_quantum_scope_summary", "claim_context_evidence_ladder"],
    "quantum_separability_entropy": ["finite_quantum_scope_summary", "claim_context_evidence_ladder"],
    "quantum_contextuality_witness": ["finite_quantum_scope_summary", "claim_context_evidence_ladder"],
    "quantum_measurement_contextuality": ["finite_quantum_scope_summary", "claim_context_evidence_ladder"],
    "quantum_open_system_dephasing": ["finite_quantum_scope_summary", "claim_context_evidence_ladder"],
    "pymdp_runtime_canary": ["pymdp_profile_comparison", "claim_context_evidence_ladder"],
    "criticality_proxy_boundary": ["criticality_stochastic_ensemble", "claim_context_evidence_ladder"],
    "compassion_proxy_boundary": ["evidence_ceiling_stress_matrix", "claim_context_evidence_ladder"],
    "self_evidencing_boundary": ["claim_context_evidence_ladder"],
    "metacognitive_access_model": ["simulation_sensitivity_heatmap", "claim_context_evidence_ladder"],
    "artifact_release_readiness": ["claim_context_evidence_ladder"],
}


def _source_entries_by_key(project_root: Path) -> dict[str, dict[str, Any]]:
    manifest = load_scholarship_manifest(project_root)
    return {entry["citation_key"]: entry for entry in manifest.get("entries", [])}


def _support_rows_for_claim(support_rows: list[dict[str, Any]], claim_id: str) -> list[dict[str, Any]]:
    return sorted(
        [row for row in support_rows if row.get("claim_id") == claim_id and row.get("public_crosswalk_claim") is True],
        key=lambda row: row.get("citation_key", ""),
    )


def _sections_for_claim(source_coverage: dict[str, Any], claim_id: str) -> list[str]:
    sections = set(SECTION_DEFAULTS.get(claim_id, []))
    for row in source_coverage.get("rows", []):
        if claim_id in row.get("evidence_ceiling_claims", []):
            sections.update(row.get("local_sections", []))
    return sorted(sections)


def _role_rule(claim: dict[str, Any], support_rows: list[dict[str, Any]]) -> dict[str, Any]:
    claim_id = claim.get("id", "")
    status = claim.get("claim_status", "")
    role_text = " ".join(
        " ".join(str(row.get(key, "")) for key in ("citation_key", "role", "evidence_status", "source_id"))
        for row in support_rows
    ).lower()
    source_keys = {row.get("citation_key") for row in support_rows}

    if claim_id == "separation_prior_sigma":
        ok = "sandvedsmith2026noself" in source_keys
        return {
            "rule": "primary_source_formal_target_allowed",
            "ok": ok,
            "rationale": "A single primary-preprint row is sufficient because sigma is a source-paper formal claim.",
        }
    if status == "runtime_canary":
        ok = any(term in role_text for term in ("implementation", "runtime", "pymdp", "discrete active-inference"))
        return {"rule": "runtime_claim_requires_implementation_source", "ok": ok, "rationale": "Runtime claims need implementation or discrete active-inference support."}
    if status == "finite_quantum_simulation" or claim_id == "qfep_surrogate_scope":
        ok = any(
            term in role_text
            for term in (
                "quantum",
                "chsh",
                "contextual",
                "bell",
                "lindblad",
                "gksl",
                "trajectory",
                "wave-function",
                "cptp",
                "ppt",
                "entanglement",
                "measurement-cover",
            )
        )
        return {"rule": "quantum_or_qfep_claim_requires_quantum_method_source", "ok": ok, "rationale": "Finite quantum/qFEP claims need quantum, contextuality, or open-system method sources."}
    if status in {"proxy_boundary", "safety_boundary"}:
        ok = any(
            term in role_text
            for term in (
                "boundary",
                "caution",
                "practice",
                "criticality",
                "care",
                "compassion",
                "meta-awareness",
                "attentional",
                "constructive",
                "deconstructive",
                "empirical adapter",
                "provenance",
            )
        )
        return {"rule": "proxy_or_practice_claim_requires_boundary_or_caution_source", "ok": ok, "rationale": "Proxy and practice claims need boundary, caution, or domain-interface sources."}
    if status in {"finite_sweep", "implemented_model", "implementation_boundary"}:
        if claim_id == "artifact_release_readiness":
            ok = any(term in role_text for term in ("artifact", "reproducib", "workflow", "validation", "release"))
            return {"rule": "release_readiness_requires_artifact_or_workflow_source", "ok": ok, "rationale": "Local release-readiness claims need artifact, reproducibility, workflow, or validation support."}
        ok = any(term in role_text for term in ("active-inference", "bmr", "bayesian", "primary formal target", "metacognitive"))
        return {"rule": "model_claim_requires_formal_or_active_inference_source", "ok": ok, "rationale": "Finite model claims need formal, active-inference, or BMR support."}
    if status == "background_boundary":
        ok = any(term in role_text for term in ("background", "self-evidencing", "primary formal target"))
        return {"rule": "background_claim_requires_background_source", "ok": ok, "rationale": "Background claims need background or primary-source support."}
    return {"rule": "declared_support_present", "ok": bool(support_rows), "rationale": "Fallback rule requires at least one scoped source row."}


def _reader_claim_overclaims(claim: dict[str, Any]) -> bool:
    if claim.get("claim_status") not in PROXY_OR_SAFETY_STATUSES:
        return False
    text = f"{claim.get('paraphrase', '')} {claim.get('evidence_ceiling', '')}".lower()
    for phrase in FORBIDDEN_READER_PHRASES:
        for match in re.finditer(re.escape(phrase), text):
            window = text[max(0, match.start() - 16) : match.start()]
            if re.search(r"\b(not|no|without|absent|neither)\b\s+(?:a\s+|an\s+|any\s+)?$", window):
                continue
            return True
    return False


def build_claim_context_ledger(
    project_root: Path,
    crosswalk: dict[str, Any],
    *,
    claim_support: dict[str, Any] | None = None,
    evidence_ceiling: dict[str, Any] | None = None,
    source_coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a reader-facing claim ledger from source, support, and ceiling artifacts."""
    claim_support = claim_support or build_claim_support_audit(project_root, crosswalk)
    evidence_ceiling = evidence_ceiling or build_evidence_ceiling_audit(project_root, crosswalk)
    source_coverage = source_coverage or build_source_argument_coverage_audit(project_root)
    source_entries = _source_entries_by_key(project_root)
    bib_keys = bibliography_keys(project_root)
    ceiling_rows = {row["claim_id"]: row for row in evidence_ceiling.get("rows", [])}
    support_rows = claim_support.get("support_rows", [])

    rows = []
    missing_reader_claims = []
    missing_source_roles = []
    unresolved_source_keys = []
    missing_artifacts = []
    missing_gates = []
    missing_allowed_interpretations = []
    missing_prohibited_interpretations = []
    missing_future_evidence = []
    missing_manuscript_sections = []
    missing_figure_bindings = []
    role_compatibility_failures = []
    proxy_overclaiming_reader_claims = []

    for claim in sorted(crosswalk.get("claims", []), key=lambda row: row["id"]):
        claim_id = claim["id"]
        claim_sources = _support_rows_for_claim(support_rows, claim_id)
        source_keys = sorted({row["citation_key"] for row in claim_sources})
        source_roles = [
            {
                "citation_key": row["citation_key"],
                "source_id": row["source_id"],
                "role": row["role"],
                "evidence_status": row["evidence_status"],
            }
            for row in claim_sources
        ]
        unresolved = sorted(key for key in source_keys if key not in bib_keys or key not in source_entries)
        unresolved_source_keys.extend({"claim_id": claim_id, "citation_key": key} for key in unresolved)
        if not source_roles:
            missing_source_roles.append(claim_id)

        reader_claim = claim.get("paraphrase", "")
        allowed = f"Allowed only as {claim.get('evidence_ceiling', '')}: {reader_claim}"
        prohibited = claim.get("prohibited_inference", "")
        if not reader_claim or len(reader_claim) < 20:
            missing_reader_claims.append(claim_id)
        if not allowed or len(allowed) < 40:
            missing_allowed_interpretations.append(claim_id)
        if not prohibited or len(prohibited) < 20:
            missing_prohibited_interpretations.append(claim_id)
        if not claim.get("future_evidence_required", "") or len(claim.get("future_evidence_required", "")) < 20:
            missing_future_evidence.append(claim_id)
        if _reader_claim_overclaims(claim):
            proxy_overclaiming_reader_claims.append(claim_id)

        artifact_exists = bool(claim.get("artifact")) and (project_root / claim["artifact"]).exists()
        if not artifact_exists:
            missing_artifacts.append({"claim_id": claim_id, "artifact": claim.get("artifact", "")})
        if not claim.get("gate"):
            missing_gates.append(claim_id)

        role_compatibility = _role_rule(claim, claim_sources)
        if not role_compatibility["ok"]:
            role_compatibility_failures.append({"claim_id": claim_id, **role_compatibility})

        manuscript_sections = _sections_for_claim(source_coverage, claim_id)
        figure_bindings = FIGURE_BINDINGS.get(claim_id, ["claim_context_evidence_ladder"])
        if not manuscript_sections:
            missing_manuscript_sections.append(claim_id)
        if not figure_bindings:
            missing_figure_bindings.append(claim_id)

        rows.append(
            {
                "claim_id": claim_id,
                "reader_claim": reader_claim,
                "paper_locator": claim.get("paper_locator", ""),
                "allowed_interpretation": allowed,
                "prohibited_inference": prohibited,
                "source_roles": source_roles,
                "source_keys": source_keys,
                "source_role_count": len(source_roles),
                "artifact": claim.get("artifact", ""),
                "artifact_exists": artifact_exists,
                "validation_gate": claim.get("gate", ""),
                "evidence_class": claim.get("claim_status", ""),
                "evidence_ceiling": claim.get("evidence_ceiling", ""),
                "stressors": sorted(claim.get("stressors", [])),
                "future_evidence_required": claim.get("future_evidence_required", ""),
                "manuscript_sections": manuscript_sections,
                "figure_bindings": figure_bindings,
                "role_compatibility": role_compatibility,
                "support_count": ceiling_rows.get(claim_id, {}).get("support_count", len(source_roles)),
            }
        )

    controls = {
        "all_public_claims_represented": len(rows) == crosswalk.get("claim_count"),
        "all_reader_claims_present": not missing_reader_claims,
        "all_source_roles_present": not missing_source_roles,
        "all_source_keys_resolve": not unresolved_source_keys,
        "all_artifacts_exist": not missing_artifacts,
        "all_gates_declared": not missing_gates,
        "all_allowed_interpretations_present": not missing_allowed_interpretations,
        "all_prohibited_interpretations_present": not missing_prohibited_interpretations,
        "all_future_evidence_boundaries_present": not missing_future_evidence,
        "all_manuscript_sections_present": not missing_manuscript_sections,
        "all_figure_bindings_present": not missing_figure_bindings,
        "all_role_compatibility_rules_pass": not role_compatibility_failures,
        "no_proxy_or_safety_reader_overclaims": not proxy_overclaiming_reader_claims,
    }
    return {
        "schema": "realizing_emptiness.claim_context_ledger.v1",
        "claim_count": len(rows),
        "rows": rows,
        "missing_reader_claims": missing_reader_claims,
        "missing_source_roles": missing_source_roles,
        "unresolved_source_keys": unresolved_source_keys,
        "missing_artifacts": missing_artifacts,
        "missing_gates": missing_gates,
        "missing_allowed_interpretations": missing_allowed_interpretations,
        "missing_prohibited_interpretations": missing_prohibited_interpretations,
        "missing_future_evidence": missing_future_evidence,
        "missing_manuscript_sections": missing_manuscript_sections,
        "missing_figure_bindings": missing_figure_bindings,
        "role_compatibility_failures": role_compatibility_failures,
        "proxy_overclaiming_reader_claims": proxy_overclaiming_reader_claims,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_claim_context_ledger(project_root: Path, crosswalk: dict[str, Any]) -> Path:
    """Write claim context ledger JSON."""
    payload = build_claim_context_ledger(project_root, crosswalk)
    path = project_root / "output" / "data" / "claim_context_ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
