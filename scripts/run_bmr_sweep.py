#!/usr/bin/env python3
"""Write Bayesian model-reduction sweep artifacts."""

from __future__ import annotations

from _bootstrap import PROJECT_ROOT
from simulation.bmr import write_bmr_sweep


def main() -> int:
    write_bmr_sweep(PROJECT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

