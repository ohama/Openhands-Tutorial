# Roadmap: OpenHands Agentic AI 튜토리얼

## Milestones

- ✅ **v1 MVP** — Phases 1–5 (shipped 2026-05-28)
- ✅ **v1.1 Model Comparison (35B vs 122B)** — Phases 6–7 (shipped 2026-05-28) — [archive](milestones/v1.1-ROADMAP.md)
- ✅ **v1.2 Rust Example** — Phases 8–9 (shipped 2026-06-01) — [archive](milestones/v1.2-ROADMAP.md)
- ✅ **v1.3 Scala Example** — Phases 10–11 (shipped 2026-06-01) — [archive](milestones/v1.3-ROADMAP.md)
- ✅ **v1.4 Planning Comparison** — Phases 12–14 (shipped 2026-06-04) — [archive](milestones/v1.4-ROADMAP.md)

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

<details>
<summary>✅ v1.2 Rust Example (Phases 8–9) — SHIPPED 2026-06-01</summary>

**Goal:** Add a second worked example — 35B OpenHands builds a minimal Rust HTTP server (`GET / → "hello\n"`, std-only) — captured honestly and published as a new 6부 to the book.

**Outcome:** The same 35B that could NOT write FsLex unaided in v1 wrote a working 43-line std-only Rust HTTP server (`TcpListener` + `BufReader`) **unaided on attempt 1**; two genuine build failures (format! heredoc syntax; E0382 borrow-checker) self-corrected; `curl` → `hello\n` exit 0. New 6부 "다른 워킹 예제 - Rust HTTP 서버" chapter group written verbatim from the capture, live on GitHub Pages. Per-call latency comparable to v1 (~3.8s Rust / ~5.3s F#); run-total difference is call count, not speed. Rust is more in-distribution for 35B than FsLex.

- [x] Phase 8: Capture the 35B Rust HTTP Server Run (3/3 plans) — completed 2026-05-29
- [x] Phase 9: 6부 Chapter + Publish (3/3 plans) — completed 2026-06-01

Full archive: [milestones/v1.2-ROADMAP.md](milestones/v1.2-ROADMAP.md)
Requirements: [milestones/v1.2-REQUIREMENTS.md](milestones/v1.2-REQUIREMENTS.md)
Audit: [milestones/v1.2-MILESTONE-AUDIT.md](milestones/v1.2-MILESTONE-AUDIT.md)

</details>

---

<details>
<summary>✅ v1.3 Scala Example (Phases 10–11) — SHIPPED 2026-06-01</summary>

**Goal:** Add a third worked example — 35B OpenHands builds a minimal Scala 3 arithmetic calculator (`scala-cli`, hand-rolled recursive-descent parser, std-only) — captured honestly and published as a new 7부 "다른 워킹 예제: Scala 계산기". Completes the calculator trilogy (F# FsLex/FsYacc in v1 → Scala in v1.3).

**Outcome:** The 35B wrote an idiomatic **Scala 3** recursive-descent calculator **unaided** (correct precedence + left-associativity; no `sealed trait` ADT — direct Int-returning methods); hit **one** genuine compile error (`private pos` accessed from `@main`), self-corrected with its own `sed`, and **all three canonical tests passed (14 / 20 / 5)**. Scaffold never invoked; 36/36 ActionEvents `source=agent`. New 7부 chapter live on GitHub Pages. Confirms the thesis: capability is **domain-distribution, not model size** (failed FsLex DSL; succeeded at Rust + Scala unaided).

- [x] Phase 10: Capture the 35B Scala Calculator Run (3/3 plans) — completed 2026-06-01
- [x] Phase 11: 7부 Chapter + Publish (3/3 plans) — completed 2026-06-01

Full archive: [milestones/v1.3-ROADMAP.md](milestones/v1.3-ROADMAP.md)
Requirements: [milestones/v1.3-REQUIREMENTS.md](milestones/v1.3-REQUIREMENTS.md)
Audit: [milestones/v1.3-MILESTONE-AUDIT.md](milestones/v1.3-MILESTONE-AUDIT.md)

</details>

---

<details>
<summary>✅ v1.4 Planning Comparison (Phases 12–14) — SHIPPED 2026-06-04</summary>

**Goal:** Capture and compare two task-planning regimes — Arm A (Claude-authored plan → 35B executes) vs Arm B (35B self-plans + executes) — across F#/Rust/Scala on the local 35B, and publish the findings as 부록 D. Research question: does an expert-authored plan help the 35B execute?

**Outcome:** Mixed/inconclusive — itself the finding. An expert plan helps mainly when the task is **out-of-distribution** (F#: Arm A 1/3 reps PASS vs Arm B 0/3 — the lone F# success came from the Claude plan wiring FsLex/FsYacc); for **in-distribution** work the 35B self-plans just as well (Scala Arm A 3/3 vs Arm B 2/3+PARTIAL; Rust both 3/3, zero error-fix cycles). All six (example × arm) cells captured at n=3; 18/18 honesty gates PASS; 부록 D live on GitHub Pages. Mid-study the reused canonical detector was found mis-scoring and was fixed + re-run (user-approved, `b7a74b9`) so all data traces to committed artifacts. Extends the standing "distribution, not size" thesis onto the planning axis.

- [x] Phase 12: Harness + Rust Pilot (3/3 plans) — completed 2026-06-02
- [x] Phase 13: Full Study (F# + Scala) + Analysis (4/4 plans) — completed 2026-06-04
- [x] Phase 14: 부록 D Chapter + Publish (3/3 plans) — completed 2026-06-04

Full archive: [milestones/v1.4-ROADMAP.md](milestones/v1.4-ROADMAP.md)
Requirements: [milestones/v1.4-REQUIREMENTS.md](milestones/v1.4-REQUIREMENTS.md)
Audit: [milestones/v1.4-MILESTONE-AUDIT.md](milestones/v1.4-MILESTONE-AUDIT.md)

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
| 8. Capture the 35B Rust HTTP Server Run | v1.2 | 3/3 | ✓ Complete | 2026-05-29 |
| 9. 6부 Chapter + Publish | v1.2 | 3/3 | ✓ Complete | 2026-06-01 |
| 10. Capture the 35B Scala Calculator Run | v1.3 | 3/3 | ✓ Complete | 2026-06-01 |
| 11. 7부 Chapter + Publish | v1.3 | 3/3 | ✓ Complete | 2026-06-01 |
| 12. Harness + Rust Pilot | v1.4 | 3/3 | ✓ Complete | 2026-06-02 |
| 13. Full Study (F# + Scala) + Analysis | v1.4 | 4/4 | ✓ Complete | 2026-06-04 |
| 14. 부록 D Chapter + Publish | v1.4 | 3/3 | ✓ Complete | 2026-06-04 |
