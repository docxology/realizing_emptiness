# Scholarship expansion: estimands and interpretation boundaries

As of 2026-10-14, this targeted curation adds 32 sources to the 93-entry
scholarship ledger. Its purpose is to improve the questions that the executable
research can answer and the limits attached to those answers. It is not a
systematic review, a meta-analysis, or a count of support for the source paper.
The resulting ledger has 125 entries; all additions use existing claim IDs.

## Search and provenance

Searches combined author names and article titles with the unresolved method:
simulation estimands, permutation p-values, exchangeability, stationary
bootstrap, surrogate time series, Monte Carlo standard errors, calibration,
active-inference objective derivation, quantum reference-frame resources,
phenomenological interviews, mindfulness measurement, and adverse experiences.
Publisher article records, author-hosted papers, arXiv records, PubMed/PMC
records of original articles, and publisher-deposited Crossref metadata were
used to check identities and scope. Search aggregators were discovery aids;
their summaries were not used as scientific evidence.

The source-linked synthesis below links persistent primary records. The corresponding
BibTeX entries record full author lists, titles, venues, identifiers, and years.
Issue years are used for Hemerik and Goeman (2018), Van Es (2021), Van Dam et al.
(2018), and Modrak et al. (2025), whose online-first or preprint dates differ.
McGregor et al. (2015) remains a preprint. DOI-registration metadata was
captured separately from the synthesis; a candidate DOI that resolved to an
unrelated paper was rejected. Temporary rate-limit responses were preserved
and successful records retrieved subsequently. Metadata verification is not
full-text replication of a paper's findings, and no effect sizes from human
studies were imported into the project.

The set includes original method papers and original conceptual critiques,
alongside reviews/tutorials used only for methodological framing. The latter
are not relabeled as new empirical studies. Abstracts and accessible original
texts support the bounded descriptions here; inaccessible results are not
inferred from a title. Grossman's publisher-indexed record establishes a
measurement critique, while the more detailed construct/design implications
are grounded in the accessible Davidson-Kaszniak and Van Dam texts.

## Contrast uncertainty is an estimand question

