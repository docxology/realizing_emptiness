"""Clearly labeled simulated criticality summaries from finite trajectories."""

from __future__ import annotations

from typing import Any

import numpy as np


CRITICALITY_CLAIM_BOUNDARY = (
    "seeded software trajectory diagnostics, not evidence of neural avalanches, branching ratio, "
    "or empirical criticality; not empirical, and no claim about brains, meditators, or practice efficacy"
)


def _entropy(values: np.ndarray) -> float:
    counts = np.bincount(values.astype(int).ravel(), minlength=2).astype(float)
    probs = counts / counts.sum()
    probs = probs[probs > 0]
    return float(-(probs * np.log(probs)).sum())


def branching_ratio(activity: np.ndarray) -> float:
    """Return the finite branching ratio sigma = descendants per ancestor over an activity series.

    The series ``activity`` is a non-negative per-step count of boundary-channel events.
    The estimator sums activity in the step that follows each active step and divides by
    the total ancestor activity; sigma == 1 marks a balanced (critical-style) regime, sigma
    below or above 1 marks subcritical or supercritical software dynamics. Returns 0.0 when
    there is no ancestor activity. This is a software-trajectory diagnostic only.
    """
    series = np.asarray(activity, dtype=float).ravel()
    if not np.isfinite(series).all():
        raise ValueError("activity series must be finite")
    if series.size < 2:
        return 0.0
    ancestors = series[:-1]
    descendants = series[1:]
    active = ancestors > 0.0
    ancestor_mass = float(ancestors[active].sum())
    if ancestor_mass <= 0.0:
        return 0.0
    return float(descendants[active].sum() / ancestor_mass)


def avalanche_size_distribution(activity: np.ndarray, *, threshold: float = 0.0) -> dict[str, Any]:
    """Extract avalanche sizes from supra-threshold runs of an activity series.

    An avalanche is a maximal run of consecutive steps whose activity exceeds ``threshold``;
    its size is the summed supra-threshold activity over the run. Returns the size histogram
    and a finite power-law-versus-exponential log-likelihood-ratio diagnostic (positive favors
    the power-law fit) over the observed sizes. This is a finite shape diagnostic, never a
    claim of true scale-free neural dynamics.
    """
    series = np.asarray(activity, dtype=float).ravel()
    sizes: list[float] = []
    current = 0.0
    active = False
    for value in series:
        if value > threshold:
            current += value - threshold
            active = True
        elif active:
            sizes.append(current)
            current = 0.0
            active = False
    if active:
        sizes.append(current)
    size_array = np.asarray(sizes, dtype=float)
    return {
        "avalanche_count": int(size_array.size),
        "sizes": [float(size) for size in size_array],
        "mean_size": float(size_array.mean()) if size_array.size else 0.0,
        "max_size": float(size_array.max()) if size_array.size else 0.0,
        "power_law_vs_exponential_llr": _power_law_vs_exponential_llr(size_array),
    }


def _power_law_vs_exponential_llr(sizes: np.ndarray) -> float:
    """Return a finite per-sample log-likelihood ratio favoring a power-law over an exponential.

    Positive values indicate the finite sample is better described by a power law than by an
    exponential of matched mean. Returns 0.0 when there is too little signal to discriminate.
    This is a bounded model-shape diagnostic, not a goodness-of-fit certification.
    """
    finite_sizes = sizes[np.isfinite(sizes)]
    positive = finite_sizes[finite_sizes > 0.0]
    if positive.size < 3 or np.allclose(positive, positive[0]) or float(positive.min()) < 1e-9:
        return 0.0
    x = positive
    # MLE power-law exponent for a continuous tail with xmin = min observed size.
    xmin = float(x.min())
    alpha = 1.0 + x.size / float(np.sum(np.log(x / xmin)))
    power_ll = x.size * np.log((alpha - 1.0) / xmin) - alpha * float(np.sum(np.log(x / xmin)))
    # Exponential MLE with matched mean.
    rate = 1.0 / float(x.mean())
    exp_ll = x.size * np.log(rate) - rate * float(x.sum())
    return float((power_ll - exp_ll) / x.size)


