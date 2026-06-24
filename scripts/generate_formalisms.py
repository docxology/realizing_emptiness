#!/usr/bin/env python3
"""Generate formalism registry, equation audit, source hash check, and claim crosswalk."""

from __future__ import annotations

import json

from _bootstrap import PROJECT_ROOT
from formalism.equations import evaluate_equation_surrogates, equation_registry
from formalism.governance import write_method_governance_artifacts
from formalism.manuscript import write_manuscript_claim_audit, write_manuscript_claim_intensity_audit
from formalism.scholarship import write_claim_support_audit, write_scholarship_source_matrix
from formalism.source import verify_primary_source_hash
from formalism.stress import write_evidence_ceiling_audit
from gates.contracts import write_artifact_contract_registry


def _claim_crosswalk() -> dict:
    claims = [
        {
            "id": "source_boundary_unevidenceable",
            "paper_locator": "Sections 3.1-3.2",
            "paraphrase": "The agent can model observations through a boundary but cannot evidence the boundary as ontologically separable.",
            "artifact": "output/data/qrf_boundary_indistinguishability.json",
            "gate": "qrf_indistinguishable",
            "claim_status": "operational_surrogate",
            "evidence_ceiling": "finite label-invariance audit only",
            "prohibited_inference": "Do not read this as proof that real agents lack selves or that a quantum boundary was simulated.",
            "future_evidence_required": "A full qFEP quantum-information implementation or empirical operationalization with source identity and negative controls.",
            "stressors": ["surrogate_scope", "source_role_boundary"],
        },
        {
            "id": "separation_prior_sigma",
            "paper_locator": "Equation 10",
            "paraphrase": "The separation prior restricts QRF deployments to a self/environment-preserving subspace.",
            "artifact": "output/data/formalism_registry.json",
            "gate": "equation_count_14",
            "claim_status": "implemented_model",
            "evidence_ceiling": "implemented finite data model",
            "prohibited_inference": "Do not read this as evidence that human subject-object boundaries have been reduced.",
            "future_evidence_required": "Task-linked data or formal proof showing when the modeled separation prior corresponds to an empirical or physical boundary.",
            "stressors": ["surrogate_scope"],
        },
        {
            "id": "bmr_prunes_sigma",
            "paper_locator": "Equation 12 and Section 4.3",
            "paraphrase": "When accuracy no longer depends on the separation prior, BMR favors the reduced model.",
            "artifact": "output/data/bmr_sweep.json",
            "gate": "bmr_pruning_edges",
            "claim_status": "finite_sweep",
            "evidence_ceiling": "deterministic parameter sweep, not empirical practice evidence",
            "prohibited_inference": "Do not read pruning in the sweep as evidence that meditation or realization removes self-models in people.",
            "future_evidence_required": "Pre-registered empirical or agent-benchmark evidence linking reduced complexity to task performance and subjective reports.",
            "stressors": ["surrogate_scope", "empirical_gap"],
        },
        {
            "id": "practice_protocol_boundary",
            "paper_locator": "Sections 4.2 and 6.2",
            "paraphrase": "Practice-facing language is represented as model interventions, not evidence for realization or treatment.",
            "artifact": "output/data/practice_protocol_map.json",
            "gate": "practice_boundaries",
            "claim_status": "safety_boundary",
            "evidence_ceiling": "protocol specification only",
            "prohibited_inference": "Do not read protocol mappings as instructions, therapy, or evidence that a practice induces realization.",
            "future_evidence_required": "Human review, ethics constraints, safety language, and outcome-independent usability validation before user-facing deployment.",
            "stressors": ["practice_boundary", "source_role_boundary"],
        },
        {
            "id": "qfep_surrogate_scope",
            "paper_locator": "Section 2",
            "paraphrase": "The qFEP is represented here by finite operational surrogates, source mappings, direct two-qubit tests for separability entropy, mixed-state PPT/negativity controls, CHSH contextuality, generic measurement-cover polytope checks, finite CPTP channel-cost accounting, dephasing controls, seeded quantum-trajectory unraveling, and implemented extension engines for boundary-Hamiltonian Lindblad dynamics, sparse many-body cuts, sheaf obstruction, QRF relabeling and frame covariance, and fail-closed empirical provenance.",
            "artifact": "output/data/quantum_extension_roadmap.json",
            "gate": "quantum_extension_roadmap_ok",
            "claim_status": "formal_boundary",
            "evidence_ceiling": "finite equation registry plus two-qubit quantum-information witnesses, mixed-state entanglement checks, measurement-cover/local-polytope controls, channel-cost accounting, dephasing controls, stochastic quantum-trajectory checks, and implemented extension-engine audits",
            "prohibited_inference": "Do not read finite entropy, mixed-state entanglement, CHSH, measurement-cover/local-polytope, channel-cost, dephasing, Lindblad, many-body, sheaf, QRF-covariance, or provenance controls as physical qFEP realization, empirical practice evidence, or neural measurement.",
            "future_evidence_required": "A separately reviewed physical qFEP implementation, independent quantum-information replication, or ethics-reviewed human/practice dataset depending on the stronger claim.",
            "stressors": ["surrogate_scope", "quantum_gap"],
        },
        {
            "id": "quantum_separability_entropy",
            "paper_locator": "Equation 2 and Section 2.1",
            "paraphrase": "The separability-entropy premise is directly simulated for a finite two-qubit Schmidt-family sweep using reduced density matrices and von Neumann entropy.",
            "artifact": "output/data/quantum_boundary_entropy.json",
            "gate": "quantum_boundary_entropy_ok",
            "claim_status": "finite_quantum_simulation",
            "evidence_ceiling": "finite two-qubit pure-state entropy witness",
            "prohibited_inference": "Do not read this finite witness as a simulation of a universe-agent boundary or mixed open-system qFEP dynamics.",
            "future_evidence_required": "Higher-dimensional, multipartite, externally reviewed many-body, and physical open-system extensions with independent benchmarks and negative controls.",
            "stressors": ["quantum_gap", "surrogate_scope"],
        },
        {
            "id": "quantum_contextuality_witness",
            "paper_locator": "QRF/contextuality background for Sections 2-3",
            "paraphrase": "Quantum contextuality is operationalized as a finite CHSH witness over the same two-qubit family, with product-state and Tsirelson-bound controls.",
            "artifact": "output/data/quantum_boundary_entropy.json",
            "gate": "quantum_contextuality_witness_ok",
            "claim_status": "finite_quantum_simulation",
            "evidence_ceiling": "CHSH witness over a finite two-qubit family",
            "prohibited_inference": "Do not read the CHSH witness as a general contextuality proof for all QRF deployments or as empirical evidence.",
            "future_evidence_required": "General sheaf-obstruction checks, noncontextual polytope comparisons, and explicit QRF transformation tests.",
            "stressors": ["quantum_gap", "surrogate_scope", "source_role_boundary"],
        },
        {
            "id": "quantum_measurement_contextuality",
            "paper_locator": "QRF/contextuality background for Sections 2-3",
            "paraphrase": "The CHSH contextuality extension is also represented as a finite measurement-cover empirical model with normalized joint probabilities, no-signaling controls, a product negative control, a Tsirelson-bound check, and a local-hidden-variable polytope feasibility audit over 16 deterministic assignments.",
            "artifact": "output/data/quantum_measurement_contextuality.json",
            "gate": "quantum_measurement_contextuality_ok",
            "claim_status": "finite_quantum_simulation",
            "evidence_ceiling": "finite CHSH measurement-cover probability table plus local-polytope LP audit",
            "prohibited_inference": "Do not read the CHSH table or local-polytope infeasibility as a full sheaf obstruction proof, a many-body QRF transformation, a qFEP dynamics simulation, or empirical evidence.",
            "future_evidence_required": "A general measurement-scenario engine with compatibility hypergraphs, obstruction or noncontextual-polytope witnesses, and QRF transformation tests.",
            "stressors": ["quantum_gap", "surrogate_scope", "source_role_boundary"],
        },
        {
            "id": "quantum_open_system_dephasing",
            "paper_locator": "Section 2.1 and open-system qFEP background",
            "paraphrase": "Open-system quantum behavior is simulated as a finite two-qubit dephasing channel with trace, positivity, entropy, mutual-information, and CHSH-decay controls.",
            "artifact": "output/data/quantum_open_system_dynamics.json",
            "gate": "quantum_open_system_dynamics_ok",
            "claim_status": "finite_quantum_simulation",
            "evidence_ceiling": "finite trace-preserving two-qubit dephasing-channel simulation",
            "prohibited_inference": "Do not read the dephasing channel as the paper's full qFEP dynamics, a many-body observer boundary, or empirical quantum evidence.",
            "future_evidence_required": "Boundary-Hamiltonian-linked Lindblad or collision-model dynamics, many-body subsystem cuts, and explicit QRF transformations.",
            "stressors": ["quantum_gap", "surrogate_scope", "source_role_boundary"],
        },
        {
            "id": "pymdp_runtime_canary",
            "paper_locator": "Software implementation layer",
            "paraphrase": "The active-inference runtime dependency check uses the pinned pymdp package and records a normalized policy posterior.",
            "artifact": "output/data/pymdp_profile_comparison.json",
            "gate": "pymdp_canary",
            "claim_status": "runtime_canary",
            "evidence_ceiling": "package import, agent construction, state inference, and policy-posterior normalization diagnostics",
            "prohibited_inference": "Do not read the runtime dependency check as a benchmark of active-inference optimality or scientific validity.",
            "future_evidence_required": "Version-pinned benchmark suites and comparison agents if performance or optimality claims are introduced.",
            "stressors": ["runtime_dependency"],
        },
        {
            "id": "criticality_proxy_boundary",
            "paper_locator": "Section 6.3",
            "paraphrase": "Criticality-style outputs are seeded stochastic trajectory summaries with null controls that structure future empirical work but are not neural measurements.",
            "artifact": "output/data/criticality_stochastic_ensemble.json",
            "gate": "criticality_stochastic_ensemble_ok",
            "claim_status": "proxy_boundary",
            "evidence_ceiling": "seeded stochastic simulation ensemble only",
            "prohibited_inference": "Do not read the simulated ensemble as a measured neural criticality regime or a biomarker of realization.",
            "future_evidence_required": "Neural data provenance, preprocessing records, null models, and negative controls before any neural-criticality claim.",
            "stressors": ["empirical_gap", "neural_measurement_boundary"],
        },
        {
            "id": "compassion_proxy_boundary",
            "paper_locator": "Section 6.2",
            "paraphrase": "The compassion proxy is a modeled widening of policy scope, not a moral, clinical, or contemplative attainment metric.",
            "artifact": "output/data/practice_protocol_map.json",
            "gate": "practice_boundaries",
            "claim_status": "proxy_boundary",
            "evidence_ceiling": "model-scope proxy only",
            "prohibited_inference": "Do not read broadened model scope as moral virtue, compassion, clinical improvement, or contemplative attainment.",
            "future_evidence_required": "Independent human-subject measures and normative review before any compassion or wellbeing claim.",
            "stressors": ["practice_boundary", "normative_boundary"],
        },
        {
            "id": "self_evidencing_boundary",
            "paper_locator": "Introduction and Section 1",
            "paraphrase": "Self-evidencing is treated as the background contrast class for no-self-evidence, not as an empirical result produced by this simulation.",
            "artifact": "output/data/source_claim_crosswalk.json",
            "gate": "claim_support_audit_ok",
            "claim_status": "background_boundary",
            "evidence_ceiling": "source-role binding only",
            "prohibited_inference": "Do not read background self-evidencing scholarship as a new empirical result produced by this repository.",
            "future_evidence_required": "A separate empirical or formal target with its own source ledger if self-evidencing is tested directly.",
            "stressors": ["source_role_boundary", "empirical_gap"],
        },
        {
            "id": "metacognitive_access_model",
            "paper_locator": "Sections 4.2-4.3",
            "paraphrase": "Metacognitive access is modeled as a sweep parameter controlling when the separation prior becomes dispensable.",
            "artifact": "output/data/simulation_sensitivity_grid.json",
            "gate": "simulation_sensitivity_grid_ok",
            "claim_status": "implementation_boundary",
            "evidence_ceiling": "parameterized sensitivity surrogate only",
            "prohibited_inference": "Do not read the sweep parameter as a measured metacognitive trait or training outcome.",
            "future_evidence_required": "Validated operational measures and task data if metacognitive access is tied to people or empirical agents.",
            "stressors": ["surrogate_scope", "empirical_gap"],
        },
        {
            "id": "artifact_release_readiness",
            "paper_locator": "Software artifact release package",
            "paraphrase": "The local artifact bundle is hashed, schema-registered, and command-accounted for private release-readiness review.",
            "artifact": "output/data/artifact_release_manifest.json",
            "gate": "artifact_release_manifest_ok",
            "claim_status": "implementation_boundary",
            "evidence_ceiling": "local private artifact package only, not public independent reproduction",
            "prohibited_inference": "Do not read local hashes, manifests, or validation commands as a public archive release, independent reproduction, empirical validation, or publication.",
            "future_evidence_required": "Explicit publication approval, public archive deposition, independent or blinded reproduction, and external reviewer execution before any public-release or independent-reproduction claim.",
            "stressors": ["source_role_boundary", "empirical_gap"],
        },
    ]
    return {
        "schema": "realizing_emptiness.source_claim_crosswalk.v1",
        "claims": claims,
        "claim_count": len(claims),
        "all_claims_have_gates": all(row["gate"] for row in claims),
    }


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
    (data_dir / "source_claim_crosswalk.json").write_text(
        json.dumps(_claim_crosswalk(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    crosswalk = _claim_crosswalk()
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
