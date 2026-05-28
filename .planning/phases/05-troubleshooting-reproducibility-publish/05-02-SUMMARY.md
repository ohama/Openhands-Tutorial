---
phase: 05-troubleshooting-reproducibility-publish
plan: 02
subsystem: docs
tags: [mdbook, openhands, reproducibility, korean, appendix, fsharp, fslexyacc, litellm, qwen]

# Dependency graph
requires:
  - phase: 03-capture-the-openhands-run
    provides: captured/test-output.txt (verbatim 14/20/5), task-prompts/, CAPTURE-MANIFEST.md
  - phase: 05-troubleshooting-reproducibility-publish
    provides: 05-RESEARCH.md §2 (prereqs table, invocation, timings, error-and-fix summary)
provides:
  - src/appendix-a-repro.md — 부록 A 재현 가이드 (REPRO-01): prereqs, stack verify, verbatim invocation, task-prompt pointers, verbatim expected outputs (14/20/5)
affects:
  - 05-03 (SUMMARY.md wiring — must wire appendix-a-repro.md under "부록 A: 재현 가이드")
  - 05-04 (final deploy — appendix is part of the book to publish)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Verbatim-from-artifact prose: all values copied from committed artifacts, never fabricated"
    - "Korean prose with English technical terms: env vars, CLI flags, file names, error messages in English"
    - "No Markdown links to unwired SUMMARY entries: prose references only for 5부 cross-references"

key-files:
  created:
    - src/appendix-a-repro.md
  modified: []

key-decisions:
  - "부록 A title: 재현 가이드 (Reproducibility Guide) — not FAQ — per 05-RESEARCH.md §2.6 recommendation"
  - "Task prompts referenced by in-repo path (.planning/phases/03-capture-the-openhands-run/task-prompts/) rather than duplicated in appendix"
  - "IMPORTANT bash-only block quoted verbatim from REAL-04 / 00-INVOCATION.md — not paraphrased"
  - "Error-and-fix summary quoted from §2.5 5-line Attempt 1..5 block verbatim"
  - "Real timings cited (14-32s/cycle, ~6 min total, task1=3m6s etc.) — never 240s"

patterns-established:
  - "Appendix prose pattern: intro paragraph → prerequisites table → stack-verify commands → invocation → prompt pointers → expected outputs"
  - "Colima users: DOCKER_HOST note separated clearly from Docker Desktop path"

# Metrics
duration: 8min
completed: 2026-05-28
---

# Phase 05 Plan 02: Reproducibility Appendix Summary

**부록 A 재현 가이드 written: exact prereqs (8 components with versions), verbatim openai/qwen-local env-var invocation, task-prompt pointers with IMPORTANT bash-only block, and verbatim 14/20/5 expected outputs from captured/test-output.txt — satisfies REPRO-01 with zero fabrication**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-05-28T01:03:09Z
- **Completed:** 2026-05-28T01:11:00Z
- **Tasks:** 2 (combined into one file, two logical sections)
- **Files modified:** 1 created

## Accomplishments

- Created `src/appendix-a-repro.md` (193 lines) satisfying REPRO-01
- Verbatim env-var headless invocation from §2.3 — `openai/qwen-local`, `--override-with-envs`, full env block with Colima `DOCKER_HOST` note
- Prerequisites table with all 8 components (macOS, Colima/Docker, uv, OpenHands CLI v1.16.0/SDK v1.21.0, .NET SDK 10.0.203+, litellm proxy, Qwen2.5-35B, FsLexYacc 11.3.0)
- Task-prompt pointers at canonical in-repo path; key design choices (FixLineDirectives, Lexer.fsl verbatim, %left omission from task3, bash-only IMPORTANT block)
- Verbatim expected outputs from `captured/test-output.txt`: build success + `2+3*4 = 14`, `(2+3)*4 = 20`, `10-3-2 = 5`
- Error-and-fix cycle summary (task3 events 9–30, 5-line Attempt 1..5 block ending in `calc net10.0 성공 (0.7초)`)
- mdbook build exits 0 with file unwired (safe — SUMMARY.md still has empty `()` entries)

## Task Commits

1. **Task 1+2: Write 부록 A 재현 가이드** — `2a0506c` (docs)

**Plan metadata:** (this SUMMARY)

## Files Created/Modified

- `src/appendix-a-repro.md` — 부록 A: 재현 가이드, 193 lines, Korean prose with English technical terms; covers prereqs, stack verify, invocation, task-prompt pointers, expected outputs (REPRO-01)

## Decisions Made

- Used "재현 가이드" (Reproducibility Guide) as the appendix title rather than "자주 묻는 질문" (FAQ), per 05-RESEARCH.md §2.6 recommendation for clarity
- Task prompts referenced by repo path rather than duplicated — keeps appendix concise and avoids drift from canonical prompt files
- IMPORTANT bash-only block quoted verbatim (not paraphrased) to preserve exact instruction wording the model requires
- Real timings cited from §2.5: 14–32s/cycle, ~6 min total; "240s" figure never appears (unmeasured plan estimate)

## Deviations from Plan

None — plan executed exactly as written. Both tasks (prereqs+verify section; invocation+prompts+outputs section) combined into a single coherent appendix file as the plan specified.

## Issues Encountered

None.

## Next Phase Readiness

- `src/appendix-a-repro.md` exists and builds cleanly — ready for 05-03 to wire it into SUMMARY.md under `[부록 A: 재현 가이드](appendix-a-repro.md)`
- 05-03 must also wire `appendix-b-troubleshooting.md` (05-01 output) and `ch05-wrap-up/review.md` + `ch05-wrap-up/next-steps.md` (05-01 output)

---
*Phase: 05-troubleshooting-reproducibility-publish*
*Completed: 2026-05-28*
