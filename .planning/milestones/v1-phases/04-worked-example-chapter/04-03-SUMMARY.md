---
phase: 04-worked-example-chapter
plan: "03"
subsystem: documentation
tags: [korean, mdbook, fsharp, fslexyyacc, calculator, verification]

requires:
  - phase: 03-capture-the-openhands-run
    provides: captured/final-source (4 files verbatim) + captured/test-output.txt (14/20/5 block)
  - phase: 04-worked-example-chapter
    provides: 04-RESEARCH.md with verified performance numbers and honesty constraints

provides:
  - src/ch04-calculator/final.md — complete final-source recap (WALK-03), verbatim 14/20/5 verification block (VERIFY-01), honest performance note with real timings (VERIFY-02)

affects:
  - 04-04 (SUMMARY.md wiring — final.md must exist before SUMMARY.md links it)
  - 05-appendix (references the performance/limits story established here)

tech-stack:
  added: []
  patterns:
    - "Verbatim embed pattern: all 4 source files quoted directly from captured/final-source/ with no editing"
    - "Dual-label pattern: provided files (Lexer.fsl, calc.fsproj) carry exact Korean honesty labels; agent-authored files labeled separately"
    - "Honest-numbers pattern: all timing figures traceable to 03-02-RUN-NOTES.md timestamps; zero invented or estimated figures"

key-files:
  created:
    - src/ch04-calculator/final.md
  modified: []

key-decisions:
  - "Verification block is the verbatim captured/test-output.txt including Korean build output (복원할 프로젝트를 확인하는 중..., 오류 0개) — no translation or paraphrase"
  - "Performance note uses RESEARCH §7 draft paragraph almost verbatim; '약 150분' phrasing honors the RESEARCH §8.3 approximation caveat"
  - "No 240s figure anywhere — per honesty constraint 2D; figure was stale estimate never measured in evidence"
  - "open System leftover noted factually (no editorializing) per plan task 1 action spec"

patterns-established:
  - "final.md is the authoritative source for WALK-03 + VERIFY-01 + VERIFY-02; build-test.md forward-references here"
  - "Closing prose uses 1부 vocabulary callouts without Markdown links to unwritten 5부/부록 files"

duration: ~6min
completed: 2026-05-28
---

# Phase 4 Plan 03: Final Source + Verification Chapter Summary

**완성된 계산기 (final.md): 4개 파일 전문 임베드 + 14/20/5 검증 블록 + 시도-1 실패/시도-2 성능 솔직 기록**

## Performance

- **Duration:** ~6 min
- **Started:** 2026-05-28T00:25:01Z
- **Completed:** 2026-05-28T00:31:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Wrote `src/ch04-calculator/final.md` (225 lines) covering WALK-03, VERIFY-01, and VERIFY-02
- Embedded all four captured final-source files verbatim; Lexer.fsl and calc.fsproj carry the exact Korean honesty labels from RESEARCH §5
- Quoted test-output.txt verification block verbatim (Korean build output + three test cases) with per-case prose explanation (precedence / grouping / left-associativity)
- Wrote the honest performance paragraph using real numbers from 03-02-RUN-NOTES.md: attempt-2 ~10 min (task2 16s, task5 32s, task1 3m 6s, task3 1m 17s); attempt-1 ~150 min FAILED (FsLex out-of-distribution for 35B, 94+27+16 TerminalActions); zero occurrences of the stale "240s" figure

## Task Commits

1. **Task 1: Write final.md** - `c0f0a06` (docs)

**Plan metadata:** (included in task commit — single-task plan)

## Files Created/Modified

- `src/ch04-calculator/final.md` — 4부 closing chapter: verbatim source + verification + honest perf note

## Decisions Made

- Quoted test-output.txt verbatim including Korean dotnet output lines (`복원할 프로젝트를 확인하는 중...`, `오류 0개`) — these are authentic captured output, not translated
- Used RESEARCH §7 draft paragraph nearly verbatim for performance note; adapted lightly for prose flow while preserving every number exactly
- "약 150분" phrasing used for attempt-1 duration per RESEARCH §8.3 (approximation, not a precise figure)
- Closed with prose-only forward reference to 5부/부록 per [01-02] decision: no Markdown links to unwritten files

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `src/ch04-calculator/final.md` exists and committed; 04-04 can now wire SUMMARY.md to link all five ch04 files
- WALK-03, VERIFY-01, VERIFY-02 requirements fully satisfied in this file
- No blockers for 04-04

---
*Phase: 04-worked-example-chapter*
*Completed: 2026-05-28*
