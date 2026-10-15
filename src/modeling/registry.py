"""Admit GNN declarations before model parameters reach any numerical backend."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from importlib.resources import files
import json
import math
from pathlib import Path
import re
from typing import Any, Iterator

from gnn.parsers.markdown_parser import MarkdownGNNParser
from gnn.validation.semantic_validator import SemanticValidator


CLAIM_BOUNDARY = "GNN specifications and finite software execution only; not empirical, clinical, neural, practice-efficacy, or physical qFEP evidence"
_SPECIFICATION_ROOT: ContextVar[Path | None] = ContextVar("gnn_specification_root", default=None)
_REQUIRED = ("GNNSection", "GNNVersionAndFlags", "ModelName", "ModelAnnotation", "StateSpaceBlock", "Connections", "InitialParameterization")
_ALLOWED = set(_REQUIRED) | {"Time", "ActInfOntologyAnnotation", "ModelParameters", "Equations", "Footer"}
_SETTINGS = {"family", "backend", "consumer", "parameters", "claim_boundary"}


@dataclass(frozen=True)
class ModelSpecification:
    """A source-bound declaration admitted by upstream and project contracts."""

    model_id: str
    source_hash: str
    family: str
    backend: str
    consumer: str
    parameters: dict[str, Any]
    tensors: dict[str, Any]


def upstream_identity() -> dict[str, str]:
    return json.loads(files("modeling").joinpath("upstream.json").read_text(encoding="utf-8"))


@contextmanager
def specification_root(root: Path) -> Iterator[None]:
    """Select real alternate specification files for controlled experiments and tests."""
    token = _SPECIFICATION_ROOT.set(Path(root).resolve())
    try:
        yield
    finally:
        _SPECIFICATION_ROOT.reset(token)


def specification_paths() -> list[Path]:
    root = _SPECIFICATION_ROOT.get() or Path(str(files("modeling").joinpath("specifications")))
    paths = sorted(root.glob("*.gnn.md"))
    if not paths:
        raise ValueError("GNN model inventory is empty")
    return paths


def _finite_tree(value: Any) -> bool:
    if isinstance(value, dict):
        return all(isinstance(key, str) and _finite_tree(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return all(_finite_tree(item) for item in value)
    if isinstance(value, float):
        return math.isfinite(value)
    return value is None or isinstance(value, (str, int, bool))


def _validate_blackwell_parameters(parameters: dict[str, Any]) -> None:
    if set(parameters) != {"prior", "channel", "grid_steps", "named_garblings"}:
        raise ValueError("Blackwell requires its complete finite decision contract")

    def probability(value: Any) -> bool:
        return type(value) in {int, float} and 0 <= value <= 1 and math.isfinite(value)

    def distribution(value: Any) -> bool:
        return (isinstance(value, list) and len(value) == 2 and all(probability(item) for item in value)
                and math.isclose(sum(value), 1.0, rel_tol=0, abs_tol=1e-12))

    if not distribution(parameters["prior"]):
        raise ValueError("Blackwell prior must be a normalized binary probability distribution")
    channel = parameters["channel"]
    if not isinstance(channel, list) or len(channel) != 2 or not all(distribution(row) for row in channel):
        raise ValueError("Blackwell channel must be a binary row-stochastic probability matrix")
    if type(parameters["grid_steps"]) is not int or parameters["grid_steps"] < 2:
        raise ValueError("Blackwell grid_steps must be an integer of at least two")
    garblings = parameters["named_garblings"]
    if (not isinstance(garblings, list) or not garblings
            or any(not isinstance(row, list) or len(row) != 3
                   or not isinstance(row[0], str) or not row[0]
                   or not all(probability(item) for item in row[1:]) for row in garblings)):
        raise ValueError("Blackwell named garblings require names and probability retentions")
    names = [row[0] for row in garblings]
    if len(names) != len(set(names)) or not {"partial_garbling", "complete_erasure"} <= set(names):
        raise ValueError("Blackwell garblings require unique names and both mathematical controls")


def parse_model(content: str, model_id: str) -> ModelSpecification:
    """Reject lossy parser recovery, then consume the actual upstream typed IR."""
    headings = re.findall(r"^## (.+)$", content, flags=re.MULTILINE)
    if len(headings) != len(set(headings)) or not set(headings) <= _ALLOWED:
        raise ValueError("duplicate or unsupported GNN section")
    if tuple(name for name in headings if name in _REQUIRED) != _REQUIRED:
        raise ValueError("missing or unordered required GNN sections")
    parsed = MarkdownGNNParser().parse_string(content)
    if not parsed.success or parsed.errors or parsed.warnings:
        raise ValueError(f"GNN parsing failed: {parsed.errors + parsed.warnings}")
    ir = parsed.model
    if ir.model_name != model_id or ir.raw_sections["GNNVersionAndFlags"].strip() != "GNN v1":
        raise ValueError("GNN identity/version mismatch")
    semantic = SemanticValidator("strict").validate(content)
    if not semantic["is_valid"]:
        raise ValueError(f"GNN semantic validation failed: {semantic['errors']}")
    declaration_lines = [line.strip() for line in ir.raw_sections["StateSpaceBlock"].splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not declaration_lines or any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*\[(?:[1-9][0-9]*,)*[1-9][0-9]*,type=(?:float|int)\]", line) for line in declaration_lines):
        raise ValueError("GNN variables require concrete positive dimensions and supported types")
    names = [variable.name for variable in ir.variables]
    if len(names) != len(set(names)) or len(names) != len(declaration_lines):
        raise ValueError("duplicate or unparsed GNN variable")
    connection_lines = [line for line in ir.raw_sections["Connections"].splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not ir.connections or len(connection_lines) != len(ir.connections):
        raise ValueError("GNN connections must all parse")
    parameter_lines = [line for line in ir.raw_sections["InitialParameterization"].splitlines() if line.strip() and not line.lstrip().startswith("#")]
    parameters = {parameter.name: parameter.value for parameter in ir.parameters}
    if len(parameters) != len(ir.parameters) or len(parameter_lines) != len(ir.parameters):
        raise ValueError("GNN parameters must be unique complete single-line assignments")
    settings = parameters.pop("settings", None)
    if not isinstance(settings, list) or len(settings) != 1 or not isinstance(settings[0], dict) or set(settings[0]) != _SETTINGS:
        raise ValueError("GNN settings require the complete model execution contract")
    settings = settings[0]
    if (not all(isinstance(settings[key], str) and settings[key] for key in _SETTINGS - {"parameters"})
            or not isinstance(settings["parameters"], dict) or not settings["parameters"]
            or "not empirical" not in settings["claim_boundary"] or not _finite_tree(settings)):
        raise ValueError("GNN model contract has invalid metadata or nonfinite parameters")
    if settings["backend"] not in {"pymdp", "numpy_scipy"}:
        raise ValueError("unsupported GNN numerical backend")
    section = ir.raw_sections["GNNSection"].strip()
    if settings["backend"] == "pymdp":
        if section != "ActInfPOMDP" or set(parameters) != {"A", "B", "C", "D"}:
            raise ValueError("pymdp requires an explicit complete categorical GNN model")
        from gnn.render.pomdp_contract import build_canonical_pomdp_spec

        dimensions = {variable.name: variable.dimensions for variable in ir.variables}
        if not all(key in dimensions for key in parameters):
            raise ValueError("categorical tensors must be declared")
        import numpy as np

        if any(list(np.asarray(value).shape) != dimensions[key] for key, value in parameters.items()):
            raise ValueError("declared and actual GNN tensor dimensions differ")
        canonical = build_canonical_pomdp_spec({"model_name": model_id, "model_parameters": {"b_tensor_order": "next_state_previous_state_action"}, "initialparameterization": parameters})
        tensors = canonical["initialparameterization"]
    elif section != "FiniteSurrogate" or parameters:
        raise ValueError("finite native models require the explicit FiniteSurrogate contract")
    else:
        tensors = {}
        if model_id == "finite_blackwell":
            _validate_blackwell_parameters(settings["parameters"])
    return ModelSpecification(model_id, sha256(content.encode()).hexdigest(), settings["family"], settings["backend"], settings["consumer"], deepcopy(settings["parameters"]), deepcopy(tensors))


@lru_cache(maxsize=256)
def _parse_cached(content: str, model_id: str) -> ModelSpecification:
    return parse_model(content, model_id)


def load_model(model_id: str) -> ModelSpecification:
    if not re.fullmatch(r"[a-z][a-z0-9_]*", model_id):
        raise ValueError("invalid GNN model identifier")
    root = _SPECIFICATION_ROOT.get() or Path(str(files("modeling").joinpath("specifications")))
    content = (root / f"{model_id}.gnn.md").read_text(encoding="utf-8")
    return deepcopy(_parse_cached(content, model_id))


def model_parameters(model_id: str) -> dict[str, Any]:
    return load_model(model_id).parameters
