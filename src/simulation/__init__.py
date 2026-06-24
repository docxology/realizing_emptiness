"""Simulation and active-inference surrogate modules."""

from .bmr import run_bmr_sweep
from .criticality import build_criticality_report
from .pymdp_profiles import (
    build_pymdp_runtime_diagnostics_log,
    pymdp_runtime_dependency_check,
    pymdp_version_canary,
    run_profile_comparison,
)
from .qrf_env import boundary_indistinguishability_audit, default_deployments, simulate_boundary_trajectory

__all__ = [
    "boundary_indistinguishability_audit",
    "build_criticality_report",
    "build_pymdp_runtime_diagnostics_log",
    "default_deployments",
    "pymdp_runtime_dependency_check",
    "pymdp_version_canary",
    "run_bmr_sweep",
    "run_profile_comparison",
    "simulate_boundary_trajectory",
]
