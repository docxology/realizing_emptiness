# Realizing Emptiness Design Contract

This project has an evidence-facing visual system, not a marketing UI. Figures,
the static dashboard, and manuscript visual references must communicate finite
software artifacts, source boundaries, and blocked stronger readings without
turning proxy outputs into empirical claims.

## 1. Product And Audience

- Audience: reviewers/readers checking whether software artifacts faithfully
  operationalize the source paper within explicit evidence ceilings.
- Primary surfaces: generated PNG figures, `output/dashboard/index.html`,
  manuscript figure embeds, and validation/audit JSON.
- Visual claims are bounded: every figure or dashboard state is not empirical evidence
  unless a separate external gate says otherwise.

## 2. Semantic Palette

Colors come from `src/visualizations/style.py` and must stay synchronized with
`output/data/visual_style_audit.json`.

| Role | Token | Use |
| --- | --- | --- |
| Boundary | `boundary` `#111827` | boundary screen, no-self-evidence, claim limits |
| QRF sector | `qrf_sector` `#2563eb` | QRF labels, frame/sector relabeling |
| Pass | `pass` `#0f766e` | passing gates, accepted controls |
| Fail | `fail` `#92400e` | failed controls, rejection states |
| Keep | `keep` `#6b7280` | retained models or neutral retained rows |
| Prune | `prune` `#0f766e` | pruned/reduced model rows |
| Finite | `finite` `#2563eb` | finite software surrogate outputs |
| Blocked | `blocked` `#92400e` | future, prohibited, or blocked claims |
| Stochastic | `stochastic` `#7c3aed` | seeded ensemble or uncertainty outputs |
| Null | `null` `#475569` | null controls and shuffled baselines |
| Quantum | `quantum` `#2563eb` | finite quantum-information diagnostics |
| Source | `source` `#111827` | source paper, scholarship, claim provenance |

Hatches: `null` uses `//`, `control` uses `//`, `blocked` uses `..`,
`obstruction` uses `..`, and `finite` uses no hatch.

## 3. Typography And Legibility

- Minimum readable font: 12.0 pt.
- Cover and title-like figure labels should exceed the shared minimum; dense
  axes, legends, colorbars, cell labels, and footnotes may use the minimum but
  not go below it.
- Every figure must render at least 1200 px wide and 600 px high, with nonblank
  pixel variance and source-data alternatives.

## 4. Figure Composition

- Use deterministic Matplotlib renderers only; no hand-edited PNGs.
- Every figure must have a render contract: semantic roles, panel count,
  legend count, colorbar count, and minimum font metadata.
- Every visual must include a legend or colorbar unless a validator explicitly
  proves the encoding is otherwise explained.
- Captions must name the artifact, the visual encoding, and the interpretive
  boundary. Avoid absolute machine paths.

## 5. Components And Patterns

- Lead QRF sequence: boundary-screen geometry, channel relabeling, and
  invariance/policy flow use direct labels, stable channel IDs, and the
  boundary/QRF/pass palette.
- Quantum and roadmap visuals: use finite/quantum/blocked roles and keep
  technical panels supplemental unless the placement audit permits them.
- Governance visuals: use source/pass/blocked roles and remain supplemental
  unless the manuscript placement audit explicitly allows a main-text use.
- Dashboard links must stay relative and inspectable; figure gallery links point
  to `../figures/<id>.png`.

## 6. Validation Gates

- `visual_style_audit_ok` checks palette roles, hatches, contrast against a
  white background, panel metadata, and legend/colorbar contracts.
- `figure_legibility_audit_ok` checks dimensions, nonblank pixels, font floor,
  panel metadata, and source-data alternatives.
- `visual_accessibility_audit_ok` checks alt text, source alternatives,
  non-color encodings, units/axis language, and legend/colorbar contracts.
- `figure_integrity_audit_ok` checks PNG hashes, source-artifact hashes,
  dimensions, nonblank status, and missing sources.

## 7. Anti-Patterns

- Do not introduce raw role colors outside `SEMANTIC_COLORS`.
- Do not use small text to fit crowded figures; resize, wrap, or split panels.
- Do not use visual polish to weaken claim boundaries.
- Do not describe finite software, synthetic controls, or seeded surrogates as
  clinical, neural, awakening, compassion-efficacy, or physical qFEP evidence.
