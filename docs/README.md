# Documentation

The documentation home for the `realizing_emptiness` project. Every document
records how one part of the source-faithful software foundation works or is
governed. Files are flat in this folder (no subdirectories). Two documents are
**generated** by the chain and must not be hand-edited — they are marked below.

> **Published.** v1.0.0 is archived on Zenodo at
> [doi.org/10.5281/zenodo.20834847](https://doi.org/10.5281/zenodo.20834847)
> and released on GitHub at
> [docxology/realizing_emptiness](https://github.com/docxology/realizing_emptiness).
> See the [project README](../README.md) for the landing page and citation.

The source paper itself is `There_is_no_self_evidence_Sandved-Smith_2026.pdf` in
this folder; the project recapitulates it as finite deterministic software
surrogates and never claims empirical, clinical, neural, ontological, or
physical-qFEP evidence.

## Start here (conceptual)

| Document | Purpose |
| --- | --- |
| [QRF introduction](qrf-introduction.md) | Plain-language on-ramp to the no-self-evidence problem, the `b0`-`b5` boundary screen, the three sector profiles, indistinguishability, and the separation-prior life-cycle. |
| [Glossary](glossary.md) | Every recurring term, each pointing to where the object lives in the code. |

## How it fits together and how to run it

| Document | Purpose |
| --- | --- |
| [Project architecture](architecture.md) | How manuscript, `src`, `scripts`, `tests`, and artifacts connect, with recipes for adding a figure or a claim. |
| [Running the chain](running-the-chain.md) | Setup, the full-chain run with a per-stage walkthrough, output layout, verification gates, single-result reproduction, and gate-failure troubleshooting. |
| [`src/simulation` module contract](../src/simulation/README.md) | Source-level map for the finite simulation modules, including the modular `pymdp` profile stack, its `A/B/C/D` arrays, deterministic traces, runtime diagnostics, and validation gates. |

## Formal mapping (paper to software)

| Document | Purpose |
| --- | --- |
| [QRF formalism contract](qrf-formalism.md) | Equations 7-10, admissible relabeling, negative controls, and the non-quantum-dynamical boundary of the finite screen. |
| [Equation crosswalk](equation-crosswalk.md) *(generated)* | Map from paper equations 1-14 to artifacts, gates, and interpretive boundaries, rendered from `formalism_registry.json`. |
| [Quantum simulation roadmap](quantum-simulation-roadmap.md) | Finite quantum, contextuality, tensor-network, collision-model, and no-signaling/n-cycle engines, plus the five blocked external-evidence classes and their required next gates. |

## Discipline and gates

| Document | Purpose |
| --- | --- |
| [Surrogate methodology](surrogate-methodology.md) | Evidence ceilings, discriminating negative controls, positive controls, and measured verdicts. |
| [Validation contract](validation-contract.md) | Output gates, schemas, review-response artifacts, negative controls, and statistical-robustness audits. |
| [Visualization contract](visualization-contract.md) | Figure source maps, renderer-layout telemetry, integrity hashes, semantic palette, accessibility audits, dashboard Visual QA, and figure placement. |

## Provenance and hardening

| Document | Purpose |
| --- | --- |
| [Scholarship source matrix](scholarship.md) | Source-role matrix separating primary-target claims, implementation anchors, formal background, and proxy-only empirical context. |
| [Method inventory](method-inventory.md) *(generated)* | Per-method governance ledger: hard constraints, assumptions, evidence ceilings, and falsification controls. |
| [Adversarial audit record](redteam-audit.md) | Numbered stress-test findings and their resolved minimal fixes. |

## Suggested reading path

New here? Start with the [QRF introduction](qrf-introduction.md), keeping the
[glossary](glossary.md) open. Then read the [QRF formalism contract](qrf-formalism.md)
and the [equation crosswalk](equation-crosswalk.md) to see how the paper's argument
maps onto finite software, the [surrogate methodology](surrogate-methodology.md) and
[validation contract](validation-contract.md) for how every claim is gated. Then
read the [visualization contract](visualization-contract.md) before judging or
editing figures, and the [project architecture](architecture.md) plus
[running the chain](running-the-chain.md) when you are ready to extend,
regenerate, render, or reproduce the project. For the `pymdp` simulation in
particular, read the [`src/simulation` module contract](../src/simulation/README.md)
alongside the methods section: the code keeps the QRF environment, generative
model arrays, deterministic trace, seeded ensemble, runtime diagnostics, and
validation gates as separate audit surfaces.

For blocked future claims, read the blocker ledger in the
[quantum simulation roadmap](quantum-simulation-roadmap.md) with the
[validation contract](validation-contract.md) and
[surrogate methodology](surrogate-methodology.md): those pages define why
`re-3`, `re-4`, `re-13`, `re-14`, and `re-15` remain future-only.
