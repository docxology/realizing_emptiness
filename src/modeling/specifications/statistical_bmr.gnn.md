## GNNSection
FiniteSurrogate
## GNNVersionAndFlags
GNN v1
## ModelName
statistical_bmr
## ModelAnnotation
Finite BMR grid resampling design; not empirical evidence.
## StateSpaceBlock
input[1,type=float]
output[1,type=float]
## Connections
input>output
## InitialParameterization
settings=[{'family': 'statistical', 'backend': 'numpy_scipy', 'consumer': 'simulation.statistical_robustness:build_bmr_robustness_resampling_audit', 'parameters': {'delta_seed': 8100, 'pruning_seed': 8200, 'bootstrap_draws': 1024}, 'claim_boundary': 'finite software grid resampling; not empirical evidence'}]
