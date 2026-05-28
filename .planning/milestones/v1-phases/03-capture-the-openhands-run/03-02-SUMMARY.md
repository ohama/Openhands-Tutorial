---
phase: 03-capture-the-openhands-run
plan: 02
subsystem: openhands-run-capture
tags: [openhands, fsharp, fslexyacc, calculator, jsonl, error-and-fix, qwen-local, litellm]

dependency-graph:
  requires:
    - 03-01 (task prompt strings — all 6 prompts produced)
    - 02-02 (headless invocation verified; dotnet in agent PTY confirmed)
  provides:
    - 5 per-task JSONL logs in oh-workdir/ (task1-scaffold through task5-buildtest)
    - Built calculator in oh-workdir/calc evaluating 2+3*4=14, (2+3)*4=20, 10-3-2=5
    - Genuine error-and-fix cycle in task3-parser.jsonl (4 build failures + self-correction)
    - 03-02-RUN-NOTES.md (per-task outcomes, error-and-fix location, branch taken)
  affects:
    - 03-03 (curate JSONL logs — selects representative events from these 5 JSONL files)
    - 04-xx (walkthrough chapter — written from this captured evidence)

tech-stack:
  added: []
  patterns:
    - openhands headless JSONL capture (run_in_background + poll until FinalMsg)
    - per-task shared-workdir decomposition (5 invocations, 1 workdir, files persist)
    - Branch A error-and-fix (genuine build failures within task3-parser.jsonl)

file-tracking:
  created:
    - .planning/phases/03-capture-the-openhands-run/03-02-RUN-NOTES.md
    - .planning/phases/03-capture-the-openhands-run/03-02-SUMMARY.md
    - oh-workdir/task1-scaffold.jsonl (gitignored)
    - oh-workdir/task2-lexer.jsonl (gitignored)
    - oh-workdir/task3-parser.jsonl (gitignored)
    - oh-workdir/task4-evaluator.jsonl (gitignored)
    - oh-workdir/task5-buildtest.jsonl (gitignored)
    - oh-workdir/calc/calc.fsproj (gitignored)
    - oh-workdir/calc/Lexer.fsl (gitignored)
    - oh-workdir/calc/Parser.fsy (gitignored)
    - oh-workdir/calc/Program.fs (gitignored)
  modified:
    - .planning/STATE.md

decisions:
  - id: attempt2-lexer-scaffold
    choice: Lexer.fsl content provided verbatim in task2-lexer.txt
    rationale: Attempt 1 failed because 35B model could not write valid FsLex syntax; providing it eliminates the out-of-distribution blocker while keeping the real parser/evaluator work
    alternatives: retry with adjusted prompt; try smaller steps
  - id: branch-a-taken
    choice: error-and-fix cycle captured in task3-parser.jsonl (not task5-buildtest)
    rationale: Agent hit 4 genuine build failures while writing Parser.fsy (%start syntax errors + LexBuffer.FromText API error) and self-corrected; this is more instructive than the planned precedence bug
    alternatives: Branch C re-roll for precedence bug
  - id: no-task6-needed
    choice: task6-fix.txt not invoked
    rationale: Branch A (error-and-fix in task3) satisfied RUN-03; task5 verified all 3 cases clean
    alternatives: run task6 to produce precedence bug scenario

metrics:
  duration: ~16 minutes total (07:08 to 07:18 UTC, 5 invocations)
  completed: 2026-05-28
---

# Phase 3 Plan 2: OpenHands Calculator Run (Attempt 2) Summary

**One-liner:** 5-task OpenHands run capturing a 4-failure FsYacc self-correction cycle; calculator evaluates 2+3*4=14, (2+3)*4=20, 10-3-2=5 on the host.

---

## What Was Built

The real OpenHands agent (Qwen2.5-35B via litellm proxy) was run 5 times in sequence against a shared working directory (`oh-workdir/calc`), each time given one focused task prompt. The agent built an F# FsLexYacc integer arithmetic calculator from scratch:

1. **task1-scaffold** (3m 6s, 56 events, 27 TerminalActions): `dotnet new console -lang F#`, replaced calc.fsproj with the provided FsLexYacc-wired content including the FixLineDirectives target, created Parser.fsy placeholder.
2. **task2-lexer** (16s, 6 events, 2 TerminalActions): Created Lexer.fsl with exact provided content via `cat > Lexer.fsl <<'EOF'` heredoc.
3. **task3-parser** (1m 17s, 34 events, 15 TerminalActions): Wrote Parser.fsy grammar — hit 4 genuine build failures, self-corrected on all four, ended with working grammar and all test cases passing.
4. **task4-evaluator** (45s, 30 events, 14 TerminalActions): Wrote Program.fs CLI entry point with `FSharp.Text.Lexing`, `LexBuffer<char>.FromString`, `Parser.start Lexer.tokenize lexbuf`.
5. **task5-buildtest** (32s, 20 events, 9 TerminalActions): Built the project and ran all 3 required cases — `2+3*4=14`, `(2+3)*4=20`, `10-3-2=5` — all PASS on first attempt.

---

## The Genuine Error-and-Fix Cycle (RUN-03)

