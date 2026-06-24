# Manuscript

The `realizing_emptiness` manuscript. It recapitulates the Sandved-Smith 2026
paper "There is no self-evidence" as finite deterministic software surrogates.
It makes no empirical, clinical, neural, ontological, awakening,
practice-efficacy, or physical quantum-free-energy-principle (qFEP) claims.

## Sheaf flow: fragments to composed files to audits

The top-level `0X_*.md` files are **generated**. Do not hand-edit them. The
source of truth is the per-track fragments under `sections/`.

```
sections/<section>/<track>.md   (hand-edited fragments)
        +  sheaf/manifest.yaml  (which tracks compose into which section)
        +  sheaf/tracks.yaml    (track labels, section titles, section anchors)
        |
        v
scripts/compose_manuscript.py   (compose; --strict fails on missing fragments)
        |
        v
00_abstract.md ... 06_supplement.md   (GENERATED; never hand-edit)
        |
        v
output/data/*_audit.json        (reference, figure-reuse, placement, caption,
                                 cover, sheaf-coverage audits)
```

Compose reads each section in `sheaf/manifest.yaml`, walks its tracks in
manifest order, prepends a `## Title {#anchor}` per track from `sheaf/tracks.yaml`
(`section_titles` / `section_anchors`) unless the fragment already starts with
`#`, and writes the composed `0X` file. The abstract is special: its fragments
are joined into one plain-prose paragraph with no per-track headings and no
inline formulas. A section's `_lead.md` (when present) renders between the
section title and its first subsection as a signpost.

## Sections

| Output file | Section | Tracks (manifest order) |
| --- | --- | --- |
| `00_abstract.md` | Abstract | paper_source, qfep, qrf, bmr, pymdp, limitations |
| `01_introduction.md` | Introduction | paper_source, limitations |
| `02_methods.md` | Methods | qfep, qrf, separation_prior, bmr, pymdp |
| `03_results.md` | Results | qrf, qfep, bmr, pymdp |
| `04_discussion.md` | Discussion | paper_source, scholarship, practice_protocols, criticality, compassion_proxy, evidence_ceiling, limitations |
| `05_conclusion.md` | Conclusion | paper_source, qfep, evidence_ceiling, limitations |
| `06_supplement.md` | Supplementary Audits and Reproducibility | symbol_glossary, qfep, criticality, compassion_proxy, scholarship, practice_protocols, contemplative_inquiry, validation |

Track labels live in `sheaf/tracks.yaml`. See `sheaf/README.md` and
`sections/README.md` for the manifest and fragment conventions. The table
above is checked against `sheaf/manifest.yaml`; update the manifest first, then
sync this summary.

## Figures

Figures embed as `![short](../output/figures/<id>.png){#fig:<id>}`. The short
caption is replaced at compose time by the canonical caption in `figures.yaml`,
which must be at least 120 characters and contain both an interpretive-boundary
term and an encoding term. Reference figures, sections, and equations with
`@fig:`, `@sec:`, and `@eq:` cross-references; never write a hardcoded
"Figure 3". Placement is gated: QRF lead figures belong in the main text and
precede the compact quantum summary; technical-quantum and governance figures
belong only in the supplement.

## How to edit and recompose

1. Edit the relevant `sections/<section>/<track>.md` fragment (or `_lead.md`).
   Never edit a composed `0X_*.md` file.
2. Recompose from the project root:

   ```
   uv run python scripts/compose_manuscript.py --strict
   ```

   `--strict` fails the run if any manifest fragment is missing.
3. Keep the claim ceiling and acronym-at-first-use rules intact; honor the
   figure and subsection-title gates in `AGENTS.md`.

Adjacent files in this folder: `config.yaml` (paper metadata), `preamble.md`
(title-page cover include), `references.bib`, and `99_references.md`.
