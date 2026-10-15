# finite_bmr

## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
finite_bmr

## ModelAnnotation
Finite software surrogate inputs; not empirical evidence.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{"family": "finite_bmr", "backend": "numpy_scipy", "consumer": "simulation.bmr:run_bmr_sweep", "parameters": {"access_grid": [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0], "precision_grid": [0.2, 0.5, 1.0, 2.0, 4.0], "accuracy_base": 0.55, "access_accuracy": 0.35, "sigma_accuracy": 0.3, "complexity_base": 0.25, "reduced_complexity": 0.15, "noise_base": 0.02}, "claim_boundary": "finite deterministic software surrogate; not empirical evidence"}]
