## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_cramer_rao_estimation

## ModelAnnotation
Finite quantum software surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_cramer_rao_estimation', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_estimation:build_quantum_cramer_rao_estimation_audit', 'parameters': {'radius': 0.6, 'pointer_axis': [0.0, 0.0, 1.0], 'sigma_grid': [0.4, 0.7, 1.0, 1.3]}, 'claim_boundary': 'Finite quantum software surrogate; not empirical evidence or a physical qFEP claim.'}]
