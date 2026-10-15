## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_general_measurement_cover_polytope

## ModelAnnotation
Finite quantum software surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_general_measurement_cover_polytope', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_general_measurement_cover_polytope_audit', 'parameters': {'scenarios': [{'id': 'triangle_feasible_control', 'measurements': ['A', 'B', 'C'], 'contexts': [('AB', ('A', 'B'), 1), ('BC', ('B', 'C'), 1), ('AC', ('A', 'C'), 1)], 'expected_feasible': True}, {'id': 'triangle_parity_obstruction', 'measurements': ['A', 'B', 'C'], 'contexts': [('AB', ('A', 'B'), 1), ('BC', ('B', 'C'), 1), ('AC', ('A', 'C'), -1)], 'expected_feasible': False}, {'id': 'chsh_product_control', 'measurements': ['A0', 'A1', 'B0', 'B1'], 'product_control': True, 'expected_feasible': True}, {'id': 'chsh_bell_obstruction', 'measurements': ['A0', 'A1', 'B0', 'B1'], 'product_control': False, 'expected_feasible': False}]}, 'claim_boundary': 'Finite quantum software surrogate; not empirical evidence or a physical qFEP claim.'}]
