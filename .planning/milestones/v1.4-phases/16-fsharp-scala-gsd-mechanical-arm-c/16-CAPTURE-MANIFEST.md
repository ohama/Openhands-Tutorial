# Phase 16 — Arm C (mechanical) F# + Scala Capture — CAPTURE-MANIFEST

Capture date: 2026-06-04
Study: v1.4 Planning Comparison — Arm C (GSD mechanical) follow-up, F#/Scala extension of Phase 15 (Rust)
Author: Claude (Phase 16 execution)

---

## EVENT-NUMBERING CONVENTION

All event numbers are **1-based** (JSONL line N = event #N), matching the Phase 12/13 convention.

---

## What this arm is

**Arm C (mechanical)** = an expert plan produced by the GSD multi-agent pipeline (gsd-phase-researcher → gsd-planner → gsd-plan-checker), then stripped to a **code-free** single-session prompt: GSD's research-derived failure-mode guidance is kept as prose requirements, but **all source code, literal answers, and API/DSL syntax are removed** so the 35B writes everything itself. This phase applies it to F# (FsLex/FsYacc) and Scala 3, extending the Rust capture in Phase 15.

Probes: **does an expert plan that names the failure modes but withholds code help the 35B on an OOD task (F#) vs an in-distribution task (Scala)?**

For each example the GSD plan (`planning-artifact/01-PLAN.md`, with embedded reference code) was verified PASS by gsd-plan-checker, then converted to the code-free `oh-prompt.txt` (`gsd-mechanical-plan` rules; control-block symmetry proven — see `PROMPT-DIFF.txt`, both PASS).

---

## Version Block

| Field | Value |
|-------|-------|
| OpenHands CLI | 1.16.0 |
| Model | `openai/qwen-35b` via litellm proxy (127.0.0.1:4000) |
| Agent | CodeActAgent (default headless) |
| Flags | `--headless --json --yolo --override-with-envs` |
| Toolchain | .NET 10 (F#) · scala-cli 1.14.0 + Scala 3.8.3 + JDK 17 (Scala) |
| Capture date | 2026-06-04 |

---

## Run Conditions

| Field | F# (arm-c) | Scala (arm-c) |
|-------|-----------|----------------|
| Workspace | `oh-workdir-planning/arm-c/fsharp` | `oh-workdir-planning/arm-c/scala` |
| Pre-run workspace | Empty (verified) | Empty (verified) |
| Clock start → settle | 15:22:01 → 15:42:17 | 15:42:17 → 15:46:30 |
| Wall clock (derived) | 1211.51s | 248.15s |
| Invocation | single CodeActAgent call, n=1 | single CodeActAgent call, n=1 |
| Run order | F# first, then Scala (sequential, same proxy — not restarted) | — |

**Counterbalance / cache caveat (DISCLOSED):** solo n=1 follow-up captures on 2026-06-04, run sequentially against a non-restarted externally-managed proxy. NOT counterbalanced against the Phase 13 Arm A/B runs (2026-06-02, n=3). **Wall-clock / LLM-gap values must NOT be compared across arms** — feasibility/qualitative capture only.

**Control-block symmetry:** both `PROMPT-DIFF.txt` files end `CONTROL-BLOCK SYMMETRY: PASS` — each Arm C prompt's control block is byte-identical to the Phase 13 canonical control block for that example.

---

## Metrics-tool note (honesty — detector fix applied)

The first extraction used the Phase 12 `metrics_extractor.py`, whose canonical detector uses buggy first-substring-match semantics; it **mis-scored Scala as FAIL**. Per the standing rule (fix the tool, don't trust/hand-edit outputs), all three Arm C captures (F#, Scala, and the Phase 15 Rust re-verify) were **re-scored with the FIXED Phase 13 `metrics_extractor.py`** (`_is_run_command` + any-successful-run semantics, `b7a74b9`). Ground truth was independently confirmed by fresh host re-runs (Scala 3/3 PASS; F# build fails). The numbers below are from the fixed detector.

---

## Honesty Gate

**Gate: PASS on both JSONLs.** No manual edits to any agent-written file. First run IS the run (no re-runs, no cherry-pick, no hand-fixing source to fake a pass).

| Arm | ActionEvents | Non-agent | Result |
|-----|-------------:|----------:|--------|
| F# arm-c | (all) | 0 | PASS |
| Scala arm-c | (all) | 0 | PASS |

---

## Per-Arm Results (fixed detector)

| Metric | F# (arm-c) | Scala (arm-c) |
|--------|-----------:|--------------:|
| Total events | 464 | 80 |
| TerminalActions | 213 | 37 |
| Wall clock (derived, s) | 1211.51 | 248.15 |
| Avg LLM-call gap (s) | 3.63 | 4.89 |
| Error-fix cycles | 37 | 2 |
| TaskTracker obs / act | 3 / 4 | 0 / 0 |
| usage_present | False | False |
| **Canonical tests** | **FAIL 0/3** | **PASS 3/3** (14 / 20 / 5 at events #75 / #77 / #79) |
| Honesty gate | PASS | PASS |

**F# failure is genuine (host-confirmed):** `dotnet build` fails at `Lexer.fsl(6): parse error` — the 35B's hand-written FsLex `.fsl` lexer-definition has invalid DSL syntax that `fslex.dll` cannot parse, so no binary is produced. 37 in-session error-fix cycles did not recover. This is the OOD-DSL failure mode (the 35B cannot write FsLex syntax unaided), NOT a detector artifact.

**Scala success (host-confirmed):** agent wrote an idiomatic Scala 3 recursive-descent calculator (token list + `class Parser` with `while`-loop left-fold `expression`/`term`/`factor`); fresh host re-run prints 14 / 20 / 5, all exit 0.

---

## Comparison with Phase 13 Arm A/B (canonical pass)

| Example | Arm A — Claude plan (n=3) | Arm B — self-plan (n=3) | **Arm C-mech — GSD code-free (n=1)** |
|---------|---------------------------|--------------------------|--------------------------------------|
| F# (OOD) | 1/3 PASS | 0/3 PASS | **FAIL (0/1)** |
| Scala (in-dist) | 3/3 PASS | 2/3 + 1 PARTIAL | **PASS (1/1)** |
| Rust (in-dist) | 3/3 PASS | 3/3 PASS | **PASS (1/1)** — Phase 15 |

Footprint vs Phase 13 medians (qualitative; timing not comparable):

| Example | metric | Arm A med | Arm B med | Arm C-mech (n=1) |
|---------|--------|----------:|----------:|-----------------:|
| F# | TerminalActions | 80 | 74 | **213** |
| F# | error-fix cycles | 21 | 11 | **37** |
| Scala | TerminalActions | 37 | 13 | **37** |
| Scala | error-fix cycles | 6 | 2 | **2** |

→ On the OOD F# task the code-free expert plan did NOT rescue the 35B — it **thrashed harder** than either Phase 13 arm (213 terminal actions, 37 error-fix cycles) and still could not produce valid FsLex syntax. On in-distribution Scala the pitfall guidance was sufficient: clean PASS with a footprint comparable to Arm A.

---

## RESULT

**Arm C (mechanical): Scala PASS, F# FAIL** (Rust PASS in Phase 15).

The "distribution, not size" thesis holds on the Arm C axis: an expert plan that names the failure modes but withholds code helps the 35B succeed on **in-distribution** tasks (Rust, Scala) but **cannot** carry it through the **OOD** FsLex/FsYacc DSL — the model simply cannot emit the `.fsl` grammar syntax unaided, no matter how thorough the prose guidance. n=1 feasibility captures; honesty gates PASS; ground truth host-verified.
