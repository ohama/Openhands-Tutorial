# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-28)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run a real F# FsLex/FsYacc calculator. v1.1 extends this with an honest 35B-vs-122B comparison.
**Current focus:** v1.1 — Phase 6: Capture the 122B OpenHands Run

## Current Position

Milestone: v1.1 (Model Comparison) — STARTED 2026-05-28. v1 shipped & archived (live: https://ohama.github.io/Openhands-Tutorial/).
Phase: 6 of 7 (Capture the 122B OpenHands Run)
Plan: 1 of 3 in current phase
Status: In progress — 06-01 complete (prompts + preflight done); 06-02 next (execute run).
Last activity: 2026-05-28 — Completed 06-01-PLAN.md (task-prompts-122b/ + preflight green).

Progress: [█░░░░░░░░░] v1.1 17% (1/6 plans complete)

## Performance Metrics

**Velocity (v1 history):**
- Total plans completed: 16 (v1)
- Average duration: ~8 min
- Total execution time: ~50 min

**By Phase (v1):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01 scaffold | 3/3 ✓ | ~35 min | ~12 min |
| 02 environment | 3/3 ✓ | ~16 min | ~5 min |
| 03 capture 35B | 3/3 ✓ | ~? | ~? |
| 04 chapter | 3/3 ✓ | ~? | ~? |
| 05 publish | 4/4 ✓ | ~? | ~? |

*v1.1 metrics will accumulate from Phase 6 onward*

## Accumulated Context

### Key decisions for v1.1

- [v1.1 scope]: v1.1 is ADDITIVE — all v1 chapters stay; only a comparison chapter is added (new src/ file wired into SUMMARY.md)
- [v1.1 run config]: `LLM_MODEL="openai/qwen-122b" LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" openhands --headless --json --yolo --override-with-envs -t "<task>"` — same proven invocation as v1, just swap alias; 122B served @ :8001 via litellm
- [v1.1 protocol]: 122B attempts the WHOLE calculator including .fsl lexer UNAIDED FIRST (no task2-lexer.txt scaffold) — testing if it can do what 35B could not. Scaffold fallback only if it fails; must be disclosed, never hidden.
- [v1.1 capture gate]: Phase 7 (comparison chapter) cannot start until Phase 6 JSONL artifacts are committed — all comparison claims must trace to real captured evidence
- [v1.1 baseline]: 35B run is already captured in .planning/milestones/v1-phases/03-capture-the-openhands-run/captured/ — Phase 6 reuses it as baseline; no re-running the 35B
- [06-01 task2 unaided]: Chose fully unaided variant — omits even API hint (LexBuffer<_>.LexemeString) and %% note that RESEARCH.md recommended. Maximum honesty; API bugs are genuine error-and-fix material for task5.
- [06-01 retry floor]: task2-lexer-unaided-retry.txt adds one line: FsLex format is rule/parse (not %%), nothing else. Prevents format confusion without revealing implementation.
- [06-01 task4 variant]: task4-evaluator.txt used (not task4-evaluator-adjusted.txt) — original bash-only variant confirmed correct from v1 attempt 2.

### Pending Todos

None.

### Blockers/Concerns

None at roadmap creation. Phase 6 execution risk: 122B local inference may be slower than 35B; allow longer timeouts and expect a long autonomous run.

## Session Continuity

Last session: 2026-05-28T03:28:26Z
Stopped at: Completed 06-01-PLAN.md. task-prompts-122b/ ready, oh-workdir-122b/ gitignored and clean, proxy confirmed live.
Resume file: None — next step is execute 06-02-PLAN.md (the actual OpenHands run).
