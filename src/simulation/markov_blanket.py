"""Markov-blanket conditional-independence surrogate for the paper's no-self-evidence thesis.

The paper's titular claim is that a system cannot evidence its own boundary from the inside: the
boundary is a *conditional independence* structure, not a marginal-observable one. This module
operationalises that as a finite, exact Gaussian-graphical-model computation. For a multivariate
Gaussian the precision (inverse covariance) matrix encodes conditional independence directly --
a structural zero in the precision means two variables are independent *given the rest* -- while
the covariance (the marginal the interior can passively observe) is generically dense even when the
precision is sparse.

The headline is therefore a CORRECTNESS DEMONSTRATION, not a method-beats-baseline claim: the
internal/blanket/external separation lives in the precision support and is recovered identically by
reading the exact precision support OR by thresholding partial correlations, yet it is provably
invisible to any threshold on the marginal correlation matrix. That gap -- the boundary is real but
unreadable from the marginal alone -- is the finite-software echo of no-self-evidence.

INTEGRITY: a finite deterministic linear-algebra computation over fixed precision matrices. NOT a
neural, developmental, clinical, practice-efficacy, or physical qFEP claim.
"""

from __future__ import annotations

from typing import Any

import numpy as np


CLAIM_BOUNDARY = (
    "finite deterministic Gaussian-graphical-model conditional-independence computation over fixed "
    "precision matrices; the internal/blanket/external separation is a software linear-algebra result, "
    "not empirical evidence and not a neural, developmental, clinical, practice-efficacy, or physical "
    "qFEP claim"
)

# A fixed positive-definite precision matrix on six variables with a planted Markov boundary:
# internal {0,1}, blanket {2,3}, external {4,5}. The internal-external couplings are structural
# zeros, so internal _||_ external | blanket. The weights are deliberately chosen to sit in the
# CONFOUNDED regime: blanket node 2 strongly bridges both external nodes while internal node 1's
# blanket links are weak, so the induced internal-external *marginal* correlations (e.g. corr(0,4))
# are LARGER in magnitude than a genuine internal-blanket marginal correlation (corr(1,3)). No
# threshold on the marginal correlation matrix can then isolate exactly the blanket, even though the
# conditional-independence (precision) support recovers it exactly -- the finite-software echo of
# no-self-evidence: the interior's passively-observed marginal cannot locate its own boundary.
INTERNAL = (0, 1)
BLANKET = (2, 3)
EXTERNAL = (4, 5)
_EDGES = {
    (0, 1): 0.05,  # internal-internal
    (0, 2): 0.40,  # internal-blanket (strong)
    (1, 2): 0.20,  # internal-blanket (moderate)
    (1, 3): 0.10,  # internal-blanket (weak -- this true edge is masked in the marginal)
    (2, 3): 0.30,  # blanket-blanket
    (2, 4): 0.45,  # blanket-external (strong bridge)
    (2, 5): 0.30,  # blanket-external (strong bridge)
    (3, 5): 0.25,  # blanket-external
    (4, 5): 0.05,  # external-external
}


def _precision_from_edges(edges: dict[tuple[int, int], float], *, size: int = 6, diagonal: float = 2.0) -> np.ndarray:
    precision = np.eye(size) * diagonal
    for (a, b), value in edges.items():
        precision[a, b] = value
        precision[b, a] = value
    return precision


def _correlation_from_precision(precision: np.ndarray) -> np.ndarray:
    covariance = np.linalg.inv(precision)
    scale = np.sqrt(np.diag(covariance))
    return covariance / np.outer(scale, scale)


def _partial_correlation(precision: np.ndarray) -> np.ndarray:
    scale = np.sqrt(np.diag(precision))
    partial = -precision / np.outer(scale, scale)
    np.fill_diagonal(partial, 1.0)
    return partial


def _neighbors(adjacency: np.ndarray, nodes: tuple[int, ...]) -> set[int]:
    """Markov blanket of ``nodes``: graph neighbors of the node set, excluding the set itself."""
    size = adjacency.shape[0]
    recovered: set[int] = set()
    for node in nodes:
        for other in range(size):
            if other not in nodes and adjacency[node, other]:
                recovered.add(other)
    return recovered


def _f1(recovered: set[int], truth: set[int]) -> float:
    if not recovered and not truth:
        return 1.0
    if not recovered or not truth:
        return 0.0
    overlap = len(recovered & truth)
    precision = overlap / len(recovered)
    recall = overlap / len(truth)
    if precision + recall == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def _support_adjacency(matrix: np.ndarray, tolerance: float) -> np.ndarray:
    adjacency = np.abs(matrix) > tolerance
    np.fill_diagonal(adjacency, False)
    return adjacency


