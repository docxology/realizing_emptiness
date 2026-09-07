# QRF and the Sector Situation: A Reader's Introduction

This is the conceptual on-ramp. It explains *what* a quantum reference frame
(QRF) does in this project and *why* the "sector situation" matters, before the
[QRF formalism contract](qrf-formalism.md) makes the same ideas precise with
equations 7-10. Read this first if the words "boundary screen", "sector", or
"separation prior" are new; read the formalism contract next for the exact maps
and negative controls.

Nothing in this document is empirical, clinical, neural, contemplative, or
physical-qFEP evidence. Every object named here is a finite, deterministic
software surrogate with a declared evidence ceiling. See
[surrogate methodology](surrogate-methodology.md) for what a surrogate is
allowed to be.

## The problem in one sentence

Sandved-Smith et al. (2026) argue that a finite agent can **use** a boundary to
predict and act while never obtaining evidence that the boundary is
**ontologically real**. This is the *no-self-evidence* problem, and this project
turns it into runnable code.

The whole design keeps three operations apart that prose usually blurs:

1. **Use** a boundary channel for prediction. *Licensed.*
2. **Label** that channel with a QRF sector (call it "self", "env", "care", ...).
   *Free — you may label however you like.*
3. **Ontologize** the label: treat it as proof that a real self/world boundary
   exists. *Not licensed by the bitstream.*

The software exists to make operation 3 fail honestly while operations 1 and 2
succeed.

## The finite boundary screen (b0-b5)

The agent's interface to the world is a **boundary screen** of six binary
channels, `B = {b0, b1, b2, b3, b4, b5}`. Each `b_i` carries a bit. That bit is
the only evidenced object. The channel *roles* are readability labels, not
discoveries:

| Channel | Finite surrogate role |
| --- | --- |
| `b0` | body-controllability cue |
| `b1` | action-contingency cue |
| `b2` | distal-world cue |
| `b3` | contextual-world cue |
| `b4` | other-agent cue |
| `b5` | care-salience cue |

`b3` being called a "contextual-world cue" adds no evidence that there is a real
world on the other side of the screen. It is a bit with a helpful name. The
screen is implemented in `src/simulation/qrf_env.py`
(`boundary_channel_ledger`, `simulate_boundary_trajectory`).

## A QRF is a way to carve the screen into sectors

A **QRF deployment** assigns a *sector label* to each channel. A **profile** is a
named deployment. This project ships three:

| Profile | How it carves `b0..b5` | Sectors |
| --- | --- | --- |
| **separation-constrained** | `b0,b1,b5 -> self`; `b2,b3,b4 -> env` | 2 (a dual self/env cut) |
| **opacified** | `b0 -> self`, `b1 -> action`, `b2,b3 -> env`, `b4 -> other`, `b5 -> care` | 5 (partly dual, partly inspectable) |
| **post-dual** | `b0 -> body`, `b1 -> action`, `b2,b3 -> world`, `b4 -> other`, `b5 -> care` | 5 (no privileged self/env cut) |

These are three *carvings of one interface*, not three measurements of what the
interface ultimately is. The lead visual is the **sector-situation figure**
(`output/figures/qrf_sector_situation.png`): one shared screen at the top, the
same bits tied by vertical lines down to three lens rows. Profiles and sector
colors live in `src/simulation/qrf_env.py` (`default_deployments`) and
`src/formalism/models.py` (`QRFDeployment`, `Sectorisation`).

### Keep these four words distinct

This is the single most common source of confusion:

- **boundary channel `b_i`** — a software bit. The evidenced object.
- **sector label** — a name for organizing channels (`self`, `env`, `body`,
  `action`, `world`, `other`, `care`).
- **QRF deployment / profile** — a full assignment of labels to channels.
- **ontological sector** — a *prohibited* interpretation: a claim that some
  carving is the real one. The bitstream never licenses this.

## Why indistinguishability is the whole argument

If two profiles are both admissible over the *same* bitstream, then the
bitstream's observation distribution is identical under both. Equation 9
(`P(o | Q_i) = P(o | Q_j)`) states exactly this. So the bits cannot tell you
which carving is real — they are indifferent to the carving.

This is rendered as a permission rule in
`output/figures/boundary_use_vs_ontology.png`: the licensed lane (read the bits
through any frame, predict, act — the distribution stays fixed) versus the
blocked lane (treat the frame as a real self/world boundary — not licensed). The
audit that backs it, `boundary_indistinguishability_audit` in
`src/simulation/qrf_env.py`, holds the distribution fixed across admissible
relabelings *and* includes a deliberately perturbed control that must fail. The
failing control is what makes "blocked" earned rather than asserted.

## The separation prior: useful before it is dispensable

The **separation prior** `sigma` is a structural precision that restricts which
QRF deployments are admissible (equation 10). It biases the agent toward the
dual self/env carving. Is that bias good? The honest answer is *it depends on
metacognitive access*:

- The prior first **earns** its value through agency: a factored self/env model
  predicts the consequences of the agent's own actions better than an unfactored
  one *only when channels are action-contingent* (the emergence audit,
  `src/simulation/emergence.py`).
- It is then **kept or pruned** by Bayesian model reduction (BMR): the software
  compares full and reduced models and prunes the prior only when reduction
  lowers free energy (`src/simulation/bmr.py`).

Reading BMR as the prior's net value
(`output/figures/separation_prior_net_value.png`) shows the lifecycle plainly:
the **weakest** admissible prior is kept at low access and pruned at high access,
crossing from useful to dispensable inside the sweep. Stronger priors
over-commit and are pruned throughout — a faithful in-model finding, not a
guaranteed monotone story, and not a contemplative or clinical claim about
"letting go of the self".

## Where to go next

| You want | Read |
| --- | --- |
| The exact maps for equations 7-10, with negative controls | [QRF formalism contract](qrf-formalism.md) |
| Every paper equation 1-14 mapped to an artifact and a boundary | [equation crosswalk](equation-crosswalk.md) |
| What a surrogate may and may not claim | [surrogate methodology](surrogate-methodology.md) |
| A term you do not recognize | [glossary](glossary.md) |
| How the manuscript, code, and artifacts fit together | [project architecture](architecture.md) |
| Implemented finite quantum extension engines and future-evidence governance | [quantum extension governance](quantum-simulation-roadmap.md) |
| Every code method and the engine it backs | [method inventory](method-inventory.md) |
| How to set up and run the pipeline | [running the chain](running-the-chain.md) |
| The manuscript argument itself | `docs/manuscript/01_introduction.md`, then `docs/manuscript/02_methods.md` |
