# data/sources/ - agent conventions

- Source manifest is the provenance authority. `source_manifest.yaml` pins the
  primary-source PDF by `sha256`; the chain verifies the live file against this
  hash. Treat the pinned hash as the source of truth -- if the source genuinely
  changes, update the hash deliberately, do not loosen the check.
- Do not commit the source PDF or any large/secret data. Reference by hash, URL,
  and citation key only.
- Prefer repo-relative or external references in new content; avoid embedding
  machine-specific absolute paths. (The existing `local_pdf` field is a known
  per-machine pointer; the hash, not the path, is authoritative.)
- Both manifests must validate against their schemas in `../../schemas/` and pass
  `validate_outputs`. Keep `schema` version strings, citation keys, and
  `supports_claims` ids consistent with the claim crosswalk in `src/`.
- Integrity rules are binding: paraphrased locators and short excerpts only; no
  empirical, clinical, neural, ontological, awakening, practice-efficacy, or
  physical-qFEP claims. Keep `claim_scope` / `citation_boundary` wording intact.
