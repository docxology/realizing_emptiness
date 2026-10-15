## GNNSection
ActInfPOMDP

## GNNVersionAndFlags
GNN v1

## ModelName
post_dual

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
A=[[0.82,0.08935663224781576,0.08872239747634073],[0.09000000000000002,0.8141382049245434,0.08872239747634073],[0.09000000000000002,0.09650516282764102,0.8225552050473186]]
B=[[[0.86,0.6200000000000001,0.4724],[0.32000000000000006,0.18,0.12],[0.12,0.08,0.04]],[[0.12,0.30000000000000004,0.3],[0.5800000000000001,0.68,0.5156000000000001],[0.28,0.32,0.2]],[[0.02,0.08000000000000002,0.2276],[0.10000000000000002,0.14,0.3644],[0.6,0.6,0.76]]]
C=[-0.3,0.35,1.25]
D=[0.08,0.22,0.7]
settings=[{"family":"categorical_qrf","backend":"pymdp","consumer":"simulation.pymdp_profiles:build_profile_generative_model","parameters":{"deployment":{"name":"post_dual","sector_labels":["body","action","world","world","other","care"],"metacognitive_access":1,"prior_precision":0.2}},"claim_boundary":"GNN categorical QRF software model; not empirical or physical qFEP evidence"}]
