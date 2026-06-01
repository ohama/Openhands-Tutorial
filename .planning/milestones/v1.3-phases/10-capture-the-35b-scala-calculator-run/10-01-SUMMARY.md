---
phase: 10-capture-the-35b-scala-calculator-run
plan: "01"
subsystem: infra
tags: [scala-cli, scala3, task-prompts, preflight, gitignore, litellm, qwen-35b]

requires: []

provides:
  - "4 task prompts (task1-scaffold, task2-write-calc, task2-calc-scaffold, task3-buildtest) in task-prompts-scala/"
  - "00-INVOCATION.md with qwen-35b headless command pattern + JSONL filename table + scaffold-fallback policy"
  - "10-01-PREFLIGHT.md with PREFLIGHT GREEN verdict (scala-cli 1.14.0, JDK 17, cache warm, proxy live)"
  - "oh-workdir-scala/ scratch dir (empty, gitignored)"
  - ".gitignore updated with oh-workdir-scala/ entry"

affects:
  - "10-02 (capture run depends on prompts + green preflight)"
  - "10-03 (capture gate uses CAPTURE-MANIFEST written during 10-02)"

tech-stack:
  added:
    - "scala-cli 1.14.0 (Scala 3.8.3 default; pre-installed; artifact cache pre-warmed)"
    - "Java 17.0.19 (openjdk@17 Homebrew; already present)"
  patterns:
    - "Zero-leak prompt discipline: task2 describes behavior only (no sealed trait / recursive descent / expr/term/factor / tokenizer / @main / 10-3-2)"
    - "Cache pre-warm in preflight: trivial scala-cli run done by operator before agent tasks"
    - "Scaffold-fallback as staged fallback: task2-calc-scaffold.txt staged but only invoked if agent cycles on identical compile errors 3+ times"

key-files:
  created:
    - ".planning/phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/task1-scaffold.txt"
    - ".planning/phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/task2-write-calc.txt"
    - ".planning/phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/task2-calc-scaffold.txt"
    - ".planning/phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/task3-buildtest.txt"
    - ".planning/phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/00-INVOCATION.md"
    - ".planning/phases/10-capture-the-35b-scala-calculator-run/10-01-PREFLIGHT.md"
  modified:
    - ".gitignore (added oh-workdir-scala/)"

key-decisions:
  - "scala-cli was pre-installed (1.14.0); brew install step detected as no-op and skipped cleanly"
  - "task2-write-calc.txt uses 'arithmetic expression' on single line (avoid grep false-negative from line-wrap)"
  - "task2-calc-scaffold.txt embeds verbatim Calc.scala from research §3 using outer SCAFFOLD_EOF / inner SCALA_EOF delimiters"
  - "Cache pre-warm triggered first-run artifact download successfully (PREFLIGHT_OK printed, exit 0)"

patterns-established:
  - "Prompt zero-leak discipline: banned words enumerated in plan; verified by 6 grep-c calls all returning 0"
  - "10-3-2 test withheld from task2; only revealed in task3 (left-associativity probe)"

duration: 7min
completed: 2026-06-01
---

# Phase 10 Plan 01: Preflight + Zero-Leak Task-Prompt Authoring — Summary

**Zero-leak unaided prompt (task2-write-calc.txt) + 4 task files authored; scala-cli 1.14.0 artifact cache pre-warmed; PREFLIGHT GREEN with all 5 checks passing**

## Performance

- **Duration:** ~7 min
- **Started:** 2026-06-01T05:28:29Z
- **Completed:** 2026-06-01T05:35:27Z
- **Tasks:** 3
- **Files modified:** 7 (4 prompts + INVOCATION.md + PREFLIGHT.md + .gitignore)

## Accomplishments

- Authored 4 task prompts + 00-INVOCATION.md under `task-prompts-scala/`. task2-write-calc.txt passes all 6 zero-leak grep checks (all returning 0) and all goal/behavior checks (arithmetic expression, std-only, oh-workdir-scala, 2+3*4 each returning >=1).
- task2-calc-scaffold.txt embeds the verbatim Calc.scala from research §3 (`sealed trait Expr` ADT + char tokenizer + recursive-descent parser + `@main def calc`) for use as fallback only if the agent demonstrably cycles on identical compile errors.
- Preflight GREEN: scala-cli 1.14.0 present, JDK 17.0.19 confirmed, trivial `scala-cli run` printed PREFLIGHT_OK (exit 0) with full artifact download completed (Bloop + Zinc + Scala 3.8.3), cache warm. litellm proxy confirmed serving qwen-35b. oh-workdir-scala/ empty and gitignored.

