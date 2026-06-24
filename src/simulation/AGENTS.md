# AGENTS.md - src/simulation

Finite seeded simulation engines. Read the root [`AGENTS.md`](../../AGENTS.md)
Source Contract first.

## Determinism (mandatory)

- Seed every RNG explicitly (`np.random.default_rng(seed)`); accept `seed` as a
  parameter and record it in the artifact for replay.
- No wall-clock, no `time`-based values, no unseeded randomness, no environment
  reads that vary between runs.
- Convert NumPy scalars to native Python before JSON: `float(...)`, `int(...)`,
  `bool(...)`, `np.round(...).tolist()`. A leaked `numpy.float64`/`numpy.bool_`
  breaks deterministic serialization and schema validation.

## Every new engine needs (all five)

1. A discriminating negative control (one that genuinely *fails* — not a
   size-preserving relabel that cannot falsify the quantity).
2. A positive control whenever the finding rests on a non-rejection (inject a
   known effect; show the same test fires).
3. A JSON schema in `schemas/`.
4. A `gates/validation.py` check and an `artifact_manifest.yaml` entry.
5. A no-mocks test in `../tests/` using real numerical examples.

## Do NOT

- Do NOT claim neural criticality, empirical statistical power over real
  subjects, compassion/well-being outcomes, or physical qFEP — these are
  software-trajectory diagnostics only.
- Do NOT hardcode a verdict/`*_helps`/status literal; derive every verdict from a
  measured comparator and add a flip test.
- Do NOT drop the `claim_boundary` string (must contain `not empirical`).
