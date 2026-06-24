"""Bayesian model-reduction sweeps for the separation prior."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from formalism.models import BMRComparison, FreeEnergyTerms


CLAIM_BOUNDARY = "finite Bayesian model-reduction sweep over software priors; not empirical, clinical, neural, awakening, practice-efficacy, or physical qFEP evidence"


def compare_models(prior_precision: float, metacognitive_access: float) -> BMRComparison:
    """Compare full and reduced models at one point in the finite sweep."""
    retained_accuracy = 0.55 + 0.35 * metacognitive_access
    sigma_accuracy_bonus = 0.30 * (1.0 - metacognitive_access)
    full = FreeEnergyTerms(
        accuracy=retained_accuracy + sigma_accuracy_bonus,
        complexity=0.25 + prior_precision,
        noise=0.02,
    )
    reduced = FreeEnergyTerms(
        accuracy=retained_accuracy,
        complexity=0.25 + 0.15 * (1.0 - metacognitive_access),
        noise=0.02,
    )
    return BMRComparison(full_model=full, reduced_model=reduced)


def run_bmr_sweep(
    *,
    access_grid: tuple[float, ...] = (0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0),
    precision_grid: tuple[float, ...] = (0.2, 0.5, 1.0, 2.0, 4.0),
) -> dict[str, Any]:
    """Run deterministic BMR sweep over prior precision and metacognitive access."""
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
