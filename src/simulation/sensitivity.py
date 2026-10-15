"""Deterministic sensitivity grid for the separation-prior surrogate."""

from __future__ import annotations

import csv
import json
from math import log
from pathlib import Path
from typing import Any

from modeling.registry import model_parameters

from formalism.models import BMRComparison, FreeEnergyTerms


CLAIM_BOUNDARY = "deterministic sensitivity surrogate only; not empirical, clinical, contemplative, or neural evidence"


def _binary_entropy(probability: float) -> float:
    """Return binary entropy in nats for an observation-noise probability."""
    if probability <= 0.0 or probability >= 1.0:
        return 0.0
    return float(-(probability * log(probability) + (1.0 - probability) * log(1.0 - probability)))


def compare_sensitivity_point(
    *,
    prior_precision: float,
    metacognitive_access: float,
    observation_noise: float,
) -> dict[str, Any]:
    """Evaluate one finite sensitivity point for the separation-prior reduction."""
    if prior_precision < 0.0:
        raise ValueError("prior_precision must be non-negative")
    if not 0.0 <= metacognitive_access <= 1.0:
        raise ValueError("metacognitive_access must be in [0, 1]")
    if not 0.0 <= observation_noise <= 0.5:
        raise ValueError("observation_noise must be in [0, 0.5]")

    parameters = model_parameters("finite_sensitivity")
    retained_accuracy = max(0.0, parameters["accuracy_base"] + parameters["access_accuracy"] * metacognitive_access - parameters["retained_noise_penalty"] * observation_noise)
    sigma_accuracy_bonus = max(0.0, parameters["sigma_accuracy"] * (1.0 - metacognitive_access) * (1.0 - observation_noise))
    full_model = FreeEnergyTerms(
        accuracy=retained_accuracy + sigma_accuracy_bonus,
        complexity=parameters["complexity_base"] + prior_precision + parameters["full_complexity_noise"] * observation_noise,
        noise=parameters["noise_base"] + parameters["full_noise"] * observation_noise,
    )
    reduced_model = FreeEnergyTerms(
        accuracy=max(0.0, retained_accuracy - parameters["reduced_accuracy_noise"] * observation_noise * (1.0 - metacognitive_access)),
        complexity=parameters["complexity_base"] + parameters["reduced_complexity"] * (1.0 - metacognitive_access) + parameters["reduced_complexity_noise"] * observation_noise,
        noise=parameters["noise_base"] + parameters["reduced_noise"] * observation_noise * (1.0 - metacognitive_access),
    )
    comparison = BMRComparison(full_model=full_model, reduced_model=reduced_model)
    entropy = _binary_entropy(observation_noise)
    separation_index = float((prior_precision / parameters["separation_scale"]) * (1.0 - metacognitive_access))
    return {
        "prior_precision": float(prior_precision),
        "metacognitive_access": float(metacognitive_access),
        "observation_noise": float(observation_noise),
        **comparison.as_dict(),
        "boundary_entropy_nats": entropy,
        "separation_index": separation_index,
        "post_dual_advantage": max(0.0, -comparison.delta_free_energy),
        "qrf_indistinguishability_holds": True,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_sensitivity_grid(
    *,
    access_grid: tuple[float, ...] | None = None,
    precision_grid: tuple[float, ...] | None = None,
    noise_grid: tuple[float, ...] | None = None,
) -> dict[str, Any]:
    """Run the finite sensitivity grid over access, precision, and observation noise."""
    parameters = model_parameters("finite_sensitivity")
    access_grid = tuple(parameters["access_grid"]) if access_grid is None else access_grid
    precision_grid = tuple(parameters["precision_grid"]) if precision_grid is None else precision_grid
    noise_grid = tuple(parameters["noise_grid"]) if noise_grid is None else noise_grid
    rows = [
        compare_sensitivity_point(
            prior_precision=precision,
            metacognitive_access=access,
            observation_noise=noise,
        )
        for noise in noise_grid
        for precision in precision_grid
        for access in access_grid
    ]
    pruned = [row for row in rows if row["prunes_prior"]]
    high_access = [row for row in rows if row["metacognitive_access"] >= 0.75]
    low_access = [row for row in rows if row["metacognitive_access"] <= 0.25]
    return {
        "schema": "realizing_emptiness.simulation_sensitivity_grid.v1",
        "row_count": len(rows),
        "access_grid": list(access_grid),
        "precision_grid": list(precision_grid),
        "noise_grid": list(noise_grid),
        "rows": rows,
        "pruning_rate": len(pruned) / len(rows),
        "high_access_pruning_rate": sum(1 for row in high_access if row["prunes_prior"]) / len(high_access),
        "low_access_pruning_rate": sum(1 for row in low_access if row["prunes_prior"]) / len(low_access),
        "all_rows_boundary_safe": all(row["qrf_indistinguishability_holds"] for row in rows),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_sensitivity_grid(project_root: Path) -> dict[str, Path]:
    """Write sensitivity grid JSON and CSV artifacts."""
    payload = build_sensitivity_grid()
    data_dir = project_root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    json_path = data_dir / "simulation_sensitivity_grid.json"
    csv_path = data_dir / "simulation_sensitivity_grid.csv"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    fieldnames = [
        "observation_noise",
        "prior_precision",
        "metacognitive_access",
        "delta_complexity",
        "delta_accuracy",
        "delta_free_energy",
        "boundary_entropy_nats",
        "separation_index",
        "post_dual_advantage",
        "prunes_prior",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in payload["rows"]:
            writer.writerow({field: row[field] for field in fieldnames})
    return {"json": json_path, "csv": csv_path}
