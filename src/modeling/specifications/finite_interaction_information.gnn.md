# finite_interaction_information

## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
finite_interaction_information

## ModelAnnotation
Finite software surrogate inputs; not empirical evidence.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{"family": "finite_interaction_information", "backend": "numpy_scipy", "consumer": "simulation.interaction_information:build_interaction_information_boundary_audit", "parameters": {"internal_fidelity": 0.85, "external_fidelity": 0.8}, "claim_boundary": "finite deterministic software surrogate; not empirical evidence"}]
