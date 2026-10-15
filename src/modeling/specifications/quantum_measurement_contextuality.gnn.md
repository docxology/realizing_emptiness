## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
quantum_measurement_contextuality

## ModelAnnotation
Finite quantum software surrogate inputs.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'quantum_measurement_contextuality', 'backend': 'numpy_scipy', 'consumer': 'simulation.quantum_surrogates:build_quantum_measurement_contextuality', 'parameters': {'contexts': [{'id': 'A0B0', 'a_label': 'A0', 'b_label': 'B0', 'a_angle': 0.0, 'b_angle': 0.7853981633974483, 'sign': 1.0}, {'id': 'A0B1', 'a_label': 'A0', 'b_label': 'B1', 'a_angle': 0.0, 'b_angle': -0.7853981633974483, 'sign': 1.0}, {'id': 'A1B0', 'a_label': 'A1', 'b_label': 'B0', 'a_angle': 1.5707963267948966, 'b_angle': 0.7853981633974483, 'sign': 1.0}, {'id': 'A1B1', 'a_label': 'A1', 'b_label': 'B1', 'a_angle': 1.5707963267948966, 'b_angle': -0.7853981633974483, 'sign': -1.0}]}, 'claim_boundary': 'Finite quantum software surrogate; not empirical evidence or a physical qFEP claim.'}]
