"""Manuscript variable aggregation and hydration."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from gates.validation import validate_outputs

TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def _load_json(project_root: Path, relative: str) -> dict:
    return json.loads((project_root / relative).read_text(encoding="utf-8"))


def compute_variables(project_root: Path) -> dict:
    checks = validate_outputs(project_root)
    equation = _load_json(project_root, "output/data/equation_audit.json")
    bmr = _load_json(project_root, "output/data/bmr_sweep.json")
    sensitivity = _load_json(project_root, "output/data/simulation_sensitivity_grid.json")
    profile = _load_json(project_root, "output/data/pymdp_profile_comparison.json")
    stochastic = _load_json(project_root, "output/data/stochastic_policy_ensemble.json")
    quantum_entropy = _load_json(project_root, "output/data/quantum_boundary_entropy.json")
    trajectory = _load_json(project_root, "output/data/quantum_trajectory_convergence_audit.json")
    validation_pass = sum(1 for value in checks.values() if value)
    return {
        "EQUATION_COUNT": equation["equation_count"],
        "IMPLEMENTED_EQUATION_COUNT": equation["implemented_count"],
        "BMR_ROW_COUNT": bmr["row_count"],
        "SENSITIVITY_ROW_COUNT": sensitivity["row_count"],
        "BEST_PROFILE": profile["best_profile"],
        "PYMDP_VERSION": profile["pymdp_canary"]["version"],
        "STOCHASTIC_RUNS_PER_PROFILE": stochastic["runs_per_profile"],
        "STOCHASTIC_STEPS": stochastic["steps"],
        "STOCHASTIC_ROW_COUNT": stochastic["row_count"],
        "QUANTUM_ENTROPY_ROW_COUNT": quantum_entropy["row_count"],
        "QUANTUM_BASIS_ROW_COUNT": quantum_entropy["basis_invariance_row_count"],
        "QUANTUM_TRAJECTORY_MAX_COUNT": max(trajectory["trajectory_counts"]),
        "VALIDATION_PASS_COUNT": validation_pass,
        "VALIDATION_TOTAL_COUNT": len(checks),
    }


def hydrate_manuscript(project_root: Path, variables: dict) -> None:
    source = project_root / "docs" / "manuscript"
    target = project_root / "output" / "manuscript"
    target.mkdir(parents=True, exist_ok=True)
    for stale in target.glob("*"):
        if stale.is_file():
            stale.unlink()
    for path in sorted(source.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        def replace(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in variables:
                raise KeyError(f"unknown manuscript variable {key}")
            return str(variables[key])
        (target / path.name).write_text(TOKEN_RE.sub(replace, text), encoding="utf-8")
    for aux in ("config.yaml", "preamble.md", "references.bib"):
        src = source / aux
        if src.exists():
            shutil.copy2(src, target / aux)
