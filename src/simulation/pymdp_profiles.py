"""Discrete active-inference profiles with pymdp runtime dependency diagnostics."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import platform
import sys
import warnings
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

import numpy as np

from formalism.models import BoundaryScreen, QRFDeployment
from simulation.qrf_env import default_deployments, simulate_boundary_trajectory
from modeling.registry import load_model, model_parameters

if TYPE_CHECKING:
    from pymdp.agent import Agent


STATE_LABELS = tuple(model_parameters("qrf_boundary")["state_labels"])
OBSERVATION_LABELS = tuple(model_parameters("qrf_boundary")["observation_labels"])
ACTION_LABELS = tuple(model_parameters("qrf_boundary")["action_labels"])
PYMDP_REQUIRED_VERSION = "1.0.4" if sys.version_info < (3, 12) else "1.0.3"
CLAIM_BOUNDARY = "pymdp discrete active-inference loop; deterministic surrogate, not empirical or quantum-dynamical evidence"
LOG_CLAIM_BOUNDARY = (
    "structured pymdp runtime diagnostics over finite software traces; not empirical data, "
    "not a neural measurement, not practice-efficacy evidence, and not quantum-dynamical evidence"
)


def _shannon_entropy(distribution: Any) -> float:
    """Return the natural-log Shannon entropy of a probability vector (0 for a point mass)."""
    probabilities = np.asarray(distribution, dtype=float).reshape(-1)
    nonzero = probabilities[probabilities > 0.0]
    return float(-np.sum(nonzero * np.log(nonzero))) if nonzero.size else 0.0


@dataclass(frozen=True)
class ProfileSpec:
    """Profile-specific active-inference generative-model parameters."""

    deployment: QRFDeployment
    model_id: str


def softmax_negative(values: np.ndarray) -> np.ndarray:
    """Return a normalized softmax over negative values for policy selection."""
    shifted = -values - np.max(-values)
    exp = np.exp(shifted)
    return exp / exp.sum()


def normalize_probability(values: np.ndarray) -> np.ndarray:
    """Normalize a nonnegative probability vector and fail on zero mass."""
    clipped = np.clip(values.astype(float), 0.0, None)
    total = float(clipped.sum())
    if total <= 0.0:
        raise ValueError("probability vector has no positive mass")
    return clipped / total


def profile_specs(channels: int | None = None) -> tuple[ProfileSpec, ...]:
    """Return the public finite QRF profile specifications."""
    deployments = default_deployments(channels)
    return tuple(ProfileSpec(deployment, deployment.name) for deployment in deployments)


def build_profile_generative_model(spec: ProfileSpec) -> dict[str, Any]:
    """Build explicit A/B/C/D arrays for one QRF profile."""
    declaration = load_model(spec.model_id)
    if declaration.backend != "pymdp" or declaration.model_id != spec.deployment.name:
        raise ValueError("profile does not bind an admitted categorical GNN model")
    return {
        "profile": spec.deployment.name,
        **{key: np.asarray(declaration.tensors[key], dtype=float) for key in ("A", "B", "C", "D")},
        "state_labels": STATE_LABELS,
        "observation_labels": OBSERVATION_LABELS,
        "action_labels": ACTION_LABELS,
    }


def expected_free_energy_values(model: dict[str, Any], posterior: np.ndarray) -> np.ndarray:
    """Compute finite expected-free-energy surrogates for every action."""
    return np.asarray([row["efe_proxy"] for row in expected_free_energy_terms(model, posterior)], dtype=float)


def expected_free_energy_terms(model: dict[str, Any], posterior: np.ndarray) -> list[dict[str, float | str]]:
    """Return risk/ambiguity/expected-free-energy terms for each action."""
    terms = []
    A = model["A"]
    B = model["B"]
    C = model["C"]
    for action_index, action_label in enumerate(ACTION_LABELS):
        predicted_state = B[:, :, action_index] @ posterior
        predicted_obs = A @ predicted_state
        preference_alignment = float(C @ predicted_obs)
        ambiguity = float(
            sum(
                predicted_state[state_index]
                * (-(A[:, state_index] * np.log(np.clip(A[:, state_index], 1e-12, 1.0))).sum())
                for state_index in range(A.shape[1])
            )
        )
        terms.append(
            {
                "action": action_label,
                "risk_proxy": float(-preference_alignment),
                "ambiguity_proxy": ambiguity,
                "efe_proxy": float(ambiguity - preference_alignment),
            }
        )
    return terms


def _agent_from_model(model: dict[str, Any]) -> Agent:
    """Construct the pinned pymdp Agent from one explicit A/B/C/D model."""
    from jax import numpy as jnp
    from pymdp.agent import Agent

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return Agent(
            A=[jnp.asarray(model["A"])],
            B=[jnp.asarray(model["B"])],
            C=[jnp.asarray(model["C"])],
            D=[jnp.asarray(model["D"])],
            batch_size=1,
        )


def _array_payload(array: np.ndarray) -> dict[str, Any]:
    """Serialize an array with shape and rounded values for audit JSON."""
    return {
        "shape": list(array.shape),
        "values": np.round(array.astype(float), 6).tolist(),
    }


def _model_hash(model: dict[str, Any]) -> str:
    """Hash rounded A/B/C/D arrays so model drift is visible in diagnostics."""
    payload = {
        key: np.round(np.asarray(model[key], dtype=float), 12).tolist()
        for key in ("A", "B", "C", "D")
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _package_version(name: str) -> str:
    """Return the installed package version or an explicit not-installed marker."""
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "not-installed"


def _term_residuals(saved_terms: list[dict[str, Any]], computed_terms: list[dict[str, Any]]) -> dict[str, float]:
    """Compute maximum saved-vs-recomputed residuals for EFE term fields."""
    residuals: dict[str, float] = {}
    for key in ("risk_proxy", "ambiguity_proxy", "efe_proxy"):
        residuals[key] = float(
            max(
                abs(float(saved[key]) - float(computed[key]))
                for saved, computed in zip(saved_terms, computed_terms, strict=True)
            )
        )
    return residuals


def build_generative_model_audit(*, channels: int | None = None) -> dict[str, Any]:
    """Audit profile-specific A/B/C/D arrays and their normalization."""
    rows = []
    for spec in profile_specs(channels):
        model = build_profile_generative_model(spec)
        A = model["A"]
        B = model["B"]
        C = model["C"]
        D = model["D"]
        rows.append(
            {
                "profile": model["profile"],
                "deployment": spec.deployment.as_dict(),
                "A": _array_payload(A),
                "B": _array_payload(B),
                "C": _array_payload(C),
                "D": _array_payload(D),
                "A_column_sums": np.round(A.sum(axis=0), 8).tolist(),
                "B_column_sums_by_action": np.round(B.sum(axis=0), 8).tolist(),
                "D_sum": float(D.sum()),
                "A_normalized": bool(np.allclose(A.sum(axis=0), 1.0)),
                "B_normalized": bool(np.allclose(B.sum(axis=0), 1.0)),
                "D_normalized": bool(np.isclose(D.sum(), 1.0)),
            }
        )
    return {
        "schema": "realizing_emptiness.pymdp_generative_model_audit.v1",
        "profile_count": len(rows),
        "state_labels": list(STATE_LABELS),
        "observation_labels": list(OBSERVATION_LABELS),
        "action_labels": list(ACTION_LABELS),
        "rows": rows,
        "all_models_normalized": all(row["A_normalized"] and row["B_normalized"] and row["D_normalized"] for row in rows),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _extract_state_posterior(qs: list[Any]) -> np.ndarray:
    """Flatten the latest pymdp state posterior into a one-dimensional vector."""
    values = np.asarray(qs[0], dtype=float)
    return values.reshape(-1, values.shape[-1])[-1]


def _simulate_profile(spec: ProfileSpec, *, steps: int, seed: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run one deterministic profile trace and summarize its action choices."""
    from jax import numpy as jnp

    model = build_profile_generative_model(spec)
    agent = _agent_from_model(model)
    prior = agent.D
    hidden_state = int(np.argmax(model["D"]))
    profile_rows: list[dict[str, Any]] = []
    weighted_efe_values: list[float] = []
    vfe_values: list[float] = []
    action_counts = {action: 0 for action in ACTION_LABELS}
    design = model_parameters("qrf_boundary")
    for step in range(steps):
        base_observation = int(np.argmax(model["A"][:, hidden_state]))
        perturb = (step + seed + int(design["access_perturbation_scale"] * spec.deployment.metacognitive_access)) % design["perturbation_period"] == 0
        observation = int((base_observation + 1) % len(OBSERVATION_LABELS)) if perturb else base_observation
        qs, info = agent.infer_states([jnp.asarray([observation])], empirical_prior=prior, return_info=True)
        posterior = _extract_state_posterior(qs)
        q_pi, neg_efe = agent.infer_policies(qs)
        sampled = agent.sample_action(q_pi)
        action_index = int(np.asarray(sampled).reshape(-1)[0])
        action_label = ACTION_LABELS[action_index]
        action_counts[action_label] += 1
        q_pi_values = np.asarray(q_pi, dtype=float).reshape(-1)
        neg_efe_values = np.asarray(neg_efe, dtype=float).reshape(-1)
        efe_values = -neg_efe_values
        weighted_efe = float(q_pi_values @ efe_values)
        weighted_efe_values.append(weighted_efe)
        vfe = float(np.asarray(info.get("vfe", np.array([0.0])), dtype=float).reshape(-1)[-1])
        vfe_values.append(vfe)
        terms = expected_free_energy_terms(model, posterior)
        profile_rows.append(
            {
                "profile": spec.deployment.name,
                "step": step,
                "true_state": STATE_LABELS[hidden_state],
                "observation": observation,
                "observation_label": OBSERVATION_LABELS[observation],
                "perturbed_observation": bool(perturb),
                "state_posterior": np.round(posterior, 8).tolist(),
                "state_posterior_sum": float(posterior.sum()),
                "policy_posterior": np.round(q_pi_values, 8).tolist(),
                "policy_posterior_sum": float(q_pi_values.sum()),
                "negative_expected_free_energy": np.round(neg_efe_values, 8).tolist(),
                "expected_free_energy": np.round(efe_values, 8).tolist(),
                "weighted_expected_free_energy": weighted_efe,
                "vfe": vfe,
                "selected_action": action_label,
                "selected_action_index": action_index,
                "efe_terms": terms,
            }
        )
        transition = model["B"][:, :, action_index]
        next_prior = transition @ posterior
        next_prior = next_prior / next_prior.sum()
        prior = [jnp.asarray(next_prior[None, :])]
        hidden_state = int(np.argmax(transition[:, hidden_state]))
    summary = {
        "profile": spec.deployment.name,
        "deployment": spec.deployment.as_dict(),
        "mean_weighted_expected_free_energy": float(np.mean(weighted_efe_values)),
        "mean_vfe": float(np.mean(vfe_values)),
        "action_counts": action_counts,
        "final_state_posterior": profile_rows[-1]["state_posterior"],
        "final_policy_posterior": profile_rows[-1]["policy_posterior"],
        "posterior_normalized_all_steps": all(abs(row["state_posterior_sum"] - 1.0) < 1e-5 and abs(row["policy_posterior_sum"] - 1.0) < 1e-5 for row in profile_rows),
        "profile_energy": float(np.mean(weighted_efe_values) + design["energy_precision_weight"] * np.log1p(spec.deployment.prior_precision) - design["energy_flexibility_weight"] * spec.deployment.flexibility),
    }
    return profile_rows, summary


