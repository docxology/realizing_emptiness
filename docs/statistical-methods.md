# Statistical estimands and finite simulation uncertainty

This project studies a specified software generator. A trajectory run is the
replication unit; its dependent timesteps are never counted as separate subjects
or independent samples. Neither a large effect nor a small permutation p-value
establishes empirical, neural, clinical, practice-efficacy or physical-qFEP
evidence. The [scholarship synthesis](scholarship-expansion.md) explains the
methodological sources and counterweights. This document specifies the executed
methods in `simulation.resampling`, `statistical_robustness` and `criticality`.

## Estimands and designs

| Output | Estimand | Resampling unit and reference |
| --- | --- | --- |
| Stochastic mean contrast | Mean profile run statistic minus mean random-null run statistic | Independently resample complete runs in each group. |
| Cliff's delta | Probability a profile statistic exceeds a null statistic minus the reverse probability, with ties contributing zero | Recompute the rank-based statistic after independently resampling both run groups. |
| Branching paired contrast | Mean original-minus-shuffled branching ratio | Resample intact original/shuffle run pairs; each run has one fixed observation permutation. |
| BMR robustness | Pruning fraction and mean Delta F over the specified finite noise grid | Uniform resampling of designed grid rows is a conditional design diagnostic, not subject-sampling uncertainty. Exact grid minima, maxima and prune counts are also recorded. |

The stochastic profile/random-null comparison is not the same null as the
histogram-preserving branching shuffle. The former changes the generating
process; the latter preserves a trajectory's empirical observation histogram
and disrupts its order. Neither is a universal test of criticality or a
justification for treating coded observation labels as neural event counts.

## Bootstrap intervals

The contrast artifact uses 2,048 seeded percentile replicates for both mean
differences and Cliff's delta. Intact pairs are sampled together for the
branching contrast. Each reported interval belongs to its named contrast;
group means are descriptive point estimates.
Confidence level is 95% pointwise, not simultaneous across profiles or metrics.
Percentile intervals can have imperfect finite-sample coverage, particularly
for discrete, skewed or small samples. A degenerate interval on a constant
fixture is an exact property of that empirical resampling distribution, not
evidence that uncertainty is universally zero.

## Random-permutation precision and multiplicity

For each of eighteen profile/metric contrasts the independent-run label test
uses the absolute difference in means and 4,095 random permutations sampled
with replacement. It reports `(exceedances + 1)/(draws + 1)`, with resolution
1/4,096. Floating-point ties use a relative tolerance of 100 machine epsilons.
The exchangeability assumption is equality of the relevant run distributions
under the reference null; equal means alone do not establish it. The correction
does not repair an invalid null or dependence design.

All eighteen contrasts form one declared Holm family, including metrics not
selected for the compact forest. Exceedance counts, seeds, budgets, plug-in
binomial Monte Carlo standard errors and Clopper-Pearson intervals are saved.
Each tail interval uses confidence `1 - 0.05/18`; a union bound therefore gives
at least 95% joint coverage of the eighteen conditional permutation tail
probabilities. Applying the coordinatewise-monotone Holm map to both endpoint
vectors bounds the corresponding adjusted probabilities on that event. A
diamond marks a threshold decision unresolved by those bounds. These are
numerical Monte Carlo bounds, not confidence intervals for an effect or a
probability that a scientific hypothesis is true. At an exceedance boundary,
the plug-in standard error can be zero; the exact interval remains informative.

## Seed-bank calibration

The generator check uses 128 prespecified independent seed sets, 64 runs per
group, 512 bootstrap replicates and 511 permutations per comparison. For each
seed it generates a standard-normal baseline, an independent zero-shift sample
and an independent unit-shift sample. Saved interval endpoints support an audit
of coverage against the known generator truth. Rejection uses alpha 0.05.
Coverage and rejection frequencies have exact 95% binomial intervals and
Monte Carlo standard errors. These intervals describe finite repetition error
under this normal generator only; they do not certify nonnormal generators,
heteroscedastic models, correlated runs, real-subject power or universal coverage.

The software controls require at least 32 repetitions, a null-rejection upper
bound no larger than 0.25, and an injected-effect rejection lower bound at least
0.75. These deliberately broad qualification limits detect a broken test or
removed signal; they are not declarations of nominal 5% error control. Actual
coverage and its uncertainty are reported without forcing every repetition to
cover. Removing the injected shift must fail the headline calibration verdict.
The original planted branching, sign-flip and collapsed-observation controls
remain in force.

## Scope and extensions

The calibration is a frequentist finite-generator diagnostic, not Bayesian
simulation-based calibration. Block/stationary bootstrap, dependence-adaptive
stepdown, posterior calibration, and proper scoring are discussed in the
expanded scholarship as possible future methods; they are not silently claimed
as current implementations. Multi-shuffle branching uncertainty, wider
generator families and preregistered external adapters remain future work.

See the canonical commands in [AGENTS.md](../AGENTS.md), the
[validation contract](validation-contract.md), and the generated
[method inventory](method-inventory.md) for the executable verification path.
