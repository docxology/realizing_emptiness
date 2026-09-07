from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from .claim_context import build_claim_context_ledger
from .manuscript import build_manuscript_claim_audit, build_manuscript_claim_intensity_audit
from .scholarship import build_claim_support_audit
from .source_fit import build_source_argument_coverage_audit
from .stress import build_evidence_ceiling_audit


CLAIM_BOUNDARY = (
    "claim red-team audit over public claim locations, figure bindings, gates, "
    "and language intensity; not empirical evidence, not a physical qFEP "
    "realization, and not a clinical, neural, awakening, or practice-efficacy claim"
)

READER_OVERCLAIM_PHRASES = (
    "empirical evidence",
    "clinical evidence",
    "neural measurement",
    "neural measurements",
    "practice efficacy",
    "practice outcome",
    "practice outcomes",
    "awakening evidence",
    "awakening outcome",
    "realization evidence",
    "realisation evidence",
    "ontological verdict",
    "ontological proof",
    "physical qfep realization",
    "physical qfep realisation",
)

_NEGATED_PREFIX = re.compile(
    r"\b(not|no|without|absent|neither|nor|cannot|does\s+not|do\s+not|never)\b"
    r"(?:\s+\w+){0,5}\s*$",
    re.IGNORECASE,
)


def _load_json(project_root: Path, relative: str) -> dict[str, Any]:
    path = project_root / relative
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _composed_manuscript_anchors(project_root: Path) -> set[str]:
    anchors: set[str] = set()
    for path in sorted((project_root / "docs" / "manuscript").glob("[0-9][0-9]_*.md")):
        text = path.read_text(encoding="utf-8")
        anchors.update(match.group(1) for match in re.finditer(r"\{#(sec:[^}\s]+)\}", text))
        anchors.update(match.group(1) for match in re.finditer(r"id=[\"'](sec:[^\"']+)[\"']", text))
    return anchors


def _figure_ids(figure_source_map: dict[str, Any]) -> set[str]:
    return {row.get("id", "") for row in figure_source_map.get("figures", []) if row.get("id")}


def _source_themes_by_claim(source_coverage: dict[str, Any]) -> dict[str, list[str]]:
    by_claim: dict[str, list[str]] = defaultdict(list)
    for row in source_coverage.get("rows", []):
        for claim_id in row.get("evidence_ceiling_claims", []):
            by_claim[claim_id].append(row.get("theme_id", ""))
    return {claim_id: sorted(theme for theme in themes if theme) for claim_id, themes in by_claim.items()}


def _binding_resolves(binding: str, figure_ids: set[str]) -> bool:
    return binding in figure_ids or binding.startswith("governed_fallback:")


def _reader_overclaims(text: str) -> list[str]:
    lower = text.lower()
    hits: list[str] = []
    for phrase in READER_OVERCLAIM_PHRASES:
        for match in re.finditer(re.escape(phrase), lower):
            prefix = lower[max(0, match.start() - 64) : match.start()]
            if _NEGATED_PREFIX.search(prefix):
                continue
            hits.append(phrase)
    return sorted(set(hits))


