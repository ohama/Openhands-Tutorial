# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-01 — v1.3 Scala Example shipped)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run real programs. The book teaches via REAL captured runs: v1 F# calculator (35B), v1.1 122B comparison (부록 C), v1.2 Rust HTTP server (6부), v1.3 Scala calculator (7부).
**Current focus:** Between milestones — v1.3 shipped + archived 2026-06-01. The "calculator trilogy" (F#/Rust/Scala) is complete. Next milestone scoped via `/gsd:new-milestone`.

## Current Position

Milestone: None active — v1.3 (Scala Example) SHIPPED + archived 2026-06-01.
Phase: None active — phases 1–11 all complete and archived under `.planning/milestones/`.
Plan: Not started — awaiting next milestone definition.
Status: Ready to plan. Run `/gsd:new-milestone` to scope the next worked example / cross-language comparison appendix / translation.
Last activity: 2026-06-01 — /gsd:complete-milestone v1.3 (archived roadmap/requirements/audit/phases; tagged milestone-v1.3).

Progress: ✅ v1 + v1.1 + v1.2 + v1.3 shipped (11 phases, 35 plans total). No active milestone.
Live: https://ohama.github.io/Openhands-Tutorial/ (worked examples: 4부 F# calc · 6부 Rust server · 7부 Scala calc · 부록 C model comparison)

## Cumulative History

- **v1 MVP** (shipped 2026-05-28): 5 phases, 17 plans, Korean mdBook tutorial + 35B captured run of F# FsLex/FsYacc calculator. See `milestones/v1-ROADMAP.md`.
- **v1.1 Model Comparison** (shipped 2026-05-28): 2 phases, 6 plans, 122B capture + 부록 C 35B-vs-122B comparison + UX callouts. See `milestones/v1.1-ROADMAP.md`.
- **v1.2 Rust Example** (shipped 2026-06-01): 2 phases, 6 plans, 35B Rust HTTP server (6부) — unaided. See `milestones/v1.2-ROADMAP.md`.
- **v1.3 Scala Example** (shipped 2026-06-01): 2 phases, 6 plans, 35B Scala 3 calculator (7부) — unaided, one self-corrected compile error. Completes the calculator trilogy; confirms capability is domain-distribution, not model size. See `milestones/v1.3-ROADMAP.md`.

## Accumulated Context

### Key decisions still live (carried across milestones)

- [stack]: Headless macOS (SSH) + Colima + OpenHands 1.16 headless CLI on LocalWorkspace; local litellm proxy at 127.0.0.1:4000 serving `openai/qwen-35b` and `openai/qwen-122b`. Verified host toolchains: .NET 10, rustc/cargo 1.95.0, scala-cli 1.14.0 (Scala 3.8.3) + JDK 17.
- [run-config]: `OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openai/qwen-{35b|122b} LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy OPENHANDS_WORK_DIR=<wd> openhands --headless --json --yolo --override-with-envs -t "<task>"`. Capture pattern: background the run, `tee` to per-task JSONL, poll for settle (FinishAction/idle). The CLI exits 0 regardless of task success — judge from the JSONL, not the exit code.
- [honesty discipline]: real captured runs only; no manual edits to agent-written files; `source=agent` on every ActionEvent (mechanical python3 gate before any commit); scaffolding disclosed; **pre-run predictions never presented as measurements**.
- [real measured per-call timing]: 35B ≈ 5.3s/call (v1 F# derived) / 3.8s/call (v1.2 Rust) / ~5.0s/call (v1.3 Scala); 122B ≈ 6.3s/call. The legacy `~14–32s/call` figure is a v1 pre-run PREDICTION, NOT a measurement.
- [capture event-numbering]: chapters cite the CAPTURE-MANIFEST's 1-based event numbers, NOT RUN-NOTES 0-based scratchpad positions (recurring tech debt — v1.2 TD-7/TD-8; held correct in v1.3).
- [35B capability]: domain-distribution, not size — fails OOD DSLs (FsLex) but writes in-distribution languages (Rust std, Scala 3) unaided; errors it makes are teachable in-distribution mistakes (borrow-checker, access modifiers).
- [publish]: book deploys to GitHub Pages via `.github/workflows/deploy.yml` on push to `main` (do NOT modify); mdbook sidebar nav is JS-rendered from `toc-{hash}.js` — verify live sidebar there. One accepted build warning: the `<char>` tag in 부록 C (TD-4).

### Open tech debt (deferrable; carried forward — not yet addressed)

- **TD-2**: 부록 C event-71 → should be event-25 citation. ~5 min sed.
- **TD-3**: 부록 C "events 9–30 (21 events)" should be 22 (inclusive count). Trivial.
- **TD-4**: cosmetic mdbook WARN on `<char>` HTML tag inside a code span (부록 C). The one accepted build warning.
- **TD-5**: 부록 C Sources bibliography paths not clickable.
- (v1.2 TD-6/7/8 and v1.3 TD-9/10 were fixed during their respective milestone audits.)

### Candidate next milestones (no commitment)

- EXT-07: cross-language "calculator in 3 languages" comparison appendix (F# / Scala / + future) — now natural since the trilogy is complete; language-axis parallel to 부록 C's model-axis comparison.
- EXT-01: more-language worked examples (Go / Python), following the precedent.
- EXT-06: 35B-vs-122B comparison on the Rust or Scala example.
- EXT-02: English translation. EXT-03: "build your own minimal agent" appendix. EXT-04: local-vs-cloud comparison. EXT-05: Rust/Scala with a framework.

### Blockers/Concerns

None. Host toolchains verified (.NET 10, rustc/cargo 1.95.0, scala-cli 1.14.0 + JDK 17). LLM proxy serving qwen-35b/122b/local.

## Session Continuity

Last session: 2026-06-01
Stopped at: v1.3 milestone shipped + archived; tag milestone-v1.3 created. Calculator trilogy live.
Resume file: None — next: `/gsd:new-milestone` to scope the next milestone.
