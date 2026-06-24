# Glossary

Terms used across the manuscript, code, and contracts. Each entry names where
the object lives in the code. Every term denotes a finite software surrogate or a
governance device, never empirical, clinical, neural, contemplative, or
physical-qFEP evidence.

## Boundary and QRF

- **boundary screen `B`** — the agent's interface: six binary channels
  `{b0..b5}`. The carried bits are the only evidenced object.
  (`src/simulation/qrf_env.py`, `src/formalism/models.py:BoundaryScreen`)
- **boundary channel `b_i`** — one software observation channel carrying a bit.
  Its role name (e.g. "care-salience cue") aids reading and adds no evidence.
- **sector label** — a name assigned to a channel for organizing the model:
  `self`, `env`, `body`, `action`, `world`, `other`, `care`.
- **neutral sector alias** — the label-ablation names used to show that loaded
  words are not doing the evidential work: `self -> sector_s`, `env -> sector_e`,
  `body -> sector_b`, `action -> sector_a`, `world -> sector_w`,
  `other -> sector_o`, and `care -> sector_c`.
- **sectorisation** — a mapping from sectors to the channels they contain.
  (`src/formalism/models.py:Sectorisation`)
- **QRF deployment** — a complete assignment of sector labels to all channels,
  plus a metacognitive-access parameter and a separation-prior precision.
  (`src/formalism/models.py:QRFDeployment`)
- **profile** — a named QRF deployment. The three shipped profiles are
  `separation_constrained`, `opacified`, and `post_dual`.
  (`src/simulation/qrf_env.py:default_deployments`)
- **agency** — action-contingency inside the finite model: selected actions
  lower prediction error for some boundary channels under the declared
  generative model. It is not autonomous selfhood or empirical volition.
- **care** — the `b5` care-salience cue and later policy-scope proxy input. It
  is not moral compassion, a validated affective measure, or evidence of
  contemplative concern.
- **QRF mode** — reader-facing shorthand for one of the three QRF deployments,
  not a psychological state. The modes differ in sector labels,
  metacognitive access, prior precision, generative-model priors/preferences,
  and selected-action frequencies while preserving the same observed bitstream.
- **ontological sector** — a *prohibited* reading: the claim that one
  sectorisation is the real carving of self from world. The bitstream never
  licenses this; this is the no-self-evidence point.
- **boundary indistinguishability** — the property that admissible relabelings
  leave the observation distribution unchanged (equation 9). Verified with a
  perturbation control that must fail.
  (`src/simulation/qrf_env.py:boundary_indistinguishability_audit`)

## Free energy and model reduction

- **separation prior `sigma`** — a structural precision restricting admissible
  QRF deployments toward the dual self/env carving (equation 10).
  (`src/formalism/models.py:SeparationPrior`)
- **metacognitive access** — a model parameter (0-1) for how much the agent can
  inspect and revise its own priors. Higher access tends to make the separation
  prior dispensable.
- **emergence** — the finite test that a factored self/env predictor beats an
  unfactored one only when channels are action-contingent.
  (`src/simulation/emergence.py`)
- **Bayesian model reduction (BMR)** — a sweep comparing full vs. reduced models
  to decide when pruning the separation prior lowers free energy
  (`Delta F = F_reduced - F_full`). (`src/simulation/bmr.py`)
- **VFE decomposition** — the exact information split of variational free energy
  into accuracy, complexity, and noise terms (equation 6).
  (`src/formalism/models.py:vfe_noise_insufficient_learning`)

## Simulation surrogates

- **pymdp profile** — a discrete active-inference agent (pinned
  `inferactively-pymdp==1.0.3`) with profile-specific `A`, `B`, `C`, `D` arrays
  and the action vocabulary `stabilize_dual`, `inspect_boundary`,
  `release_prior`. (`src/simulation/pymdp_profiles.py`)
- **pymdp runtime dependency check** — the limited package-surface check that
  imports the pinned `pymdp` runtime, constructs a small agent, runs state
  inference, and confirms policy-posterior normalization. It is not a benchmark
  of active-inference optimality, human behavior, or scientific validity.
  (`src/simulation/pymdp_profiles.py:pymdp_runtime_dependency_check`)
- **criticality proxy** — software branching-ratio and avalanche diagnostics on a
  simulated activity trace; a *shape* for future empirical tests, not a neural
  measurement. (`src/simulation/criticality.py`)
- **compassion / scope-of-concern proxy** — a finite policy-scope surrogate
  measuring per-channel concern asymmetry; not a measure of compassion.
  (`src/simulation/compassion_scope.py`)
- **quantum surrogate** — the finite quantum-information audit layer: two-qubit
  entropy/CHSH/PPT/negativity/dephasing plus implemented extension engines (multipartite and
  higher-dimensional witnesses, tensor-network/MPS benchmarks, collision-model
  thermalization, no-signaling and n-cycle contextuality libraries, many-body and
  sparse boundary sweeps). Not open-system qFEP or empirical physics; see the
  generated [method inventory](method-inventory.md) for the full catalog.
  (`src/simulation/quantum_surrogates.py`)
- **implemented extension engine** — a finite quantum/tensor surrogate beyond
  the original two-qubit layer, each with its own schema, validation gate, and
  discriminating controls; enumerated in the generated method inventory.
- **roadmap / TODO governance** — the future-only planning surface that blocks
  external evidence classes and fails when a TODO row describes an already
  implemented extension engine as future work.

## Governance devices

- **evidence ceiling** — the strongest claim an artifact is allowed to support;
  stronger readings are explicitly blocked.
  ([surrogate methodology](surrogate-methodology.md))
- **evidence class** — the tier an artifact occupies (e.g.
  `operational_surrogate`, `finite_sweep`, `finite_quantum_simulation`,
  `proxy_boundary`). (`output/data/claim_context_ledger.json`)
- **negative control** — a deliberately broken input that a faithful audit must
  reject; without it a passing audit shows little.
- **positive control** — a planted known effect a faithful audit must detect;
  without it a non-rejection could just mean a weak test.
- **claim crosswalk / claim-context ledger** — the per-claim record of reader
  claim, source role, artifact, gate, prohibited inference, and future evidence
  required. (`src/formalism/claim_context.py`)
- **artifact release readiness** — local private release accounting over hashes
  for generated outputs, source files, schemas, tests, manuscript fragments,
  docs, manifests, rerun scripts, and validation commands. It is a bounded
  implementation claim and does not mean public archive deposition or
  independent reproduction.
- **sheaf / track** — the modular manuscript system: each section is composed
  from per-topic track fragments under `manuscript/sections/`.
  ([architecture](architecture.md))

See [the QRF introduction](qrf-introduction.md) for how these fit together and
the [QRF formalism contract](qrf-formalism.md) for the equation-level detail.
