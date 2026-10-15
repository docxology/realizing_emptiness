## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
practice_mapping

## ModelAnnotation
Finite practice-to-parameter vocabulary mapping. Declaration metadata only; these deltas are never applied to a simulation or offered as practice instructions.

## StateSpaceBlock
input[3,type=float]
output[3,type=float]

## Connections
input>output

## InitialParameterization
settings=[{'family': 'practice_governance', 'backend': 'numpy_scipy', 'consumer': 'practice.protocols:practice_protocol_map', 'parameters': {'interventions': {'attentional_opacification': {'metacognitive_access_delta': 0.25, 'prior_precision_delta': -0.5}, 'dependent_origination_inquiry': {'sector_label_revisability': 0.5, 'fixed_partition_weight_delta': -0.4}, 'compassion_alignment': {'compassion_scope_delta': 0.35, 'self_privilege_weight_delta': -0.3}}}, 'claim_boundary': 'Finite interface metadata; not empirical, practice-efficacy or clinical evidence'}]
