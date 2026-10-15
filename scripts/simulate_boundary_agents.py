#!/usr/bin/env python3
"""Generate QRF boundary audit and active-inference profile comparison."""

from __future__ import annotations

import json

from _bootstrap import PROJECT_ROOT
from modeling.registry import model_parameters
from formalism.models import BoundaryScreen
from simulation.pymdp_profiles import (
    build_generative_model_audit,
    build_pymdp_runtime_diagnostics_log,
    run_policy_trace,
    run_profile_comparison,
)
from simulation.compassion_scope import build_compassion_scope_audit
from simulation.qrf_env import (
    boundary_channel_ledger,
    boundary_indistinguishability_audit,
    default_deployments,
)
from simulation.stochastic import build_stochastic_policy_ensemble


def main() -> int:
    cfg = model_parameters("qrf_boundary")
    data_dir = PROJECT_ROOT / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    channels = int(cfg["channels"])
    screen = BoundaryScreen.default(channels)
    audit = boundary_indistinguishability_audit(default_deployments(channels), screen)
    ledger = boundary_channel_ledger(default_deployments(channels), screen)
    profile = run_profile_comparison(seed=int(cfg["seed"]), steps=int(cfg["steps"]), channels=channels)
    policy_trace = run_policy_trace(seed=int(cfg["seed"]), steps=int(cfg["steps"]), channels=channels)
    stochastic = build_stochastic_policy_ensemble(
        seed=int(cfg["seed"]) + cfg["stochastic_seed_offset"],
        channels=channels,
    )
    model_audit = build_generative_model_audit(channels=channels)
    runtime_log = build_pymdp_runtime_diagnostics_log(seed=int(cfg["seed"]), steps=int(cfg["steps"]), channels=channels)
    compassion_scope = build_compassion_scope_audit(default_deployments(channels), seed=int(cfg["seed"]) + cfg["compassion_seed_offset"])
    (data_dir / "qrf_boundary_indistinguishability.json").write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "qrf_boundary_channel_ledger.json").write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "pymdp_profile_comparison.json").write_text(
        json.dumps(profile, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "pymdp_policy_trace.json").write_text(
        json.dumps(policy_trace, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "pymdp_generative_model_audit.json").write_text(
        json.dumps(model_audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "pymdp_runtime_diagnostics_log.json").write_text(
        json.dumps(runtime_log, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "stochastic_policy_ensemble.json").write_text(
        json.dumps(stochastic, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (data_dir / "compassion_scope_audit.json").write_text(
        json.dumps(compassion_scope, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
