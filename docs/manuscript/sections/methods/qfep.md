Every symbol introduced in this subsection — the sectorisation map, the boundary screen, the separation prior, the free-energy terms, and the finite quantum quantities — is defined, with its natural-language name and a short description, in the symbol and variable glossary (@sec:supplement-symbol-glossary). Readers meeting a symbol for the first time should treat that glossary as the canonical reference; the prose here introduces each symbol only where it is first used.

The equation registry covers paper equations 1-14. Each row records the paper section, formal expression, computability status, operational status, paper-to-software bridge, validation artifact, and interpretive boundary. The registry therefore treats the source paper as a formal specification rather than as a set of slogans to be reproduced in code. The operational status map is retained as supplemental governance material so the first numbered result can present the finite QRF boundary model directly.

For stable internal reference, the registry file records all fourteen source equations, while the manuscript anchors the QRF rows used repeatedly by the boundary-channel argument. The sectorisation map $Q$ sends boundary states $B$ to sector labels $S_Q$:

$$
Q: B \rightarrow S_Q
$$ {#eq:7}

The frame-restricted model $M_Q$ reproduces the coarse-grained observation likelihood of the full model under that sectorisation:

$$
P(\bar{o} \mid M_Q) = P(\bar{o} \mid Q, M)
$$ {#eq:8}

Two sectors $Q_i$ and $Q_j$ are indistinguishable when they induce the same observation distribution:

$$
P(o \mid Q_i) = P(o \mid Q_j)
$$ {#eq:9}

The separation prior $\sigma$ restricts admissible sectorisations to a subspace $Q_{\sigma}$:

$$
\sigma: Q \rightarrow Q_{\sigma} \subset Q
$$ {#eq:10}

These anchors are manuscript reference targets for the finite registry, not a replacement for the source paper's formal derivations.

The resulting formal layer has three kinds of rows. First, computable active-inference rows become finite surrogates over boundary channels, QRF sector labels, profile-conditioned scores, separation-prior admissibility, and free-energy comparisons. The free-energy rows include a worked complexity decomposition for registry equation 6, a Kullback-Leibler complexity surrogate for registry equation 11, and a solution-set containment audit for registry equations 13 and 14 whose discriminating negative control is a strict-superset witness.

Second, quantum-information rows that can be represented faithfully in a small Hilbert space are simulated directly as finite controls. Each engine records a primary quantity together with a positive control and a discriminating negative control; the full per-engine construction, controls, and claim boundary live in @sec:supplement-finite-quantum-contextuality-audits, and the entries below name each engine and forward to that audit:

- a Schmidt-family two-qubit sweep recording reduced von Neumann entropy, mutual information, Clauser-Horne-Shimony-Holt (CHSH) witness strength, contextual-fraction scaling, local-basis entropy invariance, and a Landauer-scaled erasure lower bound;
- a mixed-state audit adding positive-partial-transpose (PPT) and negativity controls for separable, Bell, and Werner-family cases [@peres1996separability; @horodecki1996separability; @werner1989quantum], extended by a multipartite witness suite over three-party cuts [@greenberger1989going];
- a CHSH measurement-cover table recording context-by-outcome joint probabilities, no-signaling marginals, product-control locality, Tsirelson-bound saturation [@cirelson1980quantum], and local-hidden-variable polytope feasibility over the sixteen deterministic assignments following the joint-probability/local-polytope reading of Bell inequalities [@fine1982hidden], with a general measurement-cover parser and a no-signaling scenario library repeating the linear-program (LP) test for triangle, parity, CHSH-product, CHSH-Bell, and n-cycle scenarios [@araujo2013ncycle];
- finite completely-positive trace-preserving (CPTP) channels recording entropy-change and Landauer lower-bound summaries [@kraus1983states; @nielsen2010quantum], a finite dephasing channel recording trace preservation, positivity, entropy production, mutual-information contraction, and CHSH decay, and a collision-model thermalisation engine recording relaxation toward a fixed point.

Third, the implemented extension methods are finite software engines, again with their full construction and controls in @sec:supplement-finite-quantum-contextuality-audits:

- a two-qubit boundary-Hamiltonian Lindblad audit following Gorini-Kossakowski-Sudarshan-Lindblad (GKSL) trace and positivity constraints [@gorini1976completelypositive; @lindblad1976generators; @manzano2020lindblad];
- seeded quantum-trajectory unraveling that samples jump and no-jump Monte Carlo wave functions and compares the ensemble density with exact Lindblad evolution using the Monte Carlo wave-function literature as the methodological anchor [@dalibard1992wavefunction; @molmer1993montecarlo; @plenio1998quantumjump; @wiseman2010quantum];
- exact and sparse boundary-screen sweeps that test cut sensitivity as many-body precursors to tensor-network scaling, with a matrix-product-state tensor-network benchmark recording entanglement-bounded compression error [@eisert2010area; @orus2014tensor];
- an internal-cut unmeasurability audit and a contextuality-suppression audit that operationalise the source paper's internal-boundary and contextuality-suppression sections;
- sheaf and measurement-cover LP audits that distinguish noncontextual global sections from obstruction cases [@kochen1967problem; @abramsky2011sheaf];
- QRF covariance audits that test probability-preserving relabelings and finite unitary and permutation frame transforms [@giacomini2019qrf; @vanrietvelde2020perspective; @hoehn2021trinity; @bartlett2007reference];
- an empirical adapter provenance audit that requires source identity, preprocessing, null models, and preregistration-oriented governance before any human claim [@wilkinson2016fair; @nosek2018preregistration].

This structure makes `qfep_surrogate_scope` narrower and more useful. The claims `quantum_separability_entropy`, `quantum_contextuality_witness`, `quantum_measurement_contextuality`, and `quantum_open_system_dephasing` are allowed because they point to audited finite quantum artifacts and pass negative controls. The additional implemented extension artifacts add stronger software validation and more adversarial failure cases, but the prohibited inference remains explicit: none of these finite engines is physical qFEP realization, empirical practice evidence, neural measurement, or evidence for contemplative attainment.
