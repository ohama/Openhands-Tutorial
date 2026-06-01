# Roadmap: OpenHands Agentic AI 튜토리얼

## Milestones

- ✅ **v1 MVP** — Phases 1–5 (shipped 2026-05-28)
- ✅ **v1.1 Model Comparison (35B vs 122B)** — Phases 6–7 (shipped 2026-05-28) — [archive](milestones/v1.1-ROADMAP.md)
- ✅ **v1.2 Rust Example** — Phases 8–9 (shipped 2026-06-01) — [archive](milestones/v1.2-ROADMAP.md)
- 🚧 **v1.3 Scala Example** — Phases 10–11 (in progress)

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

## v1.3 Scala Example (Phases 10–11)

**Goal:** Add a third worked example — 35B OpenHands builds a minimal Scala 3 arithmetic calculator (`scala-cli`, `sealed trait Expr` ADT + hand-written recursive-descent parser + pattern-matching evaluator, std-only) — captured honestly and published as a new 7부 "다른 워킹 예제: Scala 계산기". Completes the calculator trilogy (F# FsLex/FsYacc in v1 → Scala in v1.3). Canonical test: `2+3*4 → 14`, `(2+3)*4 → 20`, `10-3-2 → 5`.

**Honesty constraints (carried from all prior milestones):**
- Real captured run only; no manual edits to agent-written files; `source=agent` on every ActionEvent
- Any scaffolding disclosed in the capture manifest; unaided-first protocol applies (agent sets up `scala-cli` project itself)
- No parser-combinator library or parser generator — std-only discipline (parallel to v1.2)
- `.github/workflows/deploy.yml` is NOT modified
- Existing 1부~6부 + 부록 A/B/C are not regressed
- The legacy `~14–32s/call` figure is a v1 pre-run prediction, NOT a measurement — never cite it as measured

### Phase 10: Capture the 35B Scala Calculator Run

**Goal:** A real, honest 35B OpenHands run of a minimal Scala 3 arithmetic calculator (`scala-cli` project setup → `sealed trait Expr` ADT → hand-rolled recursive-descent parser → pattern-matching evaluator → canonical test `2+3*4 → 14`, `(2+3)*4 → 20`, `10-3-2 → 5`) captured on disk as per-task JSONL, with preflight verification and the honesty discipline from v1/v1.1/v1.2 applied throughout.
**Depends on:** Phase 9 complete (v1.2 shipped; environment and honesty protocols proven).
**Requirements:** SCAL-01, SCAL-02, SCAL-03

**Success Criteria:**

1. A host preflight verifies `scala-cli` and a compatible JDK are present and a trivial `scala-cli run` (e.g., `println("ok")`) exits 0 — before the agent run begins. Preflight result is recorded in the capture notes.
2. The captured JSONL shows the agent attempting to set up the `scala-cli` project, write the ADT, parser, and evaluator **unaided on the first attempt** — no source files provided to it beforehand. If a scaffold fallback was staged and actually invoked for any task, it is disclosed verbatim in CAPTURE-MANIFEST.md (not hidden, not manually patched away).
3. Every ActionEvent across all task JSONLs carries `source=agent`. Zero manually edited agent-written files between tasks. The capture is bit-identical to what the agent produced at runtime.
4. The canonical test outcome (`2+3*4 → 14`, `(2+3)*4 → 20`, `10-3-2 → 5` — or an honest failure) appears as a real terminal `ObservationEvent` in the JSONL. Any genuine errors (operator-precedence bug, Scala 3-vs-2 syntax slip, type/compile error, `scala-cli` usage confusion) and the agent's self-correction sequence are present in the JSONL and traceable — no fabricated events.
5. CAPTURE-MANIFEST.md is committed to the repo as the capture gate, recording: did-write-calc-unaided (YES/NO), scaffold invoked (YES/NO + which tasks), canonical test result, honesty gate outcome (PASS/FAIL), and the host re-run confirmation.

### Phase 11: 7부 Chapter + Publish

**Goal:** A new 7부 "다른 워킹 예제: Scala 계산기" chapter group, written verbatim from the Phase 10 captured JSONL, wired into the book, `mdbook build` clean, and the updated book live on GitHub Pages with `deploy.yml` unchanged.
**Depends on:** Phase 10 complete and CAPTURE-MANIFEST.md committed (capture gate).
**Requirements:** CHAP-01, CHAP-02, PUB-01, PUB-02

**Success Criteria:**

1. The `src/ch07-scala-calc/` directory (or equivalent) exists and contains the 7부 chapter files wired into `src/SUMMARY.md`; the chapter is structurally parallel to 4부/6부 (intro / planning / writing / build-test / final or similar), uses the `사용자 프롬프트 / 내부 프로세스 / 결과` callout pattern without pictograph emojis, and includes a short ADT-vs-FsLex contrast note comparing the Scala approach to 4부's F# DSL.
2. Every code quote, event number, error message, timing figure, and capability claim in 7부 traces verbatim to the captured JSONL, `scala-cli` output, or CAPTURE-MANIFEST.md. No fabricated or idealized content; the legacy `~14–32s/call` figure never appears as a measurement.
3. `mdbook build` completes with zero errors and zero NEW warnings. Existing chapters (1부~6부 + 부록 A/B/C) are not regressed; the pre-existing cosmetic `<char>` warning from 부록 C (TD-4) is the only accepted warning.
4. The updated book is live on GitHub Pages with HTTP 200, the new 7부 chapters reachable from sidebar navigation, and `.github/workflows/deploy.yml` is byte-identical to what it was before Phase 11 began.

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
| 10. Capture the 35B Scala Calculator Run | v1.3 | 0/3 | Not started | — |
| 11. 7부 Chapter + Publish | v1.3 | 0/3 | Not started | — |
