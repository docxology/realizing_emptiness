# Realizing Emptiness TODO

This backlog is future-only. Past work belongs in generated artifacts, tests,
manuscript fragments, and validation reports.

## Current V1 Scope

- Maintain faithful source and claim provenance for the 2026 preprint.
- Keep the equation registry complete for equations 1-14.
- Treat finite entropy, contextuality, open-system, stochastic trajectory,
  mixed-state, channel-cost, sparse-screen, covariance, and provenance outputs
  as bounded software computations.
- Keep physical qFEP realization, human-subject validation, clinical,
  awakening, neural-measurement, and practice-efficacy claims blocked until
  external reviewed evidence and ethics constraints exist.
- Keep practice-facing interfaces clearly labeled as model protocols.

## Backlog

### Blocked external-evidence classes

| ID | Status | Scope | Scope detail and docs |
| --- | --- | --- | --- |
| re-3 | blocked_external_evidence | Physical qFEP realization remains blocked until reviewed Hamiltonians, thermodynamic accounting, and independent quantum-information replication exist. | Finite Lindblad, trajectory, channel-cost, and boundary-screen artifacts remain software surrogates, not physical qFEP evidence. Docs: [quantum roadmap](docs/quantum-simulation-roadmap.md), [validation contract](docs/validation-contract.md), [surrogate methodology](docs/surrogate-methodology.md). |
| re-4 | blocked_external_evidence | Human-subject validation remains blocked until ethics review, preregistered outcomes, sourced data, preprocessing provenance, null models, and safety review exist. | Synthetic fixtures and provenance adapters cannot stand in for ethics-reviewed data, preregistration, source identity, preprocessing records, nulls, or safety review. Docs: [validation contract](docs/validation-contract.md), [surrogate methodology](docs/surrogate-methodology.md). |
| re-13 | blocked_external_evidence | Clinical, awakening, compassion-efficacy, and neural-measurement claims remain blocked and must not be inferred from finite software simulations. | Compassion, criticality, and practice-protocol outputs are proxy or boundary audits only; they do not measure clinical outcomes, awakening, compassion efficacy, or neural signals. Docs: [validation contract](docs/validation-contract.md), [surrogate methodology](docs/surrogate-methodology.md), [adversarial audit](docs/redteam-audit.md). |
| re-14 | blocked_external_evidence | User-facing practice applications require human review, safety wording, and explicit non-efficacy language before release. | Practice maps are model protocols, not user guidance; release requires human safety review, non-efficacy wording, and practice-facing governance. Docs: [validation contract](docs/validation-contract.md), [surrogate methodology](docs/surrogate-methodology.md). |
| re-15 | blocked_external_release | Public archive release and independent or blinded reproduction remain blocked until explicit publication approval, public deposition, and external reproduction of the artifact bundle exist. | Local hashes, manifests, and render gates support private readiness only; they do not certify public deposition or independent reproduction. Docs: [running the chain](docs/running-the-chain.md), [validation contract](docs/validation-contract.md). |

## Agent orientation (local, unblocked)

A cold agent should: (1) read [README.md](README.md) top-to-bottom, (2) confirm
status from the "State right now" section, (3) come here for next actions, (4)
verify with the canonical commands in [AGENTS.md](AGENTS.md).

### Backlog: local doc/ergonomics items (from the 2026-08-31 agent-ergonomics pass — see REVIEW_LOG_2026-08-31.md)

| ID | Priority | Scope | Scope detail and docs |
| --- | --- | --- | --- |
| re-doc-1 | Medium | Fix the generator, not the generated files: `scripts/compose_manuscript.py` emits `../output/figures/*.png` links in `docs/manuscript/0X_*.md` that do not resolve at the committed location (57 links). Emit paths valid from `docs/manuscript/` or reference the dashboard instead. | Docs: [docs/manuscript/README.md](docs/manuscript/README.md), `scripts/compose_manuscript.py`. |
| re-doc-2 | Medium | Pin Python floor/upper in `pyproject.toml`: current env uses Python 3.14 and binary wheels for scipy/matplotlib/rpds break (collection ImportError). Environment had to be rebuilt on 2026-08-31. | Docs: `pyproject.toml`, verify with `uv run pytest tests/ --collect-only -q`. |
| re-doc-3 | Done (2026-08-31) | Render `--project` qualifier conflicted across README/AGENTS/running-the-chain; one canonical statement now lives in docs/running-the-chain.md. | Docs: [docs/running-the-chain.md](docs/running-the-chain.md). |
| re-doc-4 | Done (2026-08-31) | README lacked an orientation ladder (state / next actions / canonical pointers) and never linked TODO.md; added "State right now" section and canonical-command pointer to AGENTS.md. | Docs: [README.md](README.md), [AGENTS.md](AGENTS.md). |
| re-doc-5 | Done (2026-08-31) | AGENTS.md pointed to nonexistent ../projects/AGENTS.md from the standalone checkout; fixed to name the template-mirror location conditionally. | Docs: [AGENTS.md](AGENTS.md). |
| re-doc-6 | Done (2026-08-31) | Badge/quick-start counts lacked provenance; README now stamps them "as of 2026-08-31" with re-verification commands. | Docs: [README.md](README.md). |

### Re-verify before publishing any updated claim

```bash
uv run pytest tests/ --collect-only -q | tail -1        # test count
uv run python scripts/validate_outputs.py | tail -5     # gate count / PASS-FAIL summary
```
