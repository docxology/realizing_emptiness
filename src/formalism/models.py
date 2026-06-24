"""Typed finite surrogates for boundary, QRF, separation-prior, and BMR concepts."""

from __future__ import annotations

from dataclasses import dataclass
from math import log1p
from typing import Any

import numpy as np


@dataclass(frozen=True)
class BoundaryScreen:
    """Finite boundary screen carrying binary observation channels."""

    channel_count: int
    bit_names: tuple[str, ...]

    @classmethod
    def default(cls, channel_count: int = 6) -> "BoundaryScreen":
        """Create a named finite boundary screen."""
        return cls(channel_count=channel_count, bit_names=tuple(f"b{i}" for i in range(channel_count)))

    def validate(self) -> None:
        """Reject malformed boundary screens."""
        if self.channel_count <= 0:
            raise ValueError("channel_count must be positive")
        if len(self.bit_names) != self.channel_count:
            raise ValueError("bit_names length must match channel_count")

    def all_bitstrings(self) -> np.ndarray:
        """Enumerate all binary strings over the boundary."""
        self.validate()
        rows = 2 ** self.channel_count
        values = np.zeros((rows, self.channel_count), dtype=int)
        for row in range(rows):
            bits = [int(bit) for bit in format(row, f"0{self.channel_count}b")]
            values[row, :] = bits
        return values


@dataclass(frozen=True)
class QRFDeployment:
    """A QRF deployment as a semantic sector label per boundary channel."""

    name: str
    sector_labels: tuple[str, ...]
    metacognitive_access: float
    prior_precision: float

    def validate(self, screen: BoundaryScreen) -> None:
        """Check deployment dimensions and parameter ranges."""
        screen.validate()
        if len(self.sector_labels) != screen.channel_count:
            raise ValueError("sector label count must match boundary channel count")
        if not 0.0 <= self.metacognitive_access <= 1.0:
            raise ValueError("metacognitive_access must be in [0, 1]")
        if self.prior_precision < 0:
            raise ValueError("prior_precision must be non-negative")

    @property
    def is_dual(self) -> bool:
        """Return whether the deployment preserves only self/env labels."""
        return set(self.sector_labels) <= {"self", "env"}

    @property
    def flexibility(self) -> float:
        """Operational flexibility score used by the finite surrogate."""
        diversity = len(set(self.sector_labels)) / max(1, len(self.sector_labels))
        return float(0.5 * diversity + 0.5 * self.metacognitive_access)

    def as_dict(self) -> dict[str, Any]:
        """Serialize deployment to JSON-compatible data."""
        return {
            "name": self.name,
            "sector_labels": list(self.sector_labels),
            "metacognitive_access": self.metacognitive_access,
            "prior_precision": self.prior_precision,
            "is_dual": self.is_dual,
            "flexibility": self.flexibility,
        }


@dataclass(frozen=True)
class Sectorisation:
    """Grouped view of a QRF deployment."""

    deployment: str
    groups: dict[str, tuple[int, ...]]

    @classmethod
    def from_deployment(cls, deployment: QRFDeployment) -> "Sectorisation":
        """Build sector-to-channel mapping from channel labels."""
        groups: dict[str, list[int]] = {}
        for index, label in enumerate(deployment.sector_labels):
            groups.setdefault(label, []).append(index)
        return cls(deployment=deployment.name, groups={key: tuple(value) for key, value in groups.items()})

    def as_dict(self) -> dict[str, Any]:
        """Serialize grouped sectorisation."""
        return {"deployment": self.deployment, "groups": {key: list(value) for key, value in self.groups.items()}}


@dataclass(frozen=True)
class SeparationPrior:
    """Structural prior that restricts admissible deployments to dual sectorisations."""

    precision: float
    enforced: bool = True

    def complexity_cost(self) -> float:
        """Return a positive complexity cost for the structural prior."""
        return float(log1p(max(0.0, self.precision)) if self.enforced else 0.0)

    def admissible(self, deployments: tuple[QRFDeployment, ...]) -> tuple[QRFDeployment, ...]:
        """Restrict deployments if the prior remains enforced."""
        if not self.enforced:
            return deployments
        return tuple(deployment for deployment in deployments if deployment.is_dual)


def complexity_kl(posterior: np.ndarray, prior: np.ndarray, *, base: float = 2.0) -> float:
    """Return the categorical KL complexity D_KL[Q(s) || P(s|m)] for eq 11.

    This is the finite, worked complexity term the equation-11 registry row names.
    Both arguments are normalized categorical distributions over the same finite
    state factor (for example the dual self/env posterior versus the sigma prior).
    The result is non-negative and is zero exactly when ``posterior == prior``
    (Gibbs' inequality). Units default to bits (``base=2``).
    """
    q = np.asarray(posterior, dtype=float)
    p = np.asarray(prior, dtype=float)
    if q.shape != p.shape or q.ndim != 1:
        raise ValueError("posterior and prior must be 1-D arrays of the same length")
    if not (np.all(q >= 0.0) and np.all(p >= 0.0)):
        raise ValueError("posterior and prior must be non-negative")
    if not (np.isclose(q.sum(), 1.0) and np.isclose(p.sum(), 1.0)):
        raise ValueError("posterior and prior must each sum to 1")
    support = q > 0.0
    if np.any(p[support] <= 0.0):
        raise ValueError("prior must be positive wherever the posterior has support")
    ratio = q[support] / p[support]
    return float((q[support] * (np.log(ratio) / np.log(base))).sum())


