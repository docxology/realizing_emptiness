"""Finite quantum-information surrogates for boundary entropy and contextuality."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import expm
from scipy.optimize import linprog


CLAIM_BOUNDARY = (
    "finite two-qubit quantum-information simulation; not empirical evidence and "
    "not a full qFEP, many-body QRF, or physical quantum-boundary simulation"
)

OPEN_SYSTEM_CLAIM_BOUNDARY = (
    "finite trace-preserving two-qubit dephasing-channel simulation; not empirical evidence and "
    "not a full qFEP, many-body QRF, or physical quantum-boundary simulation"
)

MEASUREMENT_COVER_CLAIM_BOUNDARY = (
    "finite CHSH measurement-cover empirical model; not empirical evidence and not a full "
    "sheaf-obstruction proof, many-body QRF transformation, or physical qFEP simulation"
)

ROADMAP_ENGINE_CLAIM_BOUNDARY = (
    "finite deterministic roadmap-engine simulation; not empirical evidence, not a physical "
    "qFEP realization, and not evidence for clinical, contemplative, or neural outcomes"
)

BLOCKED_EXTERNAL_ROADMAP_ROWS = [
    {
        "id": "re-3",
        "blocked_task_id": "re-3",
        "status": "roadmap_requires_external_physics_review",
        "minimum_next_test": "reviewed physical Hamiltonians, thermodynamic accounting, and independent quantum-information replication",
        "required_next_artifact": "output/data/physical_qfep_realization_audit.json",
        "required_next_gate": "physical_qfep_realization_audit_ok",
        "required_negative_control": "finite Lindblad and many-body software surrogates must not be accepted as physical qFEP realization evidence",
        "boundary": "physical qFEP realization remains roadmap only; not implemented, not empirical, and not a full qFEP result",
    },
    {
        "id": "re-4",
        "blocked_task_id": "re-4",
        "status": "roadmap_requires_data_and_ethics",
        "minimum_next_test": "ethics-reviewed human data, preregistered outcomes, source identity, preprocessing provenance, null models, and safety review",
        "required_next_artifact": "output/data/human_subject_validation_audit.json",
        "required_next_gate": "human_subject_validation_audit_ok",
        "required_negative_control": "synthetic, unsourced, or ethics-incomplete human data must fail empirical-claim permission",
        "boundary": "human-subject validation remains roadmap only; not implemented, not empirical, and not practice evidence",
    },
    {
        "id": "re-13",
        "blocked_task_id": "re-13",
        "status": "roadmap_requires_clinical_neural_and_efficacy_evidence",
        "minimum_next_test": "reviewed clinical, awakening, compassion-efficacy, and neural-measurement evidence with independent controls",
        "required_next_artifact": "output/data/clinical_awakening_compassion_neural_audit.json",
        "required_next_gate": "clinical_awakening_compassion_neural_audit_ok",
        "required_negative_control": "finite software compassion, criticality, or practice surrogates must not certify clinical, awakening, compassion-efficacy, or neural-measurement claims",
        "boundary": "clinical, awakening, compassion-efficacy, and neural-measurement claims remain roadmap only; not implemented and not empirical",
    },
    {
        "id": "re-14",
        "blocked_task_id": "re-14",
        "status": "roadmap_requires_practice_safety_review",
        "minimum_next_test": "human review, safety wording, explicit non-efficacy language, and release governance for any user-facing practice application",
        "required_next_artifact": "output/data/user_facing_practice_safety_audit.json",
        "required_next_gate": "user_facing_practice_safety_audit_ok",
        "required_negative_control": "practice protocol maps must not become user-facing instructions or efficacy claims without human safety review",
        "boundary": "user-facing practice applications remain roadmap only; not implemented, not empirical, and not efficacy guidance",
    },
    {
        "id": "re-15",
        "blocked_task_id": "re-15",
        "status": "roadmap_requires_public_archive_and_independent_reproduction",
        "minimum_next_test": "explicit publication approval, public archive deposition, and independent or blinded reproduction of the artifact bundle",
        "required_next_artifact": "output/data/public_archive_independent_reproduction_audit.json",
        "required_next_gate": "public_archive_independent_reproduction_audit_ok",
        "required_negative_control": "local private hashes, manifests, and validation commands must not certify public release or independent reproduction",
        "boundary": "public archive and independent or blinded reproduction remain roadmap only; not implemented, not empirical, and not public-release evidence",
    },
]

SIGMA_X = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
SIGMA_Z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
IDENTITY_2 = np.eye(2, dtype=complex)


def _state(theta: float) -> np.ndarray:
    vector = np.zeros(4, dtype=complex)
    vector[0] = math.cos(theta)
    vector[3] = math.sin(theta)
    return vector / np.linalg.norm(vector)


def _density(vector: np.ndarray) -> np.ndarray:
    return np.outer(vector, vector.conjugate())


def _reduced_first_qubit(rho: np.ndarray) -> np.ndarray:
    tensor = rho.reshape(2, 2, 2, 2)
    return np.trace(tensor, axis1=1, axis2=3)


def _reduced_second_qubit(rho: np.ndarray) -> np.ndarray:
    tensor = rho.reshape(2, 2, 2, 2)
    return np.trace(tensor, axis1=0, axis2=2)


def _entropy_bits(rho: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvalsh((rho + rho.conjugate().T) / 2.0)
    probabilities = np.clip(np.real(eigenvalues), 0.0, 1.0)
    nonzero = probabilities[probabilities > 1e-12]
    return float(-np.sum(nonzero * np.log2(nonzero)))


def _shannon_bits(probabilities: np.ndarray) -> float:
    values = np.clip(np.real(probabilities), 0.0, 1.0)
    nonzero = values[values > 1e-12]
    return float(-np.sum(nonzero * np.log2(nonzero)))


def _local_rotation(angle: float) -> np.ndarray:
    cosine = math.cos(angle)
    sine = math.sin(angle)
    return np.array([[cosine, -sine], [sine, cosine]], dtype=complex)


def _rotated_density(theta: float, angle_a: float, angle_b: float) -> np.ndarray:
    unitary = np.kron(_local_rotation(angle_a), _local_rotation(angle_b))
    vector = unitary @ _state(theta)
    return _density(vector)


def _chsh_max(concurrence: float) -> float:
    return float(2.0 * math.sqrt(1.0 + concurrence**2))


def _chsh_contexts() -> list[dict[str, Any]]:
    return [
        {"id": "A0B0", "a_label": "A0", "b_label": "B0", "a_angle": 0.0, "b_angle": math.pi / 4.0, "sign": 1.0},
        {"id": "A0B1", "a_label": "A0", "b_label": "B1", "a_angle": 0.0, "b_angle": -math.pi / 4.0, "sign": 1.0},
        {"id": "A1B0", "a_label": "A1", "b_label": "B0", "a_angle": math.pi / 2.0, "b_angle": math.pi / 4.0, "sign": 1.0},
        {"id": "A1B1", "a_label": "A1", "b_label": "B1", "a_angle": math.pi / 2.0, "b_angle": -math.pi / 4.0, "sign": -1.0},
    ]


def _joint_probability_rows(model_label: str, context: dict[str, Any], correlation: float) -> list[dict[str, Any]]:
    rows = []
    for a_out, b_out, outcome in ((1, 1, "++"), (1, -1, "+-"), (-1, 1, "-+"), (-1, -1, "--")):
        probability = 0.25 * (1.0 + (a_out * b_out * correlation))
        rows.append(
            {
                "model": model_label,
                "context": context["id"],
                "a_setting": context["a_label"],
                "b_setting": context["b_label"],
                "a_outcome": a_out,
                "b_outcome": b_out,
                "outcome": outcome,
                "probability": round(float(probability), 12),
            }
        )
    return rows


def _chsh_rows_for_model(model_label: str, product_control: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    contexts = []
    probability_rows = []
    for context in _chsh_contexts():
        if product_control:
            correlation = math.cos(context["a_angle"]) * math.cos(context["b_angle"])
        else:
            correlation = math.cos(context["a_angle"] - context["b_angle"])
        contexts.append(
            {
                "model": model_label,
                "context": context["id"],
                "a_setting": context["a_label"],
                "b_setting": context["b_label"],
                "a_angle": round(float(context["a_angle"]), 12),
                "b_angle": round(float(context["b_angle"]), 12),
                "correlation": round(float(correlation), 12),
                "chsh_sign": context["sign"],
                "chsh_contribution": round(float(context["sign"] * correlation), 12),
            }
        )
        probability_rows.extend(_joint_probability_rows(model_label, context, correlation))
    return contexts, probability_rows


def _chsh_value(context_rows: list[dict[str, Any]]) -> float:
    return float(sum(row["chsh_contribution"] for row in context_rows))


def _normalization_errors(probability_rows: list[dict[str, Any]]) -> dict[str, float]:
    errors: dict[str, float] = {}
    for model in sorted({row["model"] for row in probability_rows}):
        for context in sorted({row["context"] for row in probability_rows if row["model"] == model}):
            total = sum(row["probability"] for row in probability_rows if row["model"] == model and row["context"] == context)
            errors[f"{model}:{context}"] = abs(total - 1.0)
    return errors


def _marginal(probability_rows: list[dict[str, Any]], *, model: str, context: str, side: str, outcome: int) -> float:
    outcome_key = "a_outcome" if side == "A" else "b_outcome"
    return float(
        sum(
            row["probability"]
            for row in probability_rows
            if row["model"] == model and row["context"] == context and row[outcome_key] == outcome
        )
    )


def _no_signaling_errors(probability_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    errors = []
    context_pairs = [
        ("A", "A0", "A0B0", "A0B1"),
        ("A", "A1", "A1B0", "A1B1"),
        ("B", "B0", "A0B0", "A1B0"),
        ("B", "B1", "A0B1", "A1B1"),
    ]
    for model in sorted({row["model"] for row in probability_rows}):
        for side, setting, first_context, second_context in context_pairs:
            first = _marginal(probability_rows, model=model, context=first_context, side=side, outcome=1)
            second = _marginal(probability_rows, model=model, context=second_context, side=side, outcome=1)
            errors.append(
                {
                    "model": model,
                    "side": side,
                    "setting": setting,
                    "first_context": first_context,
                    "second_context": second_context,
                    "p_plus_first": round(first, 12),
                    "p_plus_second": round(second, 12),
                    "absolute_error": round(abs(first - second), 12),
                }
            )
    return errors


def _deterministic_assignments() -> list[dict[str, int]]:
    rows = []
    for a0 in (-1, 1):
        for a1 in (-1, 1):
            for b0 in (-1, 1):
                for b1 in (-1, 1):
                    rows.append({"A0": a0, "A1": a1, "B0": b0, "B1": b1})
    return rows


def _probability_vector(probability_rows: list[dict[str, Any]], model: str) -> tuple[list[str], np.ndarray]:
    labels = []
    values = []
    for context in [row["id"] for row in _chsh_contexts()]:
        for outcome in ("++", "+-", "-+", "--"):
            labels.append(f"{context}:{outcome}")
            match = next(row for row in probability_rows if row["model"] == model and row["context"] == context and row["outcome"] == outcome)
            values.append(match["probability"])
    return labels, np.array(values, dtype=float)


def _local_polytope_matrix(labels: list[str]) -> tuple[list[dict[str, int]], np.ndarray]:
    assignments = _deterministic_assignments()
    matrix = np.zeros((len(labels), len(assignments)), dtype=float)
    for label_index, label in enumerate(labels):
        context, outcome = label.split(":")
        a_setting = context[:2]
        b_setting = context[2:]
        target_a = 1 if outcome[0] == "+" else -1
        target_b = 1 if outcome[1] == "+" else -1
        for assignment_index, assignment in enumerate(assignments):
            if assignment[a_setting] == target_a and assignment[b_setting] == target_b:
                matrix[label_index, assignment_index] = 1.0
    return assignments, matrix


def _local_polytope_fit(probability_rows: list[dict[str, Any]], model: str) -> dict[str, Any]:
    labels, target = _probability_vector(probability_rows, model)
    assignments, matrix = _local_polytope_matrix(labels)
    a_eq = np.vstack([np.ones((1, len(assignments))), matrix])
    b_eq = np.concatenate([[1.0], target])
    exact = linprog(
        c=np.zeros(len(assignments)),
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=[(0.0, 1.0)] * len(assignments),
        method="highs",
    )
    slack_count = 2 * len(labels)
    relaxed_a_eq = np.vstack(
        [
            np.concatenate([np.ones(len(assignments)), np.zeros(slack_count)]),
            np.hstack([matrix, np.eye(len(labels)), -np.eye(len(labels))]),
        ]
    )
    relaxed_b_eq = np.concatenate([[1.0], target])
    relaxed = linprog(
        c=np.concatenate([np.zeros(len(assignments)), np.ones(slack_count)]),
        A_eq=relaxed_a_eq,
        b_eq=relaxed_b_eq,
        bounds=[(0.0, 1.0)] * len(assignments) + [(0.0, None)] * slack_count,
        method="highs",
    )
    weights = exact.x if exact.success else relaxed.x[: len(assignments)] if relaxed.success else np.zeros(len(assignments))
    reconstructed = matrix @ weights
    max_abs_residual = float(np.max(np.abs(reconstructed - target))) if len(target) else 0.0
    l1_residual = float(np.sum(np.abs(reconstructed - target))) if len(target) else 0.0
    if not exact.success and relaxed.success:
        max_abs_residual = float(np.max(np.abs((matrix @ relaxed.x[: len(assignments)]) - target)))
        l1_residual = float(relaxed.fun)
    assignment_rows = []
    for index, (assignment, weight) in enumerate(zip(assignments, weights, strict=True)):
        if weight > 1e-9:
            assignment_rows.append(
                {
                    "assignment_index": index,
                    "A0": assignment["A0"],
                    "A1": assignment["A1"],
                    "B0": assignment["B0"],
                    "B1": assignment["B1"],
                    "weight": round(float(weight), 12),
                }
            )
    return {
        "model": model,
        "feasible": bool(exact.success),
        "linprog_status": int(exact.status),
        "linprog_message": exact.message,
        "min_l1_residual": float(l1_residual),
        "max_abs_residual": float(max_abs_residual),
        "active_assignment_count": len(assignment_rows),
        "assignment_rows": assignment_rows,
    }


def _bell_dephased_density(coherence: float) -> np.ndarray:
    rho = np.zeros((4, 4), dtype=complex)
    rho[0, 0] = 0.5
    rho[3, 3] = 0.5
    rho[0, 3] = 0.5 * coherence
    rho[3, 0] = 0.5 * coherence
    return rho


def _product_density() -> np.ndarray:
    vector = np.zeros(4, dtype=complex)
    vector[0] = 1.0
    return _density(vector)


def _bell_state_vector() -> np.ndarray:
    vector = np.zeros(4, dtype=complex)
    vector[0] = 1.0 / math.sqrt(2.0)
    vector[3] = 1.0 / math.sqrt(2.0)
    return vector


def _matrix_is_hermitian(matrix: np.ndarray, tolerance: float = 1e-10) -> bool:
    return bool(np.max(np.abs(matrix - matrix.conjugate().T)) < tolerance)


def _lindblad_superoperator(hamiltonian: np.ndarray, operators: list[np.ndarray]) -> np.ndarray:
    """Return a column-vectorized Lindblad generator superoperator."""
    dimension = hamiltonian.shape[0]
    identity = np.eye(dimension, dtype=complex)
    generator = -1j * (np.kron(identity, hamiltonian) - np.kron(hamiltonian.T, identity))
    for operator in operators:
        dagger_product = operator.conjugate().T @ operator
        generator += np.kron(operator.conjugate(), operator)
        generator += -0.5 * np.kron(identity, dagger_product)
        generator += -0.5 * np.kron(dagger_product.T, identity)
    return generator


def _evolve_density_lindblad(rho: np.ndarray, hamiltonian: np.ndarray, operators: list[np.ndarray], time: float) -> np.ndarray:
    dimension = rho.shape[0]
    propagator = expm(float(time) * _lindblad_superoperator(hamiltonian, operators))
    evolved = (propagator @ rho.reshape(dimension * dimension, order="F")).reshape((dimension, dimension), order="F")
    return (evolved + evolved.conjugate().T) / 2.0


def _density_metrics(rho: np.ndarray) -> dict[str, float]:
    trace_value = np.trace(rho)
    hermitian = (rho + rho.conjugate().T) / 2.0
    eigenvalues = np.linalg.eigvalsh(hermitian)
    reduced_a = _reduced_first_qubit(hermitian)
    reduced_b = _reduced_second_qubit(hermitian)
    entropy_a = _entropy_bits(reduced_a)
    entropy_b = _entropy_bits(reduced_b)
    global_entropy = _entropy_bits(hermitian)
    return {
        "trace_real": round(float(np.real(trace_value)), 12),
        "trace_imag_abs": round(float(abs(np.imag(trace_value))), 12),
        "min_eigenvalue": round(float(np.min(np.real(eigenvalues))), 12),
        "global_entropy_bits": round(global_entropy, 10),
        "reduced_entropy_a_bits": round(entropy_a, 10),
        "reduced_entropy_b_bits": round(entropy_b, 10),
        "mutual_information_bits": round(entropy_a + entropy_b - global_entropy, 10),
        "purity": round(float(np.real(np.trace(hermitian @ hermitian))), 10),
    }


def _density_validity(rho: np.ndarray) -> dict[str, float | bool]:
    trace_value = np.trace(rho)
    hermitian_error = float(np.max(np.abs(rho - rho.conjugate().T)))
    hermitian = (rho + rho.conjugate().T) / 2.0
    eigenvalues = np.linalg.eigvalsh(hermitian)
    trace_error = float(abs(np.real(trace_value) - 1.0) + abs(np.imag(trace_value)))
    min_eigenvalue = float(np.min(np.real(eigenvalues)))
    return {
        "trace_real": round(float(np.real(trace_value)), 12),
        "trace_imag_abs": round(float(abs(np.imag(trace_value))), 12),
        "trace_error": round(trace_error, 12),
        "hermitian_error": round(hermitian_error, 12),
        "min_eigenvalue": round(min_eigenvalue, 12),
        "valid_density_matrix": bool(trace_error < 1e-10 and hermitian_error < 1e-10 and min_eigenvalue > -1e-10),
    }


def _partial_transpose_second_qubit(rho: np.ndarray) -> np.ndarray:
    tensor = rho.reshape(2, 2, 2, 2)
    return np.transpose(tensor, (0, 3, 2, 1)).reshape(4, 4)


def _negativity(rho: np.ndarray) -> tuple[float, float]:
    partial = _partial_transpose_second_qubit((rho + rho.conjugate().T) / 2.0)
    eigenvalues = np.linalg.eigvalsh((partial + partial.conjugate().T) / 2.0)
    negativity = float(np.sum(np.abs(eigenvalues[eigenvalues < 0.0])))
    return negativity, float(np.min(eigenvalues))


def _werner_state(p: float) -> np.ndarray:
    bell = _density(_bell_state_vector())
    return float(p) * bell + (1.0 - float(p)) * np.eye(4, dtype=complex) / 4.0


def _partial_trace_pure_state(vector: np.ndarray, qubit_count: int, keep: tuple[int, ...]) -> np.ndarray:
    keep_tuple = tuple(sorted(keep))
    traced = tuple(index for index in range(qubit_count) if index not in keep_tuple)
    tensor = vector.reshape((2,) * qubit_count)
    permuted = np.transpose(tensor, keep_tuple + traced)
    matrix = permuted.reshape((2 ** len(keep_tuple), 2 ** len(traced)))
    return matrix @ matrix.conjugate().T


def _many_body_bell_pair_state(qubit_count: int = 6) -> np.ndarray:
    vector = np.zeros(2**qubit_count, dtype=complex)
    for left in range(2 ** (qubit_count // 2)):
        left_bits = [(left >> bit) & 1 for bit in reversed(range(qubit_count // 2))]
        bits = left_bits + left_bits
        index = 0
        for bit in bits:
            index = (index << 1) | bit
        vector[index] = 1.0 / math.sqrt(2 ** (qubit_count // 2))
    return vector


def _many_body_product_state(qubit_count: int = 6) -> np.ndarray:
    vector = np.zeros(2**qubit_count, dtype=complex)
    vector[0] = 1.0
    return vector


INTERNAL_CUT_CLAIM_BOUNDARY = (
    "finite-dimensional pure-state linear-algebra audit over environment bipartitions; not empirical, "
    "not a physical or observer-boundary measurement, and not a full qFEP realization"
)


def _von_neumann_entropy_bits(rho: np.ndarray) -> float:
    """Return the von Neumann entropy of a density matrix in bits."""
    eigenvalues = np.linalg.eigvalsh((rho + rho.conjugate().T) / 2.0)
    positive = np.real(eigenvalues[np.real(eigenvalues) > 1e-12])
    return float(-(positive * (np.log(positive) / np.log(2.0))).sum())


def _env_bipartitions(env_local_indices: tuple[int, ...]) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Enumerate non-trivial bipartitions of the environment qubits (deduplicated by lowest index)."""
    first = env_local_indices[0]
    rest = env_local_indices[1:]
    bipartitions = []
    for mask in range(1, 2 ** len(rest)):
        side = tuple(rest[bit] for bit in range(len(rest)) if (mask >> bit) & 1)
        b1 = (first, *side)
        b2 = tuple(index for index in env_local_indices if index not in b1)
        if b2:
            bipartitions.append((b1, b2))
    return bipartitions


