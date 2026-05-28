---
phase: 06-capture-the-122b-openhands-run
verified: 2026-05-28T00:00:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 6: Capture the 122B OpenHands Run — Verification Report

**Phase Goal:** A real, honest 122B OpenHands run of the F# FsLex/FsYacc calculator captured on disk (per-task JSONL), `.fsl` lexer attempted UNAIDED first, real outcome (incl. genuine agent error-and-fix) recorded without fabrication.
**Verified:** 2026-05-28
**Status:** passed
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Per-task JSONL committed in captured-122b/logs/ with non-empty ActionEvent + ObservationEvent records | VERIFIED | 5 JSONL files: task1(A=21,O=21), task2(A=7,O=7), task3(A=39,O=39), task4(A=48,O=48), task5(A=40,O=40) — all non-empty, all git-tracked |
| 2 | task2-lexer-unaided.jsonl confirms lexer submitted UNAIDED (no lexer body in prompt, agent wrote it itself) | VERIFIED | Event[0] llm_message content confirmed: token names only, behavioral requirements only, zero lexer body/API hints. Grep on prompt file: 0 matches for `rule tokenize = parse`, `LexemeString`, `%%`, `['0'-'9']`. Agent wrote via event[9] cat heredoc. |
| 3 | CAPTURE-MANIFEST.md records did-lexer-unaided (YES) and is cross-checked against task2 events | VERIFIED | CAPTURE-MANIFEST did-lexer-unaided=YES, unaided-attempts=1. Cross-check: task2 event[9] TerminalAction writes Lexer.fsl with `rule tokenize = parse` (correct FsLex format, no `%%`). Event[12] ObservationEvent confirms file content. |
| 4 | Final outcomes 14/20/5 traceable to terminal observation in task5 JSONL AND test-output.txt | VERIFIED | task5 events [75]/[76] → `dotnet run -- "2+3*4"` exit=0 content="14"; [77]/[78] → "(2+3)*4" exit=0 "20"; [79]/[80] → "10-3-2" exit=0 "5". test-output.txt: all-pass=YES (14,20,5). Host re-run confirmed independently by verifier. |
| 5 | CAPTURE-MANIFEST records invocation, lexer outcome, deviations, parallel to v1 manifest | VERIFIED | Manifest has: Run Metadata, Lexer Outcome (RUN122-01/02), Error-and-Fix Record (RUN122-03), Test Results, Timing Summary (CMP-01), Comparison Hook, Artifact-to-Requirement Map, Deviations section |

