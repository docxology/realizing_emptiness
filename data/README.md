# data/

Committed input data for the Realizing Emptiness surrogates. This holds source
provenance only; it is small, text, and version-controlled. Generated artifacts
never live here -- they go to `output/data/` and are disposable. The provenance
recorded here anchors the project to the Sandved-Smith et al. 2026 "There is no
self-evidence" paper without reproducing it.

## Contents

- `sources/` - source provenance manifests (primary-source hash pin + scholarship
  matrix). See `sources/README.md`.

## Pipeline fit

The chain reads `sources/source_manifest.yaml` first: `generate_formalisms.py`
verifies the primary-source PDF hash against the pinned `sha256` before building
any formalism. Both manifests are validated against their schemas in
`../schemas/` during `validate_outputs`. Nothing in this folder asserts empirical,
clinical, neural, ontological, awakening, practice-efficacy, or physical-qFEP
evidence -- it is provenance and citation context only.
