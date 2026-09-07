# Methods (IMRAD: Methods)

Per-track fragments for the Methods. They compose into `docs/manuscript/02_methods.md` via the
sheaf, in the track order declared in `docs/manuscript/sheaf/manifest.yaml`
(`qfep, qrf, separation_prior, bmr, pymdp`).
`_lead.md` is the section signpost, rendered before the first subsection.

Fragments present:
- `_lead.md` - signpost describing the finite chain built in dependency order.
- `qfep.md` - equation registry (paper eq. 1-14) and implemented finite quantum extension engines.
- `qrf.md` - finite QRF boundary screen (b0-b5) and channel/label relabeling semantics.
- `separation_prior.md` - separation prior as an admissible QRF subspace and its emergence audit construction; measured emergence and net-value figures are reported in Results.
- `bmr.md` - Bayesian model reduction sweep and sensitivity grid over the separation prior.
- `pymdp.md` - profile-specific pymdp generative models and the four linked runtime contracts.

Do not hand-edit the composed `docs/manuscript/02_methods.md`; edit fragments here.
