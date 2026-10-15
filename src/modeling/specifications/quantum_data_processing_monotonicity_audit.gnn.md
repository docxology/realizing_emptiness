## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_data_processing_monotonicity_audit

## ModelAnnotation
Finite deterministic quantum-information surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_data_processing_monotonicity_audit', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_data_processing_monotonicity_audit', 'parameters': {'state_pairs': [{'id': 'z_axis_pair', 'rho': (0.3, 0.0, 0.5), 'sigma': (0.0, 0.0, -0.4)}, {'id': 'tilted_pair', 'rho': (0.5, 0.2, 0.1), 'sigma': (-0.2, 0.3, 0.4)}, {'id': 'antipodal_pair', 'rho': (0.0, 0.0, 0.6), 'sigma': (0.0, 0.0, -0.6)}], 'channels': [{'name': 'phase_damping', 'strengths': (0.2, 0.5, 0.9)}, {'name': 'amplitude_damping', 'strengths': (0.2, 0.5, 0.9)}, {'name': 'depolarizing', 'strengths': (0.2, 0.5, 0.9)}], 'structural_strength': 0.5, 'selection_angles': [0.39269908169872414, 0.5235987755982988, 0.6283185307179586]}, 'claim_boundary': 'Finite quantum-information software surrogate; not empirical evidence, not a physical qFEP or clinical claim.'}]