def vfe_noise_insufficient_learning(
    realized: np.ndarray, predicted: np.ndarray, *, base: float = 2.0
) -> dict[str, float]:
    """Decompose a finite VFE-style surprise into noise and insufficient learning (eq 6).

    The paper's equation 6 reads variational free energy as irreducible ``noise`` plus reducible
    ``insufficient learning``. Over a finite categorical observation channel this is the exact
    information-theoretic split: the cross-entropy H(realized, predicted) equals the realized
    entropy H(realized) (irreducible noise) plus the KL divergence D_KL[realized || predicted]
    (the model mismatch a better-learned model would remove). Both arguments are normalized
    categorical distributions; units default to bits.
    """
    realized_dist = np.asarray(realized, dtype=float)
    predicted_dist = np.asarray(predicted, dtype=float)
    if realized_dist.shape != predicted_dist.shape or realized_dist.ndim != 1:
        raise ValueError("realized and predicted must be 1-D arrays of the same length")
    if not (np.all(realized_dist >= 0.0) and np.all(predicted_dist >= 0.0)):
        raise ValueError("distributions must be non-negative")
    if not (np.isclose(realized_dist.sum(), 1.0) and np.isclose(predicted_dist.sum(), 1.0)):
        raise ValueError("distributions must each sum to 1")
    support = realized_dist > 0.0
    if np.any(predicted_dist[support] <= 0.0):
        raise ValueError("predicted must be positive wherever realized has support")
    log_base = np.log(base)
    noise = float(-(realized_dist[support] * (np.log(realized_dist[support]) / log_base)).sum())
    insufficient_learning = complexity_kl(realized_dist, predicted_dist, base=base)
    return {
        "noise_bits": noise,
        "insufficient_learning_bits": insufficient_learning,
        "vfe_bits": noise + insufficient_learning,
    }


@dataclass(frozen=True)
class FreeEnergyTerms:
    """Finite free-energy decomposition used by the surrogate."""

    accuracy: float
    complexity: float
    noise: float = 0.0

    @classmethod
    def from_distributions(
        cls,
        posterior: np.ndarray,
        prior: np.ndarray,
        log_likelihood: np.ndarray,
        *,
        noise: float = 0.0,
        base: float = 2.0,
    ) -> "FreeEnergyTerms":
        """Build VFE terms from finite categorical distributions (eq 11 worked example).

        ``complexity`` is the real KL divergence D_KL[Q||P] and ``accuracy`` is the
        expected log-likelihood <ln P(o|s,m)> = sum_s Q(s) log P(o|s,m), so that the
        free energy is the genuine complexity-minus-accuracy variational bound rather
        than a hand-set scalar pair.
        """
        q = np.asarray(posterior, dtype=float)
        ll = np.asarray(log_likelihood, dtype=float)
        if q.shape != ll.shape:
            raise ValueError("log_likelihood must match the posterior shape")
        complexity = complexity_kl(q, prior, base=base)
        accuracy = float((q * ll).sum())
        return cls(accuracy=accuracy, complexity=complexity, noise=noise)

    @property
    def free_energy(self) -> float:
        """Compute F = complexity - accuracy + noise."""
        return float(self.complexity - self.accuracy + self.noise)

    def as_dict(self) -> dict[str, float]:
        """Serialize terms."""
        return {
            "accuracy": float(self.accuracy),
            "complexity": float(self.complexity),
            "noise": float(self.noise),
            "free_energy": self.free_energy,
        }


@dataclass(frozen=True)
class BMRComparison:
    """Bayesian model-reduction comparison between full and reduced models."""

    full_model: FreeEnergyTerms
    reduced_model: FreeEnergyTerms

    @property
    def delta_complexity(self) -> float:
        """Reduced-minus-full complexity."""
        return float(self.reduced_model.complexity - self.full_model.complexity)

    @property
    def delta_accuracy(self) -> float:
        """Reduced-minus-full accuracy."""
        return float(self.reduced_model.accuracy - self.full_model.accuracy)

    @property
    def delta_free_energy(self) -> float:
        """Delta F = Delta complexity - Delta accuracy, with noise folded into F."""
        return float(self.reduced_model.free_energy - self.full_model.free_energy)

    @property
    def prunes_prior(self) -> bool:
        """Return whether the reduced model is preferred."""
        return self.delta_free_energy < 0

    def as_dict(self) -> dict[str, Any]:
        """Serialize BMR comparison."""
        return {
            "full_model": self.full_model.as_dict(),
            "reduced_model": self.reduced_model.as_dict(),
            "delta_complexity": self.delta_complexity,
            "delta_accuracy": self.delta_accuracy,
            "delta_free_energy": self.delta_free_energy,
            "prunes_prior": self.prunes_prior,
        }

