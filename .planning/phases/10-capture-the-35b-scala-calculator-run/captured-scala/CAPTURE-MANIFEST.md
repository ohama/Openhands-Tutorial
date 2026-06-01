# Capture Manifest — 35B Scala 3 Calculator Run (v1.3)

**Run date:** 2026-06-01  
**Model:** openai/qwen-35b (Qwen2.5-35B via litellm proxy at 127.0.0.1:4000)  
**OpenHands version:** SDK v1.21.0 / CLI 1.16.0  
**Workspace:** oh-workdir-scala/ (LocalWorkspace, host PTY) — gitignored live project  

---

## Run Metadata

- **Run date:** 2026-06-01
- **Model:** openai/qwen-35b (Qwen2.5-35B via litellm @ http://127.0.0.1:4000/v1)
- **Model alias map:** `openai/qwen-35b` → litellm proxy → llama.cpp serving Qwen2.5-35B-Instruct GGUF
- **OpenHands version:** SDK v1.21.0 / CLI 1.16.0
- **Workspace:** oh-workdir-scala/ (LocalWorkspace, host PTY, gitignored)
- **scala-cli version:** 1.14.0
- **Scala version:** 3.8.3 (default; no `//> using scala` directive in final Calc.scala — uses scala-cli default)
- **JDK:** 17.0.19
- **Invocation pattern:** `OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL="openai/qwen-35b" LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" OPENHANDS_WORK_DIR=".../oh-workdir-scala" openhands --headless --json --yolo --override-with-envs -t "$(cat task-prompts-scala/taskN.txt)" 2>oh-workdir-scala/taskN.stderr.log | tee oh-workdir-scala/taskN.jsonl`

---

## Calculator Outcome (SCAL-01/02)

- **did-write-calc-unaided: YES**
- **unaided-attempts: 1**
- **scaffold-invoked: NO**
- **calc-description:** Agent wrote a 70-line idiomatic Scala 3 recursive-descent arithmetic calculator. Entry point `@main def calc(args: String*)` (Scala 3 `@main`). Class `ExprParser(input: String):` with Scala 3 significant-indentation (`:` block syntax). Hand-rolled recursive descent: `parseExpression` (`+`/`-`) → `parseTerm` (`*`/`/`) → `parseFactor` (digits / parenthesised sub-expression). Correct operator precedence and left-associativity via `while ... do` loops. Uses only `scala.*` standard library (no `//> using dep` directives, no build.sbt/external dependencies).
- **fallback-disclosure:** N/A — the fallback scaffold (task2-calc-scaffold.txt) was staged but never invoked. The agent's task2 output, while produced via multiple write attempts, is unambiguously a valid Scala 3 calculator. The fallback bar was never triggered.

**SCAL-01 status: PASS** (agent set up scala-cli itself: task1 events #6, #16–#17; wrote calculator unaided: task2 events #6–#41)  
**SCAL-02 status: PASS** (unaided attempt 1; scaffold not invoked; all ActionEvents source=agent)

---

## Scala 3 Idiom Notes

These observations from the final Calc.scala are for the 7부 chapter narrative.

- **entry-point-used:** `@main def calc(args: String*)` — Scala 3 `@main` annotation (not `object extends App` / `def main(args: Array[String])`)
- **adt-style:** None — the calculator uses direct `Int`-returning methods without a sealed trait Expr ADT. This is a simpler but valid approach. The model did not add a sealed trait / case class tree.
- **syntax-style:** Scala 3 significant-indentation throughout — `class ExprParser(input: String):`, `if ... then ... else`, `while ... do`, `peek() match { case Some('+') => ... }`. No Scala 2 braces. Scala 3 idiom consistent and unprompted.
- **scala-2-vs-3-slip:** NONE — the model did NOT revert to `object extends App` or `Array[String]` args or `{ ... }` block syntax. A predicted failure mode that did not occur.
- **left-associativity:** CORRECT — `while ... do { left = left - right }` loops implement left-to-right evaluation. `10-3-2` evaluates as `(10-3)-2 = 5`, not the naive right-recursive `10-(3-2) = 9`.

---

## Error-and-Fix Record (SCAL-03)

One genuine compile error, self-corrected by the agent.

### Error: private member access from top-level definition

**Location:** task3-buildtest.jsonl, events #6–#9

**Event #6 (ActionEvent, TerminalAction, source=agent):**
```
cd .../calc && scala-cli run Calc.scala -- "2+3*4" 2>&1
```

**Event #7 (ObservationEvent, TerminalObservation, exit=1) — COMPILE ERROR:**
```
Compiling project (Scala 3.8.3, JVM (17))
[error] ./Calc.scala:5:6
[error] variable pos cannot be accessed as a member of (parser : ExprParser) from the top-level definitions in package <empty>.
[error]   private variable pos can only be accessed from class ExprParser.
[error]   if parser.pos < expr.length then
[error]      ^^^^^^^^^^
[error] ./Calc.scala:6:72
[error] variable pos cannot be accessed as a member of (parser : ExprParser) from the top-level definitions in package <empty>.
[error]   private variable pos can only be accessed from class ExprParser.
[error]     throw new IllegalArgumentException("Unexpected character: " + expr(parser.pos))
[error]                                                                        ^^^^^^^^^^
Error compiling project (Scala 3.8.3, JVM (17))
Compilation failed
```

Root cause: `pos` was declared `private var pos = 0` in class `ExprParser`, but the `@main` top-level function accessed `parser.pos` directly (lines 5–6 of the agent's unaided Calc.scala). In Scala 3, top-level definitions (including `@main`) cannot access private members of other classes. This is a clean, in-distribution access-modifier mistake.

**Event #8 (ActionEvent, TerminalAction, source=agent) — AGENT'S OWN FIX:**
```
cd .../calc && sed -i '' 's/private var pos = 0/var pos = 0/' Calc.scala
```
Agent diagnosed the cause (private field) and made `pos` package-private by removing the `private` modifier.

**Event #9 (ObservationEvent, exit=0):** sed applied successfully (empty output, no errors).

### Error-and-fix summary

| # | Event | Type | Description | Fix |
|---|-------|------|-------------|-----|
| 1 | #7 (exit=1) | Compile error | `private var pos` accessed from `@main` top-level | `sed` removes `private` (event #8) |
| — | #9 (exit=0) | Fix confirmed | sed applied | Recompile at event #10 succeeds |

- **error-location:** task3-buildtest.jsonl, events #6–#9
- **iterations:** 1 (1 failed compile → 1 successful fix → all tests pass)
- **operator-intervention:** NONE — all events source=agent

---

## Canonical Test Outcome (SCAL-03)

Three canonical tests from task3-buildtest.jsonl, with independent host re-run confirmation.

### Agent JSONL results (task3-buildtest.jsonl)

| Input | Expected | Actual | exit | JSONL location | Result |
|-------|----------|--------|------|----------------|--------|
| `2+3*4` | 14 | `14` | 0 | events #10 (TA) / #11 (TO) | **PASS** |
| `(2+3)*4` | 20 | `20` | 0 | events #12 (TA) / #13 (TO) | **PASS** |
| `10-3-2` | 5 | `5` | 0 | events #14 (TA) / #15 (TO) | **PASS** |

**Event #11 verbatim content (TerminalObservation for `2+3*4`):**
```
Compiling project (Scala 3.8.3, JVM (17))
Compiled project (Scala 3.8.3, JVM (17))
14
```

**Event #13 verbatim content (TerminalObservation for `(2+3)*4`):**
```
20
```
(Cached compilation — only result printed)

**Event #15 verbatim content (TerminalObservation for `10-3-2`):**
```
5
```
(Cached compilation — only result printed; left-associative: (10-3)-2=5)

### Independent host re-run (captured-scala/test-output.txt)

Run date: 2026-06-01T06:03:25Z. scala-cli 1.14.0 / Scala 3.8.3.

```
$ scala-cli run Calc.scala -- "2+3*4"
14
(exit: 0)

$ scala-cli run Calc.scala -- "(2+3)*4"
20
(exit: 0)

$ scala-cli run Calc.scala -- "10-3-2"
5
(exit: 0)
```

- **host-rerun-matches-agent-capture: YES**
- **all-pass: YES** (14 / 20 / 5 — both JSONL and host re-run)

---

## Std-only Check

**File checked:** final-source/Calc.scala (70 lines)

- **Imports:** None — Calc.scala uses no import statements. All types used (`String`, `Int`, `Option`, `Some`, `None`, `IllegalArgumentException`) are in `scala.*` / `java.lang.*` — available by default in any Scala compilation unit.
- **`//> using dep` directives:** NONE present in Calc.scala.
- **External build files:** No build.sbt, no project/ directory, no Gradle/Mill files in oh-workdir-scala/calc/. The calc/ directory contains only Calc.scala, Hello.scala, and the .bsp/.scala-build caches (excluded from committed final-source/).
- **Parser library check:** No parser-combinator library (Fastparse, parboiled2, etc.) added. Pure hand-rolled recursive descent.

**Std-only constraint: SATISFIED** — no deviation.

---

## Timing Summary (CHAP-01/CHAP-02)

Wall-clock times from JSONL timestamps (first event → last event per task).  
LLM-call gaps = ObservationEvent timestamp → next ActionEvent timestamp (pure model thinking time, excludes bash execution).

| Task | First event | Last event | Total wall-clock | TerminalActions | Avg LLM-call gap | Min | Max |
|------|------------|-----------|------------------|-----------------|-----------------|-----|-----|
| task1-scaffold | 14:40:30.693 | 14:41:01.220 | **30.5s** | 4 | 2.1s | 1.1s | 2.9s |
| task2-write-calc | 14:42:16.270 | 14:45:11.031 | **174.8s (~2m55s)** | 20 | 6.5s | 1.4s | 14.7s |
| task3-buildtest | 14:52:18.696 | 14:52:48.221 | **29.5s** | 6 | 2.3s | 1.9s | 2.8s |
| **Total active** | — | — | **234.8s (~3m55s)** | **30** | **~5.0s avg** | — | — |

**Inter-task gaps:** ~1.25min between task1 and task2; ~7.1min between task2 and task3 (operator review + launch). Active agent time only: 234.8s.

**NOTE on the legacy ~14–32s/call figure:** This is a v1 pre-run PREDICTION (documented in v1 ROADMAP, 2026-05-28). It is NOT cited here as a measurement and does NOT appear in this manifest. The real measured per-call averages for this run are 2.1s (task1), 6.5s (task2), and 2.3s (task3), computed from JSONL timestamps.

---

## Comparison Hook (for Phase 11 / 7부 chapter)

- **vs-v1-35B-FsLex:** In v1 (F# calculator, 2026-05-28), the 35B could NOT write a valid FsLex lexer unaided — 3 agent invocations (94+27+16 TerminalActions) all failed (wrong grammar format, `%%` confusion). The FsLex lexer was provided verbatim as a scaffold. In v1.3, the same 35B model wrote a working Scala 3 recursive-descent calculator unaided on attempt 1 (task2-write-calc.jsonl). **Scala/calculator is more in-distribution for this model than FsLex/lexer generators.**

- **vs-v1.2-35B-Rust:** In v1.2 (Rust HTTP server, 2026-05-28), the 35B wrote the server unaided on attempt 1 (did-write-server-unaided=YES). The same pattern holds in v1.3: did-write-calc-unaided=YES. Both confirm the 35B can produce working code unaided in standard domains. Error-and-fix count: v1.2 had 2 build fix iterations (format! syntax + E0382 borrow checker); v1.3 had 1 compile fix (private access). Both were self-corrected.

- **ADT-vs-FsLex contrast:** The v1 F# calculator used FsLex/FsYacc grammar files (a domain-specific format the model did not know). The v1.3 Scala calculator uses a hand-rolled recursive-descent parser with explicit precedence levels — a general pattern the model does know. This explains the capability gap: it is not the calculator that's hard, it is the parser-generator domain knowledge.

- **Calculator-trilogy completion:** v1 (F# with FsLex, scaffold needed) → v1.2 (Rust HTTP server, unaided) → v1.3 (Scala 3 recursive-descent calculator, unaided). The 35B that needed FsLex scaffolding in v1 wrote the same calculator unaided in Scala in v1.3. This is the core thesis of 7부.

---

## Deviations

### 1. No FinishAction in any task JSONL

All 3 tasks ended with MessageEvent (agent reporting completion in task1/task2) or implicitly after the last ObservationEvent (task3). No FinishAction observed. Consistent with OpenHands 1.16 behavior — same as v1/v1.1/v1.2.

### 2. file_editor AgentErrorEvent at task3 event #2–#3

Agent tried the `file_editor` tool (event #2 ActionEvent with `action.kind=None`), which produced an AgentErrorEvent (#3). Agent recovered immediately by using bash (`cat`, `sed`, `scala-cli`). Not a run failure. Same pattern as v1.2 task3.

### 3. Brief non-Scala fragment early in task2 (self-corrected)

task2 events #10–#15: Agent briefly attempted Python-style writes (`import os`, `lines = [...]`) that failed (exit=1/exit=258). Agent self-corrected within task2 and the final on-disk Calc.scala is clean Scala 3. This is an in-task deviation self-corrected before task2 concluded — the write process was exploratory but the output is correct.

### 4. No `//> using scala` directive

The agent did not add a `//> using scala 3` directive to Calc.scala (reasonable, since scala-cli defaults to Scala 3.8.3 on this installation). Not a constraint violation.

### 5. Zero manual edits

No operator/human edited any agent-produced file (Calc.scala, Hello.scala) at any point between tasks or within a task. All fix events (the `sed` at task3 event #8) are the agent's own ActionEvents (source=agent). The honesty-gate check (see below) mechanically confirms this.

### 6. No library-add attempts; no scalac-direct attempts

The agent never tried to add a parser library, never invoked `scalac` directly (always used `scala-cli run`). The std-only constraint was satisfied without any intervention.

---

## Honesty Gate Result

**HONESTY GATE: PASSED**

The source=agent check was run mechanically across all 3 JSONL files before any artifact was copied or committed. Every ActionEvent across task1-scaffold.jsonl, task2-write-calc.jsonl, and task3-buildtest.jsonl has `source=agent`. The first event (MessageEvent, source=user) in each JSONL contains the task prompt — these are MessageEvents, not ActionEvents, and are not subject to the gate.

**Python3 check snippet (run 2026-06-01):**
```python
import json, glob, sys
bad = []
for f in sorted(glob.glob('/Users/ohama/projs/OpenHandsTests/oh-workdir-scala/*.jsonl')):
    for ln, line in enumerate(open(f), 1):
        line = line.strip()
        if not line.startswith('{'): continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            print(f'PARSE_ERROR {f}:{ln}')
            continue
        if e.get('kind') == 'ActionEvent':
            src = e.get('source')
            if src != 'agent':
                bad.append((f, ln, src, str(e.get('action', {}).get('command', ''))[:60]))
if bad:
    print('HONESTY GATE FAILED — ActionEvents with source != agent:')
    for f, ln, src, cmd in bad:
        print(f'  {f}:{ln}  source={src!r}  command={cmd!r}')
    sys.exit(2)
print('HONESTY GATE PASS — every ActionEvent has source=agent across all JSONLs')
```

**Result:** `HONESTY GATE PASS — every ActionEvent has source=agent across all JSONLs`  
**Total ActionEvents checked:** 36 (task1: 9, task2: 20, task3: 7)  
**Offending events:** 0  
**Check date:** 2026-06-01  
**Exit code:** 0  

This is the v1.3 mechanical enforcement of the v1/v1.1/v1.2 manual-edits prohibition. No manual edits to agent files; no fabricated success; the ~14–32s/call prediction not cited as a measurement.

---

## Artifact-to-Requirement Map

### SCAL-01 — Agent set up scala-cli and verified it unaided

**Evidence:** `captured-scala/logs/task1-scaffold.jsonl`

- Event #6 (ActionEvent, TerminalAction): `scala-cli --version` → `Scala CLI version: 1.14.0 / Scala version (default): 3.8.3` (event #7, exit=0)
- Event #12 (ActionEvent, TerminalAction): writes Hello.scala using `@main def hello()` — Scala 3 idiom unprompted
- Event #16 (ActionEvent, TerminalAction): `scala-cli run Hello.scala` → `SCALA_OK` (event #17, exit=0)

**SCAL-01 status: PASS**

---

### SCAL-02 — Agent wrote the calculator unaided (zero manual edits)

**Evidence:** `captured-scala/logs/task2-write-calc.jsonl`, `captured-scala/final-source/Calc.scala`

- Event #6 (ActionEvent, TerminalAction): first Calc.scala write attempt via heredoc
- Events #30, #32, #34, #36, #38 (ActionEvent, TerminalAction): `printf '%s\n'` section writes completing final Calc.scala
- Event #40 (ActionEvent, TerminalAction): `cat Calc.scala` verification (event #41, exit=0, shows 70-line Scala 3 calculator)
- did-write-calc-unaided=YES; scaffold not invoked; all ActionEvents source=agent (honesty gate PASS)

**SCAL-02 status: PASS**

---

### SCAL-03 — Canonical tests + error-and-fix traceable to JSONL

**Evidence:** `captured-scala/logs/task3-buildtest.jsonl`, `captured-scala/test-output.txt`

Error-and-fix:
- Event #6 (ActionEvent): run `2+3*4` → event #7 (ObservationEvent, exit=1): compile error (`private var pos` accessed from `@main`)
- Event #8 (ActionEvent): `sed -i '' 's/private var pos = 0/var pos = 0/' Calc.scala` → event #9 (exit=0)

Canonical test outcomes (post-fix):
- Events #10/#11 (exit=0): `2+3*4` → `14` — PASS
- Events #12/#13 (exit=0): `(2+3)*4` → `20` — PASS
- Events #14/#15 (exit=0): `10-3-2` → `5` — PASS

Host re-run (test-output.txt, 2026-06-01T06:03:25Z): 14 / 20 / 5, all exit=0 — PASS

**SCAL-03 status: PASS**

---

## Artifact Index

| Path | Description | Requirement(s) evidenced |
|------|-------------|--------------------------|
| logs/task1-scaffold.jsonl | Raw JSONL: scaffold task (20 events, 4 TA) | **SCAL-01** (scala-cli setup events #6, #16–#17; @main idiom at #12) |
| logs/task2-write-calc.jsonl | Raw JSONL: write-calc unaided (42 events, 20 TA) | **SCAL-02** (did-write-calc-unaided, events #6–#41) |
| logs/task3-buildtest.jsonl | Raw JSONL: buildtest (16 events, 6 TA) | **SCAL-03** (error+fix events #6–#9; canonical tests #10–#15) |
| logs/task1-scaffold.stderr.log | Stderr from task1 OpenHands invocation | Background/diagnostic |
| logs/task2-write-calc.stderr.log | Stderr from task2 invocation | Background/diagnostic |
| logs/task3-buildtest.stderr.log | Stderr from task3 invocation | Background/diagnostic |
| transcript.md | Human-readable per-task command/output transcript | Readable reference for chapter writers |
| final-source/Calc.scala | Final agent-written Calc.scala (70 lines, post-sed, Scala 3) | SCAL-02 final state; SCAL-03 fixed state |
| final-source/Hello.scala | Scaffold file written by agent in task1 | SCAL-01 (task1 evidence) |
| test-output.txt | Fresh host `scala-cli run` for all three canonical tests (2026-06-01) | **SCAL-03** host-side independent confirmation; host-rerun-matches-agent-capture=YES |
| CAPTURE-MANIFEST.md | This file — artifact-to-requirement map | Phase 11 navigation |
