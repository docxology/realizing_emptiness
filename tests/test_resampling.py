from __future__ import annotations

import numpy as np
import pytest

from simulation.resampling import bootstrap_contrast, permutation_test, binomial_summary
from simulation.statistical_robustness import build_seed_bank_calibration


def test_paired_bootstrap_retains_shared_trajectory_variation() -> None:
    baseline = np.arange(24, dtype=float)
    result = bootstrap_contrast(baseline + 2, baseline, seed=7, paired=True)
    assert result["mean_difference"] == 2
    assert result["difference_ci95_low"] == result["difference_ci95_high"] == 2
    independent = bootstrap_contrast(baseline + 2, baseline, seed=7)
    assert independent["difference_ci95_low"] < 2 < independent["difference_ci95_high"]


def test_contrast_intervals_have_the_correct_estimand_and_sign() -> None:
    first, second = np.ones(8), np.zeros(8)
    result = bootstrap_contrast(first, second, seed=4)
    assert result["difference_ci95_low"] == result["difference_ci95_high"] == 1
    assert result["cliffs_ci95_low"] == result["cliffs_ci95_high"] == 1
    reverse = bootstrap_contrast(second, first, seed=4)
    assert reverse["mean_difference"] == reverse["cliffs_delta"] == -1
    assert bootstrap_contrast(first, first, seed=4)["cliffs_delta"] == 0
    assert result == bootstrap_contrast(first, second, seed=4)


def test_permutation_reports_resolution_counts_and_uncertainty() -> None:
    result = permutation_test(np.ones(8), np.zeros(8), seed=3, draws=127)
    assert result["p_value"] == (result["exceedances"] + 1) / 128
    assert result["resolution"] == 1 / 128
    assert result["tail_ci_low"] <= result["exceedances"] / 127 <= result["tail_ci_high"]
    assert 0 < result["tail_ci_high"] < 1
    ties = permutation_test(np.ones(8), np.ones(8), seed=3, draws=127)
    assert ties["exceedances"] == 127 and ties["p_value"] == 1
    assert ties["tail_ci_low"] < 1
    assert result == permutation_test(np.ones(8), np.zeros(8), seed=3, draws=127)


@pytest.mark.parametrize("bad", [[], [np.nan, 0], [np.inf, 0], [[1, 2], [3, 4]]])
def test_resampling_rejects_invalid_samples(bad: list) -> None:
    with pytest.raises(ValueError):
        bootstrap_contrast(bad, [0, 1], seed=1)
    with pytest.raises(ValueError):
        permutation_test([0, 1], bad, seed=1)


def test_invalid_resampling_designs_fail_explicitly() -> None:
    with pytest.raises(ValueError):
        bootstrap_contrast([1, 2], [1, 2, 3], seed=1, paired=True)
    for draws in (0, -1, True, 2.5):
        with pytest.raises(ValueError):
            permutation_test([1, 2], [2, 3], seed=1, draws=draws)
    with pytest.raises(ValueError):
        binomial_summary(5, 4)
    with pytest.raises(ValueError):
        binomial_summary(0, 0)


def test_exact_binomial_intervals_remain_informative_at_boundaries() -> None:
    zero = binomial_summary(0, 32)
    all_hits = binomial_summary(32, 32)
    assert zero["ci_low"] == 0 < zero["ci_high"] < 0.2
    assert 0.8 < all_hits["ci_low"] < all_hits["ci_high"] == 1


def test_seed_bank_detects_injection_and_rejects_absent_effect() -> None:
    calibrated = build_seed_bank_calibration()
    assert calibrated["all_controls_pass"] is True
    assert calibrated["repetitions"] == len(calibrated["rows"]) == 128
    assert calibrated["positive_rejection"]["ci_low"] >= 0.75
    assert calibrated["null_rejection"]["ci_high"] <= 0.25
    removed = build_seed_bank_calibration(positive_shift=0)
    assert removed["all_controls_pass"] is False
    assert removed["controls"]["injected_effect_detected"] is False
    assert calibrated == build_seed_bank_calibration()


@pytest.mark.parametrize("filename,field", [
    ("stochastic_effect_size_audit.json", "difference_ci95_low"),
    ("criticality_stochastic_ensemble.json", "paired_branching_ci95_low"),
    ("effect_size_calibration_audit.json", "null_covered"),
])
def test_statistical_artifacts_require_estimand_and_calibration_rows(pytestconfig, tmp_path, filename, field) -> None:
    import json
    import shutil
    from gates.validation import _load_json

    root = pytestconfig.realizing_emptiness_root
    shutil.copytree(root / "schemas", tmp_path / "schemas")
    relative = f"output/data/{filename}"
    target = tmp_path / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.loads((root / relative).read_text(encoding="utf-8"))
    target.write_text(json.dumps(payload), encoding="utf-8")
    assert _load_json(tmp_path, relative)
    rows = payload["seed_bank"]["rows"] if "seed_bank" in payload else payload.get("rows", payload.get("null_contrasts"))
    rows[0].pop(field)
    target.write_text(json.dumps(payload), encoding="utf-8")
    assert _load_json(tmp_path, relative) == {}


def test_seed_bank_rejects_invalid_designs() -> None:
    with pytest.raises(ValueError):
        build_seed_bank_calibration(repetitions=0)
    with pytest.raises(ValueError):
        build_seed_bank_calibration(positive_shift=np.nan)


@pytest.mark.parametrize("field,value", [
    ("holm_decision_mc_stable", False),
    ("permutation_resolution", 0.5),
    ("permutation_tail_family_ci95_high", 1.0),
    ("holm_p", 1.0),
    ("permutation_exceedances", 100000),
])
def test_permutation_gate_recomputes_decisions(pytestconfig, field, value) -> None:
    import json
    from gates.validation import _permutation_metadata_matches

    path = pytestconfig.realizing_emptiness_root / "output/data/stochastic_effect_size_audit.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert _permutation_metadata_matches(payload)
    assert payload["rows"][0][field] != value
    payload["rows"][0][field] = value
    assert not _permutation_metadata_matches(payload)
    assert not _permutation_metadata_matches({})
