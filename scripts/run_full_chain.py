#!/usr/bin/env python3
"""Run the deterministic Realizing Emptiness artifact chain."""

from __future__ import annotations

import subprocess
import sys

from _bootstrap import PROJECT_ROOT


COMMANDS = [
    [sys.executable, "scripts/generate_formalisms.py"],
    [sys.executable, "scripts/simulate_boundary_agents.py"],
    [sys.executable, "scripts/generate_quantum_surrogates.py"],
    [sys.executable, "scripts/generate_extended_surrogates.py"],
    [sys.executable, "scripts/run_bmr_sweep.py"],
    [sys.executable, "scripts/generate_statistics.py"],
    [sys.executable, "scripts/generate_sheaf_tracks.py"],
    [sys.executable, "scripts/generate_figures.py"],
    [sys.executable, "scripts/compose_manuscript.py"],
    [sys.executable, "scripts/generate_method_inventory.py"],
    [sys.executable, "scripts/generate_equation_crosswalk.py"],
    [sys.executable, "scripts/generate_dashboard.py"],
    [sys.executable, "scripts/generate_review_response_artifacts.py"],
    [sys.executable, "scripts/z_generate_manuscript_variables.py"],
    [sys.executable, "scripts/generate_review_response_artifacts.py"],
    [sys.executable, "scripts/validate_outputs.py"],
]


def main() -> int:
    for command in COMMANDS:
        print("$", " ".join(command))
        result = subprocess.run(command, cwd=PROJECT_ROOT, check=False)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
