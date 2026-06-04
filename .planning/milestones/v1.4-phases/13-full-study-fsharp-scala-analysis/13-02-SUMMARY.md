---
phase: 13-full-study-fsharp-scala-analysis
plan: 02
subsystem: capture-protocol
tags: [fsharp, scala, rust, fslex, fsyacc, planning-ab-study, live-capture, jsonl, v1.4]

# Dependency graph
requires:
  - phase: 13-full-study-fsharp-scala-analysis
    provides: "Frozen F# + Scala prompt sets (13-01); Arm A claude plans + Arm B task-tracker prompts; n=3 layout scaffolded"
  - phase: 12-harness-rust-pilot
    provides: "Proven harness mechanics (background + poll-to-settle, JSONL schema, idle-settle criterion); Rust pilot run-1 JSONL (provenance for run-1 in this phase)"
provides:
  - "F# arm-a/runs/run-1..3.jsonl — 207/456/204 events each; arm-a run-1 PASS, run-2/3 FAIL (FsLex OOD)"
  - "F# arm-b/runs/run-1..3.jsonl — 227/174/139 events; all FAIL (FsLex/FsYacc OOD for 35B)"
  - "Scala arm-a/runs/run-1..3.jsonl — 44/76/132 events; all PASS (14/20/5)"
  - "Scala arm-b/runs/run-1..3.jsonl — 83/37/50 events; run-1/2 PASS, run-3 PARTIAL-PASS"
  - "Rust arm-a/runs/run-1..3.jsonl — run-1 from Phase-12 pilot; run-2/3 fresh; all PASS"
  - "Rust arm-b/runs/run-1..3.jsonl — run-1 from Phase-12 pilot; run-2/3 fresh; all PASS"
  - "13-02-RUN-NOTES.md (427 lines) — full run log with counterbalance, settle evidence, verbatim canonical outcomes"
affects:
  - "13-03 (metrics extraction + comparison — reads all 18 JSONLs)"
  - "13-04 (부록 D chapter — cites run results and pass/fail matrix)"

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Idle-settle detection: 3 consecutive polls with identical last_ts declares settle (process may have exited without FinishAction)"
    - "Workspace path substitution: Phase-12 Rust prompts use hardcoded paths (not __WORKDIR__ token); use sed old-path→new-path substitution for top-up runs"
    - "Run-1 provenance: Copy Phase-12 pilot JSONL as run-1 in Phase-13 tree; label provenance in RUN-NOTES"

key-files:
  created:
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/arm-a/runs/run-1.jsonl"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/arm-a/runs/run-2.jsonl"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/arm-a/runs/run-3.jsonl"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/arm-b/runs/run-1.jsonl"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/arm-b/runs/run-2.jsonl"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/arm-b/runs/run-3.jsonl"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/scala/arm-a/runs/run-1..3.jsonl"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/scala/arm-b/runs/run-1..3.jsonl"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/rust/arm-a/runs/run-1..3.jsonl"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/rust/arm-b/runs/run-1..3.jsonl"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/13-02-RUN-NOTES.md"
  modified: []

key-decisions:
  - "Idle-settle threshold: 3 consecutive polls with identical last_ts + no FinishAction = process exited; this is THE settled state even if JSONL lacks a FinishAction line"
  - "Rust top-up prompt substitution: Phase-12 Rust prompts use hardcoded workspace paths, not __WORKDIR__ tokens; correct approach is sed old-path→new-path; discard first mis-substituted attempt"
  - "Run-1 provenance: Phase-12 pilot JSONLs copied as run-1 in Phase-13 tree; labelled '(Phase-12 pilot rep)' in RUN-NOTES"
  - "Scala arm-b run-3 recorded as PARTIAL-PASS: test 1 (2+3*4) first failed due to compile error; agent fixed and ran tests 2+3 (PASS); test 1 not re-verified after fix"
  - "F# is OOD confirmed at n=3: arm-b 0/3 PASS; arm-a 1/3 PASS (run-1 succeeded with claude plan); FsLex/FsYacc syntax is outside 35B training distribution"
  - "Scala is in-distribution confirmed at n=3: arm-a 3/3 PASS; arm-b 2/3 PASS + 1 PARTIAL-PASS"
  - "Rust is in-distribution confirmed at n=3: both arms 3/3 PASS"

