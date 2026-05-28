# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-28 — started v1.2 Rust Example)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run real programs. v1: F# FsLex/FsYacc calculator (35B). v1.1: same calculator with 122B, comparison. **v1.2: same 35B model, different language — a minimal Rust HTTP server.**
**Current focus:** v1.2 — defining requirements + roadmap.

## Current Position

Milestone: v1.2 (Rust Example) — STARTED 2026-05-28
Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-05-28 — v1.2 milestone started (PROJECT.md updated, between-milestones state cleared)

Progress: ░░░░░░░░░░ v1.2 0% (requirements and roadmap pending)
Live (v1 + v1.1): https://ohama.github.io/Openhands-Tutorial/

## Cumulative History

- **v1 MVP** (shipped 2026-05-28): 5 phases, 17 plans, Korean mdBook tutorial + 35B captured run of F# calculator. See `milestones/v1-ROADMAP.md`.
- **v1.1 Model Comparison** (shipped 2026-05-28): 2 phases, 6 plans, 122B capture + 부록 C comparison + UX callouts. See `milestones/v1.1-ROADMAP.md`.
- **v1.2 Rust Example** (started 2026-05-28): IN PROGRESS. Adds a second worked example (Rust HTTP server, 35B) as 6부.

## Accumulated Context

### Key decisions still live (carried across milestones)

- [stack]: Headless macOS (SSH) + Colima + OpenHands 1.16 headless CLI on LocalWorkspace; local litellm proxy at 127.0.0.1:4000 serving `openai/qwen-35b` and `openai/qwen-122b`; .NET 10 on host (verified) **+ rustc/cargo 1.95.0 on host (verified 2026-05-28)**
- [run-config]: `LLM_MODEL=openai/qwen-{35b|122b} LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy openhands --headless --json --yolo --override-with-envs -t "<task>"`
- [honesty discipline]: real captured runs only; no manual edits to agent-written files; setup-asymmetry (scaffolding) disclosed; pre-run predictions never presented as measurements
- [real measured per-call timing on this hardware]: 35B ≈ 5.3s/call, 122B ≈ 6.3s/call (from v1 + v1.1 JSONL)

### Key decisions for v1.2 (just made)

- [v1.2 scope]: minimal HTTP server — `GET / → "hello\n"`, no other routes. Keeps the milestone tight and gives the 35B a fighting chance even if Rust ownership becomes a stumbling block.
- [v1.2 dependencies]: **std only** — no `hyper`/`axum`/`actix-web`. The agent must do the HTTP framing at the byte level (Status-Line, headers, blank line, body). Why: tutorial-grade visibility of what an HTTP response actually is; no framework knowledge requirement on the model.
- [v1.2 model]: 35B only (same model as v1). Tests the hypothesis that Rust is more in-distribution for 35B than FsLex was. Single-model run; no 35B-vs-122B comparison this milestone (could be a later milestone if interesting).
- [v1.2 placement]: new 6부 "다른 워킨 예제: Rust HTTP 서버" — structurally parallel to 4부 (calculator). Book becomes: 1부~5부 + 6부 + 부록 A/B/C.
- [v1.2 honesty]: same discipline as v1/v1.1 — capture as-written, no manual fixes, disclose any scaffolding. If 35B fails on Rust ownership / borrow checker / std::io edge cases, that's the chapter's material exactly as the FsLex story was v1's.

### Open tech debt (from v1.1 audit, deferrable; not in v1.2 scope)

- **TD-2**: event-71 → should be event 25 citation (CAPTURE-MANIFEST + 부록 C §2). ~5 min sed.
- **TD-3**: "events 9–30 (21 events)" should be 22 (inclusive count). Trivial.
- **TD-4**: cosmetic mdbook WARN on `<char>` HTML tag inside code span. Optional.
- **TD-5**: Sources section bibliography paths not clickable in 부록 C. v1.2-or-later polish opportunity.

### Pending Todos

- Decide on research (Phase 7 of /gsd:new-milestone): research vs skip
- Define v1.2 requirements (REQ-IDs in RUST-* category, ~3-5 requirements expected)
- Build roadmap (Phases 8–9 of new milestone? — continuing numbering from v1.1's Phase 7)

### Blockers/Concerns

None. Rust toolchain verified on host (rustc/cargo/rustup 1.95.0). LLM proxy still serving qwen-35b/122b/local.

## Session Continuity

Last session: 2026-05-28T~16:30Z
Stopped at: v1.2 milestone started; PROJECT.md updated with Current Milestone section; STATE.md reset; next step is /gsd:new-milestone Phase 7 (research decision).
Resume file: None — continue in the /gsd:new-milestone flow.
