# Roadmap: OpenHands Agentic AI 튜토리얼

## Milestones

- ✅ **v1 MVP** — Phases 1–5 (shipped 2026-05-28)
- ✅ **v1.1 Model Comparison (35B vs 122B)** — Phases 6–7 (shipped 2026-05-28) — [archive](milestones/v1.1-ROADMAP.md)
- 🚧 **v1.2 Rust Example** — Phases 8–9 (in progress)

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

## v1.2 Rust Example (Phases 8–9)

**Goal:** Add a second worked example — 35B OpenHands builds a minimal Rust HTTP server (`GET / → "hello\n"`, std-only) — captured honestly and published as a new 6부 to the book.

**Scope:** Structurally parallel to v1.1 (tight 2-phase: capture gate → chapter + publish). The env is already proven; Rust toolchain verified on host. New work is the capture itself and the 6부 chapter writing.

**Honesty constraints (carried from all prior milestones):**
- Real captured run only; no manual edits to agent-written files; `source=agent` on every ActionEvent
- Any scaffolding disclosed in capture manifest; unaided-first protocol applies to the whole run (agent runs `cargo new` itself)
- `.github/workflows/deploy.yml` is NOT modified
- Existing 1부~5부 + 부록 A/B/C are not regressed

---

### Phase 8: Capture the 35B Rust HTTP Server Run

**Goal:** A real, honest 35B OpenHands run of a minimal Rust HTTP server (`cargo new` → `std::net::TcpListener` accept loop → minimal HTTP/1.1 response → `curl localhost:8080/` returns `hello\n`) captured on disk as per-task JSONL, with the honesty discipline from v1/v1.1 applied throughout.

**Depends on:** Phase 7 complete (v1.1 shipped; environment and honesty protocols proven).

**Requirements:** RUST-01, RUST-02, RUST-03

**Plan count estimate:** ~3 plans (preflight + execute + verify; mirrors Phase 6 shape)

**Success Criteria:**

1. Per-task JSONL files exist on disk in `captured-rust/` (or equivalent); every `ActionEvent` across all JSONLs has `source=agent` — zero manually edited agent-written files.
2. The JSONL record shows the agent ran `cargo new` itself (no pre-seeded `Cargo.toml` or `src/main.rs` provided by the operator), establishing the unaided-first baseline for the run.
3. A terminal `ObservationEvent` in the JSONL captures the real outcome of `curl localhost:8080/` while the server runs from `cargo run` — success (`hello\n`) or honest failure — whichever actually occurred.
4. Any scaffold fallback invoked (for any task) is recorded in a CAPTURE-MANIFEST.md and flagged with `scaffolded: true`; any genuine build error or borrow-checker issue the agent encountered and its self-correction sequence are traceable in the JSONL (no fabricated or edited events).
5. A committed CAPTURE-MANIFEST.md summarizes per-task outcome (did-write-unaided, final build status, timing, event count) and closes the capture gate — Phase 9 cannot begin until this file exists and is committed.

---

### Phase 9: 6부 Chapter + Publish

**Goal:** A new 6부 "다른 워킨 예제: Rust HTTP 서버" chapter group, written verbatim from the Phase 8 captured JSONL, is wired into the book, `mdbook build` is clean, and the updated book is live on GitHub Pages.

**Depends on:** Phase 8 complete and CAPTURE-MANIFEST.md committed (capture gate — chapter cannot be written from invented evidence).

**Requirements:** CHAP-01, CHAP-02, PUB-01, PUB-02

**Plan count estimate:** ~3 plans (write chapter + wire SUMMARY → build verify → push + confirm live; mirrors Phase 7 shape)

**Success Criteria:**

1. `src/ch06-rust-server/` (or equivalent path) contains the 6부 chapter files; `src/SUMMARY.md` has entries for all 6부 sections; the chapter structure is parallel to 4부 (intro / writing / build-test / final or equivalent decomposition).
2. Every code quote, event number, timing figure, error message, and capability claim in 6부 is verbatim-traceable to the Phase 8 JSONL or `cargo` output — no fabricated or idealized values; sections with no real backing evidence are omitted rather than invented.
3. The 사용자 프롬프트 / 내부 프로세스 / 결과 callout pattern (without pictograph emojis, per the v1.1 post-cleanup convention) is used where a real run cycle is described; concept↔action callouts pair agent actions with 1부/2부 concepts.
4. `mdbook build` completes with zero errors and zero new warnings (the pre-existing cosmetic `<char>` warning from 부록 C is acceptable; no NEW warnings introduced); existing chapters 1부–5부 + 부록 A/B/C pass link-checking and render correctly.
5. After push to `main`, the GitHub Actions deploy workflow fires; the live URL `https://ohama.github.io/Openhands-Tutorial/` returns HTTP 200 and the 6부 chapters are reachable from the sidebar navigation; `.github/workflows/deploy.yml` is unchanged (audit-verifiable by `git diff`).

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
| 8. Capture the 35B Rust HTTP Server Run | v1.2 | 0/? | Not started | — |
| 9. 6부 Chapter + Publish | v1.2 | 0/? | Not started | — |
