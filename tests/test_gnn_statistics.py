from __future__ import annotations

import shutil

import pytest

from modeling.registry import model_parameters, specification_root
from simulation.criticality import (
    branching_estimator_calibration,
    build_criticality_stochastic_ensemble,
)
from simulation.statistical_robustness import (
    _synthetic_arm,
    build_bmr_robustness_resampling_audit,
    build_effect_size_test_calibration_audit,
    build_quantum_trajectory_convergence_audit,
    build_seed_bank_calibration,
    build_stochastic_effect_size_audit,
)
from simulation.stochastic import build_stochastic_policy_ensemble


@pytest.fixture
def specifications(pytestconfig, tmp_path):
    source = pytestconfig.realizing_emptiness_root / "src/modeling/specifications"
    destination = tmp_path / "specifications"
    shutil.copytree(source, destination)
    return destination


def change_parameters(root, model_id, **changes):
    path = root / f"{model_id}.gnn.md"
    content = path.read_text(encoding="utf-8")
    with specification_root(root):
        original = model_parameters(model_id)
    changed = {**original, **changes}
    assert repr(original) in content
    path.write_text(content.replace(repr(original), repr(changed), 1), encoding="utf-8")


@pytest.fixture(scope="module")
def policy():
    return build_stochastic_policy_ensemble(seed=771, runs=8, steps=12)


def test_gnn_policy_defaults_and_explicit_overrides(specifications):
    explicit = build_stochastic_policy_ensemble(seed=771, runs=8, steps=12, channels=6)
    change_parameters(specifications, "statistical_policy_ensemble", seed=772, runs=4, steps=10, channels=6)
    with specification_root(specifications):
        changed = build_stochastic_policy_ensemble()
        replay = build_stochastic_policy_ensemble()
        override = build_stochastic_policy_ensemble(seed=771, runs=8, steps=12, channels=6)
    assert changed == replay
    assert (changed["seed"], changed["runs_per_profile"], changed["steps"]) == (772, 4, 10)
    assert changed["row_count"] == changed["profile_count"] * 4 * 10 * 2
    assert changed["profile_summaries"] != explicit["profile_summaries"]
    assert override == explicit


def test_gnn_resampling_design_changes_measured_intervals(specifications, policy):
    baseline = build_stochastic_effect_size_audit(policy)
    change_parameters(specifications, "statistical_effects", bootstrap_seed=1, bootstrap_draws=31,
                      permutation_seed=2, permutation_draws=31)
    with specification_root(specifications):
        changed = build_stochastic_effect_size_audit(policy)
    assert all(row["bootstrap_draws"] == 31 and row["permutation_draws"] == 31 for row in changed["rows"])
    assert any(left["difference_ci95_low"] != right["difference_ci95_low"]
               for left, right in zip(baseline["rows"], changed["rows"], strict=True))
    assert any(left["permutation_p"] != right["permutation_p"]
               for left, right in zip(baseline["rows"], changed["rows"], strict=True))


def test_gnn_bmr_design_changes_resampled_interval(specifications):
    sensitivity = {"rows": [
        {"prior_precision": 1.0, "metacognitive_access": 0.5,
         "delta_free_energy": value, "prunes_prior": value > 0}
        for value in (-3.0, -1.0, 0.5, 1.0, 5.0)
    ]}
    baseline = build_bmr_robustness_resampling_audit(sensitivity)
    change_parameters(specifications, "statistical_bmr", delta_seed=2, pruning_seed=3, bootstrap_draws=7)
    with specification_root(specifications):
        changed = build_bmr_robustness_resampling_audit(sensitivity)
    assert changed["rows"][0]["delta_ci95_low"] != baseline["rows"][0]["delta_ci95_low"]


