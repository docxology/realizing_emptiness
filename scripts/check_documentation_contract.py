#!/usr/bin/env python3
"""Check local documentation contract."""

from __future__ import annotations

import argparse

from _bootstrap import PROJECT_ROOT
from gates.validation import check_documentation_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    issues = check_documentation_contract(PROJECT_ROOT)
    if issues:
        for issue in issues:
            print(issue)
        return 1 if args.check else 0
    print("Documentation contract passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

