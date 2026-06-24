"""Formal data models and equation registry."""

from .claim_context import build_claim_context_ledger
from .claim_redteam import build_claim_redteam_audit
from .equations import EquationSurrogate, evaluate_equation_surrogates, equation_registry
from .manuscript import build_manuscript_claim_audit
from .models import BoundaryScreen, BMRComparison, FreeEnergyTerms, QRFDeployment, Sectorisation, SeparationPrior
from .scholarship import (
    build_claim_support_audit,
    build_scholarship_source_matrix,
    load_scholarship_manifest,
    validate_scholarship_manifest,
)
from .source import load_source_manifest, verify_primary_source_hash
from .stress import build_evidence_ceiling_audit

__all__ = [
    "BMRComparison",
    "BoundaryScreen",
    "EquationSurrogate",
    "FreeEnergyTerms",
    "QRFDeployment",
    "Sectorisation",
    "SeparationPrior",
    "build_manuscript_claim_audit",
    "build_claim_support_audit",
    "build_claim_context_ledger",
    "build_claim_redteam_audit",
    "build_evidence_ceiling_audit",
    "build_scholarship_source_matrix",
    "evaluate_equation_surrogates",
    "equation_registry",
    "load_scholarship_manifest",
    "load_source_manifest",
    "validate_scholarship_manifest",
    "verify_primary_source_hash",
]
