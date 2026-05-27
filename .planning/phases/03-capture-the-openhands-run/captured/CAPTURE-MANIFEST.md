# Capture Manifest

**Run date:** 2026-05-28  
**Model:** openai/qwen-local (Qwen2.5-35B via litellm proxy at 127.0.0.1:4000)  
**Run attempt:** 2 (attempt 1 archived in oh-workdir/_attempt1-attic/)  
**OpenHands version:** SDK v1.21.0 / CLI 1.16.0  
**Workspace:** oh-workdir/ (LocalWorkspace, host PTY) — gitignored live project  

---

## Artifact-to-Requirement Map

### RUN-01 — Real captured commands and output (not synthetic)

**Evidence:** `captured/logs/*.jsonl`

All 5 per-task JSONL logs are verbatim captures from the OpenHands headless CLI
(`openhands --headless --json --yolo --override-with-envs | tee <file>.jsonl`).
Each event is a raw JSON line: ActionEvent (TerminalAction) or ObservationEvent (TerminalObservation).
These are the unedited, authoritative record of what the agent did and what the system returned.

| Log file | Events | TerminalActions | Task |
|----------|--------|-----------------|------|
| logs/task1-scaffold.jsonl | 56 | 27 | Scaffold calc/ project |
| logs/task2-lexer.jsonl | 6 | 2 | Write Lexer.fsl |
| logs/task3-parser.jsonl | 34 | 15 | Write Parser.fsy (primary: error-and-fix) |
| logs/task4-evaluator.jsonl | 30 | 14 | Write Program.fs CLI wiring |
| logs/task5-buildtest.jsonl | 20 | 9 | Build + test all 3 expressions |

**Total:** 146 events, 67 TerminalActions across 5 logs.

---

### RUN-02 — Agent decomposed the work into >=5 scoped tasks

**Evidence:** The 5 distinct per-task JSONL logs above (task1 through task5)

Each log corresponds to a separate OpenHands headless invocation with a scoped task prompt.
All share the same working directory (oh-workdir/calc) as confirmed by ObservationEvent metadata.

**Task sequence:**

1. `task1-scaffold` — created calc/ project with dotnet new, wrote calc.fsproj (with
   FixLineDirectives workaround for .NET 10 + FsLexYacc 11.3.0), wrote placeholder Parser.fsy
   and Program.fs
2. `task2-lexer` — wrote Lexer.fsl from the verbatim content provided in the task prompt
   (see note below on lexer scaffolding)
3. `task3-parser` — wrote Parser.fsy with FsYacc grammar, self-corrected 4 build failures
4. `task4-evaluator` — wrote Program.fs with CLI argument parsing and FSharp.Text.Lexing wiring
5. `task5-buildtest` — built and ran all 3 test expressions; all passed on first attempt

---

### RUN-03 — A genuine error-and-fix cycle (not scripted)

**Evidence:** `captured/logs/task3-parser.jsonl`, events 10–30

**Location for Phase 4 narration:** task3-parser.jsonl, events 10–30

**Failure sequence (4 genuine build failures, self-corrected):**

| Event | Exit code | Error |
|-------|-----------|-------|
| 10 | 1 | `FSY000: at least one %start declaration is required` — agent omitted `%start` entirely |
| 16 | 1 | `Parser.fsy(16,7): error parse error` — agent used invalid `%start <int> start` syntax |
| 20 | 1 | `Parser.fsy(16,7): error parse error` — same error, another attempt |
| 26 | 1 | `FS0039: 'LexBuffer<_>' does not define 'FromText'` — agent used non-existent API |

**Fix at event 30 (exit_code=0):** Agent separated `%start start` and `%type <int> start` onto
separate lines (correct FsYacc syntax), and changed `LexBuffer.FromText` to
`LexBuffer<char>.FromString` (correct FSharp.Text.Lexing API). Build output:
`calc net10.0 성공 (0.7초) → bin/Debug/net10.0/calc.dll`

**Nature of errors:** These are ordinary F# / FsYacc API errors — wrong declaration syntax and
a non-existent method name. The model diagnosed and fixed each autonomously without external help.

**What to narrate in Phase 4:** The agent saw a build error, read the compiler output, identified
the specific line and error code, rewrote the file with the correction, and retried. This cycle
repeated 4 times before the build succeeded.

---

### 2+3*4=14 criterion — Operator precedence is correct (plus grouping and associativity)

