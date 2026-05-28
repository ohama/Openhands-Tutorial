# Roadmap: OpenHands Agentic AI 튜토리얼

## Milestones

- ✅ **v1 MVP** — Phases 1–5 (shipped 2026-05-28)
- ✅ **v1.1 Model Comparison (35B vs 122B)** — Phases 6–7 (shipped 2026-05-28) — [archive](milestones/v1.1-ROADMAP.md)

## Phases

<details>
<summary>✅ v1 MVP (Phases 1–5) — SHIPPED 2026-05-28</summary>

### Phase 1: Scaffold and Concept Chapters
**Goal**: The mdBook scaffold exists and the agentic AI concept chapters are written in Korean.
**Plans**: 3 plans — complete

Plans:
- [x] 01-01: Initialize mdBook + GitHub repo structure
- [x] 01-02: Write 1부 agentic AI concept chapter
- [x] 01-03: Write 2부 OpenHands architecture chapter

### Phase 2: Environment Setup and Verification
**Goal**: The real OpenHands + litellm + LocalWorkspace stack is verified end-to-end on the headless SSH Mac and documented as the 3부 setup chapter.
**Plans**: 3 plans (re-planned from 5; Docker-Desktop path archived) — complete

Plans:
- [x] 02-01: Discover + document actual stack (Colima, litellm proxy, headless CLI)
- [x] 02-02: Prove tool-call end-to-end (PING + DOTNET PASS)
- [x] 02-03: Write 3부 setup chapter from verified evidence

### Phase 3: Capture the 35B OpenHands Run
**Goal**: A real, honest captured 35B OpenHands run of the FsLex/FsYacc calculator exists on disk (JSONL per task), with genuine error-and-fix cycles documented.
**Plans**: 3 plans (attempt 1 rejected for honesty; attempt 2 the real capture) — complete

Plans:
- [x] 03-01: Produce task-prompt files; run attempt 1 (rejected — manual fix caught)
- [x] 03-02: Run attempt 2 (lexer scaffolded; genuine parser error-and-fix captured)
- [x] 03-03: Verify and commit captured artifacts

### Phase 4: Worked-Example Chapter
**Goal**: The 4부 walkthrough chapter is written verbatim from captured JSONL, with concept↔action callouts, error-and-fix narration, final source, and honest performance numbers.
**Plans**: 3 plans — complete

Plans:
- [x] 04-01: Write task 1–2 walkthrough from captured JSONL
- [x] 04-02: Write task 3–5 walkthrough + error-and-fix narration
- [x] 04-03: Write 5부 troubleshooting, reproducibility, and final source appendix

### Phase 5: Publish
**Goal**: The mdBook builds cleanly and is live on GitHub Pages.
**Plans**: 4 plans — complete

Plans:
- [x] 05-01: Wire all SUMMARY.md entries; final mdbook build green
- [x] 05-02: Milestone audit (cross-part contradiction caught + fixed)
- [x] 05-03: Set up GitHub Actions deploy workflow
- [x] 05-04: Push to ohama/Openhands-Tutorial; enable Pages; verify live

</details>

---

<details>
<summary>✅ v1.1 Model Comparison (Phases 6–7) — SHIPPED 2026-05-28</summary>

**Goal:** Capture a real 122B OpenHands run of the same FsLex/FsYacc calculator (lexer unaided first), then write a 35B-vs-122B comparison chapter backed by both runs' captured evidence and re-deploy the book live.

**Outcome:** 122B wrote the `.fsl` lexer unaided (where 35B could not). Comparison chapter (`src/appendix-c-comparison.md`) live with verbatim citations. Per-call latency comparable between models (35B ≈ 5.3s, 122B ≈ 6.3s); run-total difference came from iteration count, not speed.

- [x] Phase 6: Capture the 122B OpenHands Run (3/3 plans) — completed 2026-05-28
- [x] Phase 7: Comparison Chapter + Publish (3/3 plans) — completed 2026-05-28

Full archive: [milestones/v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md)
Requirements: [milestones/v1.1-REQUIREMENTS.md](milestones/v1.1-REQUIREMENTS.md)
Audit: [milestones/v1.1-MILESTONE-AUDIT.md](milestones/v1.1-MILESTONE-AUDIT.md)

</details>

---

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Scaffold and Concept Chapters | v1 | 3/3 | Complete | 2026-05-27 |
| 2. Environment Setup and Verification | v1 | 3/3 | Complete | 2026-05-27 |
| 3. Capture the 35B OpenHands Run | v1 | 3/3 | Complete | 2026-05-28 |
| 4. Worked-Example Chapter | v1 | 3/3 | Complete | 2026-05-28 |
| 5. Publish | v1 | 4/4 | Complete | 2026-05-28 |
| 6. Capture the 122B OpenHands Run | v1.1 | 3/3 | ✓ Complete | 2026-05-28 |
| 7. Comparison Chapter + Publish | v1.1 | 3/3 | ✓ Complete | 2026-05-28 |