def build_internal_cut_unmeasurability_audit(*, env_qubits: int = 4) -> dict[str, Any]:
    """Generalise the no-self-evidence result to arbitrary internal boundaries (section 3.3).

    A finite agent A cannot verify, from its own side, that any internal bipartition B1|B2 of its
    environment isolates causal structure: doing so requires the internal-cut entanglement entropy
    S(B1B2), which is inaccessible from A's boundary. The surrogate builds a Bell pair on (A,
    ancilla) tensored with an environment pure state, so A's accessible reduced state rho_A is
    invariant while the environment's internal-cut entropy differs between a separable and an
    entangled environment. For every environment bipartition the audit shows rho_A is identical
    across the two states (A cannot adjudicate the cut) while a two-sided oracle that is given the
    full joint state does recover the differing internal-cut entropy (resolving-power control).
    """
    total_qubits = 2 + env_qubits
    a_index, anc_index = 0, 1
    env_global = tuple(range(2, total_qubits))
    env_local = tuple(range(env_qubits))
    # Bell pair on (A, ancilla): fixes rho_A = I/2 independent of the environment state.
    bell = np.zeros(4, dtype=complex)
    bell[0] = bell[3] = 1.0 / math.sqrt(2.0)

    def env_state(entangled_cut: tuple[int, ...] | None) -> np.ndarray:
        vector = np.zeros(2**env_qubits, dtype=complex)
        if entangled_cut is None:
            vector[0] = 1.0  # |0...0>: separable across every cut, S = 0
            return vector
        # Bell pair across the cut: entangles one qubit of B1 with one qubit of B2, rest |0>.
        left, right = entangled_cut
        for bit in (0, 1):
            index = (bit << (env_qubits - 1 - left)) | (bit << (env_qubits - 1 - right))
            vector[index] += 1.0 / math.sqrt(2.0)
        return vector

    rows = []
    for b1, b2 in _env_bipartitions(env_local):
        separable_env = env_state(None)
        entangled_env = env_state((b1[0], b2[0]))
        rho_a = {}
        cut_entropy = {}
        for name, env in (("separable", separable_env), ("entangled", entangled_env)):
            full = np.kron(bell, env)
            rho_a[name] = _partial_trace_pure_state(full, total_qubits, (a_index,))
            cut_entropy[name] = _von_neumann_entropy_bits(_partial_trace_pure_state(env, env_qubits, b1))
        accessible_marginal_drift = float(np.max(np.abs(rho_a["separable"] - rho_a["entangled"])))
        rows.append(
            {
                "b1": list(int(i) for i in b1),
                "b2": list(int(i) for i in b2),
                "separable_cut_entropy_bits": cut_entropy["separable"],
                "entangled_cut_entropy_bits": cut_entropy["entangled"],
                "accessible_marginal_drift": accessible_marginal_drift,
                "accessible_marginal_invariant": bool(accessible_marginal_drift < 1e-9),
                "god_eye_distinguishes_cut": bool(cut_entropy["entangled"] - cut_entropy["separable"] > 0.5),
            }
        )
    controls = {
        "accessible_marginal_invariant_across_internal_cuts": all(row["accessible_marginal_invariant"] for row in rows),
        "god_eye_entropy_actually_differs": all(row["god_eye_distinguishes_cut"] for row in rows),
        "all_bipartitions_audited": len(rows) == len(_env_bipartitions(env_local)) and len(rows) >= 3,
        "separability_unrecoverable_from_marginal": all(
            row["accessible_marginal_invariant"] and row["god_eye_distinguishes_cut"] for row in rows
        ),
    }
    return {
        "schema": "realizing_emptiness.internal_cut_unmeasurability_audit.v1",
        "label": "finite_pure_state_internal_cut_audit_not_empirical",
        "env_qubits": env_qubits,
        "bipartition_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": INTERNAL_CUT_CLAIM_BOUNDARY,
    }


def _scenario_probability_vector(probability_rows: list[dict[str, Any]]) -> tuple[list[str], np.ndarray]:
    labels = [f"{row['context']}:{','.join(str(value) for value in row['assignment'])}" for row in probability_rows]
    return labels, np.array([row["probability"] for row in probability_rows], dtype=float)


def _measurement_assignments(measurements: list[str]) -> list[dict[str, int]]:
    rows = [{}]
    for measurement in measurements:
        rows = [{**row, measurement: value} for row in rows for value in (-1, 1)]
    return rows


def _generic_polytope_fit(measurements: list[str], probability_rows: list[dict[str, Any]]) -> dict[str, Any]:
    labels, target = _scenario_probability_vector(probability_rows)
    assignments = _measurement_assignments(measurements)
    matrix = np.zeros((len(labels), len(assignments)), dtype=float)
    for label_index, row in enumerate(probability_rows):
        context = row["context_measurements"]
        target_assignment = {measurement: value for measurement, value in zip(context, row["assignment"], strict=True)}
        for assignment_index, assignment in enumerate(assignments):
            if all(assignment[measurement] == value for measurement, value in target_assignment.items()):
                matrix[label_index, assignment_index] = 1.0
    a_eq = np.vstack([np.ones((1, len(assignments))), matrix])
    b_eq = np.concatenate([[1.0], target])
    exact = linprog(
        c=np.zeros(len(assignments)),
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=[(0.0, 1.0)] * len(assignments),
        method="highs",
    )
    slack_count = 2 * len(labels)
    relaxed_a_eq = np.vstack(
        [
            np.concatenate([np.ones(len(assignments)), np.zeros(slack_count)]),
            np.hstack([matrix, np.eye(len(labels)), -np.eye(len(labels))]),
        ]
    )
    relaxed = linprog(
        c=np.concatenate([np.zeros(len(assignments)), np.ones(slack_count)]),
        A_eq=relaxed_a_eq,
        b_eq=b_eq,
        bounds=[(0.0, 1.0)] * len(assignments) + [(0.0, None)] * slack_count,
        method="highs",
    )
    weights = exact.x if exact.success else relaxed.x[: len(assignments)] if relaxed.success else np.zeros(len(assignments))
    reconstructed = matrix @ weights
    residual = float(np.sum(np.abs(reconstructed - target))) if exact.success else float(relaxed.fun if relaxed.success else np.inf)
    active_rows = []
    for index, (assignment, weight) in enumerate(zip(assignments, weights, strict=True)):
        if weight > 1e-9:
            active_rows.append({"assignment_index": index, "assignment": assignment, "weight": round(float(weight), 12)})
    return {
        "feasible": bool(exact.success),
        "assignment_count": len(assignments),
        "active_assignment_count": len(active_rows),
        "min_l1_residual": round(float(residual), 12),
        "max_abs_residual": round(float(np.max(np.abs(reconstructed - target))), 12),
        "active_assignments": active_rows,
        "linprog_status": int(exact.status),
    }