Morris, White, and Crowther organize simulation studies around aims,
data-generating mechanisms, estimands, methods, and performance measures.
Burton et al. emphasize planning the generator and simulation budget. Applied
here, these methods require declaring whether a statistic targets a profile
mean, a mean contrast, a dominance effect, or an original-minus-shuffled
trajectory difference. This application is our methodological inference, not
a result those papers establish about the present simulator.
([Morris et al.](https://doi.org/10.1002/sim.8086),
[Burton et al.](https://doi.org/10.1002/sim.2673))

An interval for a pooled mean is not an interval for a difference. For two
independent run populations, each bootstrap replicate must reconstruct the
contrast from resampled runs in both populations. If runs are intentionally
paired, an intact pair is the resampling unit. A dominance effect must be
recomputed within each replicate rather than assigned the mean contrast's
interval. These are consequences of specifying the statistic and sampling
design. Within-run timesteps remain dependent; Kunsch and Politis-Romano
provide stationary dependent-data methods with assumptions about dependence
and block construction, rather than permission to treat timepoints as
independent replications. Their presence in the ledger does not mean those
methods are implemented locally.
([Kunsch](https://doi.org/10.1214/aos/1176347265),
[Politis and Romano](https://doi.org/10.1080/01621459.1994.10476870))

## A resampling operation defines its null

Permutation inference requires a distributional invariance or exchangeability
argument. Restricted permutations and blocks can encode dependence; arbitrary
label shuffling cannot substitute for that argument. Likewise, sign-flipping
paired differences requires symmetry under the null or a justified randomized
design. An observed/shuffled trajectory pair is computationally paired, but
pairing alone does not establish sign symmetry.
([Winkler et al.](https://doi.org/10.1016/j.neuroimage.2014.01.060),
[Hemerik and Goeman](https://doi.org/10.1007/s11749-017-0571-1))

For the usual valid random-permutation construction including the observed
identity arrangement, reporting `(b + 1) / (B + 1)` makes the finite attainable
resolution explicit, where `b` counts exceedances and `B` counts sampled
permutations. The sampling convention, ties, statistic direction, and whether
the identity is already included must be recorded. Exact enumeration is a
different convention. A plus-one adjustment cannot make an invalid
exchangeability assumption valid. Multiplicity correction must then name its
family; Romano-Wolf's resampling stepdown methods are a comparison to the local
Holm procedure, not evidence that it implements dependence-adaptive stepdown.
([Phipson and Smyth](https://doi.org/10.2202/1544-6115.1585),
[Romano and Wolf](https://doi.org/10.1198/016214504000000539))

Theiler et al. formulate surrogate tests by specifying a null process before
constructing the reference distribution. Schreiber and Schmitz show why
matching selected temporal and distributional properties matters. A complete
time-order shuffle preserves the empirical value distribution while destroying
serial order; it does not preserve autocorrelation. Consequently, a contrast
against that shuffle is evidence about temporal-order sensitivity under that
construction. It is neither a universal nonlinearity test nor sufficient
evidence of criticality. The existing criticality false-positive counterweights
remain essential.
([Theiler et al.](https://doi.org/10.1016/0167-2789(92)90102-S),
[Schreiber and Schmitz](https://doi.org/10.1103/PhysRevLett.77.635))

## Calibration checks need their own negative controls

Finite simulation budgets introduce Monte Carlo uncertainty even when the
generator and target quantity are completely specified. Flegal et al. analyze
this problem for correlated Markov-chain output; those standard-error formulas
must not be transferred unchanged to independent permutation draws. For the
present work the shared principle is to report numerical precision separately
from the scientific estimand, including the resampling budget and exceedance
count. A fixed seed gives reproducibility of one computation, not robustness
across independently generated seed banks.
([Flegal et al.](https://doi.org/10.1214/08-STS257),
[Morris et al.](https://doi.org/10.1002/sim.8086))

Cook et al. use posterior quantiles for Bayesian software validation. Modrak
et al. show that the choice of test quantity changes which computational
failures simulation-based calibration can detect; data-dependent quantities
can detect failures missed by less informative checks. Sailynoja et al.
distinguish validation averaged across a prior predictive distribution from
validation conditional on observed data. These are computational-correctness
questions. They do not show that the model describes human subjects or that
the local synthetic effect-size calibration is Bayesian posterior calibration.
They motivate deliberate failing controls and an explicit statement of what
each current gate can detect.
([Cook et al.](https://doi.org/10.1198/106186006X136976),
[Modrak et al.](https://doi.org/10.1214/23-BA1404),
[Sailynoja et al.](https://doi.org/10.1007/s11222-026-10825-9))

Proper scoring rules supply a different evaluation target: the predictive
distribution relative to outcomes. Our operational inference is that a model
should not be praised merely because its predictions become more concentrated
or its entropy decreases. The scoring target and comparison distribution need
to be specified. This source is methodological background, not a claim that
every local prediction is currently assessed by a proper scoring rule.
([Gneiting and Raftery](https://doi.org/10.1198/016214506000001437))

## Active inference does not eliminate interpretive assumptions

Buckley et al. expose assumptions in a mathematical implementation; Friston
et al. provide a process theory, and McGregor et al. provide a minimal
agent construction. These make algorithmic choices available for inspection.
Millidge et al. question the derivation of expected free energy and explain
why exploration does not follow from merely extending variational free energy
into the future. The implementation consequence is to state the objective,
preferences, factorization, and policy-selection rule explicitly rather than
using the free-energy label as a complete explanation.
([Buckley et al.](https://doi.org/10.1016/j.jmp.2017.09.004),
[Friston et al.](https://doi.org/10.1162/NECO_a_00912),
[McGregor et al.](https://arxiv.org/abs/1503.04187),
[Millidge et al.](https://doi.org/10.1162/neco_a_01354))

Van Es argues that scientists' models and models attributed to organisms can
be conflated. That argument is included as an original conceptual counterweight,
not treated as a settled verdict on every realist interpretation. Together with
the existing technical critiques and qualified responses, it supports a narrow
reading: the local model specifies a useful computational experiment without
settling whether an organism literally instantiates its representations or
whether the simulated boundary is ontologically fundamental.
([Van Es](https://doi.org/10.1177/1059712320918678))

## Quantum operations and numerical descriptions are different objects

No-cloning excludes a universal physical transformation that duplicates an
arbitrary unknown quantum state. No-broadcasting extends the restriction to
noncommuting mixed-state families. A simulator copying a known array violates
neither theorem: it copies a classical description. Our application is to
require physical-operation claims to specify input-state access, channels,
and assumptions instead of borrowing authority from array operations.
([Wootters and Zurek](https://doi.org/10.1038/299802a0),
[Barnum et al.](https://doi.org/10.1103/PhysRevLett.76.2818))

Gour and Spekkens formulate quantum reference frames as resources under
restrictions on allowed operations. Marvian and Spekkens analyze asymmetry
modes and additional constraints on state transformations. Their formal
settings require symmetries and operation classes; the available resources
matter. Thus the local finite relabeling/covariance check cannot by itself
establish a physical quantum-reference-frame resource theory or the complete
quantum free-energy principle. The original QRF counterweight group remains
unchanged.
([Gour and Spekkens](https://doi.org/10.1088/1367-2630/10/3/033023),
[Modes of asymmetry](https://doi.org/10.1103/PhysRevA.90.062110),
[Extending Noether's theorem](https://doi.org/10.1038/ncomms4821))

## Phenomenological reports require a measurement bridge

Petitmengin proposes a structured interview method and discusses the validity
of elicited descriptions. Lutz et al. provide a first-person-data design that
links reports to separately collected behavioral and physiological data. The
relevance here is methodological: an operational parameter named after an
experiential distinction is not itself a report or measurement of that
experience. A future empirical bridge would need an elicitation procedure,
coding rules, independent outcomes, and a defensible mapping to model variables.
([Petitmengin](https://doi.org/10.1007/s11097-006-9022-2),
[Lutz et al.](https://doi.org/10.1073/pnas.032658199))

Grossman frames mindfulness measurement as a problem requiring scrutiny.
Davidson and Kaszniak address self-report inference, comparison conditions,
and intervention description; Van Dam et al. critically evaluate definitions
and research claims. These sources support explicit construct and design
boundaries, not the equation of mindfulness, attentional performance,
metacognitive access, compassion, and realization. Their critique is not
evidence that all first-person reports are invalid.
([Grossman](https://doi.org/10.1016/j.jpsychores.2008.02.001),
[Davidson and Kaszniak](https://doi.org/10.1037/a0039512),
[Van Dam et al.](https://doi.org/10.1177/1745691617709589))

Lindahl et al. distinguish reported experiences from their interpretations and
impacts. Britton et al. explicitly measure dimensions of adverse experiences.
Our consequence for any future human interface is to specify safety monitoring
and functional impact separately from a theoretically valued experience.
Neither study supplies participants, prevalence estimates, clinical outcomes,
or a safety certification for this software. No simulation profile is offered
as a practice recommendation or an indicator of attainment.
([Lindahl et al.](https://doi.org/10.1371/journal.pone.0176239),
[Britton et al.](https://doi.org/10.1177/2167702621996340))

## Executable use and limits

The additions bind the existing statistical/proxy, Bayesian-model-reduction,
active-inference, QRF, quantum-surrogate, practice-boundary, and artifact-release
claim IDs. They introduce no claim IDs and do not change the source PDF hash.
The manifest and bibliography are checked for unique keys and identifiers,
schema conformance, valid claim bindings, and retained counterweight groups.
Manuscript discussion and supplement fragments explain the resulting
interpretation; source validation alone does not attest to generated outputs,
render quality, publication, or implementation of prospective methods.

The research agenda that follows is concrete: declare the contrast and its
sampling unit; preserve dependence when resampling; describe the null's
invariances; report Monte Carlo precision; test calibration sensitivity with
known failures; specify physical-operation assumptions; and require a separate
measurement bridge for experiential interpretation. These are constraints on
future stronger claims, not a promotion of the current evidence ceiling.
