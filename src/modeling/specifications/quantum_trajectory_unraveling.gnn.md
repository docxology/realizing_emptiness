## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_trajectory_unraveling

## ModelAnnotation
Finite deterministic quantum-information surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_trajectory_unraveling', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_quantum_trajectory_unraveling', 'parameters': {'seed': 404, 'trajectory_count': 1024, 'step_count': 30, 'total_time': 3.0, 'rates': [0.0, 0.12, 0.3, 0.6], 'hamiltonian_z': 0.35, 'hamiltonian_zz': 0.2}, 'claim_boundary': 'Finite quantum-information software surrogate; not empirical evidence, not a physical qFEP or clinical claim.'}]
