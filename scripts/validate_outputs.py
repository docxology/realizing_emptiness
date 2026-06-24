#!/usr/bin/env python3
"""Validate generated project outputs."""

from __future__ import annotations

from _bootstrap import PROJECT_ROOT
from gates.validation import validate_outputs, write_validation_report


def main() -> int:
    checks = validate_outputs(PROJECT_ROOT)
    write_validation_report(PROJECT_ROOT)
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print("Failed checks:")
        for name in failed:
            print(f"- {name}")
        return 1
    print(f"All {len(checks)} output checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

