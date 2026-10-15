# finite_classical_data_processing

## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
finite_classical_data_processing

## ModelAnnotation
Finite software surrogate inputs; not empirical evidence.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{"family": "finite_classical_data_processing", "backend": "numpy_scipy", "consumer": "simulation.classical_data_processing:build_classical_data_processing_audit", "parameters": {"external_prior": [0.3333333333333333, 0.3333333333333333, 0.3333333333333333], "blanket_given_external": [[0.8, 0.1, 0.1], [0.1, 0.8, 0.1], [0.1, 0.1, 0.8]], "lossy_merge": [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]], "lossy_partial": [[0.9, 0.1], [0.5, 0.5], [0.1, 0.9]]}, "claim_boundary": "finite deterministic software surrogate; not empirical evidence"}]
