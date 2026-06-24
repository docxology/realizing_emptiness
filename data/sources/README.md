# data/sources/

Source provenance for the Realizing Emptiness surrogates: the pinned primary
source and the wider scholarship matrix that scopes citation context. These
manifests anchor the project to the Sandved-Smith et al. 2026 "There is no
self-evidence" paper and its background literature -- as scoped scholarly
context, not as empirical, clinical, neural, ontological, awakening,
practice-efficacy, or physical-qFEP evidence.

## Files

| File | Purpose |
| --- | --- |
| `source_manifest.yaml` | Primary source record: title, authors, OSF URL, pinned `sha256` of the source PDF, citation key, integrity rules (paraphrase-only, surrogate claim scope). |
| `scholarship_manifest.yaml` | ~47 scholarship entries (primary preprint, peer-reviewed articles, monographs, preprints) with roles, evidence status, tracks, and the claims each supports. |

## Pipeline fit

`generate_formalisms.py` reads `source_manifest.yaml` and verifies the live PDF's
hash against the pinned `sha256` before building formalisms; the scholarship
manifest feeds the source matrix and claim-support audits. Both files validate
against `../../schemas/source_manifest.schema.json` and
`../../schemas/scholarship_manifest.schema.json` during `validate_outputs`.
