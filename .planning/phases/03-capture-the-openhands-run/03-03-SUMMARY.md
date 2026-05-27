---
phase: 03-capture-the-openhands-run
plan: 03
subsystem: documentation
tags: [openhands, jsonl, fsharp, fsyacc, fslexer, dotnet, capture, artifacts]

# Dependency graph
requires:
  - phase: 03-capture-the-openhands-run
    provides: 5 keeper JSONL logs (task1-task5) in oh-workdir/, calculator verified 14/20/5

provides:
  - committed captured/ directory with 5 JSONL logs, transcript.md, final-source/ (4 files), test-output.txt, CAPTURE-MANIFEST.md
  - programmatic verification of RUN-01/02/03 + 2+3*4=14 from real evidence
  - error-and-fix cycle pointer: task3-parser.jsonl events 10–30 (for Phase 4 narration)

affects: [04-write-worked-example-chapter, WALK-03]

# Tech tracking
tech-stack:
  added: []
  patterns: ["JSONL filtering: l.strip().startswith('{') skips non-JSON OpenHands banner lines", "Nested event structure: ActionEvent.action.kind=='TerminalAction', ObservationEvent.observation.kind=='TerminalObservation'"]

key-files:
  created:
    - .planning/phases/03-capture-the-openhands-run/captured/logs/task1-scaffold.jsonl
    - .planning/phases/03-capture-the-openhands-run/captured/logs/task2-lexer.jsonl
    - .planning/phases/03-capture-the-openhands-run/captured/logs/task3-parser.jsonl
    - .planning/phases/03-capture-the-openhands-run/captured/logs/task4-evaluator.jsonl
    - .planning/phases/03-capture-the-openhands-run/captured/logs/task5-buildtest.jsonl
    - .planning/phases/03-capture-the-openhands-run/captured/transcript.md
    - .planning/phases/03-capture-the-openhands-run/captured/final-source/calc.fsproj
    - .planning/phases/03-capture-the-openhands-run/captured/final-source/Lexer.fsl
    - .planning/phases/03-capture-the-openhands-run/captured/final-source/Parser.fsy
    - .planning/phases/03-capture-the-openhands-run/captured/final-source/Program.fs
    - .planning/phases/03-capture-the-openhands-run/captured/test-output.txt
    - .planning/phases/03-capture-the-openhands-run/captured/CAPTURE-MANIFEST.md
  modified: []

key-decisions:
  - "JSONL event structure is nested dicts: action.kind=='TerminalAction', observation.kind=='TerminalObservation', observation.content[0].text for output — not flat key-value pairs"
  - "Error-and-fix cycle confirmed in task3-parser.jsonl events 10-30 (4 build failures: FSY000 missing %start, parse error on %start <int> start syntax, same, FS0039 LexBuffer.FromText non-existent)"
  - "Lexer.fsl and .fsproj were scaffolded via task prompts — documented honestly in manifest and transcript; agent's real work was parser+evaluator+self-correction"
  - "oh-workdir/ confirmed gitignored; captured/ is the sole committed location for all run artifacts"

patterns-established:
  - "OpenHands JSONL event parsing: filter startswith('{'), then navigate ev['action']['kind'] and ev['observation']['kind'] for nested structure"
  - "Error-and-fix evidence: ObservationEvent with observation.exit_code != 0 on dotnet build followed by exit_code == 0 on later dotnet build"

# Metrics
duration: ~20min
completed: 2026-05-28
---

# Phase 3 Plan 03: Verify & Commit Captured Run Artifacts Summary

**Programmatic verification of 5 JSONL logs confirmed RUN-01/02/03 + 2+3*4=14; captured/ committed with logs, transcript, final-source snapshot, test-output, and manifest tying each artifact to Phase 3 criteria.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-05-28T07:25:00Z (approx)
- **Completed:** 2026-05-28T07:45:00Z (approx)
- **Tasks:** 2
- **Files created:** 12 (11 in captured/, 1 summary)

## Accomplishments

- Programmatic JSONL scan confirmed 5 keeper logs with 27/2/15/14/9 TerminalActions each (RUN-02); error-and-fix cycle confirmed in task3-parser.jsonl events 10–30 with 4 build failures and autonomous self-correction (RUN-03)
- Fresh host run produced captured/test-output.txt confirming Build succeeded, 2+3*4=14, (2+3)*4=20, 10-3-2=5 (2+3*4=14 criterion)
- All captured artifacts (logs, transcript, final-source, test output, manifest) committed to tracked captured/ directory; oh-workdir/ confirmed gitignored and not committed

