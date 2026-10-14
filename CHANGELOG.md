# Changelog

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
