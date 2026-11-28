---
project: realizing_emptiness
title: Realizing Emptiness
status: working
---

# ISA - Integrity Specification

This project recapitulates the attached paper's formalisms as executable,
bounded software. The integrity boundary is deliberately narrow:

- every paper equation is represented in `output/data/formalism_registry.json`
  and either mapped to an executable finite surrogate or labeled
  non-computable for v1;
- the source ledger verifies the attached PDF hash and records the OSF preprint
  URL without copying long passages from the source;
- The PyMDP runtime check verifies the profile-specific package version, agent
  construction and posterior normalization. See [the contract](api-contracts.md#runtime-dependency-check).
- QRF, separation-prior, Bayesian model reduction, criticality, compassion, and
  practice outputs are deterministic toy or proxy artifacts unless separately
  evidenced;
- generated figures must declare their backing JSON/CSV sources.

The manuscript should not claim empirical awakening, neural criticality,
practice efficacy, or compassion gains. It may claim that the software creates
inspectable simulations, validation ledgers, and research interfaces for those
future questions.
