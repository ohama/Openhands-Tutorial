# Roadmap: OpenHands Agentic AI 튜토리얼

## Milestones

- ✅ **v1 MVP** — Phases 1–5 (shipped 2026-05-28)
- ✅ **v1.1 Model Comparison (35B vs 122B)** — Phases 6–7 (shipped 2026-05-28) — [archive](milestones/v1.1-ROADMAP.md)
- ✅ **v1.2 Rust Example** — Phases 8–9 (shipped 2026-06-01) — [archive](milestones/v1.2-ROADMAP.md)
- ✅ **v1.3 Scala Example** — Phases 10–11 (shipped 2026-06-01) — [archive](milestones/v1.3-ROADMAP.md)
- 🚧 **v1.4 Planning Comparison** — Phases 12–14 (in progress)

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

## v1.4 Planning Comparison (Phases 12–14)

**Goal:** Capture and compare two task-planning regimes (Arm A: Claude-authored plan → 35B executes; Arm B: 35B self-plans + executes) across the three existing examples (F# FsLex/FsYacc calculator, Rust HTTP server, Scala calculator), and publish the findings as 부록 D. Research question: does who plans the task decomposition change the 35B's execution efficiency? Whatever the data shows — including mixed or inconclusive results — is reported honestly from real captured runs.

**Requirements:** METH-01/02/03, PCAP-01/02/03, ANAL-01/02, DCHAP-01/02, DPUB-01/02 (12 total)

---

### Phase 12: Harness + Rust Pilot

**Goal:** The comparison harness is proven: both prompt templates exist, pass a side-by-side diff for symmetry, and produce clean JSONL captures for both Arm A and Arm B on the Rust HTTP server pilot — with `metrics_extractor.py` validated and the critical open unknowns (TaskTracker emission, token `usage` in JSONL) resolved before committing to the full study.

**Requirements:** METH-01, METH-02, METH-03

**Dependencies:** None (first phase of v1.4)

**Research flags:**
- If Arm B does not emit `TaskTrackerObservation` events on the Qwen 35B at the chosen prompt phrasing, adjust the Arm B prompt before proceeding to Phase 13.
- Check `usage` field in ObservationEvents during pilot to determine whether P3 token metrics are available.

**Honesty controls baked in:**
- Both prompts share an identical control block (goal, constraints, canonical tests); the only diff is plan content vs. goal-only. A literal diff is run and any non-plan asymmetry is stripped before the first invocation (METH-01 / Pitfall 1).
- `oh-workdir-planning/` is gitignored; each arm gets its own empty workspace directory; pre-run workspace-empty verification is logged in the manifest (METH-02 / Pitfall 6).
- Run order is documented and counterbalanced; litellm proxy state is controlled between arms (METH-02 / Pitfall 3).
- `metrics_extractor.py` uses `enumerate(events, start=1)` throughout; event numbers in manifests are 1-based (METH-03 / Pitfall 8).
- The mechanical `source=agent` honesty gate runs over both Rust JSONLs before any artifact is committed; the initial `source=user` MessageEvent in Arm A is excluded from the gate check (METH-03 / Pitfall 7).

**Success criteria:**
1. Both arm prompt templates are written side-by-side and a literal diff confirms the only difference is the planning input (Arm A numbered task plan vs. Arm B bare goal + task-tracker instruction); no non-plan wording asymmetry remains.
2. Arm A Rust invocation completes with a real JSONL on disk; Arm B Rust invocation completes with a real JSONL on disk; each workspace was empty before its run and neither arm's workspace was touched during the other arm's run.
3. The `source=agent` honesty gate returns PASS on both Rust JSONLs (excluding the Arm A `source=user` plan-delivery event).
4. `metrics_extractor.py` successfully parses both Rust JSONLs and writes `captured-planning/rust/arm-a/metrics.json` and `arm-b/metrics.json`, each with `honesty_gate = "PASS"` and `canonical_tests.curl_hello` recorded as PASS or FAIL (not null).
5. The Phase 12 manifest documents whether Arm B emitted `TaskTrackerObservation` events and whether `usage` data is present in the JSONL — resolving both open unknowns before Phase 13 begins.

**Plans:** 3 plans

Plans:
- [x] 12-01-PLAN.md — Preflight + harness: gitignored arm-isolated workspaces, both Rust prompts (identical control block) + mandatory symmetry diff (PASS), metrics_extractor.py (1-based, self-validated)
- [x] 12-02-PLAN.md — Ran both arms live on Rust (single invocation each); both PASS curl→hello; resolved unknowns (TaskTracker YES / token-usage NO→P3 dropped)
- [x] 12-03-PLAN.md — Capture gate: honesty gate PASS, metrics.json x2 + comparison.json, CAPTURE-MANIFEST (GATE CLOSED), human-verified, committed pilot artifacts

**Outcome:** Harness proven on the Rust pilot. Both arms ran as single CodeActAgent invocations in isolated empty workspaces and **both passed** curl→hello (Arm A 14 TA/48.3s; Arm B 12 TA/59.0s — timing carries a cache-warmth caveat). Symmetry diff PASS; honesty gate 0/0 non-agent. **Both open unknowns resolved:** the 35B self-plans via TaskTracker (Arm B, no prompt change needed) and there is **no token `usage` in the JSONL** (P3 token metrics dropped). Verified 5/5. ✓ Complete 2026-06-02.

---

### Phase 13: Full Study (F# + Scala) + Analysis

**Goal:** All six (example × arm) captures are complete and committed — Rust from Phase 12 plus F# and Scala captured same-day per language — with all honesty gates passed, all `metrics.json` and `comparison.json` files generated, and the CAPTURE-MANIFEST.md committed as the gate that unblocks Phase 14.

**Requirements:** PCAP-01, PCAP-02, PCAP-03, ANAL-01, ANAL-02

**Dependencies:** Phase 12 capture gate (both Rust `metrics.json` committed with `honesty_gate = "PASS"` and `canonical_tests.curl_hello` recorded)

**Research flags:**
- F# arms may both fail the canonical test (FsLex/FsYacc is out-of-distribution for the 35B); this is valid data — report as FAIL. Pre-confirm Claude's F# plan covers `fslex`/`fsyacc` invocation explicitly so Arm A is not also blocked.
- n=3 is preferred per (example × arm); n=1 is the acceptable floor only if time or stability prevents repetition — every n=1 result must be labeled explicitly.

**Honesty controls baked in:**
- Both arms per language are captured in the same session (same day, same version, same proxy state) to prevent inter-run version drift (Pitfall 10).
- Each arm's planning artifact is saved verbatim: Claude's task plan as `claude-plan.md` (Arm A input) and the first agent planning output extracted from the Arm B JSONL as `oh-self-plan.md` — no rewording, no editorial additions (Pitfall 5).
- n=3 repetitions report `median (min–max)`; n=1 results are labeled `(단일 실행)` everywhere they appear (PCAP-01).
- Canonical tests (F#: `2+3*4 = 14`, `(2+3)*4 = 20`, `10-3-2 = 5`; Rust: `curl` → `hello\n`; Scala: all three expressions) are the objective correctness gate — FAIL cells are included in the comparison tables, not hidden (ANAL-01).
- The Arm A converter applies mechanical formatting only: each Claude subtask → one numbered item, verbatim text, no additions or restructuring; both the original plan and converted prompt are archived (Pitfall 5 / METH-01).
- The `source=agent` honesty gate runs over all six JSONLs before CAPTURE-MANIFEST.md is committed (PCAP-01 / Pitfall 7).
- `~14–32s/call` is never cited; per-call timing is derived from real JSONL timestamps only (ANAL-01 / Pitfall 9).

**Success criteria:**
1. All six (example × arm) captures exist as real JSONL files on disk; all six honesty gates return PASS; no ActionEvent carries `source=user` except the legitimate Arm A plan-delivery event.
2. Both planning artifacts are saved per example: `claude-plan.md` (Arm A) and `oh-self-plan.md` (Arm B, verbatim from first agent planning output in JSONL); all six artifact files are committed under `captured-planning/`.
3. All six `metrics.json` files are committed with `honesty_gate = "PASS"` and all `canonical_tests` fields populated (PASS or FAIL — not null); all three `comparison.json` files are committed.
4. The per-example comparison tables (ANAL-01) show Arm A vs. Arm B on all P1/P2 metrics, with `median (min–max)` for n≥2 repetitions and explicit `(단일 실행)` labels for n=1 — no metric presented without its applicable fairness caveat.
5. The qualitative plan comparison (ANAL-02) is written per example, covering task count, granularity, ordering, and structural match to the scaffold→write→build→test shape for both Claude's plan and the agent's self-plan.
6. `CAPTURE-MANIFEST.md` is committed under `captured-planning/` summarizing all six outcomes, run conditions and order, and honesty-gate results — closing the capture gate and unblocking Phase 14.

---

### Phase 14: 부록 D Chapter + Publish

**Goal:** A new 부록 D "계획 방식 비교: Claude 계획 vs OpenHands 자체 계획" chapter is written verbatim from the committed `captured-planning/` data, wired into the book after 부록 C, and deployed live to GitHub Pages — with all existing 1부–7부 and 부록 A/B/C chapters not regressed.

**Requirements:** DCHAP-01, DCHAP-02, DPUB-01, DPUB-02

**Dependencies:** Phase 13 capture gate (CAPTURE-MANIFEST.md committed; all six `metrics.json` with `honesty_gate = "PASS"` and all `canonical_tests` populated)

**Honesty controls baked in:**
- Every number, plan excerpt, and metric in 부록 D is traceable to a committed artifact; manifest 1-based event numbers are cited throughout (DCHAP-01 / Pitfall 8).
- The chapter's opening paragraph frames the research question as "does an expert-authored plan help the 35B execute?" — not "Claude plans better than the 35B"; n=1 figures carry explicit `(단일 실행)` hedges everywhere they appear (DCHAP-02 / Pitfall 4).
- Mixed or per-metric or inconclusive outcomes are reported as valid findings, not softened or omitted (DCHAP-02).
- `~14–32s/call` is not cited as a measurement; a grep of the chapter text for this string is an audit checklist item (DCHAP-02 / Pitfall 9).
- `.github/workflows/deploy.yml` is not modified; the existing deploy pipeline handles all content (DPUB-02).
- `mdbook build` is run and must be clean before push; the only accepted warning is the pre-existing `<char>` tag in 부록 C (TD-4) (DPUB-01).

**Success criteria:**
1. `src/appendix-d-planning-comparison.md` exists and contains a cross-example comparison table (F# / Rust / Scala × Arm A / Arm B × all P1/P2 metrics), per-arm planning artifact excerpts, qualitative plan comparison observations, and an honest interpretation section — all numbers traceable to committed `captured-planning/` artifacts.
2. The chapter's opening paragraph correctly states the research question ("does an expert-authored plan help the 35B execute?"); n=1 figures are hedged with `(단일 실행)` in every table row and prose reference; mixed or inconclusive results are reported as valid findings, not omitted.
3. `src/SUMMARY.md` is updated to wire 부록 D after 부록 C; `mdbook build` completes with zero errors (only the pre-existing `<char>` warning is acceptable); existing 1부–7부 + 부록 A/B/C content is not changed.
4. A push to `main` triggers the existing GitHub Actions deploy workflow without modifications to `deploy.yml`; the live site returns HTTP 200 on the root URL; 부록 D is reachable from the sidebar nav and returns HTTP 200.

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
| 13. Full Study (F# + Scala) + Analysis | v1.4 | 0/? | Not started | — |
| 14. 부록 D Chapter + Publish | v1.4 | 0/? | Not started | — |
