from __future__ import annotations

import ast
from pathlib import Path
import shutil

import pytest

from formalism.equations import evaluate_equation_surrogates
from formalism.review_response_bmr import build_bmr_alternative_prior_audit
from modeling.registry import load_model, specification_paths, specification_root
from simulation.blackwell_ordering import build_blackwell_bayes_risk_audit
from simulation.bmr import run_bmr_sweep
from simulation.classical_data_processing import build_classical_data_processing_audit
from simulation.compassion_scope import compassion_boundary_stream
from simulation.emergence import build_ongoing_revision_audit, build_separation_prior_emergence_audit
from simulation.interaction_information import build_interaction_information_boundary_audit
from simulation.markov_blanket import build_markov_blanket_discovery_audit
from simulation.sensitivity import build_sensitivity_grid


def _mutate(root: Path, model_id: str, key: str, value: object) -> None:
    path = root / f"{model_id}.gnn.md"
    text = path.read_text()
    line = next(line for line in text.splitlines() if line.startswith("settings="))
    settings = ast.literal_eval(line.removeprefix("settings="))
    settings[0]["parameters"][key] = value
    path.write_text(text.replace(line, "settings=" + repr(settings)))


@pytest.fixture
def finite_specs(tmp_path: Path) -> Path:
    for path in specification_paths():
        shutil.copyfile(path, tmp_path / path.name)
    return tmp_path


@pytest.mark.parametrize(
    ("model_id", "key", "value", "build"),
    [
        ("finite_bmr", "sigma_accuracy", 0.6, run_bmr_sweep),
        ("finite_sensitivity", "sigma_accuracy", 0.6, build_sensitivity_grid),
        ("finite_alternative_bmr", "access_grid", [0.0, 0.5, 1.0], build_bmr_alternative_prior_audit),
        ("finite_emergence", "steps", 128, build_separation_prior_emergence_audit),
        ("finite_emergence", "revision_margin", 0.6, build_ongoing_revision_audit),
        ("finite_compassion_scope", "controllability", [0.0] * 6, compassion_boundary_stream),
        ("finite_markov_blanket", "diagonal", 3.0, lambda: build_markov_blanket_discovery_audit(ensemble_samples=4)),
        ("finite_interaction_information", "internal_fidelity", 0.5, build_interaction_information_boundary_audit),
        ("finite_blackwell", "channel", [[0.5, 0.5], [0.5, 0.5]], build_blackwell_bayes_risk_audit),
        ("finite_classical_data_processing", "blanket_given_external", [[1 / 3] * 3] * 3, build_classical_data_processing_audit),
        ("finite_equations", "eq6_predicted", [0.5, 0.5], evaluate_equation_surrogates),
    ],
)
def test_real_gnn_edits_change_finite_execution(finite_specs, model_id, key, value, build):
    baseline = build()
    old_hash = load_model(model_id).source_hash
    _mutate(finite_specs, model_id, key, value)
    with specification_root(finite_specs):
        assert load_model(model_id).source_hash != old_hash
        assert build() != baseline
    assert build() == baseline


@pytest.mark.parametrize(
    ("model_id", "key", "value", "build", "control"),
    [
        ("finite_blackwell", "channel", [[0.5, 0.5], [0.5, 0.5]], build_blackwell_bayes_risk_audit,
         "nontrivial_garbling_strictly_increases_bayes_risk"),
        ("finite_interaction_information", "internal_fidelity", 0.5, build_interaction_information_boundary_audit,
         "redundant_interaction_information_is_negative"),
        ("finite_classical_data_processing", "blanket_given_external", [[1 / 3] * 3] * 3,
         build_classical_data_processing_audit, "lossy_readout_strictly_loses_information"),
    ],
)
def test_model_mutation_cannot_rewrite_independent_controls(finite_specs, model_id, key, value, build, control):
    assert build()["all_controls_pass"]
    _mutate(finite_specs, model_id, key, value)
    with specification_root(finite_specs):
        result = build()
    assert result["controls"][control] is False
    assert result["all_controls_pass"] is False


