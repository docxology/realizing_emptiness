# GNN model authority

`specifications/` supplies the model inputs consumed by the numerical engines.
`catalog.json` binds each declaration to its consumer; `upstream.json` pins the
external GNN implementation. `registry.py` admits sources through the upstream
parser, semantic checks, and categorical tensor contract. `audit.py` records
source and implementation hashes plus real upstream categorical execution.

See the [modeling guide](../../docs/gnn-modeling.md) for authoring, backend scope,
controlled overrides, package resources, and validation. The root
[source contract](../../AGENTS.md) governs scientific claims and regeneration.
