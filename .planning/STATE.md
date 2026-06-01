# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-28 — started v1.2 Rust Example)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run real programs. v1: F# FsLex/FsYacc calculator (35B). v1.1: same calculator with 122B, comparison. **v1.2: same 35B model, different language — a minimal Rust HTTP server.**
**Current focus:** v1.2 — BOTH phases COMPLETE + verified. 6부 (Rust HTTP 서버) is LIVE. Milestone ready for /gsd:audit-milestone close-out.

## Current Position

Milestone: v1.2 (Rust Example) — COMPLETE 2026-06-01
Phase: 9 — 6부 Chapter + Publish — COMPLETE (all 3 plans done)
Plan: 09-01 COMPLETE; 09-02 COMPLETE (PUB-01 gate); 09-03 COMPLETE (PUB-02 gate — live deploy)
Status: Phase 9 complete — 6부 live on GitHub Pages. v1.2 milestone deliverable shipped. Phase verifier 5/5 PASS (09-VERIFICATION.md): code byte-identical to final-source/main.rs, both build errors verbatim from JSONL, no fabrication/emoji, only pre-existing <char> warning, live pages HTTP 200, deploy.yml unchanged. CHAP-01/02 + PUB-01/02 = Complete.
Last activity: 2026-06-01 — /gsd:execute-phase 9 (3 waves: write+wire → build verify → publish); verifier 5/5 PASS; ROADMAP/STATE/REQUIREMENTS updated

Progress: ██████████ v1.2 100% (Phase 8 + Phase 9 all 3 plans complete; book live)
Live (v1 + v1.1 + v1.2): https://ohama.github.io/Openhands-Tutorial/

## Cumulative History

- **v1 MVP** (shipped 2026-05-28): 5 phases, 17 plans, Korean mdBook tutorial + 35B captured run of F# calculator. See `milestones/v1-ROADMAP.md`.
- **v1.1 Model Comparison** (shipped 2026-05-28): 2 phases, 6 plans, 122B capture + 부록 C comparison + UX callouts. See `milestones/v1.1-ROADMAP.md`.
- **v1.2 Rust Example** (shipped 2026-06-01): 2 phases, 6 plans, 35B Rust HTTP server capture + 6부 chapter (다른 워킹 예제) live. Confirms Rust is more in-distribution for 35B than FsLex was (wrote the server unaided where it failed FsLex). Pending milestone audit/close-out.

## Accumulated Context

### Key decisions still live (carried across milestones)

- [stack]: Headless macOS (SSH) + Colima + OpenHands 1.16 headless CLI on LocalWorkspace; local litellm proxy at 127.0.0.1:4000 serving `openai/qwen-35b` and `openai/qwen-122b`; .NET 10 on host (verified) **+ rustc/cargo 1.95.0 on host (verified 2026-05-28)**
- [run-config]: `LLM_MODEL=openai/qwen-{35b|122b} LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy openhands --headless --json --yolo --override-with-envs -t "<task>"`
- [honesty discipline]: real captured runs only; no manual edits to agent-written files; setup-asymmetry (scaffolding) disclosed; pre-run predictions never presented as measurements
- [real measured per-call timing on this hardware]: 35B ≈ 5.3s/call, 122B ≈ 6.3s/call (from v1 + v1.1 JSONL)

### Key decisions for v1.2 Phase 8 plan 03

- [08-03 honesty-gate]: PASSED — every ActionEvent across all 3 JSONLs has source=agent; verified mechanically by python3 before any commit
- [08-03 capture-gate]: CLOSED — captured-rust/ committed (CAPTURE-MANIFEST.md + logs/ + final-source/ + test-output.txt + transcript.md); oh-workdir-rust/ stays gitignored (0 tracked files)
- [08-03 event-indices]: JSONL line numbers: curl at task3-buildtest.jsonl lines #37/#38 (not #32 as in RUN-NOTES — RUN-NOTES used 0-based or different counting; manifest uses actual line indices)
- [08-03 host-rerun]: PASS — fresh cargo run + curl on 2026-05-29; HTTP/1.1 200 OK, Content-Length: 6, "hello\n", exit 0. Matches agent's task3 capture.

### Key decisions for v1.2 Phase 8 plan 02

