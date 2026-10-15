# finite_sensitivity

## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
finite_sensitivity

## ModelAnnotation
Finite software surrogate inputs; not empirical evidence.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{"family": "finite_sensitivity", "backend": "numpy_scipy", "consumer": "simulation.sensitivity:build_sensitivity_grid", "parameters": {"access_grid": [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0], "precision_grid": [0.2, 0.5, 1.0, 2.0, 4.0], "accuracy_base": 0.55, "access_accuracy": 0.35, "sigma_accuracy": 0.3, "complexity_base": 0.25, "reduced_complexity": 0.15, "noise_base": 0.02, "noise_grid": [0.0, 0.05, 0.1, 0.2, 0.25, 0.35, 0.4], "retained_noise_penalty": 0.18, "full_complexity_noise": 0.1, "full_noise": 0.08, "reduced_accuracy_noise": 0.05, "reduced_complexity_noise": 0.05, "reduced_noise": 0.14, "separation_scale": 4.0}, "claim_boundary": "finite deterministic software surrogate; not empirical evidence"}]
