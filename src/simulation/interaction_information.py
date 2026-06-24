"""Interaction-information synergy surrogate: the sharpest finite echo of no-self-evidence.

Where the Gaussian Markov-blanket engine shows a boundary that is *contingently* hard to read from the
marginal, this engine exhibits the extreme case directly. Over a categorical joint p(I,B,E) the
interaction information II(I;E;B) = I(I;E|B) - I(I;E) separates two regimes the interior cannot tell
apart from the marginal alone:

- a SYNERGISTIC boundary B = I XOR E, where the marginal mutual information I(I;E) is EXACTLY zero (the
  interior observes literally nothing passively) yet the conditional mutual information I(I;E|B) is a
  full bit and II is strongly positive; and
- a REDUNDANT screen (a common cause), where I _||_ E | B so I(I;E|B) is zero, the marginal dependence
  is positive, and II is negative.

The sign of II flips between the regimes while a marginal-only reading sees no conditional structure at
all -- a finite, exact information-theoretic statement of the paper's thesis that the boundary is not
evidenceable from inside. This is qualitatively beyond the Gaussian engine: partial correlation is zero
for BOTH regimes, so a second-order (covariance) method cannot represent XOR synergy.

INTEGRITY: a finite deterministic Shannon-information computation over fixed categorical distributions.
NOT a neural, developmental, clinical, practice-efficacy, or physical qFEP claim.
"""

from __future__ import annotations

from typing import Any

import numpy as np


CLAIM_BOUNDARY = (
    "finite deterministic Shannon interaction-information computation over fixed categorical "
    "distributions; the synergy/redundancy sign is a software information-theory result, not empirical "
    "evidence and not a neural, developmental, clinical, practice-efficacy, or physical qFEP claim"
)


def _conditional_mutual_information(joint: np.ndarray) -> float:
    """I(I;E|B) in bits for a joint indexed [internal, blanket, external]."""
    blanket_marginal = joint.sum(axis=(0, 2))
    total = 0.0
    for b in range(joint.shape[1]):
        weight = blanket_marginal[b]
        if weight <= 0.0:
            continue
        conditional = joint[:, b, :] / weight
        internal = conditional.sum(axis=1)
        external = conditional.sum(axis=0)
        for i in range(joint.shape[0]):
            for e in range(joint.shape[2]):
                if conditional[i, e] > 0.0:
                    total += weight * conditional[i, e] * np.log2(conditional[i, e] / (internal[i] * external[e]))
    return float(total)


def _marginal_mutual_information(joint: np.ndarray) -> float:
    """I(I;E) in bits, marginalising out the blanket."""
    marginal = joint.sum(axis=1)
    internal = marginal.sum(axis=1)
    external = marginal.sum(axis=0)
    total = 0.0
    for i in range(marginal.shape[0]):
        for e in range(marginal.shape[1]):
            if marginal[i, e] > 0.0:
                total += marginal[i, e] * np.log2(marginal[i, e] / (internal[i] * external[e]))
    return float(total)


def _synergistic_xor_joint() -> np.ndarray:
    """B = I XOR E with I, E independent and uniform: marginal I(I;E) = 0 exactly, I(I;E|B) = 1 bit."""
    joint = np.zeros((2, 2, 2))
    for i in (0, 1):
        for e in (0, 1):
            joint[i, i ^ e, e] = 0.25
    return joint


def _redundant_screen_joint(internal_fidelity: float = 0.85, external_fidelity: float = 0.8) -> np.ndarray:
    """Common cause: B uniform, I and E each track B independently, so I _||_ E | B (a clean screen)."""
    joint = np.zeros((2, 2, 2))
    for b in (0, 1):
        for i in (0, 1):
            for e in (0, 1):
                p_i = internal_fidelity if i == b else (1.0 - internal_fidelity)
                p_e = external_fidelity if e == b else (1.0 - external_fidelity)
                joint[i, b, e] = 0.5 * p_i * p_e
    return joint


def _independent_null_joint() -> np.ndarray:
    """All three variables independent and uniform: no structure, so II = 0."""
    return np.full((2, 2, 2), 1.0 / 8.0)


def build_interaction_information_boundary_audit() -> dict[str, Any]:
    """Finite interaction-information surrogate with synergy, redundancy, and null regimes.

    Each fixture reports the marginal mutual information the interior can passively observe, the
    conditional mutual information given the blanket, and the interaction information II = conditional -
    marginal. The discriminating controls: the synergistic XOR boundary has marginal information exactly
    zero yet a full bit of conditional information (II strongly positive); the redundant screen has zero
    conditional information and negative II; and the sign of II flips between the two regimes while a
    null distribution sits at II = 0. A marginal-only reading cannot tell synergy from a null -- which is
    precisely the no-self-evidence point.
    """
    tolerance = 1e-9
    fixtures = {
        "synergistic_xor": _synergistic_xor_joint(),
        "redundant_screen": _redundant_screen_joint(),
        "independent_null": _independent_null_joint(),
    }
    rows = []
    for name, joint in fixtures.items():
        marginal = _marginal_mutual_information(joint)
        conditional = _conditional_mutual_information(joint)
        rows.append({
            "fixture": name,
            "marginal_mutual_information_bits": round(marginal, 10),
            "conditional_mutual_information_bits": round(conditional, 10),
            "interaction_information_bits": round(conditional - marginal, 10),
        })
    by_fixture = {row["fixture"]: row for row in rows}
    synergy = by_fixture["synergistic_xor"]
    redundant = by_fixture["redundant_screen"]
    null = by_fixture["independent_null"]
    controls = {
        "synergistic_boundary_marginal_is_exactly_zero": bool(abs(synergy["marginal_mutual_information_bits"]) < tolerance),
        "synergistic_boundary_conditional_is_a_full_bit": bool(abs(synergy["conditional_mutual_information_bits"] - 1.0) < 1e-6),
        "synergistic_interaction_information_is_positive": bool(synergy["interaction_information_bits"] > 0.5),
        "redundant_screen_is_conditionally_independent": bool(abs(redundant["conditional_mutual_information_bits"]) < 1e-6),
        "redundant_interaction_information_is_negative": bool(redundant["interaction_information_bits"] < -0.01),
        "interaction_information_sign_discriminates_regimes": bool(
            synergy["interaction_information_bits"] > 0.0 > redundant["interaction_information_bits"]
        ),
        "null_distribution_has_no_interaction": bool(abs(null["interaction_information_bits"]) < tolerance),
    }
    return {
        "schema": "realizing_emptiness.interaction_information_boundary_audit.v1",
        "fixture_count": len(rows),
        "row_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
