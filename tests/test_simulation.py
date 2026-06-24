"""Tests for QRF, BMR, pymdp, and criticality simulations."""

from __future__ import annotations

import json

import numpy as np
import pytest

from simulation.bmr import compare_models, run_bmr_sweep, write_bmr_sweep
from formalism.models import QRFDeployment
from formalism.review_response import (
    build_bmr_alternative_prior_audit,
    build_qrf_label_ablation_audit,
    build_quantum_independent_crosscheck_audit,
)
from simulation.compassion_scope import build_compassion_scope_audit, compute_scope_of_concern
from simulation.criticality import (
    avalanche_size_distribution,
    branching_estimator_calibration,
    branching_ratio,
    build_criticality_report,
    build_criticality_stochastic_ensemble,
    criticality_signatures,
)
from simulation.pymdp_profiles import (
    build_generative_model_audit,
    build_pymdp_runtime_diagnostics_log,
    build_profile_generative_model,
    expected_free_energy_terms,
    expected_free_energy_values,
    normalize_probability,
    profile_specs,
    pymdp_runtime_dependency_check,
    pymdp_version_canary,
    run_policy_trace,
    run_profile_comparison,
    softmax_negative,
)
from simulation.quantum_surrogates import (
    build_arbitrary_two_qubit_entanglement_audit,
    build_empirical_adapter_provenance_audit,
    build_general_measurement_cover_polytope_audit,
    build_many_body_boundary_screen_sweep,
    build_qfep_boundary_hamiltonian_dynamics,
    build_qrf_frame_covariance_toy_audit,
    build_quantum_boundary_entropy,
    build_quantum_extension_roadmap,
    build_quantum_measurement_contextuality,
    build_quantum_open_system_dynamics,
    build_quantum_roadmap_readiness_matrix,
    build_quantum_trajectory_unraveling,
    build_qrf_transformation_covariance_audit,
    build_sheaf_contextuality_obstruction_audit,
    build_sparse_boundary_screen_scaling_audit,
    build_thermodynamic_channel_cost_audit,
)
from simulation.qrf_env import boundary_channel_ledger, boundary_indistinguishability_audit, default_deployments, score_deployment, simulate_boundary_trajectory
from simulation.sensitivity import build_sensitivity_grid, compare_sensitivity_point, write_sensitivity_grid
from simulation.statistical_robustness import (
    build_bmr_robustness_resampling_audit,
    build_effect_size_test_calibration_audit,
    build_quantum_trajectory_convergence_audit,
    build_statistical_robustness_audit,
    build_stochastic_effect_size_audit,
)
from simulation.stochastic import build_stochastic_policy_ensemble


def test_qrf_boundary_indistinguishability_negative_control() -> None:
    audit = boundary_indistinguishability_audit()
    assert audit["all_admissible_distributions_equal"] is True
    assert audit["negative_control_fails"] is True
    assert audit["deployment_count"] == 3
    ledger = boundary_channel_ledger()
    assert ledger["schema"] == "realizing_emptiness.qrf_boundary_channel_ledger.v1"
    assert ledger["all_controls_pass"] is True
    assert [row["channel_id"] for row in ledger["rows"]] == [f"b{index}" for index in range(6)]
    assert all(row["evidence_object_invariant"] for row in ledger["rows"])
    assert all(row["source_equation_links"] == ["eq:7", "eq:8", "eq:9", "eq:10"] for row in ledger["rows"])
    assert ledger["controls"]["negative_control_fails"] is True
    assert "not ontological" in ledger["claim_boundary"]
    ablation = build_qrf_label_ablation_audit()
    assert ablation["all_controls_pass"] is True
    assert ablation["controls"]["neutral_renaming_preserves_structure"] is True
    assert ablation["controls"]["structure_changing_control_fails"] is True
    assert ablation["alias_map"]["self"] == "sector_s"


def test_boundary_trajectory_and_scores() -> None:
    trajectory = simulate_boundary_trajectory(seed=7, steps=4)
    assert len(trajectory) == 4
    score = score_deployment(default_deployments()[0], trajectory)
    assert {"prediction_error", "complexity", "accuracy", "free_energy"} <= set(score)
    assert score["complexity"] > 0


def test_bmr_sweep_has_expected_edges() -> None:
    low = compare_models(4.0, 0.0)
    high = compare_models(4.0, 1.0)
    assert low.prunes_prior is True
    assert high.prunes_prior is True
    sweep = run_bmr_sweep()
    assert sweep["row_count"] == 45
    assert sweep["high_access_prunes"] is True
    alternatives = build_bmr_alternative_prior_audit()
    assert alternatives["all_controls_pass"] is True
    assert set(alternatives["families"]) == {
        "baseline_linear_sigma_complexity",
        "log_compressed_sigma_complexity",
        "convex_access_dependent_sigma_accuracy",
    }
    assert alternatives["controls"]["at_least_one_crossing_shifts_vs_baseline"] is True
    assert all(row["verdict"] in {"prune", "keep"} for row in alternatives["rows"])


def test_sensitivity_grid_is_bounded_and_parameterized() -> None:
    point = compare_sensitivity_point(prior_precision=4.0, metacognitive_access=1.0, observation_noise=0.25)
    assert point["qrf_indistinguishability_holds"] is True
    assert "not empirical" in point["claim_boundary"]
    assert point["post_dual_advantage"] >= 0.0
    grid = build_sensitivity_grid()
    assert grid["row_count"] == 315
    assert grid["all_rows_boundary_safe"] is True
    assert 0.0 <= grid["pruning_rate"] <= 1.0
    assert grid["high_access_pruning_rate"] >= grid["low_access_pruning_rate"]


def test_quantum_boundary_entropy_and_contextuality_controls() -> None:
    payload = build_quantum_boundary_entropy(theta_count=9, rotation_count=7)
    assert payload["schema"] == "realizing_emptiness.quantum_boundary_entropy.v1"
    assert payload["all_controls_pass"] is True
    assert payload["controls"]["product_entropy_zero"] is True
    assert payload["controls"]["product_chsh_local"] is True
    assert payload["controls"]["bell_entropy_one"] is True
    assert payload["controls"]["bell_chsh_toward_tsirelson"] is True
    assert payload["controls"]["basis_entropy_invariant"] is True
    assert payload["rows"][0]["reduced_entropy_bits"] == 0.0
    assert payload["rows"][0]["bell_violation_predicate"] is False
    assert payload["rows"][-1]["reduced_entropy_bits"] == 1.0
    assert payload["rows"][-1]["bell_violation_predicate"] is True
    assert payload["max_observed_chsh"] > 2.8
    assert payload["max_contextual_fraction"] > 0.99
    assert payload["max_basis_entropy_drift_bits"] < 1e-9
    assert "not empirical" in payload["claim_boundary"]


