# Release validation

## Scope

Version 2.0.0 covers source, finite numerical surrogates, source and claim
contracts, manuscript composition, visualization pipeline, documentation,
distribution contents, and publication metadata. These checks establish
software behavior only. The empirical and independent-reproduction boundaries
in the [validation contract](validation-contract.md) remain in force.

The current release consolidates runtime APIs and versioned data contracts,
removes unused statistical fields and a coarse heuristic chart, and requires
a strict majority of profiles to separate on measured branching. Validation
reconstructs the numerical acceptance from trajectory records. The 125-source
scholarship ledger, run-level contrast intervals, finite-permutation bounds
and 128-seed calibration remain documented. The figure set contains 60 figures.
The [current contracts](api-contracts.md), [statistical methods](statistical-methods.md)
and [scholarship synthesis](scholarship-expansion.md) record assumptions,
selection scope and limitations. These are methodological software additions;
the original source digest and empirical evidence ceilings remain binding.

## Reproduced findings and repairs

| Surface | Reproduced defect | Repair |
| --- | --- | --- |
| Schemas | A truncated schema was loaded as an empty object and accepted arbitrary data. | Reject invalid schemas and validate nested artifact structure before consumption. |
| Source integrity | Replacing both the source and its manifest digest passed the source check. | Compare both against the independently pinned original digest. |
| Manuscript | Strict validation wrote an output file and missed stale composition. | Read-only comparison with the fragments, plus reference, citation, and image checks. |
| Figure links | Composed Markdown used paths that did not resolve from its directory. | Resolve source links from `docs/manuscript/`; rebase hydrated copies to `output/figures/`. |
| Hydration | Editor guides entered the rendered manuscript; every target file was deleted. | Hydrate numbered sections and rendering support files; preserve unmanaged files. |
| Numerical APIs | Non-six-channel defaults had incompatible dimensions; non-finite precision and invalid logarithm bases were accepted. | Validate inputs with discriminating regression examples. |
| Visual audit | Missing layout telemetry defaulted to success; minimum type size was declared rather than measured. | Clear telemetry on every run, fail on missing telemetry, and measure rendered text sizes. |
| Dashboard | Failed/pending validation used the passing-state color, and the report lagged generation. | Use semantic status colors and refresh the dashboard after validation. |
| Distribution | The wheel lacked a license; the source archive lacked reproduction inputs. | Include the license, sources, schemas, tests, manifests, documentation, and lockfile. |
| Operations | Render commands referenced a removed template script; counts and release identity were stale. | Update canonical instructions, add CI, and distinguish each version from the older DOI. |
| Test runtime | Pytest prepended the old local environment's dependencies ahead of the selected environment. | Keep dependency resolution in the selected runtime and assert imported package locations. |
| macOS / Python 3.10 | SciPy 1.15.x could not load its PROPACK binary on the current macOS loader. | A scoped SciPy 1.14.1 dependency marker uses the wheel verified by a real linear-program solve. |
| Fresh source tree | Statistics consumed a sensitivity file produced later; readiness and validation counts depended on previous outputs. | Generate prerequisites first, declare provisional readiness explicitly, and hydrate counts after validation. A real source-only chain regression exercises the complete path. |
| Dependency advisories | The locked Pillow 12.2.0 had 25 reported advisories. | Require Pillow 12.3.0 or newer and re-audit the installed dependency set. |
| Independent review | Uniform random draws were described as a shuffled branching null; a pooled-mean interval was labeled as a mean-difference interval. | Use per-run observation permutations for branching, distinguish the other random controls, and correct the interval estimand in figure and prose. |
| Extreme numeric inputs | JSON exponent overflow admitted infinity; tiny positive KL priors overflowed an intermediate ratio. | Reject non-finite parsed floats and compute KL using log differences. |
| Platform rendering | macOS standalone export and tests selected different Matplotlib backends and produced different PNG bytes. | Bind raster export to Agg and test an explicitly conflicting backend selection. |

## Verification

The canonical verification commands are in [AGENTS.md](../AGENTS.md).
The full chain regenerates analysis artifacts and figures. The separate
[render step](running-the-chain.md#render-and-manual-qa) produces PDF, HTML,
and EPUB. The release checks also build and install a wheel, unpack and run
the source distribution, replay generated artifacts, and inspect the rendered
surfaces. The corruption corpus rejected 171 malformed JSON, nested-structure,
and PNG cases against a passing baseline. Numeric regressions additionally
exercise non-finite constants, exponent overflow, and finite extreme values.
Versioned release notes record the final test totals, coverage, artifact checks,
and publication receipts. Full test runs require the documented analysis-chain
prerequisite; an unpacked source archive intentionally omits generated analysis.

## Publication boundary

The local artifact release manifest records reproducibility inputs; it is not
a receipt for GitHub publication or Zenodo deposition. Version 1.0.0 retains
its archived DOI. Version 2.0.0 uses its GitHub version URL until a new DOI is
actually assigned. A public repository or release does not establish independent
or blinded reproduction, physical qFEP realization, neural measurement, clinical
benefit, or contemplative attainment.