## Task Commits

1. **Task 1: Programmatic verification** - `4224848` (feat)
2. **Task 2: Assemble captured artifacts** - `862c283` (docs)

## Files Created/Modified

- `captured/logs/task1-scaffold.jsonl` — Raw JSONL: scaffold task (56 events, 27 TerminalActions)
- `captured/logs/task2-lexer.jsonl` — Raw JSONL: lexer task (6 events, 2 TerminalActions)
- `captured/logs/task3-parser.jsonl` — Raw JSONL: parser task (34 events, 15 TerminalActions); primary error-and-fix evidence
- `captured/logs/task4-evaluator.jsonl` — Raw JSONL: evaluator task (30 events, 14 TerminalActions)
- `captured/logs/task5-buildtest.jsonl` — Raw JSONL: build+test task (20 events, 9 TerminalActions)
- `captured/transcript.md` — Per-task command/output transcript; marks error-and-fix in Task 3
- `captured/final-source/calc.fsproj` — Verbatim final project file with FixLineDirectives workaround
- `captured/final-source/Lexer.fsl` — Verbatim Lexer.fsl (provided via prompt; agent did not author)
- `captured/final-source/Parser.fsy` — Verbatim Parser.fsy (%left PLUS MINUS / %left STAR SLASH; %start/%type on separate lines)
- `captured/final-source/Program.fs` — Verbatim Program.fs (LexBuffer<char>.FromString — corrected by agent)
- `captured/test-output.txt` — Fresh host dotnet build + 3-case run; confirms 14/20/5
- `captured/CAPTURE-MANIFEST.md` — Maps RUN-01/02/03 + 2+3*4=14 to artifacts; error-and-fix pointer for Phase 4

## Decisions Made

- JSONL event structure is nested dicts, not flat: `ev['action']['kind'] == 'TerminalAction'` and `ev['observation']['kind'] == 'TerminalObservation'` (the plan's parser note assumed flat structure; adapted to real nested format)
- Documented Lexer.fsl and .fsproj as scaffolded via prompts throughout manifest and transcript — honest record for Phase 4 narration
- Error-and-fix pointer in manifest gives Phase 4 the exact file + event range: task3-parser.jsonl events 10–30

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] JSONL parser adapted to nested event structure**

- **Found during:** Task 1 (programmatic JSONL verification)
- **Issue:** Plan described `action == "run"` (flat), `observation == "run"` (flat), and `extras.exit_code`. Actual structure uses nested dicts: `ev['action']['kind'] == 'TerminalAction'`, `ev['observation']['kind'] == 'TerminalObservation'`, `ev['observation']['exit_code']`, `ev['observation']['content'][0]['text']`.
- **Fix:** Adapted all parser functions to navigate nested dict structure; confirmed 27/2/15/14/9 TerminalActions (matching RUN-NOTES.md)
- **Files modified:** (Python script only — no committed file changed)
- **Verification:** TerminalAction counts matched 03-02-RUN-NOTES.md exactly; error-and-fix events found at correct indices
- **Committed in:** 4224848 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — bug fix in parser logic)
**Impact on plan:** Necessary to correctly parse the real JSONL structure. No scope creep.

## Issues Encountered

- Initial JSONL parsing reported 0 TerminalActions because plan assumed flat `action == "run"` key. Real structure has nested `action` dict with `kind` field. Corrected by inspecting first event structure; all counts then matched RUN-NOTES.md exactly.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

**Phase 4 is ready to start.** The captured/ directory provides:

- **Error-and-fix narration source:** task3-parser.jsonl events 10–30 (4 build failures → autonomous self-correction)
- **Source-of-truth code:** final-source/ (4 verbatim files, no edits)
- **Correctness proof:** test-output.txt (14/20/5 from fresh host run)
- **Navigation:** CAPTURE-MANIFEST.md maps every artifact to the Phase 3 criterion it evidences

**Honest framing for Phase 4:** The lexer (.fsl) and project file (.fsproj) were provided via prompts — the agent's real autonomous work was Parser.fsy grammar writing, Program.fs CLI wiring, and 4-iteration self-correction of build errors.

---
*Phase: 03-capture-the-openhands-run*
*Completed: 2026-05-28*
