---
phase: 17-arm-c-orig-full-plan-capture
plan: "17"
subsystem: study-capture
tags: [openHands, qwen-35b, fsharp, scala, rust, gsd, diagnostic, capture]
requires:
  - phase: 16-fsharp-scala-gsd-mechanical-arm-c
    provides: Arm C-mech results (the FAIL→PASS contrast)
provides:
  - Arm C-orig captures (GSD plan handed over WITH code) — F# PASS, Scala PASS, Rust incomplete
  - The F# FAIL→PASS flip that pinpoints DSL-authorship as the OOD bottleneck
duration: ~25min
completed: 2026-06-04
---

# Phase 17: Arm C-orig (full GSD plan WITH code) — Summary

**Fed the GSD plans to the 35B AS-IS (reference code embedded) — the opposite of Arm C-mech.
Result: F# flips FAIL→PASS, Scala PASS, Rust incomplete (OpenHands CLI bug). The flip pinpoints
the OOD bottleneck: the 35B fails F# because it can't author FsLex/FsYacc DSL syntax, NOT because
it can't follow a plan. Handing over the code = transcription, not capability — which is exactly
why Arm C-orig is study-invalid as a measurement.**

## What happened
1. Built Arm C-orig prompts = control block + GSD `01-PLAN.md` objective+tasks WITH all fenced
   code (`.fsl`/`.fsy`/`.fsproj`/`main.rs`/`Calc.scala`); executor-only `<context>` stripped.
2. Captured the 35B (single invocation each, isolated empty workspaces).
3. Scored with the fixed Phase 13 extractor; ground truth host-verified.

## Result (canonical pass)

| Example | Arm C-mech (no code) | **Arm C-orig (with code)** |
|---------|----------------------|----------------------------|
| F# (OOD) | FAIL (37 error-fix cycles, no build) | **PASS 3/3** (4 error-fix cycles) |
| Scala (in-dist) | PASS | **PASS** (0 error-fix cycles) |
| Rust (in-dist) | PASS | **INCOMPLETE** — OpenHands `MissingStyle` CLI bug (2 attempts), harness not model |

## Key finding
**F# FAIL→PASS when code is handed over** isolates the bottleneck: it is *DSL-syntax authorship*,
not planning. Give the 35B the literal `.fsl`/`.fsy` to transcribe → builds + passes with 4 minor
heredoc fixes (vs 37 fruitless cycles writing it itself). Sharpens "distribution, not size": for
an OOD DSL, no amount of *planning* (even GSD-grade, code-free) closes the gap — only handing over
the *code* does, and that's transcription.

## Honesty notes
- Rust = INCOMPLETE due to a reproducible OpenHands TUI color-parsing bug (`ConversationErrorEvent
  code=MissingStyle`) triggered by the embedded `awk '/^\[dependencies\]/...'` verify command;
  agent never left scaffolding. Disclosed, NOT scored. Least-informative cell anyway.
- n=1, not counterbalanced; timing not comparable. Arm C-orig spoon-feeds the answer → diagnostic
  only, not a capability measure. Honesty gates PASS; runs are the runs (no cherry-pick).

## Next options
- Publish: add 부록 D §6.9 (Arm C-orig + the 4-condition table) — completes the Arm-A/B/C-mech/C-orig matrix.
- Optional: report the OpenHands `MissingStyle` rendering bug upstream (awk with `\[...\]` in output).
