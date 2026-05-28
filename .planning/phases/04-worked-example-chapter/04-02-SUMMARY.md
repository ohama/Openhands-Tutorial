---
phase: 04-worked-example-chapter
plan: 02
subsystem: docs
tags: [korean, mdbook, fsharp, fsyacc, openhands, writing, build-test, error-and-fix]

# Dependency graph
requires:
  - phase: 03-capture-the-openhands-run
    provides: transcript.md, task3-parser.jsonl, final-source/Parser.fsy, final-source/Program.fs with verbatim error-and-fix evidence

provides:
  - src/ch04-calculator/writing.md: Korean prose narrating agent writing Parser.fsy (correct %left from start) + Program.fs; tool calling + memory callouts (A, C); verbatim Parser.fsy embed (WALK-03)
  - src/ch04-calculator/build-test.md: Korean prose narrating 4 real build failures (FSY000, parse error x2, FS0039) with verbatim quotes, observed->decided->corrected format, honest no-ThinkAction disclosure for F3; agent loop callout (B)

affects:
  - 04-03 (final.md) needs final source embed + verification block
  - 04-04 (SUMMARY.md wiring) needs both files to exist
  - Any future ch04 editing must maintain honesty constraints: no precedence bug, verbatim evidence only

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Evidence-faithful Korean narration: all error text verbatim from captured JSONL/transcript; no invented reasoning where ThinkAction absent"
    - "Observed->decided->corrected structure for each build failure cycle"
    - "Concept callouts linking ch04 agent actions to ch01 vocabulary terms"

key-files:
  created:
    - src/ch04-calculator/writing.md
    - src/ch04-calculator/build-test.md
  modified: []

key-decisions:
  - "No precedence bug narrative: agent wrote correct %left PLUS MINUS / %left STAR SLASH on first attempt; error-and-fix is purely FsYacc syntax + F# API issues"
  - "F3 honest disclosure: no ThinkAction recorded for third build failure; stated explicitly as such, no invented rationale"
  - "Out-of-scope Program.fs noted as observed genuine agent behavior that exceeded task3 scope"
  - "Callout C (memory) placed in writing.md: cross-invocation persistence in filesystem not LLM EventLog"
  - "Forward refs to final.md for Program.fs full source and official verification block (prose only, no dead Markdown links)"

patterns-established:
  - "4부 chapters use blockquote callout format: > **개념 ↔ 행동: [term]** with ch01 cross-reference"
  - "WALK-02 satisfied with observed->decided->corrected structure per build failure"
  - "WALK-03 satisfied with verbatim Parser.fsy embed in writing.md"

# Metrics
duration: 12min
completed: 2026-05-28
---

# Phase 4 Plan 02: Writing + Build-Test Chapters Summary

**Korean 4부 chapters narrating agent writing Parser.fsy with correct %left precedence (WALK-03) and self-correcting 4 real FsYacc/F# build failures observed->decided->corrected (WALK-02), with verbatim error text from captured JSONL logs**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-28T~07:00Z
- **Completed:** 2026-05-28
- **Tasks:** 2 (writing.md, build-test.md)
- **Files modified:** 2 created

## Accomplishments

- writing.md (149 lines): narrates task1 scaffolding struggle (summarized), task2 lexer copy-in, task3 parser writing; agent writes correct `%left PLUS MINUS` / `%left STAR SLASH` on first attempt; Program.fs out-of-scope agent behavior documented; Callouts A (tool calling = CmdRunAction dotnet build) and C (memory = filesystem cross-invocation persistence) tied to ch01 vocabulary; verbatim Parser.fsy embed (WALK-03)
- build-test.md (187 lines): all 4 real build failures narrated with verbatim error text (FSY000, `Parser.fsy(16,7): error parse error` x2, FS0039 LexBuffer.FromText), verbatim ThinkAction quotes for F1/F2/F4, explicit no-ThinkAction disclosure for F3; verbatim success block + agent's 8-expression in-task validation; Callout B (agent loop = self-correction as natural loop consequence) tied to ch01 vocabulary
- HONESTY maintained throughout: no precedence bug narrated; F3 reasoning gap stated explicitly; no "240" string; no dead Markdown links

## Task Commits

1. **Task 1: writing.md + Task 2: build-test.md** - `e519147` (docs)

**Plan metadata:** (follows below)

## Files Created/Modified

- `src/ch04-calculator/writing.md` - 코드 작성 단계: agent Parser.fsy authoring, tool calling + memory callouts, Parser.fsy embed
- `src/ch04-calculator/build-test.md` - 빌드와 테스트 단계: 4 build failures observed->decided->corrected, agent loop callout

## Decisions Made

- Confirmed: no precedence bug ever occurred; error-and-fix is pure FsYacc `%start` syntax confusion + non-existent `LexBuffer.FromText` API — chapters narrate exactly this
- F3 ThinkAction absence: stated as "이 단계에서는 ThinkAction이 기록되지 않았습니다" with no invented reasoning
- Program.fs out-of-scope: framed as observed genuine agent behavior (task3 exceeded scope to verify build, which caused F4)
- Callout placement: A + C in writing.md (tool calling, memory); B in build-test.md (agent loop); combined with Callout D in 04-01 gives 4 total callouts across ch04

## Deviations from Plan

None - plan executed exactly as written. Both files produced from verbatim captured evidence.

## Issues Encountered

None.

## Next Phase Readiness

- writing.md and build-test.md complete; ch04-calculator directory exists
- 04-01 (intro.md, planning.md) and 04-03 (final.md) remain per parallel agents
- 04-04 can wire SUMMARY.md once all 5 ch04 files exist
- No blockers for 04-03 or 04-04

---
*Phase: 04-worked-example-chapter*
*Completed: 2026-05-28*
