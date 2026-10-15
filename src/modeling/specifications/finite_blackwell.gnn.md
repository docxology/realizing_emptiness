# finite_blackwell

## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
finite_blackwell

## ModelAnnotation
Finite software surrogate inputs; not empirical evidence.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{"family": "finite_blackwell", "backend": "numpy_scipy", "consumer": "simulation.blackwell_ordering:build_blackwell_bayes_risk_audit", "parameters": {"prior": [0.5, 0.5], "channel": [[0.8, 0.2], [0.2, 0.8]], "grid_steps": 21, "named_garblings": [["weak_garbling", 0.85, 0.85], ["partial_garbling", 0.7, 0.7], ["strong_garbling", 0.6, 0.6], ["complete_erasure", 0.5, 0.5]]}, "claim_boundary": "finite deterministic software surrogate; not empirical evidence"}]
