#!/usr/bin/env python3
"""Generate or check a simple method inventory."""

from __future__ import annotations

import argparse

from _bootstrap import PROJECT_ROOT
from gates.method_inventory import collect_entries, render


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = PROJECT_ROOT / "docs" / "method-inventory.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    text = render(collect_entries(PROJECT_ROOT))
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != text:
            print("method inventory is stale")
            return 1
        print("Method inventory is current.")
        return 0
    output.write_text(text, encoding="utf-8")
    print(f"Wrote {output.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
