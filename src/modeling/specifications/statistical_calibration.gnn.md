## GNNSection
FiniteSurrogate
## GNNVersionAndFlags
GNN v1
## ModelName
statistical_calibration
## ModelAnnotation
Synthetic normal-generator effect calibration; not empirical statistical power.
## StateSpaceBlock
input[1,type=float]
output[1,type=float]
## Connections
input>output
## InitialParameterization
settings=[{'family': 'statistical', 'backend': 'numpy_scipy', 'consumer': 'simulation.statistical_robustness:build_effect_size_test_calibration_audit', 'parameters': {'seed': 4242, 'positive_shift': 1.0, 'sample_size': 128, 'normal_mean': 0.0, 'normal_scale': 1.0, 'positive_seed_offset': 1000, 'sign_flip_seed_offset': 2000, 'permutation_seed_offset': 1, 'bootstrap_seed_offset': 2, 'permutation_draws': 1024, 'bootstrap_draws': 2048}, 'claim_boundary': 'finite synthetic calibration; not empirical statistical power'}]
