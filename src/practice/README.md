# src/practice

Bounded mappings from the paper's contemplative-practice vocabulary to *model
interventions* (parameter deltas on the finite surrogate). These are research
interfaces and software interventions only — not medical, spiritual, therapeutic,
or efficacy claims.

## Modules

| File | Key API | Role |
| --- | --- | --- |
| `protocols.py` | `practice_protocol_map` | Returns the bounded protocol map: each protocol has an `id`, `label`, `model_intervention` (parameter deltas), `paper_role`, and a non-empty `safety_boundary`; the payload sets `allow_user_facing_claims = False` |

The three protocols map to model-side parameter changes only:
`attentional_opacification` (metacognitive-access / prior-precision deltas),
`dependent_origination_inquiry` (sector-label revisability), and
`compassion_alignment` (policy-scope / self-privilege deltas).

## Pipeline fit

`scripts/` writes the map to `output/data/practice_protocol_map.json` (schema
`practice_protocol_map.schema.json`, gate via the contract registry). The
`practice_policy_scope_map` figure in `visualizations/` reads this artifact. The
map is governance metadata; it drives no simulation.
