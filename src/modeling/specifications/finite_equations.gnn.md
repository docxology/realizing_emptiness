# finite_equations

## GNNSection
FiniteSurrogate

## GNNVersionAndFlags
GNN v1

## ModelName
finite_equations

## ModelAnnotation
Finite software surrogate inputs; not empirical evidence.

## StateSpaceBlock
input[1,type=float]
output[1,type=float]

## Connections
input>output

## InitialParameterization
settings=[{"family": "finite_equations", "backend": "numpy_scipy", "consumer": "formalism.equations:evaluate_equation_surrogates", "claim_boundary": "finite worked equation examples; not empirical evidence", "parameters": {"deployment_complexity_access": 0.2, "deployment_accuracy_base": 0.6, "deployment_accuracy_flexibility": 0.35, "deployments": [["dual", ["self", "self", "env", "env", "env", "self"], 0.0, 4.0], ["contextual", ["body", "action", "world", "world", "other", "care"], 1.0, 0.2]], "channel_cost": 1.0, "predicted": 0.0, "realized": [0.0, 1.0, 1.0, 0.0, 1.0, 0.0], "eq6_realized": [0.55, 0.45], "eq6_predicted": [0.7, 0.3], "eq11_posterior": [0.7, 0.3], "eq11_prior": [0.5, 0.5], "eq11_likelihood": [0.8, 0.4], "eq11_noise": 0.05, "posterior_logits": [-0.3, -0.2, -0.7], "prior_precision": 4.0}}]
