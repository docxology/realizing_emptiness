#!/usr/bin/env python3
"""Generate finite quantum-information surrogate artifacts."""

from __future__ import annotations

from _bootstrap import PROJECT_ROOT
from simulation.quantum_surrogates import write_quantum_artifacts


def main() -> int:
    write_quantum_artifacts(PROJECT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