def test_explicit_grid_override_and_fresh_parameter_load(finite_specs):
    explicit = run_bmr_sweep(access_grid=(0.0, 1.0), precision_grid=(0.2, 1.0))
    _mutate(finite_specs, "finite_bmr", "access_grid", [0.0, 0.5, 1.0])
    with specification_root(finite_specs):
        assert run_bmr_sweep()["row_count"] == 15
        assert run_bmr_sweep(access_grid=(0.0, 1.0), precision_grid=(0.2, 1.0)) == explicit
        _mutate(finite_specs, "finite_bmr", "access_grid", [0.0, 1.0])
        assert run_bmr_sweep()["row_count"] == 10


def test_missing_specification_has_no_python_default(tmp_path):
    with specification_root(tmp_path), pytest.raises(FileNotFoundError):
        run_bmr_sweep()


@pytest.mark.parametrize(("key", "value"), [
    ("prior", [0.25, 0.25]),
    ("prior", [-0.1, 1.1]),
    ("prior", [1.0]),
    ("prior", [True, False]),
    ("channel", [[0.4, 0.1], [0.1, 0.4]]),
    ("channel", [[1.1, -0.1], [0.2, 0.8]]),
    ("channel", [[0.8, 0.2]]),
    ("grid_steps", 1),
    ("grid_steps", 2.5),
    ("grid_steps", True),
    ("named_garblings", [["partial_garbling", 1.1, 0.7], ["complete_erasure", 0.5, 0.5]]),
    ("named_garblings", [["complete_erasure", 0.5, 0.5]]),
    ("named_garblings", [["partial_garbling", 0.7, 0.7]] * 2 + [["complete_erasure", 0.5, 0.5]]),
])
def test_blackwell_invalid_gnn_domains_fail_before_execution(finite_specs, key, value):
    _mutate(finite_specs, "finite_blackwell", key, value)
    with specification_root(finite_specs):
        with pytest.raises(ValueError, match="Blackwell"):
            load_model("finite_blackwell")
        with pytest.raises(ValueError, match="Blackwell"):
            build_blackwell_bayes_risk_audit()


def test_blackwell_normalized_nonuniform_prior_is_consumed(finite_specs):
    baseline = build_blackwell_bayes_risk_audit()
    _mutate(finite_specs, "finite_blackwell", "prior", [0.6, 0.4])
    with specification_root(finite_specs):
        result = build_blackwell_bayes_risk_audit()
    assert result["prior"] == [0.6, 0.4]
    assert result["chance_risk"] == pytest.approx(0.4)
    assert result["chance_risk"] != baseline["chance_risk"]
    assert result["original_bayes_risk"] == pytest.approx(0.2)
    assert result["all_controls_pass"]


@pytest.mark.parametrize("grid_steps", [0, 1, 2.5, True])
def test_blackwell_invalid_explicit_grid_is_rejected(grid_steps):
    with pytest.raises(ValueError, match="Blackwell"):
        build_blackwell_bayes_risk_audit(grid_steps=grid_steps)


def test_compatibility_exports_resolve_current_specification(finite_specs):
    import simulation.compassion_scope as compassion
    import simulation.markov_blanket as blanket

    assert len(compassion.CHANNEL_CONTROLLABILITY) == 6
    assert blanket.INTERNAL == (0, 1)
    assert blanket.BLANKET == (2, 3)
    assert blanket.EXTERNAL == (4, 5)
    assert blanket._EDGES[(0, 2)] == 0.4
    _mutate(finite_specs, "finite_compassion_scope", "controllability", [0.2] * 6)
    with specification_root(finite_specs):
        assert compassion.CHANNEL_CONTROLLABILITY == (0.2,) * 6
    for module in (compassion, blanket):
        with pytest.raises(AttributeError):
            getattr(module, "unknown_model_constant")
