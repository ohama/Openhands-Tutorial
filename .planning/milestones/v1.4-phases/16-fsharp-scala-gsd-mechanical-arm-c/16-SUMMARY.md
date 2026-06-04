---
phase: 16-fsharp-scala-gsd-mechanical-arm-c
plan: "16"
subsystem: study-capture
tags: [openHands, qwen-35b, fsharp, scala, gsd, a-b-comparison, capture, planning]

requires:
  - phase: 15-arm-c-mechanical-capture
    provides: Arm C (GSD mechanical) method + Rust result
  - phase: 13-full-study-fsharp-scala-analysis
    provides: Arm A/B baseline + fixed metrics_extractor.py
provides:
  - Arm C (GSD mechanical) F# + Scala live 35B captures (n=1 each)
  - 3-arm comparison (Arm A vs B vs C-mech) across F#/Rust/Scala
affects:
  - src/appendix-d-planning-comparison.md §6 (Arm C extended to 3 languages)

key-decisions:
  - "GSD pipeline (research→plan→verify) run for F# and Scala; both plans verified PASS; converted to code-free mechanical prompts (control-block symmetry PASS)"
  - "Used the FIXED Phase 13 metrics_extractor.py after the Phase 12 version mis-scored Scala; ground truth host-verified for both"
  - "n=1 solo captures (2026-06-04), sequential, NOT counterbalanced vs Phase 13 — timing not comparable"
  - "First run IS the run: no re-runs, no cherry-pick, no hand-fix; F# failure recorded honestly"

duration: ~30min (incl. ~24min of 35B run time)
completed: 2026-06-04
---

# Phase 16: Arm C (mechanical) F# + Scala Capture — Summary

**Ran the GSD pipeline for F# and Scala, stripped both plans to code-free mechanical prompts, and captured the 35B. Result: Scala PASS 3/3 (14/20/5), F# FAIL (FsLex `.fsl` parse error, 37 error-fix cycles, no build). With Phase 15's Rust PASS, Arm C now spans all three languages — and the "distribution, not size" thesis holds on the Arm C axis.**

## What happened

1. **GSD pipeline ×2** (real agents): gsd-phase-researcher → gsd-planner → gsd-plan-checker for F# and Scala. Both plans **VERIFICATION PASSED**. (Both embed full reference code → study-invalid as-is.)
2. **Code-free mechanical conversion ×2:** stripped source/answers/API+DSL syntax, kept pitfall guidance as prose. Reused the Phase 13 control blocks → `CONTROL-BLOCK SYMMETRY: PASS` for both.
3. **Live 35B capture ×2** (single invocation each, isolated empty workspaces, sequential).
4. **Metrics** with the **fixed** Phase 13 extractor (Phase 12 version mis-scored Scala); ground truth host-verified.

## Result (canonical pass)

| Example | Arm A (n=3) | Arm B (n=3) | **Arm C-mech (n=1)** |
|---------|-------------|-------------|----------------------|
| F# (OOD) | 1/3 | 0/3 | **FAIL** |
| Scala (in-dist) | 3/3 | 2/3+P | **PASS** |
| Rust (in-dist) | 3/3 | 3/3 | **PASS** (Phase 15) |

- **F#:** build fails at `Lexer.fsl(6): parse error` — the 35B cannot emit valid FsLex DSL syntax even with detailed prose guidance; it thrashed *harder* than either Phase 13 arm (213 TerminalActions, 37 error-fix cycles vs Arm A median 80/21).
- **Scala:** clean PASS, idiomatic recursive-descent (while-loop left-fold), footprint comparable to Arm A (37 TerminalActions, 2 error-fix cycles).
- Honesty gates PASS on both; usage absent (no token metrics).

## Key finding

An expert plan that **names the failure modes but withholds code** behaves like Arm A: it helps the 35B on **in-distribution** tasks (Rust, Scala) but **cannot** carry it through the **OOD** FsLex/FsYacc DSL. The bottleneck is the model's inability to write the DSL syntax — not planning quality. **Distribution, not size — now confirmed on the Arm C (code-free expert plan) axis too.**

## Caveats (disclosed)

- n=1 solo captures, not counterbalanced vs Phase 13 (n=3); timing not comparable across arms.
- First run is THE run; no manual edits; F# failure recorded honestly (37 cycles, no recovery).
- Detector fix applied (fixed Phase 13 extractor); ground truth host-verified.

## Next options

- n>1 + counterbalanced order if a defensible quantitative Arm-C comparison is wanted.
- Document in 부록 D §6 (extend Arm C from Rust-only to all three languages).
