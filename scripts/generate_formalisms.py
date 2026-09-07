#!/usr/bin/env python3
"""Generate formalism registry, equation audit, source hash check, and claim crosswalk."""

from __future__ import annotations

import json

from _bootstrap import PROJECT_ROOT
from formalism.claim_crosswalk import claim_crosswalk
from formalism.equations import evaluate_equation_surrogates, equation_registry
from formalism.governance import write_method_governance_artifacts
from formalism.manuscript import write_manuscript_claim_audit, write_manuscript_claim_intensity_audit
from formalism.scholarship import write_claim_support_audit, write_scholarship_source_matrix
from formalism.source import verify_primary_source_hash
from formalism.stress import write_evidence_ceiling_audit
from gates.contracts import write_artifact_contract_registry


def main() -> int:
    data_dir = PROJECT_ROOT / "output" / "data"
    reports_dir = PROJECT_ROOT / "output" / "reports"
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    registry = {
        "schema": "realizing_emptiness.formalism_registry.v1",
        "equations": [row.as_dict() for row in equation_registry()],
        "equation_count": len(equation_registry()),
        "source_hash": verify_primary_source_hash(PROJECT_ROOT),
    }
    (data_dir / "formalism_registry.json").write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (data_dir / "equation_audit.json").write_text(
        json.dumps(evaluate_equation_surrogates(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    crosswalk = claim_crosswalk()
    (data_dir / "source_claim_crosswalk.json").write_text(
        json.dumps(crosswalk, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_scholarship_source_matrix(PROJECT_ROOT)
    write_claim_support_audit(PROJECT_ROOT, crosswalk)
    write_manuscript_claim_audit(PROJECT_ROOT, crosswalk)
    write_manuscript_claim_intensity_audit(PROJECT_ROOT)
    write_evidence_ceiling_audit(PROJECT_ROOT, crosswalk)
    write_method_governance_artifacts(PROJECT_ROOT)
    write_artifact_contract_registry(PROJECT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