**Score:** 5/5 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `captured-122b/logs/task1-scaffold.jsonl` | Non-empty, A+O events | VERIFIED | 88,356 bytes; A=21 O=21 TA=20; FinishAction=True |
| `captured-122b/logs/task2-lexer-unaided.jsonl` | Unaided proof, A+O events | VERIFIED | 36,214 bytes; A=7 O=7 TA=7; 16 total events (incl. 2 MessageEvents) |
| `captured-122b/logs/task3-parser.jsonl` | Non-empty, A+O events | VERIFIED | 140,824 bytes; A=39 O=39 TA=37; FinishAction=True |
| `captured-122b/logs/task4-evaluator.jsonl` | Non-empty, A+O events | VERIFIED | 216,491 bytes; A=48 O=48 TA=47 |
| `captured-122b/logs/task5-buildtest.jsonl` | Non-empty, 3-case outcomes | VERIFIED | 158,425 bytes; A=40 O=40 TA=39; outcomes at events 76/78/80 |
| `captured-122b/CAPTURE-MANIFEST.md` | did-lexer-unaided field | VERIFIED | Contains did-lexer-unaided: YES, all RUN122 fields, Phase-7 fields |
| `captured-122b/test-output.txt` | Fresh host re-run, 3 cases | VERIFIED | all-pass: YES (14, 20, 5); dotnet build 0 errors |
| `captured-122b/final-source/Lexer.fsl` | Agent's final state (`new string(lexbuf.Lexeme)`) | VERIFIED | Line 10: `| ['0'-'9']+ { INT (int (new string(lexbuf.Lexeme))) }` — bit-for-bit matches oh-workdir-122b/calc/Lexer.fsl |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| task2-lexer-unaided.jsonl event[9] | calc/Lexer.fsl on disk | agent TerminalAction cat heredoc | VERIFIED | Command writes `rule tokenize = parse` FsLex file; event[12] ObservationEvent confirms content; `did-lexer-unaided=YES` correct |
| task5-buildtest.jsonl ObservationEvents | Outputs 14/20/5 | events [76]/[78]/[80] TerminalObservation | VERIFIED | exit_code=0, content.text="14"/"20"/"5" respectively |
| CAPTURE-MANIFEST.md claims | captured-122b/logs/*.jsonl events | event-range citations (e.g., events 12–74 for error-fix) | VERIFIED | Manifest cites specific event indices; spot-checked event[71] cat heredoc with `new string(lexbuf.Lexeme)` at correct position |
| captured-122b/ committed tree | git index | git ls-files | VERIFIED | 17 files tracked under captured-122b/; oh-workdir-122b/ shows 0 tracked files |

---

### Critical Honesty Checks

#### Error-and-Fix: Agent's Own Work

All 5 JSONL files were checked for ActionEvent `source` field:
- task1-scaffold.jsonl: 21/21 ActionEvents source=agent
- task2-lexer-unaided.jsonl: 7/7 ActionEvents source=agent
- task3-parser.jsonl: 39/39 ActionEvents source=agent
- task4-evaluator.jsonl: 48/48 ActionEvents source=agent
- task5-buildtest.jsonl: 40/40 ActionEvents source=agent

**Zero non-agent ActionEvents found across all 5 JSONL files.** The 8 fix iterations in task5 (events 12–74) are entirely agent-driven. No human edit traces.

The error-fix sequence (observed independently, not from SUMMARY claims):
- Event[11]: `dotnet build` → exit=1 (FS0001: `as s` char array error)
- Events [13]/[15]/[17]: agent reads generated Lexer.fs, rewrites Lexer.fsl, rebuilds → exit=1
- Events [19]/[21]/[23]: agent inspects generated code, spots issue, tries Lexing namespace variant → exit=1
- Events [25]: ThinkAction (thought logged)
- Events [27]/[29]: rewrites with `Lexing.matched lexbuf` → exit=1
- Events [37]/[39]/[41]/[43]: inspects generated .fs output, tries different Lexing.* calls → exit=1
- Events [47]/[49]: tries FSharp.Text.Lexing namespace open → exit=1
- Events [53]/[55]: tries matchedText → exit=1
- Events [57]/[59]: tries full namespace matchedText → exit=1
- Events [61]/[63]: rewrites → exit=0 (build success) BUT
- Events [65]/[66]: `dotnet run -- "2+3*4"` → exit=134 (runtime crash: `lexbuf.ToString()` returns type name)
- Events [67]/[69]: tries `lexbuf.Lexeme` (char array) → exit=1 (FS0193: can't convert char[] to int)
- Events [71]/[73]: final rewrite with `new string(lexbuf.Lexeme)` → exit=0
- Events [75]/[76]: `dotnet run -- "2+3*4"` → exit=0, output="14"

#### Unaided-First Confirmation

The task2 prompt (recovered from event[0] llm_message content) contains:
- Token names: INT, PLUS, MINUS, STAR, SLASH, LPAREN, RPAREN, EOF — named for parser agreement
- Rule name `tokenize` named (required for parser calls)
- Behavioral requirements (skip whitespace, match digits, etc.) — behavior only, no code
- ZERO: no `rule tokenize = parse`, no LexemeString, no `%%`, no pattern examples, no API names

The agent produced a structurally correct FsLex file on first attempt (rule/parse format, no `%%` confusion). The initial lexer had a recoverable API bug (`int s` on char array) that the agent self-corrected in task5.

#### Lexer.fsl Bit-For-Bit Match

`diff oh-workdir-122b/calc/Lexer.fsl captured-122b/final-source/Lexer.fsl` → files identical. The `new string(lexbuf.Lexeme)` line is present in both.

#### Host Re-Check (Verifier-Run, Independent)

```
dotnet run --project /Users/ohama/projs/OpenHandsTests/oh-workdir-122b/calc -- "2+3*4"   → 14
dotnet run --project /Users/ohama/projs/OpenHandsTests/oh-workdir-122b/calc -- "(2+3)*4" → 20
dotnet run --project /Users/ohama/projs/OpenHandsTests/oh-workdir-122b/calc -- "10-3-2"  → 5
```
All three correct. Build 0 errors.

#### Gitignore Confirmation

`git check-ignore oh-workdir-122b` → prints `oh-workdir-122b` (ignored).
`git ls-files oh-workdir-122b/` → 0 files tracked. Only `captured-122b/` is in the git index.

#### Provenance

CAPTURE-MANIFEST Provenance Note honestly states: tasks 1–4 ran outside this recording conversation (12:32–13:10), task5 ran at ~13:18. Timestamps from JSONL confirm:
- task1: 12:32:31–12:35:19
- task2: 12:43:14–12:44:12
- task3: 12:53:59–12:58:12
- task4: 13:04:21–13:10:24
- task5: 13:18:35–13:25:04

The provenance is honest and matches the JSONL evidence.

---

### Anti-Patterns Found

None detected that affect goal achievement.

Minor discrepancy (informational): CAPTURE-MANIFEST attributes a ThinkAction quote ("lexbuf.Lexeme returns a char array…") to "event 71", but event[71] in the JSONL is the final TerminalAction write (not a ThinkAction). Event[25] is the only ThinkAction in task5. The quote is accurate in substance (the agent did reach this conclusion), but the event citation is slightly imprecise. This is a documentation detail, not a fabrication.

---

### Deviations (Confirmed Honest)

1. No task6-fix.jsonl — agent self-completed in task5; disclosed in manifest.
2. Lexer.fsl modified in task3/task4 by agent initiative — honestly disclosed in manifest Deviations section.
3. No FinishAction in tasks 2, 4, 5 — honestly disclosed; consistent with natural stop behavior.
4. Zero manual edits to agent files — confirmed by source=agent on all ActionEvents.

---

## Summary

Phase 6 achieved its goal. All five success criteria are met from committed evidence:

1. Per-task JSONL committed and non-empty with A+O events (5 files, all in git).
2. Unaided-first confirmed from task2 JSONL: prompt contained no lexer body; agent wrote `rule tokenize = parse` FsLex file on first attempt.
3. CAPTURE-MANIFEST records did-lexer-unaided=YES with cross-referenced JSONL event citations.
4. Outcomes 14/20/5 traced to task5 events [76]/[78]/[80] and confirmed by independent verifier host re-run.
5. CAPTURE-MANIFEST has all required fields (invocation, lexer outcome, error-fix with 8-iteration table, timing, comparison hooks, deviations) parallel to v1 manifest structure.

The honesty criteria are satisfied: every ActionEvent across all 5 JSONL files has source=agent, confirming the error-and-fix sequence is entirely the agent's own work with no human interventions.

---

_Verified: 2026-05-28_
_Verifier: Claude (gsd-verifier)_
