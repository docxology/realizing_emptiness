"""Separation-prior emergence surrogate for the paper's section 4.1.

Section 4.1 argues that the separation prior sigma emerges because a metacognitive agent
that can attribute boundary observations to its own action benefits: a generative model
*factored* into self (action-contingent) and environment (action-independent) sectors
predicts the consequences of the agent's own actions better than an unfactored model — but
only when such action-contingency (empowerment) is actually present. This module
operationalises that claim as a finite deterministic predictor comparison.

It is the emergence (when-useful) half of the sigma life-cycle whose dispensable
(when-prunable) half is the BMR sweep. Together they trace the paper's account: sigma is
useful when agency is present, hardens into a habit, and later becomes prunable once
metacognitive access makes its accuracy contribution dispensable.

INTEGRITY: a finite deterministic predictor comparison on a toy boundary stream. NOT a
developmental, neural, or empirical empowerment claim — only that a factored model gains
finite predictive accuracy in proportion to action-contingency.
"""

from __future__ import annotations

from typing import Any

import numpy as np


CLAIM_BOUNDARY = (
    "finite deterministic factored-vs-unfactored predictor comparison on a toy boundary stream; "
    "not a developmental, neural, clinical, practice-efficacy, or physical qFEP claim"
)


def emergence_trajectory(
    *, empowerment: float, seed: int = 5, steps: int = 64, channels: int = 6
) -> dict[str, Any]:
    """Build a boundary stream where a fraction ``empowerment`` of channels track the action.

    The first ``round(empowerment * channels)`` channels are action-contingent (a deterministic
    function of the chosen action and a fixed per-channel bias); the remaining channels are
    action-independent (driven by their own seeded process). Returns the action sequence, the
    observation matrix, and the index set of action-contingent (self) channels.
    """
    if not 0.0 <= empowerment <= 1.0:
        raise ValueError("empowerment must be in [0, 1]")
    rng = np.random.default_rng(seed)
    self_count = int(round(empowerment * channels))
    bias = rng.integers(0, 2, size=channels)
    env_state = rng.integers(0, 2, size=channels)
    actions = rng.integers(0, 2, size=steps)
    observations = np.zeros((steps, channels), dtype=int)
    for step in range(steps):
        action = int(actions[step])
        for channel in range(channels):
            if channel < self_count:
                observations[step, channel] = action ^ int(bias[channel])
            else:
                # Action-independent channel: a seeded process unrelated to the action.
                env_state[channel] = env_state[channel] ^ int(rng.integers(0, 2))
                observations[step, channel] = env_state[channel]
    return {
        "empowerment": float(empowerment),
        "self_channel_count": self_count,
        "actions": actions.tolist(),
        "observations": observations.tolist(),
    }


def _mode_predictor_error(observations: np.ndarray, actions: np.ndarray, *, condition_on_action: np.ndarray) -> float:
    """Return the mean bit error of a per-channel mode predictor.

    For channels flagged in ``condition_on_action`` the predictor uses the action-conditioned
    mode (the most frequent observation for each action value); for the others it uses the
    marginal mode. This is the realized prediction error a model achieves, not an assertion.
    """
    steps, channels = observations.shape
    errors = []
    for channel in range(channels):
        column = observations[:, channel]
        if condition_on_action[channel]:
            prediction = np.empty(steps, dtype=int)
            for action_value in (0, 1):
                mask = actions == action_value
                if mask.any():
                    prediction[mask] = int(round(column[mask].mean()))
        else:
            prediction = np.full(steps, int(round(column.mean())), dtype=int)
        errors.append(float(np.mean(prediction != column)))
    return float(np.mean(errors))


def score_factored_vs_unfactored(trajectory: dict[str, Any]) -> dict[str, float]:
    """Return the measured prediction errors of the factored and unfactored predictors."""
    observations = np.asarray(trajectory["observations"], dtype=int)
    actions = np.asarray(trajectory["actions"], dtype=int)
    channels = observations.shape[1]
    self_count = int(trajectory["self_channel_count"])
    # Factored model: action-contingent (self) channels are action-conditioned; the rest are marginal.
    factored_mask = np.array([index < self_count for index in range(channels)], dtype=bool)
    # Unfactored model: no self/env split, so every channel uses the marginal predictor only.
    unfactored_mask = np.zeros(channels, dtype=bool)
    factored_error = _mode_predictor_error(observations, actions, condition_on_action=factored_mask)
    unfactored_error = _mode_predictor_error(observations, actions, condition_on_action=unfactored_mask)
    return {
        "factored_error": factored_error,
        "unfactored_error": unfactored_error,
        "factored_advantage": float(unfactored_error - factored_error),
    }


REVISION_CLAIM_BOUNDARY = (
    "finite toy non-stationary boundary stream modeling revision-vs-rigidity dynamics; not a claim of "
    "realized awakening, attainment, impermanence insight, a zero-person perspective, or any empirical outcome"
)


