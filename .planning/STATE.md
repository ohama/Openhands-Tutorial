# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-28)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run a real F# FsLex/FsYacc calculator. v1.1 extends this with an honest 35B-vs-122B comparison.
**Current focus:** v1.1 — COMPLETE. All phases delivered. Live: https://ohama.github.io/Openhands-Tutorial/appendix-c-comparison.html

## Current Position

Milestone: v1.1 (Model Comparison) — COMPLETE 2026-05-28. Live: https://ohama.github.io/Openhands-Tutorial/.
Phase: 7 of 7 (Comparison Chapter + Publish) — COMPLETE
Plan: 3 of 3 in phase 7 (07-03 complete — comparison chapter live on GitHub Pages)
Status: v1.1 COMPLETE. All 6 plans across Phases 6-7 done.
Last activity: 2026-05-28 — Completed 07-03-PLAN.md (pushed to origin/main, Actions deploy succeeded, 부록 C live).

Progress: [██████████] v1.1 100% (6/6 plans complete)

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

### Accumulated Decisions (added 06-03)

- [06-03 did-lexer-unaided]: YES — 122B wrote structurally valid FsLex on first unaided attempt (rule/parse, no %%). task2-lexer-unaided.jsonl event 9 is the proof artifact.
- [06-03 error-fix]: 8 API fix iterations in task5 (events 12–74) — agent-driven, no manual edits. Key API guesses: int s → Lexing.matched → matchedText → lexbuf.ToString() → lexbuf.Lexeme → new string(lexbuf.Lexeme) (final working).
- [06-03 outcome]: 14/20/5 confirmed both in JSONL (events 76/78/80) and fresh host re-run (test-output.txt).
- [06-03 capture gate]: CLOSED. captured-122b/ committed. Phase 7 can consume comparison claims.
- [06-03 timing]: 122B avg 6.3s/LLM call (150 calls, 20.5 min total). Faster per-call than 35B (~14–32s) but more calls due to longer lexer error-fix sequence.

### Accumulated Decisions (added 07-03)

- [07-03 nav-verification]: mdBook sidebar is JS-injected via `<mdbook-sidebar-scrollbox>` web component. Nav links live in toc.js, not root HTML. Future nav checks: `curl toc-*.js | grep href`.
- [07-03 push-warnings]: macOS Keychain `-25308` during `git push` is cosmetic; push succeeded. Not a failure signal.
- [07-03 v1.1-complete]: v1.1 fully delivered. 부록 C live. No further v1.1 work planned.

### Pending Todos

None. v1.1 complete.

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-05-28T06:24:10Z
Stopped at: Completed 07-03-PLAN.md. 부록 C live at https://ohama.github.io/Openhands-Tutorial/appendix-c-comparison.html. v1.1 done.
Resume file: None — v1.1 milestone complete.
