---
phase: 06-capture-the-122b-openhands-run
plan: 01
subsystem: capture
tags: [openhands, qwen-122b, fslexer, task-prompts, gitignore, preflight, litellm]

# Dependency graph
requires:
  - phase: 03-capture-the-openhands-run (v1)
    provides: v1 task-prompt text (task1/3/4/5/6) reused verbatim with workdir swap; v1 lexer scaffold (task2-lexer-scaffold.txt fallback)
provides:
  - task-prompts-122b/ directory with 8 prompt files + 00-INVOCATION.md
  - Fully unaided task2-lexer-unaided.txt (no lexer body, no API hints, no format hints)
  - Structural-only retry prompt task2-lexer-unaided-retry.txt
  - Verbatim v1 fallback task2-lexer-scaffold.txt (last resort)
  - oh-workdir-122b/ gitignored and clean
  - Confirmed litellm proxy serving qwen-122b at http://127.0.0.1:4000/v1
affects:
  - 06-02-PLAN (execute run — consumes all task-prompts-122b/ files)
  - 06-03-PLAN (post-run — depends on oh-workdir-122b/ being gitignored)
  - 07-comparison-chapter (consumes captured JSONL artifacts)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - unaided-first lexer protocol: task2 gives token names + rule name only, no source; fallback cascade (unaided -> retry -> scaffold) with disclosure
    - bash-only file-write constraint: all prompts forbid file_editor (security_risk field issue)
    - per-task JSONL capture: each task runs separately, output to oh-workdir-122b/<task>.jsonl

key-files:
  created:
    - .planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task2-lexer-unaided.txt
    - .planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task2-lexer-unaided-retry.txt
    - .planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task2-lexer-scaffold.txt
    - .planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task1-scaffold.txt
    - .planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task3-parser.txt
    - .planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task4-evaluator.txt
    - .planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task5-buildtest.txt
    - .planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task6-fix.txt
    - .planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/00-INVOCATION.md
  modified:
    - .gitignore

key-decisions:
  - "Fully unaided task2: omit even the API hint (LexBuffer<_>.LexemeString) and %% note that RESEARCH.md's recommended variant suggested — the key decision for this phase is maximum honesty, accepting that 122B may need more fix iterations in task5"
  - "task2-lexer-unaided-retry.txt adds structural floor only (rule/parse format line) — raises format awareness without handing over lexer code or API names"
  - "task1 FixLineDirectives .fsproj retained verbatim — toolchain workaround, not a model capability test; fair comparison with v1"
  - "task4-evaluator.txt used (not task4-evaluator-adjusted.txt) — original bash-only variant confirmed correct from v1 attempt 2"

patterns-established:
  - "unaided-first: task2 names only the 8-token contract (for parser agreement) and the tokenize rule entry point; zero source/format/API hints"
  - "fallback cascade: unaided -> structural-retry -> scaffold (v1 verbatim); each level disclosed in CAPTURE-MANIFEST if triggered"
  - "workdir isolation: oh-workdir-122b separate from oh-workdir (v1); both gitignored independently"

# Metrics
duration: 3min
completed: 2026-05-28
---

# Phase 6 Plan 01: Prepare 122B Task-Prompts (Unaided Lexer) Summary

**Fully unaided task2-lexer prompt (8-token contract only, zero hints) + v1 task1/3/4/5/6 reused with oh-workdir-122b swap, preflight confirmed: proxy live, scratch dir gitignored**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-05-28T03:25:24Z
- **Completed:** 2026-05-28T03:28:26Z
- **Tasks:** 3
- **Files modified:** 10 (9 created + .gitignore)

## Accomplishments

- Authored genuinely unaided task2-lexer-unaided.txt: names the 8 tokens + `tokenize` rule, zero lexer body/format/API hints (verified by grep — count is 0 for all forbidden patterns)
- Authored task2-lexer-unaided-retry.txt: adds one structural-floor line (`rule <name> = parse` format note) only; still zero API/body hints
- Created task2-lexer-scaffold.txt: verbatim v1 lexer with workdir swapped (fallback of last resort)
- Reused v1 task1/3/4/5/6 with `oh-workdir` -> `oh-workdir-122b` substitution; task1 FixLineDirectives .fsproj preserved verbatim
- Wrote 00-INVOCATION.md with exact qwen-122b invocation command, JSONL naming table, speed notes, and preflight checklist
- Added `oh-workdir-122b/` to .gitignore; v1 `oh-workdir/` untouched; scratch dir created and confirmed clean
- Confirmed litellm proxy at http://127.0.0.1:4000/v1 is live and lists qwen-122b

## Task Commits

Each task committed atomically:

1. **Task 1: Author unaided lexer prompts (task2 x3)** - `c2401b4` (feat)
2. **Task 2: Reuse v1 task1/3/4/5/6 + write 00-INVOCATION.md** - `8cbc540` (feat)
3. **Task 3: Preflight — gitignore, scratch dir, proxy confirm** - `2ed1662` (chore)

**Plan metadata:** (docs commit below)

## Files Created/Modified

- `.planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task2-lexer-unaided.txt` - Core unaided prompt: 8 token names + tokenize rule name, zero hints
- `.planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task2-lexer-unaided-retry.txt` - Structural floor retry: adds rule/parse format line only
- `.planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task2-lexer-scaffold.txt` - Verbatim v1 fallback lexer (oh-workdir-122b workdir)
- `.planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task1-scaffold.txt` - v1 task1 with workdir swapped; FixLineDirectives .fsproj retained
- `.planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task3-parser.txt` - v1 task3 with workdir swapped
- `.planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task4-evaluator.txt` - v1 task4 (bash-only variant) with workdir swapped
- `.planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task5-buildtest.txt` - v1 task5 with workdir swapped
- `.planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/task6-fix.txt` - v1 task6 (conditional fix) with workdir swapped
- `.planning/phases/06-capture-the-122b-openhands-run/task-prompts-122b/00-INVOCATION.md` - qwen-122b invocation reference + JSONL naming + speed notes
- `.gitignore` - Added oh-workdir-122b/ entry

## Decisions Made

- **Fully unaided task2 (hardest variant):** Chose to omit even the API hint (`LexBuffer<_>.LexemeString`) and `%%` note that 06-RESEARCH.md's "Recommended" variant suggested. The milestone's point is maximum honesty — the API bugs observed in the live probe are exactly the kind of genuine error-and-fix that task5 is designed to handle. This makes the unaided run harder but more revealing.
- **Structural-only retry:** task2-lexer-unaided-retry.txt adds only one line about FsLex format structure (to prevent the same `%%`-confusion that defeated 35B), with zero API hints or code bodies. This is the minimum floor that separates "format confusion" from "API capability."
- **task4-evaluator.txt (not task4-evaluator-adjusted.txt):** Used the original bash-only variant confirmed to work in v1 attempt 2.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. All three tasks executed cleanly:
- Proxy was live and serving qwen-122b on first check (no retry needed)
- oh-workdir-122b/ was not yet present (created fresh, confirmed empty)
- .gitignore did not already have oh-workdir-122b/ (appended once)

## User Setup Required

None - no external service configuration required. Proxy was already live.

## Next Phase Readiness

Ready for 06-02 (execute the actual 122B OpenHands run). All preconditions met:
- task-prompts-122b/ has all 9 files (8 .txt + 00-INVOCATION.md)
- oh-workdir-122b/ is empty, gitignored, and ready to receive the calc/ project and JSONL logs
- Proxy confirmed serving qwen-122b
- No blockers or concerns

---
*Phase: 06-capture-the-122b-openhands-run*
*Completed: 2026-05-28*
