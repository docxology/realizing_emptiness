# Surrogate Methodology

This document records the design philosophy that keeps every finite surrogate in
the project honest. It is the reasoning behind the validators, not a restatement
of them.

## What a surrogate is allowed to be

A surrogate is a finite, deterministic or seeded-stochastic software computation
that operationalizes one inferential role from the source paper. It is never a
measurement of a brain, a practitioner, a physical quantum system, or a
contemplative attainment. Every surrogate carries an explicit **evidence
ceiling** naming the stronger reading its support does *not* license, and the
ceiling is stored on the artifact, not only in prose.

## Negative controls: a control must be able to fail

A passing check is only informative if a corresponding failing case exists. Each
method therefore declares a **negative control** that must fail when the modelled
effect is absent. Examples:

- the QRF boundary screen ships a perturbed relabeling that must break invariance;
- the criticality ensemble requires the measured branching ratio to differ from a
  shuffled null beyond tolerance;
- the quantum-trajectory audit ships a too-few-trajectory run that must fail to
  reconstruct the exact Lindblad density;
- the multipartite witness suite ships separable product fixtures that must stay
  undetected on every bipartition, plus an asymmetric Bell-pair-plus-spectator
  fixture whose per-cut pattern must fail under a wrong-axis transpose;
- the collision-model surrogate ships a zero-coupling collision that must leave
  the system state unchanged;
- the no-signaling scenario library ships a deliberately disturbing table that
  must be flagged as signaling, and the n-cycle contextuality library ships even
  (two-colorable) cycles that must stay feasible while odd cycles do not.
- the QRF label-ablation audit ships neutral aliases that must preserve the
  ledger structure and a collapsed-label structure control that must fail.

A negative control is only valid if it can actually falsify the quantity it
guards. A size-preserving label shuffle, for instance, cannot falsify a quantity
whose value is governed by partition size and a scalar parameter; for the
compassion scope-of-concern surrogate the discriminating control is therefore a
**precision ablation** that removes the separation prior's self-precision boost,
not a label shuffle.

## Positive controls: a non-rejection must be interpretable

A failure to reject a null is uninterpretable without evidence that the same
machinery rejects a known effect. Each estimator therefore declares a **positive
control** on synthetic data:

- the effect-size machinery is calibrated with null, positive, and sign-flip
  synthetic arms that must fail to reject the null and reject a known injected
  effect with the correct Cliff's-delta sign;
- the branching estimator is calibrated against planted geometric activity
  series whose exact branching ratio is known, and must recover subcritical,
  critical, and supercritical values in order;
- the compassion surrogate must show a monotone dose-response: raising the
  separation-prior precision deepens the self-concentration.

## Verdicts must be measured, not declared

A verdict field set to a string literal, or a control gated on a variable the
analysis already declares inferior, passes even when the finding flips. Every
keep/prune, recover/fail, and pass/fail verdict in this project is therefore
derived from a measured comparator, and each is paired with a mutation test that
zeroes the signal and confirms the verdict flips.

## Blocked evidence classes are not surrogates

Some rows in the roadmap are intentionally not finite surrogates. They are
external evidence classes whose absence is part of the claim boundary:

- `re-3` blocks physical qFEP realization until reviewed Hamiltonians,
  thermodynamic accounting, and independent quantum-information replication
  exist.
- `re-4` blocks human-subject validation until ethics review, preregistration,
  source identity, preprocessing provenance, null models, and safety review
  exist.
- `re-13` blocks clinical, awakening, compassion-efficacy, and
  neural-measurement claims until reviewed external evidence and independent
  controls exist.
- `re-14` blocks user-facing practice applications until human safety review,
  non-efficacy wording, and release governance exist.
- `re-15` blocks public archive and independent or blinded reproduction claims
  until explicit publication approval, public deposition, and external
  reproduction of the artifact bundle exist.

The finite artifacts can document why these blockers remain visible and
fail-closed. They cannot satisfy the blockers by themselves. A local hash,
negative control, schema, render, or synthetic fixture is therefore a governance
signal inside the software bundle, not external evidence for the stronger
claim.

## Where this is enforced

The [validation contract](validation-contract.md) lists the gates; the
[method inventory](method-inventory.md) lists the per-method hard constraints,
assumptions, evidence ceilings, and falsification controls; and the
[adversarial audit record](redteam-audit.md) records the stress-tested findings
that produced these rules.

The local artifact-release manifest is a governance surrogate too. It hashes
manifest-listed outputs plus the source tree, schemas, tests, manuscript
fragments, docs, and rerun-support files for private review readiness; the
validator recomputes those hashes so stale source or artifact bytes fail. It is
explicitly blocked from claiming public archive deposition or independent
reproduction.