patterns-established:
  - "PCAP-01 complete: all 18 (example × arm × rep) cells have real per-run JSONL from live 35B invocations"
  - "Honesty discipline held: no re-runs for poor results; FAILs recorded as FAILs; infrastructure re-run disclosed"
  - "Idle-settle caveat: runs can continue after apparent settle-detection; final event count is authoritative"

# Metrics
duration: 2h20min
completed: 2026-06-02
---

# Phase 13 Plan 02: Full Study Runs Summary

**Live 35B planning A/B study complete: F# 6 runs (arm-a 1/3 PASS), Scala 6 runs (arm-a 3/3 PASS, arm-b 2+1partial/3), Rust 6 runs (6/6 PASS) — 18 JSONL captures total, all committed with honest pass/fail outcomes.**

## Performance

- **Duration:** ~2 h 20 min (10:31 UTC → 13:33 UTC, derived from JSONL timestamps)
- **Started:** 2026-06-02T10:31:36Z (F# Arm B Run 1 launch)
- **Completed:** 2026-06-02T13:33:02Z (Rust Arm B Run 3 settle)
- **Tasks:** 2 (Task 1: F# 6 runs; Task 2: Scala 6 runs + Rust top-up 6 runs)
- **Files created:** 18 JSONL runs + 1 RUN-NOTES.md = 19

## Accomplishments

- All six (example × arm) cells have real per-run JSONL at n=3 from live 35B CodeActAgent invocations, satisfying PCAP-01.
- F# OOD confirmed at n=3: arm-b 0/3 PASS (FsLex parse errors in all reps), arm-a 1/3 PASS (run-1 succeeded with claude-authored plan, run-2/3 failed). Confirms F# is OOD for the 35B and produces naturally honest failure data.
- Scala in-distribution confirmed at n=3: arm-a 3/3 PASS (14/20/5), arm-b 2/3 PASS + 1 PARTIAL-PASS. Scala Arm B's file-write difficulties (bash quoting failures) occurred but agents recovered and passed.
- Rust in-distribution confirmed at n=3 per arm: both arms 6/6 PASS (hello/exit=0). Consistent with prior Phase-12 pilot findings.
- Counterbalanced run order documented (Arm B first for F#/Scala; Arm A first for Rust top-up); cache-warmth caveat explicitly recorded per METH-02 / Pitfall 3.
- All 18 runs isolated in per-run empty workspaces; no workspace contamination; no manual source edits; honesty discipline maintained.

## Task Commits

1. **Task 1: F# full study both arms n=3** - `569bd8e` (feat)
2. **Task 2: Scala + Rust top-up both arms n=3** - `8e9c328` (feat)

**Plan metadata:** (see below — committed after SUMMARY.md)

## Files Created/Modified

- `captured-planning/fsharp/arm-{a,b}/runs/run-{1,2,3}.jsonl` — 6 F# capture files (207/456/204/227/174/139 events)
- `captured-planning/scala/arm-{a,b}/runs/run-{1,2,3}.jsonl` — 6 Scala capture files (44/76/132/83/37/50 events)
- `captured-planning/rust/arm-{a,b}/runs/run-{1,2,3}.jsonl` — 6 Rust capture files (30pilot/26/26/40pilot/44/50 events)
- `13-02-RUN-NOTES.md` — 427-line full run log

## Decisions Made

- **Idle-settle threshold:** 3 consecutive polls with same last_ts + no FinishAction = idle-settled (process exited). Runs can accumulate more events after apparent settle; final event count is authoritative. A "post-settle" caveat is added to RUN-NOTES.
- **Rust prompt path substitution:** Phase-12 Rust prompts have hardcoded workspace paths (not `__WORKDIR__` tokens). Correct substitution is `sed "s#$OLD_PATH#$NEW_PATH#g"`. First mis-substituted attempt (Arm A run-2) was discarded as infrastructure failure; re-run documented in RUN-NOTES.
- **Run-1 provenance:** Phase-12 pilot Rust JSONLs copied as `run-1.jsonl` in this phase's tree (both arms); labelled "(Phase-12 pilot rep)" in RUN-NOTES.
- **Scala arm-b run-3 PARTIAL-PASS:** The agent had a compilation failure on test 1 (`2+3*4`), fixed the code, then ran tests 2+3 successfully (20/5 exit=0), but did not re-verify test 1 after the fix. Recorded honestly as PARTIAL-PASS, not PASS.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Rust top-up: first attempt used wrong workspace (path substitution failure)**

- **Found during:** Task 2 (Rust Arm A run-2 invocation)
- **Issue:** The Phase-12 Rust arm-a prompt uses a hardcoded workspace path, not a `__WORKDIR__` token. `sed "s#__WORKDIR__#$WD#g"` had no match; agent ran in the old Phase-12 `arm-a/rust` workspace which was already populated (had src/main.rs from prior run). This constitutes an infrastructure failure (wrong workspace).
- **Fix:** Re-ran with `sed "s#$OLD_PATH#$NEW_PATH#g"` direct old→new path substitution. Re-run is the official run-2 record.
- **Files modified:** `captured-planning/rust/arm-a/runs/run-2.jsonl` (overwritten with corrected run)
- **Verification:** JSONL event #1 (MessageEvent) confirms prompt shows correct new workspace path. Agent ran `cargo new rust-server` successfully in empty workspace.
- **Committed in:** `8e9c328` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 — infrastructure path substitution bug; infrastructure failure, not task quality failure)
**Impact on plan:** Minimal — one run-2 re-attempt for Rust Arm A; all other runs first-attempts. No scope change.

## Issues Encountered

- Idle-settle detection proved unreliable for long-running F# runs: the 3-consecutive-poll criterion declared some F# arm-a runs settled when they were merely between LLM calls. Final event counts for arm-a run-2 (456 vs. 284 estimated) and run-3 (204 vs. 76 estimated) were larger than the settle-time snapshots. This does not affect the canonical outcomes (no canonical tests reached in either run regardless).
- Scala arm-b all three runs experienced bash quoting failures in early events (python3 heredoc exit=-1, `printf` syntax errors). The agents recovered by trying alternate approaches and eventually succeeded in runs 1+2, partially succeeded in run-3.
- F# arm-a run-3 had a different failure mode from runs 1+2: the build succeeded but the runtime crashed (exit=134, Program.fs line 13 error). This is the first observed runtime-success-but-crash pattern; captured honestly.

## Next Phase Readiness

- All 18 JSONL captures committed. Ready for 13-03 (metrics_extractor.py on all runs, honesty gate, comparison.json, CAPTURE-MANIFEST.md).
- F# pass/fail pattern (arm-a 1/3, arm-b 0/3) is a valid and interesting finding for 부록 D: the claude-authored plan helped in 1/3 runs but OOD nature of FsLex dominated.
- Scala pattern (arm-a 3/3, arm-b ~3/3) shows both arms succeeded on in-distribution task; interesting that arm-b had file-write difficulties before recovery.
- Rust pattern (6/6 PASS both arms) confirms in-distribution reliability.
- Key metric for 13-03: TaskTracker event counts (arm-b self-planned in all languages); error-fix cycle counts; wall-clock (with cache caveat); event count comparisons.

---
*Phase: 13-full-study-fsharp-scala-analysis*
*Completed: 2026-06-02*
