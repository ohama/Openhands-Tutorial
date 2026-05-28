# Requirements: OpenHands Agentic AI 튜토리얼 — v1.1 (Model Comparison)

**Defined:** 2026-05-28
**Milestone:** v1.1 — Model Comparison (35B vs 122B)
**Core Value:** A reader understands agentic AI by watching a real OpenHands run; v1.1 extends this with an honest 35B-vs-122B comparison on the same task.

> v1 requirements (the original 20) are archived complete at `.planning/milestones/v1-REQUIREMENTS.md`. This file scopes ONLY the new v1.1 work.

## v1.1 Requirements

### 122B run capture

- [x] **RUN122-01**: A real captured 122B OpenHands run of the F# FsLex/FsYacc calculator exists (per-task JSONL on disk), with the `.fsl` lexer attempted **unaided first** (no provided lexer) — testing whether the 122B can do what the 35B could not.
- [x] **RUN122-02**: The run honestly records whether 122B wrote the `.fsl` lexer itself; if 122B also couldn't and scaffolding was provided as a fallback, that is disclosed (never hidden, never manually patched to fake success).
- [x] **RUN122-03**: The run's real outcome on `2+3*4=14`, `(2+3)*4=20`, `10-3-2=5` is captured (success or honest failure), along with any genuine error-and-fix cycle the agent performed.

### Comparison content

- [x] **CMP-01**: A comparison chapter/appendix contrasts 35B vs 122B on this task — capability (did 122B write the lexer unaided?), error-and-fix differences, and **measured speed** (real per-call timing from both runs' JSONL — the original "~14–32s/cycle" estimate was a pre-run prediction, not measured data).
- [x] **CMP-02**: Every comparison claim is backed by real captured evidence from both runs (verbatim, traceable to the JSONL/logs); no fabrication or idealized numbers.

### Publish

- [x] **PUB-01**: The updated book builds clean with `mdbook build` (no broken links), the new comparison chapter wired into `src/SUMMARY.md`.
- [x] **PUB-02**: The updated book is re-deployed live to GitHub Pages (the existing GitHub Actions workflow on push to `main`).

## Future Requirements

Deferred to a later milestone (carried from v1's v2 backlog):

- **EXT-01**: Additional worked examples beyond the calculator
- **EXT-02**: English translation of the tutorial
- **EXT-03**: A "build your own minimal agent in F#" appendix

## Out of Scope (v1.1)

| Feature | Reason |
|---------|--------|
| Rewriting v1 chapters | v1.1 is additive — v1 content stays; only a comparison chapter is added |
| Cloud/hosted models | The comparison is local-only (35B vs 122B); cloud comparison stays deferred |
| Re-running the 35B | The 35B run is already captured in v1; v1.1 reuses it as the baseline |
| Fabricated/idealized comparison numbers | Honesty is the core value — all numbers come from real captured runs |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| RUN122-01 | Phase 6 | Complete |
| RUN122-02 | Phase 6 | Complete |
| RUN122-03 | Phase 6 | Complete |
| CMP-01 | Phase 7 | Complete |
| CMP-02 | Phase 7 | Complete |
| PUB-01 | Phase 7 | Complete |
| PUB-02 | Phase 7 | Complete |

**Coverage:**
- v1.1 requirements: 7 total
- Mapped to phases: 7 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-05-28 (v1.1 milestone)*
*Traceability updated: 2026-05-28 (roadmap created — Phases 6–7)*
