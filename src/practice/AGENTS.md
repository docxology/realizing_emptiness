# AGENTS.md - src/practice

Practice-to-model-intervention mappings. Read the root
[`AGENTS.md`](../../AGENTS.md) Source Contract first.

## Do

- Keep `allow_user_facing_claims = False` in the `practice_protocol_map` payload.
  This is the boundary flag that marks the map as research/software metadata, not
  user-facing instruction.
- Give every protocol a non-empty `safety_boundary` string; the payload's
  `all_have_safety_boundaries` must stay `True`.
- Express each protocol only as `model_intervention` parameter deltas
  (metacognitive access, prior precision, sector-label revisability, policy
  scope, self-privilege weight) tied to a paraphrased `paper_role`.
- Keep `protocol_count` consistent with the `protocols` list and the schema.

## Do NOT

- Do NOT phrase any field as medical, spiritual, therapeutic, clinical, or
  attainment guidance, or as a claim that a protocol works.
- Do NOT flip `allow_user_facing_claims` to `True`.
- Do NOT add a protocol without updating the schema and its test, and without a
  safety boundary.
- Do NOT drive a simulation from this map; it is governance metadata only.
