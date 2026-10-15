# GNN model specifications and execution

Generalized Notation Notation (GNN) is the model specification authority for
this project. Readable `.gnn.md` files declare the categorical QRF models and
the inputs to the finite, quantum, and statistical surrogate engines. The
registry validates these files before numerical execution. GNN provides a
shared model language and a checked route into the computation; it does not
establish the source paper's physical or empirical claims.

## One source for model inputs

The packaged declarations live in `src/modeling/specifications/`. The
`separation_constrained`, `opacified`, and `post_dual` specifications contain
explicit likelihood `A`, transition `B`, preference `C`, and initial-prior `D`
tensors, together with their QRF deployment labels and parameters. The
`qrf_boundary` specification supplies the shared boundary design. Other
specifications declare the canonical inputs to BMR, finite quantum models,
surrogate controls, and statistical experiments.

The `practice_mapping` declaration holds numerical intervention-delta metadata
used to construct the practice governance map. These mappings are not applied
to simulation state or interpreted as measured practice effects. Safety prose
and the prohibition on user-facing efficacy claims remain enforced in Python.

Model inputs belong in these specifications rather than parallel Python or
YAML defaults. Python retains numerical algorithms, mathematical constants,
input validation, and independently defined acceptance thresholds. The
manuscript's source and scholarship manifests remain provenance records;
they do not become GNN model parameters. The original paper digest and all
existing public claim ceilings still apply.

## From declaration to numerical result

`modeling.registry` uses the upstream `MarkdownGNNParser` and strict
`SemanticValidator`, then checks the project's execution contract. It rejects
duplicate or missing sections, incomplete parsing, malformed connections,
invalid dimensions, non-finite parameters, and unsupported backends. A
`ModelSpecification` binds the admitted inputs to the SHA-256 of their source
text.

For categorical models, upstream `build_canonical_pomdp_spec` validates the
explicit tensors. `B[next_state, previous_state, action]` is the declared
axis order; `A`, `B`, and `D` must describe valid probability distributions.
`C` contains preference scores and is not a probability distribution. The
project adapter passes the admitted tensors to the real `pymdp.Agent` calls,
deterministic diagnostics, and seeded trajectory sampling.

The other specifications declare `FiniteSurrogate` models with the
`numpy_scipy` backend. The existing NumPy/SciPy engines consume those
parameters and implement the finite computations. In particular, GNN parsing
does not supply a quantum inference engine: density matrices, channels,
contextuality tests, and quantum trajectories remain explicit local finite
methods with their own controls. The upstream native categorical execution
receipt is a bounded interoperability check, not a replacement for those
engines or a physical qFEP result.

## Runtime API

```python
from modeling import load_model, model_parameters

model = load_model("separation_constrained")
tensors = model.tensors
source_digest = model.source_hash
boundary = model_parameters("qrf_boundary")
```

`load_model` reads the current source content and returns a source-bound
specification with `parameters`, `tensors`, `family`, `backend`, and `consumer`
fields. Each result is independently copied; editing a returned dictionary
does not edit a packaged specification or a subsequent result. Missing files
and invalid declarations fail explicitly.

For controlled experiments, `specification_root(Path(...))` is a context
manager that selects a directory of real alternate `.gnn.md` files. Copy
the complete specification inventory, change the intended model, and call
the consumer inside that context. This preserves the same parser and
validation path and lets mutation tests demonstrate that a changed input
reaches the actual computation. Explicit runtime arguments remain available
where the consumer API declares them; they are experiment overrides, not
additional stored defaults.

## Authoring and validation

1. Start from a specification in the same model family. Preserve the ordered
   required GNN sections and give the file and `ModelName` the same identifier.
2. Declare concrete dimensions, valid connections, complete single-line
   parameter assignments, and the execution settings: `family`, `backend`,
   `consumer`, `parameters`, and `claim_boundary`.
3. For categorical models, update explicit `A/B/C/D` tensors consistently
   with their dimensions and canonical axis order. For finite models, update
   the parameters consumed by the named engine.
4. Exercise the real consumer and a discriminating negative control. A
   grammar-valid declaration alone does not demonstrate that an input was
   consumed or that a scientific interpretation follows.
5. Regenerate the chain and run the canonical checks in
   [AGENTS.md](../AGENTS.md). Inspect `output/data/gnn_model_audit.json` and
   the `gnn_model_audit_ok` gate alongside the model-specific audits. Then
   recompose and render any affected manuscript or figure through the
   [running guide](running-the-chain.md).

The model audit records source identity, admitted model contracts, and bounded
execution checks. Source-hash and mutation controls are required because a
valid file that is ignored by its consumer is not a working integration.
The [validation contract](validation-contract.md) specifies the surrounding
artifact gates; [API contracts](api-contracts.md) explain migration.

## Installation, packaging, and upstream provenance

Python 3.11 through 3.14 is supported. Installation uses the frozen `uv.lock`
through the [setup instructions](running-the-chain.md#setup). The dependency
is `generalized-notation-notation` 4.1.0, pinned to upstream commit
`46459949944e3217f8a6a804d4ff8c52829ef275`; the source is the
[Generalized Notation Notation repository](https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation).
`src/modeling/upstream.json` records the repository, revision, parser,
validator, compiler, and dependency license. The upstream Python markers use
`inferactively-pymdp` 1.0.4 on Python 3.11 and 1.0.3 on Python 3.12 and later.

The pin was selected from the canonical GitVault checkout at
`Username/ActiveInferenceInstitute/Public/Generalized_Notation_Notation`.
Portable installations resolve that revision through the dependency lock.

The wheel includes the GNN specifications, `catalog.json`, and `upstream.json` as package
resources. A built-wheel smoke check must load these resources outside the
source checkout; a source-tree import cannot establish packaging completeness.
The source distribution also preserves the reproduction inputs described in
the [release validation record](release-validation.md).

This repository's own license is MIT. The upstream GNN dependency declares
CC-BY-NC-SA-4.0, as recorded in its provenance file; its license is separate
from this repository's license. Neither software license is an empirical
validation or an endorsement of the manuscript's scientific interpretations.
