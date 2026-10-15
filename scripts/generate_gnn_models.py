"""Generate the GNN source and native-execution audit."""

import json

from _bootstrap import PROJECT_ROOT
from modeling.audit import build_gnn_model_audit


def main() -> int:
    payload = build_gnn_model_audit(PROJECT_ROOT)
    path = PROJECT_ROOT / "output/data/gnn_model_audit.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return 0 if payload["all_controls_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
