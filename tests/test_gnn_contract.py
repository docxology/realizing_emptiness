from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import shutil

import jsonschema
import pytest

from modeling.audit import _consumer_binding, build_gnn_model_audit, gnn_model_audit_matches
from modeling.registry import load_model, parse_model, specification_paths, specification_root, upstream_identity


@pytest.fixture(scope="module")
def receipt(pytestconfig):
    root = pytestconfig.realizing_emptiness_root
    return root, build_gnn_model_audit(root)


@pytest.fixture
def mirror(tmp_path, pytestconfig):
    root = pytestconfig.realizing_emptiness_root
    shutil.copytree(root / "src", tmp_path / "src", ignore=shutil.ignore_patterns("__pycache__"))
    return tmp_path


def test_native_receipt_is_complete_and_reconstructs(receipt):
    root, payload = receipt
    schema = json.loads((root / "schemas/gnn_model_audit.schema.json").read_text())
    jsonschema.Draft202012Validator(schema).validate(payload)
    assert payload["all_controls_pass"]
    assert all(payload["controls"].values())
    assert {row["model_id"] for row in payload["native_probes"]} == {"separation_constrained", "opacified", "post_dual"}
    assert gnn_model_audit_matches(payload, root)
    assert len(payload["models"]) == len(json.loads((root / "src/modeling/catalog.json").read_text())["models"])
    for row in payload["native_probes"]:
        assert len(row["actions"]) == len(row["beliefs"]) == row["steps"]
        assert row["beliefs"][0] == pytest.approx(row["manual_first_posterior"], abs=1e-6)
        assert "memory_usage_mb" not in row


@pytest.mark.parametrize("field", ["beliefs", "policy_posterior", "negative_expected_free_energy", "actions", "source_sha256"])
def test_forged_native_receipt_fails_independent_reconstruction(receipt, field):
    root, payload = receipt
    forged = deepcopy(payload)
    trace = forged["native_probes"][0]
    if field == "source_sha256":
        trace[field] = "0" * 64
    elif field == "actions":
        trace[field][0] = 99
    else:
        trace[field][0][0] += 0.1
    assert not gnn_model_audit_matches(forged, root)


def test_missing_and_extra_models_fail_closed(receipt, mirror):
    _, payload = receipt
    missing = mirror / "src/modeling/specifications/finite_bmr.gnn.md"
    missing.rename(missing.with_suffix(".absent"))
    assert not gnn_model_audit_matches(payload, mirror)
    missing.with_suffix(".absent").rename(missing)
    shutil.copyfile(missing, missing.with_name("unexpected.gnn.md"))
    assert not gnn_model_audit_matches(payload, mirror)


def test_curated_consumer_and_implementation_binding_fail_closed(receipt, mirror):
    _, payload = receipt
    spec = mirror / "src/modeling/specifications/finite_bmr.gnn.md"
    text = spec.read_text()
    spec.write_text(text.replace("simulation.bmr:run_bmr_sweep", "simulation.bmr:compare_models"))
    assert not gnn_model_audit_matches(payload, mirror)
    spec.write_text(text)
    module = mirror / "src/simulation/bmr.py"
    module.write_text(module.read_text().replace('model_parameters("finite_bmr")', 'model_parameters("finite_sensitivity")'))
    assert not gnn_model_audit_matches(payload, mirror)


def test_valid_real_source_edit_invalidates_stale_audit(receipt, mirror):
    _, payload = receipt
    spec = mirror / "src/modeling/specifications/finite_bmr.gnn.md"
    original = spec.read_text()
    assert '"sigma_accuracy": 0.3' in original
    spec.write_text(original.replace('"sigma_accuracy": 0.3', '"sigma_accuracy": 0.6'))
    with specification_root(spec.parent):
        assert load_model("finite_bmr").parameters["sigma_accuracy"] == 0.6
    assert not gnn_model_audit_matches(payload, mirror)


