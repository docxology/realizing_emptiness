#!/usr/bin/env python3

from __future__ import annotations

import json

from _bootstrap import PROJECT_ROOT
from formalism.claim_redteam import write_claim_redteam_audit
from formalism.review_response import write_artifact_release_manifest, write_review_response_artifacts
from visualizations.dashboard import write_artifact_dashboard


def main() -> int:
    write_review_response_artifacts(PROJECT_ROOT)
    write_claim_redteam_audit(PROJECT_ROOT)
    source_map = json.loads((PROJECT_ROOT / "output" / "data" / "figure_source_map.json").read_text(encoding="utf-8"))
    write_artifact_dashboard(PROJECT_ROOT, source_map)
    write_artifact_release_manifest(PROJECT_ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