def _runtime_arguments(seed: int | None, steps: int | None, channels: int | None) -> tuple[int, int, int]:
    cfg = model_parameters("qrf_boundary")
    return (cfg["seed"] if seed is None else seed, cfg["trace_steps"] if steps is None else steps, cfg["channels"] if channels is None else channels)


def run_policy_trace(*, seed: int | None = None, steps: int | None = None, channels: int | None = None) -> dict[str, Any]:
    """Run a deterministic multi-profile pymdp policy trace."""
    seed, steps, channels = _runtime_arguments(seed, steps, channels)
    rows: list[dict[str, Any]] = []
    summaries = []
    for spec in profile_specs(channels):
        profile_rows, summary = _simulate_profile(spec, steps=steps, seed=seed)
        rows.extend(profile_rows)
        summaries.append(summary)
    return {
        "schema": "realizing_emptiness.pymdp_policy_trace.v1",
        "seed": seed,
        "steps": steps,
        "channels": channels,
        "state_labels": list(STATE_LABELS),
        "observation_labels": list(OBSERVATION_LABELS),
        "action_labels": list(ACTION_LABELS),
        "rows": rows,
        "profile_summaries": summaries,
        "row_count": len(rows),
        "all_posteriors_normalized": all(summary["posterior_normalized_all_steps"] for summary in summaries),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def runtime_warnings_match_version(check: dict[str, Any]) -> bool:
    messages = check.get("warnings")
    expected_count = {"1.0.3": 1, "1.0.4": 0}.get(check.get("version"))
    return (isinstance(messages, list) and all(isinstance(message, str) for message in messages)
            and expected_count is not None and len(messages) == expected_count)


def pymdp_runtime_dependency_check(required_version: str = PYMDP_REQUIRED_VERSION) -> dict[str, Any]:
    """Verify the pinned pymdp runtime surface without asserting model validity."""
    from jax import numpy as jnp
    from pymdp.agent import Agent

    version = importlib.metadata.version("inferactively-pymdp")
    ok_version = version == required_version
    model = build_profile_generative_model(profile_specs()[0])
    with warnings.catch_warnings(record=True) as captured_warnings:
        warnings.simplefilter("always")
        agent = Agent(A=[jnp.asarray(model["A"])], B=[jnp.asarray(model["B"])], C=[jnp.asarray(model["C"])], D=[jnp.asarray(model["D"])], batch_size=1)
    observation = [jnp.array([0])]
    qs, info = agent.infer_states(observation, empirical_prior=agent.D, return_info=True)
    q_pi, neg_efe = agent.infer_policies(qs)
    posterior_sum = float(jnp.sum(q_pi))
    return {
        "schema": "realizing_emptiness.pymdp_runtime_dependency_check.v1",
        "required_version": required_version,
        "version": version,
        "version_ok": ok_version,
        "agent_class": type(agent).__name__,
        "state_factor_count": len(qs),
        "policy_posterior_sum": posterior_sum,
        "policy_posterior_normalized": abs(posterior_sum - 1.0) < 1e-5,
        "neg_efe_shape": list(np.asarray(neg_efe).shape),
        "vfe_available": "vfe" in info,
        "warnings": [str(warning.message) for warning in captured_warnings],
        "ok": bool(ok_version and abs(posterior_sum - 1.0) < 1e-5),
    }


def run_profile_comparison(*, seed: int | None = None, steps: int | None = None, channels: int | None = None) -> dict[str, Any]:
    """Compare QRF profiles using a deterministic pymdp policy trace."""
    seed, steps, channels = _runtime_arguments(seed, steps, channels)
    policy_trace = run_policy_trace(seed=seed, steps=steps, channels=channels)
    model_audit = build_generative_model_audit(channels=channels)
    summaries = policy_trace["profile_summaries"]
    energies = np.array([row["profile_energy"] for row in summaries], dtype=float)
    posterior = softmax_negative(energies)
    rows = []
    for index, summary in enumerate(summaries):
        rows.append(
            {
                "deployment": summary["deployment"],
                "prediction_error": float(max(0.0, summary["mean_vfe"])),
                "complexity": float(model_parameters("qrf_boundary")["energy_precision_weight"] * np.log1p(summary["deployment"]["prior_precision"])),
                "accuracy": float(-summary["mean_weighted_expected_free_energy"]),
                "free_energy": float(summary["profile_energy"]),
                "flexibility": summary["deployment"]["flexibility"],
                "compassion_scope": float(len(set(summary["deployment"]["sector_labels"]) - {"self"}) / len(set(summary["deployment"]["sector_labels"]))),
                "posterior_mass": float(posterior[index]),
                "mean_weighted_expected_free_energy": summary["mean_weighted_expected_free_energy"],
                "mean_vfe": summary["mean_vfe"],
                "action_counts": summary["action_counts"],
                "final_state_posterior": summary["final_state_posterior"],
                "final_policy_posterior": summary["final_policy_posterior"],
                "posterior_normalized_all_steps": summary["posterior_normalized_all_steps"],
            }
        )
    best_row = min(rows, key=lambda row: row["free_energy"])
    return {
        "schema": "realizing_emptiness.pymdp_profile_comparison.v3",
        "seed": seed,
        "steps": steps,
        "channels": channels,
        "state_labels": list(STATE_LABELS),
        "observation_labels": list(OBSERVATION_LABELS),
        "action_labels": list(ACTION_LABELS),
        "trajectory": simulate_boundary_trajectory(seed=seed, steps=steps, screen=BoundaryScreen.default(channels)),
        "rows": rows,
        "policy_trace_summary": summaries,
        "generative_model_summary": {
            "profile_count": model_audit["profile_count"],
            "all_models_normalized": model_audit["all_models_normalized"],
        },
        "posterior_sum": float(sum(row["posterior_mass"] for row in rows)),
        "posterior_normalized": abs(sum(row["posterior_mass"] for row in rows) - 1.0) < 1e-9,
        "policy_trace_all_posteriors_normalized": policy_trace["all_posteriors_normalized"],
        "best_profile": best_row["deployment"]["name"],
        "runtime_dependency_check": pymdp_runtime_dependency_check(),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_pymdp_runtime_diagnostics_log(*, seed: int | None = None, steps: int | None = None, channels: int | None = None) -> dict[str, Any]:
    """Build the four-layer runtime/model/trace/replay diagnostics log."""
    seed, steps, channels = _runtime_arguments(seed, steps, channels)
    policy_trace = run_policy_trace(seed=seed, steps=steps, channels=channels)
    replay_trace = run_policy_trace(seed=seed, steps=steps, channels=channels)
    model_audit = build_generative_model_audit(channels=channels)
    models = {
        spec.deployment.name: build_profile_generative_model(spec)
        for spec in profile_specs(channels)
    }
    runtime_check = pymdp_runtime_dependency_check()
    model_hash_rows = [
        {
            "profile": profile_name,
            "sha256": _model_hash(model),
            "array_shapes": {
                key: list(np.asarray(model[key]).shape)
                for key in ("A", "B", "C", "D")
            },
        }
        for profile_name, model in models.items()
    ]
    diagnostic_rows = []
    for row in policy_trace["rows"]:
        model = models[row["profile"]]
        posterior = np.asarray(row["state_posterior"], dtype=float)
        policy_posterior = np.asarray(row["policy_posterior"], dtype=float)
        expected_free_energy = np.asarray(row["expected_free_energy"], dtype=float)
        computed_terms = expected_free_energy_terms(model, posterior)
        term_residuals = _term_residuals(row["efe_terms"], computed_terms)
        weighted_efe_recomputed = float(policy_posterior @ expected_free_energy)
        selected_action_index = int(row["selected_action_index"])
        diagnostic_rows.append(
            {
                "profile": row["profile"],
                "step": int(row["step"]),
                "true_state": row["true_state"],
                "observation_label": row["observation_label"],
                "selected_action": row["selected_action"],
                "selected_action_index": selected_action_index,
                "perturbed_observation": bool(row["perturbed_observation"]),
                "state_posterior_norm_residual": float(abs(float(row["state_posterior_sum"]) - 1.0)),
                "policy_posterior_norm_residual": float(abs(float(row["policy_posterior_sum"]) - 1.0)),
                "weighted_expected_free_energy_recomputed": weighted_efe_recomputed,
                "weighted_expected_free_energy_residual": float(
                    abs(weighted_efe_recomputed - float(row["weighted_expected_free_energy"]))
                ),
                "efe_term_residuals": term_residuals,
                "max_efe_term_residual": float(max(term_residuals.values())),
                "trace_labels_resolve": bool(
                    row["true_state"] in STATE_LABELS
                    and row["observation_label"] in OBSERVATION_LABELS
                    and row["selected_action"] in ACTION_LABELS
                ),
                "selected_action_index_matches": bool(ACTION_LABELS[selected_action_index] == row["selected_action"]),
                "posteriors_finite": bool(np.isfinite(posterior).all() and np.isfinite(policy_posterior).all()),
                "expected_free_energy_finite": bool(np.isfinite(expected_free_energy).all()),
                "vfe": float(row["vfe"]),
                "vfe_finite": bool(np.isfinite(float(row["vfe"]))),
                "state_posterior_entropy": _shannon_entropy(posterior),
                "policy_posterior_entropy": _shannon_entropy(policy_posterior),
                "entropies_in_bounds": bool(
                    -1e-9 <= _shannon_entropy(posterior) <= math.log(len(posterior)) + 1e-9
                    and -1e-9 <= _shannon_entropy(policy_posterior) <= math.log(len(policy_posterior)) + 1e-9
                ),
            }
        )
    max_state_residual = max(row["state_posterior_norm_residual"] for row in diagnostic_rows)
    max_policy_residual = max(row["policy_posterior_norm_residual"] for row in diagnostic_rows)
    max_weighted_efe_residual = max(row["weighted_expected_free_energy_residual"] for row in diagnostic_rows)
    max_efe_term_residual = max(row["max_efe_term_residual"] for row in diagnostic_rows)

    # Bind the manual temporal-prior step (B @ posterior) to the real library method, so the
    # numpy-transparent shortcut used in the trace cannot silently diverge from pymdp's own
    # update_empirical_prior convention. This also exercises a real pymdp 1.0.3 method.
    from jax import numpy as jnp

    empirical_prior_binding = []
    for spec in profile_specs(channels):
        model = models[spec.deployment.name]
        agent = _agent_from_model(model)
        observation = int(np.argmax(model["A"][:, int(np.argmax(model["D"]))]))
        qs, _ = agent.infer_states([jnp.asarray([observation])], empirical_prior=agent.D, return_info=True)
        posterior = _extract_state_posterior(qs)
        q_pi, _ = agent.infer_policies(qs)
        sampled = agent.sample_action(q_pi)
        action_index = int(np.asarray(sampled).reshape(-1)[0])
        manual_prior = model["B"][:, :, action_index] @ posterior
        manual_prior = manual_prior / manual_prior.sum()
        library_prior = np.asarray(agent.update_empirical_prior(sampled, qs)[0], dtype=float).reshape(-1)
        empirical_prior_binding.append(
            {
                "profile": spec.deployment.name,
                "action_index": action_index,
                "manual_vs_library_prior_residual": float(np.max(np.abs(library_prior - manual_prior))),
            }
        )
    max_empirical_prior_residual = max(
        row["manual_vs_library_prior_residual"] for row in empirical_prior_binding
    )

    replay = {
        "same_seed": seed,
        "row_count": len(policy_trace["rows"]),
        "trace_rows_equal": policy_trace["rows"] == replay_trace["rows"],
        "profile_summaries_equal": policy_trace["profile_summaries"] == replay_trace["profile_summaries"],
    }
    controls = {
        "runtime_dependency_ok": runtime_check.get("ok") is True,
        "runtime_warnings_captured": runtime_warnings_match_version(runtime_check),
        "all_model_hashes_present": all(row["sha256"] for row in model_hash_rows),
        "all_models_normalized": model_audit.get("all_models_normalized") is True,
        "deterministic_replay_equal": replay["trace_rows_equal"] and replay["profile_summaries_equal"],
        "all_state_posteriors_normalized": max_state_residual < 1e-5,
        "all_policy_posteriors_normalized": max_policy_residual < 1e-5,
        "weighted_expected_free_energy_recomputed": max_weighted_efe_residual < 1e-7,
        "efe_terms_rederived": max_efe_term_residual < 1e-7,
        "all_trace_labels_resolve": all(row["trace_labels_resolve"] for row in diagnostic_rows),
        "all_selected_action_indices_match": all(row["selected_action_index_matches"] for row in diagnostic_rows),
        "all_numeric_fields_finite": all(
            row["posteriors_finite"] and row["expected_free_energy_finite"]
            for row in diagnostic_rows
        ),
        "perturbation_flags_present": any(row["perturbed_observation"] for row in diagnostic_rows),
        "all_vfe_finite": all(row["vfe_finite"] for row in diagnostic_rows),
        "all_entropies_in_bounds": all(row["entropies_in_bounds"] for row in diagnostic_rows),
        "empirical_prior_matches_library": bool(max_empirical_prior_residual < 1e-5),
    }
    return {
        "schema": "realizing_emptiness.pymdp_runtime_diagnostics_log.v2",
        "seed": seed,
        "steps": steps,
        "channels": channels,
        "runtime_versions": {
            "python": platform.python_version(),
            "inferactively_pymdp": _package_version("inferactively-pymdp"),
            "jax": _package_version("jax"),
            "jaxlib": _package_version("jaxlib"),
            "numpy": _package_version("numpy"),
            "scipy": _package_version("scipy"),
        },
        "runtime_dependency_check": runtime_check,
        "model_hashes": model_hash_rows,
        "model_profile_count": len(model_hash_rows),
        "trace_row_count": len(diagnostic_rows),
        "profile_count": len(policy_trace["profile_summaries"]),
        "state_labels": list(STATE_LABELS),
        "observation_labels": list(OBSERVATION_LABELS),
        "action_labels": list(ACTION_LABELS),
        "rows": diagnostic_rows,
        "summary": {
            "max_state_posterior_norm_residual": max_state_residual,
            "max_policy_posterior_norm_residual": max_policy_residual,
            "max_weighted_expected_free_energy_residual": max_weighted_efe_residual,
            "max_efe_term_residual": max_efe_term_residual,
            "mean_vfe": float(np.mean([row["vfe"] for row in diagnostic_rows])),
            "max_vfe": float(max(row["vfe"] for row in diagnostic_rows)),
            "max_state_posterior_entropy": float(max(row["state_posterior_entropy"] for row in diagnostic_rows)),
            "max_policy_posterior_entropy": float(max(row["policy_posterior_entropy"] for row in diagnostic_rows)),
            "max_empirical_prior_library_residual": max_empirical_prior_residual,
            "perturbed_step_count": sum(1 for row in diagnostic_rows if row["perturbed_observation"]),
        },
        "empirical_prior_binding": empirical_prior_binding,
        "replay": replay,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": LOG_CLAIM_BOUNDARY,
    }
