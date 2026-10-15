"""Source-bound GNN admission and real upstream execution receipts."""

from __future__ import annotations

import ast
from hashlib import sha256
from importlib import import_module, metadata
import inspect
import json
from pathlib import Path
import re
from tempfile import TemporaryDirectory
from typing import Any

import numpy as np

from modeling.registry import CLAIM_BOUNDARY, ModelSpecification, load_model, parse_model, specification_root


_PROFILES = {"separation_constrained", "opacified", "post_dual"}
_PROFILE_CONSUMER = "simulation.pymdp_profiles:build_profile_generative_model"
_UPSTREAM_MODULES = (
    "gnn.parsers.markdown_parser", "gnn.validation.semantic_validator",
    "gnn.render.pomdp_contract", "gnn.execute.pymdp.simulation",
)


def _digest(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _upstream(project_root: Path) -> dict[str, Any]:
    pin = json.loads((project_root / "src/modeling/upstream.json").read_text())
    distribution = metadata.distribution("generalized-notation-notation")
    direct = json.loads(distribution.read_text("direct_url.json") or "{}")
    if (distribution.version != pin["version"] or direct.get("vcs_info", {}).get("commit_id") != pin["commit"]
            or direct.get("vcs_info", {}).get("vcs") != "git"
            or direct.get("url", "").removesuffix(".git") != pin["repository"]):
        raise ValueError("installed GNN distribution does not match its pinned VCS identity")
    for name in _UPSTREAM_MODULES:
        installed = Path(distribution.locate_file(Path(*name.split(".")).with_suffix(".py"))).resolve()
        if Path(inspect.getfile(import_module(name))).resolve() != installed:
            raise ValueError("executing GNN module is not provided by the pinned distribution")
    return {
        "version": distribution.version, "commit": pin["commit"], "repository": pin["repository"],
        "pin_sha256": _file_hash(project_root / "src/modeling/upstream.json"),
        "direct_url_sha256": _digest(direct),
        "module_sha256": {name: _file_hash(Path(inspect.getfile(import_module(name)))) for name in _UPSTREAM_MODULES},
    }


def _consumer_binding(model: ModelSpecification, project_root: Path) -> dict[str, str]:
    module_name, symbol = model.consumer.split(":")
    module = import_module(module_name)
    function = getattr(module, symbol)
    if not inspect.isfunction(function) or function.__module__ != module_name:
        raise ValueError("GNN consumer must resolve to a function in its declared module")
    relative_path = Path("src", *module_name.split(".")).with_suffix(".py")
    source_path = project_root / relative_path
    source = source_path.read_text()
    if _file_hash(source_path) != _file_hash(Path(inspect.getfile(module))):
        raise ValueError("consumer checkout differs from the executing module")
    calls = [node for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Name) and node.func.id in {"model_parameters", "load_model"}]
    literal_binding = any(call.args and isinstance(call.args[0], ast.Constant) and call.args[0].value == model.model_id for call in calls)
    if model.model_id in _PROFILES and model.consumer == _PROFILE_CONSUMER:
        from formalism.models import QRFDeployment
        from simulation.pymdp_profiles import ProfileSpec

        dynamic_binding = any(call.func.id == "load_model" and call.args
                              and isinstance(call.args[0], ast.Attribute) and call.args[0].attr == "model_id" for call in calls)
        deployment = model.parameters["deployment"]
        profile = ProfileSpec(QRFDeployment(deployment["name"], tuple(deployment["sector_labels"]),
                                           deployment["metacognitive_access"], deployment["prior_precision"]), model.model_id)
        actual = function(profile)
        literal_binding = dynamic_binding and all(np.array_equal(actual[key], model.tensors[key]) for key in ("A", "B", "C", "D"))
    if not literal_binding:
        raise ValueError(f"consumer has no executable GNN source binding for {model.model_id}")
    return {"consumer_source": relative_path.as_posix(), "consumer_sha256": _file_hash(source_path)}