def _window_error(observations: np.ndarray, actions: np.ndarray, self_set: frozenset[int]) -> float:
    """Mean bit error when the channels in ``self_set`` are action-conditioned, the rest marginal."""
    channels = observations.shape[1]
    mask = np.array([channel in self_set for channel in range(channels)], dtype=bool)
    return _mode_predictor_error(observations, actions, condition_on_action=mask)


def _best_self_set(obs: np.ndarray, act: np.ndarray, channels: int, *, margin: float = 0.1) -> frozenset[int]:
    """Post-dual revision: action-condition a channel only when that MATERIALLY lowers its error.

    The margin prevents switching the sectorisation on in-sample noise (a two-bucket action-conditioned
    fit can beat the marginal by chance on a genuinely action-independent channel), so the revision
    tracks a real regime change rather than overfitting.
    """
    chosen = set()
    for channel in range(channels):
        column = obs[:, channel:channel + 1]
        marginal = _mode_predictor_error(column, act, condition_on_action=np.array([False]))
        conditioned = _mode_predictor_error(column, act, condition_on_action=np.array([True]))
        if conditioned < marginal - margin:
            chosen.add(channel)
    return frozenset(chosen)


def _run_revision_stream(*, regime_change: bool, steps: int, seed: int, channels: int) -> dict[str, Any]:
    """Run one rigid-vs-revising comparison over a (possibly) non-stationary boundary stream."""
    rng = np.random.default_rng(seed)
    half = steps // 2
    window_a_self = frozenset(range(channels // 2))
    window_b_self = frozenset(range(channels // 2, channels)) if regime_change else window_a_self
    bias = rng.integers(0, 2, size=channels)
    env_state = rng.integers(0, 2, size=channels)
    actions = rng.integers(0, 2, size=steps)
    observations = np.zeros((steps, channels), dtype=int)
    for step in range(steps):
        action = int(actions[step])
        active_self = window_a_self if step < half else window_b_self
        for channel in range(channels):
            if channel in active_self:
                observations[step, channel] = action ^ int(bias[channel])
            else:
                env_state[channel] = env_state[channel] ^ int(rng.integers(0, 2))
                observations[step, channel] = env_state[channel]
    windows = []
    for label, lo, hi in (("pre_regime", 0, half), ("post_regime", half, steps)):
        obs_window, act_window = observations[lo:hi], actions[lo:hi]
        rigid_error = _window_error(obs_window, act_window, window_a_self)
        post_dual_set = _best_self_set(obs_window, act_window, channels)
        post_dual_error = _window_error(obs_window, act_window, post_dual_set)
        windows.append(
            {
                "window": label,
                "rigid_error": rigid_error,
                "post_dual_error": post_dual_error,
                "post_dual_advantage": float(rigid_error - post_dual_error),
                "post_dual_self_set": sorted(post_dual_set),
            }
        )
    by_window = {row["window"]: row for row in windows}
    pre_adv = by_window["pre_regime"]["post_dual_advantage"]
    post_adv = by_window["post_regime"]["post_dual_advantage"]
    return {
        "regime_change": regime_change,
        "windows": windows,
        "pre_regime_advantage": pre_adv,
        "post_regime_advantage": post_adv,
        "revision_jump": float(post_adv - pre_adv),
    }


def build_ongoing_revision_audit(*, steps: int = 64, seed: int = 11, channels: int = 6) -> dict[str, Any]:
    """Operationalize the post-dual agent's ongoing revision under non-stationarity (5.2/5.3).

    A non-stationary boundary stream changes regime at the midpoint: the action-contingent (self)
    channels flip. A RIGID sigma-locked agent keeps its original sectorisation; a POST-DUAL agent
    re-selects the sectorisation that minimizes measured error per window. The claim-bearing signal
    is that the revising agent's advantage JUMPS at the regime change. The discriminating negative
    control is a STATIONARY stream run with identical machinery: there the advantage must not jump,
    so the gain is attributable to revision-under-change rather than to generic adaptive overfitting.
    All verdicts are derived from measured window errors.
    """
    nonstationary = _run_revision_stream(regime_change=True, steps=steps, seed=seed, channels=channels)
    stationary = _run_revision_stream(regime_change=False, steps=steps, seed=seed, channels=channels)
    controls = {
        "post_dual_outperforms_after_regime_change": bool(nonstationary["post_regime_advantage"] > 0.05),
        "revision_gain_concentrated_at_regime_change": bool(nonstationary["revision_jump"] > 0.1),
        "stationary_stream_shows_no_revision_jump": bool(abs(stationary["revision_jump"]) < 0.05),
        "nonstationary_jump_exceeds_stationary": bool(
            nonstationary["revision_jump"] > stationary["revision_jump"] + 0.1
        ),
    }
    return {
        "schema": "realizing_emptiness.ongoing_revision_audit.v1",
        "label": "finite_non_stationary_revision_vs_rigidity_not_empirical",
        "nonstationary_stream": nonstationary,
        "stationary_stream": stationary,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": REVISION_CLAIM_BOUNDARY,
    }


def _action_shuffled_factored_advantage(trajectory: dict[str, Any], *, shuffle_count: int, seed: int) -> float:
    """Mean factored advantage after permuting the action sequence relative to the observations.

    Shuffling destroys the (observation, action) pairing, so the action-conditioned predictor on the
    self channels can no longer exploit any real contingency: a genuine factored advantage must
    collapse toward zero. A green-by-construction estimator would not move under this shuffle.
    """
    observations = np.asarray(trajectory["observations"], dtype=int)
    actions = np.asarray(trajectory["actions"], dtype=int)
    self_count = int(trajectory["self_channel_count"])
    rng = np.random.default_rng(seed)
    advantages: list[float] = []
    for _ in range(shuffle_count):
        permuted = rng.permutation(actions)
        shuffled = {
            "observations": observations.tolist(),
            "actions": permuted.tolist(),
            "self_channel_count": self_count,
        }
        advantages.append(score_factored_vs_unfactored(shuffled)["factored_advantage"])
    return float(np.mean(advantages)) if advantages else 0.0


def build_separation_prior_emergence_audit(
    *, empowerment_grid: tuple[float, ...] = (0.0, 0.25, 0.5, 0.75, 1.0), seed: int = 5, action_shuffle_count: int = 32
) -> dict[str, Any]:
    """Audit when a factored self/env model buys predictive accuracy over an unfactored model.

    The factored advantage is measured (unfactored error minus factored error) across an
    empowerment grid. The positive resolving-power control is the full-empowerment row: a fully
    action-determined stream must yield a large, detected advantage.

    Two negative controls of different strengths guard the claim. The zero-empowerment row is a
    CONSTRUCTIVE correctness check: with no action-contingent channel the factored and unfactored
    masks are byte-identical, so the advantage is *necessarily* zero — green-by-construction and
    therefore unable to falsify the action-contingency hypothesis on its own. The DISCRIMINATING
    negative control is the action shuffle at full empowerment: permuting the action sequence breaks
    the realised contingency, so the measured factored advantage must collapse far below the real
    full-empowerment advantage. That collapse, not the constructive zero row, is what attributes the
    gain to genuine action-contingency rather than to the factored predictor's extra free parameters.
    All verdicts are derived from measured predictor errors.
    """
    rows = []
    full_trajectory = None
    for empowerment in empowerment_grid:
        trajectory = emergence_trajectory(empowerment=empowerment, seed=seed)
        if empowerment == max(empowerment_grid):
            full_trajectory = trajectory
        scores = score_factored_vs_unfactored(trajectory)
        rows.append({"empowerment": float(empowerment), "self_channel_count": trajectory["self_channel_count"], **scores})
    by_empowerment = {row["empowerment"]: row for row in rows}
    zero_row = by_empowerment[min(empowerment_grid)]
    full_row = by_empowerment[max(empowerment_grid)]
    advantages = [row["factored_advantage"] for row in rows]
    assert full_trajectory is not None
    mean_action_shuffled_advantage = _action_shuffled_factored_advantage(
        full_trajectory, shuffle_count=action_shuffle_count, seed=seed
    )
    controls = {
        "factored_beats_unfactored_at_high_empowerment": bool(full_row["factored_advantage"] > 0.05),
        # Constructive correctness check: identical masks at zero empowerment force a zero advantage.
        "factored_does_not_beat_unfactored_at_zero_empowerment": bool(abs(zero_row["factored_advantage"]) < 1e-9),
        "accuracy_gain_monotone_in_empowerment": all(b >= a - 1e-9 for a, b in zip(advantages, advantages[1:])),
        "planted_full_contingency_detected": bool(full_row["factored_advantage"] > 0.2),
        # Discriminating negative control with teeth: breaking the action pairing must collapse the gain.
        "action_shuffle_collapses_factored_advantage": bool(
            mean_action_shuffled_advantage < 0.25 * full_row["factored_advantage"]
            and full_row["factored_advantage"] - mean_action_shuffled_advantage > 0.2
        ),
    }
    return {
        "schema": "realizing_emptiness.separation_prior_emergence_audit.v1",
        "label": "finite_factored_vs_unfactored_predictor_comparison_not_empirical",
        "row_count": len(rows),
        "rows": rows,
        "zero_empowerment_advantage": zero_row["factored_advantage"],
        "full_empowerment_advantage": full_row["factored_advantage"],
        "mean_action_shuffled_advantage": mean_action_shuffled_advantage,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
