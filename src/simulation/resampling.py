from __future__ import annotations

import numpy as np
from scipy.stats import binomtest, rankdata


def _sample(values: list[float] | np.ndarray) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    if array.ndim != 1 or array.size < 2 or not np.isfinite(array).all():
        raise ValueError("samples must be finite one-dimensional arrays with at least two runs")
    return array


def _draw_count(draws: int) -> None:
    if isinstance(draws, bool) or not isinstance(draws, int) or draws < 1:
        raise ValueError("draws must be a positive integer")


def binomial_summary(hits: int, trials: int, *, confidence: float = 0.95) -> dict[str, float | int]:
    """Report a finite count, rate, Monte Carlo SE and exact binomial interval."""
    if not 0 <= hits <= trials or trials < 1 or not 0 < confidence < 1:
        raise ValueError("invalid binomial count or confidence level")
    interval = binomtest(hits, trials).proportion_ci(confidence_level=confidence, method="exact")
    rate = hits / trials
    return {"hits": hits, "trials": trials, "rate": float(rate),
            "mcse": float(np.sqrt(rate * (1 - rate) / trials)),
            "confidence_level": confidence, "ci_low": float(interval.low), "ci_high": float(interval.high)}


def bootstrap_contrast(
    first: list[float] | np.ndarray, second: list[float] | np.ndarray,
    *, seed: int, draws: int = 2048, paired: bool = False,
) -> dict[str, float]:
    """Percentile intervals for the mean difference and tie-aware Cliff's delta."""
    left, right = _sample(first), _sample(second)
    _draw_count(draws)
    if paired and left.size != right.size:
        raise ValueError("paired samples must have equal run counts")
    rng = np.random.default_rng(seed)
    indices = rng.integers(left.size, size=(draws, left.size))
    left_boot = left[indices]
    right_boot = right[indices] if paired else rng.choice(right, size=(draws, right.size))
    differences = left_boot.mean(axis=1) - right_boot.mean(axis=1)
    ranks = rankdata(np.concatenate([left_boot, right_boot], axis=1), axis=1)
    u_values = ranks[:, :left.size].sum(axis=1) - left.size * (left.size + 1) / 2
    dominance = 2 * u_values / (left.size * right.size) - 1
    point_ranks = rankdata(np.concatenate([left, right]))
    u_point = point_ranks[:left.size].sum() - left.size * (left.size + 1) / 2
    return {"mean_difference": float(left.mean() - right.mean()),
            "difference_ci95_low": float(np.quantile(differences, 0.025)),
            "difference_ci95_high": float(np.quantile(differences, 0.975)),
            "cliffs_delta": float(2 * u_point / (left.size * right.size) - 1),
            "cliffs_ci95_low": float(np.quantile(dominance, 0.025)),
            "cliffs_ci95_high": float(np.quantile(dominance, 0.975))}


def permutation_test(
    first: list[float] | np.ndarray, second: list[float] | np.ndarray,
    *, seed: int, draws: int = 4095, confidence: float = 0.95,
) -> dict[str, float | int]:
    """Two-sided independent-run label permutations with plus-one correction."""
    left, right = _sample(first), _sample(second)
    _draw_count(draws)
    observed = abs(float(left.mean() - right.mean()))
    pooled = np.concatenate([left, right])
    rng = np.random.default_rng(seed)
    permutations = rng.permuted(np.broadcast_to(pooled, (draws, pooled.size)), axis=1)
    differences = abs(permutations[:, :left.size].mean(axis=1) - permutations[:, left.size:].mean(axis=1))
    tolerance = 100 * np.finfo(float).eps * abs(observed)
    exceedances = int(np.count_nonzero(differences >= observed - tolerance))
    uncertainty = binomial_summary(exceedances, draws, confidence=confidence)
    return {"p_value": float((exceedances + 1) / (draws + 1)),
            "exceedances": exceedances, "draws": draws, "resolution": 1 / (draws + 1),
            "mcse": uncertainty["mcse"], "tail_confidence_level": confidence,
            "tail_ci_low": uncertainty["ci_low"], "tail_ci_high": uncertainty["ci_high"]}