## Task Commits

1. **Task 1: Author 4 task prompts** - `a63dd00` (feat)
2. **Task 2: Write 00-INVOCATION.md** - `1444bc9` (docs)
3. **Task 3: Preflight + gitignore + PREFLIGHT.md** - `f86aa01` (feat)

## Files Created/Modified

- `.planning/phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/task1-scaffold.txt` — agent verifies scala-cli + runs trivial Hello.scala (SCALA_OK); first-run download warning
- `.planning/phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/task2-write-calc.txt` — zero-leak unaided prompt: behavior-only (arithmetic expression, precedence, parentheses, std-only); no technique hints; no 10-3-2
- `.planning/phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/task2-calc-scaffold.txt` — fallback only: verbatim Calc.scala (sealed trait Expr + recursive-descent + @main def calc)
- `.planning/phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/task3-buildtest.txt` — reveals all 3 canonical tests incl. 10-3-2; bans parser libs; honesty mandate
- `.planning/phases/10-capture-the-35b-scala-calculator-run/task-prompts-scala/00-INVOCATION.md` — openai/qwen-35b command pattern; JSONL filename table; forbids 14-32s/call as measurement; scaffold-fallback policy
- `.planning/phases/10-capture-the-35b-scala-calculator-run/10-01-PREFLIGHT.md` — PREFLIGHT GREEN with all evidence (scala-cli version, JDK, cache pre-warm output, proxy response, gitignore)
- `.gitignore` — added `oh-workdir-scala/` (5th entry alongside book/, oh-workdir/, oh-workdir-122b/, oh-workdir-rust/)

## Decisions Made

- **scala-cli pre-installed**: The plan assumed scala-cli was absent and would need `brew install`. It was already at 1.14.0. Detected as no-op; skipped cleanly. The artifact cache had NOT been pre-warmed (scala-cli was installed but never run), so the trivial `scala-cli run` in Step 3 still triggered the full first-run download — this was CORRECT and necessary.
- **task2 wording adjusted**: "arithmetic expression" had to be on a single line to pass the `grep -c -iE "arithmetic expression"` verify check. Initial draft wrapped to two lines; fixed by restructuring the sentence.
- **Scaffold heredoc delimiters**: task2-calc-scaffold.txt uses outer `SCAFFOLD_EOF` and inner `SCALA_EOF` to avoid delimiter collision when the agent runs the inner heredoc in its bash session.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] "arithmetic expression" split across two lines in initial task2 draft**

- **Found during:** Task 1 (verify step — `grep -c -iE "arithmetic expression"` returned 0)
- **Issue:** The sentence "...that, when given an arithmetic / expression string..." wrapped across two lines; `grep` matches within single lines only, so the check returned 0 instead of >=1.
- **Fix:** Restructured the sentence to place "arithmetic expression" on a single line: "...that evaluates an arithmetic expression — given as a command-line argument..."
- **Files modified:** task-prompts-scala/task2-write-calc.txt
- **Verification:** `grep -c -iE "arithmetic expression"` returned 1 after fix.
- **Committed in:** a63dd00 (Task 1 commit — fix applied before commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — Bug/wording in prompt)
**Impact on plan:** Trivial fix; no scope change. Prompt behavior unchanged, only phrasing restructured.

## Issues Encountered

- First-run scala-cli artifact download triggered verbose output (246KB) during preflight. This is expected behavior (Pitfall 2 from research §5). The "Failed to download" lines for snapshot repositories are normal — coursier tries snapshot mirrors first, falls back to nightlies/central. All required artifacts downloaded successfully.

## Next Phase Readiness

- All prompts authored and verified (zero-leak greps all pass).
- scala-cli artifact cache is warm — agent's task1 should be fast (no first-run download).
- litellm proxy confirmed live and serving qwen-35b.
- oh-workdir-scala/ is empty and gitignored — clean launchpad.
- **10-02 can launch immediately.** No blockers.

---
*Phase: 10-capture-the-35b-scala-calculator-run*
*Completed: 2026-06-01*
