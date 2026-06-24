#!/usr/bin/env python3
"""Generate compact sheaf-track, practice, criticality, and dependency artifacts."""

from __future__ import annotations

import json

from _bootstrap import PROJECT_ROOT
from formalism.claim_context import write_claim_context_ledger
from formalism.source_fit import write_source_argument_coverage_audit
from gates.roadmap import write_roadmap_governance_artifacts
from practice.protocols import practice_protocol_map
from simulation.criticality import build_criticality_report, build_criticality_stochastic_ensemble
from simulation.sensitivity import write_sensitivity_grid


def _load_json(relative: str) -> dict:
    return json.loads((PROJECT_ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    data_dir = PROJECT_ROOT / "output" / "data"
    reports_dir = PROJECT_ROOT / "output" / "reports"
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    profile = _load_json("output/data/pymdp_profile_comparison.json")
    stochastic = _load_json("output/data/stochastic_policy_ensemble.json")
    criticality = build_criticality_report(profile)
    criticality_stochastic = build_criticality_stochastic_ensemble(stochastic)
    practice = practice_protocol_map()
    write_sensitivity_grid(PROJECT_ROOT)
    write_source_argument_coverage_audit(PROJECT_ROOT)
    (reports_dir / "criticality_proxy_report.json").write_text(
        json.dumps(criticality, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "criticality_stochastic_ensemble.json").write_text(
        json.dumps(criticality_stochastic, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "practice_protocol_map.json").write_text(
        json.dumps(practice, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    crosswalk = _load_json("output/data/source_claim_crosswalk.json")
    write_claim_context_ledger(PROJECT_ROOT, crosswalk)
    write_roadmap_governance_artifacts(PROJECT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