**Location:** `oh-workdir/task3-parser.jsonl`, events 9–30
**Branch:** A (error-and-fix within the main run, not in a separate fix task)

The agent hit four successive build failures during Task 3 and self-diagnosed each one:

| Attempt | Event | Error | Agent Diagnosis |
|---------|-------|-------|-----------------|
| 1 | Event 10 | `FSY000: at least one %start declaration is required` | Added `%start` declaration |
| 2 | Event 16 | `Parser.fsy(16,7): error parse error` | `%start <int> start` is invalid FsYacc syntax |
| 3 | Event 20 | Same `parse error` | Continued diagnosis |
| 4 | Event 26 | `FS0039: LexBuffer<_> does not define 'FromText'` | API is `FromString`, not `FromText` |
| 5 | Event 30 | BUILD SUCCESS | Fixed: separated `%start start` + `%type <int> start`; used `LexBuffer<char>.FromString` |

This is a genuine, JSONL-locatable error-and-fix cycle. The errors are ordinary in-distribution F# and FsYacc mistakes; the agent diagnosed and corrected each without any external help.

---

## Host Verification

Executed directly on the host after all 5 tasks completed:

```
$ dotnet run --project oh-workdir/calc -- "2+3*4"
14

$ dotnet run --project oh-workdir/calc -- "(2+3)*4"
20

$ dotnet run --project oh-workdir/calc -- "10-3-2"
5
```

All three required outputs confirmed.

---

## Decisions Made

1. **Lexer provided verbatim (key change vs. attempt 1):** Attempt 1 failed because FsLex syntax is out-of-distribution for the 35B model — it confused FsLex with FsYacc (added `%%` separators, used `lexeme` instead of `LexBuffer<_>.LexemeString`). Providing the lexer content in task2-lexer.txt eliminated this blocker while keeping the real parser and evaluator work genuine.

2. **Branch A taken (error-and-fix in task3, not task5):** The planned scenario was a precedence bug in task5. Instead, the agent hit genuine FsYacc `%start` syntax errors and a wrong API call (`FromText`) during Task 3. These are more numerous and more interesting than the planned precedence scenario — 4 distinct build errors vs. 1 wrong arithmetic result. Branch A is cleaner: error-and-fix is self-contained in one JSONL.

3. **Task 6 not invoked:** Since task3 contained the error-and-fix cycle and task5 passed all three cases cleanly, there was no need to invoke task6-fix.txt.

---

## Deviations from Plan

### Auto-fixed Issues

None — the plan executed as designed.

### Deviations

**1. [Scope] Task 3 also wrote Program.fs**

- **Found during:** Task 3 execution
- **Issue:** The parser task's prompt only asked for Parser.fsy, but the agent also wrote a Program.fs to test its grammar (to run `dotnet build` and validate). This caused the `LexBuffer.FromText` error — the agent had to fix Program.fs too.
- **Impact:** Task 4 (evaluator) still ran, but by the time it ran, Program.fs was already correct. Task 4 overwrote it with the same correct implementation.
- **Assessment:** Genuine agent behavior, not a problem. The JSONL capture is honest.

**2. [Actual vs. planned error-and-fix] FsYacc syntax errors instead of precedence bug**

- **Planned:** The naive parser would omit `%left` declarations, causing `10-3-2=9` (wrong right-associativity), caught in task5.
- **Actual:** Task 3's agent wrote `%left PLUS MINUS` and `%left STAR SLASH` correctly from the start, so no precedence bug surfaced. Instead, the genuine errors were FsYacc `%start` syntax and a wrong API call.
- **Assessment:** More instructive for the tutorial — 4 distinct compiler errors + self-correction is a richer capture than 1 arithmetic wrong-answer scenario.

---

## JSONL Keeper Inventory

| File | Events | TerminalActions | Role |
|------|--------|-----------------|------|
| `task1-scaffold.jsonl` | 56 | 27 | Scaffold creation |
| `task2-lexer.jsonl` | 6 | 2 | Verbatim lexer write |
| `task3-parser.jsonl` | 34 | 15 | **Primary: error-and-fix cycle** |
| `task4-evaluator.jsonl` | 30 | 14 | CLI entry point |
| `task5-buildtest.jsonl` | 20 | 9 | Final build+test verification |

Total: 146 events, 67 TerminalActions across 5 invocations.

---

## Next Phase Readiness

- **03-03** (curate JSONL logs): Ready. The 5 keeper logs are in `oh-workdir/`. Task 3 is the primary log to curate — it contains the error-and-fix events. Plan 03-03 should strip large payloads and select representative events for Phase 4 reference.
- **04-xx** (walkthrough chapter): Ready after 03-03. The captured evidence is complete: genuine errors, self-correction, and final verification. RUN-01 (≥5 invocations), RUN-02 (shared workdir), and RUN-03 (genuine error-and-fix) are all satisfied.

### Potential Phase 4 Concerns

- The actual error-and-fix is FsYacc `%start` syntax + wrong API call — not the "precedence bug" originally conceived for the tutorial narrative. Phase 4 will need to write the walkthrough chapter around the actual captured errors. This is fine — the actual errors are arguably more interesting and more typical of real agentic debugging.