def criticality_signatures(activity: np.ndarray, *, threshold: float = 0.0) -> dict[str, Any]:
    """Bundle the measured criticality signatures and a DERIVED criticality index.

    ``criticality_index`` is |sigma_branch - 1| computed from the measured branching ratio
    (lower is closer to a balanced regime); it is never a hand-tuned score. All quantities are
    finite software-trajectory diagnostics under the criticality claim boundary.
    """
    sigma = branching_ratio(activity)
    avalanches = avalanche_size_distribution(activity, threshold=threshold)
    return {
        "branching_ratio": sigma,
        "criticality_index": float(abs(sigma - 1.0)),
        "avalanche_size_distribution": avalanches,
        "claim_boundary": CRITICALITY_CLAIM_BOUNDARY,
    }


def _planted_geometric_activity(sigma: float, *, length: int = 8, start: float = 1.0) -> np.ndarray:
    """Return a geometric activity series whose exact branching ratio is ``sigma``."""
    return start * np.power(float(sigma), np.arange(length, dtype=float))


def branching_estimator_calibration(*, tolerance: float = 1e-9) -> dict[str, Any]:
    """Positive control: the branching estimator recovers a planted branching ratio.

    A pure geometric activity series with ratio sigma has branching ratio exactly sigma, so the
    estimator must recover subcritical, critical, and supercritical planted values and preserve
    their ordering. Without this, the measured-branching result is a number of unknown meaning;
    with it, the estimator is shown to measure branching rather than emit an artifact. Calibration
    on synthetic series, not an empirical claim.
    """
    planted = {"subcritical": 0.5, "critical": 1.0, "supercritical": 1.5}
    recovered = {name: branching_ratio(_planted_geometric_activity(sigma)) for name, sigma in planted.items()}
    recovers = all(abs(recovered[name] - sigma) <= tolerance for name, sigma in planted.items())
    ordered = recovered["subcritical"] < recovered["critical"] < recovered["supercritical"]
    return {
        "planted_branching_ratios": planted,
        "recovered_branching_ratios": recovered,
        "branching_estimator_recovers_planted_sigma": bool(recovers),
        "branching_ordering_preserved": bool(ordered),
    }


def _activity_series(observations: np.ndarray) -> np.ndarray:
    """Return a per-step boundary-channel activity series (count of channel flips)."""
    matrix = np.asarray(observations, dtype=float)
    if matrix.ndim == 1:
        matrix = matrix[:, None]
    if matrix.shape[0] < 2:
        return np.zeros(0, dtype=float)
    return np.abs(np.diff(matrix, axis=0)).sum(axis=1)


def build_criticality_report(profile_payload: dict[str, Any]) -> dict[str, Any]:
    """Build a single-trace diagnostic retained for source-boundary continuity."""
    observations = np.array([row["observation"] for row in profile_payload["trajectory"]], dtype=float)
    diffs = np.abs(np.diff(observations, axis=0))
    flattened = observations.ravel()
    if len(flattened) > 1:
        autocorrelation = float(np.corrcoef(flattened[:-1], flattened[1:])[0, 1])
        if not np.isfinite(autocorrelation):
            autocorrelation = 0.0
    else:
        autocorrelation = 0.0
    switch_rate = float(diffs.mean()) if diffs.size else 0.0
    variance = float(observations.var())
    entropy = _entropy(observations)
    # Legacy coarse score retained for source-boundary continuity; the claim-bearing
    # quantities are now the MEASURED branching and avalanche signatures below.
    near_critical_score = float(1.0 - min(1.0, abs(switch_rate - 0.5) + abs(autocorrelation)))
    activity = _activity_series(observations)
    signatures = criticality_signatures(activity)
    return {
        "schema": "realizing_emptiness.criticality_proxy_report.v1",
        "label": "single_trace_diagnostic_not_empirical_neural_measure",
        "entropy_nats": entropy,
        "switch_rate": switch_rate,
        "variance": variance,
        "autocorrelation_lag1": autocorrelation,
        "near_critical_score": near_critical_score,
        "branching_ratio": signatures["branching_ratio"],
        "criticality_index": signatures["criticality_index"],
        "avalanche_size_distribution": signatures["avalanche_size_distribution"],
        "claim_boundary": CRITICALITY_CLAIM_BOUNDARY,
    }


