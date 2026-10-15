# finite_markov_blanket

## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
finite_markov_blanket

## ModelAnnotation
Finite software surrogate inputs; not empirical evidence.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{"family": "finite_markov_blanket", "backend": "numpy_scipy", "consumer": "simulation.markov_blanket:build_markov_blanket_discovery_audit", "parameters": {"internal": [0, 1], "blanket": [2, 3], "external": [4, 5], "edges": [[0, 1, 0.05], [0, 2, 0.4], [1, 2, 0.2], [1, 3, 0.1], [2, 3, 0.3], [2, 4, 0.45], [2, 5, 0.3], [3, 5, 0.25], [4, 5, 0.05]], "size": 6, "diagonal": 2.0, "threshold_steps": 500, "ensemble_samples": 200, "ensemble_noise": 0.25, "ensemble_seed": 0}, "claim_boundary": "finite deterministic software surrogate; not empirical evidence"}]