def test_gnn_convergence_sweep_and_explicit_overrides(specifications):
    baseline = build_quantum_trajectory_convergence_audit(seed=29, trajectory_counts=(16, 32), too_few_count=8)
    change_parameters(specifications, "statistical_convergence", seed=30, trajectory_counts=[16, 64], too_few_count=4)
    with specification_root(specifications):
        changed = build_quantum_trajectory_convergence_audit()
        override = build_quantum_trajectory_convergence_audit(seed=29, trajectory_counts=(16, 32), too_few_count=8)
    assert changed["trajectory_counts"] == [16, 64]
    assert changed["too_few_count"] == 4
    assert changed["rows"][0]["max_trace_distance_to_exact"] != baseline["rows"][0]["max_trace_distance_to_exact"]
    assert override == baseline


def test_gnn_synthetic_effect_removal_flips_measured_verdict(specifications):
    baseline = build_effect_size_test_calibration_audit()
    assert baseline["all_controls_pass"] is True
    change_parameters(specifications, "statistical_calibration", positive_shift=0.0)
    with specification_root(specifications):
        changed = build_effect_size_test_calibration_audit()
        override = build_effect_size_test_calibration_audit(seed=4242, positive_shift=1.0)
    assert changed["positive_arm"]["mean_difference"] != baseline["positive_arm"]["mean_difference"]
    assert changed["controls"]["positive_effect_rejected"] is False
    assert changed["all_controls_pass"] is False
    assert override == baseline


def test_gnn_normal_generator_scale_changes_effect_estimate(specifications):
    baseline = _synthetic_arm(shift=1.0, seed=4242, sample_size=32)
    change_parameters(specifications, "statistical_calibration", normal_scale=2.0)
    with specification_root(specifications):
        changed = _synthetic_arm(shift=1.0, seed=4242, sample_size=32, base_seed_offset=3)
    assert changed["mean_difference"] != baseline["mean_difference"]
    assert changed["cliffs_delta"] != baseline["cliffs_delta"]


def test_gnn_seed_bank_effect_removal_flips_measured_verdict(specifications):
    baseline = build_seed_bank_calibration(seed=104242, repetitions=32, positive_shift=1.0)
    assert baseline["controls"]["injected_effect_detected"] is True
    change_parameters(specifications, "statistical_seed_bank", positive_shift=0.0, repetitions=32)
    with specification_root(specifications):
        changed = build_seed_bank_calibration()
        override = build_seed_bank_calibration(seed=104242, repetitions=32, positive_shift=1.0)
    assert changed["positive_rejection"]["rate"] < baseline["positive_rejection"]["rate"]
    assert changed["controls"]["injected_effect_detected"] is False
    assert override == baseline


def test_gnn_criticality_design_changes_real_shuffle_and_intervals(specifications, policy):
    baseline = build_criticality_stochastic_ensemble(policy)
    change_parameters(specifications, "statistical_criticality", shuffle_seed_offset=92,
                      bootstrap_seed_offset=93000, bootstrap_draws=31)
    with specification_root(specifications):
        changed = build_criticality_stochastic_ensemble(policy)
    assert changed["branching_null_seed"] == policy["seed"] + 92
    assert any(left["branching_ratio"] != right["branching_ratio"]
               for left, right in zip(baseline["metric_rows"], changed["metric_rows"], strict=True)
               if left["null_control"])
    assert all(row["paired_bootstrap_draws"] == 31 for row in changed["null_contrasts"])
    assert any(left["paired_branching_ci95_low"] != right["paired_branching_ci95_low"]
               for left, right in zip(baseline["null_contrasts"], changed["null_contrasts"], strict=True))


def test_gnn_planted_generator_collapse_fails_independent_calibration(specifications):
    baseline = branching_estimator_calibration()
    assert baseline["branching_estimator_recovers_planted_sigma"] is True
    change_parameters(specifications, "statistical_criticality", calibration_start=0.0)
    with specification_root(specifications):
        changed = branching_estimator_calibration()
    assert set(changed["recovered_branching_ratios"].values()) == {0.0}
    assert changed["branching_estimator_recovers_planted_sigma"] is False
    assert changed["branching_ordering_preserved"] is False