def build_claim_redteam_audit(
    project_root: Path,
    crosswalk: dict[str, Any],
    *,
    claim_context: dict[str, Any] | None = None,
    claim_support: dict[str, Any] | None = None,
    evidence_ceiling: dict[str, Any] | None = None,
    source_coverage: dict[str, Any] | None = None,
    manuscript_claim: dict[str, Any] | None = None,
    claim_intensity: dict[str, Any] | None = None,
    figure_source_map: dict[str, Any] | None = None,
) -> dict[str, Any]:
    claim_support = claim_support or build_claim_support_audit(project_root, crosswalk)
    evidence_ceiling = evidence_ceiling or build_evidence_ceiling_audit(project_root, crosswalk)
    source_coverage = source_coverage or build_source_argument_coverage_audit(project_root)
    claim_context = claim_context or build_claim_context_ledger(
        project_root,
        crosswalk,
        claim_support=claim_support,
        evidence_ceiling=evidence_ceiling,
        source_coverage=source_coverage,
    )
    manuscript_claim = manuscript_claim or build_manuscript_claim_audit(project_root, crosswalk)
    claim_intensity = claim_intensity or build_manuscript_claim_intensity_audit(project_root)
    figure_source_map = figure_source_map or _load_json(project_root, "output/data/figure_source_map.json")

    manuscript_anchors = _composed_manuscript_anchors(project_root)
    mapped_figure_ids = _figure_ids(figure_source_map)
    context_rows = {row.get("claim_id"): row for row in claim_context.get("rows", [])}
    ceiling_rows = {row.get("claim_id"): row for row in evidence_ceiling.get("rows", [])}
    themes_by_claim = _source_themes_by_claim(source_coverage)

    rows: list[dict[str, Any]] = []
    missing_sections: list[str] = []
    unresolved_sections: list[dict[str, str]] = []
    missing_figure_bindings: list[str] = []
    unresolved_figure_bindings: list[dict[str, str]] = []
    missing_boundaries: list[dict[str, str]] = []
    reader_overclaims: list[dict[str, Any]] = []
    missing_source_roles: list[str] = []
    missing_artifacts_or_gates: list[dict[str, str]] = []

    for claim in sorted(crosswalk.get("claims", []), key=lambda item: item.get("id", "")):
        claim_id = claim.get("id", "")
        context = context_rows.get(claim_id, {})
        ceiling = ceiling_rows.get(claim_id, {})
        sections = list(context.get("manuscript_sections", []))
        figure_bindings = list(context.get("figure_bindings", []))
        unresolved_for_claim = sorted(section for section in sections if section not in manuscript_anchors)
        unresolved_figures_for_claim = sorted(
            binding for binding in figure_bindings if not _binding_resolves(binding, mapped_figure_ids)
        )

        if not sections:
            missing_sections.append(claim_id)
        unresolved_sections.extend({"claim_id": claim_id, "section": section} for section in unresolved_for_claim)
        if not figure_bindings:
            missing_figure_bindings.append(claim_id)
        unresolved_figure_bindings.extend(
            {"claim_id": claim_id, "figure_id": figure_id}
            for figure_id in unresolved_figures_for_claim
        )

        boundary_fields = {
            "allowed_interpretation": context.get("allowed_interpretation", ""),
            "prohibited_inference": context.get("prohibited_inference", claim.get("prohibited_inference", "")),
            "future_evidence_required": context.get(
                "future_evidence_required", claim.get("future_evidence_required", "")
            ),
        }
        for field, value in boundary_fields.items():
            if not isinstance(value, str) or len(value.strip()) < 20:
                missing_boundaries.append({"claim_id": claim_id, "field": field})

        source_role_count = int(context.get("source_role_count", 0) or 0)
        if source_role_count <= 0:
            missing_source_roles.append(claim_id)
        artifact = str(context.get("artifact", claim.get("artifact", "")))
        gate = str(context.get("validation_gate", claim.get("gate", "")))
        artifact_exists = bool(artifact) and (project_root / artifact).exists()
        if not artifact_exists or not gate:
            missing_artifacts_or_gates.append({"claim_id": claim_id, "artifact": artifact, "gate": gate})

        wording = " ".join(
            str(value)
            for value in (
                context.get("reader_claim", ""),
                context.get("allowed_interpretation", ""),
            )
        )
        overclaim_hits = _reader_overclaims(wording)
        if overclaim_hits:
            reader_overclaims.append({"claim_id": claim_id, "phrases": overclaim_hits})

        failure_reasons = []
        if not sections:
            failure_reasons.append("missing manuscript sections")
        if unresolved_for_claim:
            failure_reasons.append("unresolved manuscript sections")
        if not figure_bindings:
            failure_reasons.append("missing figure bindings")
        if unresolved_figures_for_claim:
            failure_reasons.append("unresolved figure bindings")
        if source_role_count <= 0:
            failure_reasons.append("missing source role")
        if not artifact_exists:
            failure_reasons.append("missing artifact")
        if not gate:
            failure_reasons.append("missing validation gate")
        if overclaim_hits:
            failure_reasons.append("reader overclaim wording")
        if any(item["claim_id"] == claim_id for item in missing_boundaries):
            failure_reasons.append("missing boundary field")

        row_controls_pass = not failure_reasons
        rows.append(
            {
                "claim_id": claim_id,
                "evidence_class": claim.get("claim_status", ""),
                "artifact": artifact,
                "artifact_exists": artifact_exists,
                "validation_gate": gate,
                "source_role_count": source_role_count,
                "source_themes": themes_by_claim.get(claim_id, []),
                "manuscript_sections": sections,
                "section_count": len(sections),
                "section_anchors_resolve": not unresolved_for_claim and bool(sections),
                "unresolved_sections": unresolved_for_claim,
                "figure_bindings": figure_bindings,
                "figure_bindings_resolve": not unresolved_figures_for_claim and bool(figure_bindings),
                "unresolved_figure_bindings": unresolved_figures_for_claim,
                "allowed_interpretation": context.get("allowed_interpretation", ""),
                "prohibited_inference": boundary_fields["prohibited_inference"],
                "future_evidence_required": boundary_fields["future_evidence_required"],
                "evidence_ceiling": ceiling.get("evidence_ceiling", claim.get("evidence_ceiling", "")),
                "support_count": int(ceiling.get("support_count", source_role_count) or 0),
                "reader_overclaim_phrases": overclaim_hits,
                "row_controls_pass": row_controls_pass,
                "failure_reasons": failure_reasons,
                "redteam_note": (
                    "Reader locations, figure bindings, source role, artifact, gate, prohibited inference, "
                    "and future-evidence boundary are all present for this finite-software claim."
                    if row_controls_pass
                    else "Fails claim RedTeam controls: " + "; ".join(failure_reasons)
                ),
            }
        )

    crosswalk_claim_ids = sorted(claim.get("id", "") for claim in crosswalk.get("claims", []))
    context_claim_ids = sorted(context_rows)
    controls = {
        "all_public_claims_joined": crosswalk_claim_ids == context_claim_ids == sorted(row["claim_id"] for row in rows),
        "claim_count_matches_crosswalk": len(rows) == crosswalk.get("claim_count"),
        "all_claims_have_source_roles": not missing_source_roles,
        "all_claims_have_artifacts_and_gates": not missing_artifacts_or_gates,
        "all_claims_have_reader_locations": not missing_sections,
        "all_section_anchors_resolve": not unresolved_sections,
        "all_claims_have_figure_bindings": not missing_figure_bindings,
        "all_figure_bindings_resolve": not unresolved_figure_bindings,
        "all_claim_boundaries_complete": not missing_boundaries,
        "no_reader_overclaims": not reader_overclaims,
        "claim_context_controls_pass": claim_context.get("all_controls_pass") is True,
        "claim_support_audit_pass": claim_support.get("ok") is True,
        "evidence_ceiling_controls_pass": evidence_ceiling.get("ok") is True,
        "source_argument_coverage_pass": source_coverage.get("all_controls_pass") is True,
        "manuscript_claim_audit_pass": manuscript_claim.get("ok") is True,
        "manuscript_claim_intensity_pass": claim_intensity.get("ok") is True,
    }
    return {
        "schema": "realizing_emptiness.claim_redteam_audit.v1",
        "claim_count": len(rows),
        "rows": rows,
        "missing_sections": missing_sections,
        "unresolved_sections": unresolved_sections,
        "missing_figure_bindings": missing_figure_bindings,
        "unresolved_figure_bindings": unresolved_figure_bindings,
        "missing_boundaries": missing_boundaries,
        "missing_source_roles": missing_source_roles,
        "missing_artifacts_or_gates": missing_artifacts_or_gates,
        "reader_overclaims": reader_overclaims,
        "risky_claim_sentences": claim_intensity.get("risky_rows", []),
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_claim_redteam_audit(project_root: Path, crosswalk: dict[str, Any] | None = None) -> Path:
    crosswalk = crosswalk or _load_json(project_root, "output/data/source_claim_crosswalk.json")
    payload = build_claim_redteam_audit(project_root, crosswalk)
    path = project_root / "output" / "data" / "claim_redteam_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
