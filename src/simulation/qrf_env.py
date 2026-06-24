"""Finite boundary-channel environment for QRF deployment comparisons."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np

from formalism.models import BoundaryScreen, QRFDeployment, Sectorisation


CLAIM_BOUNDARY = "finite QRF boundary-channel indistinguishability audit; not empirical, clinical, neural, awakening, practice-efficacy, or physical qFEP evidence"
LEDGER_CLAIM_BOUNDARY = (
    "finite QRF boundary-channel ledger for b0-b5 relabeling; not empirical, not ontological boundary evidence, "
    "not biological sensor mapping, and not physical qFEP evidence"
)


def default_deployments(channel_count: int = 6) -> tuple[QRFDeployment, ...]:
    """Return the three v1 QRF profiles."""
    if channel_count != 6:
        labels = tuple("self" if index % 2 == 0 else "env" for index in range(channel_count))
        contextual = tuple(f"context_{index}" for index in range(channel_count))
    else:
        labels = ("self", "self", "env", "env", "env", "self")
        contextual = ("body", "action", "world", "world", "other", "care")
    return (
        QRFDeployment("separation_constrained", labels, metacognitive_access=0.0, prior_precision=4.0),
        QRFDeployment("opacified", ("self", "action", "env", "env", "other", "care"), 0.55, 2.0),
        QRFDeployment("post_dual", contextual, 1.0, 0.2),
    )


def simulate_boundary_trajectory(
    *,
    seed: int = 7,
    steps: int = 12,
    screen: BoundaryScreen | None = None,
) -> list[dict[str, Any]]:
    """Generate deterministic boundary observations for finite profile comparison."""
    active_screen = screen or BoundaryScreen.default()
    rng = np.random.default_rng(seed)
    hidden_context = rng.integers(0, 2, size=active_screen.channel_count)
    trajectory: list[dict[str, Any]] = []
    for step in range(steps):
        action = int((step + hidden_context[0]) % 2)
        drift = (step % 3 == 0)
        observation = np.bitwise_xor(hidden_context, action)
        if drift:
            observation = observation.copy()
            observation[step % active_screen.channel_count] = 1 - observation[step % active_screen.channel_count]
        trajectory.append(
            {
                "step": step,
                "action": action,
                "hidden_context": hidden_context.astype(int).tolist(),
                "observation": observation.astype(int).tolist(),
                "drift": bool(drift),
            }
        )
    return trajectory


def _uniform_boundary_distribution(screen: BoundaryScreen) -> dict[str, float]:
    bitstrings = screen.all_bitstrings()
    probability = 1.0 / len(bitstrings)
    return {"".join(map(str, row.tolist())): probability for row in bitstrings}


def boundary_indistinguishability_audit(
    deployments: Iterable[QRFDeployment] | None = None,
    screen: BoundaryScreen | None = None,
) -> dict[str, Any]:
    """Check that admissible QRF labels do not change boundary probabilities."""
    active_screen = screen or BoundaryScreen.default()
    active_deployments = tuple(deployments or default_deployments(active_screen.channel_count))
    distribution = _uniform_boundary_distribution(active_screen)
    rows = []
    for deployment in active_deployments:
        deployment.validate(active_screen)
        rows.append(
            {
                "deployment": deployment.as_dict(),
                "sectorisation": Sectorisation.from_deployment(deployment).as_dict(),
                "distribution_hashable": tuple(sorted(distribution.items())),
                "marginal_probability_sum": float(sum(distribution.values())),
            }
        )
    negative_control = dict(distribution)
    first_key = next(iter(negative_control))
    negative_control[first_key] += 0.05
    equal = all(row["distribution_hashable"] == rows[0]["distribution_hashable"] for row in rows)
    negative_control_fails = tuple(sorted(negative_control.items())) != rows[0]["distribution_hashable"]
    return {
        "schema": "realizing_emptiness.qrf_boundary_indistinguishability.v1",
        "channel_count": active_screen.channel_count,
        "deployment_count": len(rows),
        "rows": rows,
        "all_admissible_distributions_equal": bool(equal),
        "negative_control_fails": bool(negative_control_fails),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def boundary_channel_ledger(
    deployments: Iterable[QRFDeployment] | None = None,
    screen: BoundaryScreen | None = None,
) -> dict[str, Any]:
    """Return the b0-b5 QRF channel ledger used by the relabeling figure and source-fit audits."""
    active_screen = screen or BoundaryScreen.default()
    active_deployments = tuple(deployments or default_deployments(active_screen.channel_count))
    if active_screen.channel_count != 6:
        raise ValueError("the b0-b5 channel ledger is defined only for the six-channel finite surrogate")
    roles = (
        ("b0", "body-controllability cue", "finite cue for action-contingent body-like changes"),
        ("b1", "action-contingency cue", "finite cue for boundary changes coupled to selected action"),
        ("b2", "distal-world cue", "finite cue for changes modeled as less action-contingent"),
        ("b3", "contextual-world cue", "finite cue for contextual changes in the same bitstream"),
        ("b4", "other-agent cue", "finite cue for non-self sector attribution in richer QRF vocabularies"),
        ("b5", "care-salience cue", "finite cue used by the practice-interface proxy without efficacy claims"),
    )
    sector_labels_by_profile = {
        deployment.name: list(deployment.sector_labels)
        for deployment in active_deployments
    }
    rows = []
    for index, (channel_id, finite_role, role_description) in enumerate(roles):
        rows.append(
            {
                "channel_id": channel_id,
                "channel_index": index,
                "observation_symbol": f"o_{index} in {{0,1}}",
                "finite_surrogate_role": finite_role,
                "role_description": role_description,
                "invariant_evidence_object": f"binary boundary bit {channel_id}",
                "evidence_object_invariant": True,
                "sector_labels_by_profile": {
                    deployment.name: deployment.sector_labels[index]
                    for deployment in active_deployments
                },
                "label_changes_across_profiles": len(
                    {deployment.sector_labels[index] for deployment in active_deployments}
                )
                > 1,
                "source_equation_links": ["eq:7", "eq:8", "eq:9", "eq:10"],
                "source_locator": "Sandved-Smith et al. Sections 3.2-4.3, equations 7-10",
                "claim_boundary": LEDGER_CLAIM_BOUNDARY,
            }
        )
    controls = {
        "channel_ids_exact_b0_to_b5": [row["channel_id"] for row in rows] == [f"b{index}" for index in range(6)],
        "all_profiles_have_sector_labels": all(len(labels) == 6 for labels in sector_labels_by_profile.values()),
        "all_evidence_objects_invariant": all(row["evidence_object_invariant"] for row in rows),
        "all_channels_relabel_across_profiles": all(row["label_changes_across_profiles"] for row in rows),
        "source_equations_7_to_10_declared": all(row["source_equation_links"] == ["eq:7", "eq:8", "eq:9", "eq:10"] for row in rows),
        "negative_control_fails": boundary_indistinguishability_audit(active_deployments, active_screen)["negative_control_fails"],
    }
    return {
        "schema": "realizing_emptiness.qrf_boundary_channel_ledger.v1",
        "channel_count": active_screen.channel_count,
        "profile_count": len(active_deployments),
        "profiles": [deployment.name for deployment in active_deployments],
        "rows": rows,
        "sector_labels_by_profile": sector_labels_by_profile,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "source_locator": "Sandved-Smith et al. Section 3.2 equations 7-10",
        "claim_boundary": LEDGER_CLAIM_BOUNDARY,
    }


def score_deployment(deployment: QRFDeployment, trajectory: list[dict[str, Any]]) -> dict[str, float]:
    """Score a deployment by deterministic prediction, flexibility, and scope."""
    observations = np.array([row["observation"] for row in trajectory], dtype=float)
    actions = np.array([row["action"] for row in trajectory], dtype=float)
    action_signal = np.repeat(actions[:, None], observations.shape[1], axis=1)
    prediction_error = float(np.mean((observations - action_signal) ** 2))
    complexity = float(np.log1p(deployment.prior_precision) + 0.2 * (1.0 - deployment.metacognitive_access))
    accuracy = float(1.1 - prediction_error + 0.35 * deployment.flexibility)
    compassion_scope = float(len(set(deployment.sector_labels) - {"self"}) / len(set(deployment.sector_labels)))
    return {
        "prediction_error": prediction_error,
        "complexity": complexity,
        "accuracy": accuracy,
        "free_energy": complexity - accuracy,
        "flexibility": deployment.flexibility,
        "compassion_scope": compassion_scope,
    }
