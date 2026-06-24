# AGENTS.md - src/gates

Fail-closed validators. Read the root [`AGENTS.md`](../../AGENTS.md) Source
Contract first.

## Fail-closed discipline (mandatory)

- A missing/unparseable artifact must make a check `False`, never raise. Read
  gated JSON through `_load_json`, which returns `{}` on
  `FileNotFoundError`/`JSONDecodeError`; then assert specific keys are present and
  truthy.
- Never mask a producer or validator failure with `2>/dev/null || true` or a bare
  `except`. Let it surface, or record it as a failed check.
- A `*_ok` check passes only when the artifact declares its `claim_boundary`
  (containing `not empirical` plus the domain blocker), its schema/control flags,
  AND its negative control fails as expected.

## When adding/changing artifacts

- Add the path to the correct `EXPECTED_*` list and to `SCHEMA_TARGETS` (with its
  schema + kind) in `validation.py`.
- Keep `build_artifact_contract_registry` count equal to the manifest artifact
  count; `validate_outputs` cross-checks both.
- `check_documentation_contract` fails on `/Users/` machine paths, stale
  `template_active_inference` text, orphaned docs, and broken local links — keep
  it strict; do not loosen these guards.

## Do NOT

- Do NOT turn a fail-closed empty-payload into a default-pass.
- Do NOT add a gate that asserts empirical, clinical, neural, or qFEP truth; gates
  assert finite-surrogate structure only.
