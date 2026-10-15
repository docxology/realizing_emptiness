# Realizing Emptiness

**Source-faithful, fully reproducible software operationalizing the formalisms of *There is no self-evidence: A physics of emptiness realisation* (Sandved-Smith, Fields, Doctor, Laukkonen & Hohwy, 2026).**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20834847.svg)](https://doi.org/10.5281/zenodo.20834847)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Validation](https://github.com/docxology/realizing_emptiness/actions/workflows/ci.yml/badge.svg)](https://github.com/docxology/realizing_emptiness/actions/workflows/ci.yml)

| | |
| --- | --- |
| **Version** | v2.0.0; [changes](CHANGELOG.md) and [release validation](docs/release-validation.md) |
| **Archived v1.0.0 (Zenodo)** | [10.5281/zenodo.20834847](https://doi.org/10.5281/zenodo.20834847); [concept DOI](https://doi.org/10.5281/zenodo.20834846). A new version DOI is not yet recorded. |
| **Manuscript PDF** | [`realizing_emptiness_combined.pdf`](output/pdf/realizing_emptiness_combined.pdf) · [latest release](https://github.com/docxology/realizing_emptiness/releases/latest) |
| 📚 **Source preprint** | [osf.io/preprints/psyarxiv/m78z2_v1](https://osf.io/preprints/psyarxiv/m78z2_v1) |
| 📖 **Documentation** | [`docs/`](docs/README.md) |

---

## State right now (orientation for a cold agent)

- **Project status:** v2.0.0 consolidates the runtime API and statistical contracts,
  requires measured branching for criticality gates, and removes superseded
  manuscript material and visualizations. The scholarship ledger has 125 sources.
  The v1.0.0 DOI identifies the earlier archive; it does
  not identify this version.
- **Measured status:** use the [release validation record](docs/release-validation.md),
  the CI run for the commit, and `output/reports/validation_report.json`.
  Test counts and coverage are measured at validation time.
- **Next actions / backlog:** [TODO.md](TODO.md) is the single canonical backlog — including the five blocked-external-evidence classes and any local, unblocked work.
- **Commands:** the canonical command list lives in [AGENTS.md](AGENTS.md) (Commands section); the quick start below is a subset.

## What this is

`realizing_emptiness` turns the paper's formal argument — no-self-evidence,
quantum reference frame (QRF) sectorisation, the separation (σ) prior,
opacification, and Bayesian model reduction — into finite, deterministic,
individually-gated software surrogates.

Every public claim is bound to a manuscript anchor, a generated artifact, a
validation gate, and an explicit **evidence ceiling** stating what must *not* be
inferred from it. Nothing here measures awakening, neural criticality, clinical
outcome, or physical qFEP realization; the project makes the paper's formal
commitments **inspectable and reproducible**, and is rigorous about saying where
the software stops and empirical science would have to begin.

## Highlights

- **Equations 1–14 as finite surrogates** — worked VFE/KL decompositions, an evidenced `b0`–`b5` QRF boundary-channel ledger, and three QRF deployment profiles (separation-constrained, opacified, post-dual).
- **Active inference** — a real `pymdp` profile stack (explicit `A/B/C/D` arrays, deterministic policy traces, runtime diagnostics) plus seeded stochastic ensembles with null controls and replayable seeds.
- **Bayesian model reduction** — separation-prior pruning sweeps with sensitivity analysis over prior precision, metacognitive access, and observation noise.
- **Finite quantum information** — two-qubit separability entropy, CHSH/contextuality witnesses, local-polytope feasibility audits, CPTP channel-cost and dephasing surrogates, quantum-trajectory unraveling, and a Cramér–Rao coherence bound.
- **Measured statistics** — run-level mean-difference and Cliff's-delta intervals, paired branching contrasts, permutation Monte Carlo uncertainty with Holm correction, and calibration over 128 seed sets. See [statistical methods](docs/statistical-methods.md).
- **Expanded scholarship** — 125 ledger entries with source roles and claim ceilings, including statistical limitations, FEP critiques, quantum reference frames and contemplative measurement. See the [expansion synthesis](docs/scholarship-expansion.md).
- **Adversarial claim governance** — scholarship source-role matrix, claim-support and claim-context ledgers, evidence-ceiling and claim-intensity audits, and a 37-finding [red-team record](docs/redteam-audit.md).
- **Reproducible visualization** — source-mapped figures with integrity hashes, a semantic palette, accessibility/caption audits, and a static [artifact dashboard](output/dashboard/index.html).

See the [documentation index](docs/README.md) for the full contract-by-contract breakdown.

## Repository layout

| Path | Contents |
| --- | --- |
| [`src/`](src/) | Finite simulation, formalism, gates, and visualization modules |
| [`scripts/`](scripts/) | Thin orchestrators — the deterministic artifact chain |
| [`docs/manuscript/`](docs/manuscript/) | Sheaf-composed manuscript sources (compose into the combined PDF) |
| [`docs/`](docs/README.md) | Conceptual on-ramp, formal mapping, and discipline/gate contracts |
| [`output/`](output/) | Generated artifacts: data, figures, dashboard, and the rendered PDF |
| [`schemas/`](schemas/) | JSON schemas for every generated artifact |
| [`data/sources/`](data/sources/source_manifest.yaml) | Source + claim provenance (preprint SHA-256 and OSF URL) |

## Quick start

```bash
uv sync --frozen --extra dev
uv run python scripts/run_full_chain.py          # regenerate every artifact, deterministically
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run python scripts/validate_outputs.py
```

The analysis chain uses fixed seeds and stable JSON serialization. Figure bytes
are reproducible within the same locked runtime and rendering dependencies;
PDF/HTML/EPUB rendering is a separate template step. See
[running the chain](docs/running-the-chain.md) for the per-stage walkthrough and
gate-failure troubleshooting.

Render the manuscript PDF through the sibling template checkout:

```bash
# from the template checkout
uv run python scripts/pipeline/stage_03_render.py --project <qualifier>
```

The correct `--project` qualifier depends on which sidecar lifecycle folder holds the mirror; [docs/running-the-chain.md](docs/running-the-chain.md) is canonical for determining it.

## Reproducibility & validation

- Artifact gates cover existence, schemas, the pinned source digest, per-claim
  boundaries, figure integrity, manifest coverage, and review-response checks.
- Tests use real objects and computations, with a 90% branch-inclusive source
  coverage floor and adversarial corruption controls; no mocking frameworks.
- Deterministic crosswalk and method-inventory generation that cannot drift from the source registry.
- Independent or blinded reproduction of the full artifact bundle remains a **declared future-evidence boundary** — see the blocker ledger in the [quantum simulation roadmap](docs/quantum-simulation-roadmap.md).

## Citation

> Friedman, Daniel Ari (2026). *Realizing Emptiness* (v2.0.0). Active Inference
> Institute. https://github.com/docxology/realizing_emptiness/releases/tag/v2.0.0

The archived v1.0.0 version DOI remains available above. The concept DOI
[10.5281/zenodo.20834846](https://doi.org/10.5281/zenodo.20834846) tracks the
Zenodo archive and may lag GitHub releases. Machine-readable metadata:
[`CITATION.cff`](CITATION.cff), [`codemeta.json`](codemeta.json),
[`.zenodo.json`](.zenodo.json).

## License

MIT — see [`LICENSE`](LICENSE). The source preprint *There is no
self-evidence: A physics of emptiness realisation* (Sandved-Smith et al., 2026)
is © its authors; its provenance is recorded by SHA-256 and OSF URL in
[`data/sources/source_manifest.yaml`](data/sources/source_manifest.yaml).

## Integrity boundary

The software does not claim to prove awakening, compassion, neural criticality,
clinical benefit, or physical qFEP realization. It implements finite surrogate
checks and seeded stochastic simulations that make the paper's formal
commitments inspectable. Targeted quantum-trajectory and QRF-transformation
sources support method vocabulary only. Practice protocols are model
interventions and research interfaces, not medical, spiritual, or therapeutic
instructions.
