from copy import deepcopy
import json
import shutil

import pytest

from gates.validation import _load_json


@pytest.mark.parametrize("artifact", ["pymdp_profile_comparison", "pymdp_runtime_diagnostics_log"])
@pytest.mark.parametrize("location", ["root", "dependency", "schema"])
def test_runtime_artifacts_reject_unknown_fields_and_wrong_nested_versions(pytestconfig, tmp_path, artifact, location):
    root = pytestconfig.realizing_emptiness_root
    shutil.copytree(root / "schemas", tmp_path / "schemas")
    relative = f"output/data/{artifact}.json"
    payload = json.loads((root / relative).read_text(encoding="utf-8"))
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(payload), encoding="utf-8")
    assert _load_json(tmp_path, relative) == payload
    changed = deepcopy(payload)
    if location == "root":
        changed["unknown_field"] = True
    elif location == "dependency":
        changed["runtime_dependency_check"]["unknown_field"] = True
    else:
        changed["runtime_dependency_check"]["schema"] = "invalid_runtime_contract"
    target.write_text(json.dumps(changed), encoding="utf-8")
    assert _load_json(tmp_path, relative) == {}


@pytest.mark.parametrize("mutation", ["unknown", "missing"])
def test_dashboard_runtime_contract_is_closed(pytestconfig, tmp_path, mutation):
    root = pytestconfig.realizing_emptiness_root
    shutil.copytree(root / "schemas", tmp_path / "schemas")
    relative = "output/data/artifact_dashboard_payload.json"
    payload = json.loads((root / relative).read_text(encoding="utf-8"))
    target = tmp_path / relative
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps(payload), encoding="utf-8")
    assert _load_json(tmp_path, relative) == payload
    if mutation == "unknown":
        payload["pymdp_runtime"]["unknown_field"] = 1
    else:
        del payload["pymdp_runtime"]["runtime_warning_count"]
    target.write_text(json.dumps(payload), encoding="utf-8")
    assert _load_json(tmp_path, relative) == {}
