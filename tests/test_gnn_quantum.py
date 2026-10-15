from __future__ import annotations

import ast
import importlib
import json
import shutil

import pytest

from modeling.registry import load_model, specification_root
from simulation.quantum_estimation import build_quantum_cramer_rao_estimation_audit
from simulation.quantum_surrogates import build_quantum_boundary_entropy


MUTATIONS = [
    ("quantum_boundary_entropy", "theta_count", 17),
    ("quantum_open_system_dynamics", "time_count", 11),
    ("quantum_qfep_boundary_hamiltonian_dynamics", "hamiltonian_z", 0.17),
    ("quantum_trajectory_unraveling", "seed", 405),
    ("quantum_internal_cut_unmeasurability_audit", "env_qubits", 3),
    ("quantum_many_body_boundary_screen_sweep", "cuts", [
        {"id": "observer_boundary_cut", "qubits": [0, 1, 2], "cut_class": "candidate_observer_boundary"},
        {"id": "local_cluster_cut", "qubits": [0, 1, 4], "cut_class": "structured_control"},
        {"id": "alternating_cut", "qubits": [0, 2, 4], "cut_class": "structured_control"},
        {"id": "random_cut_control", "qubits": [0, 3, 5], "cut_class": "negative_control_random_cut"},
    ]),
    ("quantum_sheaf_contextuality_obstruction_audit", "scenarios", None),
    ("quantum_sigma_contextuality_suppression_audit", "scenarios", None),
    ("quantum_qrf_transformation_covariance_audit", "observable", [0.3, 0.8, 1.4, 2.0]),
    ("quantum_arbitrary_two_qubit_entanglement_audit", "mixture_weights", [0.6, 0.4]),
    ("quantum_multipartite_witness_suite_audit", "qubit_counts", [2, 3]),
    ("quantum_tensor_network_benchmark_audit", "qubit_counts", [2, 3, 4]),
    ("quantum_collision_model_thermalization_audit", "steps", 20),
    ("quantum_no_signaling_scenario_library_audit", "disturbance", 0.0),
    ("quantum_n_cycle_contextuality_library_audit", "cycles", [3, 4, 5, 6]),
    ("quantum_thermodynamic_channel_cost_audit", "biased_population", [0.6, 0.4]),
    ("quantum_sparse_boundary_screen_scaling_audit", "qubit_counts", [6, 8]),
    ("quantum_qrf_frame_covariance_toy_audit", "mixture_weights", [0.6, 0.4]),
    ("quantum_data_processing_monotonicity_audit", "selection_angles", [0.3, 0.4]),
    ("quantum_cramer_rao_estimation", "radius", 0.5),
    ("quantum_measurement_contextuality", "contexts", None),
    ("quantum_general_measurement_cover_polytope", "scenarios", None),
]


def _replace_parameter(path, key, value):
    content = path.read_text()
    line = next(line for line in content.splitlines() if line.startswith("settings="))
    settings = ast.literal_eval(line.split("=", 1)[1])
    parameters = settings[0]["parameters"]
    if value is None:
        if key == "contexts":
            parameters[key][0]["b_angle"] = 0.1
        else:
            parameters[key][0]["contexts"][0] = ("AB", ("A", "B"), -1)
    else:
        parameters[key] = value
    path.write_text(content.replace(line, "settings=" + repr(settings)))


@pytest.mark.parametrize("model_id,key,value", MUTATIONS)
def test_each_quantum_family_consumes_real_gnn(tmp_path, pytestconfig, model_id, key, value):
    source = pytestconfig.realizing_emptiness_root / "src/modeling/specifications"
    copied = tmp_path / "specifications"
    shutil.copytree(source, copied)
    original = load_model(model_id)
    module, function = original.consumer.split(":")
    build = getattr(importlib.import_module(module), function)
    before = build()
    with specification_root(copied):
        _replace_parameter(copied / (model_id + ".gnn.md"), key, value)
        changed = load_model(model_id)
        after = build()
        assert changed.source_hash != original.source_hash
        assert json.dumps(after, sort_keys=True) != json.dumps(before, sort_keys=True)
        assert "not empirical" in after["claim_boundary"]
        if model_id == "quantum_no_signaling_scenario_library_audit":
            assert before["all_controls_pass"]
            assert not after["all_controls_pass"]
    assert load_model(model_id).source_hash == original.source_hash


def test_explicit_quantum_overrides_take_precedence(tmp_path, pytestconfig):
    copied = tmp_path / "specifications"
    shutil.copytree(pytestconfig.realizing_emptiness_root / "src/modeling/specifications", copied)
    entropy = build_quantum_boundary_entropy(theta_count=9, rotation_count=7)
    estimation = build_quantum_cramer_rao_estimation_audit(radius=0.7)
    with specification_root(copied):
        _replace_parameter(copied / "quantum_boundary_entropy.gnn.md", "theta_count", 17)
        _replace_parameter(copied / "quantum_cramer_rao_estimation.gnn.md", "radius", 0.5)
        assert build_quantum_boundary_entropy(theta_count=9, rotation_count=7) == entropy
        assert build_quantum_cramer_rao_estimation_audit(radius=0.7) == estimation


def test_broken_quantum_specification_fails_closed(tmp_path, pytestconfig):
    copied = tmp_path / "specifications"
    shutil.copytree(pytestconfig.realizing_emptiness_root / "src/modeling/specifications", copied)
    path = copied / "quantum_cramer_rao_estimation.gnn.md"
    path.write_text(path.read_text().replace("input>output", "input>missing"))
    with specification_root(copied), pytest.raises(ValueError):
        build_quantum_cramer_rao_estimation_audit()
