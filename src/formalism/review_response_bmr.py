from __future__ import annotations

import math
from typing import Any

from modeling.registry import model_parameters

from formalism.models import BMRComparison, FreeEnergyTerms
from formalism.review_response_common import CLAIM_BOUNDARY, round_float


def bmr_comparison(prior_precision: float, metacognitive_access: float, family: str) -> BMRComparison:
    parameters = model_parameters("finite_bmr")
    retained_accuracy = parameters["accuracy_base"] + parameters["access_accuracy"] * metacognitive_access
    if family == "baseline_linear_sigma_complexity":
        sigma_accuracy_bonus = parameters["sigma_accuracy"] * (1.0 - metacognitive_access)
        full_complexity = parameters["complexity_base"] + prior_precision
    elif family == "log_compressed_sigma_complexity":
        sigma_accuracy_bonus = parameters["sigma_accuracy"] * (1.0 - metacognitive_access)
        full_complexity = parameters["complexity_base"] + math.log1p(prior_precision)
    elif family == "convex_access_dependent_sigma_accuracy":
        sigma_accuracy_bonus = parameters["sigma_accuracy"] * (1.0 - metacognitive_access) ** 2
        full_complexity = parameters["complexity_base"] + prior_precision
    else:
        raise ValueError(f"unknown BMR comparator family: {family}")
    full = FreeEnergyTerms(
        accuracy=retained_accuracy + sigma_accuracy_bonus,
        complexity=full_complexity,
        noise=parameters["noise_base"],
    )
    reduced = FreeEnergyTerms(
        accuracy=retained_accuracy,
        complexity=parameters["complexity_base"] + parameters["reduced_complexity"] * (1.0 - metacognitive_access),
        noise=parameters["noise_base"],
    )
    return BMRComparison(full_model=full, reduced_model=reduced)


def crossing_for_prior(rows: list[dict[str, Any]], precision: float) -> float | None:
    target_rows = sorted(
        [row for row in rows if abs(row["prior_precision"] - precision) < 1e-12],
        key=lambda row: row["metacognitive_access"],
    )
    for first, second in zip(target_rows, target_rows[1:], strict=False):
        first_value = float(first["delta_free_energy"])
        second_value = float(second["delta_free_energy"])
        if first_value == 0.0:
            return float(first["metacognitive_access"])
        if first_value * second_value <= 0:
            span = second["metacognitive_access"] - first["metacognitive_access"]
            ratio = abs(first_value) / (abs(first_value) + abs(second_value))
            return float(first["metacognitive_access"] + ratio * span)
    if target_rows and target_rows[0]["prunes_prior"]:
        return float(target_rows[0]["metacognitive_access"])
    return None


def build_bmr_alternative_prior_audit() -> dict[str, Any]:
    parameters = model_parameters("finite_alternative_bmr")
    access_grid = tuple(parameters["access_grid"])
    precision_grid = tuple(parameters["precision_grid"])
    families = (
        "baseline_linear_sigma_complexity",
        "log_compressed_sigma_complexity",
        "convex_access_dependent_sigma_accuracy",
    )
    rows = []
    for family in families:
        for access in access_grid:
            for precision in precision_grid:
                comparison = bmr_comparison(float(precision), float(access), family)
                rows.append(
                    {
                        "family": family,
                        "metacognitive_access": float(access),
                        "prior_precision": float(precision),
                        **comparison.as_dict(),
                        "verdict": "prune" if comparison.prunes_prior else "keep",
                    }
                )
    weakest_precision = min(float(value) for value in precision_grid)
    family_rows = {family: [row for row in rows if row["family"] == family] for family in families}
    crossings = {
        family: crossing_for_prior(family_rows[family], weakest_precision)
        for family in families
    }
    baseline_crossing = crossings["baseline_linear_sigma_complexity"]
    crossing_shifts = {
        family: None if baseline_crossing is None or crossing is None else round_float(abs(crossing - baseline_crossing))
        for family, crossing in crossings.items()
    }
    high_access_rows = [row for row in rows if row["metacognitive_access"] >= 0.75]
    controls = {
        "baseline_family_included": "baseline_linear_sigma_complexity" in family_rows,
        "log_compressed_family_included": "log_compressed_sigma_complexity" in family_rows,
        "convex_access_family_included": "convex_access_dependent_sigma_accuracy" in family_rows,
        "all_verdicts_measured": all(row["verdict"] in {"prune", "keep"} for row in rows),
        "high_access_pruning_remains_bounded": (
            bool(high_access_rows)
            and all(math.isfinite(float(row["delta_free_energy"])) and abs(float(row["delta_free_energy"])) < 10.0 for row in high_access_rows)
        ),
        "weakest_prior_crossings_measured": all(value is not None for value in crossings.values()),
        "at_least_one_crossing_shifts_vs_baseline": any(
            shift is not None and shift >= 0.05 for family, shift in crossing_shifts.items() if family != "baseline_linear_sigma_complexity"
        ),
        "claim_boundary_declares_not_empirical": "not empirical" in CLAIM_BOUNDARY,
    }
    return {
        "schema": "realizing_emptiness.bmr_alternative_prior_audit.v1",
        "families": list(families),
        "access_grid": list(access_grid),
        "precision_grid": list(precision_grid),
        "row_count": len(rows),
        "rows": rows,
        "weakest_prior": weakest_precision,
        "weakest_prior_crossings": crossings,
        "crossing_shifts_vs_baseline": crossing_shifts,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
