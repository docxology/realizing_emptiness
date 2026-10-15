## GNNSection
FiniteSurrogate
## GNNVersionAndFlags
GNN v1
## ModelName
statistical_convergence
## ModelAnnotation
Finite quantum trajectory convergence experiment; not empirical evidence.
## StateSpaceBlock
input[1,type=float]
output[1,type=float]
## Connections
input>output
## InitialParameterization
settings=[{'family': 'statistical', 'backend': 'numpy_scipy', 'consumer': 'simulation.statistical_robustness:build_quantum_trajectory_convergence_audit', 'parameters': {'seed': 29, 'trajectory_counts': [16, 64, 128, 256, 512, 1024, 2048], 'too_few_count': 8, 'step_count': 16, 'total_time': 1.2}, 'claim_boundary': 'finite software convergence design; not empirical or physical qFEP evidence'}]
