import pytest
import json
from jsonschema import Draft202012Validator

from simulation.pymdp_profiles import runtime_warnings_match_version


@pytest.mark.parametrize("version,messages,expected", [
    ("1.0.3", ["static JAX array"], True),
    ("1.0.4", [], True),
    ("1.0.3", [], False),
    ("1.0.4", ["unexpected warning"], False),
    ("1.0.4", None, False),
    ("1.0.3", [None], False),
    ("unknown", [], False),
])
def test_runtime_warning_contract_matches_pinned_version(version, messages, expected):
    assert runtime_warnings_match_version({"version": version, "warnings": messages}) is expected


def test_missing_runtime_warning_record_fails():
    assert not runtime_warnings_match_version({"version": "1.0.4"})


@pytest.mark.parametrize("schema_name", ["pymdp_profile_comparison", "pymdp_runtime_diagnostics_log"])
@pytest.mark.parametrize("version,messages,expected", [
    ("1.0.3", ["static JAX array"], True), ("1.0.4", [], True),
    ("1.0.3", [], False), ("1.0.4", ["unexpected warning"], False),
])
def test_schema_preserves_version_specific_warning_contract(pytestconfig, schema_name, version, messages, expected):
    root = pytestconfig.realizing_emptiness_root
    schema = json.loads((root / f"schemas/{schema_name}.schema.json").read_text())
    check = {"schema": "realizing_emptiness.pymdp_runtime_dependency_check.v1", "ok": True,
             "version": version, "required_version": version, "version_ok": True,
             "policy_posterior_normalized": True, "warnings": messages}
    contract = schema.get("$defs", {}).get("runtime_dependency_check", schema["properties"]["runtime_dependency_check"])
    assert Draft202012Validator(contract).is_valid(check) is expected
