#!/usr/bin/env python3
"""Generate manuscript variables and hydrated manuscript copies."""

from __future__ import annotations

import argparse
import json

from _bootstrap import PROJECT_ROOT
from gates.manuscript_variables import (
    compute_variables,
    hydrate_manuscript,
    write_template_figure_registry,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--retained-variables",
        action="store_true",
        help="Use values from the retained analysis instead of recomputing validation counts.",
    )
    args = parser.parse_args()
    data_dir = PROJECT_ROOT / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    variables_file = data_dir / "manuscript_variables.json"
    if args.retained_variables:
        variables = json.loads(variables_file.read_text(encoding="utf-8"))
    else:
        variables = compute_variables(PROJECT_ROOT)
        variables_file.write_text(
            json.dumps(variables, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    hydrate_manuscript(PROJECT_ROOT, variables)
    write_template_figure_registry(PROJECT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