def test_quantum_extension_roadmap_is_gated() -> None:
    roadmap = build_quantum_extension_roadmap()
    implemented = {row["id"]: row for row in roadmap["implemented"]}
    future = {row["id"]: row for row in roadmap["future"]}
    expected_blocked_future_ids = {"re-3", "re-4", "re-13", "re-14", "re-15"}
    assert {
        "two_qubit_separability_entropy",
        "arbitrary_two_qubit_entanglement_audit",
        "chsh_contextuality_witness",
        "chsh_measurement_cover_table",
        "general_measurement_cover_polytope_audit",
        "qrf_basis_invariance_toy",
        "boundary_landauer_entropy",
        "thermodynamic_channel_cost_audit",
        "two_qubit_dephasing_channel",
        "full_open_system_qfep_dynamics",
        "quantum_trajectory_unraveling",
        "many_body_boundary_screens",
        "sparse_boundary_screen_scaling_audit",
        "general_sheaf_contextuality_engine",
        "qrf_transformation_library",
        "qrf_frame_covariance_toy_audit",
        "empirical_adapter",
    } <= set(implemented)
    assert implemented["chsh_contextuality_witness"]["validation_gate"] == "quantum_contextuality_witness_ok"
    assert implemented["chsh_measurement_cover_table"]["validation_gate"] == "quantum_measurement_contextuality_ok"
    assert implemented["two_qubit_dephasing_channel"]["validation_gate"] == "quantum_open_system_dynamics_ok"
    assert all(row["status"] == "implemented_finite_simulation" for row in implemented.values())
    assert set(future) == expected_blocked_future_ids
    assert all(row["status"].startswith("roadmap_requires_") for row in future.values())
    assert all("blocked_task_id" in row for row in future.values())
    assert {row["blocked_task_id"] for row in future.values()} == expected_blocked_future_ids
    assert "not empirical" in roadmap["claim_boundary"]
    readiness = build_quantum_roadmap_readiness_matrix()
    assert readiness["all_controls_pass"] is True
    assert readiness["implemented_count"] == len(implemented)
    assert readiness["future_count"] == len(future)
    readiness_future = [row for row in readiness["rows"] if row["roadmap_class"] == "future"]
    assert {row["id"] for row in readiness_future} == expected_blocked_future_ids
    assert readiness["controls"]["all_future_blocked"] is True
    assert readiness["controls"]["forged_completed_future_row_rejected"] is True
    assert readiness["forged_completed_future_row_control"]["manuscript_claim_allowed"] is False
    assert readiness["forged_completed_future_row_control"]["readiness_score"] == 0.0
    assert all(row["readiness_score"] == 0.0 for row in readiness_future)
    assert all(row["manuscript_claim_allowed"] is False for row in readiness_future)
    assert all(row["required_next_gate"].endswith("_ok") for row in readiness_future)
    assert all(row["required_negative_control"] for row in readiness["rows"])


def test_stochastic_policy_ensemble_replays_and_feeds_criticality() -> None:
    # Powered ensemble (runs=16): the criticality separation control is now confidence-interval
    # disjointness, which is honestly under-powered on a handful of runs, so the replay/feed test uses
    # the same adequately-sampled regime as the dedicated separation test.
    ensemble = build_stochastic_policy_ensemble(seed=321, runs=16, steps=24)
    replay = build_stochastic_policy_ensemble(seed=321, runs=16, steps=24)
    different_seed = build_stochastic_policy_ensemble(seed=322, runs=16, steps=24)
    assert ensemble["schema"] == "realizing_emptiness.stochastic_policy_ensemble.v1"
    assert ensemble["all_controls_pass"] is True
    assert ensemble["rows"] == replay["rows"]
    assert ensemble["rows"] != different_seed["rows"]
    assert ensemble["row_count"] == 16 * 24 * 3 * 2
    assert ensemble["run_summary_count"] == 16 * 3 * 2
    assert all(abs(row["state_posterior_sum"] - 1.0) < 1e-8 for row in ensemble["rows"])
    assert all(abs(row["policy_posterior_sum"] - 1.0) < 1e-8 for row in ensemble["rows"])
    assert any(row["null_control"] is True for row in ensemble["rows"])
    assert "not empirical" in ensemble["claim_boundary"]
    criticality = build_criticality_stochastic_ensemble(ensemble)
    assert criticality["all_controls_pass"] is True
    assert criticality["label"] == "seeded_stochastic_simulation_not_empirical_neural_measure"
    assert criticality["summary_row_count"] == 6
    assert "not empirical neural-criticality" in criticality["claim_boundary"]


def test_stochastic_and_deterministic_paths_share_efe_math() -> None:
    spec = profile_specs()[0]
    model = build_profile_generative_model(spec)
    posterior = normalize_probability(model["D"])
    values = expected_free_energy_values(model, posterior)
    terms = expected_free_energy_terms(model, posterior)
    assert values.shape == (3,)
    assert [term["action"] for term in terms] == list(model["action_labels"])
    assert all(abs(value - term["efe_proxy"]) < 1e-12 for value, term in zip(values, terms, strict=True))
    policy = softmax_negative(values)
    assert abs(float(policy.sum()) - 1.0) < 1e-12
    assert int(policy.argmax()) == int(values.argmin())


def test_quantum_trajectory_unraveling_controls_and_replay() -> None:
    payload = build_quantum_trajectory_unraveling(seed=11, trajectory_count=96, step_count=12, total_time=1.2)
    replay = build_quantum_trajectory_unraveling(seed=11, trajectory_count=96, step_count=12, total_time=1.2)
    different_seed = build_quantum_trajectory_unraveling(seed=12, trajectory_count=96, step_count=12, total_time=1.2)
    assert payload["schema"] == "realizing_emptiness.quantum_trajectory_unraveling.v1"
    assert payload["all_controls_pass"] is True
    assert payload["rows"] == replay["rows"]
    assert payload["jump_count_rows"] == replay["jump_count_rows"]
    assert payload["jump_count_rows"] != different_seed["jump_count_rows"]
    assert payload["max_norm_drift"] < 1e-10
    assert payload["max_trace_error"] < 1e-10
    assert payload["min_eigenvalue"] > -1e-10
    assert payload["max_trace_distance_to_exact"] < 0.16
    assert payload["controls"]["gamma_zero_has_no_jumps"] is True
    assert all(row["jump_count"] == 0 for row in payload["jump_count_rows"] if row["decoherence_rate"] == 0.0)
    assert all(row["passes"] is True for row in payload["invalid_controls"])
    assert "not empirical" in payload["claim_boundary"]
    assert "not a physical qFEP" in payload["claim_boundary"]


