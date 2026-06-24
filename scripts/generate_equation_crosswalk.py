#!/usr/bin/env python3
"""Generate or check the paper-to-software equation crosswalk doc.

Thin orchestrator: renders ``docs/equation-crosswalk.md`` from the
generated ``output/data/formalism_registry.json`` so the crosswalk cannot drift
from the registry. Mirrors the ``--check`` drift-guard used by the method inventory.
"""

from __future__ import annotations

import argparse
import json

from _bootstrap import PROJECT_ROOT
from formalism.equations import render_equation_crosswalk


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry_path = PROJECT_ROOT / "output" / "data" / "formalism_registry.json"
    if not registry_path.exists():
        print("formalism_registry.json missing; run scripts/generate_formalisms.py first")
        return 1
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    output = PROJECT_ROOT / "docs" / "equation-crosswalk.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    text = render_equation_crosswalk(registry)
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != text:
            print("equation crosswalk is stale; run scripts/generate_equation_crosswalk.py")
            return 1
        print("Equation crosswalk is current.")
        return 0
    output.write_text(text, encoding="utf-8")
    print(f"Wrote {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
