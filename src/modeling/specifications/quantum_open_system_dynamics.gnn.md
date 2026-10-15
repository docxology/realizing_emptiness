## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_open_system_dynamics

## ModelAnnotation
Finite deterministic quantum-information surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_open_system_dynamics', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_quantum_open_system_dynamics', 'parameters': {'time_count': 21, 'decoherence_rate_count': 4, 'time_bounds': [0.0, 4.0], 'rates': [0.0, 0.2, 0.5, 1.0]}, 'claim_boundary': 'Finite quantum-information software surrogate; not empirical evidence, not a physical qFEP or clinical claim.'}]