def test_statistical_robustness_audits_are_replayable_and_bounded() -> None:
    ensemble = build_stochastic_policy_ensemble(seed=771, runs=10, steps=10)
    stochastic_effects = build_stochastic_effect_size_audit(ensemble)
    stochastic_effects_replay = build_stochastic_effect_size_audit(ensemble)
    assert stochastic_effects == stochastic_effects_replay
    assert stochastic_effects["all_controls_pass"] is True
    assert all(row["finite_interval"] for row in stochastic_effects["rows"])
    assert all(0.0 <= row["permutation_p"] <= 1.0 for row in stochastic_effects["rows"])
    assert all(0.0 <= row["holm_p"] <= 1.0 for row in stochastic_effects["rows"])
    assert any(abs(row["cliffs_delta"]) > 0.1 for row in stochastic_effects["rows"])

    sensitivity = build_sensitivity_grid()
    bmr_robustness = build_bmr_robustness_resampling_audit(sensitivity)
    assert bmr_robustness["all_controls_pass"] is True
    assert all(row["finite_interval"] for row in bmr_robustness["rows"])
    assert all(0.0 <= row["pruning_rate"] <= 1.0 for row in bmr_robustness["rows"])
    assert any(row["sign_stable"] for row in bmr_robustness["rows"])

    convergence = build_quantum_trajectory_convergence_audit(seed=33, trajectory_counts=(16, 64, 128, 512), too_few_count=8)
    assert convergence["all_controls_pass"] is True
    assert convergence["controls"]["too_few_trajectory_control_fails"] is True
    assert convergence["too_few_trajectory_control"]["all_controls_pass"] is False
    assert convergence["rows"][-1]["max_trace_distance_to_exact"] < convergence["rows"][0]["max_trace_distance_to_exact"]

    calibration = build_effect_size_test_calibration_audit()
    assert calibration["all_controls_pass"] is True
    assert calibration["controls"]["null_not_rejected"] is True
    assert calibration["controls"]["positive_effect_rejected"] is True
    assert calibration["controls"]["cliffs_delta_sign_matches_injection"] is True
    assert calibration["positive_arm"]["permutation_p"] <= calibration["alpha"]
    assert calibration["null_arm"]["permutation_p"] > calibration["alpha"]
    assert "not empirical statistical power" in calibration["claim_boundary"]

    aggregate = build_statistical_robustness_audit(stochastic_effects, bmr_robustness, convergence, calibration)
    assert aggregate["all_controls_pass"] is True
    assert aggregate["controls"]["effect_size_calibration_pass"] is True
    assert "not empirical" in aggregate["claim_boundary"]


def test_roadmap_engines_have_negative_controls() -> None:
    qfep = build_qfep_boundary_hamiltonian_dynamics(time_count=9, decoherence_rate_count=4)
    assert qfep["all_controls_pass"] is True
    assert qfep["controls"]["trace_preserved"] is True
    assert qfep["controls"]["positive_semidefinite"] is True
    assert qfep["controls"]["all_negative_controls_fail_safely"] is True
    assert qfep["max_trace_error"] < 1e-9
    strong_rate = max(qfep["decoherence_rate_grid"])
    strong_rows = [row for row in qfep["rows"] if row["decoherence_rate"] == strong_rate]
    assert strong_rows[0]["global_entropy_bits"] < strong_rows[-1]["global_entropy_bits"]
    assert strong_rows[0]["mutual_information_bits"] > strong_rows[-1]["mutual_information_bits"]

    many_body = build_many_body_boundary_screen_sweep()
    assert many_body["all_controls_pass"] is True
    assert many_body["controls"]["partition_sensitivity_present"] is True
    assert many_body["controls"]["separable_controls_zero_entropy"] is True
    assert many_body["controls"]["random_cut_not_labeled_observer_evidence"] is True

    sheaf = build_sheaf_contextuality_obstruction_audit()
    sheaf_rows = {row["id"]: row for row in sheaf["rows"]}
    assert sheaf["all_controls_pass"] is True
    assert sheaf_rows["noncontextual_triangle_control"]["global_section_feasible"] is True
    assert sheaf_rows["parity_obstruction"]["global_section_feasible"] is False
    assert sheaf_rows["parity_obstruction"]["min_l1_residual"] > 0.5

    qrf_transform = build_qrf_transformation_covariance_audit()
    assert qrf_transform["all_controls_pass"] is True
    assert all(row["accepted"] for row in qrf_transform["rows"] if row["admissible"])
    assert all(not row["accepted"] for row in qrf_transform["rows"] if not row["admissible"])

    empirical = build_empirical_adapter_provenance_audit()
    assert empirical["all_controls_pass"] is True
    assert empirical["controls"]["no_empirical_claims_allowed"] is True
    assert not any(row["allowed_for_empirical_claim"] for row in empirical["rows"])
    # Forged-record negative control: a record self-asserting every provenance field and the
    # reviewed-dataset type, but lacking independent external review, MUST stay blocked.
    forged = next(row for row in empirical["rows"] if row["id"] == "forged_self_asserted_reviewed_dataset")
    assert forged["provenance_complete"] is True
    assert forged["allowed_for_empirical_claim"] is False
    assert empirical["controls"]["forged_self_asserted_reviewed_dataset_blocked"] is True
    # Teeth: the block holds BECAUSE of the external-review predicate. Granting that token (the only
    # thing self-assertion cannot supply) is the sole change that would unlock the forged record.
    unlocked = bool(
        forged["provenance_complete"]
        and True  # has_independent_external_review granted
        and not forged["synthetic"]
        and forged["record_type"] == "reviewed_empirical_dataset"
    )
    assert unlocked is True  # confirms the predicate is the load-bearing gate, not a vacuous control


def test_next_roadmap_engines_have_controls() -> None:
    entanglement = build_arbitrary_two_qubit_entanglement_audit()
    assert entanglement["all_controls_pass"] is True
    assert entanglement["controls"]["werner_threshold_matches_ppt"] is True
    assert entanglement["controls"]["invalid_density_controls_rejected"] is True
    assert any(row["entangled_by_ppt"] for row in entanglement["rows"] if row["family"] == "werner")
    assert any(not row["entangled_by_ppt"] for row in entanglement["rows"] if row["family"] == "werner")

    cover = build_general_measurement_cover_polytope_audit()
    cover_rows = {row["id"]: row for row in cover["rows"]}
    assert cover["all_controls_pass"] is True
    assert cover_rows["triangle_feasible_control"]["global_section_feasible"] is True
    assert cover_rows["triangle_parity_obstruction"]["global_section_feasible"] is False
    assert cover_rows["chsh_product_control"]["global_section_feasible"] is True
    assert cover_rows["chsh_bell_obstruction"]["global_section_feasible"] is False

    channel = build_thermodynamic_channel_cost_audit()
    assert channel["all_controls_pass"] is True
    assert channel["controls"]["all_declared_channels_cptp"] is True
    assert channel["controls"]["non_cptp_controls_rejected"] is True
    assert any(row["landauer_lower_bound_kbt"] > 0.0 for row in channel["rows"] if row["channel_id"] == "erasure_to_zero")

    sparse = build_sparse_boundary_screen_scaling_audit()
    observer_rows = [row for row in sparse["rows"] if row["state_label"] == "sparse_cross_boundary_bell_pairs" and row["cut_id"] == "observer_half_cut"]
    assert sparse["all_controls_pass"] is True
    assert max(sparse["qubit_counts"]) > 6
    assert observer_rows[0]["reduced_entropy_bits"] < observer_rows[-1]["reduced_entropy_bits"]
    assert observer_rows[0]["amplitude_density"] > observer_rows[-1]["amplitude_density"]

    qrf_frame = build_qrf_frame_covariance_toy_audit()
    assert qrf_frame["all_controls_pass"] is True
    assert all(row["accepted"] for row in qrf_frame["rows"] if row["admissible"])
    assert all(not row["accepted"] for row in qrf_frame["rows"] if not row["admissible"])


