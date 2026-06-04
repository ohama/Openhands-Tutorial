# Phase 17 — Arm C-orig (full GSD plan WITH code) — CAPTURE-MANIFEST

Capture date: 2026-06-04
Study: v1.4 Planning Comparison — Arm C-orig diagnostic (GSD plan handed over AS-IS, with code)
Author: Claude (Phase 17 execution)

---

## What this arm is

**Arm C-orig** = the GSD plan converted to an OpenHands prompt **AS-IS, with the reference
source code left in** — the exact opposite of the Arm C-mech strip. The prompt = the study
control block (byte-identical) + the GSD `01-PLAN.md` objective+tasks **including every
fenced code block** (the full `.fsl`/`.fsy`/`.fsproj`/`main.rs`/`Calc.scala`). The 35B is
told to transcribe the given files via bash heredoc and run the tests.

**Diagnostic question (NOT a capability measure):** when the answer code is handed over, does
F# flip FAIL→PASS — proving the OOD bottleneck is *writing the DSL syntax*, not *following a
plan*? And it demonstrates concretely **why Arm C-orig is study-invalid**: it spoon-feeds the
answer, so a pass measures transcription, not capability.

---

## Version Block / Run Conditions

| Field | Value |
|-------|-------|
| OpenHands CLI | 1.16.0 · Model `openai/qwen-35b` (litellm 127.0.0.1:4000) |
| Agent / Flags | CodeActAgent · `--headless --json --yolo --override-with-envs` |
| Toolchain | .NET 10 · scala-cli 1.14.0/Scala 3.8.3/JDK 17 · rustc 1.95.0 |
| Capture | 2026-06-04, single invocation per example, n=1, isolated empty workspaces |
| Control block | byte-identical to the Phase 12/13 canonical block per example |

**Caveat (DISCLOSED):** n=1 solo captures, not counterbalanced vs Phase 13 (n=3). Timing not
comparable across arms. This arm **hands the agent the answer code** — it is a diagnostic, not
a capability measurement.

**Metrics tool:** scored with the FIXED Phase 13 `metrics_extractor.py`; ground truth confirmed
by fresh host re-runs.

---

## Results (fixed detector + host ground-truth)

| Metric | Rust | F# | Scala |
|--------|------|----|-------|
| Total events | — | 174 | 37 |
| TerminalActions | — | 77 | 11 |
| Wall clock (s) | — | 495.62 | 99.9 |
| Error-fix cycles | — | 4 | 0 |
| TaskTracker obs/act | — | 4/4 | 5/6 |
| **Canonical** | **INCOMPLETE** (harness bug) | **PASS 3/3** (14/20/5 @#151) | **PASS 3/3** (14/20/5 @#23) |
| Honesty gate | PASS (on events that ran) | PASS | PASS |

**Rust — INCOMPLETE (harness bug, not a task/model outcome):** two capture attempts both
terminated early with OpenHands `ConversationErrorEvent code=MissingStyle` ("failed to get
style 'dependencies\\'; unable to parse as color") — an out-of-band OpenHands CLI
color-parsing bug triggered while rendering the embedded GSD verify command
`awk '/^\[dependencies\]/{...}' Cargo.toml`. The agent never progressed past `cargo init`
scaffolding (main.rs left at the 3-line default). NOT scored. Rust is the least informative
Arm C-orig cell anyway (Rust passes code-free in Arm C-mech). Re-run was legitimate (no task
outcome was produced); both attempts hit the same deterministic rendering bug.

**F# / Scala host-confirmed:** `dotnet run`/`scala-cli run` reproduce 14/20/5 from the
agent-written `final-source/`.

---

## THE KEY RESULT — F# flips FAIL→PASS when code is handed over

| F# condition | code given? | result | error-fix cycles |
|--------------|:-----------:|--------|:----------------:|
| Arm C-mech (Phase 16) | ✗ (pitfall guidance only) | **FAIL** (build never succeeds) | 37 (thrashing) |
| **Arm C-orig (this phase)** | ✓ (full `.fsl`/`.fsy`/`.fsproj`) | **PASS 3/3** | 4 (minor heredoc fixes) |

This isolates the OOD bottleneck precisely: the 35B fails the F# FsLex/FsYacc task **not**
because it can't follow a plan or doesn't know the algorithm — but because it **cannot author
the FsLex/FsYacc DSL syntax**. Hand it the exact `.fsl`/`.fsy` text to transcribe, and it
builds and passes with only 4 small heredoc-transcription fixes (vs 37 fruitless cycles when it
had to write the DSL itself). The bottleneck is *DSL authorship*, confirmed.

---

## Full 4-condition comparison (canonical pass)

| Example | Arm A — Claude plan (n=3) | Arm B — self-plan (n=3) | Arm C-mech — GSD, no code (n=1) | Arm C-orig — GSD + code (n=1) |
|---------|---------------------------|--------------------------|---------------------------------|-------------------------------|
| F# (OOD) | 1/3 PASS | 0/3 PASS | **FAIL** | **PASS** |
| Scala (in-dist) | 3/3 PASS | 2/3 + 1 PARTIAL | PASS | PASS |
| Rust (in-dist) | 3/3 PASS | 3/3 PASS | PASS | n/a (harness bug) |

Reading:
- **In-distribution (Rust, Scala):** every condition succeeds — even code-free self-plan (Arm B).
  The expert plan / code adds nothing observable; the model already has the capability.
- **OOD (F#):** the dividing line is **code**, not plan quality. Arm A's *one* lucky pass and
  all the no-code conditions (Arm B 0/3, Arm C-mech FAIL) confirm the model cannot reliably
  emit FsLex/FsYacc. Only Arm C-orig — which hands over the literal DSL source — passes.
- → **"distribution, not size" sharpened:** for an OOD DSL, no amount of *planning* (even
  GSD-grade, failure-mode-aware, code-free) closes the gap; only handing over the *code* does —
  which is transcription, not capability.

---

## RESULT

Arm C-orig: **F# PASS, Scala PASS** (Rust incomplete — OpenHands CLI bug). Handing the 35B the
reference code flips the OOD F# task FAIL→PASS, pinpointing DSL-syntax authorship (not planning)
as the bottleneck — and concretely showing why Arm C-orig is a diagnostic, not a capability
measurement (it spoon-feeds the answer). Honesty gates PASS; first/second runs are the runs;
Rust incompleteness disclosed as a harness bug, not a result.
