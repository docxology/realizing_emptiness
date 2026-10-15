## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_sheaf_contextuality_obstruction_audit

## ModelAnnotation
Finite deterministic quantum-information surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_sheaf_contextuality_obstruction_audit', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_sheaf_contextuality_obstruction_audit', 'parameters': {'scenarios': [{'id': 'noncontextual_triangle_control', 'measurements': ['A', 'B', 'C'], 'contexts': [('AB', ('A', 'B'), 1), ('BC', ('B', 'C'), 1), ('AC', ('A', 'C'), 1)], 'expected_feasible': True}, {'id': 'parity_obstruction', 'measurements': ['A', 'B', 'C'], 'contexts': [('AB', ('A', 'B'), 1), ('BC', ('B', 'C'), 1), ('AC', ('A', 'C'), -1)], 'expected_feasible': False}]}, 'claim_boundary': 'Finite quantum-information software surrogate; not empirical evidence, not a physical qFEP or clinical claim.'}]