- [08-02 capture]: did-write-server-unaided=YES — qwen-35b wrote 42-line Rust HTTP server using TcpListener + BufReader on unaided attempt 1. Scaffold not invoked.
- [08-02 build story]: build-status=PASS after 2 failures. Error 1: format! syntax (missing paren — agent's own task2 heredoc issue). Error 2: E0382 use of moved value (BufReader iterator moved twice). Both agent-diagnosed and agent-fixed in task3.
- [08-02 curl-result]: `hello\n`, exit 0 — task3-buildtest.jsonl ObservationEvent line #38. Primary RUST-03 evidence.
- [08-02 honesty]: zero manual edits; no fabrication. All 3 JSONL files reflect verbatim agent actions. No FinishAction in any JSONL (all ended with MessageEvent) — run settled via background process exit.

### Key decisions for v1.2 Phase 8 plan 01

- [08-01 prompt authoring]: task2-server.txt zero-leak discipline enforced — "any incoming HTTP request" → "any HTTP request it receives" (the word "incoming" triggers TcpListener::incoming() grep). All four leak-greps return 0.
- [08-01 preflight]: PREFLIGHT GREEN confirmed 2026-05-28 — rustc/cargo 1.95.0, port 8080 free, qwen-35b proxy live. oh-workdir-rust/ empty + gitignored.
- [08-01 scaffold]: task2-server-scaffold.txt staged; fallback policy documented in 00-INVOCATION.md — only triggers on 3+ identical build failures with no variation.

### Key decisions for v1.2 (just made)

- [v1.2 scope]: minimal HTTP server — `GET / → "hello\n"`, no other routes. Keeps the milestone tight and gives the 35B a fighting chance even if Rust ownership becomes a stumbling block.
- [v1.2 dependencies]: **std only** — no `hyper`/`axum`/`actix-web`. The agent must do the HTTP framing at the byte level (Status-Line, headers, blank line, body). Why: tutorial-grade visibility of what an HTTP response actually is; no framework knowledge requirement on the model.
- [v1.2 model]: 35B only (same model as v1). Tests the hypothesis that Rust is more in-distribution for 35B than FsLex was. Single-model run; no 35B-vs-122B comparison this milestone (could be a later milestone if interesting).
- [v1.2 placement]: new 6부 "다른 워킨 예제: Rust HTTP 서버" — structurally parallel to 4부 (calculator). Book becomes: 1부~5부 + 6부 + 부록 A/B/C.
- [v1.2 honesty]: same discipline as v1/v1.1 — capture as-written, no manual fixes, disclose any scaffolding. If 35B fails on Rust ownership / borrow checker / std::io edge cases, that's the chapter's material exactly as the FsLex story was v1's.
- [v1.2 phase structure]: 2 phases (8 + 9) — same tight additive shape as v1.1. Phase 8 closes with CAPTURE-MANIFEST.md committed (capture gate); Phase 9 cannot begin until gate is closed.

### Open tech debt (from v1.1 audit, deferrable; not in v1.2 scope)

- **TD-2**: event-71 → should be event 25 citation (CAPTURE-MANIFEST + 부록 C §2). ~5 min sed.
- **TD-3**: "events 9–30 (21 events)" should be 22 (inclusive count). Trivial.
- **TD-4**: cosmetic mdbook WARN on `<char>` HTML tag inside code span. Optional.
- **TD-5**: Sources section bibliography paths not clickable in 부록 C. v1.2-or-later polish opportunity.

### Key decisions for v1.2 Phase 9 plan 01

- [09-01 event-numbering]: Used CAPTURE-MANIFEST.md event numbers as authoritative (e.g., build-fail-1 = #16, E0382 = #28, curl = #37/#38). Raw JSONL line-indices differ due to non-JSON header/trailer lines in the JSONL files. The manifest is the plan's stated authoritative source.
- [09-01 audit]: Task 4 honesty audit PASSED — zero fabricated values, zero stale artifacts, no emoji in callouts, deploy.yml untouched.

### Key decisions for v1.2 Phase 9 plan 02

- [09-02 build-gate]: PUB-01 PASSED — mdbook build exit 0, zero errors, exactly one WARN (pre-existing <char> in appendix-c-comparison.md), zero new warnings for 6부.
- [09-02 sidebar-nav]: Confirmed via toc-e259f6ea.js — all five ch06-rust-server/*.html entries present in TOC JS. Sidebar nav uses collapsible JS tree, not inline HTML.
- [09-02 no-regression]: All 1부–5부 and 부록 A/B/C HTML files confirmed present post-build.

### Key decisions for v1.2 Phase 9 plan 03

- [09-03 deploy.yml-guard]: PUB-02 HARD GUARD PASSED — both `git diff -- .github/workflows/deploy.yml` and `git diff origin/main..HEAD -- .github/workflows/deploy.yml` returned zero output (byte-for-byte unchanged)
- [09-03 push]: Pushed 7 commits to origin/main (ff953b1..56bfcad). Keychain stderr noise is a headless SSH artifact, not a push failure.
- [09-03 actions]: Run 26731890916 — build (10s) + deploy (10s) both green; conclusion: success
- [09-03 live-verify]: root HTTP 200; ch06-rust-server/intro.html HTTP 200; toc-e259f6ea.js CDN contains all 5 ch06 pages; last-modified: Mon, 01 Jun 2026 02:24:44 GMT
- [09-03 toc-pattern]: mdbook sidebar nav is JS-rendered from toc-{hash}.js — check that file for live sidebar verification, not root HTML

### Pending Todos

- Run /gsd:audit-milestone (v1.2 milestone close-out, parallel to v1.1)

### Blockers/Concerns

None. Rust toolchain verified on host (rustc/cargo/rustup 1.95.0). LLM proxy still serving qwen-35b/122b/local.

## Session Continuity

Last session: 2026-06-01
Stopped at: 09-03 COMPLETE — 6부 live on GitHub Pages; v1.2 milestone shipped. Actions run 26731890916 green; HTTP 200 on root + ch06-rust-server/intro.html.
Resume file: None — next: /gsd:audit-milestone (v1.2 closeout).
