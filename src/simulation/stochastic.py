"""Seeded stochastic active-inference ensembles for finite QRF profiles."""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

import numpy as np

from simulation.pymdp_profiles import (
    ACTION_LABELS,
    OBSERVATION_LABELS,
    STATE_LABELS,
    build_profile_generative_model,
    expected_free_energy_values,
    normalize_probability,
    profile_specs,
    softmax_negative,
)


CLAIM_BOUNDARY = (
    "seeded stochastic software simulation over finite active-inference profiles; "
    "not empirical data, not a neural measurement, and not evidence for practice outcomes"
)


def _categorical_sample(rng: np.random.Generator, probabilities: np.ndarray) -> int:
    return int(rng.choice(len(probabilities), p=normalize_probability(probabilities)))


def _entropy(values: list[int], support: int) -> float:
    counts = np.bincount(np.asarray(values, dtype=int), minlength=support).astype(float)
    probs = counts / counts.sum()
    probs = probs[probs > 0.0]
    return float(-(probs * np.log(probs)).sum())


def _run_profile_once(
    *,
    model: dict[str, Any],
    seed: int,
    profile: str,
    run_index: int,
    steps: int,
    null_control: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rng = np.random.default_rng(seed)
    prior = normalize_probability(model["D"])
    hidden_state = _categorical_sample(rng, prior)
    rows: list[dict[str, Any]] = []
    observations: list[int] = []
    actions: list[int] = []
    weighted_efe_values: list[float] = []
    surprise_values: list[float] = []
    for step in range(steps):
        if null_control:
            observation = _categorical_sample(rng, np.ones(len(OBSERVATION_LABELS), dtype=float))
        else:
            observation = _categorical_sample(rng, model["A"][:, hidden_state])
        evidence = float(model["A"][observation, :] @ prior)
        posterior = normalize_probability(model["A"][observation, :] * prior)
        efe = expected_free_energy_values(model, posterior)
        policy_posterior = softmax_negative(efe)
        if null_control:
            action_index = _categorical_sample(rng, np.ones(len(ACTION_LABELS), dtype=float))
        else:
            action_index = _categorical_sample(rng, policy_posterior)
        transition = model["B"][:, :, action_index]
        next_prior = normalize_probability(transition @ posterior)
        hidden_state = _categorical_sample(rng, transition[:, hidden_state])
        observations.append(observation)
        actions.append(action_index)
        weighted_efe = float(policy_posterior @ efe)
        weighted_efe_values.append(weighted_efe)
        surprise = float(-math.log(max(evidence, 1e-12)))
        surprise_values.append(surprise)
        rows.append(
            {
                "profile": profile,
                "run_index": run_index,
                "seed": seed,
                "step": step,
                "null_control": null_control,
                "hidden_state": STATE_LABELS[hidden_state],
                "observation": observation,
                "observation_label": OBSERVATION_LABELS[observation],
                "state_posterior": np.round(posterior, 8).tolist(),
                "state_posterior_sum": float(posterior.sum()),
                "policy_posterior": np.round(policy_posterior, 8).tolist(),
                "policy_posterior_sum": float(policy_posterior.sum()),
                "selected_action": ACTION_LABELS[action_index],
                "selected_action_index": action_index,
                "weighted_expected_free_energy": weighted_efe,
                "surprise": surprise,
            }
        )
        prior = next_prior
    switches = [1.0 if observations[i] != observations[i - 1] else 0.0 for i in range(1, len(observations))]
    if len(observations) > 1:
        autocorrelation = float(np.corrcoef(observations[:-1], observations[1:])[0, 1])
        if not np.isfinite(autocorrelation):
            autocorrelation = 0.0
    else:
        autocorrelation = 0.0
    summary = {
        "profile": profile,
        "run_index": run_index,
        "seed": seed,
        "null_control": null_control,
        "observation_entropy_nats": _entropy(observations, len(OBSERVATION_LABELS)),
        "action_entropy_nats": _entropy(actions, len(ACTION_LABELS)),
        "switch_rate": float(np.mean(switches)) if switches else 0.0,
        "observation_variance": float(np.var(observations)),
        "autocorrelation_lag1": autocorrelation,
        "mean_weighted_expected_free_energy": float(np.mean(weighted_efe_values)),
        "mean_surprise": float(np.mean(surprise_values)),
        "posterior_normalized": all(
            abs(row["state_posterior_sum"] - 1.0) < 1e-8 and abs(row["policy_posterior_sum"] - 1.0) < 1e-8
            for row in rows
        ),
    }
    return rows, summary


def _interval(values: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    mean = float(array.mean())
    sd = float(array.std(ddof=1)) if len(array) > 1 else 0.0
    half_width = 1.96 * sd / math.sqrt(max(1, len(array)))
    return {
        "mean": mean,
        "sd": sd,
        "ci95_low": mean - half_width,
        "ci95_high": mean + half_width,
    }


def _summaries_by_profile(run_summaries: list[dict[str, Any]], *, null_control: bool) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in run_summaries:
        if row["null_control"] is null_control:
            grouped[row["profile"]].append(row)
    metric_names = [
        "observation_entropy_nats",
        "action_entropy_nats",
        "switch_rate",
        "observation_variance",
        "autocorrelation_lag1",
        "mean_weighted_expected_free_energy",
        "mean_surprise",
    ]
    summaries = []
    for profile, rows in sorted(grouped.items()):
        summaries.append(
            {
                "profile": profile,
                "null_control": null_control,
                "run_count": len(rows),
                "metrics": {name: _interval([float(row[name]) for row in rows]) for name in metric_names},
                "posterior_normalized_all_runs": all(row["posterior_normalized"] for row in rows),
            }
        )
    return summaries


def build_stochastic_policy_ensemble(
    *,
    seed: int = 101,
    runs: int = 128,
    steps: int = 48,
    channels: int = 6,
) -> dict[str, Any]:
    """Run seeded stochastic active-inference ensembles and null controls."""
    rows: list[dict[str, Any]] = []
    run_summaries: list[dict[str, Any]] = []
    for profile_index, spec in enumerate(profile_specs(channels)):
        model = build_profile_generative_model(spec)
        for run_index in range(runs):
            run_seed = seed + 10000 * profile_index + run_index
            profile_rows, summary = _run_profile_once(
                model=model,
                seed=run_seed,
                profile=spec.deployment.name,
                run_index=run_index,
                steps=steps,
            )
            null_rows, null_summary = _run_profile_once(
                model=model,
                seed=run_seed + 500000,
                profile=spec.deployment.name,
                run_index=run_index,
                steps=steps,
                null_control=True,
            )
            rows.extend(profile_rows)
            rows.extend(null_rows)
            run_summaries.extend([summary, null_summary])
    profile_summaries = _summaries_by_profile(run_summaries, null_control=False)
    null_summaries = _summaries_by_profile(run_summaries, null_control=True)
    profile_by_name = {row["profile"]: row for row in profile_summaries}
    null_by_name = {row["profile"]: row for row in null_summaries}
    separation_rows = []
    for profile, summary in profile_by_name.items():
        null_summary = null_by_name[profile]
        separation_rows.append(
            {
                "profile": profile,
                "switch_rate_delta_vs_null": summary["metrics"]["switch_rate"]["mean"]
                - null_summary["metrics"]["switch_rate"]["mean"],
                "mean_surprise_delta_vs_null": summary["metrics"]["mean_surprise"]["mean"]
                - null_summary["metrics"]["mean_surprise"]["mean"],
                "efe_delta_vs_null": summary["metrics"]["mean_weighted_expected_free_energy"]["mean"]
                - null_summary["metrics"]["mean_weighted_expected_free_energy"]["mean"],
            }
        )
    controls = {
        "all_posteriors_normalized": all(row["posterior_normalized"] for row in run_summaries),
        "all_intervals_finite": all(
            np.isfinite(value)
            for summary in profile_summaries + null_summaries
            for metric in summary["metrics"].values()
            for value in metric.values()
        ),
        "profiles_differ_from_null_controls": any(
            abs(row["switch_rate_delta_vs_null"]) > 0.02 or abs(row["mean_surprise_delta_vs_null"]) > 0.02
            for row in separation_rows
        ),
        "seeded_replay_declared": True,
    }
    return {
        "schema": "realizing_emptiness.stochastic_policy_ensemble.v1",
        "seed": seed,
        "runs_per_profile": runs,
        "steps": steps,
        "channels": channels,
        "profile_count": len(profile_summaries),
        "row_count": len(rows),
        "run_summary_count": len(run_summaries),
        "state_labels": list(STATE_LABELS),
        "observation_labels": list(OBSERVATION_LABELS),
        "action_labels": list(ACTION_LABELS),
        "rows": rows,
        "run_summaries": run_summaries,
        "profile_summaries": profile_summaries,
        "null_summaries": null_summaries,
        "profile_null_separation": separation_rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
