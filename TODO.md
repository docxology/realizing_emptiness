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

### Local documentation and environment maintenance

| ID | Priority | Scope | Scope detail and docs |
| --- | --- | --- | --- |
| re-doc-1 | Done (v1.1.0) | Composer now emits resolving figure paths and hydration rebases them for rendering; strict validation checks image files. | Docs: [manuscript guide](docs/manuscript/README.md), [release validation](docs/release-validation.md). |
| re-doc-2 | Done (v1.1.0) | Python support is bounded to 3.10-3.14 with a frozen dependency lock and CI matrix. A separate GitVault environment preserves the original local environment. | Docs: [running the chain](docs/running-the-chain.md), `pyproject.toml`. |
| re-doc-3 | Done (2026-08-31) | Render `--project` qualifier conflicted across README/AGENTS/running-the-chain; one canonical statement now lives in docs/running-the-chain.md. | Docs: [docs/running-the-chain.md](docs/running-the-chain.md). |
| re-doc-4 | Done (2026-08-31) | README lacked an orientation ladder (state / next actions / canonical pointers) and never linked TODO.md; added "State right now" section and canonical-command pointer to AGENTS.md. | Docs: [README.md](README.md), [AGENTS.md](AGENTS.md). |
| re-doc-5 | Done (2026-08-31) | AGENTS.md pointed to nonexistent ../projects/AGENTS.md from the standalone checkout; fixed to name the template-mirror location conditionally. | Docs: [AGENTS.md](AGENTS.md). |
| re-doc-6 | Done (2026-08-31) | Badge/quick-start counts lacked provenance; README now stamps them "as of 2026-08-31" with re-verification commands. | Docs: [README.md](README.md). |

### Re-verify before publishing any updated claim

```bash
uv run pytest tests/ --collect-only -q | tail -1        # test count
uv run python scripts/validate_outputs.py | tail -5     # gate count / PASS-FAIL summary
```

## Workflowz review — 2026-11-10

- [ ] **re-wf-1 — P2 — Make the documented Python support range and runtime pin agree.** Observable outcome: README, the completed TODO environment note, and the interpreter pin describe one supported range, with any upper bound recorded as a deliberate compatibility constraint rather than left contradictory. Evidence: README.md:24-25 says Python 3.11-3.14 is supported and README.md:81 repeats that range; TODO.md:41 says support is bounded to 3.10-3.14; .python-version:1 selects 3.15; pyproject.toml:11 declares only `>=3.11`, while pyproject.toml:21-22 has explicit pymdp markers at Python 3.12. Acceptance probe: from the repository root, run `uv run python -c 'import sys; print(sys.version); import simulation.pymdp_profiles as p; print(p._package_version("inferactively-pymdp"))'` and `uv run pytest tests/ --collect-only -q`; record the selected interpreter, installed pymdp version, and collection result in the environment note. Dependencies/constraints: do not claim 3.15 support or change the pymdp pins without executing the locked runtime; preserve any demonstrated scientific/reproducibility constraint and update the badge/metadata only to match verified behavior.

- [ ] **re-wf-2 — P2 — Make roadmap/TODO auditing recognize the new review section without weakening blocked-external gates.** Observable outcome: the two unchecked local review items are represented in the generated roadmap/TODO audit and dashboard, while the five existing blocked external IDs remain blocked and no historical-backlog violation is introduced. Evidence: src/gates/roadmap.py:100-105 parses TODO records by heading and line, src/gates/roadmap.py:165-170 feeds TODO text and historical rows into the fail-closed audit, and src/visualizations/dashboard.py:137-141 exposes stale/historical/blocked-class violations; tests/test_practice_and_chain.py:234-238 fixes the expected future IDs and requires no historical rows. Acceptance probe: from the repository root, run `uv run python scripts/generate_review_response_artifacts.py && uv run python scripts/generate_dashboard.py && uv run python scripts/validate_outputs.py`, then run `uv run pytest tests/test_practice_and_chain.py -q`; confirm validation passes, the dashboard reports the new local items, and the future/blocked ID sets remain exactly `re-3`, `re-4`, `re-13`, `re-14`, and `re-15`. Dependencies/constraints: inspect the omitted portions of `_todo_records` and `_historical_backlog_rows` before editing; preserve every existing tasks.yaml ID/status/dependency/hold and do not reclassify blocked external work as locally complete.
