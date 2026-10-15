## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_qfep_boundary_hamiltonian_dynamics

## ModelAnnotation
Finite deterministic quantum-information surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_qfep_boundary_hamiltonian_dynamics', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_qfep_boundary_hamiltonian_dynamics', 'parameters': {'time_count': 21, 'decoherence_rate_count': 4, 'time_bounds': [0.0, 3.0], 'rates': [0.0, 0.12, 0.3, 0.6], 'hamiltonian_z': 0.35, 'hamiltonian_zz': 0.2}, 'claim_boundary': 'Finite quantum-information software surrogate; not empirical evidence, not a physical qFEP or clinical claim.'}]
