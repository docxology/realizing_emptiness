# Current API and data contracts

Version 3.0.0 makes GNN declarations authoritative for model inputs. Consumers
must regenerate artifacts with the installed package and update their field
lookups to the contracts below. Reusing an artifact from an earlier release
fails schema validation. The canonical commands are in [AGENTS.md](../AGENTS.md).

## GNN model interface and migration

Python 3.11-3.14 replaces the previous Python 3.10 floor. The frozen dependency
set pins upstream GNN; `pymdp` is 1.0.4 on Python 3.11 and 1.0.3 on later
supported interpreters. See [GNN modeling](gnn-modeling.md) for provenance,
packaging, authoring, and the distinct categorical and finite execution paths.

`modeling.load_model(id)` returns a `ModelSpecification` with source hash,
family, backend, consumer, parameters, and canonical categorical tensors where
applicable. `modeling.model_parameters(id)` returns an independent parameter
dictionary. `modeling.specification_root(path)` selects real alternate files
for controlled experiments; it restores the prior root on context exit.

`ProfileSpec` identifies its authoritative GNN model instead of carrying
independent numerical defaults. Update callers that constructed profiles with
the old numerical fields to use the corresponding model identifier and
declaration. Do not recreate the removed defaults in YAML or Python. The
model audit at `output/data/gnn_model_audit.json` is checked by
`gnn_model_audit_ok`; existing model-specific and claim-ceiling gates still
apply. This changes specification authority without introducing new public
scientific claim IDs.

## Runtime dependency check

`simulation.pymdp_runtime_dependency_check()` invokes the real installed
`inferactively-pymdp` agent and records the required version, posterior and
policy inference, and captured warnings. It returns
`realizing_emptiness.pymdp_runtime_dependency_check.v1`.

| Consumer | Current contract |
| --- | --- |
| Profile comparison | `realizing_emptiness.pymdp_profile_comparison.v3`, field `runtime_dependency_check` |
| Runtime diagnostics | `realizing_emptiness.pymdp_runtime_diagnostics_log.v2`, field `runtime_dependency_check` |
| Runtime controls | `runtime_dependency_ok`, `runtime_warnings_captured` |
| Dashboard | Payload v3 adds the source-bound `modeling` summary and retains `runtime_warning_count` |

The pinned constructor emits one captured warning on pymdp 1.0.3 and none
on 1.0.4. Both the runtime gate and nested JSON schema enforce that version-specific
record; missing records and unexpected counts fail. A zero count on 1.0.4 is an
observed runtime outcome, not an omitted diagnostic.
| Claim / gate | `pymdp_runtime_dependency` / `pymdp_runtime_dependency_ok` |

The dependency check establishes finite runtime behavior. It supplies no
empirical evidence for the paper's scientific predictions.

## Statistical estimands

`realizing_emptiness.stochastic_effect_size_audit.v2` records descriptive
`profile_mean` and `null_mean` point estimates. Its uncertainty fields are
`difference_ci95_low/high` for the profile-minus-null mean difference and
`cliffs_ci95_low/high` for tie-aware Cliff's delta. Seeds, draw counts,
permutation exceedances and finite Monte Carlo bounds remain explicit.
Every row has a closed schema: an unrecognized field is rejected.

`simulation.resampling.bootstrap_contrast` and `permutation_test` implement
the shared numerical methods used by both production contrasts and calibration.
The [statistical methods guide](statistical-methods.md) specifies the independent
and paired sampling units, multiplicity assumptions and interpretation limits.

## Measured branching

`realizing_emptiness.criticality_proxy_report.v2` contains measured branching,
the derived absolute distance from one, avalanche sizes and a bounded shape
diagnostic. A single trace supplies descriptive data only.

`realizing_emptiness.criticality_stochastic_ensemble.v2` compares complete
original trajectories with their own seeded histogram-preserving shuffles.
The readiness gate reconstructs the numerical summaries from trajectory
records and requires a strict majority of profiles to have disjoint original
and shuffled branching intervals. Observation entropy and switch-rate plots
describe separate independently sampled random controls; they do not determine
branching readiness. The figure set contains 60 source-mapped figures.

Activity counts and avalanche thresholds must be finite and non-negative.
The APIs raise `ValueError` for invalid inputs. These are software-trajectory
diagnostics, not empirical measurements of neural criticality.

## Manuscript and source map

The sheaf manifest selects the active fragments. Consolidated validation,
visualization and limitations material resides in `sections/supplement/validation.md`;
only manifest-selected fragments belong in the section directories. Every
figure binding must resolve to an actual source-map figure. Composition,
hydration, figure regeneration and final rendering are separate observable
steps, described in [Running the chain](running-the-chain.md). Placement audit
v2 records any unregistered image paths and accepts only the current control set.
