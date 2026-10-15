# finite_compassion_scope

## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
finite_compassion_scope

## ModelAnnotation
Finite software surrogate inputs; not empirical evidence.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{"family": "finite_compassion_scope", "backend": "numpy_scipy", "consumer": "simulation.compassion_scope:build_compassion_scope_audit", "parameters": {"controllability": [0.95, 0.9, 0.1, 0.35, 0.55, 0.75], "stream_seed": 7, "audit_seed": 19, "steps": 96, "action_shuffle_count": 32, "dose_precisions": [0.0, 1.0, 2.0, 4.0, 8.0], "baseline_concern": 1.0, "influence_weight": 1.0, "baseline_precision": 1.0}, "claim_boundary": "finite deterministic software surrogate; not empirical evidence"}]
