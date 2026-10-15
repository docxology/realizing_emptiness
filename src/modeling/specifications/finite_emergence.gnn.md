# finite_emergence

## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
finite_emergence

## ModelAnnotation
Finite software surrogate inputs; not empirical evidence.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{"family": "finite_emergence", "backend": "numpy_scipy", "consumer": "simulation.emergence:build_separation_prior_emergence_audit", "parameters": {"empowerment_grid": [0.0, 0.25, 0.5, 0.75, 1.0], "seed": 5, "steps": 64, "channels": 6, "revision_seed": 11, "revision_margin": 0.1, "regime_fraction": 0.5, "self_fraction": 0.5, "action_shuffle_count": 32}, "claim_boundary": "finite deterministic software surrogate; not empirical evidence"}]