@pytest.mark.parametrize("mutation", [
    lambda text: text + "\n## Connections\nA>o\n",
    lambda text: text.replace("D>s", "undeclared>s"),
    lambda text: text.replace("C[3,type=float]", "C[2,type=float]"),
    lambda text: text.replace("D=[0.82,0.15,0.03]", "D=[0.82,0.82,0.82]"),
    lambda text: text.replace("D=[0.82,0.15,0.03]", "D=[inf,0.15,0.03]"),
    lambda text: text.replace("C=[1.15,0.15,-0.25]\n", ""),
])
def test_real_invalid_specification_is_rejected(mirror, mutation):
    root = mirror / "src/modeling/specifications"
    path = root / "separation_constrained.gnn.md"
    path.write_text(mutation(path.read_text()))
    with specification_root(root), pytest.raises((ValueError, TypeError, KeyError, SyntaxError)):
        load_model("separation_constrained")
    assert not gnn_model_audit_matches({}, mirror)


def test_missing_receipt_and_modified_upstream_pin_fail_closed(receipt, mirror):
    root, payload = receipt
    assert not gnn_model_audit_matches({}, root)
    assert not gnn_model_audit_matches(None, root)
    pin = mirror / "src/modeling/upstream.json"
    data = json.loads(pin.read_text())
    data["commit"] = "0" * 40
    pin.write_text(json.dumps(data))
    assert not gnn_model_audit_matches(payload, mirror)


def test_admission_preserves_declared_tensor_parameters(pytestconfig):
    path = pytestconfig.realizing_emptiness_root / "src/modeling/specifications/separation_constrained.gnn.md"
    admitted = parse_model(path.read_text(), "separation_constrained")
    assert admitted.tensors["C"] == [1.15, 0.15, -0.25]
    assert admitted.tensors["D"] == pytest.approx([0.82, 0.15, 0.03])


@pytest.mark.parametrize(("source", "replacement", "field"), [
    ("C=[1.15,0.15,-0.25]", "C=[-0.25,0.15,1.15]", "policy_posterior"),
    ("D=[0.82,0.15,0.03]", "D=[0.03,0.82,0.15]", "beliefs"),
])
def test_real_gnn_tensor_file_mutation_changes_native_agent(receipt, mirror, source, replacement, field):
    _, payload = receipt
    path = mirror / "src/modeling/specifications/separation_constrained.gnn.md"
    original = path.read_text()
    assert source in original
    path.write_text(original.replace(source, replacement))
    changed = build_gnn_model_audit(mirror)
    before = next(row for row in payload["native_probes"] if row["model_id"] == "separation_constrained")
    after = next(row for row in changed["native_probes"] if row["model_id"] == "separation_constrained")
    assert before["source_sha256"] != after["source_sha256"]
    assert before["tensors_sha256"] != after["tensors_sha256"]
    assert after[field][0] != pytest.approx(before[field][0])
    assert changed["all_controls_pass"]


def test_claim_flags_cannot_replace_actual_controls(receipt):
    root, payload = receipt
    forged = deepcopy(payload)
    forged["controls"]["unknown_edge_rejected"] = False
    forged["all_controls_pass"] = True
    assert not gnn_model_audit_matches(forged, root)


def test_catalog_duplicates_and_registry_drift_are_rejected(receipt, mirror):
    _, payload = receipt
    path = mirror / "src/modeling/catalog.json"
    catalog = json.loads(path.read_text())
    catalog["models"].append(catalog["models"][0])
    path.write_text(json.dumps(catalog))
    assert not gnn_model_audit_matches(payload, mirror)
    catalog["models"].pop()
    path.write_text(json.dumps(catalog))
    registry = mirror / "src/modeling/registry.py"
    registry.write_text(registry.read_text() + "\nchanged_admission = True\n")
    assert not gnn_model_audit_matches(payload, mirror)


