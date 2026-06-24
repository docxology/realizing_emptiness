from __future__ import annotations

from pathlib import Path

from formalism.review_response_bmr import build_bmr_alternative_prior_audit
from formalism.review_response_common import LOCAL_RELEASE_BOUNDARY, json_write
from formalism.review_response_external import build_external_review_response_audit
from formalism.review_response_figures import build_figure_parameter_ledger
from formalism.review_response_qrf import build_qrf_label_ablation_audit
from formalism.review_response_quantum import build_quantum_independent_crosscheck_audit
from formalism.review_response_release import write_artifact_release_manifest


def write_review_response_artifacts(project_root: Path) -> dict[str, Path]:
    data_dir = project_root / "output" / "data"
    paths = {
        "figure_parameter_ledger": json_write(
            data_dir / "figure_parameter_ledger.json",
            build_figure_parameter_ledger(project_root),
        ),
        "qrf_label_ablation_audit": json_write(
            data_dir / "qrf_label_ablation_audit.json",
            build_qrf_label_ablation_audit(project_root),
        ),
        "quantum_independent_crosscheck_audit": json_write(
            data_dir / "quantum_independent_crosscheck_audit.json",
            build_quantum_independent_crosscheck_audit(project_root),
        ),
        "bmr_alternative_prior_audit": json_write(
            data_dir / "bmr_alternative_prior_audit.json",
            build_bmr_alternative_prior_audit(),
        ),
    }
    release_path = data_dir / "artifact_release_manifest.json"
    json_write(
        release_path,
        {
            "schema": "realizing_emptiness.artifact_release_manifest.v1",
            "provisional": True,
            "claim_boundary": LOCAL_RELEASE_BOUNDARY,
        },
    )
    paths["external_review_response_audit"] = json_write(
        data_dir / "external_review_response_audit.json",
        build_external_review_response_audit(project_root),
    )
    from gates.contracts import write_artifact_contract_registry

    write_artifact_contract_registry(project_root)
    paths["artifact_release_manifest"] = write_artifact_release_manifest(project_root)
    return paths
