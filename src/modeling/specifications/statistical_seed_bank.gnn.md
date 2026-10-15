## GNNSection
FiniteSurrogate
## GNNVersionAndFlags
GNN v1
## ModelName
statistical_seed_bank
## ModelAnnotation
Independent finite synthetic normal-generator calibration repetitions; not empirical power.
## StateSpaceBlock
input[1,type=float]
output[1,type=float]
## Connections
input>output
## InitialParameterization
settings=[{'family': 'statistical', 'backend': 'numpy_scipy', 'consumer': 'simulation.statistical_robustness:build_seed_bank_calibration', 'parameters': {'seed': 104242, 'repetitions': 128, 'positive_shift': 1.0, 'seed_stride': 10, 'sample_size': 64, 'normal_mean': 0.0, 'normal_scale': 1.0, 'bootstrap_seed_offset': 1, 'permutation_seed_offset': 2, 'bootstrap_draws': 512, 'permutation_draws': 511}, 'claim_boundary': 'finite synthetic calibration design; not empirical statistical power'}]