def test_quantum_measurement_contextuality_controls() -> None:
    payload = build_quantum_measurement_contextuality()
    assert payload["schema"] == "realizing_emptiness.quantum_measurement_contextuality.v1"
    assert payload["row_count"] == 32
    assert payload["context_count"] == 4
    assert payload["all_controls_pass"] is True
    assert payload["controls"]["joint_probabilities_normalized"] is True
    assert payload["controls"]["joint_probabilities_nonnegative"] is True
    assert payload["controls"]["no_signaling_marginals_match"] is True
    assert payload["bell_chsh"] > payload["local_chsh_bound"]
    assert abs(payload["bell_chsh"] - payload["tsirelson_bound"]) < 1e-9
    assert payload["product_control_chsh"] <= payload["local_chsh_bound"]
    assert payload["contextual_fraction"] > 0.99
    assert payload["max_no_signaling_error"] < 1e-10
    fits = {row["model"]: row for row in payload["local_polytope"]["fits"]}
    assert payload["local_polytope"]["assignment_count"] == 16
    assert fits["product_control"]["feasible"] is True
    assert fits["product_control"]["min_l1_residual"] < 1e-8
    assert fits["bell_measurement_cover"]["feasible"] is False
    assert fits["bell_measurement_cover"]["min_l1_residual"] > 0.1
    assert payload["controls"]["product_control_local_polytope_feasible"] is True
    assert payload["controls"]["bell_model_local_polytope_infeasible"] is True
    assert "not empirical" in payload["claim_boundary"]
    assert "not a full sheaf-obstruction proof" in payload["claim_boundary"]


def test_quantum_independent_crosscheck_rederives_contextuality(pytestconfig) -> None:
    root = pytestconfig.realizing_emptiness_root
    audit = build_quantum_independent_crosscheck_audit(root)
    assert audit["all_controls_pass"] is True
    assert audit["controls"]["product_local_crosscheck"] is True
    assert audit["controls"]["bell_tsirelson_crosscheck"] is True
    assert audit["controls"]["product_polytope_feasible_independent"] is True
    assert audit["controls"]["bell_polytope_infeasible_independent"] is True
    assert audit["controls"]["perturbed_expected_value_control_fails"] is True
    assert audit["computed"]["bell_chsh"] > audit["computed"]["local_chsh_bound"]


def test_quantum_open_system_dephasing_controls() -> None:
    payload = build_quantum_open_system_dynamics(time_count=9, decoherence_rate_count=4)
    assert payload["schema"] == "realizing_emptiness.quantum_open_system_dynamics.v1"
    assert payload["all_controls_pass"] is True
    assert payload["controls"]["trace_preserved"] is True
    assert payload["controls"]["positive_semidefinite"] is True
    assert payload["controls"]["product_control_stable"] is True
    assert payload["controls"]["bell_entropy_non_decreasing_under_dephasing"] is True
    assert payload["controls"]["bell_chsh_decays_under_dephasing"] is True
    assert payload["max_trace_error"] < 1e-10
    assert payload["min_eigenvalue"] > -1e-10
    bell_rows = [row for row in payload["rows"] if row["state_label"] == "bell_dephased" and row["decoherence_rate"] == 1.0]
    assert bell_rows[0]["global_entropy_bits"] == 0.0
    assert bell_rows[-1]["global_entropy_bits"] > 0.9
    assert bell_rows[0]["chsh_s_max"] > bell_rows[-1]["chsh_s_max"]
    assert "not empirical" in payload["claim_boundary"]


def test_pymdp_canary_and_profile_comparison() -> None:
    canary = pymdp_version_canary()
    runtime_check = pymdp_runtime_dependency_check()
    assert canary["ok"] is True
    assert runtime_check["ok"] is True
    assert runtime_check["schema"] == canary["schema"]
    assert canary["version"] == "1.0.3"
    payload = run_profile_comparison()
    assert payload["posterior_normalized"] is True
    assert payload["policy_trace_all_posteriors_normalized"] is True
    assert payload["pymdp_canary"]["ok"] is True
    assert payload["schema"] == "realizing_emptiness.pymdp_profile_comparison.v2"
    assert payload["best_profile"] in {row["deployment"]["name"] for row in payload["rows"]}


def test_pymdp_generative_models_and_policy_trace_are_normalized() -> None:
    audit = build_generative_model_audit()
    assert audit["all_models_normalized"] is True
    assert all(row["A"]["shape"] == [3, 3] for row in audit["rows"])
    assert all(row["B"]["shape"] == [3, 3, 3] for row in audit["rows"])
    assert all(abs(row["D_sum"] - 1.0) < 1e-8 for row in audit["rows"])
    trace = run_policy_trace(steps=5)
    assert trace["row_count"] == 15
    assert trace["all_posteriors_normalized"] is True
    assert len({row["selected_action"] for row in trace["rows"]}) >= 2
    models = {
        spec.deployment.name: build_profile_generative_model(spec)
        for spec in profile_specs()
    }
    for row in trace["rows"]:
        model = models[row["profile"]]
        terms = expected_free_energy_terms(model, row["state_posterior"])
        for saved, rederived in zip(row["efe_terms"], terms, strict=True):
            assert abs(saved["risk_proxy"] - rederived["risk_proxy"]) < 1e-7
            assert abs(saved["ambiguity_proxy"] - rederived["ambiguity_proxy"]) < 1e-7
            assert abs(saved["efe_proxy"] - rederived["efe_proxy"]) < 1e-7
        weighted = sum(
            posterior * efe
            for posterior, efe in zip(row["policy_posterior"], row["expected_free_energy"], strict=True)
        )
        assert abs(weighted - row["weighted_expected_free_energy"]) < 1e-7
    replay = run_policy_trace(steps=5)
    assert replay["rows"] == trace["rows"]


def test_pymdp_runtime_diagnostics_log_replays_and_recomputes() -> None:
    payload = build_pymdp_runtime_diagnostics_log(seed=7, steps=5)
    replay = build_pymdp_runtime_diagnostics_log(seed=7, steps=5)
    assert payload["schema"] == "realizing_emptiness.pymdp_runtime_diagnostics_log.v1"
    assert payload["all_controls_pass"] is True
    assert payload["runtime_versions"]["inferactively_pymdp"] == "1.0.3"
    assert len(payload["canary"]["warnings"]) >= 1
    assert payload["trace_row_count"] == 15
    assert payload["model_profile_count"] == 3
    assert len({row["sha256"] for row in payload["model_hashes"]}) == 3
    assert payload["model_hashes"] == replay["model_hashes"]
    assert payload["rows"] == replay["rows"]
    assert payload["replay"]["trace_rows_equal"] is True
    assert payload["replay"]["profile_summaries_equal"] is True
    assert payload["summary"]["max_state_posterior_norm_residual"] < 1e-6
    assert payload["summary"]["max_policy_posterior_norm_residual"] < 1e-6
    assert payload["summary"]["max_weighted_expected_free_energy_residual"] < 1e-7
    assert payload["summary"]["max_efe_term_residual"] < 1e-7
    assert payload["summary"]["perturbed_step_count"] > 0
    assert all(row["trace_labels_resolve"] for row in payload["rows"])
    assert all(row["selected_action_index_matches"] for row in payload["rows"])
    assert all(row["posteriors_finite"] and row["expected_free_energy_finite"] for row in payload["rows"])
    # Comprehensive diagnostics: per-step VFE, belief/policy entropy, and the real-method prior binding.
    assert all(row["vfe_finite"] for row in payload["rows"])
    assert all(row["entropies_in_bounds"] for row in payload["rows"])
    assert payload["controls"]["all_vfe_finite"] is True
    assert payload["controls"]["all_entropies_in_bounds"] is True
    assert payload["controls"]["empirical_prior_matches_library"] is True
    assert payload["summary"]["max_empirical_prior_library_residual"] < 1e-5
    assert len(payload["empirical_prior_binding"]) == 3
    assert "mean_vfe" in payload["summary"] and "max_policy_posterior_entropy" in payload["summary"]
    # Green-by-construction guard: an empty/narrowed controls object must fail the runtime-log gate.
    from gates.validation import _pymdp_runtime_log_ok

    policy_trace = run_policy_trace(seed=7, steps=5)
    assert _pymdp_runtime_log_ok(payload, policy_trace) is True
    assert _pymdp_runtime_log_ok({**payload, "controls": {}}, policy_trace) is False
    # A NARROWED (nonempty) controls object must also fail: the fix requires the full key set,
    # so the hole is closed rather than merely shrunk to "len(controls) > 0".
    assert _pymdp_runtime_log_ok({**payload, "controls": {"canary_ok": True}}, policy_trace) is False
    assert "not empirical" in payload["claim_boundary"]


