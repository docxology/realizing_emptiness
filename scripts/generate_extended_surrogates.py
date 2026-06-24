#!/usr/bin/env python3
"""Generate the extended source-fidelity surrogates (paper sections 3.3, 4.1, 5.3, 6.1).

Thin orchestrator: builds the finite extended surrogates and writes their JSON artifacts.
"""

from __future__ import annotations

import json

from _bootstrap import PROJECT_ROOT
from simulation.emergence import build_ongoing_revision_audit, build_separation_prior_emergence_audit
from simulation.blackwell_ordering import build_blackwell_bayes_risk_audit
from simulation.classical_data_processing import build_classical_data_processing_audit
from simulation.interaction_information import build_interaction_information_boundary_audit
from simulation.markov_blanket import build_markov_blanket_discovery_audit
from simulation.quantum_estimation import build_quantum_cramer_rao_estimation_audit
from simulation.quantum_surrogates import (
    build_collision_model_thermalization_audit,
    build_data_processing_monotonicity_audit,
    build_internal_cut_unmeasurability_audit,
    build_multipartite_witness_suite_audit,
    build_n_cycle_contextuality_library_audit,
    build_no_signaling_scenario_library_audit,
    build_sigma_contextuality_suppression_audit,
    build_tensor_network_benchmark_audit,
)


def main() -> int:
    data_dir = PROJECT_ROOT / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "separation_prior_emergence_audit.json": build_separation_prior_emergence_audit(),
        "internal_cut_unmeasurability_audit.json": build_internal_cut_unmeasurability_audit(),
        "sigma_contextuality_suppression_audit.json": build_sigma_contextuality_suppression_audit(),
        "ongoing_revision_audit.json": build_ongoing_revision_audit(),
        "multipartite_witness_suite_audit.json": build_multipartite_witness_suite_audit(),
        "tensor_network_benchmark_audit.json": build_tensor_network_benchmark_audit(),
        "collision_model_thermalization_audit.json": build_collision_model_thermalization_audit(),
        "no_signaling_scenario_library_audit.json": build_no_signaling_scenario_library_audit(),
        "n_cycle_contextuality_library_audit.json": build_n_cycle_contextuality_library_audit(),
        "data_processing_monotonicity_audit.json": build_data_processing_monotonicity_audit(),
        "markov_blanket_discovery_audit.json": build_markov_blanket_discovery_audit(),
        "quantum_cramer_rao_estimation_audit.json": build_quantum_cramer_rao_estimation_audit(),
        "interaction_information_boundary_audit.json": build_interaction_information_boundary_audit(),
        "blackwell_bayes_risk_audit.json": build_blackwell_bayes_risk_audit(),
        "classical_data_processing_audit.json": build_classical_data_processing_audit(),
    }
    for filename, payload in artifacts.items():
        (data_dir / filename).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
