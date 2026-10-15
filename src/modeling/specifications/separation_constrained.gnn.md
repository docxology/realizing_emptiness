## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
separation_constrained

## ModelAnnotation
Three-state categorical surrogate with explicit likelihood, controlled transitions, log preferences, and initial prior. B axes are next state, previous state, action.

## StateSpaceBlock
A[3,3,type=float]
B[3,3,3,type=float]
C[3,type=float]
D[3,type=float]
s[3,type=float]
o[3,type=int]
u[1,type=int]

## Connections
D>s
s>A
A>o
s>B
u>B
B>s
C>u

## InitialParameterization
A=[[0.86,0.07,0.07],[0.07,0.86,0.07],[0.07,0.07,0.86]]
B=[[[0.86,0.6200000000000001,0.5736],[0.32000000000000006,0.18,0.12],[0.12,0.08,0.04]],[[0.12,0.30000000000000004,0.3],[0.5800000000000001,0.68,0.5984],[0.28,0.32,0.2]],[[0.02,0.08000000000000002,0.1264],[0.10000000000000002,0.14,0.2816],[0.6,0.6,0.76]]]
C=[1.15,0.15,-0.25]
D=[0.82,0.15,0.03]
settings=[{"family":"categorical_qrf","backend":"pymdp","consumer":"simulation.pymdp_profiles:build_profile_generative_model","parameters":{"deployment":{"name":"separation_constrained","sector_labels":["self","self","env","env","env","self"],"metacognitive_access":0,"prior_precision":4}},"claim_boundary":"GNN categorical QRF software model; not empirical or physical qFEP evidence"}]
