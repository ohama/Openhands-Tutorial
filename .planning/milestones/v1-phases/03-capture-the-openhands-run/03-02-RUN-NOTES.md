# 03-02 Run Notes — OpenHands Calculator Build (Attempt 2)

**Date:** 2026-05-28
**Model:** openai/qwen-local (Qwen2.5-35B via litellm proxy at 127.0.0.1:4000)
**Invocation:** `openhands --headless --json --yolo --override-with-envs`
**Workspace:** `/Users/ohama/projs/OpenHandsTests/oh-workdir` (LocalWorkspace, host PTY)
**Attempt:** 2 (attempt 1 archived in `oh-workdir/_attempt1-attic/`)

---

## Preflight Status

| Check | Result |
|-------|--------|
| `openhands --version` | OK (SDK v1.21.0 / CLI 1.16.0) |
| litellm proxy qwen-local | PROXY_OK |
| oh-workdir/calc clean | OK — no stale calc/ from attempt 1 (moved to _attempt1-attic/) |
| Task prompt files present | OK — all 6 prompts in task-prompts/ |
| oh-workdir gitignored | CONFIRMED (`git check-ignore` returns oh-workdir) |

---

## Per-Task Outcome Table

| # | Task | JSONL Log | Duration | Events | TerminalActions | Completion Signal | Retries | Prompt Adjustments | Host Check |
|---|------|-----------|----------|--------|-----------------|-------------------|---------|--------------------|------------|
| 1 | scaffold | task1-scaffold.jsonl | 3m 6s (07:08:28–07:11:34) | 56 | 27 | FinalMsg (agent) | 0 | None | PASS: calc.fsproj (FixLineDirectives), Parser.fsy, Program.fs present; no Lexer.fsl |
| 2 | lexer | task2-lexer.jsonl | 16s (07:14:15–07:14:31) | 6 | 2 | FinalMsg (agent) | 0 | None | PASS: Lexer.fsl present with exact provided content |
| 3 | parser | task3-parser.jsonl | 1m 17s (07:14:57–07:16:14) | 34 | 15 | FinalMsg (agent) | 0 | None | PASS: Parser.fsy non-empty with %left grammar |
| 4 | evaluator | task4-evaluator.jsonl | 45s (07:16:48–07:17:33) | 30 | 14 | FinalMsg (agent) | 0 | None | PASS: Program.fs references FSharp.Text.Lexing |
| 5 | build&test | task5-buildtest.jsonl | 32s (07:17:57–07:18:29) | 20 | 9 | FinalMsg (agent) | 0 | None | PASS: build succeeded, all 3 cases correct |

**Total invocations:** 5
**Total retries:** 0 (zero prompt adjustments needed in this attempt)

---

## Branch Taken

**Branch A** — The error-and-fix cycle was captured within task3-parser.jsonl.

The agent hit genuine build failures during Task 3 (writing Parser.fsy) and self-corrected across 4 build attempts before succeeding. The error-and-fix cycle is entirely within `task3-parser.jsonl`.

Task 5 (build&test) reported all three cases passing on first attempt — no task6-fix.jsonl was needed.

---

## Error-and-Fix Cycle (Branch A)

**Location:** `oh-workdir/task3-parser.jsonl`, events 9–30
**Type:** Genuine F# / FsYacc build failures — diagnosed and fixed autonomously by the agent

### Failure Sequence

**Attempt 1 — Event 9 (build) → Event 10 (error):**
Agent wrote Parser.fsy with `%type <int> start` but omitted `%start start`.
Build error: `FSYACC : error FSY000: at least one %start declaration is required`

**Attempt 2 — Event 11 (rewrite) → Event 16 (error):**
Agent added `%start <int> start` (wrong FsYacc syntax; FsYacc takes just the symbol, not the type).
Build error: `Parser.fsy(16,7): error parse error` (fsyacc grammar parse failure)

