#!/usr/bin/env python3
"""Generate all project figures."""

from __future__ import annotations

from _bootstrap import PROJECT_ROOT
from visualizations.figures import generate_all_figures


def main() -> int:
    generate_all_figures(PROJECT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

