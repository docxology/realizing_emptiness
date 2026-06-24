"""Blackwell garbling / Bayes-risk surrogate: use is licensed, ontology is not.

The QRF indistinguishability audits elsewhere assert that admissible sector relabelings leave the
boundary probabilities unchanged. This engine upgrades that assertion to a measured DECISION-THEORETIC
ordering via Blackwell's theorem. A boundary observation channel defines a statistical decision
problem; the Bayes risk (the expected loss of the optimal decision rule) measures the channel's
decision value. An invertible relabeling of the boundary outcomes -- a QRF sector relabel -- is a
reversible post-processing and preserves the Bayes risk exactly: deciding is just as good under any
admissible relabeling, so *use* of the boundary is licensed. A genuine garbling -- a lossy, irreversible
stochastic post-processing, the decision-theoretic image of collapsing the boundary into an ontology --
can only raise the Bayes risk, and a nontrivial one strictly does: committing to a lossy coarse-graining
destroys decision value, so *ontology* is not licensed.

INTEGRITY: a finite deterministic statistical-decision computation over fixed channels. NOT a neural,
developmental, clinical, practice-efficacy, or physical qFEP claim.
"""

from __future__ import annotations

from typing import Any

import numpy as np


CLAIM_BOUNDARY = (
    "finite deterministic Blackwell garbling / Bayes-risk computation over fixed boundary channels; the "
    "relabel-preserves / garble-degrades ordering is a software statistical-decision result, not "
    "empirical evidence and not a neural, developmental, clinical, practice-efficacy, or physical qFEP claim"
)

# A symmetric binary boundary channel A[state, outcome] = p(outcome | state) and a uniform prior over
# the hidden boundary state, under 0-1 loss. The channel is informative (Bayes error 0.2 < chance 0.5).
_PRIOR = np.array([0.5, 0.5])
_CHANNEL = np.array([[0.8, 0.2], [0.2, 0.8]])


def _bayes_error(channel: np.ndarray) -> float:
    """Bayes risk of the optimal decision rule under 0-1 loss: 1 - sum_o max_state p(state) p(o|state)."""
    joint = _PRIOR[:, None] * channel
    return float(1.0 - joint.max(axis=0).sum())


def _relabel(channel: np.ndarray, permutation: tuple[int, int]) -> np.ndarray:
    """Invertible relabeling: permute the outcome columns (a reversible post-processing)."""
    return channel[:, list(permutation)]


def _garble(channel: np.ndarray, retention_a: float, retention_b: float) -> np.ndarray:
    """Row-stochastic post-processing G; A' = A @ G. Lossy unless G is a permutation."""
    garbling = np.array([[retention_a, 1.0 - retention_a], [1.0 - retention_b, retention_b]])
    return channel @ garbling


def build_blackwell_bayes_risk_audit(*, grid_steps: int = 21) -> dict[str, Any]:
    """Finite Blackwell ordering surrogate with relabel-preserves and garble-degrades controls.

    The original channel's Bayes risk is compared against every invertible relabeling (which must
    preserve it) and a family of garblings (which can only raise it). Controls: relabeling preserves
    the Bayes risk; a named nontrivial garbling strictly raises it (the discriminating control); no
    garbling over a dense grid ever lowers it (Blackwell monotonicity, a data-processing inequality);
    and a complete-erasure garbling reaches the prior chance risk.
    """
    tolerance = 1e-9
    chance_risk = float(1.0 - _PRIOR.max())
    original_risk = _bayes_error(_CHANNEL)

    relabel_rows = []
    for name, permutation in (("identity", (0, 1)), ("swap_outcomes", (1, 0))):
        relabel_rows.append({
            "relabeling": name,
            "permutation": list(permutation),
            "bayes_risk": round(_bayes_error(_relabel(_CHANNEL, permutation)), 10),
        })

    named_garblings = (
        ("weak_garbling", 0.85, 0.85),
        ("partial_garbling", 0.7, 0.7),
        ("strong_garbling", 0.6, 0.6),
        ("complete_erasure", 0.5, 0.5),
    )
    garble_rows = []
    for name, retention_a, retention_b in named_garblings:
        risk = _bayes_error(_garble(_CHANNEL, retention_a, retention_b))
        garble_rows.append({
            "garbling": name,
            "retention": [round(retention_a, 6), round(retention_b, 6)],
            "bayes_risk": round(risk, 10),
            "risk_increase_vs_original": round(risk - original_risk, 10),
        })

    # Dense grid of garblings to test Blackwell monotonicity (no post-processing lowers the Bayes risk).
    grid_risks = []
    for step_a in range(grid_steps):
        for step_b in range(grid_steps):
            risk = _bayes_error(_garble(_CHANNEL, step_a / (grid_steps - 1), step_b / (grid_steps - 1)))
            grid_risks.append(risk)
    minimum_grid_risk = min(grid_risks)

    by_garbling = {row["garbling"]: row for row in garble_rows}
    controls = {
        "invertible_relabeling_preserves_bayes_risk": all(
            abs(row["bayes_risk"] - original_risk) < tolerance for row in relabel_rows
        ),
        "nontrivial_garbling_strictly_increases_bayes_risk": bool(
            by_garbling["partial_garbling"]["risk_increase_vs_original"] > 0.01
        ),
        "bayes_risk_never_below_original_under_garbling": bool(minimum_grid_risk >= original_risk - tolerance),
        "complete_erasure_reaches_chance_risk": bool(abs(by_garbling["complete_erasure"]["bayes_risk"] - chance_risk) < tolerance),
    }
    return {
        "schema": "realizing_emptiness.blackwell_bayes_risk_audit.v1",
        "prior": _PRIOR.tolist(),
        "channel": _CHANNEL.tolist(),
        "chance_risk": round(chance_risk, 10),
        "original_bayes_risk": round(original_risk, 10),
        "minimum_grid_garbling_risk": round(minimum_grid_risk, 10),
        "relabeling_rows": relabel_rows,
        "garbling_rows": garble_rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
