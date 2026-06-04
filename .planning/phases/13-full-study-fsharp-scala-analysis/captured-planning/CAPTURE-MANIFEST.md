# Phase 13 Full Study — CAPTURE-MANIFEST

Capture date: 2026-06-02 (runs) / 2026-06-04 (extractor fix + re-extraction; gate assertion)
Study: v1.4 Planning Comparison (F# + Scala full study; Rust top-up to n=3)
Author: Claude (Phase 13 execution agent)

---

## EVENT-NUMBERING CONVENTION

**All event numbers in this manifest are 1-based: JSONL line N = event #N.**
The first JSONL line is event #1. This matches metrics_extractor.py v1.4 output
(enumerate(events, start=1) throughout).

(Pitfall note: ARCHITECTURE.md uses 0-based `events.index()`; this manifest
and all extractor output use 1-based. Chapters must cite the 1-based numbers
recorded here, NOT any 0-based scratchpad positions.)

---

## Study Design

**Research question (framing rule):** "Does an expert-authored plan help the 35B
execute?" — NOT "Claude plans better." Arm A provides the agent with a complete,
Claude-authored step-by-step plan embedded in the prompt; Arm B asks the 35B to
self-plan via the task tracker and then execute. The expert-plan benefit is what
is under investigation; the planning origin (Claude vs. 35B) is the independent
variable.

**Design:**
- v1.4 A/B parallel arms across three examples: F# FsLex/FsYacc calculator,
  Scala 3 calculator, Rust HTTP server
- **Arm A:** Expert-authored Claude plan embedded in prompt (with control block)
- **Arm B:** 35B self-plans via task tracker, then executes (same control block,
  no plan supplied)
- Control-block symmetry confirmed before any invocation: PROMPT-DIFF-fsharp.txt,
  PROMPT-DIFF-scala.txt, PROMPT-DIFF-rust.txt (all end with CONTROL-BLOCK SYMMETRY: PASS)
- Single-session, one CodeActAgent invocation per (arm × rep); no per-task split
- **n = 3** for F#, Scala, and Rust (Rust run-1 = Phase-12 pilot; runs 2–3 are top-ups)

---

## Version Block

| Field | Value |
|-------|-------|
| OpenHands CLI | 1.16.0 |
| Model | `openai/qwen-35b` via litellm proxy |
| LLM_BASE_URL | `http://127.0.0.1:4000/v1` |
| Agent | CodeActAgent (default headless) |
| Flags | `--headless --json --yolo --override-with-envs` |
| Run date | 2026-06-02 |
| Extractor | metrics_extractor.py (Phase-13 patched; canonical detector fixed 2026-06-04) |

---

## Run Conditions and Counterbalanced Order

**Host toolchains (verified):** .NET 10, rustc/cargo 1.95.0, scala-cli 1.14.0
(Scala 3.8.3) + JDK 17.

**Proxy state:** litellm proxy was NOT restarted between arms. All 18 runs were
sequential; runs within the same example share a warming proxy cache.

**Counterbalanced run order (per example):**

| Example | Order within example |
|---------|---------------------|
| F# | Arm B first (reps 1–3 positions 1–3), then Arm A (reps 1–3 positions 4–6) |
| Scala | Arm B first (reps 1–3 positions 7–9), then Arm A (reps 1–3 positions 10–12) |
| Rust | Arm A first (reps 2–3 positions 13–14), then Arm B (reps 2–3 positions 15–16); run-1 from Phase-12 pilot |

**Workspace isolation:** Each run used a separate empty `oh-workdir-planning/` directory
(gitignored); emptiness verified before each run (no cross-contamination).

### Timing caveat (mandatory)

Wall-clock and per-call timing are **derived from JSONL timestamps**
(first_event_ts → last_event_ts and obs→act gaps). They carry a
**cache-warmth / run-order confound**: the arm that ran second within each
example benefited from a warmer KV/prefix cache in the litellm proxy, and
each successive rep also encountered a warmer cache. These timing values MUST
NOT be used as planning-quality signals in isolation.

**The legacy figure `~14–32s/call` is a v1 pre-run PREDICTION, NOT a
measurement.** It does not appear as a measurement anywhere in this study.
All timing values reported here are labelled "derived from JSONL."

---

## Six-Cell Outcome Table

Metrics are median (min–max) across n=3 reps, derived from committed metrics.json.
Canonical pass counts are per-rep outcomes per example × arm (authoritative:
metrics_extractor.py patched; agrees with 13-02-RUN-NOTES.md per rep).

### F# — FsLex/FsYacc Calculator (`dotnet run -- "<expr>"`)

Canonical tests: `2+3*4`→14, `(2+3)*4`→20, `10-3-2`→5

| Cell | n | Canonical pass | honesty_gate | TerminalActions | TotalEvents | WallClock (s) | ErrorFixCycles |
|------|---|---------------|--------------|-----------------|-------------|---------------|----------------|
| F# Arm A (Claude plan) | 3 | **1/3 reps** (run-1 only) | PASS | 80 (77–210) | 207 (204–456) | 1475 (470–1853) | 21 (17–28) |
| F# Arm B (35B self-plan) | 3 | **0/3 reps** (all FAIL) | PASS | 74 (52–97) | 174 (139–227) | 487 (352–695) | 11 (7–14) |

**F# canonical pass detail (per rep):**

| Rep | Arm A | Arm B |
|-----|-------|-------|
| 1 | PASS (14/20/5 at events #200, #202, #204) | FAIL (build error; all 3 tests NOT REACHED) |
| 2 | FAIL (build/runtime errors; 456 events) | FAIL (build error; tests NOT REACHED) |
| 3 | FAIL (build succeeded; runtime crash exit=134) | FAIL (build error; tests NOT REACHED) |

**F# one-line takeaway:** FsLex/FsYacc is out-of-distribution (OOD) for the 35B;
5/6 runs failed regardless of arm. The Claude plan helped navigate the OOD task
in one run (Arm A run-1: step-by-step wiring of FsLex/FsYacc succeeded), but
this is a single observation and the OOD nature dominated overall. Result is
mixed/inconclusive, not evidence of systematic Arm A advantage.

---

### Scala — Scala 3 Calculator (`scala-cli run Calc.scala -- "<expr>"`)

Canonical tests: `2+3*4`→14, `(2+3)*4`→20, `10-3-2`→5

| Cell | n | Canonical pass | honesty_gate | TerminalActions | TotalEvents | WallClock (s) | ErrorFixCycles |
|------|---|---------------|--------------|-----------------|-------------|---------------|----------------|
| Scala Arm A (Claude plan) | 3 | **3/3 reps** | PASS | 37 (21–62) | 76 (44–132) | 346 (304–544) | 6 (3–10) |
| Scala Arm B (35B self-plan) | 3 | **2/3 reps** PASS + 1 PARTIAL | PASS | 13 (8–27) | 50 (37–83) | 936 (868–1442) | 2 (2–5) |

**Scala canonical pass detail (per rep):**

| Rep | Arm A | Arm B |
|-----|-------|-------|
| 1 | PASS (14/20/5 at events #39, #41, #43) | PASS (14/20/5 at events #69, #73, #77) |
| 2 | PASS (14/20/5 at events #55, #57, #59) | PASS (all 3 at event #31) |
| 3 | PASS (all 3 at event #129) | PARTIAL-PASS (tests 2+3 at event #45; test 1 not re-run after compilation fix) |

**PARTIAL-PASS definition:** Scala arm-b run-3 had test 1 (`2+3*4`) fail at
first attempt (compilation error); agent fixed and ran tests 2+3 successfully;
test 1 was not re-run after the fix. Evidence that the fixed binary would pass
test 1 is circumstantial. Recorded honestly as PARTIAL-PASS.

**Scala one-line takeaway:** Scala (in-distribution) broadly succeeds in both
arms. Arm B used fewer terminal actions (median 13 vs 37) but had a higher
wall-clock (median 936s vs 346s) — the wall-clock difference carries the
run-order cache confound (Arm B ran first, colder cache) and MUST NOT be read
as a planning-quality signal. Both arms converged on correct results.

---

### Rust — HTTP Server (`curl -s http://localhost:8080/` → `hello`)

Canonical test: `curl_hello` → "hello" exit=0

| Cell | n | Canonical pass | honesty_gate | TerminalActions | TotalEvents | WallClock (s) | ErrorFixCycles |
|------|---|---------------|--------------|-----------------|-------------|---------------|----------------|
| Rust Arm A (Claude plan) | 3 | **3/3 reps** | PASS | 12 (12–14) | 26 (26–30) | 48 (42–49) | 0 (0–0) |
| Rust Arm B (35B self-plan) | 3 | **3/3 reps** | PASS | 13 (12–16) | 44 (40–50) | 67 (59–71) | 0 (0–0) |

**Rust canonical pass detail (per rep):**

| Rep | Arm A | Arm B |
|-----|-------|-------|
| 1 (Phase-12 pilot) | PASS (event #25, exit=0) | PASS (event #31, exit=0) |
| 2 | PASS (event #21, exit=0) | PASS (event #37, exit=0) |
| 3 | PASS (event #21, exit=0) | PASS (event #45, exit=0) |

**Rust provenance note:** run-1.jsonl for both arms are copies of the Phase-12
pilot captures (`12-harness-rust-pilot/captured-planning/rust/arm-{a,b}/logs/run.jsonl`).
The Phase-12 Rust prompt has the workspace path hardcoded (not `__WORKDIR__`);
top-up runs used `sed "s#$OLD_PATH#$NEW_PATH#g"` direct substitution. An initial
Rust arm-a run-2 attempt using `__WORKDIR__` substitution ran in the wrong
workspace (old Phase-12 workspace, already populated); that JSONL was discarded
and a correct re-run performed — infrastructure failure, not task failure,
per honesty policy.

**Rust one-line takeaway:** Rust (in-distribution) succeeds reliably in both
arms with zero error-fix cycles. No meaningful arm-level difference in canonical
outcome; wall-clock difference (48s vs 67s) carries the run-order cache confound
(Arm A ran first for Rust top-ups).

---

## Overall Canonical Pass/Fail Summary

| Example | Arm A pass count | Arm B pass count |
|---------|-----------------|-----------------|
| F# (n=3) | **1/3** PASS | **0/3** PASS (all FAIL) |
| Scala (n=3) | **3/3** PASS | **2/3** PASS + 1 PARTIAL |
| Rust (n=3) | **3/3** PASS | **3/3** PASS |

---

## Honesty Results

### source=agent gate

All 18 runs verified: every ActionEvent has source=agent. The first event per
arm in each run is a MessageEvent with source=user (the task-prompt delivery);
MessageEvents are NOT ActionEvents and are correctly excluded from the gate.

| Example | Arm | Runs checked | Non-agent ActionEvents | Result |
|---------|-----|-------------|----------------------|--------|
| F# | A | 3 | 0 | PASS |
| F# | B | 3 | 0 | PASS |
| Scala | A | 3 | 0 | PASS |
| Scala | B | 3 | 0 | PASS |
| Rust | A | 3 | 0 | PASS |
| Rust | B | 3 | 0 | PASS |

Total: 18/18 runs PASS. Blocking sweep confirmed in metrics_extractor.py before
any aggregation.

### No manual edits

No agent-written file was manually edited after capture. All source code in
`final-source/` directories was written by the agent via bash commands per JSONL
ActionEvents and copied verbatim from the last-rep (run-3) gitignored workspaces.

### No cherry-picking

The first completed run per (example × arm × rep) IS the run, with one disclosed
exception: Rust arm-a run-2 initial attempt was discarded due to infrastructure
failure (wrong workspace from missing `__WORKDIR__` token substitution). The
re-run used the correct workspace. This is disclosed in 13-02-RUN-NOTES.md
(Infrastructure issues §1).

### Timing citation

All timing values in this manifest are labelled "derived from JSONL" and carry
the cache-warmth/run-order caveat. The legacy pre-run prediction `~14–32s/call`
is not cited as a measurement anywhere in this study.

---

## Planning Artifact Pointers

Both arms' planning artifacts are committed per example:

| Example | Arm A artifact | Arm B artifact |
|---------|---------------|---------------|
| F# | `captured-planning/fsharp/arm-a/planning-artifact/claude-plan.md` (5-step plan: fslex/fsyacc wiring; no source embedded) | `captured-planning/fsharp/arm-b/planning-artifact/oh-self-plan.md` (verbatim TaskTrackerAction event #4: 5 self-planned tasks) |
| Scala | `captured-planning/scala/arm-a/planning-artifact/claude-plan.md` (3-step plan: write/build/test) | `captured-planning/scala/arm-b/planning-artifact/oh-self-plan.md` (verbatim TaskTrackerAction event #6: 4 tasks) |
| Rust | `captured-planning/rust/arm-a/planning-artifact/claude-plan.md` (3-step plan; from Phase-12) | `captured-planning/rust/arm-b/planning-artifact/oh-self-plan.md` (verbatim TaskTrackerAction event #4: 4 tasks; from Phase-12 run-1) |

**Qualitative plan comparison (ANAL-02):**
`captured-planning/PLAN-COMPARISON-QUALITATIVE.md` — per-example comparison
of task count, granularity, ordering, and scaffold→write→build→test match
across all three examples.

### Task tracker confirmation

Arm B emitted task_tracker events in every example (confirmed in metrics.json):
- F# arm-b: median 7 TaskTrackerObservation events (4–8 range)
- Scala arm-b: median 5 TaskTrackerObservation events (5–9 range)
- Rust arm-b: median 7 TaskTrackerObservation events (7–7; consistent across all 3 reps)

Arm A emitted 0 task_tracker events in all examples — executed the supplied
Claude plan as designed. This confirms the arms differ on the planning axis.

---

## Capture Completeness

| Artifact | Status |
|----------|--------|
| `fsharp/arm-{a,b}/runs/run-{1,2,3}.jsonl` (6 files) | Committed |
| `scala/arm-{a,b}/runs/run-{1,2,3}.jsonl` (6 files) | Committed |
| `rust/arm-{a,b}/runs/run-{1,2,3}.jsonl` (6 files; run-1 = Phase-12 pilot copies) | Committed |
| `{fsharp,scala,rust}/arm-{a,b}/metrics-run-{1,2,3}.json` (18 files) | Committed (honesty_gate=PASS all 18) |
| `{fsharp,scala,rust}/arm-{a,b}/metrics.json` (6 files) | Committed (n=3 aggregates) |
| `{fsharp,scala,rust}/comparison.json` (3 files) | Committed |
| `{fsharp,scala,rust}/arm-{a,b}/planning-artifact/` (6 directories) | Committed |
| `{fsharp,scala,rust}/arm-{a,b}/final-source/` (6 directories; run-3 workspaces) | Committed |
| `PLAN-COMPARISON-QUALITATIVE.md` (ANAL-02, 144 lines) | Committed |
| `aggregate_metrics.py` (317 lines) | Committed |
| `metrics_extractor.py` (Phase-13 patched) | Committed |
| `oh-workdir-planning/` scratch | Gitignored (NOT committed) |
| `.github/workflows/deploy.yml` | Untouched |

---

## PHASE 13 CAPTURE GATE: CLOSED

Gate assertion result: **6/6 metrics.json have honesty_gate=PASS; all
canonical_tests fields populated (no null cells).**

- F# arm-a: honesty_gate=PASS; canonical 1/3 PASS (run-1 only; run-2/3 FAIL — honest)
- F# arm-b: honesty_gate=PASS; canonical 0/3 PASS (all FAIL — honest OOD result)
- Scala arm-a: honesty_gate=PASS; canonical 3/3 PASS
- Scala arm-b: honesty_gate=PASS; canonical 2/3 PASS + 1 PARTIAL (honest)
- Rust arm-a: honesty_gate=PASS; canonical 3/3 PASS
- Rust arm-b: honesty_gate=PASS; canonical 3/3 PASS

A canonical FAIL does NOT block the gate (it is valid data). The gate is
CLOSED because all six cells have honesty_gate=PASS and no cell has a null
canonical_test. F# FAILs are preserved as valid findings; no cherry-picking.

**Phase 14 (부록 D chapter) is unblocked.**
