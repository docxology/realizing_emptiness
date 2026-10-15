# finite_alternative_bmr

## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
finite_alternative_bmr

## ModelAnnotation
Finite software surrogate inputs; not empirical evidence.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{"family": "finite_alternative_bmr", "backend": "numpy_scipy", "consumer": "formalism.review_response_bmr:build_bmr_alternative_prior_audit", "parameters": {"access_grid": [0.0, 0.25, 0.5, 0.75, 1.0], "precision_grid": [0.2, 1.0, 2.0, 4.0]}, "claim_boundary": "finite deterministic software surrogate; not empirical evidence"}]
