# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-01 — v1.2 Rust Example shipped)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run real programs. v1: F# FsLex/FsYacc calculator (35B). v1.1: same calculator with 122B, comparison. v1.2: same 35B, different language — a minimal Rust HTTP server (6부).
**Current focus:** Between milestones — v1.2 shipped + archived 2026-06-01. Next milestone scoped via `/gsd:new-milestone`.

## Current Position

Milestone: None active — v1.2 (Rust Example) SHIPPED + archived 2026-06-01.
Phase: None active — phases 1–9 all complete and archived under `.planning/milestones/`.
Plan: Not started — awaiting next milestone definition.
Status: Ready to plan. Run `/gsd:new-milestone` to scope the next worked example / comparison / translation.
Last activity: 2026-06-01 — /gsd:complete-milestone v1.2 (archived roadmap/requirements/audit/phases; tagged milestone-v1.2).

Progress: ✅ v1 + v1.1 + v1.2 shipped (9 phases, 29 plans total). No active milestone.
Live: https://ohama.github.io/Openhands-Tutorial/ (6부 Rust example at /ch06-rust-server/intro.html)

## Cumulative History

- **v1 MVP** (shipped 2026-05-28): 5 phases, 17 plans, Korean mdBook tutorial + 35B captured run of F# calculator. See `milestones/v1-ROADMAP.md`.
- **v1.1 Model Comparison** (shipped 2026-05-28): 2 phases, 6 plans, 122B capture + 부록 C comparison + UX callouts. See `milestones/v1.1-ROADMAP.md`.
- **v1.2 Rust Example** (shipped 2026-06-01): 2 phases, 6 plans, 35B Rust HTTP server capture + 6부 chapter (다른 워킹 예제) live. Confirmed Rust is more in-distribution for 35B than FsLex was (wrote the server unaided where it failed FsLex). Audit caught + fixed TD-6 (timing prediction mislabeled as measurement). See `milestones/v1.2-ROADMAP.md`.

## Accumulated Context

### Key decisions still live (carried across milestones)

- [stack]: Headless macOS (SSH) + Colima + OpenHands 1.16 headless CLI on LocalWorkspace; local litellm proxy at 127.0.0.1:4000 serving `openai/qwen-35b` and `openai/qwen-122b`; .NET 10 on host (verified) + rustc/cargo 1.95.0 on host (verified 2026-05-28).
- [run-config]: `LLM_MODEL=openai/qwen-{35b|122b} LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy openhands --headless --json --yolo --override-with-envs -t "<task>"`.
- [honesty discipline]: real captured runs only; no manual edits to agent-written files; setup-asymmetry (scaffolding) disclosed; **pre-run predictions never presented as measurements** (enforced again in v1.2 audit — TD-6).
- [real measured per-call timing on this hardware]: 35B ≈ 5.3s/call (v1 F# derived; v1.2 Rust run ≈ 3.8s/call), 122B ≈ 6.3s/call. The legacy "~14–32s/call" figure is a v1 pre-run prediction, NOT a measurement — do not cite it as measured.
- [publish]: book deploys to GitHub Pages via `.github/workflows/deploy.yml` on push to `main` (do NOT modify the workflow); mdbook sidebar nav is JS-rendered from `toc-{hash}.js` — verify live sidebar there, not in root HTML. One accepted build warning: the `<char>` tag in 부록 C (TD-4).

### Open tech debt (deferrable; carried forward — not yet addressed)

- **TD-2**: 부록 C event-71 → should be event-25 citation (CAPTURE-MANIFEST + 부록 C §2). ~5 min sed.
- **TD-3**: 부록 C "events 9–30 (21 events)" should be 22 (inclusive count). Trivial.
- **TD-4**: cosmetic mdbook WARN on `<char>` HTML tag inside a code span (부록 C). The one accepted build warning.
- **TD-5**: 부록 C Sources bibliography paths not clickable.
- (v1.2 TD-6/TD-7/TD-8 were fixed during the v1.2 audit close-out — see `milestones/v1.2-MILESTONE-AUDIT.md`.)

### Candidate next milestones (no commitment)

- EXT-01: more-language worked examples (Go / Python), following the Rust precedent.
- EXT-06: 35B-vs-122B comparison on the Rust example (parallel to v1.1 for F#).
- EXT-02: English translation. EXT-03: "build your own minimal agent in F#" appendix. EXT-04: local-vs-cloud comparison. EXT-05: Rust with a framework.

### Blockers/Concerns

None. Toolchains verified on host (.NET 10, rustc/cargo 1.95.0). LLM proxy serving qwen-35b/122b/local.

## Session Continuity

Last session: 2026-06-01
Stopped at: v1.2 milestone shipped + archived; tag milestone-v1.2 created. Book live with 6부.
Resume file: None — next: `/gsd:new-milestone` to scope the next milestone.
