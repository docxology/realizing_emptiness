"""Manuscript citation and claim-boundary audits."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .scholarship import bibliography_keys


STRONG_CLAIM_VERBS = (
    "prove",
    "proves",
    "proved",
    "establish",
    "establishes",
    "established",
    "confirm",
    "confirms",
    "confirmed",
    "validate",
    "validates",
    "validated",
    "demonstrate",
    "demonstrates",
    "demonstrated",
    "show",
    "shows",
    "shown",
)

CLAIM_TARGET_TERMS = (
    "software",
    "repository",
    "audit",
    "artifact",
    "result",
    "results",
    "model",
    "simulation",
    "surrogate",
    "claim",
    "evidence",
    "qrf",
    "bmr",
    "qfep",
    "criticality",
    "compassion",
    "practice",
    "no-self",
    "no self",
    "self",
    "boundary",
)

# Outcome phrases that may not be positively claimed for the finite software (blocked classes
# re-3 physical qFEP, re-4 human-subject, re-13 clinical/neural/awakening, re-14 practice). Hyphens
# are normalized to spaces before scanning (see _normalize_for_scan), so "human-subject" matches here.
_BLOCKED_OUTCOME_PHRASES = (
    "awakening",
    "realization",
    "realisation",
    "neural criticality",
    "clinical benefit",
    "clinical efficacy",
    "therapeutic benefit",
    "practice efficacy",
    "compassion gain",
    "compassion gains",
    "compassion efficacy",
    "physical qfep realization",
    "physical qfep realisation",
    "human subject validation",
    "human subject outcome",
    "human subject outcomes",
    "human subject effect",
    "human subject effects",
    "human subject data",
)

_STRONG_VERB_ALT = "|".join(STRONG_CLAIM_VERBS)
_BLOCKED_OUTCOME_ALT = "|".join(re.escape(phrase) for phrase in _BLOCKED_OUTCOME_PHRASES)

FORBIDDEN_POSITIVE_PATTERNS = {
    "proves_realization_or_efficacy": re.compile(
        r"\b(prove|proves|proved|proving)\s+(awakening|realization|realisation|emptiness|compassion|clinical|therapeutic)",
        re.IGNORECASE,
    ),
    "claims_therapeutic_effectiveness": re.compile(
        r"\b(clinically|therapeutically)\s+(effective|validated|proven)\b",
        re.IGNORECASE,
    ),
    "claims_neural_criticality_measurement": re.compile(r"\bmeasures?\s+neural\s+criticality\b", re.IGNORECASE),
    "claims_evidence_for_attainment": re.compile(
        r"\bevidence\s+for\s+(awakening|realization|realisation|clinical benefit|spiritual attainment)\b",
        re.IGNORECASE,
    ),
    # Any strong claim verb (prove/establish/confirm/validate/demonstrate/show + inflections) within a
    # few words of a blocked outcome phrase. The narrow `prove*` pattern above missed
    # confirms/establishes/demonstrates/validates/shows entirely; this closes that gap. Negation is
    # exempted at the sentence level in ``_forbidden_hits`` so honestly-hedged prose stays clean.
    "claims_blocked_outcome_with_strong_verb": re.compile(
        rf"\b({_STRONG_VERB_ALT})\b(?:\s+\w+){{0,3}}\s+({_BLOCKED_OUTCOME_ALT})",
        re.IGNORECASE,
    ),
    # Human-subject (re-4) outcomes matched as a CLASS rather than enumerated phrases, so singular and
    # plural forms are both caught ("human subject outcome", "human-subjects validation"). Hyphens are
    # normalized to spaces before scanning, so the hyphenated forms reduce to this space-delimited class.
    "claims_human_subject_outcome": re.compile(
        rf"\b({_STRONG_VERB_ALT})\b(?:\s+\w+){{0,3}}\s+human subjects?\s+(validation|outcomes?|effects?|data|results?)",
        re.IGNORECASE,
    ),
}

# Sentence-level negation exemption (cannot/never/no/without/neither/nor/nothing/non/n't), broader and
# more robust than the prior 16-character "not " prefix substring test, which false-positived on
# never/nothing-hedged sentences and was inconsistent with the claim-context negation regex.
_NEGATION_PATTERN = re.compile(
    r"\b(not|none|never|without|neither|nor|nothing|cannot|non)\b|\bno\b(?![-\s]+self)|n't",
    re.IGNORECASE,
)

BOUNDARY_SCOPING_TERMS = (
    "finite",
    "software",
    "surrogate",
    "simulation",
    "audit",
    "not empirical",
    "not evidence",
    "claim boundary",
    "evidence ceiling",
    "negative control",
)

BLOCKED_CLAIM_DOMAINS = (
    "awakening",
    "realization",
    "realisation",
    "clinical",
    "therapeutic",
    "neural",
    "practice efficacy",
    "physical qfep",
    "human subject",
)


def manuscript_fragment_text(project_root: Path) -> str:
    """Concatenate source manuscript fragments for audit."""
    section_root = project_root / "docs" / "manuscript" / "sections"
    parts = []
    for path in sorted(section_root.glob("*/*.md")):
        parts.append(path.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def citation_keys_in_text(text: str) -> set[str]:
    """Extract Pandoc citation keys from manuscript Markdown text."""
    keys = set(re.findall(r"(?<![A-Za-z0-9_:-])@([A-Za-z0-9_:-]+)", text))
    return {key.rstrip(":") for key in keys if not key.startswith(("sec:", "fig:", "eq:"))}


def _forbidden_hits(text: str) -> list[dict[str, str]]:
    """Find positive blocked-domain claims, exempting sentences that negate the claim.

    Scans sentence by sentence so the negation check binds to the clause that actually contains the
    strong verb: a sentence is exempt only when a negation token precedes the matched verb within the
    same sentence (e.g. "the audit does not demonstrate clinical benefit"), so an honestly-hedged
    sentence stays clean while a bare positive claim ("the audit demonstrates clinical benefit") fires.
    """
    hits = []
    for sentence_match in re.finditer(r"[^.!?\n]+[.!?]", text):
        # Normalize hyphens to spaces so hyphenated blocked phrases (e.g. "human-subject validation")
        # are caught by the same space-delimited patterns; collapse whitespace for robust word spans.
        sentence = re.sub(r"\s+", " ", sentence_match.group(0).replace("-", " "))
        for name, pattern in FORBIDDEN_POSITIVE_PATTERNS.items():
            match = pattern.search(sentence)
            if not match:
                continue
            preceding = sentence[: match.start()]
            if _NEGATION_PATTERN.search(preceding):
                continue
            hits.append({"pattern": name, "match": re.sub(r"\s+", " ", match.group(0)).strip()})
    return hits


def _sentences_with_locations(project_root: Path) -> list[dict[str, str]]:
    rows = []
    for path in sorted((project_root / "docs" / "manuscript" / "sections").glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"[^.!?\n]+[.!?]", text):
            sentence = re.sub(r"\s+", " ", match.group(0)).strip()
            if sentence:
                rows.append({"file": str(path.relative_to(project_root)), "sentence": sentence})
    return rows


def classify_sentence_intensity(sentence: str) -> dict[str, Any]:
    lower = sentence.lower()
    strong_verbs = [verb for verb in STRONG_CLAIM_VERBS if re.search(rf"\b{re.escape(verb)}\b", lower)]
    domains = [domain for domain in BLOCKED_CLAIM_DOMAINS if domain in lower]
    targets = [term for term in CLAIM_TARGET_TERMS if term in lower]
    scoped = any(term in lower for term in BOUNDARY_SCOPING_TERMS)
    negated = bool(_NEGATION_PATTERN.search(lower))
    no_self_assertion = any(term in lower for term in ("no-self", "no self"))
    no_self_boundary_scoped = any(term in lower for term in ("boundary", "evidence ceiling", "claim boundary"))
    blocked_domain_scoped = any(
        term in lower
        for term in (
            "finite",
            "surrogate",
            "simulation",
            "not empirical",
            "not evidence",
            "claim boundary",
            "evidence ceiling",
            "negative control",
        )
    )
    blocked_domain_risky = bool(strong_verbs and domains and not blocked_domain_scoped and not negated)
    unscoped_strong_claim = bool(strong_verbs and targets and not scoped and not negated)
    no_self_risky = bool(strong_verbs and no_self_assertion and not no_self_boundary_scoped and not negated)
    risky = blocked_domain_risky or unscoped_strong_claim or no_self_risky
    return {
        "sentence": sentence,
        "strong_verbs": strong_verbs,
        "blocked_domains": domains,
        "claim_target_terms": targets,
        "has_boundary_scope": scoped,
        "has_negation": negated,
        "blocked_domain_risky": blocked_domain_risky,
        "unscoped_strong_claim": unscoped_strong_claim,
        "no_self_risky": no_self_risky,
        "allowed": not risky,
    }


def build_manuscript_claim_intensity_audit(project_root: Path) -> dict[str, Any]:
    """Audit strong claim verbs at sentence level."""
    rows = []
    for item in _sentences_with_locations(project_root):
        classified = classify_sentence_intensity(item["sentence"])
        if classified["strong_verbs"] or classified["blocked_domains"]:
            rows.append({"file": item["file"], **classified})
    risky_rows = [row for row in rows if not row["allowed"]]
    return {
        "schema": "realizing_emptiness.manuscript_claim_intensity_audit.v1",
        "sentence_count": len(_sentences_with_locations(project_root)),
        "row_count": len(rows),
        "rows": rows,
        "risky_rows": risky_rows,
        "strong_verb_count": sum(len(row["strong_verbs"]) for row in rows),
        "ok": not risky_rows,
        "claim_boundary": "sentence-level manuscript language audit; not empirical evidence",
    }


def build_manuscript_claim_audit(project_root: Path, crosswalk: dict[str, Any]) -> dict[str, Any]:
    """Audit manuscript citations, public claim mentions, and positive-efficacy wording."""
    text = manuscript_fragment_text(project_root)
    used_citations = citation_keys_in_text(text)
    declared_bib = bibliography_keys(project_root)
    public_claim_ids = sorted(claim["id"] for claim in crosswalk.get("claims", []))
    missing_claim_mentions = sorted(claim_id for claim_id in public_claim_ids if claim_id not in text)
    missing_bibliography_keys = sorted(key for key in used_citations if key not in declared_bib)
    uncited_bibliography_keys = sorted(key for key in declared_bib if key not in used_citations)
    forbidden_hits = _forbidden_hits(text)
    return {
        "schema": "realizing_emptiness.manuscript_claim_audit.v1",
        "fragment_count": len(list((project_root / "docs" / "manuscript" / "sections").glob("*/*.md"))),
        "used_citation_count": len(used_citations),
        "declared_bibliography_count": len(declared_bib),
        "public_claim_count": len(public_claim_ids),
        "used_citations": sorted(used_citations),
        "missing_bibliography_keys": missing_bibliography_keys,
        "uncited_bibliography_keys": uncited_bibliography_keys,
        "public_claim_ids": public_claim_ids,
        "missing_claim_mentions": missing_claim_mentions,
        "forbidden_positive_claims": forbidden_hits,
        "ok": not missing_bibliography_keys and not missing_claim_mentions and not forbidden_hits,
    }


def write_manuscript_claim_audit(project_root: Path, crosswalk: dict[str, Any]) -> Path:
    """Write the manuscript claim audit artifact."""
    payload = build_manuscript_claim_audit(project_root, crosswalk)
    path = project_root / "output" / "data" / "manuscript_claim_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def write_manuscript_claim_intensity_audit(project_root: Path) -> Path:
    """Write the sentence-level manuscript claim-intensity audit."""
    payload = build_manuscript_claim_intensity_audit(project_root)
    path = project_root / "output" / "data" / "manuscript_claim_intensity_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
