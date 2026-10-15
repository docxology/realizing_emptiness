"""Bayesian model-reduction sweeps for the separation prior."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from modeling.registry import model_parameters

from formalism.models import BMRComparison, FreeEnergyTerms


CLAIM_BOUNDARY = "finite Bayesian model-reduction sweep over software priors; not empirical, clinical, neural, awakening, practice-efficacy, or physical qFEP evidence"


def compare_models(prior_precision: float, metacognitive_access: float) -> BMRComparison:
    """Compare full and reduced models at one point in the finite sweep."""
    parameters = model_parameters("finite_bmr")
    retained_accuracy = parameters["accuracy_base"] + parameters["access_accuracy"] * metacognitive_access
    sigma_accuracy_bonus = parameters["sigma_accuracy"] * (1.0 - metacognitive_access)
    full = FreeEnergyTerms(
        accuracy=retained_accuracy + sigma_accuracy_bonus,
        complexity=parameters["complexity_base"] + prior_precision,
        noise=parameters["noise_base"],
    )
    reduced = FreeEnergyTerms(
        accuracy=retained_accuracy,
        complexity=parameters["complexity_base"] + parameters["reduced_complexity"] * (1.0 - metacognitive_access),
        noise=parameters["noise_base"],
    )
    return BMRComparison(full_model=full, reduced_model=reduced)


def run_bmr_sweep(
    *,
    access_grid: tuple[float, ...] | None = None,
    precision_grid: tuple[float, ...] | None = None,
) -> dict[str, Any]:
    """Run deterministic BMR sweep over prior precision and metacognitive access."""
    parameters = model_parameters("finite_bmr")
    access_grid = tuple(parameters["access_grid"]) if access_grid is None else access_grid
    precision_grid = tuple(parameters["precision_grid"]) if precision_grid is None else precision_grid
    rows = []
    for access in access_grid:
        for precision in precision_grid:
            comparison = compare_models(precision, access)
            rows.append(
                {
                    "metacognitive_access": access,
                    "prior_precision": precision,
                    **comparison.as_dict(),
                }
            )
    return {
        "schema": "realizing_emptiness.bmr_sweep.v1",
        "row_count": len(rows),
        "rows": rows,
        "any_pruning": any(row["prunes_prior"] for row in rows),
        "high_access_prunes": all(row["prunes_prior"] for row in rows if row["metacognitive_access"] >= 0.75),
        "low_access_not_all_pruned": not all(row["prunes_prior"] for row in rows if row["metacognitive_access"] == 0.0),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_bmr_sweep(project_root: Path) -> dict[str, Path]:
    """Write BMR sweep JSON and CSV artifacts."""
    payload = run_bmr_sweep()
    data_dir = project_root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    json_path = data_dir / "bmr_sweep.json"
    csv_path = data_dir / "bmr_sweep.csv"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fieldnames = [
        "metacognitive_access",
        "prior_precision",
        "delta_complexity",
        "delta_accuracy",
        "delta_free_energy",
        "prunes_prior",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in payload["rows"]:
            writer.writerow({field: row[field] for field in fieldnames})
    return {"json": json_path, "csv": csv_path}