**Attempt 3 — Event 17 (rewrite) → Event 20 (same error):**
Agent made another attempt — same parse error remained.
Build error: `Parser.fsy(16,7): error parse error`

**Attempt 4 — Event 23 (rewrite) → Event 25 → Event 26 (new error):**
Agent correctly separated `%start start` and `%type <int> start` on separate lines.
Parser.fsy now accepted by fsyacc. New error in Program.fs:
`FS0039: 'LexBuffer<_>' does not define 'FromText'` (agent used `LexBuffer.FromText` but correct API is `LexBuffer<char>.FromString`)

**Attempt 5 — Event 27 (fix Program.fs) → Event 29 (build) → Event 30 (SUCCESS):**
Agent corrected `LexBuffer<char>.FromString input` in Program.fs.
Build output: `calc net10.0 성공 (0.7초) → bin/Debug/net10.0/calc.dll`

**Validation — Event 31 (run tests):**
Agent ran 8 test expressions:
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
All correct, including the critical left-associativity case (`10-3-2 = 5`).

### Summary of the Real Error and Real Fix

| What the agent did wrong | What it fixed |
|--------------------------|---------------|
| Omitted `%start` declaration | Added `%start start` |
| Used `%start <int> start` (invalid FsYacc syntax) | Separated into `%start start` + `%type <int> start` |
| Used `LexBuffer.FromText` (non-existent API) | Changed to `LexBuffer<char>.FromString` |

The final fix commit (conceptually): Task 3 overwrote Program.fs with a working implementation — this was not in the task scope but was genuine agent behavior to get the build working.

---

## Final Host Re-Check (Source of Truth)

Executed directly on host after all 5 tasks:

```
$ dotnet run --project /Users/ohama/projs/OpenHandsTests/oh-workdir/calc -- "2+3*4"
14

$ dotnet run --project /Users/ohama/projs/OpenHandsTests/oh-workdir/calc -- "(2+3)*4"
20

$ dotnet run --project /Users/ohama/projs/OpenHandsTests/oh-workdir/calc -- "10-3-2"
5
```

All three required outputs confirmed: **14, 20, 5**.

---

## Keeper Logs

| Log | Status | Notes |
|-----|--------|-------|
| `oh-workdir/task1-scaffold.jsonl` | KEEPER | Scaffold creation (56 events, 27 TerminalActions) |
| `oh-workdir/task2-lexer.jsonl` | KEEPER | Verbatim lexer creation (6 events, minimal) |
| `oh-workdir/task3-parser.jsonl` | KEEPER (PRIMARY) | Contains full error-and-fix cycle; 4 build failures + self-correction |
| `oh-workdir/task4-evaluator.jsonl` | KEEPER | Program.fs CLI wiring (30 events) |
| `oh-workdir/task5-buildtest.jsonl` | KEEPER | Final build+test verification (all 3 cases PASS) |
| `oh-workdir/task6-fix.jsonl` | N/A — not created (Branch A, no fix task needed) |

---

## Notable Observations

1. **Attempt 2 success vs. Attempt 1 failure:** Providing the Lexer.fsl content verbatim in task2-lexer.txt eliminated the FsLex syntax confusion that defeated attempt 1. The agent never touched Lexer.fsl syntax in this run.

2. **The genuine error-and-fix is in-distribution:** FsYacc `%start` syntax (wrong → `%start <int> start`, correct → `%start start` + separate `%type`) and `LexBuffer.FromText` vs `LexBuffer<char>.FromString` are ordinary F# API errors well within the model's capability. Four build attempts, four distinct diagnoses.

3. **Task 3 scope creep:** The parser task also wrote Program.fs (beyond its scope), which introduced the `FromText` error. This is genuine agent behavior — not a problem, just observed.

4. **Task 1 took 3 minutes / 27 TerminalActions:** The agent ran `dotnet new` and several exploration commands. The scaffold output was correct regardless.

5. **Zero retries needed:** All tasks completed in first invocation. The revised prompts (explicit bash-only file writing, provided lexer) worked.
