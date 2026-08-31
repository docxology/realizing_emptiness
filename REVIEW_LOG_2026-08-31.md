# Review Log — Agent-Ergonomics Deep Pass (2026-08-31)

Lane: realizing-emptiness · Repo: /Volumes/external_drive/Git/projects/ongoing/docxology/realizing_emptiness (mirror: template/projects/ongoing/ActiveInference/realizing_emptiness) · Branch: main

## PHASE 0 — Preflight

- git fetch origin done; branch main, remote github.com/docxology/realizing_emptiness.git.
- Dirty files at dispatch: 108 (76 D under legacy manuscript/, 9 M docs, 23 ?? under docs/manuscript/ and output/*/AGENTS.md|README.md). All pre-existing; treated as out-of-pass state. The manuscript migration (root manuscript/ -> docs/manuscript/) was already in progress before this pass; docs mostly reflect the new location but the code still hard-codes the old one (finding M1/D2).
- No dated review log existed; this file establishes the convention.
- Note: .venv was broken at dispatch (Python 3.14 binary wheels for rpds, matplotlib._c_internal_utils, scipy._ccallback_c unimportable -> 3 collection errors). Rebuilt with: rm -rf .venv && uv sync --extra dev (30+ min on the contended external drive; fleet-coordinated). Environment restoration is operational repair, not a doc change; logged here for the record.

## PHASE 1 — Cold-start audit (entry doc = README.md)

Attempted as a cold agent, using only what the docs say:

- (a) Current project status — PASS (with caveats). README states published v1.0.0 with DOI/Zenodo/GitHub release links; docs/README.md corroborates. Verification path: Zenodo DOI resolves; git log shows "Realizing Emptiness v1.0.0" at HEAD. Badge numbers (85 tests, 95% coverage, 428 gates) were prose-only — no date/command provenance (fixed, m2).
- (b) What to do next — PARTIAL FAIL before fixes. TODO.md exists but is exclusively a blocked-external-evidence ledger (re-3/4/13/14/15): correct, but a cold agent cannot tell whether there is ANY local, actionable work, and the README never pointed to TODO.md. Fixed in Phase 2/3.
- (c) How to run primary verification — PARTIAL FAIL. Commands present and correct (uv run pytest tests/ --cov=src --cov-fail-under=90; scripts/validate_outputs.py), but (1) counts lacked provenance, and (2) the PDF render path conflicted with itself: README said --project archive/realizing_emptiness, AGENTS.md and docs/running-the-chain.md said --project working/realizing_emptiness — both cannot be right for one checkout (fixed, m1).

### Stale claims vs disk (verified this session)

- m1 (Medium): render --project qualifier disagrees across README/AGENTS/running-the-chain; the correct value depends on which sidecar lifecycle folder holds the mirror at render time. Fixed: one canonical statement in docs/running-the-chain.md with an "ls projects/working projects/archive" check.
- m2 (Minor): README badge/quick-start counts (85 tests / 95% / 428 gates) lacked "as of date, verified by command" provenance. Added provenance and executable-truth pointers (pytest --collect-only -q | tail -1) instead of trusting prose numbers. Test counts could NOT be re-verified in-session (drive contention) — recorded as unverified rather than confirmed.
- m3 (Minor): AGENTS.md pointed agents to ../projects/AGENTS.md, which does not exist at the canonical repo path (verified missing at /Volumes/external_drive/Git/projects/ongoing/docxology/realizing_emptiness/../projects/AGENTS.md; it only resolves inside the template mirror tree). Fixed.
- m4 (Minor): ../output/figures/*.png links in docs/manuscript/0X_*.md (57) do not resolve in the committed tree — these are GENERATED composed files (scripts/compose_manuscript.py writes them); the paths only resolve after composition. Not doc rot; marked as generated-no-edit in docs/manuscript/README.md rather than hand-edited (editing generated files would violate the repo's own contract). The two <id>.png placeholder links in that folder's AGENTS/README are intentional schema examples, now labeled as such.
- m5 (Minor): no dated log for verification provenance — this file.

### Duplicated fact-classes (canonical homes assigned)

- Blocked-evidence classes re-3/4/13/14/15: canonical = TODO.md; README/docs link to it.
- Commands: canonical = AGENTS.md "Commands"; README quick-start links there.
- Test/gate counts: canonical = executable output of pytest --collect-only -q and scripts/validate_outputs.py; prose states them with date + verification command only.

## PHASE 2 — TODO.md scope

TODO.md conventions preserved (future-only, table ID/Status/Scope/Docs). Added "Agent orientation (local, unblocked)" section: orientation pointer, executable-truth commands, in-pass doc fixes, and deferred items (D1, D2) with file paths. All Phase-1 findings have entries.

## PHASE 3 — Implemented

1. README.md: orientation ladder (state-now / next-actions), provenance-stamped counts, single render-qualifier statement, TODO.md as canonical backlog pointer, dated-log pointer.
2. AGENTS.md: fixed ../projects/AGENTS.md pointer (m3), render qualifier aligned (m1), declared canonical command list.
3. docs/running-the-chain.md: declared canonical for the render command incl. how to determine the correct qualifier.
4. docs/manuscript/README.md: generated-files note + placeholder-link label (m4).
5. TODO.md: agent-orientation section + deferred entries.
6. REVIEW_LOG_2026-08-31.md: this file.

## PHASE 4 — Verify & close

- Link check re-run on touched docs: 0 new broken links introduced; pre-existing generated-path links documented, not edited.
- Gate status: .venv rebuilt; import smoke-test passes (import jsonschema ok, 31s cold). Test collection launched in background; full-suite run NOT feasible in-session — external drive under fleet-wide uv sync contention. No gate pass is claimed beyond what was measured.
- Commits: path-scoped adds only; no pre-existing files swept in (verified per commit with git status --porcelain -- <paths>).

## Deferred

- D1 (Medium, deferred): broken-test-env root cause is Python 3.14 wheels for scipy/matplotlib/rpds; pyproject.toml does not pin a python floor/upper. Source/dependency change out of scope for a doc pass; env rebuilt this session to unblock verification. Verify: uv run pytest tests/ --collect-only -q | tail -3.
- D2 (Medium, deferred): 57 generated ../output/figures/*.png links in docs/manuscript/0X_*.md resolve only post-composition. Fix belongs to the generator (compose_manuscript.py should emit paths valid at the committed location) — out of scope per "no source refactors"; recorded in TODO.md.
