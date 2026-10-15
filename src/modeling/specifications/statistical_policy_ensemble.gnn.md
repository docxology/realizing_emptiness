## GNNSection
FiniteSurrogate
## GNNVersionAndFlags
GNN v1
## ModelName
statistical_policy_ensemble
## ModelAnnotation
Finite seeded ensemble design consuming separately declared categorical profiles; not empirical evidence.
## StateSpaceBlock
input[1,type=float]
output[1,type=float]
## Connections
input>output
## InitialParameterization
settings=[{'family': 'statistical', 'backend': 'numpy_scipy', 'consumer': 'simulation.stochastic:build_stochastic_policy_ensemble', 'parameters': {'seed': 101, 'runs': 128, 'steps': 48, 'channels': 6, 'profile_seed_stride': 10000, 'null_seed_offset': 500000}, 'claim_boundary': 'finite stochastic ensemble design; not empirical or practice-outcome evidence'}]
