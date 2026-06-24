#!/usr/bin/env python3
"""Generate statistical robustness audits."""

from __future__ import annotations

from _bootstrap import PROJECT_ROOT
from simulation.statistical_robustness import write_statistical_robustness_artifacts


def main() -> int:
    write_statistical_robustness_artifacts(PROJECT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
