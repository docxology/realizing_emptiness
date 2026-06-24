# AGENTS.md - src

Project-specific logic for Realizing Emptiness. Read the root
[`AGENTS.md`](../AGENTS.md) Source Contract and Project Surface first.

## Do

- Keep all algorithms here or in `infrastructure/`; `scripts/` and `tests/` only
  orchestrate and assert.
- Give every audit/producer a `claim_boundary` string containing `not empirical`
  (plus the domain-specific blocker, e.g. `not a physical qFEP`, `not ontological`).
- Ship a discriminating negative control AND, where a finding rests on a
  non-rejection, a positive control with every new audit.
- Wrap NumPy scalars (`float(...)`, `int(...)`, `bool(...)`, `.tolist()`) before
  writing JSON, and round for determinism.
- Mirror every new artifact across all five call sites: schema in `schemas/`,
  entry in `artifact_manifest.yaml`, a `gates/validation.py` check, a producer
  call in `scripts/run_full_chain.py`, and a test in `../tests/`.

## Do NOT

- Do NOT introduce empirical, clinical, neural, ontological, awakening,
  practice-efficacy, or physical-qFEP claims — the claim ceiling is absolute.
- Do NOT write absolute `/Users/` paths anywhere; the documentation gate fails
  closed on them. Use repo-relative paths.
- Do NOT add a public claim ID without a source role, gate, artifact, and
  evidence ceiling (enforced by `claim_support_audit`).
- Do NOT use mocks in tests; use real data and real temp files.
- Do NOT change `data/sources/source_manifest.yaml` hash
  (`94e2335c...699ac`) — `verify_primary_source_hash` fails closed on drift.
