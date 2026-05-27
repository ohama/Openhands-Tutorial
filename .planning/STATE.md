# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-27)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run a real F# FsLex/FsYacc calculator.
**Current focus:** Phase 1 — Scaffold & Concept Chapters

## Current Position

Phase: 1 of 5 (Scaffold & Concept Chapters)
Plan: 1 of 4 in current phase
Status: In progress
Last activity: 2026-05-27 — Completed 01-01-PLAN.md (mdBook scaffold: book.toml, SUMMARY.md, about.md, stubs)

Progress: [█░░░░░░░░░] 5% (1/20 plans)

## Performance Metrics

**Velocity:**
- Total plans completed: 1
- Average duration: ~15 min
- Total execution time: ~15 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-scaffold-and-concept-chapters | 1/4 | ~15 min | ~15 min |

**Recent Trend:**
- Last 5 plans: 01-01 (~15 min)
- Trend: Baseline established

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Capture gate enforced — Phase 3 (run capture) strictly depends on Phase 2 (verified env); Phase 4 (worked-example chapter) strictly depends on Phase 3
- [Roadmap]: VERIFY-01 and VERIFY-02 placed in Phase 4 (not Phase 3) — verification content belongs in the walkthrough chapter, written from captured evidence
- [Roadmap]: BOOK-01 and BOOK-02 placed in Phase 1 — mdBook scaffold and Korean language constraint apply from the very first chapter
- [01-01]: mdbook installed via brew (0.5.3) — was not pre-installed; use /opt/homebrew/bin/mdbook in all subsequent plans
- [01-01]: mdBook 0.5.x site-url goes into 404.html base href, not index.html asset paths — this is correct behavior for GitHub Pages project sites

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 2]: Exact model id string after `openai/` must be confirmed via `curl http://127.0.0.1:8000/v1/models` before configuring OpenHands
- [Phase 2]: `agent_settings.json` config key names not confirmed (official reference 404'd during research — validate against running OpenHands 1.7)
- [Phase 2]: OpenHands 1.7 ARM64 vs Rosetta status on Apple Silicon needs verification at setup time
- [Phase 3]: 35B local model reliability over a long multi-step loop is empirical — task decomposition into ≥5 narrow tasks is the primary mitigation

## Session Continuity

Last session: 2026-05-27
Stopped at: Completed 01-01-PLAN.md — mdBook scaffold complete, mdbook build exits 0
Resume file: None
