---
phase: 03-capture-the-openhands-run
plan: "01"
subsystem: capture
tags: [openhands, fsharp, fslexyacc, prompt-engineering, calculator, task-decomposition]

# Dependency graph
requires:
  - phase: 02-environment-setup-and-verification
    provides: verified headless OpenHands invocation (--override-with-envs, --yolo, --json, LocalWorkspace), confirmed dotnet 10.0.203 works in agent PTY, LiteLLM proxy on 127.0.0.1:4000
provides:
  - Six plain-text prompt files that drive the OpenHands calculator build run (task1-scaffold through task6-fix)
  - Invocation reference (00-INVOCATION.md) with exact env-var command and per-task JSONL log names
  - Known-good calc.fsproj embedded verbatim in scaffold prompt (FixLineDirectives workaround pre-wired)
  - Three required test cases encoded in task5-buildtest (incl. 10-3-2=5 to detect associativity bug)
  - Conditional fix prompt (task6) with run-time placeholder following research B6 pattern
affects: [03-02-PLAN, 04-walk-through-chapter]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Self-contained per-invocation prompt: state workdir + describe existing files + goal + constraints"
    - "Goal+constraints style: tell agent WHAT (goal) and hard constraints; not HOW (implementation)"
    - "Verbatim scaffold artifact: embed environment-specific .fsproj to bypass obscure toolchain quirk"
    - "Placeholder for run-time captured value: <ACTUAL_WRONG_OUTPUT> in fix prompt (B6)"

key-files:
  created:
    - .planning/phases/03-capture-the-openhands-run/task-prompts/00-INVOCATION.md
    - .planning/phases/03-capture-the-openhands-run/task-prompts/task1-scaffold.txt
    - .planning/phases/03-capture-the-openhands-run/task-prompts/task2-lexer.txt
    - .planning/phases/03-capture-the-openhands-run/task-prompts/task3-parser.txt
    - .planning/phases/03-capture-the-openhands-run/task-prompts/task4-evaluator.txt
    - .planning/phases/03-capture-the-openhands-run/task-prompts/task5-buildtest.txt
    - .planning/phases/03-capture-the-openhands-run/task-prompts/task6-fix.txt
  modified: []

key-decisions:
  - "Verbatim .fsproj in scaffold prompt: bypasses FsLexYacc 11.3.0 + .NET 10 line-directive incompatibility without blocking the run on a non-instructive debug session"
  - "10-3-2=5 as required third test case: the only case that exposes the naive-grammar right-associativity bug (2+3*4 and (2+3)*4 both pass even without %left)"
  - "Never mention %left/%right in any prompt: lets the associativity bug emerge honestly for a genuine error-and-fix cycle"
  - "task6 uses <ACTUAL_WRONG_OUTPUT> placeholder: executor (03-02) substitutes the real captured wrong value before invoking"
  - "Behavioral outcome only in task3 (left-to-right): state the REQUIRED RESULT, not the FsYacc declaration mechanism"

patterns-established:
  - "Fresh-conversation self-containment: every prompt opens with workdir + file inventory + cd+inspect instruction"
  - "Goal+constraints separation: goal says what to achieve; constraints say hard boundaries; agent decides how"

# Metrics
duration: 12min
completed: 2026-05-27
---

# Phase 03 Plan 01: Write OpenHands Run Prompt Strings — Summary

**Six self-contained goal+constraints prompt files for the OpenHands calculator build run, with verbatim known-good .fsproj (FixLineDirectives for .NET 10 + FsLexYacc 11.3.0) and 10-3-2=5 as the third test case to detect the associativity bug without revealing %left.**

## Performance

- **Duration:** ~12 min
- **Started:** 2026-05-27T08:49:37Z
- **Completed:** 2026-05-27T09:01:00Z
- **Tasks:** 2 of 2
- **Files modified:** 7 created

## Accomplishments

- Created 7 plain-text artifacts in task-prompts/: invocation reference + 6 prompt strings for the full OpenHands calculator build sequence
- Embedded the verbatim known-good calc.fsproj (FixLineDirectives MSBuild target, --module Parser/Lexer OtherFlags, Parser.fsi→Parser.fs→Lexer.fs→Program.fs compile order, FsLexYacc 11.3.0) in task1-scaffold.txt — bypasses the FsLexYacc 11.3.0 + .NET 10 line-directive incompatibility pre-emptively
- Encoded the critical third test case (10-3-2=5) in task5-buildtest.txt — the only case that exposes the naive-grammar right-associativity bug; task6-fix.txt follows the B6 pattern with an ACTUAL_WRONG_OUTPUT placeholder for executor substitution
- Zero %left/%right mentions across all 6 prompts — verified by grep

