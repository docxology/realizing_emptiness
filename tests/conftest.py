"""Pytest fixtures for Realizing Emptiness."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("MPLBACKEND", "Agg")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def pytest_configure(config):
    """Expose project root for tests without importing project scripts."""
    config.realizing_emptiness_root = PROJECT_ROOT


# Tests that build the whole chain in their own temporary source copy never
# touch the checkout's ``output/`` tree, so they can run beside the rest.
ISOLATED_TREE_TESTS = frozenset(
    {
        "tests/test_release_contracts.py::test_chain_bootstraps_without_existing_outputs",
    }
)


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    """Keep tests that share the checkout's ``output/`` tree on one worker.

    Most tests read or regenerate artifacts under ``output/`` in place, so under
    ``pytest-xdist --dist loadgroup`` they stay in collection order on a single
    worker; only tests in ``ISOLATED_TREE_TESTS`` are scheduled independently.
    ``tryfirst`` matters: xdist reads ``xdist_group`` markers in its own
    collection hook. Without xdist the marker is inert and the run is unchanged.
    """
    for item in items:
        if item.nodeid not in ISOLATED_TREE_TESTS:
            item.add_marker(pytest.mark.xdist_group("project-output-tree"))
