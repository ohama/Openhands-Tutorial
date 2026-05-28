# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-28 after v1.1 shipped)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run a real F# FsLex/FsYacc calculator. v1.1 added an honest 35B-vs-122B comparison.
**Current focus:** Between milestones — v1.1 shipped and archived. Next milestone not yet defined.

## Current Position

Milestone: v1.1 (Model Comparison) — ✅ SHIPPED + AUDITED + ARCHIVED 2026-05-28.
Phase: — (no active phase)
Plan: — (no active plan)
Status: Ready to plan next milestone (or stay shipped).
Last activity: 2026-05-28 — Completed /gsd:complete-milestone v1.1 (audit archived, requirements archived, phases archived, MILESTONES.md updated, PROJECT.md evolved).

Progress: ✅ v1 ✅ v1.1 — both shipped.
Live: https://ohama.github.io/Openhands-Tutorial/

## Cumulative History

- **v1 MVP** (shipped 2026-05-28): 5 phases, 17 plans, Korean mdBook tutorial with one captured 35B run. See `milestones/v1-ROADMAP.md`.
- **v1.1 Model Comparison** (shipped 2026-05-28): 2 phases, 6 plans, 122B capture + 부록 C comparison chapter + beginner UX callouts. See `milestones/v1.1-ROADMAP.md`.

## Accumulated Context

### Key decisions still live (carried across milestones)

- [stack]: Headless macOS (SSH) + Colima + OpenHands 1.16 headless CLI on LocalWorkspace; local litellm proxy at 127.0.0.1:4000 serving `openai/qwen-35b` and `openai/qwen-122b`; .NET 10 on host
- [run-config]: `LLM_MODEL=openai/qwen-{35b|122b} LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy openhands --headless --json --yolo --override-with-envs -t "<task>"`
- [honesty discipline]: real captured runs only; no manual edits to agent-written files; setup-asymmetry (scaffolding) disclosed; pre-run predictions never presented as measurements
- [real measured per-call timing]: 35B ≈ 5.3s, 122B ≈ 6.3s (derived from JSONL timestamps); the legacy "~14–32s/cycle" was a pre-run estimate, not measured data

### Open tech debt (from v1.1 audit, deferrable)

- **TD-2** (v1.1-MILESTONE-AUDIT.md): event-71 citation in CAPTURE-MANIFEST + 부록 C §2 should be event 25 — ~5 min sed
- **TD-3**: "events 9–30 (21 events)" should be 22 — trivial
- **TD-4**: cosmetic mdbook WARN on `<char>` HTML tag inside `LexBuffer<char>.FromString` code span — optional
- **TD-5**: Sources section bibliography paths in 부록 C not clickable — v1.2 polish opportunity

### Pending Todos

- **Doc-language polish (raised post-audit by user, not yet executed):**
  - Remove internal v1/v1.1 version labels from reader-facing chapter text (those are implementation/process labels, not pedagogy)
  - Correct the 35B model identifier: it is **Qwen 3.6 35B**, NOT Qwen 2.5 (the 부록 C heading currently says "Qwen2.5-35B")

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-05-28T~15:55Z
Stopped at: v1.1 milestone completion in progress (archive built; doc-language polish requested by user mid-flow; commits + git tag pending).
Resume file: None — continue with the doc-language polish + commit + tag (or run `/gsd:new-milestone` for the next milestone).
