# tests/ - agent conventions

- NO MOCKS. No `MagicMock`, `mocker.patch`, or `unittest.mock`. Use real `src/`
  code, constructed in-memory data, real temp files (`tmp_path`), real
  subprocess runs, and `pytest-httpserver` if a server is ever needed.
- 90% coverage floor on `src/`. New `src/` writers/branches need their own tests
  or the suite drops below the floor.
- Resolve paths via `pytestconfig.realizing_emptiness_root` (set in
  `conftest.py`); never hard-code absolute paths.

## Invariants to preserve

- Determinism guard: seeded surrogates must reproduce byte-for-byte on a second
  in-process build. Keep `test_seeded_surrogates_are_byte_identical_on_replay`
  and equivalents green; do not introduce unseeded randomness or
  non-canonical JSON (`indent=2, sort_keys=True`).
- Audits are tested with their negative controls. For any audit with a
  `controls`/`all_controls_pass`/verdict field, assert both the passing case and
  that corrupting a control flips the headline verdict. A passing test with no
  negative control is incomplete.
- Full-chain test: `test_full_chain_and_output_validation` runs
  `scripts/run_full_chain.py` and requires exit 0 plus all `validate_outputs`
  checks true. Keep counts (figure counts, protocol counts, etc.) in sync with
  `src/` when they change.

## Claim ceiling

Tests must keep wording and asserted artifact content within the surrogate
ceiling. `claim_boundary` strings are asserted to contain "not empirical"; do not
relax those assertions.
