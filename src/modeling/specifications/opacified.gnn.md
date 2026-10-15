## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
opacified

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
A=[[0.74,0.12948723056695488,0.1289784903563775],[0.13,0.7370811586118969,0.1289784903563775],[0.13,0.13343161082114827,0.7420430192872451]]
B=[[[0.86,0.6200000000000001,0.5252],[0.32000000000000006,0.18,0.12],[0.12,0.08,0.04]],[[0.12,0.30000000000000004,0.3],[0.5800000000000001,0.68,0.5588],[0.28,0.32,0.2]],[[0.02,0.08000000000000002,0.1748],[0.10000000000000002,0.14,0.32120000000000004],[0.6,0.6,0.76]]]
C=[0.1,1.05,0.55]
D=[0.25,0.55,0.2]
settings=[{"family":"categorical_qrf","backend":"pymdp","consumer":"simulation.pymdp_profiles:build_profile_generative_model","parameters":{"deployment":{"name":"opacified","sector_labels":["self","action","env","env","other","care"],"metacognitive_access":0.55,"prior_precision":2}},"claim_boundary":"GNN categorical QRF software model; not empirical or physical qFEP evidence"}]
