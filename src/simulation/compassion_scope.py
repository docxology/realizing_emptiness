"""Finite scope-of-concern surrogate for the paper's compassion section (6.2).

The paper argues that under an enforced separation prior, variational-free-energy
minimisation is preferentially scoped to the self partition of the boundary, and
that lifting the prior extends concern toward all *influenceable* channels. This
module operationalises that claim as a finite, measured *scope-of-modelling*
quantity over the same b0-b5 boundary screen.

Concern per channel genuinely BLENDS two finite drivers:

* the **realised action-influence** of the shared bitstream — measured per channel as
  the reduction in prediction error when the selected action is conditioned on — so a
  channel the agent can actually move earns more concern; and
* the **separation prior's precision allocation** — extra precision on the self partition
  scaled by the lack of metacognitive access.

The claim-bearing negative control for the self/non-self ASYMMETRY is PRECISION ABLATION
rather than a label shuffle: a size-preserving label shuffle cannot falsify a quantity
whose self/non-self split is driven by partition size and prior precision. The
action-influence term carries its own discriminating controls: it is zero when the stream
has no action-contingency, it tracks the per-channel controllability, and it collapses
under an ACTION SHUFFLE that breaks the (observation, action) pairing.

INTEGRITY: ``scope_asymmetry`` is a finite policy-scope number, NOT a measure of
compassion, well-being, practice efficacy, or any affective, moral, or clinical outcome.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from formalism.models import QRFDeployment


COMPASSION_CLAIM_BOUNDARY = (
    "finite policy-scope-of-modelling surrogate; not a measure of compassion, well-being, "
    "practice efficacy, or any affective, moral, or clinical outcome"
)

# Channels whose sector label places them inside the self partition B_self.
SELF_SECTORS = frozenset({"self", "body"})

# Per-channel action-contingency (controllability) for b0-b5, faithful to the
# boundary-channel ledger roles: b0 (body-controllability) and b1 (action-contingency)
# cues are strongly action-driven; b2 (distal-world) is least action-contingent; b3
# (contextual-world), b4 (other-agent), and b5 (care-salience) sit between. A channel's
# realised influence is MEASURED from the finite stream below, not read from this vector;
# the vector only parameterises how strongly each channel tracks the action.
CHANNEL_CONTROLLABILITY: tuple[float, ...] = (0.95, 0.90, 0.10, 0.35, 0.55, 0.75)


def compassion_boundary_stream(
    controllability: tuple[float, ...] = CHANNEL_CONTROLLABILITY,
    *,
    seed: int = 7,
    steps: int = 96,
) -> list[dict[str, Any]]:
    """Return a finite boundary stream with heterogeneous per-channel action-contingency.

    At each step a binary action is drawn; channel ``c`` copies ``action XOR bias[c]`` with
    probability ``controllability[c]`` and otherwise follows an action-independent seeded
    process. A channel with controllability near 1 is therefore (almost) a deterministic
    function of the action, and a channel with controllability 0 is action-independent. The
    stream is fully deterministic given ``seed``.
    """
    rng = np.random.default_rng(seed)
    channels = len(controllability)
    bias = rng.integers(0, 2, size=channels)
    env_state = rng.integers(0, 2, size=channels)
    trajectory: list[dict[str, Any]] = []
    for step in range(steps):
        action = int(rng.integers(0, 2))
        observation = np.empty(channels, dtype=int)
        for channel in range(channels):
            if rng.random() < controllability[channel]:
                observation[channel] = int(action) ^ int(bias[channel])
            else:
                env_state[channel] = env_state[channel] ^ int(rng.integers(0, 2))
                observation[channel] = int(env_state[channel])
        trajectory.append(
            {
                "step": step,
                "action": action,
                "observation": observation.astype(int).tolist(),
            }
        )
    return trajectory


def channel_influence(trajectory: list[dict[str, Any]]) -> np.ndarray:
    """Return a per-channel realised action-influence score in [0, 1].

    For each channel the action-conditioned predictor predicts the per-channel mean
    observation given the selected action value; influence is the reduction in mean squared
    prediction error relative to the unconditional (action-blind) baseline mean, expressed
    as a fraction of that baseline error. A channel whose bits are a deterministic function
    of the action gets influence near 1; an action-independent channel gets influence near 0.

    The score is a property of the (observation, action) PAIRING: permuting the actions
    relative to the observations (the action-shuffle control) destroys the conditioning gain
    and drives every channel's influence to ~0.
    """
    observations = np.array([row["observation"] for row in trajectory], dtype=float)
    actions = np.array([row["action"] for row in trajectory], dtype=float)
    baseline = observations.mean(axis=0, keepdims=True)
    baseline_error = np.mean((observations - baseline) ** 2, axis=0)
    prediction = np.empty_like(observations)
    for value in np.unique(actions):
        mask = actions == value
        prediction[mask] = observations[mask].mean(axis=0)
    action_error = np.mean((observations - prediction) ** 2, axis=0)
    reduction = np.maximum(0.0, baseline_error - action_error)
    # Normalise by an ABSOLUTE scale (the largest baseline error), not by the reduction's own
    # peak: peak-normalisation would amplify a shuffled stream's residual noise back up to 1
    # and hide the collapse. Absolute scaling keeps an action-independent stream near 0.
    scale = float(baseline_error.max())
    return reduction / scale if scale > 1e-12 else np.zeros_like(reduction)


def _precision_weights(
    deployment: QRFDeployment, sector_labels: tuple[str, ...], *, ablate: bool = False
) -> np.ndarray:
    """Return per-channel concern precision under the separation prior.

    Channels inside the self partition receive extra precision proportional to the prior
    precision scaled by the *lack* of metacognitive access, so an enforced, low-access
    separation prior privileges self-prediction while a high-access, low-precision post-dual
    deployment equalises concern. With ``ablate=True`` the self boost is removed, leaving the
    partition-size-only baseline used by the negative control.
    """
    self_boost = 0.0 if ablate else deployment.prior_precision * (1.0 - deployment.metacognitive_access)
    return np.array(
        [1.0 + self_boost if label in SELF_SECTORS else 1.0 for label in sector_labels],
        dtype=float,
    )


def compute_scope_of_concern(
    deployment: QRFDeployment,
    trajectory: list[dict[str, Any]],
    *,
    sector_labels: tuple[str, ...] | None = None,
    influence: np.ndarray | None = None,
    ablate_prior: bool = False,
) -> dict[str, Any]:
    """Return the finite self/non-self concern split for one deployment.

    Concern per channel is ``(1 + influence) * precision_weight``: it blends the realised
    action-influence of the shared bitstream with the separation prior's precision allocation.
    Shares are taken over the MEAN per-channel concern of each partition, so ``scope_asymmetry`` =
    (non-self share) - (self share) is independent of how many channels each partition holds (the
    counts are disclosed separately). It is negative when per-channel concern concentrates on the
    self partition and rises toward and above zero as concern widens to non-self channels.
    """
    labels = tuple(sector_labels) if sector_labels is not None else deployment.sector_labels
    influence_vector = channel_influence(trajectory) if influence is None else np.asarray(influence, dtype=float)
    weights = _precision_weights(deployment, labels, ablate=ablate_prior)
    concern = (1.0 + influence_vector) * weights
    self_mask = np.array([label in SELF_SECTORS for label in labels], dtype=bool)
    # Per-channel MEAN concern, not partition sum: this makes scope_asymmetry independent of how
    # many channels each partition holds, so the widening reflects the separation prior's per-unit
    # precision allocation rather than the channel-count change across profiles (the count is
    # disclosed separately). A partition with no channels contributes zero mean concern.
    mean_self = float(concern[self_mask].mean()) if self_mask.any() else 0.0
    mean_env = float(concern[~self_mask].mean()) if (~self_mask).any() else 0.0
    total = mean_self + mean_env
    if total <= 0.0:
        self_share = 0.0 if not self_mask.any() else (1.0 if not (~self_mask).any() else 0.5)
        env_share = 1.0 - self_share
    else:
        self_share = mean_self / total
        env_share = mean_env / total
    return {
        "deployment": deployment.name,
        "self_channel_count": int(self_mask.sum()),
        "non_self_channel_count": int((~self_mask).sum()),
        "mean_self_channel_concern": mean_self,
        "mean_non_self_channel_concern": mean_env,
        "self_concern_share": self_share,
        "non_self_concern_share": env_share,
        "scope_asymmetry": float(env_share - self_share),
        "prior_ablated": bool(ablate_prior),
    }


def _is_monotone_increasing(values: list[float], *, tolerance: float = 1e-9) -> bool:
    return all(b >= a - tolerance for a, b in zip(values, values[1:]))


def build_compassion_scope_audit(
    deployments: tuple[QRFDeployment, ...],
    *,
    controllability: tuple[float, ...] = CHANNEL_CONTROLLABILITY,
    seed: int = 19,
    steps: int = 96,
    action_shuffle_count: int = 32,
) -> dict[str, Any]:
    """Audit scope-of-concern widening across profiles, with separable controls for the two
    drivers of concern: the separation prior (precision) and the realised action-influence.

    Real profiles are expected to show monotonically widening ``scope_asymmetry``. The ASYMMETRY's
    primary negative control ablates the separation prior's self-precision boost: this must raise
    the most-constrained profile's asymmetry (collapse its self-concentration) and shrink the
    overall spread, isolating sigma as the cause. The ACTION-INFLUENCE term carries its own
    discriminating controls: it is non-zero and tracks per-channel controllability, it collapses to
    ~0 on an action-independent stream, and it collapses under an action shuffle that breaks the
    (observation, action) pairing — and removing it (influence-free concern) measurably changes the
    scope, which is what makes the blend genuinely active rather than decorative.
    """
    stream = compassion_boundary_stream(controllability, seed=seed, steps=steps)
    influence = channel_influence(stream)
    rows = [compute_scope_of_concern(d, stream, influence=influence) for d in deployments]
    ablated_rows = [
        compute_scope_of_concern(d, stream, influence=influence, ablate_prior=True) for d in deployments
    ]
    real_asym = [row["scope_asymmetry"] for row in rows]
    ablated_asym = [row["scope_asymmetry"] for row in ablated_rows]
    real_spread = float(max(real_asym) - min(real_asym))
    ablated_spread = float(max(ablated_asym) - min(ablated_asym))

    # The most self-concentrated profile is the one with the lowest real asymmetry.
    constrained_index = int(np.argmin(real_asym))
    ablation_lift = float(ablated_asym[constrained_index] - real_asym[constrained_index])

    # Influence-free scope (concern = precision weight only): isolates the prior's contribution
    # so that "the action-influence term changes the scope" is a measured A/B, not an assertion.
    zero_influence = np.zeros(len(influence))
    influence_free_asym = [
        compute_scope_of_concern(d, stream, influence=zero_influence)["scope_asymmetry"] for d in deployments
    ]
    influence_free_spread = float(max(influence_free_asym) - min(influence_free_asym))
    influence_scope_shift = float(
        max(abs(r - f) for r, f in zip(real_asym, influence_free_asym))
    )

    mean_real_influence = float(influence.mean())

    # Discriminating positive control: realised influence must track per-channel controllability
    # (the most-controllable channel earns more influence than the least-controllable one).
    most_controllable = int(np.argmax(controllability))
    least_controllable = int(np.argmin(controllability))
    influence_tracks_controllability = bool(
        influence[most_controllable] > influence[least_controllable] + 0.1
    )

    # Discriminating negative control: a stream with zero controllability has no action structure,
    # so a correct estimator must return ~0 influence (a green-by-construction estimator would not).
    null_stream = compassion_boundary_stream(tuple(0.0 for _ in controllability), seed=seed, steps=steps)
    null_mean_influence = float(channel_influence(null_stream).mean())

    # Action-shuffle control: permute the actions relative to the observations, destroying the
    # realised influence. Mean influence must collapse well below the real mean.
    rng = np.random.default_rng(seed)
    shuffled_means: list[float] = []
    for _ in range(action_shuffle_count):
        permuted_actions = rng.permutation([row["action"] for row in stream])
        shuffled = [
            {**row, "action": int(permuted_actions[index])} for index, row in enumerate(stream)
        ]
        shuffled_means.append(float(channel_influence(shuffled).mean()))
    mean_action_shuffled_influence = float(np.mean(shuffled_means)) if shuffled_means else 0.0

    # Positive control (dose-response) paired with a negative control. Holding the sectorisation and
    # access fixed, raising the separation-prior precision must DEEPEN the self-concentration by a
    # real margin, while the SAME sweep with the self-precision boost ablated must stay flat. (A bare
    # "non-increasing" check would be vacuous: self_boost is non-decreasing in prior_precision, so the
    # curve is algebraically non-increasing for every valid input and could never fail.)
    base = deployments[0]
    dose_precisions = (0.0, 1.0, 2.0, 4.0, 8.0)
    dose_asymmetries = [
        compute_scope_of_concern(
            QRFDeployment(f"dose_{p}", base.sector_labels, base.metacognitive_access, p),
            stream,
            influence=influence,
        )["scope_asymmetry"]
        for p in dose_precisions
    ]
    dose_ablated_asymmetries = [
        compute_scope_of_concern(
            QRFDeployment(f"dose_{p}", base.sector_labels, base.metacognitive_access, p),
            stream,
            influence=influence,
            ablate_prior=True,
        )["scope_asymmetry"]
        for p in dose_precisions
    ]
    dose_deepens = bool(dose_asymmetries[-1] < dose_asymmetries[0] - 0.05)
    dose_flat_without_boost = bool(max(dose_ablated_asymmetries) - min(dose_ablated_asymmetries) < 1e-9)

    controls = {
        "real_widening_monotone": _is_monotone_increasing(real_asym),
        "prior_precision_drives_self_scoping": bool(ablation_lift > 0.05),
        "widening_amplified_by_prior": bool(real_spread > ablated_spread + 1e-9),
        "dose_response_deepens_self_concentration": bool(dose_deepens and dose_flat_without_boost),
        # Action-influence is genuinely active, measured, and falsifiable:
        "action_influence_active": bool(mean_real_influence > 0.05),
        "influence_tracks_controllability": influence_tracks_controllability,
        "zero_controllability_gives_zero_influence": bool(null_mean_influence < 0.05),
        "action_shuffle_collapses_influence": bool(
            mean_action_shuffled_influence < 0.5 * mean_real_influence
        ),
        "influence_shapes_scope": bool(influence_scope_shift > 1e-3),
    }
    return {
        "schema": "realizing_emptiness.compassion_scope_audit.v1",
        "label": "finite_policy_scope_surrogate_not_compassion_measure",
        "deployment_count": len(rows),
        "rows": rows,
        "ablated_rows": ablated_rows,
        "real_scope_asymmetries": real_asym,
        "ablated_scope_asymmetries": ablated_asym,
        "influence_free_scope_asymmetries": influence_free_asym,
        "real_widening_monotone": _is_monotone_increasing(real_asym),
        "real_spread": real_spread,
        "ablated_spread": ablated_spread,
        "influence_free_spread": influence_free_spread,
        "influence_scope_shift": influence_scope_shift,
        "constrained_profile": rows[constrained_index]["deployment"],
        "ablation_lift": ablation_lift,
        "channel_controllability": list(controllability),
        "channel_influence": influence.tolist(),
        "mean_action_influence": mean_real_influence,
        "null_stream_mean_influence": null_mean_influence,
        "mean_action_shuffled_influence": mean_action_shuffled_influence,
        "dose_response_precisions": list(dose_precisions),
        "dose_response_asymmetries": dose_asymmetries,
        "dose_response_ablated_asymmetries": dose_ablated_asymmetries,
        "controls": controls,
        "all_controls_pass": all(controls.values()),
        "claim_boundary": COMPASSION_CLAIM_BOUNDARY,
    }
