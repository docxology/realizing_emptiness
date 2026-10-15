## GNNSection
FiniteSurrogate
## GNNVersionAndFlags
GNN v1
## ModelName
statistical_effects
## ModelAnnotation
Finite independent-run resampling experiment design; not empirical evidence.
## StateSpaceBlock
input[1,type=float]
output[1,type=float]
## Connections
input>output
## InitialParameterization
settings=[{'family': 'statistical', 'backend': 'numpy_scipy', 'consumer': 'simulation.statistical_robustness:build_stochastic_effect_size_audit', 'parameters': {'bootstrap_seed': 7400, 'bootstrap_draws': 2048, 'permutation_seed': 7300, 'permutation_metric_seed_stride': 17, 'permutation_draws': 4095}, 'claim_boundary': 'finite software resampling design; not empirical evidence'}]