@pytest.mark.parametrize("mutation", [
    lambda text: text.replace("## GNNVersionAndFlags\nGNN v1\n", ""),
    lambda text: text.replace("GNN v1", "GNN v2"),
    lambda text: text.replace("## ModelName\nfinite_bmr", "## ModelName\nwrong_name"),
    lambda text: text.replace("input[1,type=float]", "input[0,type=float]"),
    lambda text: text.replace("input[1,type=float]", "input[1,type=unsupported]"),
    lambda text: text.replace("input[1,type=float]", "input[1,type=float]\ninput[1,type=float]"),
    lambda text: text.replace("input>output", "input>output\nunparsed connection"),
    lambda text: text + "\nsettings=[{}]\n",
    lambda text: text[:text.index("settings=")] + "settings=[{}]\n",
    lambda text: text.replace("not empirical", "empirical"),
    lambda text: text.replace('"backend": "numpy_scipy"', '"backend": "unknown"'),
    lambda text: text.replace("FiniteSurrogate", "UnsupportedModel"),
    lambda text: text + "\nextra_parameter=1\n",
    lambda text: text.replace('"family": "finite_bmr"', '"family": ""'),
    lambda text: text.replace('"sigma_accuracy": 0.3', '"sigma_accuracy": 1e999'),
])
def test_registry_rejects_lossy_or_unbound_finite_declarations(pytestconfig, tmp_path, mutation):
    source = pytestconfig.realizing_emptiness_root / "src/modeling/specifications/finite_bmr.gnn.md"
    content = source.read_text()
    changed = mutation(content)
    assert changed != content
    path = tmp_path / source.name
    path.write_text(changed)
    with specification_root(tmp_path), pytest.raises((ValueError, TypeError, KeyError, SyntaxError)):
        load_model("finite_bmr")


def test_registry_inventory_identity_and_isolated_parameter_copies(tmp_path):
    assert upstream_identity()["version"] == "4.1.0"
    assert specification_paths()
    with specification_root(tmp_path), pytest.raises(ValueError, match="empty"):
        specification_paths()
    with pytest.raises(ValueError, match="identifier"):
        load_model("../finite_bmr")
    first = load_model("finite_bmr")
    first.parameters["access_grid"].append(99)
    assert 99 not in load_model("finite_bmr").parameters["access_grid"]


@pytest.mark.parametrize(("consumer", "identifier"), [
    ("simulation.bmr:CLAIM_BOUNDARY", "finite_bmr"),
    ("simulation.bmr:run_bmr_sweep", "unbound_model"),
])
def test_registered_consumer_must_be_callable_and_source_bound(pytestconfig, consumer, identifier):
    model = replace(load_model("finite_bmr"), consumer=consumer, model_id=identifier)
    with pytest.raises(ValueError):
        _consumer_binding(model, pytestconfig.realizing_emptiness_root)


@pytest.mark.parametrize(("key", "value"), [
    ("profile_ids", ["separation_constrained", "opacified", "post_dual", "post_dual"]),
    ("native_probe_steps", 0),
])
def test_runtime_selector_and_probe_design_fail_closed(receipt, mirror, key, value):
    _, payload = receipt
    path = mirror / "src/modeling/specifications/qrf_boundary.gnn.md"
    text = path.read_text()
    line = next(line for line in text.splitlines() if line.startswith("settings="))
    settings = ast.literal_eval(line.removeprefix("settings="))
    settings[0]["parameters"][key] = value
    path.write_text(text.replace(line, "settings=" + repr(settings)))
    assert not gnn_model_audit_matches(payload, mirror)


def test_overflowing_tensor_is_rejected_without_crashing_gate(receipt, mirror):
    _, payload = receipt
    path = mirror / "src/modeling/specifications/separation_constrained.gnn.md"
    text = path.read_text()
    path.write_text(text.replace("D=[0.82,0.15,0.03]", "D=[" + str(10**400) + ",0,0]"))
    assert not gnn_model_audit_matches(payload, mirror)
