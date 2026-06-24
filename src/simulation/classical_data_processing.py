"""Classical Shannon data-processing surrogate: the interior knows the external only through the blanket.

This is the classical complement to the quantum data-processing engine (which works with CPTP channels
and state distinguishability). Here the boundary is a Markov chain external -> blanket -> interior: the
interior reads the external world only through the blanket. The Shannon data-processing inequality then
bounds the interior's information by the blanket's, I(interior;external) <= I(blanket;external), with
equality if and only if the blanket-to-interior map is a sufficient statistic. A sufficient (lossless)
read-out saturates the bound; a lossy read-out strictly loses information; a constant read-out reaches
zero. The interior can therefore never know the external better than the blanket lets it -- a finite,
exact information-theoretic statement of the boundary's informational closure.

INTEGRITY: a finite deterministic Shannon-information computation over fixed categorical channels. NOT a
neural, developmental, clinical, practice-efficacy, or physical qFEP claim.
"""

from __future__ import annotations

from typing import Any

import numpy as np


CLAIM_BOUNDARY = (
    "finite deterministic classical Shannon data-processing computation over a fixed external-blanket-"
    "interior Markov chain; the sufficiency-saturation / lossy-drop ordering is a software information-"
    "theory result, not empirical evidence and not a neural, developmental, clinical, practice-efficacy, "
    "or physical qFEP claim"
)

_EXTERNAL_PRIOR = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
# p(blanket | external): the blanket tracks the external world with noise.
_BLANKET_GIVEN_EXTERNAL = np.array([[0.8, 0.1, 0.1], [0.1, 0.8, 0.1], [0.1, 0.1, 0.8]])


def _mutual_information(joint: np.ndarray) -> float:
    """I(X;Y) in bits from a 2D joint distribution."""
    marginal_x = joint.sum(axis=1)
    marginal_y = joint.sum(axis=0)
    total = 0.0
    for i in range(joint.shape[0]):
        for j in range(joint.shape[1]):
            if joint[i, j] > 0.0:
                total += joint[i, j] * np.log2(joint[i, j] / (marginal_x[i] * marginal_y[j]))
    return float(total)


def _chain_informations(interior_given_blanket: np.ndarray) -> tuple[float, float]:
    """Return (I(interior;external), I(blanket;external)) for the chain external -> blanket -> interior."""
    external_count = _EXTERNAL_PRIOR.shape[0]
    blanket_count = _BLANKET_GIVEN_EXTERNAL.shape[1]
    interior_count = interior_given_blanket.shape[1]
    external_interior = np.zeros((external_count, interior_count))
    external_blanket = np.zeros((external_count, blanket_count))
    for e in range(external_count):
        for b in range(blanket_count):
            weight = _EXTERNAL_PRIOR[e] * _BLANKET_GIVEN_EXTERNAL[e, b]
            external_blanket[e, b] += weight
            for i in range(interior_count):
                external_interior[e, i] += weight * interior_given_blanket[b, i]
    return _mutual_information(external_interior), _mutual_information(external_blanket)


def build_classical_data_processing_audit() -> dict[str, Any]:
    """Finite classical data-processing surrogate with a sufficiency-saturation discriminating control.

    Each interior read-out of the blanket is a categorical channel. The audit reports, per read-out, the
    interior's information about the external world and the blanket's, and checks the data-processing
    inequality holds. The sufficient (identity) read-out saturates the bound; a lossy (state-merging)
    read-out strictly loses information; a constant read-out reaches zero. Saturation versus strict loss
    is the discriminating control, measured from the joint, not asserted.
    """
    tolerance = 1e-9
    readouts = {
        "sufficient_identity": np.eye(3),
        "lossy_merge": np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]]),
        "lossy_partial": np.array([[0.9, 0.1], [0.5, 0.5], [0.1, 0.9]]),
        "constant_erasure": np.array([[1.0], [1.0], [1.0]]),
    }
    rows = []
    for name, interior_given_blanket in readouts.items():
        interior_external, blanket_external = _chain_informations(interior_given_blanket)
        rows.append({
            "readout": name,
            "interior_external_information_bits": round(interior_external, 10),
            "blanket_external_information_bits": round(blanket_external, 10),
            "information_gap_bits": round(blanket_external - interior_external, 10),
            "data_processing_inequality_respected": bool(interior_external <= blanket_external + tolerance),
        })
    by_readout = {row["readout"]: row for row in rows}
    controls = {
        "data_processing_inequality_holds_for_every_readout": all(row["data_processing_inequality_respected"] for row in rows),
        "sufficient_readout_saturates_bound": bool(abs(by_readout["sufficient_identity"]["information_gap_bits"]) < tolerance),
        "lossy_readout_strictly_loses_information": bool(by_readout["lossy_merge"]["information_gap_bits"] > 0.05),
        "constant_readout_reaches_zero_information": bool(abs(by_readout["constant_erasure"]["interior_external_information_bits"]) < tolerance),
    }
    return {
        "schema": "realizing_emptiness.classical_data_processing_audit.v1",
        "external_prior": _EXTERNAL_PRIOR.tolist(),
        "blanket_given_external": _BLANKET_GIVEN_EXTERNAL.tolist(),
        "row_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
