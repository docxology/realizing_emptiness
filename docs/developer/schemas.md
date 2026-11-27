# schemas/

JSON-Schema (Draft 2020-12) contracts, one per data artifact. Every JSON/YAML
artifact produced by the chain (`output/data/*`, the input manifests under
`data/sources/`, and `artifact_manifest.yaml`) is validated against the matching
schema during `validate_outputs`. The schemas pin structure, enforce the claim
ceiling (`claim_boundary` must contain "not empirical"), and lock negative
controls to true so a regression cannot pass validation.

## Layout

- ~75 `*.schema.json` files, one per artifact. Names mirror their artifact
  (e.g. `bmr_sweep.schema.json` validates `output/data/bmr_sweep.json`,
  `source_manifest.schema.json` validates `data/sources/source_manifest.yaml`).
- Each fixes `schema` to a `const` version string, requires the artifact's keys,
  and most set `additionalProperties: false`.
- Control objects use `"controls": {"additionalProperties": {"const": true}}` so
  every reported control must be `true`; verdict flags use `{"const": true}`.
- `claim_boundary` fields use `{"type": "string", "pattern": "not empirical"}`.

## Pipeline fit

Schemas are the static contract layer between the generators (`../scripts/`,
logic in `../src/`) and the tests (`../tests/`). Wiring lives in
`src/gates/validation.py`: `EXPECTED_SCHEMAS` lists every schema, `SCHEMA_TARGETS`
maps each `(schema, artifact, kind)` tuple, and per-artifact gates assert the
claim-boundary and control invariants. Adding an engine means adding a schema
here and wiring it there (see this folder's AGENTS.md).