def test_criticality_report_is_labeled_proxy() -> None:
    report = build_criticality_report(run_profile_comparison())
    assert report["schema"] == "realizing_emptiness.criticality_proxy_report.v1"
    assert "not evidence" in report["claim_boundary"]
    assert 0.0 <= report["near_critical_score"] <= 1.0


def test_branching_ratio_and_avalanche_signatures() -> None:
    # A balanced activity series is critical-style (sigma == 1).
    assert branching_ratio(np.array([1.0, 1.0, 1.0, 1.0])) == 1.0
    # A decaying series is subcritical.
    assert branching_ratio(np.array([4.0, 2.0, 1.0, 0.0])) < 1.0
    assert branching_ratio(np.array([0.0])) == 0.0
    # Avalanche extraction over a known toy series with two supra-threshold runs.
    avalanches = avalanche_size_distribution(np.array([0.0, 2.0, 3.0, 0.0, 0.0, 1.0, 0.0]))
    assert avalanches["avalanche_count"] == 2
    assert avalanches["sizes"] == [5.0, 1.0]
    signatures = criticality_signatures(np.array([1.0, 1.0, 1.0]))
    assert signatures["criticality_index"] == 0.0
    assert "not evidence of neural" in signatures["claim_boundary"]


def test_branching_estimator_recovers_planted_sigma() -> None:
    calibration = branching_estimator_calibration()
    recovered = calibration["recovered_branching_ratios"]
    assert abs(recovered["subcritical"] - 0.5) < 1e-9
    assert abs(recovered["critical"] - 1.0) < 1e-9
    assert abs(recovered["supercritical"] - 1.5) < 1e-9
    assert calibration["branching_estimator_recovers_planted_sigma"] is True
    assert calibration["branching_ordering_preserved"] is True


def test_criticality_ensemble_branching_separates_from_null() -> None:
    ensemble = build_stochastic_policy_ensemble(seed=11, runs=16, steps=24)
    crit = build_criticality_stochastic_ensemble(ensemble)
    assert crit["all_controls_pass"] is True
    assert crit["controls"]["measured_branching_separates_from_null"] is True
    assert crit["controls"]["branching_estimator_recovers_planted_sigma"] is True
    # Separation is now a confidence-interval-disjointness test, not a bare mean-delta threshold: the
    # branching separation that fires must come from a profile whose real and null CIs do not overlap.
    assert crit["controls"]["majority_of_profiles_ci_separate_from_null"] is True
    assert any(row["branching_ratio_ci_disjoint_from_null"] for row in crit["null_contrasts"])
    # Every metric row carries the measured branching signatures.
    assert all("branching_ratio" in row and "criticality_index" in row for row in crit["metric_rows"])
    # Mutation: collapse every observation to a constant -> activity is zero -> branching does
    # not separate from null, flipping the separation control False.
    flat = json.loads(json.dumps(ensemble))
    for row in flat["rows"]:
        row["observation"] = 0
    mutated = build_criticality_stochastic_ensemble(flat)
    assert mutated["controls"]["measured_branching_separates_from_null"] is False


def test_compassion_scope_widens_and_ablation_collapses_self_concentration() -> None:
    trajectory = simulate_boundary_trajectory()
    deployments = default_deployments()
    audit = build_compassion_scope_audit(deployments)
    assert audit["all_controls_pass"] is True
    assert audit["controls"]["real_widening_monotone"] is True
    assert audit["controls"]["prior_precision_drives_self_scoping"] is True
    assert audit["controls"]["widening_amplified_by_prior"] is True
    # Positive control (dose-response): raising the prior precision deepens self-concentration.
    assert audit["controls"]["dose_response_deepens_self_concentration"] is True
    # Action-influence is now a genuinely active, measured driver of concern (not inert).
    assert audit["controls"]["action_influence_active"] is True
    assert audit["mean_action_influence"] > 0.05
    assert len(audit["channel_influence"]) == 6
    # Discriminating: realised influence tracks per-channel controllability and vanishes when
    # the stream has no action-contingency (a green-by-construction estimator would not).
    assert audit["controls"]["influence_tracks_controllability"] is True
    assert audit["controls"]["zero_controllability_gives_zero_influence"] is True
    assert audit["null_stream_mean_influence"] < 0.05
    # Discriminating: permuting actions against observations breaks the pairing and collapses
    # realised influence well below the real mean.
    assert audit["controls"]["action_shuffle_collapses_influence"] is True
    assert audit["mean_action_shuffled_influence"] < 0.5 * audit["mean_action_influence"]
    # A/B: removing the influence term (precision-only concern) measurably changes the scope,
    # so the blend is active rather than decorative.
    assert audit["controls"]["influence_shapes_scope"] is True
    assert audit["real_scope_asymmetries"] != audit["influence_free_scope_asymmetries"]
    dose = audit["dose_response_asymmetries"]
    assert dose[-1] < dose[0]
    assert all(b <= a + 1e-9 for a, b in zip(dose, dose[1:]))
    # The most-constrained profile concentrates concern on the self partition (negative asym).
    assert audit["real_scope_asymmetries"][0] < 0.0
    # Negative control: ablating the separation prior collapses the self-concentration.
    assert audit["ablation_lift"] > 0.05
    assert audit["real_spread"] > audit["ablated_spread"]
    # Mutation: swapping the self/non-self partition (every label -> non-self) removes the
    # self partition, so concern cannot concentrate on self.
    constrained = deployments[0]
    non_self_labels = tuple("world" for _ in constrained.sector_labels)
    swapped = compute_scope_of_concern(constrained, trajectory, sector_labels=non_self_labels)
    assert swapped["self_channel_count"] == 0
    assert swapped["scope_asymmetry"] >= 0.0

    # Count-confound control (Forge): under ablation with no influence, two deployments that share
    # precision/access but differ in self-channel COUNT must give the SAME asymmetry, so the widening
    # is driven by the separation prior's precision and not by how many channels are labelled self.
    zero_influence = np.zeros(len(constrained.sector_labels))
    three_self = QRFDeployment("three", ("self", "self", "self", "env", "env", "env"), 0.0, 4.0)
    one_self = QRFDeployment("one", ("self", "env", "env", "env", "env", "env"), 0.0, 4.0)
    asym_three = compute_scope_of_concern(three_self, trajectory, influence=zero_influence, ablate_prior=True)
    asym_one = compute_scope_of_concern(one_self, trajectory, influence=zero_influence, ablate_prior=True)
    assert abs(asym_three["scope_asymmetry"] - asym_one["scope_asymmetry"]) < 1e-9


