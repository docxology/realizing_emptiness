"""Quantum Cramer-Rao estimation surrogate for the precision limit on the separation prior.

The separation prior sigma is a parameter the agent would have to estimate from boundary observations.
Estimation theory bounds how well any measurement can do: the classical Fisher information of any
measurement is at most the quantum Fisher information (QFI) of the state family -- the quantum
Cramer-Rao bound, itself a data-processing inequality for Fisher information. This module
operationalises that limit as a finite two-level computation and ties it to the paper's opacification
theme: when the boundary encodes sigma *coherently*, the interior's decohered pointer-basis
measurement is strictly suboptimal and cannot reach the god's-eye QFI; when sigma is encoded
classically (in populations), the pointer measurement is already optimal. The information gap is
therefore created by the coherence that opacification renders inaccessible, not by an artifact.

INTEGRITY: a finite deterministic single-qubit estimation-theory computation. NOT a metrology
experiment and not a neural, developmental, clinical, practice-efficacy, or physical qFEP claim.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np


CLAIM_BOUNDARY = (
    "finite deterministic single-qubit quantum-Cramer-Rao estimation-theory computation over the "
    "separation parameter; the classical-vs-quantum Fisher-information gap is a software linear-algebra "
    "result, not empirical evidence and not a metrology, neural, clinical, practice-efficacy, or "
    "physical qFEP claim"
)

_SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
_SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)
_SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
_IDENTITY = np.eye(2, dtype=complex)


def _density(bloch: np.ndarray) -> np.ndarray:
    return 0.5 * (_IDENTITY + bloch[0] * _SIGMA_X + bloch[1] * _SIGMA_Y + bloch[2] * _SIGMA_Z)


def _d_density(d_bloch: np.ndarray) -> np.ndarray:
    return 0.5 * (d_bloch[0] * _SIGMA_X + d_bloch[1] * _SIGMA_Y + d_bloch[2] * _SIGMA_Z)


def _symmetric_logarithmic_derivative(rho: np.ndarray, d_rho: np.ndarray) -> np.ndarray:
    """SLD operator L solving rho L + L rho = 2 d_rho, via the eigenbasis spectral formula."""
    eigenvalues, eigenvectors = np.linalg.eigh(rho)
    sld = np.zeros((2, 2), dtype=complex)
    for j in range(2):
        for k in range(2):
            denom = eigenvalues[j] + eigenvalues[k]
            if denom > 1e-12:
                coefficient = 2.0 * (eigenvectors[:, j].conjugate() @ d_rho @ eigenvectors[:, k]) / denom
                sld += coefficient * np.outer(eigenvectors[:, j], eigenvectors[:, k].conjugate())
    return sld


def _quantum_fisher_information(rho: np.ndarray, d_rho: np.ndarray) -> float:
    """QFI = Tr[d_rho L] with L the symmetric logarithmic derivative."""
    return float(np.real(np.trace(d_rho @ _symmetric_logarithmic_derivative(rho, d_rho))))


def _sld_optimal_axis(rho: np.ndarray, d_rho: np.ndarray) -> np.ndarray:
    """Bloch axis of the SLD-eigenbasis measurement, which saturates the quantum Cramer-Rao bound."""
    sld = _symmetric_logarithmic_derivative(rho, d_rho)
    direction = np.array([
        0.5 * np.real(np.trace(sld @ _SIGMA_X)),
        0.5 * np.real(np.trace(sld @ _SIGMA_Y)),
        0.5 * np.real(np.trace(sld @ _SIGMA_Z)),
    ])
    norm = float(np.linalg.norm(direction))
    return direction / norm if norm > 1e-12 else np.array([0.0, 0.0, 1.0])


def _classical_fisher_information(bloch: np.ndarray, d_bloch: np.ndarray, axis: np.ndarray) -> float:
    """Classical Fisher information of the projective measurement along ``axis`` (Bloch direction)."""
    projection = float(axis @ bloch)
    d_projection = float(axis @ d_bloch)
    probabilities = np.array([(1.0 + projection) / 2.0, (1.0 - projection) / 2.0])
    d_probabilities = np.array([d_projection / 2.0, -d_projection / 2.0])
    safe = np.clip(probabilities, 1e-12, None)
    return float(np.sum(d_probabilities ** 2 / safe))


def _coherent_bloch(sigma: float, radius: float) -> np.ndarray:
    return radius * np.array([math.sin(sigma), 0.0, math.cos(sigma)])


def _coherent_d_bloch(sigma: float, radius: float) -> np.ndarray:
    return radius * np.array([math.cos(sigma), 0.0, -math.sin(sigma)])


def _classical_bloch(sigma: float, radius: float) -> np.ndarray:
    return np.array([0.0, 0.0, radius * math.cos(sigma)])


def _classical_d_bloch(sigma: float, radius: float) -> np.ndarray:
    return np.array([0.0, 0.0, -radius * math.sin(sigma)])


def build_quantum_cramer_rao_estimation_audit(*, radius: float = 0.6) -> dict[str, Any]:
    """Finite quantum Cramer-Rao estimation surrogate with a coherent-vs-classical discriminating control.

    Over a grid of separation values the audit computes, for two encodings of sigma, the quantum Fisher
    information (the estimation ceiling), the classical Fisher information of the decohered pointer
    (z-basis) measurement, and the classical Fisher information of the symmetric-logarithmic-derivative
    eigenbasis measurement (which provably saturates the quantum Cramer-Rao bound). Controls: the
    quantum Cramer-Rao bound is never violated (classical <= quantum everywhere); the SLD-optimal
    measurement saturates the QFI exactly; the pointer measurement STRICTLY loses information for the
    coherent encoding (it fires); and for the classical encoding the pointer measurement is already
    optimal (no gap) -- so the information gap is created by coherence, not by construction.
    """
    tolerance = 1e-9
    pointer_axis = np.array([0.0, 0.0, 1.0])
    sigma_grid = (0.4, 0.7, 1.0, 1.3)

    def family_rows(bloch_fn, d_bloch_fn) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for sigma in sigma_grid:
            bloch = bloch_fn(sigma, radius)
            d_bloch = d_bloch_fn(sigma, radius)
            rho, d_rho = _density(bloch), _d_density(d_bloch)
            qfi = _quantum_fisher_information(rho, d_rho)
            pointer_fi = _classical_fisher_information(bloch, d_bloch, pointer_axis)
            optimal_fi = _classical_fisher_information(bloch, d_bloch, _sld_optimal_axis(rho, d_rho))
            rows.append({
                "sigma": round(sigma, 8),
                "quantum_fisher_information": round(qfi, 10),
                "pointer_basis_fisher_information": round(pointer_fi, 10),
                "sld_optimal_fisher_information": round(optimal_fi, 10),
                "pointer_information_gap": round(qfi - pointer_fi, 10),
                "bound_respected": bool(pointer_fi <= qfi + 1e-9 and optimal_fi <= qfi + 1e-9),
                "optimal_saturates_qfi": bool(abs(optimal_fi - qfi) < 1e-6),
            })
        return rows

    coherent_rows = family_rows(_coherent_bloch, _coherent_d_bloch)
    classical_rows = family_rows(_classical_bloch, _classical_d_bloch)

    controls = {
        "quantum_cramer_rao_bound_never_violated": all(
            row["bound_respected"] for row in coherent_rows + classical_rows
        ),
        "optimal_measurement_saturates_qfi": all(row["optimal_saturates_qfi"] for row in coherent_rows),
        "coherent_pointer_measurement_strictly_loses_information": all(
            row["pointer_information_gap"] > 0.01 for row in coherent_rows
        ),
        "classical_encoding_pointer_is_already_optimal": all(
            abs(row["pointer_information_gap"]) < tolerance for row in classical_rows
        ),
    }
    return {
        "schema": "realizing_emptiness.quantum_cramer_rao_estimation_audit.v1",
        "radius": round(radius, 8),
        "sigma_count": len(sigma_grid),
        "row_count": len(coherent_rows) + len(classical_rows),
        "coherent_rows": coherent_rows,
        "classical_rows": classical_rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
