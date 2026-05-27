---
phase: 03-capture-the-openhands-run
verified: 2026-05-28T00:00:00Z
status: passed
score: 4/4 criteria verified
re_verification: false
---

# Phase 3: Capture the OpenHands Run — Verification Report

**Phase Goal:** A real, complete OpenHands session that builds the F# FsLex/FsYacc calculator is captured to log files.
**Verified:** 2026-05-28
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Criterion 1: Real OpenHands JSONL logs exist (5 files, TerminalAction + TerminalObservation)

**Status: VERIFIED**

All 5 per-task JSONL files exist under `captured/logs/`:

| File | Parsed Events | TerminalActions | ObservationEvents | All sources |
|------|--------------|-----------------|-------------------|-------------|
| task1-scaffold.jsonl | 56 | 27 | 27 | agent/environment |
| task2-lexer.jsonl | 6 | 2 | 2 | agent/environment |
| task3-parser.jsonl | 34 | 15 (+ 1 ThinkAction) | 16 | agent/environment |
| task4-evaluator.jsonl | 30 | 14 | 14 | agent/environment |
| task5-buildtest.jsonl | 20 | 9 | 9 | agent/environment |

**Structure verified:** Each event has top-level `kind` field (`ActionEvent`, `ObservationEvent`, `MessageEvent`). ActionEvents have `action.kind = TerminalAction` or `ThinkAction`. ObservationEvents have `observation.kind = TerminalObservation` with `exit_code`, `command`, and `content[].text`. All ActionEvents have `source = agent`; all ObservationEvents have `source = environment`.

**Timestamps are contiguous:** All 5 tasks ran 2026-05-28 07:08–07:18, consistent with a single ~10-minute live session. No gaps suggesting manual intervention.

**Conversation ID cross-check:** Multiple events reference `full_output_save_dir` containing the same conversation UUID (`d4514bf309414d45aad5bed79478d68f`), confirming all task3 events belong to the same OpenHands headless session.

---

## Criterion 2: 5 scoped tasks, not one mega-prompt

**Status: VERIFIED**

Five separate JSONL log files, each corresponding to a distinct OpenHands headless invocation with a scoped task prompt. Task sequence (confirmed by timestamps and working-dir metadata):

1. `task1-scaffold` — `dotnet new console`, wrote calc.fsproj (07:08–07:11, 56 events)
2. `task2-lexer` — wrote Lexer.fsl from verbatim prompt content (07:14, 6 events)
3. `task3-parser` — wrote Parser.fsy + self-corrected 4 build failures (07:14–07:16, 34 events)
4. `task4-evaluator` — wrote Program.fs with FSharp.Text.Lexing wiring (07:16–07:17, 30 events)
5. `task5-buildtest` — final build + 3 test cases (07:17–07:18, 20 events)

All 5 task prompts exist as `.txt` files in `task-prompts/`.

**Scaffolding disclosure (honestly documented, not hidden):** Lexer.fsl content and the FixLineDirectives workaround in calc.fsproj were provided verbatim in task prompts (attempt 1 failed 3× on FsLex syntax). CAPTURE-MANIFEST.md discloses this clearly. The agent's genuine work = Parser.fsy + Program.fs + error self-correction.

---

## Criterion 3: Genuine error-and-fix cycle — AGENT'S OWN CORRECTION

**Status: VERIFIED (rigorous check)**

The full cycle is in `captured/logs/task3-parser.jsonl`, events 0–33 (0-indexed). All fix actions have `source = agent`. No human event appears in the JSONL after the task prompt MessageEvent (event 0). All timestamps are within a 1m17s window (07:14:57–07:16:14), with sub-second response times between agent actions and observations, consistent with automated loop execution.

**Failure sequence (4 build failures, agent self-correction):**

| Event (0-idx) | Exit code | Error | Agent action that caused it |
|---------------|-----------|-------|-----------------------------|
| 10 | 1 | `FSY000: at least one %start declaration is required` | Event 5 wrote Parser.fsy with `%type <int> start` but no `%start` line |
| 16 | 1 | `Parser.fsy(16,7): error parse error` | Event 11 added `%start <int> start` (invalid FsYacc syntax — combines start+type on one line) |
| 20 | 1 | `Parser.fsy(16,7): error parse error` | Event 17 wrote another attempt with same `%start <int> start` syntax |
| 26 | 1 | `FS0039: 'LexBuffer<_>' does not define 'FromText'` | Event 23 correctly separated `%start start` + `%type <int> start` (Parser.fsy now valid), but Program.fs written at event 7 used non-existent `LexBuffer<char>.FromText` |

**Agent's own reasoning (ThinkAction, event 21):**

> "The error is at line 16, column 7. Line 16 is `%start <int> start`. The issue might be that `%start` with a type annotation `<int>` is not the right syntax. In FsYacc, `%start` uses `%start rulename` and the type is inferred from the semantic action. [...] So the requirement says to use `%start start` (without type) AND `%type <int> start`."

The agent diagnosed the error itself by counting file lines against the error location, then applied the correct fix.

**Fix at event 23:** Agent wrote Parser.fsy with `%start start` and `%type <int> start` on separate lines (correct FsYacc syntax).

