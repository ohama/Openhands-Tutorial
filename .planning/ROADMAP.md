# Roadmap: OpenHands Agentic AI 튜토리얼

## Milestones

- ✅ **v1 MVP** — Phases 1–5 (shipped 2026-05-28)
- 🚧 **v1.1 Model Comparison (35B vs 122B)** — Phases 6–7 (in progress)

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

### 🚧 v1.1 Model Comparison (35B vs 122B) — In Progress

**Milestone Goal:** Capture a real 122B OpenHands run of the same FsLex/FsYacc calculator (lexer unaided first), then write a 35B-vs-122B comparison chapter backed by both runs' captured evidence and re-deploy the book live.

---

### Phase 6: Capture the 122B OpenHands Run

**Goal**: A real, honest 122B OpenHands run of the F# FsLex/FsYacc calculator is captured on disk (per-task JSONL), with the `.fsl` lexer attempted unaided first, and the run's actual outcome — including any genuine error-and-fix cycle — recorded without fabrication.

**Depends on**: Phase 5 complete (v1 shipped; 35B baseline archived). Phase 6 is the capture gate — Phase 7 cannot begin until this phase is complete and artifacts committed.

**Requirements**: RUN122-01, RUN122-02, RUN122-03

**Success Criteria** (what must be TRUE when Phase 6 completes):
1. A per-task JSONL log set for the 122B run exists on disk and is committed (at least one JSONL file per task prompt, with non-empty ActionEvent + ObservationEvent records).
2. The JSONL logs show the `.fsl` lexer task was submitted WITHOUT any provided lexer source — confirming the unaided-first protocol was followed.
3. The captured record honestly documents whether 122B wrote the `.fsl` lexer itself; if it could not and scaffolding was provided as a fallback, a disclosure note in the capture manifest explains this (no silent patching, no fabricated success).
4. The final test outcomes (`2+3*4=14`, `(2+3)*4=20`, `10-3-2=5`) — success or honest failure — are traceable to a terminal observation in the JSONL.
5. A CAPTURE-MANIFEST.md for the 122B run records the invocation used, the outcome of the lexer attempt, and any deviations (scaffolding, retries), parallel to the v1 35B manifest.

**Plans**: 3 plans

Plans:
- [x] 06-01-PLAN.md — Prepare 122B task-prompts (unaided task2; reuse v1 task1/3/4/5/6 with workdir swap) + preflight (gitignore oh-workdir-122b, confirm proxy serves qwen-122b)
- [x] 06-02-PLAN.md — Execute the 122B run (SLOW/empirical/--yolo, background+poll); unaided-first lexer with retry→disclosed-fallback; capture per-task JSONL + RUN-NOTES
- [x] 06-03-PLAN.md — Verify JSONL + extract timing/outcome/error-and-fix; write CAPTURE-MANIFEST.md; commit captured-122b/ (oh-workdir-122b/ stays gitignored)

---

### Phase 7: Comparison Chapter + Publish

**Goal**: A 35B-vs-122B comparison chapter, backed by verbatim evidence from both captured runs, is added to the book; `mdbook build` is clean; the updated book is live on GitHub Pages.

**Depends on**: Phase 6 complete and artifacts committed (comparison cannot be written from invented numbers).

**Requirements**: CMP-01, CMP-02, PUB-01, PUB-02

**Success Criteria** (what must be TRUE when Phase 7 completes):
1. The comparison chapter exists as a new `src/` file (comparison or appendix area) and is wired into `src/SUMMARY.md` — `mdbook build` completes with no errors and no broken links.
2. The chapter addresses: (a) whether 122B wrote the `.fsl` lexer unaided (vs 35B's inability), (b) the error-and-fix cycle comparison between both runs, and (c) measured speed — 122B cycles vs the 35B's documented ~14–32s/cycle.
3. Every speed number, error count, and capability claim in the comparison chapter traces to a verbatim line in either the 122B JSONL logs or the v1 35B JSONL logs — no fabricated or idealized figures.
4. The live GitHub Pages site (https://ohama.github.io/Openhands-Tutorial/) returns HTTP 200 and the comparison chapter is reachable via the book navigation.

**Plans**: 3 plans

Plans:
- [ ] 07-01-PLAN.md — Draft `src/appendix-c-comparison.md` from both captured runs (verbatim citations, setup-asymmetry disclosure, honest timing)
- [ ] 07-02-PLAN.md — Wire chapter into `src/SUMMARY.md`; `mdbook build` clean; no broken links
- [ ] 07-03-PLAN.md — Push to `main`; GitHub Actions deploys; verify live URL + new chapter both return 200

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
| 7. Comparison Chapter + Publish | v1.1 | 0/3 | Planned | - |
