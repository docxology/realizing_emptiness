# Changelog

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
