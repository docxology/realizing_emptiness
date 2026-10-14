from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pytest
import yaml
import numpy as np

from formalism.compose import compose
from formalism.source import verify_primary_source_hash
from gates.manuscript_variables import hydrate_manuscript
from gates.validation import _load_json, _schema_check, validate_outputs
from formalism.models import BoundaryScreen, QRFDeployment, complexity_kl, vfe_noise_insufficient_learning
from simulation.qrf_env import default_deployments


def test_figure_export_binds_the_raster_backend() -> None:
    import subprocess
    import sys
    result = subprocess.run(
        [sys.executable, "-c", "import matplotlib; matplotlib.use('svg'); import visualizations.figures; assert matplotlib.get_backend().lower() == 'agg'"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_kl_with_tiny_positive_prior_stays_finite() -> None:
    assert complexity_kl(np.array([0.5, 0.5]), np.array([1e-320, 1.0])) == pytest.approx(530.5085032126528)


def test_branching_null_shuffles_each_real_series() -> None:
    from simulation.criticality import _branching_observations
    observations = [0] * 8 + [1] * 8 + [2] * 8
    rows = [{"profile": "test", "run_index": 0, "step": i, "observation": obs,
             "null_control": False} for i, obs in enumerate(observations)]
    payload = {"seed": 192, "rows": rows}
    series = _branching_observations(payload)
    real = series[("test", 0, False)]
    null = series[("test", 0, True)]
    assert np.array_equal(real, observations)
    assert np.array_equal(np.sort(real), np.sort(null))
    assert not np.array_equal(real, null)
    assert np.array_equal(_branching_observations(payload)[("test", 0, True)], null)
    payload["rows"] += [{**row, "null_control": True, "observation": 99} for row in rows]
    assert np.array_equal(_branching_observations(payload)[("test", 0, True)], null)


@pytest.mark.parametrize("schema_text", ["{", "{}", "[]", '{"type": "invalid"}'])
def test_invalid_schema_cannot_certify_an_artifact(tmp_path: Path, schema_text: str) -> None:
    (tmp_path / "schema.json").write_text(schema_text, encoding="utf-8")
    (tmp_path / "artifact.json").write_text("{}", encoding="utf-8")
    assert _schema_check(tmp_path, "schema.json", "artifact.json", "json") is False


def test_valid_schema_accepts_positive_control_and_rejects_corruption(tmp_path: Path) -> None:
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object",
              "required": ["value"], "properties": {"value": {"type": "integer"}}}
    (tmp_path / "schema.json").write_text(json.dumps(schema), encoding="utf-8")
    target = tmp_path / "artifact.json"
    target.write_text('{"value": 3}', encoding="utf-8")
    assert _schema_check(tmp_path, "schema.json", "artifact.json", "json") is True
    for text in ('{"value": "three"}', "{", "[]", "null"):
        target.write_text(text, encoding="utf-8")
        assert _schema_check(tmp_path, "schema.json", "artifact.json", "json") is False


def test_gated_loader_rejects_malformed_nested_rows(pytestconfig, tmp_path: Path) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    shutil.copytree(root / "schemas", tmp_path / "schemas")
    relative = "output/data/qrf_boundary_channel_ledger.json"
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    payload = json.loads((root / relative).read_text(encoding="utf-8"))
    target.write_text(json.dumps(payload), encoding="utf-8")
    assert _load_json(tmp_path, relative)["channel_count"] == 6
    payload["rows"] = None
    target.write_text(json.dumps(payload), encoding="utf-8")
    assert _load_json(tmp_path, relative) == {}


def test_source_digest_cannot_be_redefined_by_manifest(pytestconfig, tmp_path: Path) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    manifest_path = tmp_path / "data/sources/source_manifest.yaml"
    manifest_path.parent.mkdir(parents=True)
    manifest = yaml.safe_load((root / "data/sources/source_manifest.yaml").read_text(encoding="utf-8"))
    source = tmp_path / manifest["primary_source"]["local_pdf"]
    source.parent.mkdir(parents=True)
    source.write_bytes(b"replacement source")
    manifest["primary_source"]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    assert verify_primary_source_hash(tmp_path)["ok"] is False


def test_validation_only_is_read_only_and_detects_stale_composition(pytestconfig, tmp_path: Path) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    shutil.copytree(root / "docs", tmp_path / "docs")
    shutil.copy2(root / "figures.yaml", tmp_path / "figures.yaml")
    (tmp_path / "output").mkdir()
    (tmp_path / "output/figures").symlink_to(root / "output/figures", target_is_directory=True)
    compose(tmp_path, validate_only=True, strict=True)
    assert not (tmp_path / "output/data").exists()
    target = tmp_path / "docs/manuscript/03_results.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nUncomposed edit.\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="stale composed manuscript"):
        compose(tmp_path, validate_only=True, strict=True)


def test_hydration_rebases_figures_and_preserves_unmanaged_files(tmp_path: Path) -> None:
    source = tmp_path / "docs/manuscript"
    target = tmp_path / "output/manuscript"
    source.mkdir(parents=True)
    target.mkdir(parents=True)
    (source / "00_abstract.md").write_text("Count {{COUNT}}. ![x](../../output/figures/a.png)", encoding="utf-8")
    (source / "README.md").write_text("Editor guide", encoding="utf-8")
    (source / "AGENTS.md").write_text("Agent guide", encoding="utf-8")
    (source / "MANUSCRIPT_STATUS.md").write_text("Editor status", encoding="utf-8")
    (target / "notes.txt").write_text("Keep", encoding="utf-8")
    (target / "MANUSCRIPT_STATUS.md").write_text("Old generated status", encoding="utf-8")
    hydrate_manuscript(tmp_path, {"COUNT": 7})
    assert (target / "00_abstract.md").read_text(encoding="utf-8") == "Count 7. ![x](../figures/a.png)"
    assert (target / "notes.txt").read_text(encoding="utf-8") == "Keep"
    assert not (target / "README.md").exists()
    assert not (target / "AGENTS.md").exists()
    assert not (target / "MANUSCRIPT_STATUS.md").exists()


@pytest.mark.parametrize("channels", [1, 2, 7])
def test_every_default_deployment_matches_requested_screen(channels: int) -> None:
    screen = BoundaryScreen.default(channels)
    for deployment in default_deployments(channels):
        deployment.validate(screen)


@pytest.mark.parametrize("precision", [float("nan"), float("inf"), -1.0])
def test_deployment_rejects_invalid_precision(precision: float) -> None:
    deployment = QRFDeployment("invalid", ("self",), 0.5, precision)
    with pytest.raises(ValueError, match="precision"):
        deployment.validate(BoundaryScreen.default(1))


@pytest.mark.parametrize("base", [0.0, 0.5, 1.0, float("nan"), float("inf")])
def test_information_measures_reject_invalid_logarithm_base(base: float) -> None:
    for compute in (complexity_kl, vfe_noise_insufficient_learning):
        with pytest.raises(ValueError, match="base"):
            compute(np.array([0.8, 0.2]), np.array([0.5, 0.5]), base=base)


def test_reference_audit_rejects_unknown_citations_and_missing_figures(pytestconfig, tmp_path: Path) -> None:
    from gates.manuscript import build_manuscript_reference_audit

    root: Path = pytestconfig.realizing_emptiness_root
    shutil.copytree(root / "docs", tmp_path / "docs")
    (tmp_path / "output").mkdir()
    (tmp_path / "output/figures").symlink_to(root / "output/figures", target_is_directory=True)
    assert build_manuscript_reference_audit(tmp_path)["ok"] is True
    abstract = tmp_path / "docs/manuscript/00_abstract.md"
    abstract.write_text(abstract.read_text(encoding="utf-8") + "\n[@unknown2026]. ![missing](../../output/figures/absent.png)\n", encoding="utf-8")
    audit = build_manuscript_reference_audit(tmp_path)
    assert audit["ok"] is False
    assert audit["unknown_citations"] == ["unknown2026"]
    assert audit["missing_images"] == ["docs/manuscript/00_abstract.md::../../output/figures/absent.png"]


@pytest.mark.parametrize("relative", ["artifact_manifest.yaml", "data/sources/source_manifest.yaml", "data/sources/scholarship_manifest.yaml"])
def test_validator_reports_malformed_input_manifests(pytestconfig, tmp_path: Path, relative: str) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    shutil.copytree(root / "schemas", tmp_path / "schemas")
    for name in ("artifact_manifest.yaml", "data/sources/source_manifest.yaml", "data/sources/scholarship_manifest.yaml"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(root / name, target)
    (tmp_path / relative).write_text("[", encoding="utf-8")
    checks = validate_outputs(tmp_path)
    assert checks[f"schema_valid:{relative}"] is False
    assert not all(checks.values())


def test_corrupt_png_is_a_failed_integrity_result(tmp_path: Path) -> None:
    from visualizations.integrity import build_figure_integrity_audit

    image = tmp_path / "output/figures/corrupt.png"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"broken PNG")
    source_map = {"figure_count": 1, "figures": [{"id": "corrupt", "path": "output/figures/corrupt.png", "source_artifacts": []}]}
    audit = build_figure_integrity_audit(tmp_path, source_map)
    assert audit["ok"] is False
    assert audit["blank_figures"] == ["corrupt"]


def test_missing_visual_telemetry_fails_and_font_measurement_is_observed(tmp_path: Path) -> None:
    import matplotlib.pyplot as plt
    from visualizations.figures import _LAYOUT_TELEMETRY, _empty_layout_telemetry, _save

    assert _empty_layout_telemetry()["layout_ok"] is False
    figure, axes = plt.subplots()
    axes.text(0.5, 0.5, "Small input label", fontsize=4)
    path = tmp_path / "measured.png"
    _save(figure, path, 120)
    assert path.is_file()
    assert _LAYOUT_TELEMETRY["measured"]["measured_min_font_pt"] >= 12


def test_dependencies_come_from_the_selected_runtime() -> None:
    import sys
    import matplotlib
    import PIL

    prefix = Path(sys.prefix).resolve()
    for module in (np, matplotlib, PIL, yaml):
        assert Path(module.__file__).resolve().is_relative_to(prefix), f"{module.__name__} loaded from {module.__file__}, outside {prefix}"


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity", "1e999", "-1e999"])
def test_nonfinite_json_constants_cannot_pass_number_schemas(tmp_path: Path, constant: str) -> None:
    schema = {"type": "object", "properties": {"value": {"type": "number"}}, "required": ["value"]}
    (tmp_path / "schema.json").write_text(json.dumps(schema), encoding="utf-8")
    (tmp_path / "artifact.json").write_text('{"value": ' + constant + '}', encoding="utf-8")
    assert _schema_check(tmp_path, "schema.json", "artifact.json", "json") is False
    assert _load_json(tmp_path, "artifact.json") == {}
    (tmp_path / "artifact.json").write_text('{"value": 1.25e100}', encoding="utf-8")
    assert _schema_check(tmp_path, "schema.json", "artifact.json", "json") is True
    assert _load_json(tmp_path, "artifact.json")["value"] == 1.25e100


def test_chain_bootstraps_without_existing_outputs(pytestconfig, tmp_path: Path) -> None:
    import subprocess
    import sys

    root: Path = pytestconfig.realizing_emptiness_root
    work = tmp_path / "source-only"
    shutil.copytree(root, work, ignore=shutil.ignore_patterns(
        ".git", ".venv", "output", "__pycache__", ".pytest_cache", ".coverage*", "*.egg-info", "build", "dist", "realizing_emptiness_combined.pdf",
    ))
    assert not (work / "output").exists()
    result = subprocess.run([sys.executable, "scripts/run_full_chain.py"], cwd=work, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    variables = json.loads((work / "output/data/manuscript_variables.json").read_text(encoding="utf-8"))
    checks = validate_outputs(work)
    assert all(checks.values()), [name for name, ok in checks.items() if not ok]
    assert variables["VALIDATION_PASS_COUNT"] == variables["VALIDATION_TOTAL_COUNT"] == len(checks)
