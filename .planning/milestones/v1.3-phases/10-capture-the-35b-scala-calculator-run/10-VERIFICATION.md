---
phase: 10-capture-the-35b-scala-calculator-run
verified: 2026-06-01T07:30:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 10: Scala Calculator Capture — Verification Report

**Phase Goal:** A real, honest 35B OpenHands run of a minimal Scala 3 arithmetic calculator captured on disk as per-task JSONL, preflight-verified and honesty-gated, with a committed CAPTURE-MANIFEST.md capture gate.

**Verified:** 2026-06-01T07:30:00Z
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Method

All claims were verified against raw artifacts — the three oh-workdir-scala/*.jsonl files (gitignored, live) and the captured-scala/logs/*.jsonl files (committed). The two sets are byte-identical (MD5 confirmed for all three pairs). The Python honesty-gate script was re-run independently. Calc.scala was read directly. The CAPTURE-MANIFEST.md event indices were cross-checked against raw JSONL positions.

---

## Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Host preflight verified scala-cli + JDK before any agent run | VERIFIED | 10-01-PREFLIGHT.md: scala-cli 1.14.0, JDK 17.0.19, trivial run → PREFLIGHT_OK (exit 0), proxy live |
| 2 | Agent wrote Calc.scala unaided (no source provided in task2 prompt); scaffold not invoked | VERIFIED | task2-write-calc.txt is behavior-only; no task2-calc-scaffold.jsonl exists; task2-write-calc.jsonl 20 ActionEvents all source=agent |
| 3 | Every ActionEvent across all task JSONLs has source=agent | VERIFIED | Mechanical re-check: 36 ActionEvents total (task1: 9, task2: 20, task3: 7), 0 non-agent; both oh-workdir-scala/ and captured-scala/logs/ pass |
| 4 | Canonical test outcomes appear as real ObservationEvents in task3 JSONL (14/20/5); genuine compile error + agent fix traceable | VERIFIED | Directly parsed: events #6/#7 (compile error, exit=1), #8/#9 (sed fix, exit=0), #11/#13/#15 (14/20/5, exit=0) — all real TerminalObservation events |
| 5 | CAPTURE-MANIFEST.md is committed and records all required fields | VERIFIED | Git-tracked in commit acd3009; records did-write-calc-unaided=YES, scaffold-invoked=NO, canonical test results, honesty gate PASS, host re-run |

**Score:** 5/5 truths verified

---

## Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `oh-workdir-scala/task1-scaffold.jsonl` | VERIFIED | 51 lines, 20 events, 9 ActionEvents all source=agent; byte-identical to captured copy |
| `oh-workdir-scala/task2-write-calc.jsonl` | VERIFIED | 69 lines, 42 events, 20 ActionEvents all source=agent; byte-identical to captured copy |
| `oh-workdir-scala/task3-buildtest.jsonl` | VERIFIED | 59 lines, 16 events, 7 ActionEvents all source=agent; byte-identical to captured copy |
| `captured-scala/logs/*.jsonl` (3 files) | VERIFIED | Committed; MD5-identical to live oh-workdir-scala JSONLs |
| `captured-scala/final-source/Calc.scala` | VERIFIED | 70 lines, Scala 3 significant-indentation, `var pos = 0` (post-sed); MD5-identical to oh-workdir-scala/calc/Calc.scala; byte-level match confirmed |
| `captured-scala/test-output.txt` | VERIFIED | Records host re-run 2026-06-01T06:03:25Z: 14/20/5, exit=0 for all three inputs |
| `captured-scala/CAPTURE-MANIFEST.md` | VERIFIED | Committed (git-tracked); complete; all required fields present |
| `task-prompts-scala/task2-write-calc.txt` | VERIFIED | Behavior-only prompt; no Calc.scala source provided |
| `10-01-PREFLIGHT.md` | VERIFIED | PREFLIGHT GREEN; scala-cli 1.14.0, JDK 17.0.19, cache warm, proxy live |

---

## Key Link Verification

### Criterion 1: Preflight → agent run

10-01-PREFLIGHT.md records PREFLIGHT GREEN. 10-02-RUN-NOTES.md records run invoked after preflight. The JSONL timestamps (task1 first event 14:40:30.693) are after the preflight timestamp (05:34:36Z). LINKED.

### Criterion 2: did-write-calc-unaided=YES against JSONL evidence

task2-write-calc.txt contains no Calc.scala source code — behavior-only specification. The task2 JSONL shows 20 ActionEvents all source=agent writing Calc.scala via heredoc/printf in multiple iterations (events #6, #8, #10, #12, #14, #16, #18, #20, #22, #24, #26, #28, #30, #32, #34, #36, #38, #40, with verification cat at #40). No task2-calc-scaffold.jsonl exists. WIRED.

### Criterion 3: Honesty gate independent re-run

Re-run of the Python honesty gate script on both oh-workdir-scala/*.jsonl and captured-scala/logs/*.jsonl: 36 ActionEvents each, 0 source!=agent. WIRED.

### Criterion 4: task3 JSONL event content → canonical test outcomes

Directly parsed events #6–#15 from task3-buildtest.jsonl (raw file, not MANIFEST summary):

- Event #6 (ActionEvent): `scala-cli run Calc.scala -- "2+3*4" 2>&1`
- Event #7 (ObservationEvent, exit=1): compile error — `variable pos cannot be accessed as a member of (parser : ExprParser) from the top-level definitions`
- Event #8 (ActionEvent): `sed -i '' 's/private var pos = 0/var pos = 0/' Calc.scala`
- Event #9 (ObservationEvent, exit=0): empty (sed success)
- Event #10 (ActionEvent): `scala-cli run Calc.scala -- "2+3*4" 2>&1`
- Event #11 (ObservationEvent, exit=0): `Compiling project (Scala 3.8.3, JVM (17))\nCompiled project (Scala 3.8.3, JVM (17))\n14`
- Event #12 (ActionEvent): `scala-cli run Calc.scala -- "(2+3)*4" 2>&1`
- Event #13 (ObservationEvent, exit=0): `20`
- Event #14 (ActionEvent): `scala-cli run Calc.scala -- "10-3-2" 2>&1`
- Event #15 (ObservationEvent, exit=0): `5`

All four sub-claims confirmed: real compile error (exit=1), agent-authored sed fix (source=agent), three canonical test outputs (14/20/5, all exit=0). WIRED.

### Criterion 5: CAPTURE-MANIFEST.md committed and complete

Git commit acd3009 (2026-06-01) adds all 11 files including CAPTURE-MANIFEST.md. `git ls-files --error-unmatch` confirms all key artifacts are tracked. WIRED.

---

## SCAL Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|---------|
| SCAL-01: Real captured run; agent sets up scala-cli unaided; host preflight first | SATISFIED | task1 JSONL events #6/#7 (scala-cli --version → 1.14.0), #16/#17 (Hello.scala run → SCALA_OK); 10-01-PREFLIGHT.md |
| SCAL-02: Honest recording; zero manual edits; every ActionEvent source=agent | SATISFIED | 36/36 ActionEvents source=agent (mechanically re-verified); no task2-calc-scaffold.jsonl; did-write-calc-unaided=YES |
| SCAL-03: Canonical test results in real ObservationEvents; error-and-fix traceable | SATISFIED | task3 events #6–#15 parsed directly; compile error → sed fix → 14/20/5 all confirmed |

---

## Honesty-Quality Checks

### Byte-level match: final-source/Calc.scala vs agent-produced

MD5 of captured-scala/final-source/Calc.scala = ae51fe2d553722cf6968c4928089a407
MD5 of oh-workdir-scala/calc/Calc.scala = ae51fe2d553722cf6968c4928089a407

MATCH. The final-source copy is byte-identical to the live file. The final-source correctly reflects the post-sed state (`var pos = 0`, not `private var pos = 0`), which is consistent with task2 producing `private var pos = 0` (confirmed in task2 event #41 cat output) and task3 event #8 applying `sed -i '' 's/private var pos = 0/var pos = 0/'` (confirmed in task3 JSONL). The sequence is honest.

### The ~14-32s/call figure

Checked in CAPTURE-MANIFEST.md: the figure appears exactly once, in a NOTE explicitly labelling it a "v1 pre-run PREDICTION" that "is NOT cited here as a measurement." It is not used as a measured value anywhere in the manifest. CLEAN.

### Event-numbering consistency: MANIFEST vs raw JSONL

MANIFEST event indices were cross-checked against raw JSONL position counts (1-based, inclusive of all event kinds):

- task1: MANIFEST cites #6 (scala-cli --version), #12 (Hello.scala write), #16/#17 (scala-cli run Hello.scala / SCALA_OK) — all confirmed against raw JSONL.
- task3: MANIFEST cites #6/#7 (compile error run/observation), #8/#9 (sed fix/confirmation), #10/#11 (2+3*4 run/14), #12/#13 ((2+3)*4 run/20), #14/#15 (10-3-2 run/5) — all confirmed against raw JSONL.

CONSISTENT AND TRACEABLE.

Minor flag: 10-02-RUN-NOTES.md task-level event lists for task1 and task3 are off-by-one relative to the raw JSONL (e.g., RUN-NOTES says "event #5: scala-cli --version" for task1, but actual JSONL position is #6). The RUN-NOTES final summary section correctly uses the MANIFEST-consistent numbers (e.g., "task3 event #6, exit 1" for the compile error). The RUN-NOTES is a scratchpad, not a committed canonical artifact. The MANIFEST (the committed canonical artifact) is correct throughout. This is NOT a fabrication; it is an internal numbering drift in the non-canonical RUN-NOTES only.

---

## Anti-Patterns Scan

No stub patterns, placeholder content, or fabricated events found across all verified artifacts. All ObservationEvents contain genuine terminal output (compile messages, program output, sed confirmation). All ActionEvents contain real bash commands. The agent's multi-attempt write process in task2 (Python-flavoured intermediate attempts self-corrected to clean Scala 3) is disclosed in MANIFEST Deviations §3 and in RUN-NOTES. No concealment.

---

## Human Verification Items

None required for the automated criteria. The canonical test outcomes (14/20/5), compile error content, and sed fix are directly readable in the JSONL and independently re-runnable against the committed Calc.scala. The host re-run (test-output.txt) provides additional confirmation.

---

## Gaps Summary

No gaps. All five success criteria are satisfied by direct evidence in the committed and live artifacts.

---

_Verified: 2026-06-01T07:30:00Z_
_Verifier: Claude Sonnet 4.6 (gsd-verifier)_
