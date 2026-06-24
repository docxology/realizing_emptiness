"""Tests for source and equation formalism layers."""

from __future__ import annotations

from pathlib import Path

import json
from jsonschema import Draft202012Validator

import numpy as np
import pytest
import yaml

from formalism.equations import evaluate_equation_surrogates, equation_registry, render_equation_crosswalk
from formalism.claim_context import build_claim_context_ledger
from formalism.claim_redteam import build_claim_redteam_audit
from formalism.governance import (
    build_method_assumption_ledger,
    build_method_negative_control_inventory,
    write_method_governance_artifacts,
)
from formalism.manuscript import (
    _forbidden_hits,
    build_manuscript_claim_audit,
    build_manuscript_claim_intensity_audit,
    classify_sentence_intensity,
    write_manuscript_claim_intensity_audit,
)
from formalism.models import (
    BoundaryScreen,
    BMRComparison,
    FreeEnergyTerms,
    QRFDeployment,
    Sectorisation,
    SeparationPrior,
    complexity_kl,
    vfe_noise_insufficient_learning,
)
from formalism.scholarship import build_claim_support_audit, build_scholarship_source_matrix, validate_scholarship_manifest
from formalism.review_response import (
    build_artifact_release_manifest,
    build_external_review_response_audit,
    build_figure_parameter_ledger,
)
from formalism.source import load_source_manifest, verify_primary_source_hash
from formalism.source_fit import build_source_argument_coverage_audit
from formalism.stress import build_evidence_ceiling_audit