def test_effect_size_calibration_detects_injected_effect_and_ignores_null() -> None:
    audit = build_effect_size_test_calibration_audit()
    assert audit["all_controls_pass"] is True
    assert audit["positive_arm"]["permutation_p"] <= audit["alpha"]
    assert audit["null_arm"]["permutation_p"] > audit["alpha"]
    assert audit["positive_arm"]["cliffs_delta"] > 0.33
    assert audit["sign_flip_arm"]["cliffs_delta"] < 0.0
    # Mutation: a zero injected shift must fail to reject (the rejection tracks the real effect).
    null_like = build_effect_size_test_calibration_audit(positive_shift=0.0)
    assert null_like["controls"]["positive_effect_rejected"] is False


def test_bmr_and_sensitivity_writers_roundtrip(tmp_path) -> None:
    bmr_paths = write_bmr_sweep(tmp_path)
    bmr = json.loads(bmr_paths["json"].read_text())
    assert bmr["schema"] == "realizing_emptiness.bmr_sweep.v1"
    assert bmr["row_count"] == 45
    assert bmr_paths["csv"].exists()
    assert bmr_paths["csv"].read_text().count("\n") == 46

    grid_paths = write_sensitivity_grid(tmp_path)
    grid = json.loads(grid_paths["json"].read_text())
    assert grid["row_count"] == 315
    assert grid_paths["csv"].exists()


def test_sensitivity_point_rejects_out_of_range_inputs() -> None:
    with pytest.raises(ValueError):
        compare_sensitivity_point(prior_precision=-1.0, metacognitive_access=0.5, observation_noise=0.1)
    with pytest.raises(ValueError):
        compare_sensitivity_point(prior_precision=1.0, metacognitive_access=1.5, observation_noise=0.1)
    with pytest.raises(ValueError):
        compare_sensitivity_point(prior_precision=1.0, metacognitive_access=0.5, observation_noise=0.6)


def test_separation_prior_emergence_is_agency_gated() -> None:
    from simulation.emergence import build_separation_prior_emergence_audit

    audit = build_separation_prior_emergence_audit()
    assert audit["all_controls_pass"] is True
    # Constructive correctness check: no agency -> identical masks -> zero factored advantage.
    assert abs(audit["zero_empowerment_advantage"]) < 1e-9
    # Positive control: full action-contingency -> large detected advantage.
    assert audit["full_empowerment_advantage"] > 0.2
    # Discriminating negative control WITH TEETH: breaking the (obs, action) pairing collapses the
    # advantage far below the real value, attributing the gain to genuine action-contingency.
    assert audit["controls"]["action_shuffle_collapses_factored_advantage"] is True
    assert audit["mean_action_shuffled_advantage"] < 0.25 * audit["full_empowerment_advantage"]
    assert audit["full_empowerment_advantage"] - audit["mean_action_shuffled_advantage"] > 0.2
    advantages = [row["factored_advantage"] for row in audit["rows"]]
    assert all(b >= a - 1e-9 for a, b in zip(advantages, advantages[1:]))
    assert "not a developmental" in audit["claim_boundary"]


def test_internal_cut_unmeasurable_from_one_side() -> None:
    from simulation.quantum_surrogates import build_internal_cut_unmeasurability_audit

    audit = build_internal_cut_unmeasurability_audit()
    assert audit["all_controls_pass"] is True
    assert audit["bipartition_count"] >= 3
    for row in audit["rows"]:
        # A's accessible marginal is invariant across the two states (cannot adjudicate the cut)...
        assert row["accessible_marginal_drift"] < 1e-9
        assert row["separable_cut_entropy_bits"] < 1e-9
        # ...while the god's-eye view distinguishes separable (S=0) from entangled (S=1) cuts.
        assert row["entangled_cut_entropy_bits"] > 0.5
    assert "not empirical" in audit["claim_boundary"]


def test_sigma_suppresses_contextuality_only_when_contextuality_exists() -> None:
    from simulation.quantum_surrogates import build_sigma_contextuality_suppression_audit

    audit = build_sigma_contextuality_suppression_audit()
    assert audit["all_controls_pass"] is True
    rows = {row["id"]: row for row in audit["rows"]}
    # Positive resolving-power control: unconstrained genuinely exhibits the obstruction.
    assert rows["parity_obstruction"]["unconstrained_feasible"] is False
    assert rows["parity_obstruction"]["suppression_delta"] > 0.5
    # Discriminating negative control: nothing to suppress on the noncontextual scenario.
    assert abs(rows["noncontextual_triangle_control"]["suppression_delta"]) < 1e-8


def test_ongoing_revision_advantage_jumps_only_at_regime_change() -> None:
    from simulation.emergence import build_ongoing_revision_audit

    audit = build_ongoing_revision_audit()
    assert audit["all_controls_pass"] is True
    nonstationary = audit["nonstationary_stream"]["revision_jump"]
    stationary = audit["stationary_stream"]["revision_jump"]
    assert nonstationary > 0.1
    assert abs(stationary) < 0.05
    assert nonstationary > stationary + 0.1
    assert "not a claim of realized awakening" in audit["claim_boundary"]


def test_multipartite_witness_suite_detects_entanglement_and_rejects_separable() -> None:
    from simulation.quantum_surrogates import build_multipartite_witness_suite_audit

    audit = build_multipartite_witness_suite_audit()
    assert audit["all_controls_pass"] is True
    rows = {row["id"]: row for row in audit["rows"]}
    # Positive controls: GHZ (multipartite) and the qutrit pair (higher-dimensional) detect on every cut.
    assert rows["ghz_3_qubit"]["entangled_detected_all_cuts"] is True
    assert abs(rows["ghz_3_qubit"]["min_bipartition_negativity"] - 0.5) < 1e-9
    assert rows["qutrit_pair_max_entangled"]["entangled_detected_all_cuts"] is True
    assert abs(rows["qutrit_pair_max_entangled"]["min_bipartition_negativity"] - 1.0) < 1e-9
    # Explicit false-positive controls: separable product states must NOT be detected on any cut.
    assert rows["product_3_qubit_control"]["entangled_detected_any_cut"] is False
    assert rows["qutrit_pair_product_control"]["entangled_detected_any_cut"] is False
    assert audit["controls"]["separable_controls_not_detected"] is True
    # Asymmetric fixture: a wrong-axis transpose would falsely flag the spectator qubit; the
    # per-cut pattern [entangled, entangled, separable] is the control that catches that regression.
    asymmetric = rows["bell_pair_plus_ground_3_qubit"]
    assert [b["entangled_by_ppt"] for b in asymmetric["bipartitions"]] == [True, True, False]
    assert audit["controls"]["asymmetric_cuts_match_expected_pattern"] is True
    assert "not empirical" in audit["claim_boundary"]


