# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-27)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run a real F# FsLex/FsYacc calculator.
**Current focus:** Phase 1 — Scaffold & Concept Chapters

## Current Position

Phase: 1 of 5 (Scaffold & Concept Chapters)
Plan: 0 of 4 in current phase
Status: Ready to plan
Last activity: 2026-05-27 — Roadmap created; all 20 v1 requirements mapped to 5 phases

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: —
- Total execution time: 0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: —
- Trend: —

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Capture gate enforced — Phase 3 (run capture) strictly depends on Phase 2 (verified env); Phase 4 (worked-example chapter) strictly depends on Phase 3
- [Roadmap]: VERIFY-01 and VERIFY-02 placed in Phase 4 (not Phase 3) — verification content belongs in the walkthrough chapter, written from captured evidence
- [Roadmap]: BOOK-01 and BOOK-02 placed in Phase 1 — mdBook scaffold and Korean language constraint apply from the very first chapter

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 2]: Exact model id string after `openai/` must be confirmed via `curl http://127.0.0.1:8000/v1/models` before configuring OpenHands
- [Phase 2]: `agent_settings.json` config key names not confirmed (official reference 404'd during research — validate against running OpenHands 1.7)
- [Phase 2]: OpenHands 1.7 ARM64 vs Rosetta status on Apple Silicon needs verification at setup time
- [Phase 3]: 35B local model reliability over a long multi-step loop is empirical — task decomposition into ≥5 narrow tasks is the primary mitigation

## Session Continuity

Last session: 2026-05-27
Stopped at: Roadmap created, STATE.md and REQUIREMENTS.md traceability initialized
Resume file: None
