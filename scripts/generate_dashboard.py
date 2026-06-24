#!/usr/bin/env python3
"""Refresh the static artifact dashboard from existing source maps."""

from __future__ import annotations

import json

from _bootstrap import PROJECT_ROOT
from visualizations.dashboard import write_artifact_dashboard


def main() -> int:
    source_map = json.loads((PROJECT_ROOT / "output" / "data" / "figure_source_map.json").read_text(encoding="utf-8"))
    write_artifact_dashboard(PROJECT_ROOT, source_map)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
