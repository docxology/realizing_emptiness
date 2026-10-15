## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_many_body_boundary_screen_sweep

## ModelAnnotation
Finite deterministic quantum-information surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_many_body_boundary_screen_sweep', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_many_body_boundary_screen_sweep', 'parameters': {'qubit_count': 6, 'cuts': [{'id': 'observer_boundary_cut', 'qubits': [0, 1, 2], 'cut_class': 'candidate_observer_boundary'}, {'id': 'local_cluster_cut', 'qubits': [0, 1, 3], 'cut_class': 'structured_control'}, {'id': 'alternating_cut', 'qubits': [0, 2, 4], 'cut_class': 'structured_control'}, {'id': 'random_cut_control', 'qubits': [0, 3, 5], 'cut_class': 'negative_control_random_cut'}]}, 'claim_boundary': 'Finite quantum-information software surrogate; not empirical evidence, not a physical qFEP or clinical claim.'}]
