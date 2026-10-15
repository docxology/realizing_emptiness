"""Statistical robustness audits for finite software simulations."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from simulation.quantum_surrogates import build_quantum_trajectory_unraveling
from simulation.resampling import bootstrap_contrast, permutation_test, binomial_summary


CLAIM_BOUNDARY = (
    "statistical robustness over finite seeded software simulations; not empirical data, "
    "not neural measurement, not clinical evidence, and not a physical qFEP realization"
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _finite(values: list[float] | np.ndarray) -> bool:
    return bool(np.all(np.isfinite(np.asarray(values, dtype=float))))


def _bootstrap_ci(
    values: list[float], *, seed: int, draws: int = 1024
) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    if len(array) == 0:
        raise ValueError("bootstrap requires at least one value")
    rng = np.random.default_rng(seed)
    boot = np.empty(draws, dtype=float)
    for index in range(draws):
        sample = rng.choice(array, size=len(array), replace=True)
        boot[index] = float(np.mean(sample))
    return {
        "mean": float(np.mean(array)),
        "median": float(np.median(array)),
        "ci95_low": float(np.quantile(boot, 0.025)),
        "ci95_high": float(np.quantile(boot, 0.975)),
    }


def _holm_adjust(p_values: list[float]) -> list[float]:
    indexed = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [0.0] * len(p_values)
    running = 0.0
    total = len(p_values)
    for rank, (original_index, p_value) in enumerate(indexed):
        value = min(1.0, (total - rank) * p_value)
        running = max(running, value)
        adjusted[original_index] = running
    return adjusted


def build_stochastic_effect_size_audit(stochastic: dict[str, Any]) -> dict[str, Any]:
    """Compare profile ensembles to null controls with deterministic resampling."""
    metric_names = [
        "observation_entropy_nats",
        "action_entropy_nats",
        "switch_rate",
        "autocorrelation_lag1",
        "mean_weighted_expected_free_energy",
        "mean_surprise",
    ]
    grouped: dict[tuple[str, bool], list[dict[str, Any]]] = defaultdict(list)
    for row in stochastic.get("run_summaries", []):
        grouped[(row["profile"], bool(row["null_control"]))].append(row)
    rows = []
    p_values = []
    family_size = len({profile for profile, _ in grouped}) * len(metric_names)
    for profile in sorted({profile for profile, _ in grouped}):
        for metric_index, metric in enumerate(metric_names):
            profile_values = [float(row[metric]) for row in grouped[(profile, False)]]
            null_values = [float(row[metric]) for row in grouped[(profile, True)]]
            observed_delta = float(np.mean(profile_values) - np.mean(null_values))
            contrast = bootstrap_contrast(profile_values, null_values, seed=7400 + len(rows))
            permutation = permutation_test(
                profile_values, null_values, seed=7300 + 17 * metric_index + len(rows),
                confidence=1 - 0.05 / family_size,
            )
            p_value = float(permutation["p_value"])
            p_values.append(p_value)
            rows.append(
                {
                    "profile": profile,
                    "metric": metric,
                    "profile_mean": float(np.mean(profile_values)),
                    "null_mean": float(np.mean(null_values)),
                    "delta_profile_minus_null": observed_delta,
                    "cliffs_delta": contrast["cliffs_delta"],
                    "permutation_p": p_value,
                    "difference_ci95_low": contrast["difference_ci95_low"],
                    "difference_ci95_high": contrast["difference_ci95_high"],
                    "cliffs_ci95_low": contrast["cliffs_ci95_low"],
                    "cliffs_ci95_high": contrast["cliffs_ci95_high"],
                    "profile_run_count": len(profile_values), "null_run_count": len(null_values),
                    "bootstrap_seed": 7400 + len(rows), "bootstrap_draws": 2048,
                    "permutation_seed": 7300 + 17 * metric_index + len(rows),
                    "permutation_draws": permutation["draws"],
                    "permutation_exceedances": permutation["exceedances"],
                    "permutation_resolution": permutation["resolution"],
                    "permutation_mcse": permutation["mcse"],
                    "permutation_tail_family_ci95_low": permutation["tail_ci_low"],
                    "permutation_tail_family_ci95_high": permutation["tail_ci_high"],
                    "permutation_tail_confidence_level": permutation["tail_confidence_level"],
                }
            )
    adjusted = _holm_adjust(p_values)
    lower_adjusted = _holm_adjust([row["permutation_tail_family_ci95_low"] for row in rows])
    upper_adjusted = _holm_adjust([row["permutation_tail_family_ci95_high"] for row in rows])
    for row, p_adjusted, low, high in zip(rows, adjusted, lower_adjusted, upper_adjusted, strict=True):
        row["holm_p"] = p_adjusted
        row["holm_mc_ci95_low"], row["holm_mc_ci95_high"] = low, high
        row["holm_decision_mc_stable"] = bool(high < 0.05 or low >= 0.05)
        row["finite_interval"] = _finite(
            [
                row["profile_mean"],
                row["null_mean"],
                row["cliffs_delta"],
                row["permutation_p"],
                row["holm_p"],
                row["difference_ci95_low"], row["difference_ci95_high"],
                row["cliffs_ci95_low"], row["cliffs_ci95_high"], low, high,
            ]
        )
        row["effect_direction"] = (
            "profile_higher" if row["delta_profile_minus_null"] > 0 else
            "null_higher" if row["delta_profile_minus_null"] < 0 else "equal"
        )
    controls = {
        "all_intervals_finite": all(row["finite_interval"] for row in rows),
        "all_p_values_bounded": all(
            0.0 <= row["permutation_p"] <= 1.0 and 0.0 <= row["holm_p"] <= 1.0
            for row in rows
        ),
        "has_nonzero_effects": any(abs(row["cliffs_delta"]) > 0.1 for row in rows),
        "seeded_resampling_declared": True,
        "intervals_match_estimands": all(-1 <= row["cliffs_ci95_low"] <= row["cliffs_ci95_high"] <= 1
                                        and row["difference_ci95_low"] <= row["difference_ci95_high"] for row in rows),
    }
    return {
        "schema": "realizing_emptiness.stochastic_effect_size_audit.v2",
        "metric_count": len(metric_names),
        "row_count": len(rows),
        "rows": rows,
        "resampling_design": {"unit": "independent_trajectory_run", "bootstrap_method": "percentile",
                              "interval_confidence": 0.95, "intervals_simultaneous": False,
                              "null": "independent_uniform_observation_action_runs",
                              "permutation_family_size": len(rows), "mc_family_confidence": 0.95,
                              "mc_interval_method": "Bonferroni_Clopper_Pearson_then_monotone_Holm"},
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_bmr_robustness_resampling_audit(
    sensitivity: dict[str, Any],
) -> dict[str, Any]:
    """Summarize BMR pruning robustness over observation-noise rows."""
    grouped: dict[tuple[float, float], list[dict[str, Any]]] = defaultdict(list)
    for row in sensitivity.get("rows", []):
        grouped[
            (float(row["prior_precision"]), float(row["metacognitive_access"]))
        ].append(row)
    rows = []
    for index, ((precision, access), group) in enumerate(sorted(grouped.items())):
        delta_values = [float(row["delta_free_energy"]) for row in group]
        prune_values = [1.0 if row["prunes_prior"] else 0.0 for row in group]
        delta_ci = _bootstrap_ci(delta_values, seed=8100 + index)
        prune_ci = _bootstrap_ci(prune_values, seed=8200 + index)
        rows.append(
            {
                "prior_precision": precision,
                "metacognitive_access": access,
                "noise_row_count": len(group),
                "mean_delta_free_energy": delta_ci["mean"],
                "grid_delta_min": min(delta_values), "grid_delta_max": max(delta_values),
                "pruned_noise_rows": int(sum(prune_values)),
                "all_noise_rows_same_sign": bool(min(delta_values) > 0 or max(delta_values) < 0),
                "delta_ci95_low": delta_ci["ci95_low"],
                "delta_ci95_high": delta_ci["ci95_high"],
                "pruning_rate": prune_ci["mean"],
                "pruning_ci95_low": prune_ci["ci95_low"],
                "pruning_ci95_high": prune_ci["ci95_high"],
                "sign_stable": bool(
                    delta_ci["ci95_high"] < 0.0 or delta_ci["ci95_low"] > 0.0
                ),
                "finite_interval": _finite(
                    [
                        delta_ci["mean"],
                        delta_ci["ci95_low"],
                        delta_ci["ci95_high"],
                        prune_ci["mean"],
                        prune_ci["ci95_low"],
                        prune_ci["ci95_high"],
                    ]
                ),
            }
        )
    low_access = [
        row["pruning_rate"]
        for row in rows
        if row["metacognitive_access"] == min(r["metacognitive_access"] for r in rows)
    ]
    high_access = [
        row["pruning_rate"]
        for row in rows
        if row["metacognitive_access"] == max(r["metacognitive_access"] for r in rows)
    ]
    controls = {
        "all_intervals_finite": all(row["finite_interval"] for row in rows),
        "all_pruning_rates_bounded": all(
            0.0 <= row["pruning_rate"] <= 1.0 for row in rows
        ),
        "has_stable_sign_cells": any(row["sign_stable"] for row in rows),
        "high_access_not_lower_than_low_access": float(np.mean(high_access))
        >= float(np.mean(low_access)),
    }
    return {
        "schema": "realizing_emptiness.bmr_robustness_resampling_audit.v1",
        "row_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_quantum_trajectory_convergence_audit(
    *,
    seed: int = 29,
    trajectory_counts: tuple[int, ...] = (16, 64, 128, 256, 512, 1024, 2048),
    too_few_count: int = 8,
) -> dict[str, Any]:
    """Check finite quantum-trajectory residuals across ensemble sizes."""
    rows = []
    for count in trajectory_counts:
        payload = build_quantum_trajectory_unraveling(
            seed=seed,
            trajectory_count=count,
            step_count=16,
            total_time=1.2,
        )
        rows.append(
            {
                "trajectory_count": count,
                "max_trace_distance_to_exact": payload["max_trace_distance_to_exact"],
                "all_controls_pass": payload["all_controls_pass"],
                "reconstructs_exact_lindblad_within_tolerance": payload["controls"][
                    "reconstructs_exact_lindblad_within_tolerance"
                ],
            }
        )
    too_few = build_quantum_trajectory_unraveling(
        seed=seed,
        trajectory_count=too_few_count,
        step_count=16,
        total_time=1.2,
    )
    x = np.log(np.asarray([row["trajectory_count"] for row in rows], dtype=float))
    y = np.log(
        np.asarray([row["max_trace_distance_to_exact"] for row in rows], dtype=float)
    )
    slope = float(np.polyfit(x, y, 1)[0])
    first = rows[0]["max_trace_distance_to_exact"]
    last = rows[-1]["max_trace_distance_to_exact"]
    controls = {
        "residuals_finite": _finite(
            [row["max_trace_distance_to_exact"] for row in rows]
        ),
        "log_log_slope_negative": slope < 0.0,
        "largest_count_within_tolerance": rows[-1]["max_trace_distance_to_exact"]
        < 0.08,
        "largest_count_better_than_first": last < first,
        "too_few_trajectory_control_fails": too_few["all_controls_pass"] is False,
    }
    return {
        "schema": "realizing_emptiness.quantum_trajectory_convergence_audit.v1",
        "seed": seed,
        "trajectory_counts": list(trajectory_counts),
        "too_few_count": too_few_count,
        "row_count": len(rows),
        "rows": rows,
        "log_log_residual_slope": slope,
        "too_few_trajectory_control": {
            "trajectory_count": too_few_count,
            "max_trace_distance_to_exact": too_few["max_trace_distance_to_exact"],
            "all_controls_pass": too_few["all_controls_pass"],
        },
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _synthetic_arm(
    *, shift: float, seed: int, sample_size: int = 128, base_seed_offset: int = 0
) -> dict[str, Any]:
    """Run the effect-size machinery on two seeded normal samples with a known shift.

    Returns the permutation p-value, Cliff's delta, and bootstrap interval of the shift so
    the calibration can assert the test detects an injected effect and ignores the null.
    """
    rng = np.random.default_rng(seed)
    baseline = rng.normal(0.0, 1.0, size=sample_size)
    treatment = rng.normal(shift, 1.0, size=sample_size)
    permutation = permutation_test(
        treatment.tolist(), baseline.tolist(), seed=seed + 1 + base_seed_offset, draws=1024
    )
    delta_ci = bootstrap_contrast(treatment, baseline, seed=seed + 2 + base_seed_offset)
    return {
        "injected_shift": float(shift),
        "permutation_p": permutation["p_value"],
        "cliffs_delta": delta_ci["cliffs_delta"],
        "mean_difference": float(np.mean(treatment) - np.mean(baseline)),
        "mean_difference_ci95_low": delta_ci["difference_ci95_low"],
        "mean_difference_ci95_high": delta_ci["difference_ci95_high"],
    }


def build_seed_bank_calibration(
    *, seed: int = 104242, repetitions: int = 128, positive_shift: float = 1.0,
) -> dict[str, Any]:
    """Measure rejection and difference-interval coverage across independent synthetic seed sets."""
    if repetitions < 1 or not np.isfinite(positive_shift):
        raise ValueError("calibration requires a positive repetition count and finite shift")
    rows = []
    for index in range(repetitions):
        run_seed = seed + index * 10
        rng = np.random.default_rng(run_seed)
        baseline = rng.normal(size=64)
        null = rng.normal(size=64)
        shifted = rng.normal(loc=positive_shift, size=64)
        row: dict[str, Any] = {"seed": run_seed}
        for label, values, truth in (("null", null, 0.0), ("positive", shifted, positive_shift)):
            contrast = bootstrap_contrast(values, baseline, seed=run_seed + 1, draws=512)
            p = float(permutation_test(values, baseline, seed=run_seed + 2, draws=511)["p_value"])
            row[f"{label}_p"] = p
            row[f"{label}_mean_difference"] = contrast["mean_difference"]
            row[f"{label}_ci95_low"] = contrast["difference_ci95_low"]
            row[f"{label}_ci95_high"] = contrast["difference_ci95_high"]
            row[f"{label}_rejected"] = p <= 0.05
            row[f"{label}_covered"] = contrast["difference_ci95_low"] <= truth <= contrast["difference_ci95_high"]
        rows.append(row)
    summaries = {f"{label}_{outcome}": binomial_summary(
        sum(row[f"{label}_{field}"] for row in rows), repetitions)
        for label in ("null", "positive") for outcome, field in (("rejection", "rejected"), ("coverage", "covered"))}
    controls = {"seed_bank_large_enough": repetitions >= 32,
                "null_rejection_bounded": summaries["null_rejection"]["ci_high"] <= 0.25,
                "injected_effect_detected": summaries["positive_rejection"]["ci_low"] >= 0.75}
    return {"seed": seed, "repetitions": repetitions, "sample_size_per_group": 64,
            "bootstrap_draws": 512, "permutation_draws": 511, "alpha": 0.05,
            "nominal_coverage": 0.95, "positive_shift": float(positive_shift),
            "calibration_limits": {"null_rejection_upper_max": 0.25, "positive_rejection_lower_min": 0.75},
            "rows": rows, **summaries, "controls": controls, "all_controls_pass": all(controls.values()),
            "claim_boundary": "finite normal-generator diagnostic with Monte Carlo error; not empirical statistical power or universal coverage certification"}


def build_effect_size_test_calibration_audit(
    *, seed: int = 4242, alpha: float = 0.05, positive_shift: float = 1.0
) -> dict[str, Any]:
    """Positive control: verify the effect-size machinery rejects a known injected effect.

    Three seeded synthetic arms exercise the same permutation/Cliff's-delta machinery used by
    the stochastic effect-size audit: a NULL arm (no shift) must fail to reject, a POSITIVE arm
    (a known mean shift) must reject and recover a large positive Cliff's delta, and a SIGN-FLIP
    arm (negative shift) must recover a negative Cliff's delta. Without this, a non-rejection in
    the profile-vs-null contrast is uninterpretable. This calibrates the test on synthetic data;
    it is NOT empirical statistical power over real meditators, brains, or behavioural data.
    """
    null_arm = _synthetic_arm(shift=0.0, seed=seed)
    positive_arm = _synthetic_arm(shift=positive_shift, seed=seed + 1000)
    sign_flip_arm = _synthetic_arm(shift=-positive_shift, seed=seed + 2000)
    seed_bank = build_seed_bank_calibration(positive_shift=positive_shift)
    controls = {
        "null_not_rejected": bool(
            null_arm["permutation_p"] > alpha and abs(null_arm["cliffs_delta"]) < 0.33
        ),
        "positive_effect_rejected": bool(
            positive_arm["permutation_p"] <= alpha
            and positive_arm["cliffs_delta"] > 0.33
        ),
        "cliffs_delta_sign_matches_injection": bool(
            positive_arm["cliffs_delta"] > 0.0 and sign_flip_arm["cliffs_delta"] < 0.0
        ),
        "positive_effect_magnitude_recovered": bool(
            positive_arm["mean_difference_ci95_low"]
            <= positive_shift
            <= positive_arm["mean_difference_ci95_high"]
        ),
        "seed_bank_calibrated": seed_bank["all_controls_pass"],
    }
    return {
        "schema": "realizing_emptiness.effect_size_calibration_audit.v1",
        "alpha": float(alpha),
        "positive_shift": float(positive_shift),
        "null_arm": null_arm,
        "positive_arm": positive_arm,
        "sign_flip_arm": sign_flip_arm,
        "seed_bank": seed_bank,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": (
            "internal calibration of finite seeded-stochastic null tests on synthetic data; "
            "not empirical statistical power over real meditators, brains, or behavioural data"
        ),
    }


def build_statistical_robustness_audit(
    stochastic_effects: dict[str, Any],
    bmr_resampling: dict[str, Any],
    trajectory_convergence: dict[str, Any],
    effect_size_calibration: dict[str, Any],
) -> dict[str, Any]:
    """Aggregate statistical robustness controls into one reader-facing artifact."""
    controls = {
        "stochastic_effects_pass": stochastic_effects.get("all_controls_pass") is True,
        "bmr_resampling_pass": bmr_resampling.get("all_controls_pass") is True,
        "trajectory_convergence_pass": trajectory_convergence.get("all_controls_pass")
        is True,
        "effect_size_calibration_pass": effect_size_calibration.get("all_controls_pass")
        is True,
        "claim_boundary_declared": "not empirical" in CLAIM_BOUNDARY,
    }
    return {
        "schema": "realizing_emptiness.statistical_robustness_audit.v1",
        "audits": [
            "stochastic_effect_size_audit",
            "bmr_robustness_resampling_audit",
            "quantum_trajectory_convergence_audit",
            "effect_size_calibration_audit",
        ],
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_statistical_robustness_artifacts(project_root: Path) -> tuple[Path, ...]:
    """Write statistical robustness artifacts from generated simulation outputs."""
    data_dir = project_root / "output" / "data"
    stochastic = _load_json(data_dir / "stochastic_policy_ensemble.json")
    sensitivity = _load_json(data_dir / "simulation_sensitivity_grid.json")
    stochastic_effects = build_stochastic_effect_size_audit(stochastic)
    bmr_resampling = build_bmr_robustness_resampling_audit(sensitivity)
    trajectory_convergence = build_quantum_trajectory_convergence_audit()
    effect_size_calibration = build_effect_size_test_calibration_audit()
    aggregate = build_statistical_robustness_audit(
        stochastic_effects,
        bmr_resampling,
        trajectory_convergence,
        effect_size_calibration,
    )
    payloads = {
        "stochastic_effect_size_audit.json": stochastic_effects,
        "bmr_robustness_resampling_audit.json": bmr_resampling,
        "quantum_trajectory_convergence_audit.json": trajectory_convergence,
        "effect_size_calibration_audit.json": effect_size_calibration,
        "statistical_robustness_audit.json": aggregate,
    }
    paths = []
    for filename, payload in payloads.items():
        path = data_dir / filename
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        paths.append(path)
    return tuple(paths)