def _marginal_recovers_blanket(precision: np.ndarray, truth: set[int], threshold_steps: int) -> bool:
    """True iff some marginal-correlation threshold recovers the blanket of INTERNAL exactly."""
    correlation = _correlation_from_precision(precision)
    for step in range(threshold_steps):
        threshold = step / threshold_steps
        recovered = _neighbors(_support_adjacency(correlation, threshold), INTERNAL)
        if abs(_f1(recovered, truth) - 1.0) < 1e-9:
            return True
    return False


def _perturbation_ensemble(truth: set[int], *, sample_count: int, noise: float, seed: int, threshold_steps: int) -> dict[str, Any]:
    """Perturb the planted edge weights (preserving the structural internal-external zeros) and measure
    how RELIABLY each reading recovers the blanket. The precision support recovers it in every sampled
    instance (the conditional-independence structure is preserved); the marginal-correlation threshold
    recovers it only for a minority of structurally-similar instances. This converts the single-instance
    claim into an honest DISTRIBUTIONAL one: the boundary is reliably visible in conditional independence
    but only contingently in the marginal.
    """
    rng = np.random.default_rng(seed)
    positive_definite = 0
    precision_recoveries = 0
    marginal_recoveries = 0
    for _ in range(sample_count):
        edges = {key: value * (1.0 + noise * float(rng.standard_normal())) for key, value in _EDGES.items()}
        precision = _precision_from_edges(edges)
        if float(np.min(np.linalg.eigvalsh(precision))) <= 1e-6:
            continue
        positive_definite += 1
        if abs(_f1(_neighbors(_support_adjacency(precision, 1e-9), INTERNAL), truth) - 1.0) < 1e-9:
            precision_recoveries += 1
        if _marginal_recovers_blanket(precision, truth, threshold_steps):
            marginal_recoveries += 1
    return {
        "sample_count": sample_count,
        "positive_definite_count": positive_definite,
        "precision_recovery_fraction": round(precision_recoveries / positive_definite, 6),
        "marginal_recovery_fraction": round(marginal_recoveries / positive_definite, 6),
    }


