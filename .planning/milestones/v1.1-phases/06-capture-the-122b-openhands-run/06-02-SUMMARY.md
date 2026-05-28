---
phase: 06-capture-the-122b-openhands-run
plan: 02
subsystem: capture/execution
tags: [openhands, qwen-122b, jsonl-capture, fsharp, fslexyyacc, headless-run, capture-execution]

# Dependency graph
requires:
  - phase: 06-capture-the-122b-openhands-run/01
    provides: 6 task-prompt files in task-prompts-122b/, gitignored oh-workdir-122b/, confirmed qwen-122b alias on litellm @ 127.0.0.1:4000

provides:
  - "oh-workdir-122b/logs/task1-scaffold.jsonl through task5-buildtest.jsonl — 5 per-task JSONL files from the 122B run"
  - "oh-workdir-122b/calc/ — final F# project state after task5 (later copied verbatim into captured-122b/final-source/ by 06-03)"
  - "Empirical confirmation that 122B wrote the FsLex lexer UNAIDED on first attempt (no scaffold fallback needed)"

affects: [06-03 (consumes the JSONL + final-source for verification and manifest writing)]

retro_written: true
retro_note: "This SUMMARY was written 2026-05-28 during /gsd:complete-milestone v1.1 to close audit tech-debt item TD-1. The actual execution work and evidence pre-dated this file — see Evidence section below for where the raw 06-02 outputs live and how to verify them independently."

tech-stack:
  added: []
  patterns:
    - "OpenHands 1.16 headless CLI with --override-with-envs (LLM_MODEL=openai/qwen-122b, LLM_BASE_URL=http://127.0.0.1:4000/v1)"
    - "Per-task isolated invocations: one openhands --headless --json --yolo invocation per task prompt file"
    - "LocalWorkspace inside oh-workdir-122b/ (gitignored capture sandbox)"

key-files:
  created:
    - "oh-workdir-122b/logs/task1-scaffold.jsonl"
    - "oh-workdir-122b/logs/task2-lexer-unaided.jsonl"
    - "oh-workdir-122b/logs/task3-parser.jsonl"
    - "oh-workdir-122b/logs/task4-evaluator.jsonl"
    - "oh-workdir-122b/logs/task5-buildtest.jsonl"
    - "oh-workdir-122b/calc/Lexer.fsl (agent-written, final form)"
    - "oh-workdir-122b/calc/Parser.fsy (agent-written)"
    - "oh-workdir-122b/calc/Program.fs (agent-written)"
    - "oh-workdir-122b/calc/calc.fsproj (provided by task1 scaffold)"
  modified: []

key-decisions:
  - "did-lexer-unaided: YES — task2 used task2-lexer-unaided.txt (no provided lexer body); 122B wrote structurally valid FsLex on first attempt. Scaffold fallback (task2-lexer-scaffold.txt) was NEVER triggered."
  - "Zero manual edits to any agent-written file between tasks — confirmed by 06-03's check that every ActionEvent has source=agent across all 5 JSONLs"
  - "task6-fix.txt was not invoked — agent self-completed in task5 (14/20/5 all passed in task5-buildtest.jsonl events 76/78/80)"
---

# 06-02 Capture Execution — Retroactive Summary

This summary documents the 06-02 plan's execution. It was written **retroactively during v1.1 milestone completion** to close audit tech-debt item **TD-1** (the original execution did not produce a SUMMARY.md artifact, though the captured evidence was committed in full and consumed downstream by plan 06-03).

## What 06-02 Did

Executed the 122B OpenHands run end-to-end per `06-02-PLAN.md`:

1. **task1 scaffold** — submitted `task1-scaffold.txt` to OpenHands with `LLM_MODEL=openai/qwen-122b`. Agent created the `calc/` project (calc.fsproj from the provided scaffold + initial F# files).
2. **task2 lexer (UNAIDED FIRST)** — submitted `task2-lexer-unaided.txt` (no provided lexer source, no FsLex API hints). Agent wrote a structurally valid `Lexer.fsl` using `rule tokenize = parse` (FsLex format, not FsYacc's `%%`). **Scaffold fallback was not needed.**
3. **task3 parser** — submitted `task3-parser.txt`. Agent wrote `Parser.fsy` with operator precedence declarations and the grammar.
4. **task4 evaluator** — submitted `task4-evaluator.txt`. Agent wrote `Program.fs` with the host code (parse + evaluate + print).
5. **task5 build + test** — submitted `task5-buildtest.txt`. Agent built the project, hit FsLex API errors on `lexbuf.Lexeme`, and self-corrected through **9 iterations** (events 12–74 in `task5-buildtest.jsonl`): `int s` → `Lexing.matched` → `matchedText` → `lexbuf.ToString()` → `lexbuf.Lexeme` → `new string(lexbuf.Lexeme)` (final working form). Then ran the 3 test cases — `2+3*4=14`, `(2+3)*4=20`, `10-3-2=5` all PASS (events 76/78/80).

All 5 invocations ran in **--yolo** mode with `--override-with-envs`. No human edited any file between tasks.

## Outcome

| Task | JSONL | Outcome | Notes |
|------|-------|---------|-------|
| task1 | task1-scaffold.jsonl | ✓ project scaffolded | |
| task2 | task2-lexer-unaided.jsonl | ✓ Lexer.fsl written **unaided** | event 9 = proof artifact (the agent's first FsLex write, no scaffold) |
| task3 | task3-parser.jsonl | ✓ Parser.fsy written | |
| task4 | task4-evaluator.jsonl | ✓ Program.fs written | |
| task5 | task5-buildtest.jsonl | ✓ build PASS, 3/3 tests PASS | 9 agent-driven FsLex API fix iterations (events 12–74); zero manual edits |

**did-lexer-unaided:** YES
**final-outcome:** 14/20/5 (all three cases correct)
**manual-edits:** 0 (every ActionEvent has source=agent)
**scaffold-fallback-used:** NO

## Evidence (still on disk)

Raw 06-02 outputs are preserved in the gitignored capture sandbox and were copied into the committed archive by plan 06-03:

| Evidence | Location | Committed? |
|----------|----------|------------|
| 5 per-task JSONL logs | `oh-workdir-122b/logs/*.jsonl` (gitignored) → `captured-122b/logs/*.jsonl` (committed by 06-03) | yes (via 06-03) |
| Final F# source (4 files) | `oh-workdir-122b/calc/*` → `captured-122b/final-source/*` | yes (via 06-03) |
| Run-level human-readable summary | `captured-122b/transcript.md` | yes (via 06-03) |
| Independent host re-run output | `captured-122b/test-output.txt` | yes (via 06-03) |
| Cross-referenced manifest | `captured-122b/CAPTURE-MANIFEST.md` | yes (via 06-03) |

The capture gate closed when 06-03 verified these artifacts and wrote the manifest.

## Honesty Notes

- This file was written **after the fact** (during milestone completion); it does not record contemporaneous notes from the run itself. All factual claims here trace to either the committed JSONLs or to 06-03's verification work.
- The original 06-02-PLAN.md required a `06-02-RUN-NOTES.md` artifact that was also never created — equivalent information lives in `captured-122b/CAPTURE-MANIFEST.md` (§Timing Summary, §Error-and-Fix Record, §Deviations) and in 06-VERIFICATION.md which independently re-walked the JSONLs.
- No claim in this summary is novel; every outcome was already documented and verified before this file existed.

---

*Written: 2026-05-28 during /gsd:complete-milestone v1.1 (closes audit TD-1)*
