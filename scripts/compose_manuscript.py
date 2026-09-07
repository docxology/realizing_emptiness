#!/usr/bin/env python3
"""Compose top-level manuscript files from sheaf fragments."""

from __future__ import annotations

import argparse

from _bootstrap import PROJECT_ROOT
from formalism.compose import compose


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    compose(PROJECT_ROOT, validate_only=args.validate_only, strict=args.strict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
