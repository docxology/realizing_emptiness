from copy import deepcopy
import json
import shutil

import numpy as np
import pytest

from gates.validation import _criticality_stochastic_ensemble_matches, _load_json
from simulation.criticality import (
    avalanche_size_distribution,
    branching_ratio,
    build_criticality_report,
    build_criticality_stochastic_ensemble,
)
from simulation.statistical_robustness import build_stochastic_effect_size_audit
from simulation.stochastic import build_stochastic_policy_ensemble


@pytest.fixture(scope="module")
def policy():
    return build_stochastic_policy_ensemble(seed=101, runs=32, steps=48)


@pytest.fixture(scope="module")
def ensemble(policy):
    return build_criticality_stochastic_ensemble(policy)


def test_real_seeded_branching_gate(policy, ensemble):
    assert _criticality_stochastic_ensemble_matches(ensemble, policy)


@pytest.mark.parametrize("mutation", [
    "controls", "missing_control", "extra_control", "missing_profile", "duplicate_profile",
    "duplicate_run", "summary", "derived_index", "delta", "disjoint", "paired_interval",
    "paired_seed", "null_seed", "method", "count", "nonfinite", "trajectory", "empty",
])
def test_branching_gate_rejects_forgery(policy, ensemble, mutation):
    changed, source = deepcopy(ensemble), deepcopy(policy)
    if mutation == "controls":
        changed["controls"]["measured_branching_separates_from_null"] = False
    elif mutation == "missing_control":
        del changed["controls"]["measured_branching_separates_from_null"]
    elif mutation == "extra_control":
        changed["controls"]["any_signature_separates"] = True
    elif mutation == "missing_profile":
        changed["null_contrasts"].pop()
    elif mutation == "duplicate_profile":
        changed["null_contrasts"][-1] = deepcopy(changed["null_contrasts"][0])
    elif mutation == "duplicate_run":
        changed["metric_rows"][-1] = deepcopy(changed["metric_rows"][0])
    elif mutation == "summary":
        changed["summary_rows"][0]["metrics"]["branching_ratio"]["ci95_low"] += 0.1
    elif mutation == "derived_index":
        changed["metric_rows"][0]["criticality_index"] += 0.1
    elif mutation == "delta":
        changed["null_contrasts"][0]["branching_ratio_delta_vs_null"] += 0.1
    elif mutation == "disjoint":
        changed["null_contrasts"][0]["branching_ratio_ci_disjoint_from_null"] = not changed["null_contrasts"][0]["branching_ratio_ci_disjoint_from_null"]
    elif mutation == "paired_interval":
        changed["null_contrasts"][0]["paired_branching_ci95_high"] += 0.1
    elif mutation == "paired_seed":
        changed["null_contrasts"][0]["paired_bootstrap_seed"] += 1
    elif mutation == "null_seed":
        changed["branching_null_seed"] += 1
    elif mutation == "method":
        changed["branching_null_method"] = "unpaired"
    elif mutation == "count":
        changed["metric_row_count"] += 1
    elif mutation == "nonfinite":
        changed["metric_rows"][0]["branching_ratio"] = float("nan")
    elif mutation == "trajectory":
        for row in source["rows"]:
            row["observation"] = 0
    else:
        changed = {}
    assert not _criticality_stochastic_ensemble_matches(changed, source)


def test_collapsed_trajectory_fails_even_with_forged_controls(policy):
    collapsed = deepcopy(policy)
    for row in collapsed["rows"]:
        row["observation"] = 0
    result = build_criticality_stochastic_ensemble(collapsed)
    assert not result["controls"]["measured_branching_separates_from_null"]
    result["controls"] = dict.fromkeys(result["controls"], True)
    result["all_controls_pass"] = True
    assert not _criticality_stochastic_ensemble_matches(result, collapsed)


def test_exactly_half_profiles_is_not_a_majority(policy):
    source = deepcopy(policy)
    first = sorted({row["profile"] for row in source["rows"]})[0]
    for field in ("rows", "run_summaries"):
        copies = [dict(row, profile="zzz_extra") for row in source[field] if row["profile"] == first]
        source[field].extend(copies)
    for row in source["rows"]:
        if row["profile"] in (first, "zzz_extra"):
            row["observation"] = 0
    result = build_criticality_stochastic_ensemble(source)
    assert len(result["null_contrasts"]) == 4
    assert sum(row["branching_ratio_ci_disjoint_from_null"] for row in result["null_contrasts"]) == 2
    assert result["controls"]["majority_of_profiles_ci_separate_from_null"] is False
    result["controls"] = dict.fromkeys(result["controls"], True)
    result["all_controls_pass"] = True
    assert not _criticality_stochastic_ensemble_matches(result, source)


def test_fewer_than_three_profiles_fails(policy):
    source = deepcopy(policy)
    first = sorted({row["profile"] for row in source["rows"]})[0]
    for field in ("rows", "run_summaries"):
        source[field] = [row for row in source[field] if row["profile"] != first]
    result = build_criticality_stochastic_ensemble(source)
    assert not _criticality_stochastic_ensemble_matches(result, source)


@pytest.mark.parametrize("activity", [[-1, 2], [0, float("nan")], [1, float("inf")], [[1, 2]]])
def test_invalid_activity_is_rejected(activity):
    with pytest.raises(ValueError):
        branching_ratio(np.asarray(activity))
    with pytest.raises(ValueError):
        avalanche_size_distribution(np.asarray(activity))


@pytest.mark.parametrize("threshold", [-1, float("nan"), float("inf")])
def test_invalid_avalanche_threshold_is_rejected(threshold):
    with pytest.raises(ValueError):
        avalanche_size_distribution(np.asarray([0.0, 1.0]), threshold=threshold)


@pytest.mark.parametrize("artifact", ["criticality_proxy_report", "criticality_stochastic_ensemble", "stochastic_effect_size_audit"])
def test_schema_loader_rejects_stale_and_unknown_fields(tmp_path, pytestconfig, policy, ensemble, artifact):
    root = pytestconfig.realizing_emptiness_root
    schema_name = f"schemas/{artifact}.schema.json"
    schema_path = tmp_path / schema_name
    schema_path.parent.mkdir(parents=True)
    shutil.copyfile(root / schema_name, schema_path)
    if artifact == "criticality_proxy_report":
        payload = build_criticality_report({"trajectory": [{"observation": x} for x in [0, 1, 2, 1, 0]]})
        relative = f"output/reports/{artifact}.json"
    elif artifact == "criticality_stochastic_ensemble":
        payload = deepcopy(ensemble)
        relative = f"output/data/{artifact}.json"
    else:
        payload = build_stochastic_effect_size_audit(policy)
        relative = f"output/data/{artifact}.json"
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(payload))
    assert _load_json(tmp_path, relative) == payload
    for field in ("near_critical_score", "unknown_field"):
        changed = deepcopy(payload)
        changed[field] = 1
        target.write_text(json.dumps(changed))
        assert _load_json(tmp_path, relative) == {}
    if artifact == "criticality_stochastic_ensemble":
        changed = deepcopy(payload)
        changed["null_contrasts"][0]["any_signature_ci_disjoint_from_null"] = True
        target.write_text(json.dumps(changed))
        assert _load_json(tmp_path, relative) == {}
    if artifact == "stochastic_effect_size_audit":
        changed = deepcopy(payload)
        changed["rows"][0]["pooled_effect_size"] = 1.0
        target.write_text(json.dumps(changed))
        assert _load_json(tmp_path, relative) == {}
    target.write_text("{invalid")
    assert _load_json(tmp_path, relative) == {}
    assert _load_json(tmp_path, "missing.json") == {}