## Task Commits

1. **Task 1+2: Write all 7 task-prompt files** - `711a184` (docs)

**Plan metadata:** (combined with task commit above — single atomic commit)

## Files Created/Modified

- `.planning/phases/03-capture-the-openhands-run/task-prompts/00-INVOCATION.md` - Exact env-var invocation + per-task JSONL log filenames (task1-scaffold.jsonl through task6-fix.jsonl)
- `.planning/phases/03-capture-the-openhands-run/task-prompts/task1-scaffold.txt` - Scaffold prompt: create calc/ dir, replace calc.fsproj with verbatim known-good content, touch placeholder Lexer.fsl + Parser.fsy
- `.planning/phases/03-capture-the-openhands-run/task-prompts/task2-lexer.txt` - Lexer prompt: write Lexer.fsl tokenizing integers + operators, open Parser header, fixed token names (INT, PLUS, MINUS, STAR, SLASH, LPAREN, RPAREN, EOF)
- `.planning/phases/03-capture-the-openhands-run/task-prompts/task3-parser.txt` - Parser prompt: write Parser.fsy with * / higher precedence than + -, left-to-right associativity as required behavioral outcome (no %left hint)
- `.planning/phases/03-capture-the-openhands-run/task-prompts/task4-evaluator.txt` - Evaluator prompt: rewrite Program.fs with FSharp.Text.Lexing (not old Microsoft namespace), LexBuffer<char>.FromString, dotnet run -- "expr" pattern
- `.planning/phases/03-capture-the-openhands-run/task-prompts/task5-buildtest.txt` - Build+test prompt: dotnet build + all three cases (2+3*4=14, (2+3)*4=20, 10-3-2=5), report all results explicitly
- `.planning/phases/03-capture-the-openhands-run/task-prompts/task6-fix.txt` - Conditional fix prompt: ACTUAL_WRONG_OUTPUT placeholder, fix in Parser.fsy only, do not rewrite from scratch

## Decisions Made

- **Verbatim .fsproj provided in scaffold:** The FsLexYacc 11.3.0 + .NET 10 line-directive bug (`# 0 ""` rejected by F# 10 compiler with FS0010) is an obscure environment quirk a 35B model is unlikely to self-fix. Providing the FixLineDirectives target pre-wired avoids a non-instructive stall. Build wiring is implementation detail, not the instructive part of the run.
- **Three test cases locked:** Research A5 proves 2+3*4 and (2+3)*4 both pass even with the naive no-%left grammar. Only 10-3-2=5 exposes the right-associativity failure. Without it, the bug is invisible and RUN-03 (genuine error-and-fix cycle) cannot be satisfied honestly.
- **Behavioral outcome only in task3:** task3-parser.txt states "operators of equal precedence must associate left-to-right" as a required behavioral outcome without naming %left. This lets the naive grammar (no declarations) surface its bug honestly during build+test.
- **ACTUAL_WRONG_OUTPUT placeholder in task6:** The fix prompt cannot hard-code the wrong value (it depends on which bug the model hits). Plan 03-02 executor will substitute the captured actual value from task5-buildtest.jsonl before invoking the fix task.

## Deviations from Plan

None — plan executed exactly as written. All design constraints honored:
- No %left/%right in any prompt (verified by grep)
- Verbatim .fsproj from research A2 embedded in task1-scaffold.txt
- All three test cases in task5-buildtest.txt
- task6-fix.txt follows B6 pattern with ACTUAL_WRONG_OUTPUT placeholder
- All 7 prompts self-contained with workdir + file inventory

## Issues Encountered

None.

## Next Phase Readiness

Plan 03-02 (execute the OpenHands run) can proceed immediately:
- All prompt strings are committed and ready to feed to `openhands --headless -t "$(cat ...)"`.
- 00-INVOCATION.md has the exact invocation command with all env vars.
- task6-fix.txt requires one substitution before use: replace `<ACTUAL_WRONG_OUTPUT>` with the real wrong output captured from task5-buildtest.jsonl.
- The oh-workdir/ scratch directory exists and is gitignored — agent can write freely there.

---
*Phase: 03-capture-the-openhands-run*
*Completed: 2026-05-27*