def _native_probe(model: ModelSpecification) -> dict[str, Any]:
    from gnn.execute.pymdp import run_pymdp_simulation
    from gnn.render.pomdp_contract import build_canonical_pomdp_spec

    design = load_model("qrf_boundary").parameters
    steps, seed = design["native_probe_steps"], design["native_probe_seed"]
    if type(steps) is not int or steps < 1 or type(seed) is not int or seed < 0:
        raise ValueError("native probe requires a positive horizon and nonnegative integer seed")
    canonical = build_canonical_pomdp_spec({
        "model_name": model.model_id, "initialparameterization": model.tensors,
        "model_parameters": {"b_tensor_order": "next_state_previous_state_action", "num_timesteps": steps, "random_seed": seed},
    })
    with TemporaryDirectory(prefix="gnn-native-") as directory:
        success, result = run_pymdp_simulation(canonical, Path(directory))
        recorded = json.loads((Path(directory) / "simulation_results.json").read_text())
    fields = {"observations": "observations", "actions": "actions", "beliefs": "beliefs",
              "policy_posterior": "policy_posterior", "negative_expected_free_energy": "expected_free_energy"}
    trace = {target: result[source] for target, source in fields.items()}
    if not success or any(result[key] != recorded[key] for key in fields.values()):
        raise ValueError("upstream executor did not produce a matching on-disk numerical receipt")
    likelihood, prior = np.asarray(model.tensors["A"]), np.asarray(model.tensors["D"])
    beliefs, policies = np.asarray(trace["beliefs"]), np.asarray(trace["policy_posterior"])
    action_count = np.asarray(model.tensors["B"]).shape[2]
    expected = likelihood[trace["observations"][0]] * prior
    expected = expected / expected.sum()
    valid = (
        len(trace["observations"]) == len(trace["actions"]) == steps
        and beliefs.shape == (steps, len(prior)) and policies.shape == (steps, action_count)
        and np.asarray(trace["negative_expected_free_energy"]).shape == policies.shape
        and all(type(value) is int and 0 <= value < action_count for value in trace["actions"])
        and all(type(value) is int and 0 <= value < likelihood.shape[0] for value in trace["observations"])
        and all(np.isfinite(np.asarray(trace[key])).all() for key in fields)
        and np.all(beliefs >= 0) and np.all(policies >= 0)
        and np.allclose(beliefs.sum(axis=1), 1, rtol=0, atol=1e-6)
        and np.allclose(policies.sum(axis=1), 1, rtol=0, atol=1e-6)
        and np.allclose(beliefs[0], expected, rtol=1e-5, atol=1e-6)
    )
    if not valid:
        raise ValueError("native trace violates probability, action, or manual Bayes constraints")
    return {"model_id": model.model_id, "source_sha256": model.source_hash, "tensors_sha256": _digest(model.tensors),
            "steps": steps, "seed": seed, **trace, "manual_first_posterior": expected.tolist()}


def _replace_parameter(content: str, key: str, value: Any) -> str:
    return re.sub(rf"^{key}=.*$", f"{key}={value!r}", content, flags=re.MULTILINE)


def _admission_controls(content: str, model_id: str) -> dict[str, bool]:
    variants = {
        "malformed_rejected": content.replace("A=[[", "A=broken[[", 1),
        "duplicate_section_rejected": content + "\n## Connections\nA>o\n",
        "unknown_edge_rejected": content.replace("D>s", "unknown>s", 1),
        "nonfinite_rejected": _replace_parameter(content, "C", [float("inf"), 0, 0]),
        "missing_c_rejected": re.sub(r"^C=.*\n", "", content, flags=re.MULTILINE),
        "wrong_shape_rejected": _replace_parameter(content, "C", [1, 0]),
        "invalid_probability_rejected": _replace_parameter(content, "D", [0.8, 0.8, 0.8]),
    }
    controls = {"valid_model_admitted": parse_model(content, model_id).model_id == model_id}
    for name, mutated in variants.items():
        try:
            parse_model(mutated, model_id)
        except (ValueError, TypeError, KeyError, SyntaxError):
            controls[name] = True
        else:
            controls[name] = False
    return controls


