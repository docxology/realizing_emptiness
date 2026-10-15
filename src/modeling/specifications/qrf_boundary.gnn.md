## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
qrf_boundary

## ModelAnnotation
Boundary channel, profile vocabulary, and deterministic experiment design.

## StateSpaceBlock
input[6,type=int]
output[6,type=int]

## Connections
input>output

## InitialParameterization
settings=[{"family":"boundary_runtime_design","backend":"numpy_scipy","consumer":"simulation.qrf_env:default_deployments","parameters":{"channels":6,"seed":7,"steps":24,"profile_ids":["separation_constrained","opacified","post_dual"],"state_labels":["contracted_dual","opacified_boundary","contextual_post_dual"],"observation_labels":["self_env_cue","opacity_cue","contextual_cue"],"action_labels":["stabilize_dual","inspect_boundary","release_prior"],"dual_pattern":["self","env"],"context_prefix":"context_","opacified_keep_modulus":2,"drift_period":3,"perturbation_period":7,"access_perturbation_scale":10,"energy_precision_weight":0.2,"energy_flexibility_weight":0.3,"stochastic_seed_offset":94,"compassion_seed_offset":19,"trace_steps":12,"flexibility_diversity_weight":0.5,"flexibility_access_weight":0.5,"score_access_complexity":0.2,"score_accuracy_base":1.1,"score_flexibility_accuracy":0.35,"native_probe_steps":4,"native_probe_seed":7},"claim_boundary":"Finite QRF runtime design; not empirical, neural or physical qFEP evidence"}]
