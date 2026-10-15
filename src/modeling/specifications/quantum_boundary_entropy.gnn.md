## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_boundary_entropy

## ModelAnnotation
Finite deterministic quantum-information surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_boundary_entropy', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_quantum_boundary_entropy', 'parameters': {'theta_count': 33, 'rotation_count': 25, 'theta_bounds': [0.0, 0.7853981633974483], 'rotation_bounds': [0.0, 1.5707963267948966]}, 'claim_boundary': 'Finite quantum-information software surrogate; not empirical evidence, not a physical qFEP or clinical claim.'}]