def build_gnn_model_audit(project_root: Path) -> dict[str, Any]:
    """Recompute model admission, implementation provenance, and native execution evidence."""
    project_root = Path(project_root).resolve()
    catalog_path = project_root / "src/modeling/catalog.json"
    catalog = json.loads(catalog_path.read_text())
    required = {row["model_id"]: row["consumer"] for row in catalog["models"]}
    root = project_root / "src/modeling/specifications"
    found = {path.name.removesuffix(".gnn.md") for path in root.glob("*.gnn.md")}
    if (catalog.get("schema") != "realizing_emptiness.gnn_catalog.v1" or not required
            or len(required) != len(catalog["models"]) or found != set(required)):
        raise ValueError("GNN catalog and specification inventory differ")
    for name in ("modeling.registry", "modeling.audit"):
        declared = project_root / Path("src", *name.split(".")).with_suffix(".py")
        if _file_hash(declared) != _file_hash(Path(inspect.getfile(import_module(name)))):
            raise ValueError("audited admission implementation differs from its executing source")
    upstream = _upstream(project_root)
    rows, native = [], []
    with specification_root(root):
        models = [load_model(model_id) for model_id in sorted(required)]
        if {model.model_id for model in models if model.backend == "pymdp"} != _PROFILES:
            raise ValueError("categorical profile coverage differs from the explicit runtime binding")
        profile_ids = load_model("qrf_boundary").parameters["profile_ids"]
        if set(profile_ids) != _PROFILES or len(profile_ids) != len(_PROFILES):
            raise ValueError("QRF runtime selector does not cover every categorical profile")
        for model in models:
            if model.consumer != required[model.model_id]:
                raise ValueError("declared GNN consumer differs from curated catalog")
            rows.append({"model_id": model.model_id, "path": f"src/modeling/specifications/{model.model_id}.gnn.md",
                         "sha256": model.source_hash, "family": model.family, "backend": model.backend,
                         "consumer": model.consumer, "parameters_sha256": _digest(model.parameters),
                         "tensors_sha256": _digest(model.tensors), **_consumer_binding(model, project_root)})
            if model.backend == "pymdp":
                native.append(_native_probe(model))
        reference = load_model("separation_constrained")
        content = (root / "separation_constrained.gnn.md").read_text()
        controls = _admission_controls(content, reference.model_id)
        baseline = next(row for row in native if row["model_id"] == reference.model_id)
        changed_c = _native_probe(parse_model(_replace_parameter(content, "C", list(reversed(reference.tensors["C"]))), reference.model_id))
        changed_d = _native_probe(parse_model(_replace_parameter(content, "D", np.roll(reference.tensors["D"], 1).tolist()), reference.model_id))
        controls.update({
            "catalog_complete": found == set(required), "all_consumers_source_bound": len(rows) == len(required),
            "all_categorical_models_executed": {row["model_id"] for row in native} == _PROFILES,
            "c_mutation_changes_real_policy": not np.allclose(baseline["policy_posterior"][0], changed_c["policy_posterior"][0]),
            "d_mutation_changes_real_posterior": not np.allclose(baseline["beliefs"][0], changed_d["beliefs"][0]),
        })
    return {
        "schema": "realizing_emptiness.gnn_model_audit.v1", "catalog_sha256": _file_hash(catalog_path),
        "registry_sha256": _file_hash(project_root / "src/modeling/registry.py"),
        "audit_sha256": _file_hash(project_root / "src/modeling/audit.py"),
        "upstream": upstream, "model_count": len(rows), "models": rows, "native_probes": native,
        "mutation_probes": {"C": changed_c, "D": changed_d}, "controls": controls,
        "all_controls_pass": all(controls.values()), "claim_boundary": CLAIM_BOUNDARY,
    }


def _equivalent(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and actual.keys() == expected.keys() and all(_equivalent(actual[key], value) for key, value in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(_equivalent(a, b) for a, b in zip(actual, expected, strict=True))
    if isinstance(expected, float):
        return type(actual) in (float, int) and bool(np.isfinite(actual) and np.isclose(actual, expected, rtol=1e-6, atol=1e-7))
    return type(actual) is type(expected) and actual == expected


def gnn_model_audit_matches(payload: dict[str, Any], project_root: Path) -> bool:
    """Reject missing, forged, stale, or non-reproducible receipts by independent reconstruction."""
    if not isinstance(payload, dict) or payload.get("schema") != "realizing_emptiness.gnn_model_audit.v1" or payload.get("all_controls_pass") is not True:
        return False
    try:
        expected = build_gnn_model_audit(project_root)
        return expected["all_controls_pass"] is True and _equivalent(payload, expected)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, SyntaxError, RuntimeError, OverflowError):
        return False
