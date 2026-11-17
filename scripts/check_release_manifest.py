#!/usr/bin/env python3
"""Check that the recorded release manifest matches the files on disk.

Read-only. CI runs it before the tests, because the test suite regenerates
outputs in place and would otherwise hide a stale committed manifest.
"""

from __future__ import annotations

from _bootstrap import PROJECT_ROOT
from formalism.review_response_release import RELEASE_MANIFEST_PATH, release_manifest_drift


def main() -> int:
    drift = release_manifest_drift(PROJECT_ROOT)
    if drift:
        print(f"{RELEASE_MANIFEST_PATH} does not match the files on disk:")
        for line in drift:
            print(f"- {line}")
        print("Regenerate outputs with `uv run python scripts/run_full_chain.py` and commit them.")
        return 1
    print(f"{RELEASE_MANIFEST_PATH} matches the files on disk.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
