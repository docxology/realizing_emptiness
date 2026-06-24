"""Method-governance ledgers for finite formal simulations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CLAIM_BOUNDARY = (
    "method governance ledger for finite software artifacts; not empirical, clinical, neural, "
    "practice-efficacy, awakening, or physical qFEP evidence"
)


METHOD_ROWS: tuple[dict[str, Any], ...] = (
    {
        "method_id": "finite_qrf_boundary_screen",
        "artifact": "output/data/qrf_boundary_indistinguishability.json",
        "hard_constraints": ["probability mass must normalize", "admissible relabelings must preserve the observed bitstream"],
        "modeling_choices": ["six-channel finite screen", "sector labels treated as semantic relabelings"],
        "assumptions": ["finite channel screen is an inspectable surrogate for the source paper's boundary role"],
        "evidence_ceiling": "finite QRF label-invariance audit only",
        "falsification_controls": ["perturbed label/mass negative control fails"],
    },
    {
        "method_id": "bmr_separation_prior_sweep",
        "artifact": "output/data/bmr_sweep.json",
        "hard_constraints": ["Delta F sign convention must be fixed", "prune means F_reduced - F_full < 0"],
        "modeling_choices": ["prior precision and metacognitive access grid", "accuracy and complexity decomposed finitely"],
        "assumptions": ["grid parameters are software surrogates, not measured traits"],
        "evidence_ceiling": "finite model comparison only",
        "falsification_controls": ["edge cases test keep/prune sign", "sensitivity grid tests observation-noise robustness"],
    },
    {
        "method_id": "pymdp_active_inference_profiles",
        "artifact": "output/data/pymdp_policy_trace.json",
        "hard_constraints": [
            "A/B/C/D arrays must normalize",
            "state and policy posteriors must normalize at every step",
            "runtime dependency check is limited to pinned package, import, agent construction, state inference, and policy-posterior normalization",
        ],
        "modeling_choices": [
            "three-state QRF profile model",
            "finite expected-free-energy proxy terms",
            "profile-specific priors, preferences, and transition relaxation drive action differences",
        ],
        "assumptions": [
            "profile differences are software hypotheses about QRF deployments",
            "the runtime dependency check does not certify active-inference optimality, human behavior, or scientific validity",
        ],
        "evidence_ceiling": "discrete active-inference surrogate only",
        "falsification_controls": [
            "runtime dependency check",
            "posterior normalization",
            "expected-free-energy recomputation",
            "profile-specific action differences",
        ],
    },
    {
        "method_id": "seeded_stochastic_policy_ensemble",
        "artifact": "output/data/stochastic_policy_ensemble.json",
        "hard_constraints": ["random draws must sample normalized distributions", "replay with same seed must reproduce rows"],
        "modeling_choices": ["64 runs per profile", "null-control action and observation sampling"],
        "assumptions": ["stochastic variability tests software robustness, not human variability"],
        "evidence_ceiling": "seeded simulation ensemble only",
        "falsification_controls": ["same-seed replay", "different seed changes sampled rows", "null-control contrasts"],
    },
    {
        "method_id": "quantum_trajectory_unraveling",
        "artifact": "output/data/quantum_trajectory_unraveling.json",
        "hard_constraints": ["state vectors preserve norm", "ensemble density preserves trace and PSD", "gamma-zero has no jumps"],
        "modeling_choices": ["finite two-qubit Lindblad surrogate", "Monte Carlo wave-function jump/no-jump paths"],
        "assumptions": ["two-qubit open-system dynamics are a finite method witness, not physical qFEP"],
        "evidence_ceiling": "finite stochastic quantum surrogate only",
        "falsification_controls": ["exact-Lindblad residual tolerance", "invalid operator/rate rejection", "trajectory-count convergence"],
    },
    {
        "method_id": "contextuality_and_measurement_cover_engines",
        "artifact": "output/data/general_measurement_cover_polytope_audit.json",
        "hard_constraints": ["context distributions must normalize", "global-section LP feasibility must match controls"],
        "modeling_choices": ["finite compatibility scenarios", "deterministic-assignment linear programs"],
        "assumptions": ["finite obstruction cases do not prove the source paper's full QRF contextuality"],
        "evidence_ceiling": "finite contextuality software audit only",
        "falsification_controls": ["feasible triangle/product controls", "parity and Bell obstruction cases"],
    },
    {
        "method_id": "practice_protocol_adapter",
        "artifact": "output/data/practice_protocol_map.json",
        "hard_constraints": ["no user-facing efficacy claims", "protocols must map to model interventions only"],
        "modeling_choices": ["practice language represented as bounded interface specs"],
        "assumptions": ["practice vocabulary can guide future UI without implying outcomes"],
        "evidence_ceiling": "protocol specification only",
        "falsification_controls": ["claim language blocks therapeutic, awakening, clinical, and neural claims"],
    },
    {
        "method_id": "visual_and_claim_governance",
        "artifact": "output/data/figure_source_map.json",
        "hard_constraints": ["figures need source artifacts", "claim-bearing captions need boundary language"],
        "modeling_choices": ["static publication figures", "machine-readable source maps and visual contracts"],
        "assumptions": ["metadata plus render checks reduce false certification but do not prove reader comprehension"],
        "evidence_ceiling": "documentation and visualization QA only",
        "falsification_controls": ["caption/accessibility/style/legibility audits", "supplement figure reuse audit"],
    },
)


def build_method_assumption_ledger() -> dict[str, Any]:
    """Return the method assumption ledger."""
    rows = [dict(row) for row in METHOD_ROWS]
    return {
        "schema": "realizing_emptiness.method_assumption_ledger.v1",
        "method_count": len(rows),
        "rows": rows,
        "all_methods_have_hard_constraints": all(row["hard_constraints"] for row in rows),
        "all_methods_have_assumptions": all(row["assumptions"] for row in rows),
        "all_methods_have_evidence_ceiling": all(row["evidence_ceiling"] for row in rows),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_method_negative_control_inventory() -> dict[str, Any]:
    """Return method-to-negative-control coverage rows."""
    rows = []
    for method in METHOD_ROWS:
        for control in method["falsification_controls"]:
            rows.append(
                {
                    "method_id": method["method_id"],
                    "artifact": method["artifact"],
                    "negative_control": control,
                    "evidence_ceiling": method["evidence_ceiling"],
                }
            )
    return {
        "schema": "realizing_emptiness.method_negative_control_inventory.v1",
        "method_count": len(METHOD_ROWS),
        "control_count": len(rows),
        "rows": rows,
        "all_methods_have_controls": {method["method_id"] for method in METHOD_ROWS}
        <= {row["method_id"] for row in rows},
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_method_governance_artifacts(project_root: Path) -> tuple[Path, Path]:
    """Write method governance JSON artifacts."""
    data_dir = project_root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = data_dir / "method_assumption_ledger.json"
    controls_path = data_dir / "method_negative_control_inventory.json"
    ledger_path.write_text(json.dumps(build_method_assumption_ledger(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    controls_path.write_text(
        json.dumps(build_method_negative_control_inventory(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return ledger_path, controls_path
