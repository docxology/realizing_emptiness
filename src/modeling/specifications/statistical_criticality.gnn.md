## GNNSection
FiniteSurrogate
## GNNVersionAndFlags
GNN v1
## ModelName
statistical_criticality
## ModelAnnotation
Finite shuffled-null experiment and planted geometric calibration; not empirical neural criticality.
## StateSpaceBlock
input[1,type=float]
output[1,type=float]
## Connections
input>output
## InitialParameterization
settings=[{'family': 'statistical', 'backend': 'numpy_scipy', 'consumer': 'simulation.criticality:build_criticality_stochastic_ensemble', 'parameters': {'shuffle_seed_offset': 91, 'bootstrap_seed_offset': 92000, 'bootstrap_draws': 2048, 'planted_branching_ratios': {'subcritical': 0.5, 'critical': 1.0, 'supercritical': 1.5}, 'calibration_length': 8, 'calibration_start': 1.0}, 'claim_boundary': 'finite trajectory diagnostics and synthetic calibration; not empirical neural criticality'}]
