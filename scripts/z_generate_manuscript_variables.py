#!/usr/bin/env python3
"""Generate manuscript variables and hydrated manuscript copies."""

from __future__ import annotations

import json

from _bootstrap import PROJECT_ROOT
from gates.manuscript_variables import compute_variables, hydrate_manuscript


def main() -> int:
    variables = compute_variables(PROJECT_ROOT)
    data_dir = PROJECT_ROOT / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "manuscript_variables.json").write_text(
        json.dumps(variables, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    hydrate_manuscript(PROJECT_ROOT, variables)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
