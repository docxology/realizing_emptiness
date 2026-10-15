## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_qrf_frame_covariance_toy_audit

## ModelAnnotation
Finite deterministic quantum-information surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_qrf_frame_covariance_toy_audit', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_qrf_frame_covariance_toy_audit', 'parameters': {'mixture_weights': [0.7, 0.3], 'theta': 0.5235987755982988, 'probability': [0.12, 0.38, 0.18, 0.32]}, 'claim_boundary': 'Finite quantum-information software surrogate; not empirical evidence, not a physical qFEP or clinical claim.'}]