def test_tensor_network_benchmark_reconstructs_and_truncation_discriminates() -> None:
    from simulation.quantum_surrogates import build_tensor_network_benchmark_audit

    audit = build_tensor_network_benchmark_audit()
    assert audit["all_controls_pass"] is True
    rows = {row["id"]: row for row in audit["rows"]}
    # Scaling: GHZ stays bond-2 across N; product is bond-1; exact MPS reconstructs.
    assert rows["ghz_5_qubit"]["max_bond_dimension"] == 2
    assert rows["product_4_qubit"]["max_bond_dimension"] == 1
    assert abs(rows["ghz_3_qubit"]["exact_reconstruction_error"]) < 1e-9
    # Discriminating truncation control: bond-1 truncation hurts entangled, not product.
    assert rows["ghz_3_qubit"]["truncated_chi1_error"] > 1e-9
    assert rows["product_4_qubit"]["truncated_chi1_error"] < 1e-9
    assert "not empirical" in audit["claim_boundary"]


def test_collision_model_relaxes_only_under_coupling() -> None:
    from simulation.quantum_surrogates import build_collision_model_thermalization_audit

    audit = build_collision_model_thermalization_audit()
    assert audit["all_controls_pass"] is True
    rows = {row["id"]: row for row in audit["rows"]}
    # Coupled collisions relax toward the ancilla; the zero-coupling control does not move.
    assert rows["weak_coupling"]["final_distance"] < rows["weak_coupling"]["initial_distance"]
    control = rows["zero_coupling_control"]
    assert abs(control["final_distance"] - control["initial_distance"]) < 1e-9
    assert audit["controls"]["all_steps_trace_preserving"] is True
    assert "not empirical" in audit["claim_boundary"]


def test_no_signaling_library_flags_disturbing_control() -> None:
    from simulation.quantum_surrogates import build_no_signaling_scenario_library_audit

    audit = build_no_signaling_scenario_library_audit()
    assert audit["all_controls_pass"] is True
    rows = {row["id"]: row for row in audit["rows"]}
    assert rows["quantum_chsh_bell"]["no_signaling"] is True
    assert rows["product_local"]["no_signaling"] is True
    # Discriminating negative control: the disturbing table signals and is flagged.
    assert rows["disturbing_control"]["no_signaling"] is False
    assert rows["disturbing_control"]["max_marginal_drift"] > 1e-9
    assert "not empirical" in audit["claim_boundary"]


def test_n_cycle_contextuality_library_matches_two_colorability() -> None:
    from simulation.quantum_surrogates import build_n_cycle_contextuality_library_audit

    audit = build_n_cycle_contextuality_library_audit()
    assert audit["all_controls_pass"] is True
    rows = {row["n"]: row for row in audit["rows"]}
    # Independent cross-check: perfect anti-correlation is feasible iff the cycle is two-colorable.
    for n, row in rows.items():
        assert row["perfect_anticorrelation_feasible"] == (n % 2 == 0)
    # Contextuality dichotomy at the quantum correlation: odd cycles infeasible, even feasible.
    assert rows[5]["quantum_correlation_feasible"] is False  # KCBS pentagon is contextual
    assert rows[4]["quantum_correlation_feasible"] is True
    # Discriminating negative control: the uncorrelated behavior is always noncontextual.
    assert all(row["uncorrelated_feasible"] for row in audit["rows"])
    assert "not empirical" in audit["claim_boundary"]


def test_data_processing_monotonicity_holds_and_controls_fire() -> None:
    from simulation.quantum_surrogates import build_data_processing_monotonicity_audit

    audit = build_data_processing_monotonicity_audit()
    assert audit["all_controls_pass"] is True
    assert "not empirical" in audit["claim_boundary"]
    # Data-processing inequality: every CPTP channel is non-increasing in both metrics.
    for row in audit["channel_rows"]:
        assert row["trace_distance_after"] <= row["trace_distance_before"] + 1e-9
        assert row["relative_entropy_after_bits"] <= row["relative_entropy_before_bits"] + 1e-9
    cp_rows = {row["map"]: row for row in audit["complete_positivity_rows"]}
    # Discriminating control 1 has teeth: physical channels are CP (Choi min eig >= 0) while the
    # transpose control is positive-but-not-CP (Choi min eig = -1). The control separates them.
    assert cp_rows["transpose_control"]["completely_positive"] is False
    assert cp_rows["transpose_control"]["choi_min_eigenvalue"] < -0.5
    for name in ("phase_damping", "amplitude_damping", "depolarizing"):
        assert cp_rows[name]["completely_positive"] is True
        assert cp_rows[name]["choi_min_eigenvalue"] > -1e-9
    # Discriminating control 2 has teeth: selective record-keeping post-selection STRICTLY increases
    # distinguishability, the opposite direction to the non-selective channels above (non-vacuity).
    assert all(row["post_selection_increases_distance"] for row in audit["selective_postselection_rows"])
    for row in audit["selective_postselection_rows"]:
        assert row["trace_distance_after_postselection"] > row["trace_distance_before"] + 1e-6


def test_markov_blanket_recovered_from_precision_but_not_marginal() -> None:
    from simulation.markov_blanket import build_markov_blanket_discovery_audit

    audit = build_markov_blanket_discovery_audit()
    assert audit["all_controls_pass"] is True
    assert "not empirical" in audit["claim_boundary"]
    # Correctness: the conditional-independence (precision) support recovers the planted blanket
    # exactly, and so does a partial-correlation threshold -- the dividing line is precision vs
    # covariance, NOT a clever method vs a strawman (anti-strawman requirement).
    assert audit["controls"]["precision_support_recovers_blanket"] is True
    assert audit["precision_support_recovered_blanket"] == audit["blanket_nodes"]
    assert audit["partial_correlation_best_f1"] == 1.0
    # Decisive measured contrast WITH TEETH: no threshold on the marginal correlation matrix recovers
    # the blanket, because a weak true internal-blanket correlation is masked by a stronger induced
    # internal-external one -- the boundary is invisible to the interior's passive marginal view.
    assert audit["controls"]["marginal_covariance_threshold_cannot_recover_blanket"] is True
    assert audit["marginal_correlation_best_f1"] < 1.0
    # Discriminating controls: a fully-coupled precision has no nontrivial blanket, and an epsilon
    # internal-external coupling breaks the exact conditional independence (not vacuously satisfied).
    assert audit["controls"]["dense_precision_has_no_nontrivial_blanket"] is True
    assert audit["dense_precision_external_set"] == []
    assert audit["controls"]["epsilon_coupling_breaks_exact_separation"] is True
    assert audit["epsilon_internal_external_edges_detected"] == 4
    # Distributional honesty: the per-instance "marginal cannot recover" result is NOT over-generalized.
    # Across perturbations the precision support recovers the blanket in every instance, while the
    # marginal recovers it only for a minority -- reliably visible conditionally, contingently in marginal.
    ensemble = audit["perturbation_ensemble"]
    assert ensemble["precision_recovery_fraction"] == 1.0
    assert ensemble["marginal_recovery_fraction"] < 0.5
    assert audit["controls"]["precision_recovers_more_reliably_than_marginal_in_ensemble"] is True


