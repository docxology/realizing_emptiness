# Changelog

## 2.0.0 - 2026-10-14

- Consolidate the public runtime API around `pymdp_runtime_dependency_check`;
  coordinate claim IDs, gates, schemas, dashboard keys and documentation.
- Publish current-only data contracts: profile comparison v3, runtime log v2,
  criticality report/ensemble v2, dashboard payload v2 and stochastic effect-size audit v2.
- Remove unused statistical interval fields, duplicate effect-size calculations,
  the coarse criticality heuristic and its single-trace chart. Keep 60
  source-mapped figures and distinguish descriptive random-control summaries
  from histogram-preserving shuffled branching contrasts.
- Require a strict majority of profiles to separate on measured branching,
  reconstruct acceptance from trajectory records, and reject stale fields.
- Reject invalid activity counts/avalanche thresholds and unresolved figure
  bindings. Placement audit v2 checks every image against the current registry;
  strict composition rejects unselected fragments. Remove three superseded
  manuscript fragments and an unused track.
- Regenerate the manuscript, documentation, figures and release artifacts while
  preserving the pinned source digest and finite-software evidence ceilings.

## 1.2.0 - 2026-10-14

- Expand the curated scholarship ledger from 93 to 125 entries and the
  bibliography from 98 to 130 entries, with manuscript synthesis and a
  source-linked account of the search scope and limitations.
- Estimate mean-difference and tie-aware Cliff's-delta uncertainty by resampling
  complete independent runs; add paired real-minus-shuffled branching intervals.
- Record permutation counts, finite resolution and familywise Monte Carlo
  bounds around Holm decisions, with unresolved decisions shown explicitly.
- Add 128-seed synthetic rejection/coverage calibration, exact binomial
  intervals and an absent-effect negative control.
- Redesign the effect forest and add paired-contrast and calibration figures,
  bringing the source-mapped figure set to 61. Document all estimands,
  resampling assumptions and finite-grid BMR limitations.
- Update validation schemas, regression tests, release metadata and pinned
  GitHub Actions; retain the original source hash and scientific claim ceilings.

## 1.1.0 - 2026-10-14

- Reject missing, malformed, structurally invalid, and truncated validation
  schemas; validate artifact structures before reading nested fields.
- Pin the source digest independently of the editable source manifest.
- Make strict manuscript validation read-only and detect composition drift,
  unknown citations, unresolved references, and missing figure files.
- Resolve figure links from composed Markdown and rebase them during hydration.
  Keep editor/agent guides out of the manuscript and preserve unmanaged files.
- Validate numerical boundary inputs and construct dimensionally consistent QRF
  deployments for finite screens other than the default six channels.
- Include the software license and research reproduction inputs in source
  distributions, declare Python 3.10-3.14 support, and add frozen-lock CI.
- Prevent pytest from loading dependencies from a different local environment.
- Pin the working SciPy wheel for Python 3.10 on macOS after reproducing the
  newer wheel's PROPACK loader failure; preserve newer runtimes' dependencies.
- Bootstrap the complete analysis chain from source-only archives, with
  prerequisites generated before use and final validation counts rehydrated.
- Require patched Pillow releases after the dependency audit identified
  advisories against the previous imaging-library lock.
- Use histogram-preserving per-run shuffled observations for branching controls;
  distinguish the separate random controls used for other trajectory metrics.
- Correct pooled-mean confidence-interval labels and reject exponent overflow
  at JSON boundaries; keep KL finite for tiny positive prior probabilities.
- Bind raster export to Agg for consistent standalone and test figure bytes.
- Refresh the manuscript, figures, dashboard, release metadata, and operating
  instructions while preserving the existing finite-surrogate evidence ceiling.

## 1.0.0 - 2026-06-24

Initial versioned release, archived at
[10.5281/zenodo.20834847](https://doi.org/10.5281/zenodo.20834847).