**Evidence:** `captured/test-output.txt`

Fresh host run executed after all 5 tasks completed:

```
dotnet build oh-workdir/calc          -> Build succeeded (0 errors, 0 warnings)
dotnet run -- "2+3*4"                 -> 14   (operator precedence: STAR binds tighter than PLUS)
dotnet run -- "(2+3)*4"               -> 20   (parenthesis grouping overrides precedence)
dotnet run -- "10-3-2"                -> 5    (left-associativity: (10-3)-2 = 5, not 10-(3-2) = 9)
```

All three required outputs confirmed. The critical case is `2+3*4=14`: a naive grammar without
`%left` declarations gives 20 (wrong). The agent wrote `%left PLUS MINUS` / `%left STAR SLASH`
from the start, so all three cases passed.

---

## Additional Notes

### On the lexer and .fsproj (scaffolded, not agent-authored)

The Lexer.fsl content and the calc.fsproj FixLineDirectives workaround were **provided verbatim
in the task prompts** (task2-lexer.txt and task1-scaffold.txt respectively). This was a deliberate
choice for attempt 2:

- **FsLex syntax** (.fsl format) is out-of-distribution for the Qwen2.5-35B model. In attempt 1,
  three separate agent invocations (94+27+16 TerminalActions) all produced invalid FsLex files
  (added `%%` separator, wrong rule syntax). The decision to provide Lexer.fsl verbatim was
  documented as Deviation Rule 3 after those 3 agents exhausted the retry budget.
- **The FixLineDirectives workaround** in calc.fsproj is a non-obvious .NET 10 + FsLexYacc 11.3.0
  compatibility fix. Providing it eliminated a non-instructive blocker.

The agent's genuine work in attempt 2 was:
- Writing Parser.fsy (FsYacc grammar with correct precedence declarations)
- Writing Program.fs (CLI argument parsing + FSharp.Text.Lexing API wiring)
- Self-correcting 4 build failures in task3 without any external help

This is documented honestly in transcript.md and the final source snapshot.

### Run attempts

| Attempt | Outcome | Notes |
|---------|---------|-------|
| 1 | Failed — FsLex blocker | 3 agents, 137+ TerminalActions; Lexer.fsl never produced correctly |
| 2 | SUCCESS | Provided Lexer.fsl verbatim; agent self-corrected parser in 4 iterations |

Attempt 1 logs archived in oh-workdir/_attempt1-attic/ (gitignored, not committed).

### oh-workdir/ is the live (gitignored) project

oh-workdir/ is listed in .gitignore and confirmed gitignored by `git check-ignore oh-workdir`.
The committed artifacts live ONLY under this captured/ directory. oh-workdir/calc/ contains the
live F# project that the build/test commands target; it is NOT tracked by git.

---

## Artifact Index

| Path | Description | Requirement evidenced |
|------|-------------|----------------------|
| captured/logs/task1-scaffold.jsonl | Raw JSONL: scaffold task (56 events, 27 TA) | RUN-01, RUN-02 |
| captured/logs/task2-lexer.jsonl | Raw JSONL: lexer task (6 events, 2 TA) | RUN-01, RUN-02 |
| captured/logs/task3-parser.jsonl | Raw JSONL: parser task (34 events, 15 TA) | RUN-01, RUN-02, RUN-03 |
| captured/logs/task4-evaluator.jsonl | Raw JSONL: evaluator task (30 events, 14 TA) | RUN-01, RUN-02 |
| captured/logs/task5-buildtest.jsonl | Raw JSONL: build+test task (20 events, 9 TA) | RUN-01, RUN-02 |
| captured/transcript.md | Human-readable per-task command/output transcript | RUN-01 (readable) |
| captured/final-source/calc.fsproj | Verbatim agent-produced project file | Final state evidence |
| captured/final-source/Lexer.fsl | Verbatim Lexer.fsl (provided via prompt) | Final state evidence |
| captured/final-source/Parser.fsy | Verbatim Parser.fsy (%left precedence, %start/%type correct) | RUN-03 final fix evidence |
| captured/final-source/Program.fs | Verbatim Program.fs (LexBuffer<char>.FromString) | RUN-03 final fix evidence |
| captured/test-output.txt | Fresh host dotnet build + 3-case run (14/20/5) | 2+3*4=14 criterion |
| captured/CAPTURE-MANIFEST.md | This file — artifact-to-requirement map | Phase 4 navigation |
