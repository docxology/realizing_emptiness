This glossary is the single structured home for every symbol that appears in the equation registry and in the displayed surrogate equations of @sec:methods-roadmap-quantum-engines. Each row gives the symbol, its natural-language name, and a short description of what it denotes in the finite software surrogate. Where the source paper and the active-inference literature reuse the same letter for two different quantities, the disambiguation note records which reading this project uses. The glossary describes notation only; it does not assert any empirical, neural, clinical, or ontological reading of the quantities it names.

### Boundary screen and quantum reference frames

These symbols appear in the QRF sectorisation and indistinguishability surrogates (@eq:7, @eq:8, @eq:9).

| Symbol | Name | Description |
| --- | --- | --- |
| $B$ | Boundary screen | The finite set of boundary channels (the six bits) through which an agent and its environment interact; the substrate the agent predicts across. |
| $S_Q$ | Sector set | The set of QRF sector labels that a sectorisation can assign to boundary states. |
| $Q$ | Sectorisation map (QRF) | A quantum reference frame realised as a map $Q: B \rightarrow S_Q$ from boundary states to sector labels (@eq:7). |
| $Q_i,\ Q_j$ | Sector labels | Two specific sectors whose observation distributions are compared for indistinguishability (@eq:9). |
| $o$ | Observation | A boundary readout, i.e. a bit pattern emitted by the screen. |
| $\bar{o}$ | Coarse-grained observation | A marginal or aggregated observation used in the frame-relative likelihood (@eq:8). |
| $M$ | Generative model | The agent's full model over boundary dynamics. |
| $M_Q$ | Frame-restricted model | The generative model read under a particular sectorisation $Q$ (@eq:8). |
| $P(\cdot)$ | Probability | A finite probability distribution over boundary outcomes. |

### Separation prior, free energy, and Bayesian model reduction

These symbols appear in the separation-prior and free-energy surrogates (@eq:10, equation 6, and equation 11 of the registry).

| Symbol | Name | Description |
| --- | --- | --- |
| $\sigma$ | Separation prior | A structural precision and map $\sigma: Q \rightarrow Q_{\sigma}$ restricting admissible sectorisations to a subspace (@eq:10). Disambiguation: the criticality branching ratio is conventionally also written $\sigma$; this project reports it as "branching ratio" to keep the separation prior unambiguous. |
| $Q_{\sigma}$ | Admissible subspace | The restricted set of sectorisations favoured by the separation prior (@eq:10). |
| $F$ | Variational free energy | The quantity the agent minimises; it decomposes as complexity minus accuracy (registry equation 6). |
| $\Delta F$ | Free-energy change | The free energy of the reduced model minus the free energy of the full model, i.e. the change when the separation prior is pruned. |
| complexity | Complexity term | The Kullback-Leibler divergence of the posterior from the prior over model parameters (registry equation 11). |
| accuracy | Accuracy term | The expected log-likelihood of observations under the model. |

### Active-inference generative arrays (pymdp)

The profile-specific generative models are built from four arrays. The manuscript names them in words; the conventional single letters are given here for cross-reference only.

| Array (conventional letter) | Name | Description |
| --- | --- | --- |
| likelihood array ($A$) | Observation likelihood | Maps hidden states to observation probabilities. |
| transition array ($B$) | State transition | Maps a state and selected action to the next state. Disambiguation: $B$ here is the pymdp transition array, distinct from the boundary screen $B$ above; the manuscript uses "transition array" in prose. |
| preference array ($C$) | Preferences | Encodes the agent's preferred observations as log-preferences. |
| prior array ($D$) | Initial-state prior | The prior over hidden states at the first step. |

### Seeded criticality signatures

These quantities are computed from seeded boundary-channel activity series (see @sec:supplement-criticality-indicators).

| Symbol | Name | Description |
| --- | --- | --- |
| branching ratio | Branching ratio | Estimated descendants per ancestor over a boundary-channel activity series. |
| criticality index | Criticality index | The absolute distance of the measured branching ratio from one, $\lvert\text{branching ratio} - 1\rvert$. |
| avalanche size | Avalanche size | The length of a maximal supra-threshold run of activity. |
| LLR | Power-law-versus-exponential LLR | A finite log-likelihood-ratio diagnostic comparing power-law and exponential fits to the avalanche-size distribution. |

### Finite quantum-information quantities

These appear in the finite quantum and contextuality engines (@sec:supplement-finite-quantum-contextuality-audits).

| Symbol | Name | Description |
| --- | --- | --- |
| $\rho$ | Density matrix | A finite quantum state on a small Hilbert space. |
| $S(\rho)$ | Von Neumann entropy | $-\mathrm{Tr}(\rho \log \rho)$; the reduced entropy quantifies entanglement in the two-qubit sweep. |
| CHSH value | Bell witness | A correlation sum tested against the local bound of two and the Tsirelson bound of $2\sqrt{2}$. |
| negativity | Entanglement witness | A separability witness derived from the positive-partial-transpose criterion. |
| $H_U, H_A, H_B, H_{AB}$ | Partition entropies | Joint and marginal Shannon entropies of boundary partitions used in the registry's first equation. |

Every symbol above denotes a quantity inside a finite, replayable software surrogate. None of these symbols, individually or in combination, is a measurement of a physical, neural, or contemplative quantity, and the evidence ceilings in @sec:supplement-claim-evidence-ceilings govern how any of them may be read.
