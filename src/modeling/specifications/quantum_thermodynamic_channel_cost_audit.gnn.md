## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_thermodynamic_channel_cost_audit

## ModelAnnotation
Finite deterministic quantum-information surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_thermodynamic_channel_cost_audit', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_thermodynamic_channel_cost_audit', 'parameters': {'biased_population': [0.8, 0.2], 'dephasing_weights': [0.75, 0.25], 'bit_flip_weights': [0.85, 0.15]}, 'claim_boundary': 'Finite quantum-information software surrogate; not empirical evidence, not a physical qFEP or clinical claim.'}]