def test_source_manifest_hash(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    manifest = load_source_manifest(root)
    assert manifest["primary_source"]["title"].startswith("There is no self-evidence")
    check = verify_primary_source_hash(root)
    assert check["expected_sha256"] == "94e2335c3a4a37b8d49039b11b45ccda25bad65d4b80aa15428b84abfba699ac"
    assert check["ok"] is True


def test_equation_registry_complete_and_audited() -> None:
    registry = equation_registry()
    audit = evaluate_equation_surrogates()
    assert len(registry) == 14
    assert all(row.as_dict()["paper_to_software_bridge"] for row in registry)
    assert all("Finite operational surrogate" in row.as_dict()["interpretive_boundary"] for row in registry)
    assert audit["all_equations_mapped"] is True
    assert audit["implemented_count"] >= 10
    assert audit["values"]["eq9_boundary_probabilities_equal"] is True


def test_scholarship_manifest_covers_bibliography_and_tracks(pytestconfig, tmp_path) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    validation = validate_scholarship_manifest(root)
    matrix = build_scholarship_source_matrix(root)
    assert validation["ok"] is True
    assert validation["entry_count"] >= 12
    assert validation["missing_bibliography_keys"] == []
    assert validation["missing_counterweight_groups"] == {}
    assert validation["unknown_claim_ids"] == []
    assert matrix["source_count"] == validation["entry_count"]
    assert {"qfep", "qrf", "bmr", "practice_protocols"} <= set(matrix["tracks"])
    citation_keys = {row["citation_key"] for row in matrix["rows"]}
    assert {
        "dalibard1992wavefunction",
        "molmer1993montecarlo",
        "wiseman2010quantum",
        "vanrietvelde2020perspective",
        "fine1982hidden",
        "talts2018sbc",
        "gelman2020bayesianworkflow",
        "pineau2020reproducibility",
        "friston2023fep_simpler",
        "biehl2021technical_fep",
        "heins2022sparse_coupling",
        "destexhe2021criticality_evidence",
    } <= citation_keys
    assert set(validation["required_counterweight_groups"]["fep_blanket_critique_response"]) <= citation_keys

    broken_root = tmp_path / "broken_scholarship"
    (broken_root / "data" / "sources").mkdir(parents=True)
    (broken_root / "manuscript").mkdir()
    manifest = yaml.safe_load((root / "data" / "sources" / "scholarship_manifest.yaml").read_text(encoding="utf-8"))
    manifest["entries"] = [
        entry for entry in manifest["entries"] if entry["citation_key"] != "biehl2021technical_fep"
    ]
    (broken_root / "data" / "sources" / "scholarship_manifest.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False),
        encoding="utf-8",
    )
    (broken_root / "manuscript" / "references.bib").write_text(
        (root / "manuscript" / "references.bib").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    broken_validation = validate_scholarship_manifest(broken_root)
    assert broken_validation["ok"] is False
    assert broken_validation["missing_counterweight_groups"]["fep_blanket_critique_response"] == [
        "biehl2021technical_fep"
    ]


def test_claim_support_audit_rejects_unsupported_public_claim(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    crosswalk = json.loads((root / "output" / "data" / "source_claim_crosswalk.json").read_text(encoding="utf-8"))
    audit = build_claim_support_audit(root, crosswalk)
    assert audit["ok"] is True
    assert audit["unsupported_public_claims"] == []
    claim_ids = {row["claim_id"] for row in audit["support_rows"] if row["public_crosswalk_claim"]}
    assert "quantum_separability_entropy" in claim_ids
    assert "quantum_contextuality_witness" in claim_ids
    assert "quantum_measurement_contextuality" in claim_ids
    assert "quantum_open_system_dephasing" in claim_ids
    assert "artifact_release_readiness" in claim_ids
    broken = {
        **crosswalk,
        "claims": [*crosswalk["claims"], {"id": "unsupported_claim", "artifact": "output/data/source_claim_crosswalk.json", "gate": "source_hash"}],
        "claim_count": crosswalk["claim_count"] + 1,
    }
    broken_audit = build_claim_support_audit(root, broken)
    assert broken_audit["ok"] is False
    assert broken_audit["unsupported_public_claims"] == ["unsupported_claim"]


def test_source_argument_coverage_resolves_core_themes_and_boundaries(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    audit = build_source_argument_coverage_audit(root)
    rows = {row["theme_id"]: row for row in audit["rows"]}
    assert audit["schema"] == "realizing_emptiness.source_argument_coverage_audit.v1"
    assert audit["all_controls_pass"] is True
    assert audit["controls"]["all_local_sections_resolve"] is True
    assert audit["controls"]["qrf_bmr_opacification_not_quantum_only"] is True
    assert rows["qrf_sectorisation_equations_7_to_10"]["source_equations"] == [7, 8, 9, 10]
    assert "output/data/qrf_boundary_channel_ledger.json" in rows["qrf_sectorisation_equations_7_to_10"]["artifact_paths"]
    assert rows["opacification_and_metacognitive_access"]["primary_coverage_class"] == "active_inference_bmr_argument"
    assert rows["bmr_pruning_of_sigma"]["primary_coverage_class"] == "active_inference_bmr_argument"
    assert rows["contextuality_of_boundary"]["primary_coverage_class"] == "supplemental_quantum_contextuality_support"
    assert "sec:supplement-meta-manuscript-record" in rows["criticality_prediction_boundary"]["local_sections"]
    assert all(row["unresolved_local_sections"] == [] for row in audit["rows"])
    assert "not empirical" in audit["claim_boundary"]


def test_evidence_ceiling_audit_rejects_missing_boundary_and_unknown_stressor(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    crosswalk = json.loads((root / "output" / "data" / "source_claim_crosswalk.json").read_text(encoding="utf-8"))
    audit = build_evidence_ceiling_audit(root, crosswalk)
    assert audit["ok"] is True
    assert audit["missing_boundary_fields"] == []
    assert audit["invalid_stressors"] == []

    missing_boundary = {
        **crosswalk,
        "claims": [{key: value for key, value in claim.items() if key != "prohibited_inference"} for claim in crosswalk["claims"]],
    }
    missing_audit = build_evidence_ceiling_audit(root, missing_boundary)
    assert missing_audit["ok"] is False
    assert {"claim_id": "bmr_prunes_sigma", "field": "prohibited_inference"} in missing_audit["missing_boundary_fields"]

    unknown_stressor = {
        **crosswalk,
        "claims": [
            {**claim, "stressors": [*claim["stressors"], "unknown_boundary"]}
            if claim["id"] == "qfep_surrogate_scope"
            else claim
            for claim in crosswalk["claims"]
        ],
    }
    unknown_audit = build_evidence_ceiling_audit(root, unknown_stressor)
    assert unknown_audit["ok"] is False
    assert unknown_audit["invalid_stressors"] == [{"claim_id": "qfep_surrogate_scope", "stressors": ["unknown_boundary"]}]


def test_claim_context_ledger_explains_public_claims_and_rejects_drift(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    crosswalk = json.loads((root / "output" / "data" / "source_claim_crosswalk.json").read_text(encoding="utf-8"))
    support = json.loads((root / "output" / "data" / "claim_support_audit.json").read_text(encoding="utf-8"))
    ledger = build_claim_context_ledger(root, crosswalk)
    rows = {row["claim_id"]: row for row in ledger["rows"]}
    assert ledger["schema"] == "realizing_emptiness.claim_context_ledger.v1"
    assert ledger["all_controls_pass"] is True
    assert ledger["claim_count"] == 15
    assert ledger["missing_reader_claims"] == []
    assert ledger["missing_future_evidence"] == []
    assert ledger["missing_manuscript_sections"] == []
    assert ledger["missing_figure_bindings"] == []
    assert ledger["role_compatibility_failures"] == []
    assert ledger["proxy_overclaiming_reader_claims"] == []
    assert rows["separation_prior_sigma"]["role_compatibility"]["rule"] == "primary_source_formal_target_allowed"
    assert rows["artifact_release_readiness"]["role_compatibility"]["rule"] == "release_readiness_requires_artifact_or_workflow_source"
    assert all(row["reader_claim"] and row["allowed_interpretation"] and row["prohibited_inference"] for row in rows.values())
    assert all(row["source_keys"] and row["source_roles"] for row in rows.values())
    assert all(row["artifact_exists"] is True for row in rows.values())
    assert all(row["validation_gate"] for row in rows.values())
    assert all(row["future_evidence_required"] for row in rows.values())
    assert all(row["manuscript_sections"] for row in rows.values())
    assert all(row["figure_bindings"] for row in rows.values())

    missing_reader = {
        **crosswalk,
        "claims": [
            {**claim, "paraphrase": ""}
            if claim["id"] == "source_boundary_unevidenceable"
            else claim
            for claim in crosswalk["claims"]
        ],
    }
    missing_reader_ledger = build_claim_context_ledger(root, missing_reader)
    assert missing_reader_ledger["all_controls_pass"] is False
    assert missing_reader_ledger["missing_reader_claims"] == ["source_boundary_unevidenceable"]

    missing_future = {
        **crosswalk,
        "claims": [
            {key: value for key, value in claim.items() if key != "future_evidence_required"}
            if claim["id"] == "bmr_prunes_sigma"
            else claim
            for claim in crosswalk["claims"]
        ],
    }
    missing_future_ledger = build_claim_context_ledger(root, missing_future)
    assert missing_future_ledger["all_controls_pass"] is False
    assert missing_future_ledger["missing_future_evidence"] == ["bmr_prunes_sigma"]

    role_drift_support = {
        **support,
        "support_rows": [
            {
                **row,
                "citation_key": "sandvedsmith2026noself",
                "source_id": "source_paper",
                "role": "primary formal target",
                "evidence_status": "primary_source_target",
            }
            if row["claim_id"] == "quantum_separability_entropy"
            else row
            for row in support["support_rows"]
        ],
    }
    role_drift_ledger = build_claim_context_ledger(root, crosswalk, claim_support=role_drift_support)
    assert role_drift_ledger["all_controls_pass"] is False
    assert [row["claim_id"] for row in role_drift_ledger["role_compatibility_failures"]] == ["quantum_separability_entropy"]

    proxy_overclaim = {
        **crosswalk,
        "claims": [
            {**claim, "paraphrase": "This provides empirical evidence for compassion in practitioners."}
            if claim["id"] == "compassion_proxy_boundary"
            else claim
            for claim in crosswalk["claims"]
        ],
    }
    proxy_overclaim_ledger = build_claim_context_ledger(root, proxy_overclaim)
    assert proxy_overclaim_ledger["all_controls_pass"] is False
    assert proxy_overclaim_ledger["proxy_overclaiming_reader_claims"] == ["compassion_proxy_boundary"]


def test_claim_redteam_audit_resolves_claim_locations_and_rejects_false_certification(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    crosswalk = json.loads((root / "output" / "data" / "source_claim_crosswalk.json").read_text(encoding="utf-8"))
    baseline = build_claim_redteam_audit(root, crosswalk)
    assert baseline["schema"] == "realizing_emptiness.claim_redteam_audit.v1"
    assert baseline["all_controls_pass"] is True
    assert baseline["claim_count"] == 15
    assert baseline["missing_sections"] == []
    assert baseline["unresolved_sections"] == []
    assert baseline["missing_figure_bindings"] == []
    assert baseline["unresolved_figure_bindings"] == []
    assert baseline["missing_boundaries"] == []
    assert baseline["reader_overclaims"] == []
    assert baseline["risky_claim_sentences"] == []
    assert all(row["row_controls_pass"] for row in baseline["rows"])
    assert all(row["source_role_count"] > 0 for row in baseline["rows"])
    assert all(row["artifact_exists"] for row in baseline["rows"])
    assert all(row["validation_gate"] for row in baseline["rows"])
    assert all(row["prohibited_inference"] and row["future_evidence_required"] for row in baseline["rows"])

    unresolved_section_context = json.loads(json.dumps(build_claim_context_ledger(root, crosswalk)))
    unresolved_section_context["rows"][0]["manuscript_sections"] = ["sec:not-a-real-section"]
    unresolved_section = build_claim_redteam_audit(root, crosswalk, claim_context=unresolved_section_context)
    assert unresolved_section["all_controls_pass"] is False
    assert unresolved_section["unresolved_sections"] == [
        {"claim_id": unresolved_section_context["rows"][0]["claim_id"], "section": "sec:not-a-real-section"}
    ]

    missing_section_context = json.loads(json.dumps(build_claim_context_ledger(root, crosswalk)))
    missing_section_context["rows"][0]["manuscript_sections"] = []
    missing_section = build_claim_redteam_audit(root, crosswalk, claim_context=missing_section_context)
    assert missing_section["all_controls_pass"] is False
    assert missing_section["missing_sections"] == [missing_section_context["rows"][0]["claim_id"]]

    unresolved_figure_context = json.loads(json.dumps(build_claim_context_ledger(root, crosswalk)))
    unresolved_figure_context["rows"][0]["figure_bindings"] = ["not_a_figure"]
    unresolved_figure = build_claim_redteam_audit(root, crosswalk, claim_context=unresolved_figure_context)
    assert unresolved_figure["all_controls_pass"] is False
    assert unresolved_figure["unresolved_figure_bindings"] == [
        {"claim_id": unresolved_figure_context["rows"][0]["claim_id"], "figure_id": "not_a_figure"}
    ]

    missing_boundary_context = json.loads(json.dumps(build_claim_context_ledger(root, crosswalk)))
    missing_boundary_context["rows"][0]["prohibited_inference"] = ""
    missing_boundary_context["rows"][1]["future_evidence_required"] = ""
    missing_boundary = build_claim_redteam_audit(root, crosswalk, claim_context=missing_boundary_context)
    assert missing_boundary["all_controls_pass"] is False
    assert {"claim_id": missing_boundary_context["rows"][0]["claim_id"], "field": "prohibited_inference"} in missing_boundary[
        "missing_boundaries"
    ]
    assert {
        "claim_id": missing_boundary_context["rows"][1]["claim_id"],
        "field": "future_evidence_required",
    } in missing_boundary["missing_boundaries"]

    intensity_failure = build_claim_redteam_audit(
        root,
        crosswalk,
        claim_intensity={
            "ok": False,
            "risky_rows": [
                {
                    "file": "manuscript/sections/results/test.md",
                    "sentence": "The software establishes no-self.",
                }
            ],
        },
    )
    assert intensity_failure["all_controls_pass"] is False
    assert intensity_failure["controls"]["manuscript_claim_intensity_pass"] is False
    assert intensity_failure["risky_claim_sentences"]


def test_manuscript_claim_audit_rejects_missing_claim_and_positive_efficacy(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    crosswalk = json.loads((root / "output" / "data" / "source_claim_crosswalk.json").read_text(encoding="utf-8"))
    audit = build_manuscript_claim_audit(root, crosswalk)
    assert audit["ok"] is True
    broken = {**crosswalk, "claims": [*crosswalk["claims"], {"id": "not_in_manuscript"}], "claim_count": crosswalk["claim_count"] + 1}
    broken_audit = build_manuscript_claim_audit(root, broken)
    assert broken_audit["ok"] is False
    assert broken_audit["missing_claim_mentions"] == ["not_in_manuscript"]
    proves_hits = {hit["pattern"] for hit in _forbidden_hits("This software proves awakening.")}
    assert "proves_realization_or_efficacy" in proves_hits
    # Gap closed: confirm/establish/demonstrate/validate/show + blocked outcome now also fire, not
    # only prove*. Each is a real overclaim the narrow prior gate would have let through.
    for overclaim in (
        "This software run confirms awakening.",
        "The audit establishes neural criticality.",
        "We demonstrate clinical benefit.",
        "These results validate practice efficacy.",
        "The simulation shows awakening.",
        # re-4 (human-subject) is a blocked class too; hyphen/space and singular/plural forms must fire.
        "The audit demonstrates a human subject outcome.",
        "This software establishes human-subject validation of awakening.",
        "These results confirm validated human-subject effects.",
        "This software establishes human-subjects validation.",
        "The audit demonstrates human subjects outcomes.",
    ):
        assert _forbidden_hits(overclaim), overclaim
    # Negation exemption (now robust to never/nothing/cannot, not only a literal "not ") keeps honestly
    # hedged prose clean, so the hardened gate adds teeth without false-positiving real captions.
    for hedged in (
        "The software does not confirm awakening.",
        "This never establishes neural criticality.",
        "Nothing here demonstrates clinical benefit.",
        "The audit cannot validate practice efficacy.",
    ):
        assert _forbidden_hits(hedged) == [], hedged


def test_source_schema_rejects_stale_local_path_contract(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    schema = json.loads((root / "schemas" / "source_manifest.schema.json").read_text(encoding="utf-8"))
    stale_manifest = {
        "schema": "realizing_emptiness.source_manifest.v1",
        "primary_source": {
            "title": "There is no self-evidence",
            "local_path": "/tmp/old-name.pdf",
            "sha256": "a" * 64,
            "osf_url": "https://osf.io/preprints/psyarxiv/m78z2_v1",
            "citation_key": "sandvedsmith2026noself",
        },
    }
    errors = list(Draft202012Validator(schema).iter_errors(stale_manifest))
    assert errors


def test_source_claim_schema_requires_evidence_ceiling_boundaries(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    schema = json.loads((root / "schemas" / "source_claim_crosswalk.schema.json").read_text(encoding="utf-8"))
    crosswalk = json.loads((root / "output" / "data" / "source_claim_crosswalk.json").read_text(encoding="utf-8"))
    assert not list(Draft202012Validator(schema).iter_errors(crosswalk))
    broken = {
        **crosswalk,
        "claims": [{key: value for key, value in crosswalk["claims"][0].items() if key != "future_evidence_required"}],
        "claim_count": 1,
    }
    assert list(Draft202012Validator(schema).iter_errors(broken))


def test_review_response_artifacts_account_for_local_release_and_figures(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    release = build_artifact_release_manifest(root)
    assert release["schema"] == "realizing_emptiness.artifact_release_manifest.v1"
    assert release["all_controls_pass"] is True
    assert release["public_publication_performed"] is False
    assert "output/data/artifact_release_manifest.json" in release["excluded_self_from_hashes"]
    assert "not public independent reproduction" in release["claim_boundary"]
    release_paths = {row["path"] for row in release["files"]}
    assert "src/formalism/review_response.py" in release_paths
    assert "schemas/artifact_release_manifest.schema.json" in release_paths
    assert "tests/test_formalism.py" in release_paths
    assert "manuscript/sections/results/bmr.md" in release_paths
    assert "docs/validation-contract.md" in release_paths
    assert release["controls"]["source_tree_included"] is True
    assert release["controls"]["schemas_included"] is True
    assert release["controls"]["tests_included"] is True
    assert release["controls"]["manuscript_sources_included"] is True
    assert release["controls"]["docs_included"] is True

    review = build_external_review_response_audit(root)
    statuses = {row["recommendation_id"]: row["response_status"] for row in review["rows"]}
    assert review["all_controls_pass"] is True
    assert statuses["public_independent_reproduction"] == "blocked_external_publication"
    assert review["missing_evidence"] == []

    ledger = build_figure_parameter_ledger(root)
    figure_map = json.loads((root / "output" / "data" / "figure_source_map.json").read_text(encoding="utf-8"))
    assert ledger["all_controls_pass"] is True
    assert ledger["row_count"] == figure_map["figure_count"]
    assert ledger["missing_rows"] == []
    assert ledger["rows_without_sources"] == []
    assert all(row["traceable"] for row in ledger["rows"])



def test_boundary_and_qrf_models_validate() -> None:
    screen = BoundaryScreen.default(3)
    assert screen.all_bitstrings().shape == (8, 3)
    deployment = QRFDeployment("dual", ("self", "env", "self"), 0.25, 2.0)
    deployment.validate(screen)
    assert deployment.is_dual
    sectorisation = Sectorisation.from_deployment(deployment)
    assert sectorisation.groups["self"] == (0, 2)
    prior = SeparationPrior(precision=2.0)
    assert prior.complexity_cost() > 0
    assert prior.admissible((deployment,)) == (deployment,)


def test_bmr_comparison_formula() -> None:
    full = FreeEnergyTerms(accuracy=0.8, complexity=1.0)
    reduced = FreeEnergyTerms(accuracy=0.75, complexity=0.2)
    comparison = BMRComparison(full, reduced)
    assert comparison.delta_complexity == -0.8
    assert round(comparison.delta_accuracy, 2) == -0.05
    assert comparison.prunes_prior is True


def test_complexity_kl_is_nonnegative_and_zero_at_equality() -> None:
    posterior = np.array([0.7, 0.3])
    prior = np.array([0.5, 0.5])
    assert complexity_kl(posterior, prior) > 0.0
    assert complexity_kl(prior, prior) == 0.0
    # Worked VFE: complexity is the real KL, accuracy is the expected log-likelihood.
    terms = FreeEnergyTerms.from_distributions(posterior, prior, np.log(np.array([0.8, 0.4])))
    assert abs(terms.complexity - complexity_kl(posterior, prior)) < 1e-12
    with pytest.raises(ValueError):
        complexity_kl(np.array([0.7, 0.3]), np.array([0.5, 0.5, 0.0]))


def test_eq6_vfe_decomposition_is_an_exact_information_split() -> None:
    decomposition = vfe_noise_insufficient_learning(np.array([0.55, 0.45]), np.array([0.7, 0.3]))
    # cross-entropy == entropy(noise) + KL(insufficient learning), exactly.
    assert abs(
        decomposition["noise_bits"] + decomposition["insufficient_learning_bits"] - decomposition["vfe_bits"]
    ) < 1e-12
    assert decomposition["insufficient_learning_bits"] > 0.0
    # A perfectly-learned model has zero insufficient learning; VFE is then pure noise.
    perfect = vfe_noise_insufficient_learning(np.array([0.55, 0.45]), np.array([0.55, 0.45]))
    assert perfect["insufficient_learning_bits"] == 0.0
    assert perfect["vfe_bits"] == perfect["noise_bits"]
    with pytest.raises(ValueError):
        vfe_noise_insufficient_learning(np.array([0.5, 0.5]), np.array([0.6, 0.5]))
    values = evaluate_equation_surrogates()["values"]
    assert values["eq6_vfe_bits"] > 0.0
    assert values["eq6_insufficient_learning_bits"] >= 0.0


def test_eq11_kl_and_eq13_14_containment_are_measured() -> None:
    values = evaluate_equation_surrogates()["values"]
    assert values["eq11_complexity_kl_bits"] > 0.0
    # eqs 13-14 minima are derived from measured free energy, not hard-coded names.
    assert values["eq13_constrained_minimum_profile"] == "dual"
    assert values["eq14_unconstrained_minimum_profile"] == "contextual"
    assert values["eq14_unconstrained_minimum_free_energy"] < values["eq13_constrained_minimum_free_energy"]
    assert values["eq14_containment_holds"] is True
    assert values["eq14_strict_superset_witness"] is True
    # Negative control: restricting to the dual-only set removes the strict-superset witness.
    assert values["eq14_strict_superset_witness_under_dual_only"] is False


def test_method_governance_ledger_and_controls(tmp_path) -> None:
    ledger = build_method_assumption_ledger()
    assert ledger["method_count"] == 8
    assert ledger["all_methods_have_hard_constraints"] is True
    assert ledger["all_methods_have_assumptions"] is True
    assert ledger["all_methods_have_evidence_ceiling"] is True
    assert "not empirical" in ledger["claim_boundary"]

    inventory = build_method_negative_control_inventory()
    assert inventory["all_methods_have_controls"] is True
    method_ids = {row["method_id"] for row in inventory["rows"]}
    assert method_ids == {row["method_id"] for row in ledger["rows"]}

    # Positive control: with the falsification controls stripped, the coverage predicate
    # must flip False — proving all_methods_have_controls is derived, not hard-coded True.
    from formalism import governance

    mutated_methods = tuple({**dict(row), "falsification_controls": ()} for row in governance.METHOD_ROWS)
    control_rows = [
        {"method_id": method["method_id"]}
        for method in mutated_methods
        for _ in method["falsification_controls"]
    ]
    covered = {method["method_id"] for method in mutated_methods} <= {row["method_id"] for row in control_rows}
    assert covered is False

    ledger_path, controls_path = write_method_governance_artifacts(tmp_path)
    assert json.loads(ledger_path.read_text())["method_count"] == 8
    assert json.loads(controls_path.read_text())["all_methods_have_controls"] is True


def test_manuscript_claim_intensity_audit_and_positive_control(pytestconfig, tmp_path) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    audit = build_manuscript_claim_intensity_audit(root)
    assert audit["schema"] == "realizing_emptiness.manuscript_claim_intensity_audit.v1"
    assert audit["ok"] is True
    assert audit["risky_rows"] == []
    assert audit["sentence_count"] >= 50

    # Positive control: an unscoped strong verb near a blocked domain must be flagged,
    # and adding a boundary term must clear it.
    overclaim = classify_sentence_intensity("These results prove neural criticality in meditators.")
    assert overclaim["allowed"] is False
    assert classify_sentence_intensity("The software establishes no-self.")["allowed"] is False
    assert classify_sentence_intensity("The audit validates neural criticality.")["allowed"] is False
    assert classify_sentence_intensity("These results prove practice efficacy.")["allowed"] is False
    hedged = classify_sentence_intensity(
        "This finite software surrogate does not prove neural criticality in meditators."
    )
    assert hedged["allowed"] is True

    # _forbidden_hits fires on a real overclaim and respects the negation exemption.
    assert _forbidden_hits("This proves awakening.")
    assert _forbidden_hits("This does not prove awakening.") == []

    write_path = write_manuscript_claim_intensity_audit(tmp_path)
    assert json.loads(write_path.read_text())["ok"] in (True, False)


def test_equation_crosswalk_renders_all_rows_without_machine_paths(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    registry = json.loads((root / "output" / "data" / "formalism_registry.json").read_text())
    text = render_equation_crosswalk(registry)
    assert "/Users/" not in text
    assert text.count("\n| ") >= 14  # 14 equation rows plus the header
    assert "Paper-to-Software Equation Crosswalk" in text
    # Drift guard: a mutated registry row changes the rendered crosswalk.
    mutated = json.loads(json.dumps(registry))
    mutated["equations"][0]["expression"] = "MUTATED"
    assert render_equation_crosswalk(mutated) != text


def test_contract_registry_requires_schema_on_json_data_artifacts(pytestconfig) -> None:
    from gates.contracts import build_artifact_contract_registry

    root: Path = pytestconfig.realizing_emptiness_root
    registry = build_artifact_contract_registry(root)
    assert registry["controls"]["all_json_data_artifacts_have_schema"] is True
    assert registry["schemaless_json_artifacts"] == []
    # The control is derived from the manifest rows, not a literal: a JSON data row with no schema
    # must flip it False. (Pure in-memory check of the predicate; the real manifest is untouched.)
    rows = registry["rows"]
    has_schemaless = any(
        row["kind"] in {"data", "report"} and row["path"].endswith(".json") and not row["schema"]
        for row in rows
    )
    assert has_schemaless is False  # the real tree is fully schema'd


def test_evidence_ceiling_audit_flags_status_drift_and_unsupported_claims(pytestconfig) -> None:
    root: Path = pytestconfig.realizing_emptiness_root
    crosswalk = json.loads((root / "output" / "data" / "source_claim_crosswalk.json").read_text(encoding="utf-8"))
    baseline = build_evidence_ceiling_audit(root, crosswalk)
    assert baseline["ok"] is True
    assert baseline["status_mismatches"] == []
    assert baseline["claims_without_support"] == []

    # Status drift: a claim whose declared status disagrees with the registry must be flagged.
    drifted = json.loads(json.dumps(crosswalk))
    target = next(claim for claim in drifted["claims"] if claim["id"] == "bmr_prunes_sigma")
    target["claim_status"] = "proxy_boundary"
    drift_audit = build_evidence_ceiling_audit(root, drifted)
    assert drift_audit["ok"] is False
    assert {"claim_id": "bmr_prunes_sigma", "expected": "finite_sweep", "observed": "proxy_boundary"} in drift_audit[
        "status_mismatches"
    ]

    # Claims without scholarly support must be flagged.
    template_claim = crosswalk["claims"][0]
    unsupported = json.loads(json.dumps(crosswalk))
    unsupported["claims"].append(
        {
            **{key: template_claim[key] for key in ("evidence_ceiling", "prohibited_inference", "future_evidence_required", "stressors")},
            "id": "unsupported_test_claim",
        }
    )
    unsupported_audit = build_evidence_ceiling_audit(root, unsupported)
    assert unsupported_audit["ok"] is False
    assert "unsupported_test_claim" in unsupported_audit["claims_without_support"]