def _interval(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    mean = float(array.mean())
    sd = float(array.std(ddof=1)) if len(array) > 1 else 0.0
    half_width = 1.96 * sd / np.sqrt(max(1, len(array)))
    return {
        "mean": mean,
        "sd": sd,
        "ci95_low": mean - half_width,
        "ci95_high": mean + half_width,
    }


def _branching_by_run(policy_ensemble: dict[str, Any]) -> dict[tuple[str, int, bool], float]:
    """Reconstruct each run's observation activity and return its measured branching ratio."""
    grouped: dict[tuple[str, int, bool], list[tuple[int, int]]] = {}
    for row in policy_ensemble.get("rows", []):
        key = (row["profile"], int(row["run_index"]), bool(row["null_control"]))
        grouped.setdefault(key, []).append((int(row["step"]), int(row["observation"])))
    branching: dict[tuple[str, int, bool], float] = {}
    for key, steps in grouped.items():
        observations = np.array([obs for _, obs in sorted(steps)], dtype=float)
        branching[key] = branching_ratio(_activity_series(observations))
    return branching


def build_criticality_stochastic_ensemble(policy_ensemble: dict[str, Any]) -> dict[str, Any]:
    """Summarize seeded active-inference ensembles as simulated criticality indicators."""
    branching = _branching_by_run(policy_ensemble)
    metric_rows: list[dict[str, Any]] = []
    for row in policy_ensemble.get("run_summaries", []):
        near_critical_score = float(
            1.0 - min(1.0, abs(float(row["switch_rate"]) - 0.5) + abs(float(row["autocorrelation_lag1"])))
        )
        run_branching = branching.get(
            (row["profile"], int(row["run_index"]), bool(row["null_control"])), 0.0
        )
        metric_rows.append(
            {
                "profile": row["profile"],
                "run_index": row["run_index"],
                "seed": row["seed"],
                "null_control": row["null_control"],
                "observation_entropy_nats": row["observation_entropy_nats"],
                "action_entropy_nats": row["action_entropy_nats"],
                "switch_rate": row["switch_rate"],
                "variance": row["observation_variance"],
                "autocorrelation_lag1": row["autocorrelation_lag1"],
                "near_critical_score": near_critical_score,
                "branching_ratio": run_branching,
                "criticality_index": float(abs(run_branching - 1.0)),
            }
        )
    profiles = sorted({row["profile"] for row in metric_rows})
    metrics = [
        "observation_entropy_nats",
        "action_entropy_nats",
        "switch_rate",
        "variance",
        "autocorrelation_lag1",
        "near_critical_score",
        "branching_ratio",
        "criticality_index",
    ]
    summary_rows = []
    for profile in profiles:
        for null_control in (False, True):
            rows = [row for row in metric_rows if row["profile"] == profile and row["null_control"] is null_control]
            summary_rows.append(
                {
                    "profile": profile,
                    "null_control": null_control,
                    "run_count": len(rows),
                    "metrics": {metric: _interval([float(row[metric]) for row in rows]) for metric in metrics},
                }
            )
    real_by_profile = {row["profile"]: row for row in summary_rows if row["null_control"] is False}
    null_by_profile = {row["profile"]: row for row in summary_rows if row["null_control"] is True}

    def _ci_disjoint(profile: str, metric: str) -> bool:
        """True iff the real and null 95% confidence intervals for ``metric`` do not overlap.

        This is the statistically honest separation test: a mean difference within the sampling-noise
        interval (the mildly green-by-construction failure mode of a bare mean-delta threshold) is NOT
        counted as a separation; only a genuinely disjoint interval is.
        """
        real_interval = real_by_profile[profile]["metrics"][metric]
        null_interval = null_by_profile[profile]["metrics"][metric]
        return bool(
            real_interval["ci95_low"] > null_interval["ci95_high"]
            or real_interval["ci95_high"] < null_interval["ci95_low"]
        )

    discriminating_metrics = ("branching_ratio", "switch_rate", "near_critical_score")
    null_contrasts = [
        {
            "profile": profile,
            "near_critical_delta_vs_null": real_by_profile[profile]["metrics"]["near_critical_score"]["mean"]
            - null_by_profile[profile]["metrics"]["near_critical_score"]["mean"],
            "switch_rate_delta_vs_null": real_by_profile[profile]["metrics"]["switch_rate"]["mean"]
            - null_by_profile[profile]["metrics"]["switch_rate"]["mean"],
            "branching_ratio_delta_vs_null": real_by_profile[profile]["metrics"]["branching_ratio"]["mean"]
            - null_by_profile[profile]["metrics"]["branching_ratio"]["mean"],
            "criticality_index_delta_vs_null": real_by_profile[profile]["metrics"]["criticality_index"]["mean"]
            - null_by_profile[profile]["metrics"]["criticality_index"]["mean"],
            "branching_ratio_ci_disjoint_from_null": _ci_disjoint(profile, "branching_ratio"),
            "switch_rate_ci_disjoint_from_null": _ci_disjoint(profile, "switch_rate"),
            "near_critical_score_ci_disjoint_from_null": _ci_disjoint(profile, "near_critical_score"),
            "any_signature_ci_disjoint_from_null": any(_ci_disjoint(profile, metric) for metric in discriminating_metrics),
        }
        for profile in profiles
    ]
    profiles_ci_separating = sum(1 for row in null_contrasts if row["any_signature_ci_disjoint_from_null"])
    calibration = branching_estimator_calibration()
    controls = {
        "seeded_policy_source": policy_ensemble.get("schema") == "realizing_emptiness.stochastic_policy_ensemble.v1",
        "all_intervals_finite": all(
            np.isfinite(value)
            for row in summary_rows
            for interval in row["metrics"].values()
            for value in interval.values()
        ),
        "null_controls_present": any(row["null_control"] for row in metric_rows),
        # Upgraded from a bare mean-delta > 0.01 threshold (which a noise-level difference could pass)
        # to confidence-interval disjointness, so a separation that survives is statistically genuine.
        "profiles_differ_from_null_controls": any(
            row["any_signature_ci_disjoint_from_null"] for row in null_contrasts
        ),
        "measured_branching_separates_from_null": any(
            row["branching_ratio_ci_disjoint_from_null"] for row in null_contrasts
        ),
        # Honest majority test: the criticality reading is CI-grounded only if most profiles separate
        # from their shuffled null on at least one signature; profiles within sampling noise are not
        # credited. This is what demotes a marginally-separating profile at small ensemble sizes.
        "majority_of_profiles_ci_separate_from_null": bool(profiles_ci_separating >= (len(profiles) + 1) // 2),
        "branching_estimator_recovers_planted_sigma": calibration["branching_estimator_recovers_planted_sigma"]
        and calibration["branching_ordering_preserved"],
    }
    return {
        "schema": "realizing_emptiness.criticality_stochastic_ensemble.v1",
        "label": "seeded_stochastic_simulation_not_empirical_neural_measure",
        "seed": policy_ensemble.get("seed"),
        "runs_per_profile": policy_ensemble.get("runs_per_profile"),
        "steps": policy_ensemble.get("steps"),
        "metric_row_count": len(metric_rows),
        "summary_row_count": len(summary_rows),
        "metric_rows": metric_rows,
        "summary_rows": summary_rows,
        "null_contrasts": null_contrasts,
        "branching_estimator_calibration": calibration,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": "These are seeded stochastic software indicators from simulated boundary-channel trajectories, not empirical neural-criticality measurements.",
    }
