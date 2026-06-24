# AGENTS.md - src/formalism

Equation registry, data models, and claim/provenance ledgers. Read the root
[`AGENTS.md`](../../AGENTS.md) Source Contract first.

## Do

- Keep `equation_registry()` at exactly 14 entries covering paper equations 1-14;
  each `EquationSurrogate` declares `computable`, an `implementation`, a
  `surrogate_note`, and a `PAPER_TO_SOFTWARE_BRIDGES` entry. The
  `equation_count_14` gate enforces count + full mapping.
- For every public claim ID keep the four-part binding intact: source role,
  validation gate, artifact, evidence ceiling. `build_claim_support_audit`
  rejects any unsupported ID.
- Keep `build_claim_context_ledger` and `build_evidence_ceiling_audit` output
  complete per claim: reader sentence, allowed reading, prohibited inference,
  future-evidence requirement, and at least one boundary stressor.
- Derive eq 13/14 minima and the strict-superset containment witness from
  measured free energy by genuine recomputation, not from hardcoded literals.
- Use paraphrased section/page locators only.

## Do NOT

- Do NOT paste long passages from the source paper into any ledger or registry.
- Do NOT relax `verify_primary_source_hash` or change the pinned source hash.
- Do NOT let `build_manuscript_claim_audit` /
  `build_manuscript_claim_intensity_audit` pass positive-efficacy, attainment,
  clinical, or neural-measurement wording near blocked domains without a new
  empirical gate.
- Do NOT add a claim ID, equation, or source role without its schema,
  manifest entry, gate check, and test.
