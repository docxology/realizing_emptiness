## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_collision_model_thermalization_audit

## ModelAnnotation
Finite deterministic quantum-information surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_collision_model_thermalization_audit', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_collision_model_thermalization_audit', 'parameters': {'steps': 30, 'system_density': [[1.0, 0.0], [0.0, 0.0]], 'ancilla_density': [[0.7, 0.0], [0.0, 0.3]], 'couplings': [(0.3, 'weak_coupling'), (0.8, 'strong_coupling'), (0.0, 'zero_coupling_control')]}, 'claim_boundary': 'Finite quantum-information software surrogate; not empirical evidence, not a physical qFEP or clinical claim.'}]