def build_markov_blanket_discovery_audit(*, threshold_steps: int = 500, ensemble_samples: int = 200, ensemble_noise: float = 0.25, ensemble_seed: int = 0) -> dict[str, Any]:
    """Recover a planted Markov boundary from conditional independence, invisible to the marginal.

    The precision support exactly recovers the internal node set's blanket (the blanket nodes), and
    so does a swept threshold on partial correlations -- two precision-aware readings that agree.
    A swept threshold on the *marginal* correlation matrix, by contrast, can never recover the same
    blanket, because the covariance is dense under a sparse precision. Two discriminating controls
    give the audit teeth: a fully-coupled precision matrix yields no nontrivial separation (the
    external set is empty), and an epsilon-coupled precision (internal-external coupling set to a
    tiny but nonzero value) breaks the exact conditional independence so the exact-support detector
    no longer reports a clean separation. All verdicts are measured by set comparison, never asserted.
    """
    tolerance = 1e-9
    precision = _precision_from_edges(_EDGES)
    truth = set(BLANKET)
    correlation = _correlation_from_precision(precision)
    partial = _partial_correlation(precision)

    # Precision-support detector: read the exact conditional-independence graph.
    precision_adjacency = _support_adjacency(precision, tolerance)
    precision_recovered = _neighbors(precision_adjacency, INTERNAL)
    precision_external = {node for node in EXTERNAL if node not in precision_recovered and node not in INTERNAL}
    precision_f1 = _f1(precision_recovered, truth)

    # Anti-strawman baseline 1 (precision-aware): threshold partial correlations. This ALSO recovers
    # the blanket, so the dividing line is precision-versus-covariance, not clever-method-versus-naive.
    thresholds = [round(step / threshold_steps, 6) for step in range(threshold_steps)]
    partial_best_f1 = 0.0
    partial_best_threshold = None
    for threshold in thresholds:
        recovered = _neighbors(_support_adjacency(partial, threshold), INTERNAL)
        score = _f1(recovered, truth)
        if score > partial_best_f1:
            partial_best_f1, partial_best_threshold = score, threshold

    # The marginal-correlation reading the interior can passively observe, swept over a fine grid so
    # the marginal baseline is given its STRONGEST honest threshold (anti-strawman: do not understate
    # the comparator). The best F1 is computed over the full fine grid; only a downsampled set of rows
    # is stored for inspection so the artifact stays compact.
    store_every = max(1, threshold_steps // 40)
    marginal_best_f1 = 0.0
    marginal_best_threshold = None
    marginal_rows = []
    for index, threshold in enumerate(thresholds):
        recovered = _neighbors(_support_adjacency(correlation, threshold), INTERNAL)
        score = _f1(recovered, truth)
        if index % store_every == 0:
            marginal_rows.append({"threshold": threshold, "f1": round(score, 6), "recovered": sorted(recovered)})
        if score > marginal_best_f1:
            marginal_best_f1, marginal_best_threshold = score, threshold

    # Discriminating control 1: fully-coupled precision -> internal is adjacent to everything ->
    # there is no node conditionally independent of the internal set -> no nontrivial blanket.
    dense_edges = {(a, b): 0.2 for a in range(6) for b in range(a + 1, 6)}
    dense_precision = _precision_from_edges(dense_edges, diagonal=3.0)
    dense_recovered = _neighbors(_support_adjacency(dense_precision, tolerance), INTERNAL)
    dense_external = {node for node in range(6) if node not in dense_recovered and node not in INTERNAL}

    # Discriminating control 2: epsilon internal-external coupling -> the conditional independence is
    # only approximate, so the exact-support detector must see internal-external edges and report the
    # exact separation as broken (it is not vacuously satisfied by exact-zero arithmetic).
    epsilon = 1e-3
    epsilon_edges = dict(_EDGES)
    for internal_node in INTERNAL:
        for external_node in EXTERNAL:
            epsilon_edges[(internal_node, external_node)] = epsilon
    epsilon_precision = _precision_from_edges(epsilon_edges)
    epsilon_adjacency = _support_adjacency(epsilon_precision, tolerance)
    epsilon_internal_external_edges = sum(
        1 for i in INTERNAL for e in EXTERNAL if epsilon_adjacency[i, e]
    )

    ensemble = _perturbation_ensemble(
        truth, sample_count=ensemble_samples, noise=ensemble_noise, seed=ensemble_seed, threshold_steps=threshold_steps
    )
    controls = {
        "precision_support_recovers_blanket": bool(abs(precision_f1 - 1.0) < tolerance),
        "internal_external_conditionally_independent": bool(precision_external == set(EXTERNAL)),
        "partial_correlation_threshold_also_recovers_blanket": bool(abs(partial_best_f1 - 1.0) < tolerance),
        "marginal_covariance_threshold_cannot_recover_blanket": bool(marginal_best_f1 < 1.0 - 1e-6),
        "dense_precision_has_no_nontrivial_blanket": bool(len(dense_external) == 0),
        "epsilon_coupling_breaks_exact_separation": bool(epsilon_internal_external_edges == len(INTERNAL) * len(EXTERNAL)),
        # Distributional honesty: the per-instance "marginal cannot recover" result only holds for THIS
        # confounded instance. Across structurally-similar perturbations the precision support recovers
        # the blanket in EVERY positive-definite instance while the marginal recovers it only for a
        # minority -- the boundary is reliably visible in conditional independence but only contingently
        # in the marginal. This control guards against the per-instance claim being over-generalized.
        "precision_recovers_more_reliably_than_marginal_in_ensemble": bool(
            abs(ensemble["precision_recovery_fraction"] - 1.0) < tolerance
            and ensemble["marginal_recovery_fraction"] < ensemble["precision_recovery_fraction"] - 0.2
        ),
    }
    return {
        "schema": "realizing_emptiness.markov_blanket_discovery_audit.v1",
        "variable_count": precision.shape[0],
        "internal_nodes": list(INTERNAL),
        "blanket_nodes": list(BLANKET),
        "external_nodes": list(EXTERNAL),
        "precision_matrix": np.round(precision, 6).tolist(),
        "marginal_correlation_matrix": np.round(correlation, 6).tolist(),
        "precision_support_recovered_blanket": sorted(precision_recovered),
        "precision_support_f1": round(precision_f1, 6),
        "partial_correlation_best_f1": round(partial_best_f1, 6),
        "partial_correlation_best_threshold": partial_best_threshold,
        "marginal_correlation_best_f1": round(marginal_best_f1, 6),
        "marginal_correlation_best_threshold": marginal_best_threshold,
        "marginal_threshold_rows": marginal_rows,
        "dense_precision_external_set": sorted(dense_external),
        "epsilon_internal_external_edges_detected": epsilon_internal_external_edges,
        "perturbation_ensemble": ensemble,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
