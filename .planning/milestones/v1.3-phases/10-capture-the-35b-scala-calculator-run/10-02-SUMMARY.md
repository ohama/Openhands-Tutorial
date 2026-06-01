# 10-02 SUMMARY — Execute the 35B Scala Calculator Capture

**Status:** COMPLETE — honest unaided success captured.
**Date:** 2026-06-01. Model: `openai/qwen-35b` (litellm proxy), OpenHands 1.16.0 --headless --json --yolo, scala-cli 1.14.0 / Scala 3.8.3 / JDK 17.

## Outcome (one line)

The 35B wrote an **idiomatic Scala 3** recursive-descent arithmetic calculator **unaided on attempt 1**, hit **one genuine compile error** (a `private` member accessed from `@main`), **self-corrected it** with its own `sed`, and **all three canonical tests passed: `2+3*4 → 14`, `(2+3)*4 → 20`, `10-3-2 → 5`.** Scaffold fallback never invoked.

## Per-task results

| Task | TA | Wall-clock | Outcome |
|------|----|-----------|---------|
| task1-scaffold | 4 | ~31s | PASS — agent verified scala-cli itself + ran trivial `@main` Scala 3 file → `SCALA_OK` (SCAL-01 self-setup) |
| task2-write-calc (unaided) | 20 | ~2m55s | UNAIDED SUCCESS — 70-line idiomatic Scala 3 calc (correct precedence + left-assoc); did-write-calc-unaided=YES |
| task3-buildtest | 6 | ~30s | PASS — 1 self-corrected compile error (`private pos`), then 14/20/5 all pass |

## Requirements evidence

- **SCAL-01** (unaided-first + self-setup): task1 events #5 (`scala-cli --version`) / #15 (`scala-cli run`), task2 wrote Calc.scala unaided with no provided source. PASS.
- **SCAL-02** (source=agent, zero manual edits): honesty-gate preview = 36 ActionEvents across all JSONLs, 0 non-agent. The only fix (sed on Calc.scala) was the agent's own ActionEvent (task3 #7). Scaffold not invoked. PASS.
- **SCAL-03** (canonical test outcome + error/self-correction traceable): all three results are real terminal ObservationEvents (task3 #10/#12/#14); the compile error (#6) → agent sed fix (#7) → success is fully traceable. PASS.

## Notable observations (for the 7부 chapter / manifest)

- **Scala 3 unprompted and consistent** — `@main def`, significant-indentation `class …:`, `if/then`, `while/do`, `match`. No Scala 2 `object extends App` slip (a predicted failure mode that did NOT occur).
- **Correct left-associativity** — `10-3-2 → 5` via `while … do { left = left - right }` loops, avoiding the naive right-recursive `→ 9` bug the research anticipated.
- **The genuine error** was a Scala access-modifier mistake (`private var pos` accessed externally) — a clean, teachable, in-distribution error-and-fix, not a deep capability failure.
- Harmless `file_editor` AgentErrorEvent (task3 #2) recovered to bash — same as v1.2.
- This completes the "calculator trilogy" thesis: the 35B that needed a scaffolded FsLex lexer in v1 wrote the same calculator unaided in Scala (more in-distribution).

## Honesty

Zero manual edits to any agent file. No fabricated output. Scaffold staged but never triggered. The legacy `~14–32s/call` figure is a v1 prediction and is NOT cited as a measurement; only real per-task wall-clock recorded. Full evidence in `10-02-RUN-NOTES.md`. Live JSONLs in `oh-workdir-scala/` (gitignored) — 10-03 commits them to `captured-scala/`.

## Next

10-03: mechanical `source=agent` honesty gate → CAPTURE-MANIFEST.md + final-source snapshot + host re-run → commit `captured-scala/` (closes the Phase 10 capture gate).
