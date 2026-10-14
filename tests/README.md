# tests/

Pytest suite for the Realizing Emptiness software surrogates. No mocks: every
test exercises real `src/` code, constructed data, real temp files, and (for the
chain) a real subprocess run. The suite confirms the artifacts, gates, and audits
behave as specified and stay inside the claim ceiling (no empirical, clinical,
neural, ontological, awakening, practice-efficacy, or physical-qFEP claims).

## Files

| File | Covers |
| --- | --- |
| `conftest.py` | Sets `MPLBACKEND=Agg`, puts `src/` on `sys.path`, exposes `pytestconfig.realizing_emptiness_root`. |
| `test_formalism.py` | Source manifest + pinned hash, equation registry/audit, claim crosswalk, governance ledgers, manuscript claim audits, models. |
| `test_simulation.py` | QRF/BMR/pymdp/criticality/quantum surrogates, compassion scope, statistical robustness, byte-identical determinism replay. |
| `test_resampling.py` | Independent and paired estimands, ties, finite permutation resolution, exact binomial boundaries, invalid samples, deterministic multi-seed calibration and an absent-effect negative control. |
| `test_practice_and_chain.py` | Practice maps, the full script chain end-to-end, output validation, figures, dashboard, manuscript structure/reference/placement audits. |
| `test_release_contracts.py` | Malformed schemas and inputs, pinned source identity, runtime dependency identity, read-only composition, hydration, numerical boundaries, and visual telemetry. |

## Pipeline fit

`test_practice_and_chain.py` runs `scripts/run_full_chain.py` as a subprocess and
then asserts every output gate passes, so the tests are the executable contract
for the whole pipeline. Determinism is guarded directly: seeded surrogates must
reproduce byte-for-byte on replay. Audits are validated together with their
negative controls (flipping a control flips the headline verdict).

## Running

Run the canonical coverage command from the project root using `uv`, as listed
in [AGENTS.md](../AGENTS.md). Tests use the selected runtime's dependencies;
the pytest configuration must not prepend another environment's site-packages.