**Fix at event 27:** Agent then fixed Program.fs — replaced `LexBuffer<char>.FromText(new StringReader(input))` with `LexBuffer<char>.FromString input` (correct FSharp.Text.Lexing API).

**Success at event 30:** `dotnet build 2>&1` → `calc net10.0 성공 (0.7초)`, exit_code=0.

**Critically: NO manual/human action appears between any failure and any fix.** Every `ActionEvent` in the 07:14:57–07:16:14 window has `source = agent`. The fixes are the agent's own terminal commands (`cat > Parser.fsy << 'EOF'` and `cat > Program.fs << 'EOF'`), each followed immediately by an environment ObservationEvent.

**Attempt 1 artifacts are separate:** Attempt 1 logs are in `oh-workdir/_attempt1-attic/` (gitignored, not in captured/). The `03-02-RUN-NOTES-attempt1.md` documents that attempt and is clearly labeled. No attempt-1 artifacts leaked into captured/.

---

## Criterion 4: Calculator evaluates 2+3*4=14, (2+3)*4=20, 10-3-2=5

**Status: VERIFIED (live host re-run)**

**Agent's own test in task3 (event 32, within session):**

```
1+2*3 = 7
10-3-2 = 5
(10-3)-2 = 5
10-(3-2) = 9
2*3+4 = 10
(2+3)*4 = 20
100/10/2 = 5
1+2+3+4+5 = 15
```

**Task5-buildtest JSONL confirms the three required cases:**
- Event 16: `dotnet run -- "2+3*4"` → `14` (exit_code=0)
- Event 17: `dotnet run -- "(2+3)*4"` → `20` (exit_code=0)
- Event 18: `dotnet run -- "10-3-2"` → `5` (exit_code=0)

**Live host re-run (executed during this verification):**

```
dotnet build /Users/ohama/projs/OpenHandsTests/oh-workdir/calc  →  Build succeeded (0 errors, 0 warnings)
dotnet run --project oh-workdir/calc -- "2+3*4"   →  14
dotnet run --project oh-workdir/calc -- "(2+3)*4"  →  20
dotnet run --project oh-workdir/calc -- "10-3-2"   →  5
```

`captured/final-source/Parser.fsy` is identical to `oh-workdir/calc/Parser.fsy` (diff confirmed). The grammar uses `%left PLUS MINUS` / `%left STAR SLASH` giving correct operator precedence. `captured/test-output.txt` contains the same 14/20/5 results.

---

## Additional Honesty Checks

**CAPTURE-MANIFEST.md faithfulness:** The manifest's event table (task3: 34 events, 15 TerminalActions) matches the actual parsed JSONL (34 events, 15 TerminalActions). The error sequence table (FSY000 → parse error x2 → FS0039 → success) matches the observed exit codes at events 10, 16, 20, 26, 30 (0-indexed). The manifest's event-number references (10, 16, 20, 26, 30) are accurate 0-indexed positions of the ObservationEvents.

**Scaffolding is disclosed, not hidden:** CAPTURE-MANIFEST.md and transcript.md both state explicitly that Lexer.fsl and the FixLineDirectives workaround were provided via prompt. The agent's genuine work is clearly delimited.

**Attempt 1 isolation:** `oh-workdir/_attempt1-attic/` exists and contains the attempt-1 JSONL logs (including `task6-lexer-fix.jsonl`, `task4-evaluator-retry1.jsonl`, etc.). These are gitignored and not in the committed `captured/` directory.

**No RUN-03 violation in attempt 2:** Attempt 2's task3 JSONL shows zero human/user ActionEvents between the prompt MessageEvent (event 0) and the final MessageEvent (event 33). The manual fix from attempt 1 (the "Deviation Rule 3" incident) did not recur.

---

## Observable Truths — Final Table

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | 5 real JSONL files with TerminalAction/TerminalObservation events | VERIFIED | 5 files, 146 total events, agent+environment sources, contiguous timestamps |
| 2 | 5 scoped tasks (scaffold→lexer→parser→evaluator→build&test) | VERIFIED | 5 separate invocations, distinct timestamps, separate task prompts |
| 3 | Genuine error-and-fix by the agent (not manual) | VERIFIED | 4 build failures at events 10/16/20/26; agent ThinkAction reasoning visible; fixes at events 23+27; success at event 30; all source=agent |
| 4 | 2+3*4=14, (2+3)*4=20, 10-3-2=5 | VERIFIED | task5 JSONL events 16/17/18; live host re-run; captured/test-output.txt |

**Score: 4/4 criteria verified.**

---

## Minor Discrepancy (Non-Blocking)

The CAPTURE-MANIFEST.md says "events 10–30" and "4 genuine build failures". Counting the ObservationEvents at positions 10, 16, 20, 26 (0-indexed) gives 4 build failures, but the exact numbering scheme differs slightly from how the MANIFEST describes it (the MANIFEST mixes 0-indexed event numbers with prose that implies 1-indexed). This is a documentation inconsistency only — the raw JSONL evidence is unambiguous and matches the MANIFEST's claims substantively.

---

_Verified: 2026-05-28_
_Verifier: Claude (gsd-verifier)_
