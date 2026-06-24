# schemas/ - agent conventions

- One schema per artifact. Draft 2020-12 (`$schema` =
  `https://json-schema.org/draft/2020-12/schema`). File name mirrors the artifact
  it validates.
- Pin `schema` to a `const` version string (e.g.
  `realizing_emptiness.<name>.v1`). List required keys explicitly. Prefer
  `additionalProperties: false` unless the artifact is intentionally open
  (the input manifests are the documented exceptions).
- Controls are locked true:
  `"controls": {"type": "object", "additionalProperties": {"const": true}}`,
  and headline verdict flags use `{"const": true}`. This makes a regressed
  audit fail validation instead of passing silently.
- Every schema with a claim surface MUST require
  `"claim_boundary": {"type": "string", "pattern": "not empirical"}` (some add
  further patterns such as "not ontological" / "not a full qFEP"). Do not weaken
  these patterns.

## Adding an engine = adding a schema + wiring it

In `src/gates/validation.py`:
1. add the artifact path to `EXPECTED_DATA` (and report/figure lists if it
   produces those);
2. add the schema path to `EXPECTED_SCHEMAS`;
3. add the `(schema_path, artifact_path, "json"|"yaml")` tuple to
   `SCHEMA_TARGETS`;
4. add a per-artifact gate asserting its claim-boundary and control invariants.

Then cover the new artifact and its negative control in `../tests/`. A schema
that is not wired into all four points is not actually enforced.