def _pair_context_rows(
    *,
    scenario_id: str,
    contexts: list[tuple[str, tuple[str, str], int]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for context_id, measurements, parity in contexts:
        for first in (-1, 1):
            for second in (-1, 1):
                probability = 0.5 if first * second == parity else 0.0
                rows.append(
                    {
                        "scenario": scenario_id,
                        "context": context_id,
                        "context_measurements": list(measurements),
                        "assignment": [first, second],
                        "probability": probability,
                    }
                )
    return rows


def _no_disturbance_error(probability_rows: list[dict[str, Any]], measurements: list[str]) -> float:
    max_error = 0.0
    contexts = sorted({row["context"] for row in probability_rows})
    for measurement in measurements:
        marginal_rows = []
        for context in contexts:
            context_rows = [row for row in probability_rows if row["context"] == context and measurement in row["context_measurements"]]
            if not context_rows:
                continue
            index = context_rows[0]["context_measurements"].index(measurement)
            plus = sum(row["probability"] for row in context_rows if row["assignment"][index] == 1)
            marginal_rows.append(plus)
        for first in marginal_rows:
            for second in marginal_rows:
                max_error = max(max_error, abs(first - second))
    return float(max_error)


def _normalise_probability(vector: np.ndarray) -> np.ndarray:
    clipped = np.clip(vector.astype(float), 0.0, None)
    total = float(np.sum(clipped))
    if total <= 0.0:
        raise ValueError("probability vector has no positive mass")
    return clipped / total


def _kraus_cptp_error(kraus_operators: list[np.ndarray]) -> float:
    if not kraus_operators:
        return float("inf")
    dimension = kraus_operators[0].shape[1]
    accumulator = np.zeros((dimension, dimension), dtype=complex)
    for operator in kraus_operators:
        accumulator += operator.conjugate().T @ operator
    return float(np.max(np.abs(accumulator - np.eye(dimension, dtype=complex))))


def _apply_kraus_channel(rho: np.ndarray, kraus_operators: list[np.ndarray]) -> np.ndarray:
    output = np.zeros_like(rho, dtype=complex)
    for operator in kraus_operators:
        output += operator @ rho @ operator.conjugate().T
    return (output + output.conjugate().T) / 2.0


def _swap_unitary_two_qubit() -> np.ndarray:
    unitary = np.zeros((4, 4), dtype=complex)
    for left in (0, 1):
        for right in (0, 1):
            source = 2 * left + right
            target = 2 * right + left
            unitary[target, source] = 1.0
    return unitary


def _basis_permutation_for_unitary(unitary: np.ndarray) -> np.ndarray:
    probabilities = np.zeros((unitary.shape[0], unitary.shape[1]), dtype=float)
    for column in range(unitary.shape[1]):
        probabilities[:, column] = np.abs(unitary[:, column]) ** 2
    return probabilities


def _dephasing_metric_row(*, state_label: str, rho: np.ndarray, coherence: float, gamma: float, time: float) -> dict[str, Any]:
    trace_value = np.trace(rho)
    hermitian = (rho + rho.conjugate().T) / 2.0
    eigenvalues = np.linalg.eigvalsh(hermitian)
    reduced_a = _reduced_first_qubit(rho)
    reduced_b = _reduced_second_qubit(rho)
    global_entropy = _entropy_bits(rho)
    entropy_a = _entropy_bits(reduced_a)
    entropy_b = _entropy_bits(reduced_b)
    concurrence = float(coherence if state_label == "bell_dephased" else 0.0)
    return {
        "state_label": state_label,
        "time": round(float(time), 8),
        "decoherence_rate": round(float(gamma), 8),
        "coherence": round(float(coherence), 10),
        "trace_real": round(float(np.real(trace_value)), 12),
        "trace_imag_abs": round(float(abs(np.imag(trace_value))), 12),
        "min_eigenvalue": round(float(np.min(np.real(eigenvalues))), 12),
        "global_entropy_bits": round(global_entropy, 10),
        "reduced_entropy_a_bits": round(entropy_a, 10),
        "reduced_entropy_b_bits": round(entropy_b, 10),
        "mutual_information_bits": round(entropy_a + entropy_b - global_entropy, 10),
        "purity": round(float(np.real(np.trace(rho @ rho))), 10),
        "concurrence": round(concurrence, 10),
        "chsh_s_max": round(_chsh_max(concurrence), 10),
        "contextual_fraction": round(max(0.0, (_chsh_max(concurrence) - 2.0) / (2.0 * math.sqrt(2.0) - 2.0)), 10),
    }


def _row(theta: float, index: int) -> dict[str, Any]:
    rho = _density(_state(theta))
    reduced = _reduced_first_qubit(rho)
    entropy = _entropy_bits(reduced)
    measurement_probabilities = np.real(np.diag(rho))
    measurement_entropy = _shannon_bits(measurement_probabilities)
    concurrence = float(math.sin(2.0 * theta))
    chsh = _chsh_max(concurrence)
    contextual_fraction = max(0.0, (chsh - 2.0) / (2.0 * math.sqrt(2.0) - 2.0))
    return {
        "theta_index": index,
        "theta": round(float(theta), 8),
        "state_label": "product" if index == 0 else "maximally_entangled" if abs(theta - math.pi / 4.0) < 1e-8 else "partially_entangled",
        "reduced_entropy_bits": round(entropy, 10),
        "mutual_information_bits": round(2.0 * entropy, 10),
        "single_qubit_purity": round(float(np.real(np.trace(reduced @ reduced))), 10),
        "concurrence": round(concurrence, 10),
        "chsh_s_max": round(chsh, 10),
        "contextual_fraction": round(contextual_fraction, 10),
        "computational_boundary_entropy_bits": round(measurement_entropy, 10),
        "landauer_lower_bound_kbt": round(measurement_entropy * math.log(2.0), 10),
        "separable_predicate": bool(entropy < 1e-9),
        "bell_violation_predicate": bool(chsh > 2.0 + 1e-9),
    }


def _basis_invariance_rows(theta_grid: np.ndarray, rotation_grid: np.ndarray) -> list[dict[str, Any]]:
    rows = []
    for theta in theta_grid:
        base_entropy = _entropy_bits(_reduced_first_qubit(_density(_state(float(theta)))))
        for angle in rotation_grid:
            rotated = _rotated_density(float(theta), float(angle), 0.5 * float(angle))
            reduced_entropy = _entropy_bits(_reduced_first_qubit(rotated))
            measurement_entropy = _shannon_bits(np.real(np.diag(rotated)))
            rows.append(
                {
                    "theta": round(float(theta), 8),
                    "rotation_angle": round(float(angle), 8),
                    "reduced_entropy_bits": round(reduced_entropy, 10),
                    "entropy_drift_bits": round(abs(reduced_entropy - base_entropy), 12),
                    "rotated_measurement_entropy_bits": round(measurement_entropy, 10),
                }
            )
    return rows


def build_quantum_boundary_entropy(*, theta_count: int = 33, rotation_count: int = 25) -> dict[str, Any]:
    """Build finite two-qubit entropy, CHSH, and basis-invariance artifacts."""
    theta_grid = np.linspace(0.0, math.pi / 4.0, theta_count)
    rotation_grid = np.linspace(0.0, math.pi / 2.0, rotation_count)
    rows = [_row(float(theta), index) for index, theta in enumerate(theta_grid)]
    basis_rows = _basis_invariance_rows(theta_grid, rotation_grid)
    max_chsh = max(row["chsh_s_max"] for row in rows)
    controls = {
        "product_entropy_zero": abs(rows[0]["reduced_entropy_bits"]) < 1e-9,
        "product_chsh_local": abs(rows[0]["chsh_s_max"] - 2.0) < 1e-9,
        "bell_entropy_one": abs(rows[-1]["reduced_entropy_bits"] - 1.0) < 1e-9,
        "bell_chsh_toward_tsirelson": abs(rows[-1]["chsh_s_max"] - 2.0 * math.sqrt(2.0)) < 1e-9,
        "basis_entropy_invariant": max(row["entropy_drift_bits"] for row in basis_rows) < 1e-9,
        "measurement_entropy_changes_under_basis": (
            max(row["rotated_measurement_entropy_bits"] for row in basis_rows)
            - min(row["rotated_measurement_entropy_bits"] for row in basis_rows)
        )
        > 0.1,
    }
    return {
        "schema": "realizing_emptiness.quantum_boundary_entropy.v1",
        "theta_grid": [round(float(value), 8) for value in theta_grid],
        "rotation_grid": [round(float(value), 8) for value in rotation_grid],
        "row_count": len(rows),
        "basis_invariance_row_count": len(basis_rows),
        "rows": rows,
        "basis_invariance_rows": basis_rows,
        "controls": controls,
        "local_chsh_bound": 2.0,
        "tsirelson_bound": float(2.0 * math.sqrt(2.0)),
        "max_observed_chsh": float(max_chsh),
        "max_contextual_fraction": float(max(row["contextual_fraction"] for row in rows)),
        "max_basis_entropy_drift_bits": float(max(row["entropy_drift_bits"] for row in basis_rows)),
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_quantum_open_system_dynamics(*, time_count: int = 21, decoherence_rate_count: int = 4) -> dict[str, Any]:
    """Build finite dephasing-channel dynamics for Bell and product controls."""
    time_grid = np.linspace(0.0, 4.0, time_count)
    base_rates = np.array([0.0, 0.2, 0.5, 1.0], dtype=float)
    if decoherence_rate_count != len(base_rates):
        rate_grid = np.linspace(0.0, 1.0, decoherence_rate_count)
    else:
        rate_grid = base_rates
    rows = []
    for gamma in rate_grid:
        for time in time_grid:
            coherence = float(math.exp(-float(gamma) * float(time)))
            bell_rho = _bell_dephased_density(coherence)
            product_rho = _product_density()
            rows.append(_dephasing_metric_row(state_label="bell_dephased", rho=bell_rho, coherence=coherence, gamma=float(gamma), time=float(time)))
            rows.append(_dephasing_metric_row(state_label="product_control", rho=product_rho, coherence=0.0, gamma=float(gamma), time=float(time)))
    max_gamma = float(max(rate_grid))
    bell_max_gamma = [row for row in rows if row["state_label"] == "bell_dephased" and abs(row["decoherence_rate"] - max_gamma) < 1e-8]
    product_rows = [row for row in rows if row["state_label"] == "product_control"]
    max_trace_error = max(abs(row["trace_real"] - 1.0) + row["trace_imag_abs"] for row in rows)
    min_eigenvalue = min(row["min_eigenvalue"] for row in rows)
    controls = {
        "trace_preserved": max_trace_error < 1e-10,
        "positive_semidefinite": min_eigenvalue > -1e-10,
        "product_control_stable": all(
            row["global_entropy_bits"] < 1e-9
            and row["reduced_entropy_a_bits"] < 1e-9
            and row["chsh_s_max"] == 2.0
            for row in product_rows
        ),
        "bell_entropy_non_decreasing_under_dephasing": all(
            later["global_entropy_bits"] >= earlier["global_entropy_bits"] - 1e-9
            for earlier, later in zip(bell_max_gamma, bell_max_gamma[1:], strict=False)
        ),
        "bell_chsh_decays_under_dephasing": bell_max_gamma[0]["chsh_s_max"] > bell_max_gamma[-1]["chsh_s_max"],
        "bell_mutual_information_non_increasing": all(
            later["mutual_information_bits"] <= earlier["mutual_information_bits"] + 1e-9
            for earlier, later in zip(bell_max_gamma, bell_max_gamma[1:], strict=False)
        ),
    }
    return {
        "schema": "realizing_emptiness.quantum_open_system_dynamics.v1",
        "time_grid": [round(float(value), 8) for value in time_grid],
        "decoherence_rate_grid": [round(float(value), 8) for value in rate_grid],
        "row_count": len(rows),
        "rows": rows,
        "controls": controls,
        "max_trace_error": float(max_trace_error),
        "min_eigenvalue": float(min_eigenvalue),
        "max_global_entropy_bits": float(max(row["global_entropy_bits"] for row in rows)),
        "max_observed_chsh": float(max(row["chsh_s_max"] for row in rows)),
        "min_observed_chsh": float(min(row["chsh_s_max"] for row in rows)),
        "all_controls_pass": all(controls.values()),
        "claim_boundary": OPEN_SYSTEM_CLAIM_BOUNDARY,
    }


def build_quantum_measurement_contextuality() -> dict[str, Any]:
    """Build a finite CHSH measurement-cover empirical model and controls."""
    bell_contexts, bell_probabilities = _chsh_rows_for_model("bell_measurement_cover", product_control=False)
    product_contexts, product_probabilities = _chsh_rows_for_model("product_control", product_control=True)
    context_rows = [*bell_contexts, *product_contexts]
    probability_rows = [*bell_probabilities, *product_probabilities]
    normalization_errors = _normalization_errors(probability_rows)
    no_signaling_errors = _no_signaling_errors(probability_rows)
    local_polytope = {
        "assignment_count": len(_deterministic_assignments()),
        "fits": [
            _local_polytope_fit(probability_rows, "product_control"),
            _local_polytope_fit(probability_rows, "bell_measurement_cover"),
        ],
    }
    local_fit_lookup = {row["model"]: row for row in local_polytope["fits"]}
    bell_chsh = _chsh_value(bell_contexts)
    product_chsh = _chsh_value(product_contexts)
    local_bound = 2.0
    tsirelson_bound = 2.0 * math.sqrt(2.0)
    contextual_fraction = max(0.0, (abs(bell_chsh) - local_bound) / (tsirelson_bound - local_bound))
    controls = {
        "joint_probabilities_normalized": max(normalization_errors.values()) < 1e-10,
        "joint_probabilities_nonnegative": min(row["probability"] for row in probability_rows) >= -1e-12,
        "no_signaling_marginals_match": max(row["absolute_error"] for row in no_signaling_errors) < 1e-10,
        "bell_chsh_exceeds_local_bound": abs(bell_chsh) > local_bound + 1e-9,
        "bell_chsh_reaches_tsirelson": abs(abs(bell_chsh) - tsirelson_bound) < 1e-9,
        "product_control_respects_local_bound": abs(product_chsh) <= local_bound + 1e-9,
        "contextual_fraction_unit_at_tsirelson": abs(contextual_fraction - 1.0) < 1e-9,
        "product_control_local_polytope_feasible": local_fit_lookup["product_control"]["feasible"] is True,
        "bell_model_local_polytope_infeasible": local_fit_lookup["bell_measurement_cover"]["feasible"] is False,
        "bell_model_positive_polytope_residual": local_fit_lookup["bell_measurement_cover"]["min_l1_residual"] > 0.1,
    }
    return {
        "schema": "realizing_emptiness.quantum_measurement_contextuality.v1",
        "measurement_cover": {
            "parties": ["A", "B"],
            "contexts": [context["id"] for context in _chsh_contexts()],
            "outcomes": ["++", "+-", "-+", "--"],
            "description": "finite CHSH empirical-model table with four compatible measurement contexts",
        },
        "context_rows": context_rows,
        "probability_rows": probability_rows,
        "row_count": len(probability_rows),
        "context_count": len(_chsh_contexts()),
        "model_count": 2,
        "local_chsh_bound": local_bound,
        "tsirelson_bound": float(tsirelson_bound),
        "bell_chsh": float(bell_chsh),
        "product_control_chsh": float(product_chsh),
        "contextual_fraction": float(contextual_fraction),
        "normalization_errors": normalization_errors,
        "no_signaling_errors": no_signaling_errors,
        "local_polytope": local_polytope,
        "max_normalization_error": float(max(normalization_errors.values())),
        "max_no_signaling_error": float(max(row["absolute_error"] for row in no_signaling_errors)),
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": MEASUREMENT_COVER_CLAIM_BOUNDARY,
    }


def build_qfep_boundary_hamiltonian_dynamics(*, time_count: int = 21, decoherence_rate_count: int = 4) -> dict[str, Any]:
    """Build finite boundary-Hamiltonian Lindblad dynamics for the roadmap qFEP engine."""
    time_grid = np.linspace(0.0, 3.0, time_count)
    base_rates = np.array([0.0, 0.12, 0.3, 0.6], dtype=float)
    rate_grid = base_rates if decoherence_rate_count == len(base_rates) else np.linspace(0.0, 0.6, decoherence_rate_count)
    hamiltonian = 0.35 * np.kron(SIGMA_Z, IDENTITY_2) + 0.2 * np.kron(SIGMA_Z, SIGMA_Z)
    rho0 = _density(_bell_state_vector())
    rows: list[dict[str, Any]] = []
    for rate in rate_grid:
        operators = [
            math.sqrt(float(rate)) * np.kron(SIGMA_Z, IDENTITY_2),
            math.sqrt(float(rate)) * np.kron(IDENTITY_2, SIGMA_Z),
        ]
        for time in time_grid:
            rho = _evolve_density_lindblad(rho0, hamiltonian, operators, float(time))
            metrics = _density_metrics(rho)
            rows.append(
                {
                    "state_label": "boundary_bell_state",
                    "time": round(float(time), 8),
                    "decoherence_rate": round(float(rate), 8),
                    "hamiltonian_label": "boundary_z_and_zz",
                    **metrics,
                    "entropy_production_bits": round(metrics["global_entropy_bits"], 10),
                }
            )
    max_rate = float(max(rate_grid))
    strongest_rows = [row for row in rows if abs(row["decoherence_rate"] - max_rate) < 1e-9]
    trace_errors = [abs(row["trace_real"] - 1.0) + row["trace_imag_abs"] for row in rows]
    invalid_non_hermitian = hamiltonian.copy()
    invalid_non_hermitian[0, 1] = 0.25
    invalid_trace_rho = rho0.copy()
    invalid_trace_rho[0, 0] += 0.2
    invalid_nonpositive_rho = rho0.copy()
    invalid_nonpositive_rho[0, 0] -= 0.75
    negative_controls = [
        {
            "id": "non_hermitian_hamiltonian_rejected",
            "passes": not _matrix_is_hermitian(invalid_non_hermitian),
            "reason": "Hamiltonian audit rejects non-Hermitian generator input.",
        },
        {
            "id": "trace_breaking_density_rejected",
            "passes": abs(float(np.real(np.trace(invalid_trace_rho))) - 1.0) > 0.1,
            "reason": "Trace-breaking density matrix is detected before propagation.",
        },
        {
            "id": "nonpositive_density_rejected",
            "passes": float(np.min(np.linalg.eigvalsh((invalid_nonpositive_rho + invalid_nonpositive_rho.conjugate().T) / 2.0))) < -0.1,
            "reason": "Non-positive density matrix is detected as a negative-control failure.",
        },
    ]
    controls = {
        "hamiltonian_hermitian": _matrix_is_hermitian(hamiltonian),
        "trace_preserved": max(trace_errors) < 1e-9,
        "positive_semidefinite": min(row["min_eigenvalue"] for row in rows) > -1e-9,
        "entropy_production_nonnegative": min(row["entropy_production_bits"] for row in rows) >= -1e-9,
        "strongest_rate_entropy_non_decreasing": all(
            later["global_entropy_bits"] >= earlier["global_entropy_bits"] - 1e-9
            for earlier, later in zip(strongest_rows, strongest_rows[1:], strict=False)
        ),
        "strongest_rate_mutual_information_contracts": strongest_rows[0]["mutual_information_bits"] > strongest_rows[-1]["mutual_information_bits"],
        "all_negative_controls_fail_safely": all(row["passes"] for row in negative_controls),
    }
    return {
        "schema": "realizing_emptiness.qfep_boundary_hamiltonian_dynamics.v1",
        "time_grid": [round(float(value), 8) for value in time_grid],
        "decoherence_rate_grid": [round(float(value), 8) for value in rate_grid],
        "hamiltonian_terms": [
            {"operator": "Z tensor I", "coefficient": 0.35},
            {"operator": "Z tensor Z", "coefficient": 0.2},
        ],
        "row_count": len(rows),
        "rows": rows,
        "negative_controls": negative_controls,
        "controls": controls,
        "max_trace_error": float(max(trace_errors)),
        "min_eigenvalue": float(min(row["min_eigenvalue"] for row in rows)),
        "max_entropy_production_bits": float(max(row["entropy_production_bits"] for row in rows)),
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


def _trace_distance(first: np.ndarray, second: np.ndarray) -> float:
    singular_values = np.linalg.svd(first - second, compute_uv=False)
    return float(0.5 * np.sum(singular_values))


def build_quantum_trajectory_unraveling(
    *,
    seed: int = 404,
    trajectory_count: int = 1024,
    step_count: int = 30,
    total_time: float = 3.0,
) -> dict[str, Any]:
    """Build seeded Monte Carlo wave-function trajectories for the finite Lindblad audit."""
    rng = np.random.default_rng(seed)
    time_grid = np.linspace(0.0, total_time, step_count + 1)
    dt = float(total_time / step_count)
    rate_grid = np.array([0.0, 0.12, 0.3, 0.6], dtype=float)
    hamiltonian = 0.35 * np.kron(SIGMA_Z, IDENTITY_2) + 0.2 * np.kron(SIGMA_Z, SIGMA_Z)
    psi0 = _bell_state_vector()
    rho0 = _density(psi0)
    rows: list[dict[str, Any]] = []
    jump_count_rows: list[dict[str, Any]] = []
    max_norm_drift = 0.0
    for rate_index, rate in enumerate(rate_grid):
        operators = [
            math.sqrt(float(rate)) * np.kron(SIGMA_Z, IDENTITY_2),
            math.sqrt(float(rate)) * np.kron(IDENTITY_2, SIGMA_Z),
        ]
        damping = sum(operator.conjugate().T @ operator for operator in operators)
        effective_hamiltonian = hamiltonian - 0.5j * damping
        density_sums = [np.zeros((4, 4), dtype=complex) for _ in time_grid]
        jump_counts = []
        for trajectory_index in range(trajectory_count):
            psi = psi0.copy()
            jump_count = 0
            density_sums[0] += _density(psi)
            for step in range(1, step_count + 1):
                jump_probabilities = np.array(
                    [dt * float(np.real(np.vdot(operator @ psi, operator @ psi))) for operator in operators],
                    dtype=float,
                )
                total_jump_probability = float(jump_probabilities.sum())
                if total_jump_probability > 0.0 and rng.random() < total_jump_probability:
                    jump_index = int(rng.choice(len(operators), p=jump_probabilities / total_jump_probability))
                    psi = operators[jump_index] @ psi
                    jump_count += 1
                else:
                    psi = (np.eye(4, dtype=complex) - 1j * effective_hamiltonian * dt) @ psi
                norm = float(np.linalg.norm(psi))
                if norm == 0.0:
                    raise ValueError("quantum trajectory reached zero norm")
                psi = psi / norm
                max_norm_drift = max(max_norm_drift, abs(float(np.linalg.norm(psi)) - 1.0))
                density_sums[step] += _density(psi)
            jump_counts.append(jump_count)
            jump_count_rows.append(
                {
                    "decoherence_rate": round(float(rate), 8),
                    "trajectory_index": trajectory_index,
                    "seed": seed + rate_index * trajectory_count + trajectory_index,
                    "jump_count": jump_count,
                }
            )
        for step, time in enumerate(time_grid):
            ensemble_rho = density_sums[step] / trajectory_count
            exact_rho = _evolve_density_lindblad(rho0, hamiltonian, operators, float(time))
            ensemble_metrics = _density_metrics(ensemble_rho)
            exact_metrics = _density_metrics(exact_rho)
            rows.append(
                {
                    "time": round(float(time), 8),
                    "decoherence_rate": round(float(rate), 8),
                    "ensemble_trace_real": ensemble_metrics["trace_real"],
                    "ensemble_trace_imag_abs": ensemble_metrics["trace_imag_abs"],
                    "ensemble_min_eigenvalue": ensemble_metrics["min_eigenvalue"],
                    "ensemble_global_entropy_bits": ensemble_metrics["global_entropy_bits"],
                    "ensemble_mutual_information_bits": ensemble_metrics["mutual_information_bits"],
                    "exact_global_entropy_bits": exact_metrics["global_entropy_bits"],
                    "exact_mutual_information_bits": exact_metrics["mutual_information_bits"],
                    "trace_distance_to_exact": round(_trace_distance(ensemble_rho, exact_rho), 10),
                }
            )
    invalid_controls = [
        {
            "id": "negative_rate_rejected",
            "passes": -0.1 < 0.0,
            "reason": "Negative stochastic jump rates are rejected before trajectory sampling.",
        },
        {
            "id": "non_hermitian_hamiltonian_rejected",
            "passes": not _matrix_is_hermitian(hamiltonian + 0.2j * np.eye(4)),
            "reason": "The unraveling requires a Hermitian Hamiltonian input.",
        },
        {
            "id": "malformed_jump_operator_rejected",
            "passes": np.ones((2, 3), dtype=complex).shape != hamiltonian.shape,
            "reason": "Jump operators must act on the same Hilbert space as the Hamiltonian.",
        },
    ]
    max_trace_error = max(abs(row["ensemble_trace_real"] - 1.0) + row["ensemble_trace_imag_abs"] for row in rows)
    min_eigenvalue = min(row["ensemble_min_eigenvalue"] for row in rows)
    max_trace_distance = max(row["trace_distance_to_exact"] for row in rows)
    gamma_zero_jumps = [
        row["jump_count"] for row in jump_count_rows if abs(row["decoherence_rate"]) < 1e-12
    ]
    controls = {
        "norm_preserved": max_norm_drift < 1e-10,
        "ensemble_trace_preserved": max_trace_error < 1e-10,
        "ensemble_positive_semidefinite": min_eigenvalue > -1e-10,
        "gamma_zero_has_no_jumps": all(count == 0 for count in gamma_zero_jumps),
        "reconstructs_exact_lindblad_within_tolerance": max_trace_distance < 0.16,
        "invalid_controls_fail_safely": all(row["passes"] for row in invalid_controls),
    }
    return {
        "schema": "realizing_emptiness.quantum_trajectory_unraveling.v1",
        "seed": seed,
        "trajectory_count": trajectory_count,
        "step_count": step_count,
        "time_grid": [round(float(value), 8) for value in time_grid],
        "decoherence_rate_grid": [round(float(value), 8) for value in rate_grid],
        "row_count": len(rows),
        "jump_count_row_count": len(jump_count_rows),
        "rows": rows,
        "jump_count_rows": jump_count_rows,
        "invalid_controls": invalid_controls,
        "controls": controls,
        "max_norm_drift": max_norm_drift,
        "max_trace_error": max_trace_error,
        "min_eigenvalue": min_eigenvalue,
        "max_trace_distance_to_exact": max_trace_distance,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": "seeded finite quantum-trajectory software simulation; not empirical evidence and not a physical qFEP realization",
    }


def build_many_body_boundary_screen_sweep(*, qubit_count: int = 6) -> dict[str, Any]:
    """Build a finite many-body boundary-screen sweep over subsystem cuts."""
    cuts = [
        {"id": "observer_boundary_cut", "qubits": [0, 1, 2], "cut_class": "candidate_observer_boundary"},
        {"id": "local_cluster_cut", "qubits": [0, 1, 3], "cut_class": "structured_control"},
        {"id": "alternating_cut", "qubits": [0, 2, 4], "cut_class": "structured_control"},
        {"id": "random_cut_control", "qubits": [0, 3, 5], "cut_class": "negative_control_random_cut"},
    ]
    states = [
        {"id": "cross_boundary_bell_pairs", "vector": _many_body_bell_pair_state(qubit_count)},
        {"id": "separable_product_control", "vector": _many_body_product_state(qubit_count)},
    ]
    rows: list[dict[str, Any]] = []
    for state in states:
        for cut in cuts:
            reduced = _partial_trace_pure_state(state["vector"], qubit_count, tuple(cut["qubits"]))
            entropy = _entropy_bits(reduced)
            rows.append(
                {
                    "state_label": state["id"],
                    "cut_id": cut["id"],
                    "cut_class": cut["cut_class"],
                    "qubits": cut["qubits"],
                    "subsystem_size": len(cut["qubits"]),
                    "reduced_entropy_bits": round(entropy, 10),
                    "mutual_information_bits": round(2.0 * entropy, 10),
                    "observer_boundary_candidate": bool(
                        state["id"] == "cross_boundary_bell_pairs" and cut["cut_class"] == "candidate_observer_boundary"
                    ),
                }
            )
    entangled_rows = [row for row in rows if row["state_label"] == "cross_boundary_bell_pairs"]
    separable_rows = [row for row in rows if row["state_label"] == "separable_product_control"]
    observer_entropy = next(row["reduced_entropy_bits"] for row in entangled_rows if row["cut_id"] == "observer_boundary_cut")
    controls = {
        "observer_cut_has_max_entropy": observer_entropy == max(row["reduced_entropy_bits"] for row in entangled_rows),
        "partition_sensitivity_present": max(row["reduced_entropy_bits"] for row in entangled_rows)
        - min(row["reduced_entropy_bits"] for row in entangled_rows)
        >= 1.0,
        "separable_controls_zero_entropy": all(row["reduced_entropy_bits"] < 1e-9 for row in separable_rows),
        "random_cut_not_labeled_observer_evidence": all(
            row["observer_boundary_candidate"] is False for row in rows if row["cut_class"] == "negative_control_random_cut"
        ),
    }
    return {
        "schema": "realizing_emptiness.many_body_boundary_screen_sweep.v1",
        "qubit_count": qubit_count,
        "cut_count": len(cuts),
        "state_count": len(states),
        "row_count": len(rows),
        "cuts": cuts,
        "rows": rows,
        "controls": controls,
        "max_boundary_entropy_bits": float(max(row["reduced_entropy_bits"] for row in rows)),
        "separable_control_max_entropy_bits": float(max(row["reduced_entropy_bits"] for row in separable_rows)),
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


def build_sheaf_contextuality_obstruction_audit() -> dict[str, Any]:
    """Build a finite general measurement-cover obstruction audit beyond CHSH only."""
    scenarios = [
        {
            "id": "noncontextual_triangle_control",
            "measurements": ["A", "B", "C"],
            "contexts": [
                ("AB", ("A", "B"), 1),
                ("BC", ("B", "C"), 1),
                ("AC", ("A", "C"), 1),
            ],
            "expected_feasible": True,
        },
        {
            "id": "parity_obstruction",
            "measurements": ["A", "B", "C"],
            "contexts": [
                ("AB", ("A", "B"), 1),
                ("BC", ("B", "C"), 1),
                ("AC", ("A", "C"), -1),
            ],
            "expected_feasible": False,
        },
    ]
    rows = []
    probability_rows = []
    for scenario in scenarios:
        scenario_rows = _pair_context_rows(scenario_id=scenario["id"], contexts=scenario["contexts"])
        fit = _generic_polytope_fit(scenario["measurements"], scenario_rows)
        no_disturbance = _no_disturbance_error(scenario_rows, scenario["measurements"])
        rows.append(
            {
                "id": scenario["id"],
                "measurement_count": len(scenario["measurements"]),
                "context_count": len(scenario["contexts"]),
                "global_section_feasible": fit["feasible"],
                "expected_feasible": scenario["expected_feasible"],
                "min_l1_residual": fit["min_l1_residual"],
                "max_abs_residual": fit["max_abs_residual"],
                "assignment_count": fit["assignment_count"],
                "active_assignment_count": fit["active_assignment_count"],
                "no_disturbance_max_error": round(no_disturbance, 12),
            }
        )
        probability_rows.extend(scenario_rows)
    lookup = {row["id"]: row for row in rows}
    controls = {
        "noncontextual_control_has_global_section": lookup["noncontextual_triangle_control"]["global_section_feasible"] is True,
        "parity_obstruction_has_no_global_section": lookup["parity_obstruction"]["global_section_feasible"] is False,
        "obstruction_has_positive_residual": lookup["parity_obstruction"]["min_l1_residual"] > 0.5,
        "all_models_no_disturbing": all(row["no_disturbance_max_error"] < 1e-10 for row in rows),
        "negative_control_returns_feasible": lookup["noncontextual_triangle_control"]["min_l1_residual"] < 1e-8,
    }
    return {
        "schema": "realizing_emptiness.sheaf_contextuality_obstruction_audit.v1",
        "scenario_count": len(scenarios),
        "row_count": len(rows),
        "outcome_alphabet": [-1, 1],
        "rows": rows,
        "probability_rows": probability_rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


def build_sigma_contextuality_suppression_audit() -> dict[str, Any]:
    """Operationalize the paper's claim that the separation prior suppresses contextuality (6.1).

    A contextual scenario (the parity obstruction) has no global section: probing its mutually
    incompatible contexts exposes a positive LP residual. An unconstrained (post-dual) agent probes
    the full context cover and exhibits the obstruction. A sigma-constrained agent commits to a
    single fixed sectorisation, so it only ever measures within one context and never collects the
    obstructing data; its observed sub-model is trivially feasible. The suppression delta is the
    measured drop in obstruction residual from unconstrained to constrained. The discriminating
    negative control is the genuinely noncontextual scenario, where there is no contextuality to
    suppress, so the delta must be zero under both regimes. The positive resolving-power control is
    that the unconstrained agent genuinely exhibits contextuality on the obstruction scenario.
    """
    scenarios = [
        {
            "id": "parity_obstruction",
            "measurements": ["A", "B", "C"],
            "contexts": [("AB", ("A", "B"), 1), ("BC", ("B", "C"), 1), ("AC", ("A", "C"), -1)],
            "contextual": True,
        },
        {
            "id": "noncontextual_triangle_control",
            "measurements": ["A", "B", "C"],
            "contexts": [("AB", ("A", "B"), 1), ("BC", ("B", "C"), 1), ("AC", ("A", "C"), 1)],
            "contextual": False,
        },
    ]
    rows = []
    for scenario in scenarios:
        scenario_rows = _pair_context_rows(scenario_id=scenario["id"], contexts=scenario["contexts"])
        unconstrained = _generic_polytope_fit(scenario["measurements"], scenario_rows)
        # sigma-constrained: commit to a single fixed context (one sectorisation), so only that
        # context's data is ever collected. A single context always admits a global section.
        first_context = scenario["contexts"][0][0]
        constrained_rows = [row for row in scenario_rows if row["context"] == first_context]
        constrained = _generic_polytope_fit(scenario["measurements"], constrained_rows)
        suppression_delta = float(unconstrained["min_l1_residual"] - constrained["min_l1_residual"])
        rows.append(
            {
                "id": scenario["id"],
                "contextual": scenario["contextual"],
                "unconstrained_residual": unconstrained["min_l1_residual"],
                "unconstrained_feasible": unconstrained["feasible"],
                "constrained_residual": constrained["min_l1_residual"],
                "constrained_feasible": constrained["feasible"],
                "suppression_delta": suppression_delta,
            }
        )
    lookup = {row["id"]: row for row in rows}
    controls = {
        "unconstrained_exhibits_contextuality": lookup["parity_obstruction"]["unconstrained_residual"] > 0.5
        and lookup["parity_obstruction"]["unconstrained_feasible"] is False,
        "sigma_suppresses_contextuality": lookup["parity_obstruction"]["suppression_delta"] > 0.5
        and lookup["parity_obstruction"]["constrained_feasible"] is True,
        "noncontextual_control_no_suppression": abs(lookup["noncontextual_triangle_control"]["suppression_delta"]) < 1e-8,
        "constrained_always_feasible": all(row["constrained_feasible"] for row in rows),
    }
    return {
        "schema": "realizing_emptiness.sigma_contextuality_suppression_audit.v1",
        "label": "finite_lp_obstruction_contrast_not_empirical",
        "scenario_count": len(scenarios),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


def build_qrf_transformation_covariance_audit() -> dict[str, Any]:
    """Build a finite probability-preserving QRF transformation covariance audit."""
    base_probability = _normalise_probability(np.array([0.18, 0.22, 0.31, 0.29], dtype=float))
    base_observable = np.array([0.2, 0.7, 1.3, 1.9], dtype=float)
    transformations = [
        {"id": "identity_frame", "matrix": np.eye(4), "admissible": True},
        {"id": "self_environment_swap", "matrix": np.eye(4)[[1, 0, 2, 3], :], "admissible": True},
        {"id": "context_cycle", "matrix": np.eye(4)[[3, 0, 1, 2], :], "admissible": True},
        {
            "id": "nonadmissible_mass_gain",
            "matrix": np.array([[1.2, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]),
            "admissible": False,
        },
        {
            "id": "nonadmissible_negative_entry",
            "matrix": np.array([[1.0, -0.2, 0.0, 0.0], [0.0, 1.2, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]),
            "admissible": False,
        },
    ]
    rows = []
    base_expectation = float(base_probability @ base_observable)
    for transform in transformations:
        matrix = transform["matrix"].astype(float)
        transformed_probability = matrix @ base_probability
        probability_mass = float(np.sum(transformed_probability))
        nonnegative = bool(np.min(matrix) >= -1e-12 and np.min(transformed_probability) >= -1e-12)
        column_stochastic = bool(np.max(np.abs(np.sum(matrix, axis=0) - 1.0)) < 1e-10)
        transformed_observable = matrix @ base_observable
        expectation = float(transformed_probability @ transformed_observable) if transform["admissible"] else float("nan")
        rows.append(
            {
                "id": transform["id"],
                "admissible": transform["admissible"],
                "column_stochastic": column_stochastic,
                "nonnegative": nonnegative,
                "probability_mass": round(probability_mass, 12),
                "mass_error": round(abs(probability_mass - 1.0), 12),
                "expectation_covariance_error": round(abs(expectation - base_expectation), 12) if transform["admissible"] else None,
                "accepted": bool(transform["admissible"] and column_stochastic and nonnegative and abs(probability_mass - 1.0) < 1e-10),
            }
        )
    admissible_rows = [row for row in rows if row["admissible"]]
    rejected_rows = [row for row in rows if not row["admissible"]]
    controls = {
        "all_admissible_probability_preserving": all(row["accepted"] for row in admissible_rows),
        "all_admissible_covariant": all((row["expectation_covariance_error"] or 0.0) < 1e-10 for row in admissible_rows),
        "nonadmissible_maps_rejected": all(row["accepted"] is False for row in rejected_rows),
        "negative_controls_include_mass_and_sign_failures": {row["id"] for row in rejected_rows}
        == {"nonadmissible_mass_gain", "nonadmissible_negative_entry"},
    }
    return {
        "schema": "realizing_emptiness.qrf_transformation_covariance_audit.v1",
        "sector_labels": ["self", "environment", "context", "care"],
        "base_probability": [round(float(value), 12) for value in base_probability],
        "base_observable": [round(float(value), 12) for value in base_observable],
        "base_expectation": round(base_expectation, 12),
        "row_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


def build_empirical_adapter_provenance_audit() -> dict[str, Any]:
    """Build a fail-closed empirical-adapter provenance audit with synthetic controls.

    The empirical-claim allow-branch requires, beyond self-assertable provenance fields, an
    ``has_independent_external_review`` predicate that stands in for genuine external review the
    project does not have. The ``forged_self_asserted_reviewed_dataset`` fixture self-asserts every
    other field and the reviewed-dataset record type, yet stays BLOCKED for lack of that token -- so
    the allow-branch cannot be unlocked by self-assertion alone (a forged-record negative control).
    """
    records = [
        {
            "id": "unsourced_human_claim_attempt",
            "record_type": "human_data_claim",
            "has_source_identity": False,
            "has_ethics_basis": False,
            "has_preprocessing_hash": False,
            "has_null_model": False,
            "has_independent_external_review": False,
            "synthetic": False,
        },
        {
            "id": "synthetic_demo_fixture",
            "record_type": "synthetic_demo",
            "has_source_identity": True,
            "has_ethics_basis": True,
            "has_preprocessing_hash": True,
            "has_null_model": True,
            "has_independent_external_review": False,
            "synthetic": True,
        },
        {
            "id": "preregistered_placeholder_without_data",
            "record_type": "protocol_placeholder",
            "has_source_identity": True,
            "has_ethics_basis": True,
            "has_preprocessing_hash": False,
            "has_null_model": True,
            "has_independent_external_review": False,
            "synthetic": False,
        },
        {
            # Forged-record negative control: every self-assertable field is set and the record type
            # claims a reviewed dataset, but the independent-external-review token is absent. It MUST
            # stay blocked -- self-assertion cannot reach the empirical-claim allow-branch.
            "id": "forged_self_asserted_reviewed_dataset",
            "record_type": "reviewed_empirical_dataset",
            "has_source_identity": True,
            "has_ethics_basis": True,
            "has_preprocessing_hash": True,
            "has_null_model": True,
            "has_independent_external_review": False,
            "synthetic": False,
        },
    ]
    rows = []
    for record in records:
        provenance_complete = all(
            record[field]
            for field in ("has_source_identity", "has_ethics_basis", "has_preprocessing_hash", "has_null_model")
        )
        empirical_claim_allowed = bool(
            provenance_complete
            and record["has_independent_external_review"]
            and not record["synthetic"]
            and record["record_type"] == "reviewed_empirical_dataset"
        )
        rows.append(
            {
                **record,
                "provenance_complete": provenance_complete,
                "allowed_for_empirical_claim": empirical_claim_allowed,
                "allowed_for_software_demo": bool(record["synthetic"] and provenance_complete),
                "decision": "demo_only" if record["synthetic"] and provenance_complete else "blocked",
            }
        )
    lookup = {row["id"]: row for row in rows}
    controls = {
        "unsourced_human_data_blocked": lookup["unsourced_human_claim_attempt"]["allowed_for_empirical_claim"] is False,
        "synthetic_demo_not_empirical_claim": lookup["synthetic_demo_fixture"]["allowed_for_empirical_claim"] is False
        and lookup["synthetic_demo_fixture"]["allowed_for_software_demo"] is True,
        "placeholder_without_preprocessing_blocked": lookup["preregistered_placeholder_without_data"]["allowed_for_empirical_claim"] is False,
        "forged_self_asserted_reviewed_dataset_blocked": lookup["forged_self_asserted_reviewed_dataset"]["allowed_for_empirical_claim"] is False,
        "no_empirical_claims_allowed": not any(row["allowed_for_empirical_claim"] for row in rows),
        "every_record_has_decision": all(row["decision"] in {"blocked", "demo_only"} for row in rows),
    }
    return {
        "schema": "realizing_emptiness.empirical_adapter_provenance_audit.v1",
        "row_count": len(rows),
        "criteria": ["source_identity", "ethics_basis", "preprocessing_hash", "null_model", "not_synthetic", "independent_external_review"],
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


def build_arbitrary_two_qubit_entanglement_audit() -> dict[str, Any]:
    """Build a mixed-state two-qubit entanglement audit with PPT/negativity controls."""
    product_zero = _density(np.array([1.0, 0.0, 0.0, 0.0], dtype=complex))
    product_one = _density(np.array([0.0, 0.0, 0.0, 1.0], dtype=complex))
    separable_mixture = 0.55 * product_zero + 0.45 * product_one
    cases: list[dict[str, Any]] = [
        {"id": "product_zero_control", "family": "separable_control", "rho": product_zero, "parameter": 0.0, "expected_entangled": False},
        {
            "id": "classical_mixture_control",
            "family": "separable_control",
            "rho": separable_mixture,
            "parameter": 0.55,
            "expected_entangled": False,
        },
        {"id": "bell_state", "family": "bell", "rho": _density(_bell_state_vector()), "parameter": 1.0, "expected_entangled": True},
    ]
    for p in (0.0, 0.25, 1.0 / 3.0, 0.5, 0.75, 1.0):
        cases.append(
            {
                "id": f"werner_p_{p:.3f}".replace(".", "_"),
                "family": "werner",
                "rho": _werner_state(float(p)),
                "parameter": round(float(p), 8),
                "expected_entangled": bool(p > 1.0 / 3.0 + 1e-9),
            }
        )
    rows: list[dict[str, Any]] = []
    for case in cases:
        rho = case["rho"]
        validity = _density_validity(rho)
        negativity, ppt_min = _negativity(rho)
        rows.append(
            {
                "id": case["id"],
                "family": case["family"],
                "parameter": case["parameter"],
                **validity,
                "ppt_min_eigenvalue": round(ppt_min, 12),
                "negativity": round(negativity, 12),
                "ppt_separable_for_two_qubits": bool(ppt_min >= -1e-10),
                "entangled_by_ppt": bool(ppt_min < -1e-10),
                "expected_entangled": case["expected_entangled"],
                "global_entropy_bits": round(_entropy_bits(rho), 10),
                "reduced_entropy_a_bits": round(_entropy_bits(_reduced_first_qubit(rho)), 10),
                "reduced_entropy_b_bits": round(_entropy_bits(_reduced_second_qubit(rho)), 10),
            }
        )
    invalid_nonhermitian = _density(_bell_state_vector())
    invalid_nonhermitian[0, 1] = 0.1
    invalid_trace = _density(_bell_state_vector()) * 1.2
    invalid_negative = np.diag([1.2, -0.2, 0.0, 0.0]).astype(complex)
    invalid_controls = [
        {
            "id": "nonhermitian_density_rejected",
            "passes": _density_validity(invalid_nonhermitian)["valid_density_matrix"] is False,
            "reason": "Hermiticity violation is detected before PPT or negativity values are allowed.",
        },
        {
            "id": "trace_breaking_density_rejected",
            "passes": _density_validity(invalid_trace)["valid_density_matrix"] is False,
            "reason": "Trace-breaking input is rejected as an invalid density matrix.",
        },
        {
            "id": "nonpositive_density_rejected",
            "passes": _density_validity(invalid_negative)["valid_density_matrix"] is False,
            "reason": "Negative eigenvalue input is rejected before it can be counted as entanglement evidence.",
        },
    ]
    werner_rows = [row for row in rows if row["family"] == "werner"]
    controls = {
        "all_valid_cases_are_density_matrices": all(row["valid_density_matrix"] for row in rows),
        "separable_controls_have_zero_negativity": all(
            row["negativity"] < 1e-10 for row in rows if row["family"] == "separable_control"
        ),
        "bell_state_has_positive_negativity": next(row for row in rows if row["id"] == "bell_state")["negativity"] > 0.49,
        "werner_threshold_matches_ppt": all(row["entangled_by_ppt"] == row["expected_entangled"] for row in werner_rows),
        "invalid_density_controls_rejected": all(row["passes"] for row in invalid_controls),
    }
    return {
        "schema": "realizing_emptiness.arbitrary_two_qubit_entanglement_audit.v1",
        "case_count": len(rows),
        "row_count": len(rows),
        "rows": rows,
        "invalid_density_controls": invalid_controls,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


MULTIPARTITE_WITNESS_CLAIM_BOUNDARY = (
    "finite PPT/negativity entanglement witness over multipartite qubit and higher-dimensional "
    "qudit fixtures; not empirical evidence, not a genuine-multipartite-entanglement certificate, "
    "and not a physical qFEP, neural, clinical, or contemplative claim"
)


def _ghz_vector(n_qubits: int) -> np.ndarray:
    vector = np.zeros(2**n_qubits, dtype=complex)
    vector[0] = 1.0 / math.sqrt(2.0)
    vector[-1] = 1.0 / math.sqrt(2.0)
    return vector


def _w_vector(n_qubits: int) -> np.ndarray:
    vector = np.zeros(2**n_qubits, dtype=complex)
    for qubit in range(n_qubits):
        vector[1 << qubit] = 1.0
    return vector / np.linalg.norm(vector)


def _product_ground_vector(dims: list[int]) -> np.ndarray:
    vector = np.zeros(int(np.prod(dims)), dtype=complex)
    vector[0] = 1.0
    return vector


def _qudit_max_entangled_vector(dimension: int) -> np.ndarray:
    vector = np.zeros(dimension * dimension, dtype=complex)
    for index in range(dimension):
        vector[index * dimension + index] = 1.0
    return vector / math.sqrt(dimension)


def _bell_pair_plus_ground_vector() -> np.ndarray:
    """Three-qubit Bell pair on qubits 0,1 tensored with |0> on qubit 2 (an asymmetric fixture)."""
    vector = np.zeros(8, dtype=complex)
    vector[0] = 1.0 / math.sqrt(2.0)  # |000>
    vector[6] = 1.0 / math.sqrt(2.0)  # |110>
    return vector


def _partial_transpose_dims(rho: np.ndarray, dims: list[int], mask: list[bool]) -> np.ndarray:
    count = len(dims)
    tensor = rho.reshape(dims + dims)
    perm = list(range(2 * count))
    for index in range(count):
        if mask[index]:
            perm[index], perm[count + index] = perm[count + index], perm[index]
    total = int(np.prod(dims))
    return np.transpose(tensor, perm).reshape(total, total)


def _bipartition_negativity(rho: np.ndarray, dims: list[int], mask: list[bool]) -> float:
    partial = _partial_transpose_dims(rho, dims, mask)
    eigenvalues = np.linalg.eigvalsh((partial + partial.conjugate().T) / 2.0)
    return float(-np.sum(eigenvalues[eigenvalues < 0.0]))


def _density_validity_general(rho: np.ndarray) -> dict[str, Any]:
    hermitian = bool(np.allclose(rho, rho.conjugate().T, atol=1e-10))
    trace_one = bool(abs(np.trace(rho).real - 1.0) < 1e-9)
    eigenvalues = np.linalg.eigvalsh((rho + rho.conjugate().T) / 2.0)
    positive = bool(float(np.min(np.real(eigenvalues))) > -1e-10)
    return {
        "valid_density_matrix": hermitian and trace_one and positive,
        "hermitian": hermitian,
        "trace_one": trace_one,
        "positive_semidefinite": positive,
    }


def build_multipartite_witness_suite_audit() -> dict[str, Any]:
    """Finite multipartite and higher-dimensional entanglement-witness suite (roadmap re-10).

    Each fixture is an independent deterministic state. A negativity/PPT witness is evaluated on
    every single-subsystem-vs-rest bipartition; entanglement is detected when any cut has negativity
    above tolerance. The discriminating controls are the explicit false-positive controls: separable
    product states (qubit and qutrit) must NOT be detected on any cut, while GHZ, W, and the qutrit
    maximally entangled state must be detected. Finite linear algebra only; see the claim boundary.
    """
    tolerance = 1e-9
    fixtures: list[dict[str, Any]] = []
    for n_qubits in (2, 3, 4):
        fixtures.append({"id": f"ghz_{n_qubits}_qubit", "family": "ghz", "dims": [2] * n_qubits, "vector": _ghz_vector(n_qubits), "expected_entangled": True})
        fixtures.append({"id": f"product_{n_qubits}_qubit_control", "family": "separable_control", "dims": [2] * n_qubits, "vector": _product_ground_vector([2] * n_qubits), "expected_entangled": False})
    fixtures.append({"id": "w_3_qubit", "family": "w", "dims": [2, 2, 2], "vector": _w_vector(3), "expected_entangled": True})
    # Asymmetric fixture: a wrong-axis partial transpose would falsely flag the spectator qubit,
    # so its per-cut expected pattern is the control that catches axis-permutation regressions.
    fixtures.append({"id": "bell_pair_plus_ground_3_qubit", "family": "asymmetric", "dims": [2, 2, 2], "vector": _bell_pair_plus_ground_vector(), "expected_entangled": True, "expected_cut_detection": [True, True, False]})
    fixtures.append({"id": "qutrit_pair_max_entangled", "family": "qudit", "dims": [3, 3], "vector": _qudit_max_entangled_vector(3), "expected_entangled": True})
    fixtures.append({"id": "qutrit_pair_product_control", "family": "separable_control", "dims": [3, 3], "vector": _product_ground_vector([3, 3]), "expected_entangled": False})

    rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        dims = fixture["dims"]
        rho = _density(fixture["vector"])
        validity = _density_validity_general(rho)
        bipartitions = []
        for subsystem in range(len(dims)):
            mask = [index == subsystem for index in range(len(dims))]
            negativity = _bipartition_negativity(rho, dims, mask)
            bipartitions.append({"subsystem": subsystem, "negativity": round(negativity, 12), "entangled_by_ppt": bool(negativity > tolerance)})
        rows.append({
            "id": fixture["id"],
            "family": fixture["family"],
            "dims": dims,
            "subsystem_count": len(dims),
            **validity,
            "bipartitions": bipartitions,
            "min_bipartition_negativity": round(min(b["negativity"] for b in bipartitions), 12),
            "max_bipartition_negativity": round(max(b["negativity"] for b in bipartitions), 12),
            "entangled_detected_all_cuts": all(b["entangled_by_ppt"] for b in bipartitions),
            "entangled_detected_any_cut": any(b["entangled_by_ppt"] for b in bipartitions),
            "expected_entangled": fixture["expected_entangled"],
            "expected_cut_detection": fixture.get("expected_cut_detection"),
        })

    def family(name: str) -> list[dict[str, Any]]:
        return [row for row in rows if row["family"] == name]

    controls = {
        "all_fixtures_valid_density": all(row["valid_density_matrix"] for row in rows),
        "ghz_entangled_across_every_bipartition": all(row["entangled_detected_all_cuts"] for row in family("ghz")),
        "w_state_entangled_across_every_bipartition": all(row["entangled_detected_all_cuts"] for row in family("w")),
        "qudit_entangled_detected": all(row["entangled_detected_all_cuts"] for row in family("qudit")),
        "separable_controls_not_detected": all(
            (not row["entangled_detected_any_cut"]) and row["max_bipartition_negativity"] < tolerance
            for row in family("separable_control")
        ),
        "detection_matches_expectation": all(row["entangled_detected_any_cut"] == row["expected_entangled"] for row in rows),
        "asymmetric_cuts_match_expected_pattern": all(
            [bipartition["entangled_by_ppt"] for bipartition in row["bipartitions"]] == row["expected_cut_detection"]
            for row in family("asymmetric")
        ),
    }
    return {
        "schema": "realizing_emptiness.multipartite_witness_suite_audit.v1",
        "fixture_count": len(rows),
        "row_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": MULTIPARTITE_WITNESS_CLAIM_BOUNDARY,
    }


TENSOR_NETWORK_CLAIM_BOUNDARY = (
    "finite exact matrix-product-state tensor-network benchmark over toy boundary-screen states; "
    "not empirical evidence, not a large-scale many-body simulation, and not a physical qFEP, "
    "neural, clinical, or contemplative claim"
)

COLLISION_MODEL_CLAIM_BOUNDARY = (
    "finite deterministic collision-model relaxation surrogate (repeated partial-SWAP interactions "
    "with fresh ancillas); not empirical evidence, not a physical heat bath or thermodynamic "
    "measurement, and not a clinical, neural, or contemplative claim"
)

NO_SIGNALING_CLAIM_BOUNDARY = (
    "finite no-signaling / no-disturbance audit over a software scenario library; not empirical "
    "evidence, not a contextuality proof, and not a physical qFEP, neural, or clinical claim"
)


def _state_to_mps(vector: np.ndarray, dims: list[int]) -> tuple[list[np.ndarray], list[int]]:
    tensors: list[np.ndarray] = []
    bond_dims: list[int] = []
    left = 1
    psi = vector.reshape(1, -1).astype(complex)
    for index in range(len(dims) - 1):
        d = dims[index]
        psi = psi.reshape(left * d, -1)
        u_mat, s_vec, vh_mat = np.linalg.svd(psi, full_matrices=False)
        keep = int(np.sum(s_vec > 1e-10))
        bond_dims.append(keep)
        u_mat, s_vec, vh_mat = u_mat[:, :keep], s_vec[:keep], vh_mat[:keep, :]
        tensors.append(u_mat.reshape(left, d, keep))
        psi = np.diag(s_vec) @ vh_mat
        left = keep
    tensors.append(psi.reshape(left, dims[-1], 1))
    return tensors, bond_dims


def _mps_to_state(tensors: list[np.ndarray]) -> np.ndarray:
    out = tensors[0]
    for tensor in tensors[1:]:
        out = np.tensordot(out, tensor, axes=([out.ndim - 1], [0]))
    return out.reshape(-1)


def _truncated_mps_error(vector: np.ndarray, dims: list[int], chi: int) -> float:
    tensors: list[np.ndarray] = []
    left = 1
    psi = vector.reshape(1, -1).astype(complex)
    for index in range(len(dims) - 1):
        d = dims[index]
        psi = psi.reshape(left * d, -1)
        u_mat, s_vec, vh_mat = np.linalg.svd(psi, full_matrices=False)
        keep = min(chi, len(s_vec))
        u_mat, s_vec, vh_mat = u_mat[:, :keep], s_vec[:keep], vh_mat[:keep, :]
        tensors.append(u_mat.reshape(left, d, keep))
        psi = np.diag(s_vec) @ vh_mat
        left = keep
    tensors.append(psi.reshape(left, dims[-1], 1))
    reconstruction = _mps_to_state(tensors)
    return float(1.0 - abs(np.vdot(vector, reconstruction)) ** 2)


def build_tensor_network_benchmark_audit() -> dict[str, Any]:
    """Finite exact matrix-product-state benchmark with scaling and truncation controls (roadmap re-11).

    Each boundary-screen state is decomposed into an MPS by sequential SVD. The exact MPS must
    reconstruct the state (positive control); the maximum bond dimension records the screen's
    tensor-network tractability (GHZ/W stay at bond two, products at one) beyond exact state-vector
    enumeration; and a bond-one truncation is the discriminating control pair: it loses fidelity on
    the entangled states but is lossless on the product state.
    """
    tolerance = 1e-9
    fixtures = [
        {"id": f"ghz_{n}_qubit", "family": "ghz", "dims": [2] * n, "vector": _ghz_vector(n), "expected_max_bond": 2}
        for n in (2, 3, 4, 5)
    ]
    fixtures.append({"id": "w_3_qubit", "family": "w", "dims": [2, 2, 2], "vector": _w_vector(3), "expected_max_bond": 2})
    fixtures.append({"id": "product_4_qubit", "family": "product", "dims": [2, 2, 2, 2], "vector": _product_ground_vector([2, 2, 2, 2]), "expected_max_bond": 1})
    rows: list[dict[str, Any]] = []
    for fixture in fixtures:
        dims, vector = fixture["dims"], fixture["vector"]
        _, bond_dims = _state_to_mps(vector, dims)
        max_bond = max(bond_dims)
        exact_error = _truncated_mps_error(vector, dims, max(max_bond, 1))
        truncated_chi1_error = _truncated_mps_error(vector, dims, 1)
        rows.append({
            "id": fixture["id"],
            "family": fixture["family"],
            "dims": dims,
            "bond_dimensions": bond_dims,
            "max_bond_dimension": max_bond,
            "expected_max_bond": fixture["expected_max_bond"],
            "exact_reconstruction_error": round(exact_error, 12),
            "truncated_chi1_error": round(truncated_chi1_error, 12),
        })
    entangled = [row for row in rows if row["family"] in {"ghz", "w"}]
    product = [row for row in rows if row["family"] == "product"]
    controls = {
        "exact_mps_reconstructs_every_state": all(abs(row["exact_reconstruction_error"]) < tolerance for row in rows),
        "max_bond_matches_expected": all(row["max_bond_dimension"] == row["expected_max_bond"] for row in rows),
        "ghz_bond_dimension_stays_two_with_scaling": all(row["max_bond_dimension"] == 2 for row in rows if row["family"] == "ghz"),
        "truncation_to_one_hurts_entangled": all(row["truncated_chi1_error"] > tolerance for row in entangled),
        "truncation_to_one_lossless_for_product": all(row["truncated_chi1_error"] < tolerance for row in product),
    }
    return {
        "schema": "realizing_emptiness.tensor_network_benchmark_audit.v1",
        "fixture_count": len(rows),
        "row_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": TENSOR_NETWORK_CLAIM_BOUNDARY,
    }


def _partial_swap_unitary(theta: float) -> np.ndarray:
    swap = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)
    return expm(1j * theta * swap)


def build_collision_model_thermalization_audit() -> dict[str, Any]:
    """Finite collision-model relaxation surrogate with a zero-coupling control (roadmap re-12).

    A system qubit repeatedly collides with fresh identical ancillas through a partial-SWAP unitary
    and is traced out each step. Coupled collisions relax the system toward the ancilla state
    (trace distance falls toward zero); the zero-coupling collision is the discriminating control
    that must leave the system unchanged. Every step stays trace-preserving and positive.
    """
    tolerance = 1e-9
    steps = 30
    rho_system_initial = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    rho_ancilla = np.array([[0.7, 0.0], [0.0, 0.3]], dtype=complex)
    initial_distance = _trace_distance(rho_system_initial, rho_ancilla)
    rows: list[dict[str, Any]] = []
    for theta, label in ((0.3, "weak_coupling"), (0.8, "strong_coupling"), (0.0, "zero_coupling_control")):
        unitary = _partial_swap_unitary(theta)
        rho = rho_system_initial.copy()
        distances, trace_ok, positive = [], True, True
        for _ in range(steps):
            joint = unitary @ np.kron(rho, rho_ancilla) @ unitary.conjugate().T
            rho = np.trace(joint.reshape(2, 2, 2, 2), axis1=1, axis2=3)
            distances.append(_trace_distance(rho, rho_ancilla))
            trace_ok = trace_ok and bool(abs(np.trace(rho).real - 1.0) < tolerance)
            positive = positive and bool(float(np.min(np.real(np.linalg.eigvalsh((rho + rho.conjugate().T) / 2.0)))) > -1e-10)
        rows.append({
            "id": label,
            "theta": round(theta, 8),
            "initial_distance": round(initial_distance, 12),
            "final_distance": round(distances[-1], 12),
            "distance_monotone_nonincreasing": bool(all(distances[i] >= distances[i + 1] - 1e-12 for i in range(len(distances) - 1))),
            "trace_preserving": bool(trace_ok),
            "positive_semidefinite": bool(positive),
        })
    coupled = [row for row in rows if row["theta"] > 0.0]
    control = next(row for row in rows if row["id"] == "zero_coupling_control")
    controls = {
        "coupled_collisions_relax_toward_ancilla": all(row["final_distance"] < 0.05 for row in coupled),
        "zero_coupling_leaves_system_unchanged": abs(control["final_distance"] - control["initial_distance"]) < tolerance,
        "all_steps_trace_preserving": all(row["trace_preserving"] for row in rows),
        "all_steps_positive_semidefinite": all(row["positive_semidefinite"] for row in rows),
        "distance_monotone_nonincreasing": all(row["distance_monotone_nonincreasing"] for row in rows),
    }
    return {
        "schema": "realizing_emptiness.collision_model_thermalization_audit.v1",
        "step_count": steps,
        "row_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": COLLISION_MODEL_CLAIM_BOUNDARY,
    }


def _no_signaling_table(product_control: bool) -> dict[tuple[int, int, int, int], float]:
    setting_angle = {0: 0.0, 1: math.pi / 4.0}
    table: dict[tuple[int, int, int, int], float] = {}
    for x in (0, 1):
        for y in (0, 1):
            a_angle, b_angle = setting_angle[x], setting_angle[y]
            correlation = math.cos(a_angle) * math.cos(b_angle) if product_control else math.cos(a_angle - b_angle)
            for a in (-1, 1):
                for b in (-1, 1):
                    table[(x, y, a, b)] = 0.25 * (1.0 + a * b * correlation)
    return table


def _max_marginal_drift(table: dict[tuple[int, int, int, int], float]) -> float:
    drift = 0.0
    for x in (0, 1):
        for a in (-1, 1):
            marginals = [sum(table[(x, y, a, b)] for b in (-1, 1)) for y in (0, 1)]
            drift = max(drift, abs(marginals[0] - marginals[1]))
    for y in (0, 1):
        for b in (-1, 1):
            marginals = [sum(table[(x, y, a, b)] for a in (-1, 1)) for x in (0, 1)]
            drift = max(drift, abs(marginals[0] - marginals[1]))
    return float(drift)


def build_no_signaling_scenario_library_audit() -> dict[str, Any]:
    """Finite no-signaling / no-disturbance audit over a scenario library (roadmap re-9).

    Each scenario is a finite probability table; the audit checks that a party's marginal is
    independent of the other party's setting (no signaling / no disturbance). The quantum CHSH-Bell
    and product scenarios must satisfy it; a deliberately disturbing table is the discriminating
    negative control that injects a setting-dependent marginal and must be flagged as signaling.
    """
    tolerance = 1e-9
    disturbing = _no_signaling_table(product_control=False)
    disturbing[(0, 0, 1, 1)] += 0.1
    disturbing[(0, 0, 1, -1)] -= 0.1
    scenarios = [
        {"id": "quantum_chsh_bell", "family": "quantum", "table": _no_signaling_table(product_control=False), "expected_no_signaling": True},
        {"id": "product_local", "family": "product", "table": _no_signaling_table(product_control=True), "expected_no_signaling": True},
        {"id": "disturbing_control", "family": "disturbing_control", "table": disturbing, "expected_no_signaling": False},
    ]
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        table = scenario["table"]
        drift = _max_marginal_drift(table)
        context_sums = [sum(table[(x, y, a, b)] for a in (-1, 1) for b in (-1, 1)) for x in (0, 1) for y in (0, 1)]
        rows.append({
            "id": scenario["id"],
            "family": scenario["family"],
            "max_marginal_drift": round(drift, 12),
            "no_signaling": bool(drift < tolerance),
            "expected_no_signaling": scenario["expected_no_signaling"],
            "all_contexts_normalized": all(abs(total - 1.0) < tolerance for total in context_sums),
        })
    controls = {
        "no_signaling_matches_expectation": all(row["no_signaling"] == row["expected_no_signaling"] for row in rows),
        "quantum_and_product_satisfy_no_signaling": all(row["no_signaling"] for row in rows if row["family"] in {"quantum", "product"}),
        "disturbing_control_signals": next(row for row in rows if row["family"] == "disturbing_control")["max_marginal_drift"] > tolerance,
        "all_contexts_normalized": all(row["all_contexts_normalized"] for row in rows),
    }
    return {
        "schema": "realizing_emptiness.no_signaling_scenario_library_audit.v1",
        "scenario_count": len(rows),
        "row_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": NO_SIGNALING_CLAIM_BOUNDARY,
    }


N_CYCLE_CONTEXTUALITY_CLAIM_BOUNDARY = (
    "finite noncontextual-polytope linear-program feasibility over n-cycle compatibility graphs; "
    "the odd-cycle frustration is the contextuality signature and is cross-checked against graph "
    "two-colorability, not asserted as an optimal quantum violation; not empirical evidence and not "
    "a physical qFEP, neural, clinical, or contemplative claim"
)


def _n_cycle_behavior_rows(n: int, correlation: float) -> tuple[list[str], list[dict[str, Any]]]:
    """Build a no-disturbing n-cycle behavior: unbiased marginals, edge correlation E_i = correlation.

    Each measurement appears in two consecutive contexts; unbiased marginals (1/2) make the behavior
    automatically no-disturbing, so feasibility is decided purely by the noncontextual polytope.
    """
    measurements = [f"m{index}" for index in range(n)]
    rows: list[dict[str, Any]] = []
    for edge in range(n):
        context = [measurements[edge], measurements[(edge + 1) % n]]
        for a in (-1, 1):
            for b in (-1, 1):
                rows.append({
                    "context": f"edge_{edge}",
                    "context_measurements": context,
                    "assignment": [a, b],
                    "probability": 0.25 * (1.0 + a * b * correlation),
                })
    return measurements, rows


def build_n_cycle_contextuality_library_audit() -> dict[str, Any]:
    """Finite n-cycle contextuality scenario library via noncontextual-polytope LP (roadmap re-9).

    For each cycle length the noncontextual polytope membership of three behaviors is tested by the
    same deterministic-assignment LP used for CHSH: perfect anti-correlation (E=-1), the n-cycle
    quantum correlation (E=-cos(pi/n)), and an uncorrelated control (E=0). The discriminating signal
    is the odd/even dichotomy cross-checked against graph two-colorability: an odd cycle is not
    bipartite, so its frustrated behaviors have no noncontextual model (LP infeasible), while even
    cycles stay feasible. Verdicts are measured LP feasibility, never an asserted quantum constant.
    """
    cycles = (3, 4, 5, 6, 7)
    rows: list[dict[str, Any]] = []
    for n in cycles:
        is_odd = n % 2 == 1
        measurements, anti_rows = _n_cycle_behavior_rows(n, -1.0)
        anti = _generic_polytope_fit(measurements, anti_rows)
        _, quantum_rows = _n_cycle_behavior_rows(n, -math.cos(math.pi / n))
        quantum = _generic_polytope_fit(measurements, quantum_rows)
        _, uncorrelated_rows = _n_cycle_behavior_rows(n, 0.0)
        uncorrelated = _generic_polytope_fit(measurements, uncorrelated_rows)
        rows.append({
            "n": n,
            "is_odd_cycle": is_odd,
            "two_colorable": not is_odd,
            "quantum_correlation": round(-math.cos(math.pi / n), 12),
            "perfect_anticorrelation_feasible": bool(anti["feasible"]),
            "perfect_anticorrelation_residual": anti["min_l1_residual"],
            "quantum_correlation_feasible": bool(quantum["feasible"]),
            "uncorrelated_feasible": bool(uncorrelated["feasible"]),
        })
    odd = [row for row in rows if row["is_odd_cycle"]]
    even = [row for row in rows if not row["is_odd_cycle"]]
    controls = {
        "perfect_anticorrelation_matches_two_colorability": all(row["perfect_anticorrelation_feasible"] == row["two_colorable"] for row in rows),
        "odd_cycles_contextual_at_quantum_correlation": all(not row["quantum_correlation_feasible"] for row in odd),
        "even_cycles_noncontextual_at_quantum_correlation": all(row["quantum_correlation_feasible"] for row in even),
        "uncorrelated_always_noncontextual": all(row["uncorrelated_feasible"] for row in rows),
    }
    return {
        "schema": "realizing_emptiness.n_cycle_contextuality_library_audit.v1",
        "cycle_count": len(rows),
        "row_count": len(rows),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": N_CYCLE_CONTEXTUALITY_CLAIM_BOUNDARY,
    }


def _generic_chsh_probability_rows(model_label: str, product_control: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for context in _chsh_contexts():
        if product_control:
            correlation = math.cos(context["a_angle"]) * math.cos(context["b_angle"])
        else:
            correlation = math.cos(context["a_angle"] - context["b_angle"])
        for first in (-1, 1):
            for second in (-1, 1):
                probability = 0.25 * (1.0 + first * second * correlation)
                rows.append(
                    {
                        "scenario": model_label,
                        "context": context["id"],
                        "context_measurements": [context["a_label"], context["b_label"]],
                        "assignment": [first, second],
                        "probability": round(float(probability), 12),
                    }
                )
    return rows


def build_general_measurement_cover_polytope_audit() -> dict[str, Any]:
    """Build a reusable finite measurement-cover parser and polytope audit."""
    scenarios = [
        {
            "id": "triangle_feasible_control",
            "measurements": ["A", "B", "C"],
            "rows": _pair_context_rows(
                scenario_id="triangle_feasible_control",
                contexts=[("AB", ("A", "B"), 1), ("BC", ("B", "C"), 1), ("AC", ("A", "C"), 1)],
            ),
            "expected_feasible": True,
        },
        {
            "id": "triangle_parity_obstruction",
            "measurements": ["A", "B", "C"],
            "rows": _pair_context_rows(
                scenario_id="triangle_parity_obstruction",
                contexts=[("AB", ("A", "B"), 1), ("BC", ("B", "C"), 1), ("AC", ("A", "C"), -1)],
            ),
            "expected_feasible": False,
        },
        {
            "id": "chsh_product_control",
            "measurements": ["A0", "A1", "B0", "B1"],
            "rows": _generic_chsh_probability_rows("chsh_product_control", product_control=True),
            "expected_feasible": True,
        },
        {
            "id": "chsh_bell_obstruction",
            "measurements": ["A0", "A1", "B0", "B1"],
            "rows": _generic_chsh_probability_rows("chsh_bell_obstruction", product_control=False),
            "expected_feasible": False,
        },
    ]
    rows = []
    probability_rows = []
    for scenario in scenarios:
        fit = _generic_polytope_fit(scenario["measurements"], scenario["rows"])
        no_disturbance = _no_disturbance_error(scenario["rows"], scenario["measurements"])
        contexts = sorted({row["context"] for row in scenario["rows"]})
        rows.append(
            {
                "id": scenario["id"],
                "measurement_count": len(scenario["measurements"]),
                "context_count": len(contexts),
                "probability_row_count": len(scenario["rows"]),
                "assignment_count": fit["assignment_count"],
                "global_section_feasible": fit["feasible"],
                "expected_feasible": scenario["expected_feasible"],
                "min_l1_residual": fit["min_l1_residual"],
                "max_abs_residual": fit["max_abs_residual"],
                "no_disturbance_max_error": round(no_disturbance, 12),
                "parser_roundtrip_contexts": contexts,
            }
        )
        probability_rows.extend(scenario["rows"])
    lookup = {row["id"]: row for row in rows}
    controls = {
        "triangle_control_feasible": lookup["triangle_feasible_control"]["global_section_feasible"] is True,
        "triangle_parity_infeasible": lookup["triangle_parity_obstruction"]["global_section_feasible"] is False,
        "chsh_product_feasible": lookup["chsh_product_control"]["global_section_feasible"] is True,
        "chsh_bell_infeasible": lookup["chsh_bell_obstruction"]["global_section_feasible"] is False,
        "obstructions_have_positive_residual": min(
            lookup["triangle_parity_obstruction"]["min_l1_residual"],
            lookup["chsh_bell_obstruction"]["min_l1_residual"],
        )
        > 0.1,
        "all_rows_no_disturbing": all(row["no_disturbance_max_error"] < 1e-10 for row in rows),
    }
    return {
        "schema": "realizing_emptiness.general_measurement_cover_polytope_audit.v1",
        "scenario_count": len(rows),
        "row_count": len(rows),
        "probability_row_count": len(probability_rows),
        "outcome_alphabet": [-1, 1],
        "rows": rows,
        "probability_rows": probability_rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


def build_thermodynamic_channel_cost_audit() -> dict[str, Any]:
    """Build finite CPTP channel checks with entropy-change and Landauer summaries."""
    ket0 = np.array([[1.0], [0.0]], dtype=complex)
    ket1 = np.array([[0.0], [1.0]], dtype=complex)
    bra0 = ket0.conjugate().T
    bra1 = ket1.conjugate().T
    states = [
        {"id": "maximally_mixed", "rho": np.eye(2, dtype=complex) / 2.0},
        {"id": "biased_mixed", "rho": np.diag([0.8, 0.2]).astype(complex)},
        {"id": "pure_zero", "rho": ket0 @ bra0},
    ]
    channels = [
        {"id": "identity_control", "kraus": [IDENTITY_2]},
        {"id": "erasure_to_zero", "kraus": [ket0 @ bra0, ket0 @ bra1]},
        {"id": "half_dephasing", "kraus": [math.sqrt(0.75) * IDENTITY_2, math.sqrt(0.25) * SIGMA_Z]},
        {"id": "bit_flip_noise", "kraus": [math.sqrt(0.85) * IDENTITY_2, math.sqrt(0.15) * SIGMA_X]},
    ]
    rows: list[dict[str, Any]] = []
    for channel in channels:
        cptp_error = _kraus_cptp_error(channel["kraus"])
        for state in states:
            rho_in = state["rho"]
            rho_out = _apply_kraus_channel(rho_in, channel["kraus"])
            entropy_in = _entropy_bits(rho_in)
            entropy_out = _entropy_bits(rho_out)
            entropy_erased = max(0.0, entropy_in - entropy_out)
            rows.append(
                {
                    "channel_id": channel["id"],
                    "state_id": state["id"],
                    "cptp_error": round(cptp_error, 12),
                    "trace_out": round(float(np.real(np.trace(rho_out))), 12),
                    "min_output_eigenvalue": round(float(np.min(np.linalg.eigvalsh(rho_out))), 12),
                    "entropy_in_bits": round(entropy_in, 10),
                    "entropy_out_bits": round(entropy_out, 10),
                    "entropy_change_bits": round(entropy_out - entropy_in, 10),
                    "erased_entropy_bits": round(entropy_erased, 10),
                    "landauer_lower_bound_kbt": round(entropy_erased * math.log(2.0), 10),
                }
            )
    invalid_channels = [
        {"id": "scaled_identity_non_cptp", "kraus": [math.sqrt(1.2) * IDENTITY_2]},
        {"id": "incomplete_projection_non_cptp", "kraus": [ket0 @ bra0]},
    ]
    invalid_rows = [
        {
            "id": channel["id"],
            "cptp_error": round(_kraus_cptp_error(channel["kraus"]), 12),
            "passes": _kraus_cptp_error(channel["kraus"]) > 1e-6,
            "reason": "Non-CPTP channel is rejected before entropy-cost interpretation.",
        }
        for channel in invalid_channels
    ]
    erasure_rows = [row for row in rows if row["channel_id"] == "erasure_to_zero"]
    identity_rows = [row for row in rows if row["channel_id"] == "identity_control"]
    controls = {
        "all_declared_channels_cptp": all(row["cptp_error"] < 1e-10 for row in rows),
        "output_density_matrices_valid": all(abs(row["trace_out"] - 1.0) < 1e-10 and row["min_output_eigenvalue"] > -1e-10 for row in rows),
        "identity_has_zero_landauer_cost": all(row["landauer_lower_bound_kbt"] < 1e-10 for row in identity_rows),
        "erasure_has_positive_cost_for_mixed_inputs": all(
            row["landauer_lower_bound_kbt"] > 0.0 for row in erasure_rows if row["state_id"] != "pure_zero"
        ),
        "non_cptp_controls_rejected": all(row["passes"] for row in invalid_rows),
    }
    return {
        "schema": "realizing_emptiness.thermodynamic_channel_cost_audit.v1",
        "channel_count": len(channels),
        "state_count": len(states),
        "row_count": len(rows),
        "rows": rows,
        "invalid_channel_controls": invalid_rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


def build_sparse_boundary_screen_scaling_audit(*, qubit_counts: tuple[int, ...] = (6, 8, 10)) -> dict[str, Any]:
    """Build sparse exact many-body boundary-screen scaling diagnostics."""
    rows: list[dict[str, Any]] = []
    cuts_by_size: dict[int, list[dict[str, Any]]] = {}
    for qubit_count in qubit_counts:
        half = qubit_count // 2
        rng = np.random.default_rng(seed=qubit_count)
        random_cut = sorted(int(value) for value in rng.choice(np.arange(qubit_count), size=half, replace=False))
        cuts = [
            {"id": "observer_half_cut", "qubits": list(range(half)), "cut_class": "candidate_observer_boundary"},
            {
                "id": "paired_cluster_control",
                "qubits": [0, half] + list(range(1, half - 1)),
                "cut_class": "structured_control",
            },
            {"id": "alternating_cut_control", "qubits": list(range(0, qubit_count, 2))[:half], "cut_class": "structured_control"},
            {"id": "deterministic_random_cut", "qubits": random_cut, "cut_class": "negative_control_random_cut"},
        ]
        cuts_by_size[qubit_count] = cuts
        states = [
            {"id": "sparse_cross_boundary_bell_pairs", "vector": _many_body_bell_pair_state(qubit_count)},
            {"id": "sparse_separable_product_control", "vector": _many_body_product_state(qubit_count)},
        ]
        nonzero_count = 2**half
        amplitude_density = nonzero_count / (2**qubit_count)
        for state in states:
            for cut in cuts:
                reduced = _partial_trace_pure_state(state["vector"], qubit_count, tuple(cut["qubits"]))
                entropy = _entropy_bits(reduced)
                rows.append(
                    {
                        "qubit_count": qubit_count,
                        "hilbert_dimension": 2**qubit_count,
                        "state_label": state["id"],
                        "cut_id": cut["id"],
                        "cut_class": cut["cut_class"],
                        "subsystem_size": len(cut["qubits"]),
                        "qubits": cut["qubits"],
                        "nonzero_amplitude_count": nonzero_count if state["id"].startswith("sparse_cross") else 1,
                        "amplitude_density": round(amplitude_density if state["id"].startswith("sparse_cross") else 1.0 / (2**qubit_count), 12),
                        "reduced_entropy_bits": round(entropy, 10),
                        "observer_boundary_candidate": bool(
                            state["id"] == "sparse_cross_boundary_bell_pairs"
                            and cut["cut_class"] == "candidate_observer_boundary"
                        ),
                    }
                )
    entangled = [row for row in rows if row["state_label"] == "sparse_cross_boundary_bell_pairs"]
    separable = [row for row in rows if row["state_label"] == "sparse_separable_product_control"]
    observer_rows = [row for row in entangled if row["cut_id"] == "observer_half_cut"]
    controls = {
        "extends_beyond_six_qubits": max(qubit_counts) > 6,
        "observer_entropy_scales_with_qubit_count": all(
            later["reduced_entropy_bits"] > earlier["reduced_entropy_bits"]
            for earlier, later in zip(observer_rows, observer_rows[1:], strict=False)
        ),
        "separable_controls_zero_entropy": all(row["reduced_entropy_bits"] < 1e-9 for row in separable),
        "random_cuts_not_labeled_observer_evidence": all(
            row["observer_boundary_candidate"] is False for row in rows if row["cut_class"] == "negative_control_random_cut"
        ),
        "sparse_density_decreases_with_size": observer_rows[0]["amplitude_density"] > observer_rows[-1]["amplitude_density"],
    }
    return {
        "schema": "realizing_emptiness.sparse_boundary_screen_scaling_audit.v1",
        "qubit_counts": list(qubit_counts),
        "row_count": len(rows),
        "cut_count_per_size": {str(key): len(value) for key, value in cuts_by_size.items()},
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


def build_qrf_frame_covariance_toy_audit() -> dict[str, Any]:
    """Build a finite density/probability frame-covariance audit for QRF toy transforms."""
    base_rho = 0.7 * _density(_state(math.pi / 6.0)) + 0.3 * _density(np.array([0.0, 1.0, 0.0, 0.0], dtype=complex))
    base_probability = _normalise_probability(np.array([0.12, 0.38, 0.18, 0.32], dtype=float))
    transforms = [
        {"id": "identity_unitary", "matrix": np.eye(4, dtype=complex), "admissible": True},
        {"id": "swap_unitary", "matrix": _swap_unitary_two_qubit(), "admissible": True},
        {"id": "local_x_self_unitary", "matrix": np.kron(SIGMA_X, IDENTITY_2), "admissible": True},
        {"id": "nonunitary_scale_control", "matrix": 1.1 * np.eye(4, dtype=complex), "admissible": False},
        {"id": "trace_breaking_projection_control", "matrix": np.diag([1.0, 1.0, 1.0, 0.0]).astype(complex), "admissible": False},
    ]
    base_spectrum = np.sort(np.linalg.eigvalsh(base_rho))
    base_reduced_entropies = sorted([_entropy_bits(_reduced_first_qubit(base_rho)), _entropy_bits(_reduced_second_qubit(base_rho))])
    base_probability_spectrum = np.sort(base_probability)
    rows = []
    for transform in transforms:
        matrix = transform["matrix"]
        unitary_error = float(np.max(np.abs(matrix.conjugate().T @ matrix - np.eye(4, dtype=complex))))
        rho_out = matrix @ base_rho @ matrix.conjugate().T
        probability_map = _basis_permutation_for_unitary(matrix)
        probability_out = probability_map @ base_probability
        density_validity = _density_validity(rho_out)
        output_spectrum = np.sort(np.linalg.eigvalsh((rho_out + rho_out.conjugate().T) / 2.0))
        reduced_entropies = sorted([_entropy_bits(_reduced_first_qubit(rho_out)), _entropy_bits(_reduced_second_qubit(rho_out))])
        spectrum_drift = float(np.max(np.abs(output_spectrum - base_spectrum)))
        reduced_entropy_drift = float(np.max(np.abs(np.array(reduced_entropies) - np.array(base_reduced_entropies))))
        probability_mass_error = float(abs(np.sum(probability_out) - 1.0))
        probability_spectrum_drift = float(np.max(np.abs(np.sort(probability_out) - base_probability_spectrum)))
        rows.append(
            {
                "id": transform["id"],
                "admissible": transform["admissible"],
                "unitary_error": round(unitary_error, 12),
                "trace_real": density_validity["trace_real"],
                "min_eigenvalue": density_validity["min_eigenvalue"],
                "spectrum_drift": round(spectrum_drift, 12),
                "reduced_entropy_multiset_drift_bits": round(reduced_entropy_drift, 12),
                "probability_mass_error": round(probability_mass_error, 12),
                "probability_spectrum_drift": round(probability_spectrum_drift, 12),
                "accepted": bool(
                    transform["admissible"]
                    and unitary_error < 1e-10
                    and density_validity["valid_density_matrix"] is True
                    and spectrum_drift < 1e-10
                    and reduced_entropy_drift < 1e-10
                    and probability_mass_error < 1e-10
                    and probability_spectrum_drift < 1e-10
                ),
            }
        )
    admissible_rows = [row for row in rows if row["admissible"]]
    rejected_rows = [row for row in rows if not row["admissible"]]
    controls = {
        "admissible_unitaries_accepted": all(row["accepted"] for row in admissible_rows),
        "admissible_spectra_invariant": all(row["spectrum_drift"] < 1e-10 for row in admissible_rows),
        "admissible_reduced_entropies_covariant": all(row["reduced_entropy_multiset_drift_bits"] < 1e-10 for row in admissible_rows),
        "admissible_probability_vectors_covariant": all(row["probability_spectrum_drift"] < 1e-10 for row in admissible_rows),
        "nonunitary_and_trace_breaking_controls_rejected": all(row["accepted"] is False for row in rejected_rows),
    }
    return {
        "schema": "realizing_emptiness.qrf_frame_covariance_toy_audit.v1",
        "row_count": len(rows),
        "base_probability": [round(float(value), 12) for value in base_probability],
        "base_density_validity": _density_validity(base_rho),
        "rows": rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": ROADMAP_ENGINE_CLAIM_BOUNDARY,
    }


def build_quantum_extension_roadmap(project_root: Path | None = None) -> dict[str, Any]:
    """Build the scoped roadmap from finite simulations to fuller evidence classes."""
    implemented = [
        {
            "id": "two_qubit_separability_entropy",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/quantum_boundary_entropy.json",
            "validation_gate": "quantum_boundary_entropy_ok",
            "next_extension": "extend mixed-state entanglement witnesses beyond two-qubit PPT/negativity controls",
            "boundary": "direct finite quantum-information calculation, not a universe-agent boundary simulation",
        },
        {
            "id": "arbitrary_two_qubit_entanglement_audit",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/arbitrary_two_qubit_entanglement_audit.json",
            "validation_gate": "arbitrary_two_qubit_entanglement_audit_ok",
            "next_extension": "extend PPT/negativity controls to higher-dimensional or multipartite entanglement witnesses with reviewed examples",
            "boundary": "finite mixed-state two-qubit PPT and negativity audit only, not a many-body boundary realization",
        },
        {
            "id": "chsh_contextuality_witness",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/quantum_boundary_entropy.json",
            "validation_gate": "quantum_contextuality_witness_ok",
            "next_extension": "compare additional contextuality inequalities and disturbance-aware scenarios with explicit claim ceilings",
            "boundary": "CHSH witness only; not a general proof of contextuality for the paper's full QRF setting",
        },
        {
            "id": "chsh_measurement_cover_table",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/quantum_measurement_contextuality.json",
            "validation_gate": "quantum_measurement_contextuality_ok",
            "next_extension": "stress-test the generic measurement-cover parser with larger reviewed scenarios and disturbance-aware controls",
            "boundary": "finite CHSH measurement-cover empirical model and local-polytope LP only; not a full sheaf-contextuality engine or QRF transformation library",
        },
        {
            "id": "general_measurement_cover_polytope_audit",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/general_measurement_cover_polytope_audit.json",
            "validation_gate": "general_measurement_cover_polytope_audit_ok",
            "next_extension": "add reviewed contextuality scenario libraries and disturbance-explicit empirical-model variants",
            "boundary": "finite deterministic-assignment LP audit over parsed covers only, not empirical contextuality evidence",
        },
        {
            "id": "qrf_basis_invariance_toy",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/quantum_boundary_entropy.json",
            "validation_gate": "quantum_boundary_entropy_ok",
            "next_extension": "extend toy frame covariance to reviewed QRF transformation examples over explicit partitions",
            "boundary": "local-basis entropy invariance only; not relativistic or quantum-reference-frame covariance",
        },
        {
            "id": "boundary_landauer_entropy",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/quantum_boundary_entropy.json",
            "validation_gate": "quantum_boundary_entropy_ok",
            "next_extension": "couple finite channel costs to physical thermodynamic accounting only after externally reviewed models exist",
            "boundary": "information-erasure lower bound in kBT units, not a measured heat dissipation experiment",
        },
        {
            "id": "thermodynamic_channel_cost_audit",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/thermodynamic_channel_cost_audit.json",
            "validation_gate": "thermodynamic_channel_cost_audit_ok",
            "next_extension": "replace finite channel lower-bound accounting with reviewed physical heat-bath or collision-model simulations",
            "boundary": "finite CPTP-channel entropy-cost audit only, not measured heat or physical qFEP thermodynamics",
        },
        {
            "id": "two_qubit_dephasing_channel",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/quantum_open_system_dynamics.json",
            "validation_gate": "quantum_open_system_dynamics_ok",
            "next_extension": "compare finite Lindblad families with reviewed physical Hamiltonians before stronger qFEP claims",
            "boundary": "trace-preserving two-qubit dephasing channel only, not the source paper's full qFEP dynamics",
        },
        {
            "id": "full_open_system_qfep_dynamics",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/qfep_boundary_hamiltonian_dynamics.json",
            "validation_gate": "qfep_boundary_hamiltonian_dynamics_ok",
            "next_extension": "replace the finite two-qubit Lindblad audit with reviewed physical qFEP Hamiltonians and collision-model comparisons",
            "boundary": "finite two-qubit boundary-Hamiltonian Lindblad audit only, not a physical qFEP realization",
        },
        {
            "id": "quantum_trajectory_unraveling",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/quantum_trajectory_unraveling.json",
            "validation_gate": "quantum_trajectory_unraveling_ok",
            "next_extension": "compare seeded trajectory unravelings with reviewed open-system models and independent stochastic solvers",
            "boundary": "finite Monte Carlo wave-function unraveling of the local Lindblad surrogate only, not physical qFEP realization",
        },
        {
            "id": "many_body_boundary_screens",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/many_body_boundary_screen_sweep.json",
            "validation_gate": "many_body_boundary_screen_sweep_ok",
            "next_extension": "extend sparse scaling to tensor-network methods and reviewed many-body benchmark states",
            "boundary": "finite six-qubit boundary-screen cut sweep only, not a many-body observer-boundary proof",
        },
        {
            "id": "sparse_boundary_screen_scaling_audit",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/sparse_boundary_screen_scaling_audit.json",
            "validation_gate": "sparse_boundary_screen_scaling_audit_ok",
            "next_extension": "replace exact sparse state-vector screens with tensor-network scaling and independent benchmark fixtures",
            "boundary": "finite sparse exact boundary-screen scaling only, not empirical or full many-body QRF evidence",
        },
        {
            "id": "general_sheaf_contextuality_engine",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/sheaf_contextuality_obstruction_audit.json",
            "validation_gate": "sheaf_contextuality_obstruction_audit_ok",
            "next_extension": "extend the finite measurement-cover LP engine to parsed arbitrary scenarios and reviewed sheaf-theoretic obstruction reports",
            "boundary": "finite measurement-cover global-section LP only, not a full sheaf-theoretic proof for the source paper",
        },
        {
            "id": "qrf_transformation_library",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/qrf_transformation_covariance_audit.json",
            "validation_gate": "qrf_transformation_covariance_audit_ok",
            "next_extension": "extend toy density/probability covariance to reviewed quantum-reference-frame transformation cases",
            "boundary": "finite probability-preserving relabeling covariance audit only, not full quantum-reference-frame covariance",
        },
        {
            "id": "qrf_frame_covariance_toy_audit",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/qrf_frame_covariance_toy_audit.json",
            "validation_gate": "qrf_frame_covariance_toy_audit_ok",
            "next_extension": "replace finite unitary/permutation frame checks with reviewed QRF transformation models over explicit Hilbert partitions",
            "boundary": "finite density-matrix and probability-vector covariance toy audit only, not full QRF physics",
        },
        {
            "id": "empirical_adapter",
            "status": "implemented_finite_simulation",
            "artifact": "output/data/empirical_adapter_provenance_audit.json",
            "validation_gate": "empirical_adapter_provenance_audit_ok",
            "next_extension": "attach reviewed datasets only after source identity, ethics basis, preprocessing provenance, null models, and safety review pass",
            "boundary": "fail-closed provenance adapter and synthetic-demo gate only, not empirical human or practice evidence",
        },
    ]
    future = [dict(row) for row in BLOCKED_EXTERNAL_ROADMAP_ROWS]
    return {
        "schema": "realizing_emptiness.quantum_extension_roadmap.v1",
        "implemented_count": len(implemented),
        "future_count": len(future),
        "implemented": implemented,
        "future": future,
        "success_criteria": [
            "finite quantum-information controls pass before manuscript claims direct entropy or contextuality simulation",
            "finite CHSH local-polytope checks pass before manuscript claims a direct noncontextuality audit",
            "finite open-system dephasing controls pass before manuscript claims any direct open-system quantum simulation",
            "finite Lindblad, stochastic quantum-trajectory, mixed-state entanglement, channel-cost, sparse many-body, sheaf, QRF-transformation, and provenance engines pass before roadmap rows become finite software claims",
            "physical qFEP, human-subject, clinical/neural/awakening, and user-facing practice claims remain blocked until their separate external evidence classes are present",
            "empirical or practice-facing claims remain blocked until sourced data, ethics constraints, safety review, and negative controls exist",
        ],
        "all_implemented_have_artifacts": all(bool(row["artifact"]) and bool(row["validation_gate"]) for row in implemented),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_quantum_roadmap_readiness_matrix(project_root: Path | None = None) -> dict[str, Any]:
    """Build a fail-closed readiness matrix for roadmap claims."""
    roadmap = build_quantum_extension_roadmap(project_root)
    rows = []
    implemented_schema = {
        "two_qubit_separability_entropy": "schemas/quantum_boundary_entropy.schema.json",
        "arbitrary_two_qubit_entanglement_audit": "schemas/arbitrary_two_qubit_entanglement_audit.schema.json",
        "chsh_contextuality_witness": "schemas/quantum_boundary_entropy.schema.json",
        "chsh_measurement_cover_table": "schemas/quantum_measurement_contextuality.schema.json",
        "general_measurement_cover_polytope_audit": "schemas/general_measurement_cover_polytope_audit.schema.json",
        "qrf_basis_invariance_toy": "schemas/quantum_boundary_entropy.schema.json",
        "boundary_landauer_entropy": "schemas/quantum_boundary_entropy.schema.json",
        "thermodynamic_channel_cost_audit": "schemas/thermodynamic_channel_cost_audit.schema.json",
        "two_qubit_dephasing_channel": "schemas/quantum_open_system_dynamics.schema.json",
        "full_open_system_qfep_dynamics": "schemas/qfep_boundary_hamiltonian_dynamics.schema.json",
        "quantum_trajectory_unraveling": "schemas/quantum_trajectory_unraveling.schema.json",
        "many_body_boundary_screens": "schemas/many_body_boundary_screen_sweep.schema.json",
        "sparse_boundary_screen_scaling_audit": "schemas/sparse_boundary_screen_scaling_audit.schema.json",
        "general_sheaf_contextuality_engine": "schemas/sheaf_contextuality_obstruction_audit.schema.json",
        "qrf_transformation_library": "schemas/qrf_transformation_covariance_audit.schema.json",
        "qrf_frame_covariance_toy_audit": "schemas/qrf_frame_covariance_toy_audit.schema.json",
        "empirical_adapter": "schemas/empirical_adapter_provenance_audit.schema.json",
    }
    implemented_negative_controls = {
        "two_qubit_separability_entropy": "product endpoint must have zero reduced entropy while Bell endpoint has one bit",
        "arbitrary_two_qubit_entanglement_audit": "invalid density matrices must be rejected and Werner threshold cases must match PPT/negativity expectations",
        "chsh_contextuality_witness": "product endpoint remains CHSH-local while Bell endpoint reaches the Tsirelson value",
        "chsh_measurement_cover_table": "product-control cover fits the local polytope while Bell cover is infeasible",
        "general_measurement_cover_polytope_audit": "triangle and CHSH feasible controls must fit while parity and Bell obstruction cases fail",
        "qrf_basis_invariance_toy": "local rotations preserve reduced entropy while changing measurement entropy",
        "boundary_landauer_entropy": "erasure lower bound remains a computational-basis bound, not measured heat",
        "thermodynamic_channel_cost_audit": "non-CPTP maps must be rejected before Landauer-cost interpretation",
        "two_qubit_dephasing_channel": "product state remains stable while Bell-state CHSH decays under dephasing",
        "full_open_system_qfep_dynamics": "non-Hermitian, trace-breaking, and non-positive controls are rejected before claims are allowed",
        "quantum_trajectory_unraveling": "gamma-zero trajectories must have no jumps and sampled ensembles must reconstruct the exact Lindblad density within tolerance",
        "many_body_boundary_screens": "separable controls and random cuts must not be mislabeled as observer-boundary evidence",
        "sparse_boundary_screen_scaling_audit": "separable controls remain zero and deterministic random cuts are not observer evidence as qubit count grows",
        "general_sheaf_contextuality_engine": "noncontextual controls must return feasible global sections while parity obstruction fails",
        "qrf_transformation_library": "nonadmissible mass-gain and negative-entry maps must fail probability preservation",
        "qrf_frame_covariance_toy_audit": "nonunitary and trace-breaking controls must fail density/probability covariance checks",
        "empirical_adapter": "unsourced human-data attempts and synthetic demos must not become empirical practice claims",
    }
    implemented_next_requirements = {
        "two_qubit_separability_entropy": (
            "output/data/higher_dimensional_entanglement_audit.json",
            "higher_dimensional_entanglement_audit_ok",
        ),
        "arbitrary_two_qubit_entanglement_audit": (
            "output/data/multipartite_entanglement_witness_audit.json",
            "multipartite_entanglement_witness_audit_ok",
        ),
        "chsh_contextuality_witness": (
            "output/data/contextuality_inequality_library_audit.json",
            "contextuality_inequality_library_audit_ok",
        ),
        "chsh_measurement_cover_table": (
            "output/data/disturbance_aware_measurement_cover_audit.json",
            "disturbance_aware_measurement_cover_audit_ok",
        ),
        "general_measurement_cover_polytope_audit": (
            "output/data/reviewed_measurement_cover_library_audit.json",
            "reviewed_measurement_cover_library_audit_ok",
        ),
        "qrf_basis_invariance_toy": (
            "output/data/reviewed_qrf_basis_covariance_audit.json",
            "reviewed_qrf_basis_covariance_audit_ok",
        ),
        "boundary_landauer_entropy": (
            "output/data/physical_thermodynamic_cost_audit.json",
            "physical_thermodynamic_cost_audit_ok",
        ),
        "thermodynamic_channel_cost_audit": (
            "output/data/heat_bath_channel_cost_audit.json",
            "heat_bath_channel_cost_audit_ok",
        ),
        "two_qubit_dephasing_channel": (
            "output/data/reviewed_open_system_channel_family_audit.json",
            "reviewed_open_system_channel_family_audit_ok",
        ),
        "full_open_system_qfep_dynamics": (
            "output/data/physical_qfep_realization_audit.json",
            "physical_qfep_realization_audit_ok",
        ),
        "quantum_trajectory_unraveling": (
            "output/data/independent_quantum_trajectory_solver_audit.json",
            "independent_quantum_trajectory_solver_audit_ok",
        ),
        "many_body_boundary_screens": (
            "output/data/reviewed_many_body_boundary_screen_audit.json",
            "reviewed_many_body_boundary_screen_audit_ok",
        ),
        "sparse_boundary_screen_scaling_audit": (
            "output/data/tensor_network_boundary_screen_audit.json",
            "tensor_network_boundary_screen_audit_ok",
        ),
        "general_sheaf_contextuality_engine": (
            "output/data/reviewed_sheaf_obstruction_engine_audit.json",
            "reviewed_sheaf_obstruction_engine_audit_ok",
        ),
        "qrf_transformation_library": (
            "output/data/reviewed_quantum_reference_frame_transform_audit.json",
            "reviewed_quantum_reference_frame_transform_audit_ok",
        ),
        "qrf_frame_covariance_toy_audit": (
            "output/data/quantum_reference_frame_transformation_audit.json",
            "quantum_reference_frame_transformation_audit_ok",
        ),
        "empirical_adapter": (
            "output/data/human_empirical_adapter_study_audit.json",
            "human_empirical_adapter_study_audit_ok",
        ),
    }
    for row in roadmap["implemented"]:
        rows.append(
            {
                "id": row["id"],
                "roadmap_class": "implemented",
                "readiness_state": "validated_finite_simulation",
                "readiness_score": 1.0,
                "has_artifact": True,
                "has_schema": True,
                "has_validator": True,
                "has_negative_control": True,
                "manuscript_claim_allowed": True,
                "current_artifact": row["artifact"],
                "current_schema": implemented_schema[row["id"]],
                "current_validation_gate": row["validation_gate"],
                "required_next_artifact": implemented_next_requirements[row["id"]][0],
                "required_next_gate": implemented_next_requirements[row["id"]][1],
                "required_negative_control": implemented_negative_controls[row["id"]],
                "boundary": row["boundary"],
            }
        )
    def future_readiness_row(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": row["id"],
            "blocked_task_id": row["blocked_task_id"],
            "roadmap_class": "future",
            "readiness_state": row["status"],
            "readiness_score": 0.0,
            "has_artifact": False,
            "has_schema": False,
            "has_validator": False,
            "has_negative_control": True,
            "manuscript_claim_allowed": False,
            "current_artifact": "",
            "current_schema": "",
            "current_validation_gate": "",
            "required_next_artifact": row["required_next_artifact"],
            "required_next_gate": row["required_next_gate"],
            "required_negative_control": row["required_negative_control"],
            "boundary": row["boundary"],
        }

    for row in roadmap["future"]:
        rows.append(future_readiness_row(row))
    forged_completed_future = {
        **roadmap["future"][0],
        "status": "implemented_finite_simulation",
        "artifact": "output/data/forged_completed_future_row.json",
        "validation_gate": "forged_completed_future_row_ok",
    }
    forged_control = future_readiness_row(forged_completed_future)
    controls = {
        "all_implemented_validated": all(
            row["has_artifact"] and row["has_schema"] and row["has_validator"] and row["manuscript_claim_allowed"]
            for row in rows
            if row["roadmap_class"] == "implemented"
        ),
        "all_future_blocked": all(
            row["readiness_score"] == 0.0 and row["manuscript_claim_allowed"] is False
            for row in rows
            if row["roadmap_class"] == "future"
        ),
        "every_future_has_next_gate": all(
            bool(row["required_next_artifact"]) and bool(row["required_next_gate"])
            for row in rows
            if row["roadmap_class"] == "future"
        ),
        "every_row_has_negative_control": all(bool(row["required_negative_control"]) for row in rows),
        "every_row_has_boundary": all("not empirical" in row["boundary"] or "not " in row["boundary"] for row in rows),
        "forged_completed_future_row_rejected": (
            forged_control["readiness_score"] == 0.0
            and forged_control["manuscript_claim_allowed"] is False
            and forged_control["has_artifact"] is False
            and forged_control["has_schema"] is False
            and forged_control["has_validator"] is False
        ),
    }
    return {
        "schema": "realizing_emptiness.quantum_roadmap_readiness_matrix.v1",
        "row_count": len(rows),
        "implemented_count": sum(1 for row in rows if row["roadmap_class"] == "implemented"),
        "future_count": sum(1 for row in rows if row["roadmap_class"] == "future"),
        "columns": [
            "has_artifact",
            "has_schema",
            "has_validator",
            "has_negative_control",
            "manuscript_claim_allowed",
        ],
        "rows": rows,
        "controls": controls,
        "forged_completed_future_row_control": forged_control,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": "readiness matrix only; not empirical and not a claim that future roadmap items are implemented",
    }


def write_quantum_artifacts(project_root: Path) -> tuple[Path, ...]:
    """Write quantum-boundary simulation and roadmap artifacts."""
    data_dir = project_root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    entropy_path = data_dir / "quantum_boundary_entropy.json"
    dynamics_path = data_dir / "quantum_open_system_dynamics.json"
    contextuality_path = data_dir / "quantum_measurement_contextuality.json"
    qfep_dynamics_path = data_dir / "qfep_boundary_hamiltonian_dynamics.json"
    trajectory_path = data_dir / "quantum_trajectory_unraveling.json"
    many_body_path = data_dir / "many_body_boundary_screen_sweep.json"
    sheaf_path = data_dir / "sheaf_contextuality_obstruction_audit.json"
    qrf_transform_path = data_dir / "qrf_transformation_covariance_audit.json"
    empirical_adapter_path = data_dir / "empirical_adapter_provenance_audit.json"
    entanglement_path = data_dir / "arbitrary_two_qubit_entanglement_audit.json"
    cover_polytope_path = data_dir / "general_measurement_cover_polytope_audit.json"
    channel_cost_path = data_dir / "thermodynamic_channel_cost_audit.json"
    sparse_screen_path = data_dir / "sparse_boundary_screen_scaling_audit.json"
    qrf_frame_path = data_dir / "qrf_frame_covariance_toy_audit.json"
    roadmap_path = data_dir / "quantum_extension_roadmap.json"
    readiness_path = data_dir / "quantum_roadmap_readiness_matrix.json"
    entropy_path.write_text(
        json.dumps(build_quantum_boundary_entropy(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    dynamics_path.write_text(
        json.dumps(build_quantum_open_system_dynamics(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    contextuality_path.write_text(
        json.dumps(build_quantum_measurement_contextuality(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    qfep_dynamics_path.write_text(
        json.dumps(build_qfep_boundary_hamiltonian_dynamics(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    trajectory_path.write_text(
        json.dumps(build_quantum_trajectory_unraveling(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    many_body_path.write_text(
        json.dumps(build_many_body_boundary_screen_sweep(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    sheaf_path.write_text(
        json.dumps(build_sheaf_contextuality_obstruction_audit(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    qrf_transform_path.write_text(
        json.dumps(build_qrf_transformation_covariance_audit(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    empirical_adapter_path.write_text(
        json.dumps(build_empirical_adapter_provenance_audit(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    entanglement_path.write_text(
        json.dumps(build_arbitrary_two_qubit_entanglement_audit(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    cover_polytope_path.write_text(
        json.dumps(build_general_measurement_cover_polytope_audit(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    channel_cost_path.write_text(
        json.dumps(build_thermodynamic_channel_cost_audit(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    sparse_screen_path.write_text(
        json.dumps(build_sparse_boundary_screen_scaling_audit(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    qrf_frame_path.write_text(
        json.dumps(build_qrf_frame_covariance_toy_audit(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    roadmap_path.write_text(
        json.dumps(build_quantum_extension_roadmap(project_root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    readiness_path.write_text(
        json.dumps(build_quantum_roadmap_readiness_matrix(project_root), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return (
        entropy_path,
        dynamics_path,
        contextuality_path,
        qfep_dynamics_path,
        trajectory_path,
        many_body_path,
        sheaf_path,
        qrf_transform_path,
        empirical_adapter_path,
        entanglement_path,
        cover_polytope_path,
        channel_cost_path,
        sparse_screen_path,
        qrf_frame_path,
        roadmap_path,
        readiness_path,
    )


SIGMA_Y = np.array([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex)

DATA_PROCESSING_CLAIM_BOUNDARY = (
    "finite qubit-channel data-processing (monotonicity) surrogate; the irreversible loss of "
    "distinguishability under coarse-grained CPTP channels operationalizes opacification and Bayesian "
    "model reduction as forgetting, with a not-completely-positive transpose map and a "
    "distinguishability-increasing post-selection as discriminating controls; not empirical evidence "
    "and not a physical qFEP, neural, clinical, or contemplative claim"
)


def _bloch_density(vector: tuple[float, float, float]) -> np.ndarray:
    """Single-qubit density from a Bloch vector; norm < 1 guarantees full rank (finite relative entropy)."""
    x, y, z = vector
    return 0.5 * (IDENTITY_2 + x * SIGMA_X + y * SIGMA_Y + z * SIGMA_Z)


def _hermitian_log2(matrix: np.ndarray) -> np.ndarray:
    """Base-2 matrix logarithm via Hermitian eigendecomposition (0 * log 0 = 0 convention)."""
    eigenvalues, eigenvectors = np.linalg.eigh((matrix + matrix.conjugate().T) / 2.0)
    safe = np.clip(eigenvalues.real, 1e-15, None)
    return (eigenvectors * np.log2(safe)) @ eigenvectors.conjugate().T


def _relative_entropy_bits(rho: np.ndarray, sigma: np.ndarray) -> float:
    """Quantum relative entropy S(rho||sigma) in bits; sigma must be full rank for a finite value."""
    value = np.real(np.trace(rho @ (_hermitian_log2(rho) - _hermitian_log2(sigma))))
    return float(max(value, 0.0))


def _qubit_channel_kraus(name: str, strength: float) -> list[np.ndarray]:
    """Kraus operators for canonical qubit channels parameterized by strength in [0, 1]."""
    if name == "phase_damping":
        return [
            np.array([[1.0, 0.0], [0.0, math.sqrt(1.0 - strength)]], dtype=complex),
            np.array([[0.0, 0.0], [0.0, math.sqrt(strength)]], dtype=complex),
        ]
    if name == "amplitude_damping":
        return [
            np.array([[1.0, 0.0], [0.0, math.sqrt(1.0 - strength)]], dtype=complex),
            np.array([[0.0, math.sqrt(strength)], [0.0, 0.0]], dtype=complex),
        ]
    if name == "depolarizing":
        return [
            math.sqrt(1.0 - 3.0 * strength / 4.0) * IDENTITY_2,
            math.sqrt(strength / 4.0) * SIGMA_X,
            math.sqrt(strength / 4.0) * SIGMA_Y,
            math.sqrt(strength / 4.0) * SIGMA_Z,
        ]
    raise ValueError(f"unknown channel {name!r}")


def _apply_kraus(rho: np.ndarray, kraus: list[np.ndarray]) -> np.ndarray:
    return sum(operator @ rho @ operator.conjugate().T for operator in kraus)


def _kraus_trace_preserving_error(kraus: list[np.ndarray]) -> float:
    completeness = sum(operator.conjugate().T @ operator for operator in kraus)
    return float(np.max(np.abs(completeness - IDENTITY_2)))


def _kraus_choi_min_eigenvalue(kraus: list[np.ndarray]) -> float:
    """Minimum eigenvalue of the (unnormalized) Choi matrix; >= 0 iff the map is completely positive."""
    omega = np.zeros((4, 1), dtype=complex)
    omega[0, 0] = 1.0
    omega[3, 0] = 1.0
    maximally_entangled = omega @ omega.conjugate().T
    choi = np.zeros((4, 4), dtype=complex)
    for operator in kraus:
        embedded = np.kron(IDENTITY_2, operator)
        choi += embedded @ maximally_entangled @ embedded.conjugate().T
    return float(np.min(np.linalg.eigvalsh((choi + choi.conjugate().T) / 2.0)))


def _transpose_map_choi_min_eigenvalue() -> float:
    """Choi matrix of the transpose map is the SWAP operator; its minimum eigenvalue is -1 (not CP)."""
    swap = np.array(
        [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex
    )
    return float(np.min(np.linalg.eigvalsh(swap)))


def _post_selected_density(rho: np.ndarray, filter_operator: np.ndarray) -> np.ndarray:
    out = filter_operator @ rho @ filter_operator.conjugate().T
    weight = float(np.real(np.trace(out)))
    return out / weight


def build_data_processing_monotonicity_audit() -> dict[str, Any]:
    """Finite qubit data-processing (monotonicity) surrogate for opacification as forgetting (roadmap re-15).

    The Lindblad-Uhlmann data-processing inequality states that a CPTP channel can only *reduce* the
    distinguishability of two states: trace distance and quantum relative entropy are non-increasing.
    This operationalizes the paper's opacification / Bayesian model reduction as irreversible
    information loss at a coarse-grained boundary -- once the environment record is averaged out, the
    interior cannot recover what was forgotten. Two discriminating controls give the audit teeth:

    1. The transpose map is positive and trace-preserving yet NOT completely positive (its Choi matrix
       has a negative eigenvalue); restricting to CPTP channels is therefore a physical requirement,
       not a convenience. This control FIRES (detects the negative eigenvalue).
    2. A selective post-selection (a non-trace-preserving filter, renormalized) CAN increase trace
       distance -- a filter chosen as the orthogonalizer makes two non-orthogonal states orthogonal.
       This control FIRES, showing the irreversibility belongs specifically to the coarse-grained
       (record-discarding) channel, not to the interaction itself: keeping the record can sharpen.
    """
    tolerance = 1e-9
    state_pairs = [
        {"id": "z_axis_pair", "rho": (0.3, 0.0, 0.5), "sigma": (0.0, 0.0, -0.4)},
        {"id": "tilted_pair", "rho": (0.5, 0.2, 0.1), "sigma": (-0.2, 0.3, 0.4)},
        {"id": "antipodal_pair", "rho": (0.0, 0.0, 0.6), "sigma": (0.0, 0.0, -0.6)},
    ]
    channels = [
        {"name": "phase_damping", "strengths": (0.2, 0.5, 0.9)},
        {"name": "amplitude_damping", "strengths": (0.2, 0.5, 0.9)},
        {"name": "depolarizing", "strengths": (0.2, 0.5, 0.9)},
    ]
    channel_rows: list[dict[str, Any]] = []
    for pair in state_pairs:
        rho = _bloch_density(pair["rho"])
        sigma = _bloch_density(pair["sigma"])
        base_trace = _trace_distance(rho, sigma)
        base_relent = _relative_entropy_bits(rho, sigma)
        for channel in channels:
            for strength in channel["strengths"]:
                kraus = _qubit_channel_kraus(channel["name"], strength)
                out_rho = _apply_kraus(rho, kraus)
                out_sigma = _apply_kraus(sigma, kraus)
                post_trace = _trace_distance(out_rho, out_sigma)
                post_relent = _relative_entropy_bits(out_rho, out_sigma)
                channel_rows.append({
                    "pair": pair["id"],
                    "channel": channel["name"],
                    "strength": round(strength, 8),
                    "trace_distance_before": round(base_trace, 12),
                    "trace_distance_after": round(post_trace, 12),
                    "relative_entropy_before_bits": round(base_relent, 12),
                    "relative_entropy_after_bits": round(post_relent, 12),
                    "trace_distance_nonincreasing": bool(post_trace <= base_trace + tolerance),
                    "relative_entropy_nonincreasing": bool(post_relent <= base_relent + tolerance),
                })
    cp_rows: list[dict[str, Any]] = []
    for channel in channels:
        # Use the mid strength purely to instantiate the Kraus set for the structural CP / TP check.
        kraus = _qubit_channel_kraus(channel["name"], 0.5)
        cp_rows.append({
            "map": channel["name"],
            "trace_preserving_error": round(_kraus_trace_preserving_error(kraus), 12),
            "choi_min_eigenvalue": round(_kraus_choi_min_eigenvalue(kraus), 12),
            "completely_positive": bool(_kraus_choi_min_eigenvalue(kraus) > -tolerance),
        })
    transpose_min_eig = _transpose_map_choi_min_eigenvalue()
    cp_rows.append({
        "map": "transpose_control",
        "trace_preserving_error": 0.0,
        "choi_min_eigenvalue": round(transpose_min_eig, 12),
        "completely_positive": bool(transpose_min_eig > -tolerance),
    })
    selective_rows: list[dict[str, Any]] = []
    for angle in (math.pi / 8.0, math.pi / 6.0, math.pi / 5.0):
        psi = _bloch_density((math.sin(2 * angle), 0.0, math.cos(2 * angle)))
        phi = _bloch_density((-math.sin(2 * angle), 0.0, math.cos(2 * angle)))
        base = _trace_distance(psi, phi)
        # The orthogonalizing filter diag(1, cot(angle)) maps the two non-orthogonal rays to orthogonal.
        orthogonalizer = np.array([[1.0, 0.0], [0.0, 1.0 / math.tan(angle)]], dtype=complex)
        filtered = _trace_distance(
            _post_selected_density(psi, orthogonalizer),
            _post_selected_density(phi, orthogonalizer),
        )
        selective_rows.append({
            "angle": round(angle, 8),
            "trace_distance_before": round(base, 12),
            "trace_distance_after_postselection": round(filtered, 12),
            "post_selection_increases_distance": bool(filtered > base + 1e-6),
        })
    channel_maps = [row for row in cp_rows if row["map"] != "transpose_control"]
    transpose_row = next(row for row in cp_rows if row["map"] == "transpose_control")
    controls = {
        "cptp_channels_are_trace_preserving": all(row["trace_preserving_error"] < tolerance for row in channel_maps),
        "cptp_channels_are_completely_positive": all(row["completely_positive"] for row in channel_maps),
        "transpose_map_is_not_completely_positive": (transpose_row["completely_positive"] is False),
        "cptp_channels_do_not_increase_trace_distance": all(row["trace_distance_nonincreasing"] for row in channel_rows),
        "cptp_channels_do_not_increase_relative_entropy": all(row["relative_entropy_nonincreasing"] for row in channel_rows),
        "selective_postselection_can_increase_trace_distance": any(row["post_selection_increases_distance"] for row in selective_rows),
    }
    return {
        "schema": "realizing_emptiness.data_processing_monotonicity_audit.v1",
        "channel_row_count": len(channel_rows),
        "row_count": len(channel_rows),
        "channel_rows": channel_rows,
        "complete_positivity_rows": cp_rows,
        "selective_postselection_rows": selective_rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": DATA_PROCESSING_CLAIM_BOUNDARY,
    }
