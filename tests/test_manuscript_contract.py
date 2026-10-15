import shutil

import pytest

from formalism.compose import compose
from gates.manuscript import build_figure_placement_audit


@pytest.fixture
def manuscript_tree(pytestconfig, tmp_path):
    root = pytestconfig.realizing_emptiness_root
    shutil.copytree(root / "docs/manuscript", tmp_path / "docs/manuscript")
    shutil.copyfile(root / "figures.yaml", tmp_path / "figures.yaml")
    (tmp_path / "output").symlink_to(root / "output", target_is_directory=True)
    return tmp_path


def test_strict_composition_rejects_unselected_fragments_without_writing(manuscript_tree):
    root = manuscript_tree
    before = {path: path.read_bytes() for path in (root / "docs/manuscript").glob("0*.md")}
    assert compose(root, validate_only=True, strict=True)["ok"]
    fragment = root / "docs/manuscript/sections/supplement/unselected.md"
    fragment.write_text("An unselected manuscript fragment.\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="unselected fragment"):
        compose(root, validate_only=True, strict=True)
    assert all(path.read_bytes() == content for path, content in before.items())


def test_figure_placement_requires_registered_images(manuscript_tree):
    root = manuscript_tree
    assert build_figure_placement_audit(root)["ok"]
    target = root / "docs/manuscript/02_methods.md"
    target.write_text(target.read_text(encoding="utf-8") +
                      "\n![Unregistered](../../output/figures/unregistered.png)\n", encoding="utf-8")
    failed = build_figure_placement_audit(root)
    assert failed["ok"] is False
    assert failed["controls"]["all_embedded_figures_registered"] is False
    assert failed["unregistered_figure_paths"] == ["../../output/figures/unregistered.png"]
