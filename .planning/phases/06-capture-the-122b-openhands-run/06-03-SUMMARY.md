---
phase: 06-capture-the-122b-openhands-run
plan: 03
subsystem: capture
tags: [openhands, qwen-122b, jsonl, fsharp, fslexyyacc, capture-manifest]

requires:
  - phase: 06-capture-the-122b-openhands-run/02
    provides: "5 per-task JSONL files in oh-workdir-122b/ from the actual 122B run"

provides:
  - "captured-122b/logs/ — 5 committed JSONL files (task1–task5)"
  - "captured-122b/final-source/ — 4 verbatim agent-produced F# source files"
  - "captured-122b/test-output.txt — fresh host 3-case re-run (14/20/5)"
  - "captured-122b/transcript.md — human-readable per-task summary"
  - "captured-122b/CAPTURE-MANIFEST.md — all Phase-7 fields indexed and cited"

affects: [07-comparison-chapter, CAPTURE-MANIFEST, comparison-claims]

tech-stack:
  added: []
  patterns:
    - "JSONL event analysis via Python (datetime.fromisoformat for timing; nested action/observation schema)"
    - "ObservationEvent → next ActionEvent gap as proxy for LLM inference time"
    - "Per-task TerminalAction count as proxy for agent effort"

key-files:
  created:
    - ".planning/phases/06-capture-the-122b-openhands-run/captured-122b/CAPTURE-MANIFEST.md"
    - ".planning/phases/06-capture-the-122b-openhands-run/captured-122b/transcript.md"
    - ".planning/phases/06-capture-the-122b-openhands-run/captured-122b/test-output.txt"
    - ".planning/phases/06-capture-the-122b-openhands-run/captured-122b/logs/ (5 JSONL + 5 stderr)"
    - ".planning/phases/06-capture-the-122b-openhands-run/captured-122b/final-source/ (4 files)"
  modified:
    - ".planning/STATE.md"

key-decisions:
  - "did-lexer-unaided: YES — agent wrote structurally valid FsLex on first unaided attempt (rule/parse, no %%)"
  - "task6-fix not needed — agent self-completed in task5 (14/20/5 all passed)"
  - "8 fix iterations documented in manifest (task5 events 12–74) — all agent-driven, zero manual edits"
  - "CAPTURE-MANIFEST cites JSONL event numbers for every claim — Phase 7 can audit directly"

patterns-established:
  - "Capture gate pattern: Phase 7 cannot consume comparison claims until committed JSONL evidence exists here"
  - "Honest disclosure pattern: did-lexer-unaided + unaided-attempts + fallback-disclosure fields in manifest"

duration: 45min
completed: 2026-05-28
---

# Phase 06 Plan 03: Verify & Commit Captured 122B Run Summary

**122B run verified: did-lexer-unaided=YES, 8 API fix iterations in task5 (events 12–74), 14/20/5 host-confirmed — all committed to captured-122b/ with full JSONL citations.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-05-28T~14:00Z
- **Completed:** 2026-05-28T~14:45Z
- **Tasks:** 3 of 3
- **Files modified:** 14 created, 1 modified

## Accomplishments

- Programmatic JSONL verification confirmed all 5 per-task logs are non-empty, well-formed, and have Action+Observation events; extracted timing, 3-case outcome, and 8-iteration error-and-fix sequence
- Snapshotted final agent source (Lexer.fsl with `new string(lexbuf.Lexeme)`, Parser.fsy with `%left` precedence, correct Program.fs) and ran fresh host build + 3-case test confirming 14/20/5
- Wrote CAPTURE-MANIFEST.md with all Phase-7 fields (did-lexer-unaided=YES, RUN122-01/02/03, error-fix table with event citations, timing per task + per-LLM-call avg, comparison hooks vs 35B) and committed everything to captured-122b/

## Task Commits

Each task was committed atomically (see final commit for all artifacts together):

1. **Task 1: Verify JSONL integrity + extract timing/outcome/error-fix** — Data extracted; logs copied to captured-122b/logs/
2. **Task 2: Snapshot final source + host test run + write manifest** — final-source/, test-output.txt, transcript.md, CAPTURE-MANIFEST.md created
3. **Task 3: Commit captured-122b/ artifacts** — `docs(06-03): verify & commit captured 122B run artifacts`

## Files Created/Modified

- `captured-122b/logs/task1-scaffold.jsonl` — 43 events, 20 TerminalActions
- `captured-122b/logs/task2-lexer-unaided.jsonl` — 16 events, 7 TA; unaided proof (event 9)
- `captured-122b/logs/task3-parser.jsonl` — 79 events, 37 TA, FinishAction
- `captured-122b/logs/task4-evaluator.jsonl` — 98 events, 47 TA
- `captured-122b/logs/task5-buildtest.jsonl` — 83 events, 39 TA; error-fix events 12–74, tests 76/78/80
- `captured-122b/logs/*.stderr.log` — 5 stderr logs
- `captured-122b/final-source/Lexer.fsl` — Final: `new string(lexbuf.Lexeme)` API
- `captured-122b/final-source/Parser.fsy` — `%left PLUS MINUS` / `%left STAR SLASH`, unary minus
- `captured-122b/final-source/Program.fs` — `LexBuffer<char>.FromString` wiring
- `captured-122b/final-source/calc.fsproj` — FixLineDirectives workaround
- `captured-122b/test-output.txt` — Fresh host build (0 errors) + 14/20/5
- `captured-122b/transcript.md` — Per-task human-readable summary
- `captured-122b/CAPTURE-MANIFEST.md` — All Phase-7 fields, JSONL-cited
- `.planning/STATE.md` — Updated position, progress, decisions

## Decisions Made

- **did-lexer-unaided=YES confirmed** from task2-lexer-unaided.jsonl event 9: agent used `rule tokenize = parse` (correct FsLex format), not `%%`. INT API bug (`int s` on char array) is a recoverable error, not a format failure.
- **8 fix iterations documented honestly**: agent tried `Lexing.matched`, `matched`, `matchedText`, `lexbuf.ToString()`, `lexbuf.Lexeme` (as int), before finding `new string(lexbuf.Lexeme)`. All in task5 events 12–74.
- **task6-fix not created**: task5 agent reached 14/20/5 internally; no external fix task needed.
- **JSONL event citations in manifest**: every claim (error text, fix command, test output) cites specific task file + event index so Phase 7 can audit without re-reading all logs.

## Deviations from Plan

None — plan executed exactly as written. The confirmed facts (did-lexer-unaided=YES, 8 fix iterations, 14/20/5) matched the context provided at plan invocation. No unexpected failures or blockers encountered.
