from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import linprog

from formalism.review_response_common import CLAIM_BOUNDARY, load_json, round_float


def context_signs() -> dict[str, int]:
    return {"A0B0": 1, "A0B1": 1, "A1B0": 1, "A1B1": -1}


def model_rows(probability_rows: list[dict[str, Any]], model: str) -> list[dict[str, Any]]:
    return [row for row in probability_rows if row.get("model") == model]


def expectation_from_rows(rows: list[dict[str, Any]], context: str) -> float:
    return float(
        sum(
            row["a_outcome"] * row["b_outcome"] * row["probability"]
            for row in rows
            if row.get("context") == context
        )
    )


def chsh_from_probabilities(rows: list[dict[str, Any]]) -> float:
    return float(sum(sign * expectation_from_rows(rows, context) for context, sign in context_signs().items()))


def independent_assignments() -> list[dict[str, int]]:
    assignments = []
    for a0 in (-1, 1):
        for a1 in (-1, 1):
            for b0 in (-1, 1):
                for b1 in (-1, 1):
                    assignments.append({"A0": a0, "A1": a1, "B0": b0, "B1": b1})
    return assignments


def independent_probability_vector(rows: list[dict[str, Any]]) -> tuple[list[str], np.ndarray]:
    labels = []
    values = []
    for context in ("A0B0", "A0B1", "A1B0", "A1B1"):
        for outcome in ("++", "+-", "-+", "--"):
            labels.append(f"{context}:{outcome}")
            match = next(row for row in rows if row["context"] == context and row["outcome"] == outcome)
            values.append(match["probability"])
    return labels, np.asarray(values, dtype=float)


def independent_polytope_matrix(labels: list[str]) -> np.ndarray:
    assignments = independent_assignments()
    matrix = np.zeros((len(labels), len(assignments)), dtype=float)
    for label_index, label in enumerate(labels):
        context, outcome = label.split(":")
        a_setting = context[:2]
        b_setting = context[2:]
        target_a = 1 if outcome[0] == "+" else -1
        target_b = 1 if outcome[1] == "+" else -1
        for assignment_index, assignment in enumerate(assignments):
            matrix[label_index, assignment_index] = float(
                assignment[a_setting] == target_a and assignment[b_setting] == target_b
            )
    return matrix


def independent_polytope_fit(rows: list[dict[str, Any]], model: str) -> dict[str, Any]:
    model_specific_rows = model_rows(rows, model)
    labels, target = independent_probability_vector(model_specific_rows)
    matrix = independent_polytope_matrix(labels)
    assignment_count = matrix.shape[1]
    exact = linprog(
        c=np.zeros(assignment_count),
        A_eq=np.vstack([np.ones((1, assignment_count)), matrix]),
        b_eq=np.concatenate([[1.0], target]),
        bounds=[(0.0, 1.0)] * assignment_count,
        method="highs",
    )
    slack_count = 2 * len(labels)
    relaxed = linprog(
        c=np.concatenate([np.zeros(assignment_count), np.ones(slack_count)]),
        A_eq=np.vstack(
            [
                np.concatenate([np.ones(assignment_count), np.zeros(slack_count)]),
                np.hstack([matrix, np.eye(len(labels)), -np.eye(len(labels))]),
            ]
        ),
        b_eq=np.concatenate([[1.0], target]),
        bounds=[(0.0, 1.0)] * assignment_count + [(0.0, None)] * slack_count,
        method="highs",
    )
    weights = exact.x if exact.success else relaxed.x[:assignment_count] if relaxed.success else np.zeros(assignment_count)
    residual = matrix @ weights - target
    return {
        "model": model,
        "feasible": bool(exact.success),
        "assignment_count": assignment_count,
        "min_l1_residual": round_float(float(relaxed.fun if relaxed.success else np.sum(np.abs(residual)))),
        "max_abs_residual": round_float(float(np.max(np.abs(residual)) if len(residual) else 0.0)),
    }


def build_quantum_independent_crosscheck_audit(project_root: Path) -> dict[str, Any]:
    contextuality = load_json(project_root / "output" / "data" / "quantum_measurement_contextuality.json")
    rows = contextuality.get("probability_rows", [])
    tsirelson = 2.0 * math.sqrt(2.0)
    product_chsh = chsh_from_probabilities(model_rows(rows, "product_control"))
    bell_chsh = chsh_from_probabilities(model_rows(rows, "bell_measurement_cover"))
    product_fit = independent_polytope_fit(rows, "product_control")
    bell_fit = independent_polytope_fit(rows, "bell_measurement_cover")
    perturbed_expected_value = tsirelson + 0.125
    control_rows = [
        {
            "check": "product_locality",
            "computed": round_float(product_chsh),
            "expected_boundary": "<= 2.0",
            "passes": product_chsh <= 2.0 + 1e-9,
        },
        {
            "check": "bell_tsirelson",
            "computed": round_float(bell_chsh),
            "expected_boundary": "2*sqrt(2)",
            "passes": abs(bell_chsh - tsirelson) < 1e-9,
        },
        {
            "check": "product_local_polytope",
            "computed": product_fit,
            "expected_boundary": "feasible",
            "passes": product_fit.get("feasible") is True and product_fit.get("min_l1_residual", 1.0) < 1e-8,
        },
        {
            "check": "bell_local_polytope",
            "computed": bell_fit,
            "expected_boundary": "infeasible",
            "passes": bell_fit.get("feasible") is False and bell_fit.get("min_l1_residual", 0.0) > 0.1,
        },
        {
            "check": "perturbed_expected_value_control",
            "computed": round_float(perturbed_expected_value),
            "expected_boundary": "<= 2*sqrt(2)",
            "passes": perturbed_expected_value <= tsirelson + 1e-9,
        },
    ]
    controls = {
        "product_local_crosscheck": control_rows[0]["passes"] is True,
        "bell_tsirelson_crosscheck": control_rows[1]["passes"] is True,
        "product_polytope_feasible_independent": control_rows[2]["passes"] is True,
        "bell_polytope_infeasible_independent": control_rows[3]["passes"] is True,
        "perturbed_expected_value_control_fails": control_rows[4]["passes"] is False,
        "independent_assignment_count_16": product_fit.get("assignment_count") == bell_fit.get("assignment_count") == 16,
        "claim_boundary_declared": "not empirical" in CLAIM_BOUNDARY,
    }
    return {
        "schema": "realizing_emptiness.quantum_independent_crosscheck_audit.v1",
        "method": "closed-form CHSH expectation sums plus independent local-polytope linear programs over deterministic assignments",
        "computed": {
            "product_control_chsh": round_float(product_chsh),
            "bell_chsh": round_float(bell_chsh),
            "local_chsh_bound": 2.0,
            "tsirelson_bound": round_float(tsirelson),
        },
        "rows": control_rows,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": CLAIM_BOUNDARY,
    }