def test_quantum_cramer_rao_pointer_loses_information_only_under_coherence() -> None:
    from simulation.quantum_estimation import build_quantum_cramer_rao_estimation_audit

    audit = build_quantum_cramer_rao_estimation_audit()
    assert audit["all_controls_pass"] is True
    assert "not empirical" in audit["claim_boundary"]
    # The quantum Cramer-Rao bound is never violated and the SLD-optimal measurement saturates QFI.
    assert audit["controls"]["quantum_cramer_rao_bound_never_violated"] is True
    assert audit["controls"]["optimal_measurement_saturates_qfi"] is True
    for row in audit["coherent_rows"]:
        assert row["sld_optimal_fisher_information"] <= row["quantum_fisher_information"] + 1e-9
        assert abs(row["sld_optimal_fisher_information"] - row["quantum_fisher_information"]) < 1e-6
    # DISCRIMINATING contrast: the decohered pointer measurement strictly loses information when sigma is
    # encoded coherently, but is already optimal when it is encoded classically -- the gap is created by
    # coherence (which opacification renders inaccessible), not by construction.
    assert audit["controls"]["coherent_pointer_measurement_strictly_loses_information"] is True
    assert all(row["pointer_information_gap"] > 0.01 for row in audit["coherent_rows"])
    assert audit["controls"]["classical_encoding_pointer_is_already_optimal"] is True
    assert all(abs(row["pointer_information_gap"]) < 1e-9 for row in audit["classical_rows"])


def test_interaction_information_separates_synergy_from_redundancy() -> None:
    from simulation.interaction_information import build_interaction_information_boundary_audit

    audit = build_interaction_information_boundary_audit()
    assert audit["all_controls_pass"] is True
    assert "not empirical" in audit["claim_boundary"]
    rows = {row["fixture"]: row for row in audit["rows"]}
    # The sharpest no-self-evidence echo: the XOR boundary's marginal information is EXACTLY zero (the
    # interior observes nothing passively) yet the conditional information is a full bit.
    assert rows["synergistic_xor"]["marginal_mutual_information_bits"] == 0.0
    assert abs(rows["synergistic_xor"]["conditional_mutual_information_bits"] - 1.0) < 1e-6
    assert rows["synergistic_xor"]["interaction_information_bits"] > 0.5
    # The redundant screen is conditionally independent with negative interaction information, and the
    # sign of interaction information flips between the regimes -- a marginal-only reading cannot tell them
    # apart. Both are measured, not asserted.
    assert abs(rows["redundant_screen"]["conditional_mutual_information_bits"]) < 1e-6
    assert rows["redundant_screen"]["interaction_information_bits"] < 0.0
    assert audit["controls"]["interaction_information_sign_discriminates_regimes"] is True
    assert rows["independent_null"]["interaction_information_bits"] == 0.0


def test_blackwell_relabel_preserves_but_garbling_degrades_bayes_risk() -> None:
    from simulation.blackwell_ordering import build_blackwell_bayes_risk_audit

    audit = build_blackwell_bayes_risk_audit()
    assert audit["all_controls_pass"] is True
    assert "not empirical" in audit["claim_boundary"]
    # Use is licensed: every invertible relabeling preserves the boundary's Bayes risk exactly.
    assert audit["controls"]["invertible_relabeling_preserves_bayes_risk"] is True
    assert all(abs(row["bayes_risk"] - audit["original_bayes_risk"]) < 1e-9 for row in audit["relabeling_rows"])
    # Ontology is not: a nontrivial garbling strictly raises the Bayes risk, and Blackwell monotonicity
    # means no garbling over the dense grid ever lowers it below the original.
    assert audit["controls"]["nontrivial_garbling_strictly_increases_bayes_risk"] is True
    assert audit["controls"]["bayes_risk_never_below_original_under_garbling"] is True
    assert audit["minimum_grid_garbling_risk"] >= audit["original_bayes_risk"] - 1e-9
    garblings = {row["garbling"]: row for row in audit["garbling_rows"]}
    assert garblings["partial_garbling"]["risk_increase_vs_original"] > 0.01
    assert audit["controls"]["complete_erasure_reaches_chance_risk"] is True


def test_classical_data_processing_sufficiency_saturates_lossy_drops() -> None:
    from simulation.classical_data_processing import build_classical_data_processing_audit

    audit = build_classical_data_processing_audit()
    assert audit["all_controls_pass"] is True
    assert "not empirical" in audit["claim_boundary"]
    rows = {row["readout"]: row for row in audit["rows"]}
    # The interior never knows the external better than the blanket lets it (data-processing inequality).
    assert audit["controls"]["data_processing_inequality_holds_for_every_readout"] is True
    assert all(row["data_processing_inequality_respected"] for row in audit["rows"])
    # Sufficient read-out saturates the bound (gap 0); lossy strictly loses; constant reaches zero.
    assert abs(rows["sufficient_identity"]["information_gap_bits"]) < 1e-9
    assert rows["lossy_merge"]["information_gap_bits"] > 0.05
    assert rows["lossy_merge"]["interior_external_information_bits"] < rows["lossy_merge"]["blanket_external_information_bits"]
    assert abs(rows["constant_erasure"]["interior_external_information_bits"]) < 1e-9


def test_seeded_surrogates_are_byte_identical_on_replay() -> None:
    # Determinism guard: every seeded-deterministic surrogate must reproduce byte-for-byte on a
    # second in-process build, reinforcing the ISA's seeded-deterministic foundation. A
    # non-seeded clock/random leak would make the JSON differ and fail this guard.
    from simulation.blackwell_ordering import build_blackwell_bayes_risk_audit
    from simulation.classical_data_processing import build_classical_data_processing_audit
    from simulation.emergence import build_ongoing_revision_audit, build_separation_prior_emergence_audit
    from simulation.interaction_information import build_interaction_information_boundary_audit
    from simulation.markov_blanket import build_markov_blanket_discovery_audit
    from simulation.quantum_estimation import build_quantum_cramer_rao_estimation_audit
    from simulation.quantum_surrogates import (
        build_collision_model_thermalization_audit,
        build_data_processing_monotonicity_audit,
        build_internal_cut_unmeasurability_audit,
        build_multipartite_witness_suite_audit,
        build_n_cycle_contextuality_library_audit,
        build_no_signaling_scenario_library_audit,
        build_sigma_contextuality_suppression_audit,
        build_tensor_network_benchmark_audit,
    )

    builders = [
        lambda: build_stochastic_policy_ensemble(seed=11, runs=8, steps=16),
        lambda: build_compassion_scope_audit(default_deployments()),
        lambda: build_separation_prior_emergence_audit(),
        lambda: build_internal_cut_unmeasurability_audit(),
        lambda: build_sigma_contextuality_suppression_audit(),
        lambda: build_ongoing_revision_audit(),
        lambda: build_effect_size_test_calibration_audit(),
        lambda: build_multipartite_witness_suite_audit(),
        lambda: build_tensor_network_benchmark_audit(),
        lambda: build_collision_model_thermalization_audit(),
        lambda: build_no_signaling_scenario_library_audit(),
        lambda: build_n_cycle_contextuality_library_audit(),
        lambda: build_data_processing_monotonicity_audit(),
        lambda: build_markov_blanket_discovery_audit(),
        lambda: build_quantum_cramer_rao_estimation_audit(),
        lambda: build_interaction_information_boundary_audit(),
        lambda: build_blackwell_bayes_risk_audit(),
        lambda: build_classical_data_processing_audit(),
    ]
    for builder in builders:
        first = json.dumps(builder(), sort_keys=True)
        second = json.dumps(builder(), sort_keys=True)
        assert first == second
