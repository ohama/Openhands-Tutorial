---
phase: 13-full-study-fsharp-scala-analysis
plan: 03
subsystem: analysis
tags: [fsharp, scala, rust, metrics, honesty-gate, planning-ab-study, v1.4, aggregate]

# Dependency graph
requires:
  - phase: 13-full-study-fsharp-scala-analysis
    provides: "18 live run JSONLs (fsharp/scala/rust × arm-a/arm-b × run-1..3)"
  - phase: 12-harness-rust-pilot
    provides: "metrics_extractor.py (validated, REUSED AS-IS); Phase-12 Rust planning artifacts"
provides:
  - "18 per-run metrics-run-N.json with honesty_gate=PASS and canonical_tests populated"
  - "6 per-arm metrics.json (median/min/max, n=3) for fsharp/scala/rust × arm-a/arm-b"
  - "3 per-example comparison.json (Arm A vs Arm B on all P1/P2 metrics + fairness caveats)"
  - "aggregate_metrics.py (317 lines) — median/range aggregation + comparison builder"
  - "3 oh-self-plan.md extracted verbatim from TaskTrackerAction events (fsharp event #4, scala event #6, rust event #4)"
  - "3 claude-plan.md per example (fsharp/scala in Phase-13, rust copied from Phase-12)"
  - "PLAN-COMPARISON-QUALITATIVE.md (144 lines) — ANAL-02 per example"
  - "6 final-source snapshots (last-rep workspace, no edits)"
affects:
  - "13-04 (부록 D chapter — reads comparison.json + PLAN-COMPARISON-QUALITATIVE.md + oh-self-plan.md)"

# Tech tracking
tech-stack:
  added:
    - "aggregate_metrics.py (new script; statistics.median for n≥2 metrics; single-run label logic)"
  patterns:
    - "Per-run extraction: metrics_extractor.py (REUSED AS-IS) → metrics-run-N.json per run"
    - "Aggregate shape: median/min/max/n per numeric metric; canonical_tests as pass_count/n/label"
    - "Honesty gate: blocking sweep asserting honesty_gate=PASS on all 18 metrics-run-N.json"
    - "Extractor first-match limitation: multi-line heredoc commands may match before actual test run; documented in extractor_note + caveats; authoritative outcomes in 13-02-RUN-NOTES.md"

key-files:
  created:
    - ".planning/phases/13-full-study-fsharp-scala-analysis/aggregate_metrics.py"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/arm-a/metrics-run-{1,2,3}.json"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/fsharp/arm-b/metrics-run-{1,2,3}.json"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/scala/arm-a/metrics-run-{1,2,3}.json"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/scala/arm-b/metrics-run-{1,2,3}.json"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/rust/arm-a/metrics-run-{1,2,3}.json"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/rust/arm-b/metrics-run-{1,2,3}.json"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/{fsharp,scala,rust}/arm-{a,b}/metrics.json"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/{fsharp,scala,rust}/comparison.json"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/{fsharp,scala,rust}/arm-b/planning-artifact/oh-self-plan.md"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/rust/arm-a/planning-artifact/claude-plan.md"
    - ".planning/phases/13-full-study-fsharp-scala-analysis/captured-planning/PLAN-COMPARISON-QUALITATIVE.md"
    - "final-source snapshots for all 6 (example × arm) cells"
  modified: []

key-decisions:
  - "metrics_extractor.py REUSED AS-IS (not rewritten): first-match limitation documented; canonical_tests results reflect extractor behavior; authoritative final outcomes remain in 13-02-RUN-NOTES.md"
  - "Blocking honesty gate: python3 sweep over all 18 metrics-run-N.json confirmed honesty_gate=PASS on every run before aggregation"
  - "aggregate_metrics.py uses statistics.median (not mean): no mean/SD at small n; median/min/max/n reported; n=1 label (단일 실행) logic included even though all cells have n=3"
  - "Extractor first-match limitation: for F#/Scala, multi-line heredoc commands (cat <<'EOF'...'EOF') embed the test expression in the command string, causing the extractor to match the file-write ObservationEvent as the first match rather than the actual test run. This produces false-negative FAILs for runs where the agent ultimately passed. Documented in extractor_note + comparison.json caveats."
  - "F# canonical_tests: extractor shows 0/3 PASS for arm-a (all reps FAIL per extractor). But 13-02-RUN-NOTES.md confirms arm-a run-1 = PASS (14/20/5 at events #200/202/204). Discrepancy is due to extractor first-match on heredoc write at event #19. Honest: extractor results kept, discrepancy documented."
  - "Scala canonical_tests: extractor shows partial results (arm-a tests 2+3 PASS in runs 1/2 but test 1 FAIL; arm-a run-3 all FAIL due to combined-command last-line being EXIT:0; arm-b all FAIL due to EXIT_CODE=0 last line). 13-02-RUN-NOTES.md confirms arm-a 3/3 PASS, arm-b 2/3 PASS + 1 PARTIAL."
  - "oh-self-plan.md extraction: source is TaskTrackerAction.action.task_list (event #4 for F# and Rust arm-b; event #6 for Scala arm-b); not TaskTrackerObservation (which only shows update-count notifications in Rust/F# run-1 or full list display text in Scala). Both are sourced VERBATIM from JSONL."
  - "final-source provenance: copied from last-rep (run-3) gitignored workspaces before any wipe; no agent-written source was edited"

patterns-established:
  - "ANAL-01 complete: per-run metrics + per-arm aggregates + per-example comparisons all produced from reused extractor"
  - "ANAL-02 complete: PLAN-COMPARISON-QUALITATIVE.md covers all 3 examples with task count / granularity / ordering / scaffold→write→build→test match"
  - "PCAP-02 complete: both planning artifacts per example (claude-plan.md + verbatim oh-self-plan.md)"
  - "METH-03 complete: blocking honesty gate PASS on all 18 runs; no cherry-picking"

# Metrics
duration: 10min
completed: 2026-06-02
---

# Phase 13 Plan 03: Metrics Extraction + Analysis Summary

**All 18 JSONL runs extracted with reused metrics_extractor.py (honesty gate PASS on all), 6 per-arm median/range metrics.json + 3 comparison.json + verbatim oh-self-plan.md + 144-line PLAN-COMPARISON-QUALITATIVE.md — ANAL-01/ANAL-02/PCAP-02/METH-03 complete.**

## Performance

- **Duration:** ~10 min (2026-06-02T04:51:24Z → 2026-06-02T05:01:39Z)
- **Started:** 2026-06-02T04:51:24Z
- **Completed:** 2026-06-02T05:01:39Z
- **Tasks:** 2 (Task 1: metrics extraction + aggregation; Task 2: planning artifacts + qualitative comparison)
- **Files created:** 18 metrics-run-N.json + 6 metrics.json + 3 comparison.json + 3 oh-self-plan.md + PLAN-COMPARISON-QUALITATIVE.md + aggregate_metrics.py + final-source snapshots = 46+

## Accomplishments

- metrics_extractor.py (Phase-12, REUSED AS-IS) ran over all 18 run JSONLs; every run produced metrics-run-N.json with honesty_gate=PASS (blocking sweep confirmed 18/18).
- aggregate_metrics.py (317 lines) built and executed for all three examples; 6 per-arm metrics.json (median/min/max, n=3) and 3 per-example comparison.json produced with timing caveats and extractor_note.
- oh-self-plan.md extracted verbatim from TaskTrackerAction events: F# arm-b event #4 (5 tasks), Scala arm-b event #6 (4 tasks with progression through events #42/#70/#74/#78), Rust arm-b event #4 (4 tasks, Phase-12 pilot run-1).
- PLAN-COMPARISON-QUALITATIVE.md (144 lines) covers all three examples with per-example comparison tables (task count, granularity, ordering, scaffold→write→build→test match) and a cross-example summary.
- Extractor first-match limitation documented honestly: for multi-line heredoc commands, the extractor matches file-write observations rather than actual test runs; authoritative outcomes remain in 13-02-RUN-NOTES.md.

## Task Commits

1. **Task 1: metrics_extractor + honesty gate + aggregate** - `2ab2e26` (feat)
2. **Task 2: planning artifacts + ANAL-02 qualitative comparison** - `f27dfd7` (feat)

**Plan metadata:** (committed below)

## Files Created/Modified

- `aggregate_metrics.py` (317 lines) — aggregation script: median/min/max/n + single-run label + comparison.json builder
- `captured-planning/{fsharp,scala,rust}/arm-{a,b}/metrics-run-{1,2,3}.json` — 18 per-run files with honesty_gate=PASS
- `captured-planning/{fsharp,scala,rust}/arm-{a,b}/metrics.json` — 6 per-arm aggregate files (n=3)
- `captured-planning/{fsharp,scala,rust}/comparison.json` — 3 per-example comparisons (arm_a/arm_b/deltas/caveats)
- `captured-planning/{fsharp,scala,rust}/arm-b/planning-artifact/oh-self-plan.md` — 3 verbatim self-plans
- `captured-planning/rust/arm-a/planning-artifact/claude-plan.md` — copied from Phase-12
- `captured-planning/PLAN-COMPARISON-QUALITATIVE.md` (144 lines) — ANAL-02
- `captured-planning/{fsharp,scala,rust}/arm-{a,b}/final-source/` — 6 final-source snapshots (run-3 workspaces)

## Decisions Made

- **REUSE AS-IS discipline:** metrics_extractor.py was not modified. The extractor's first-match behavior for canonical_tests (matching the first ObservationEvent whose command contains the test expression, including multi-line heredoc file writes) is a known limitation documented in extractor_note and comparison.json caveats. This produces false-negative FAILs for some Scala and F# runs; authoritative outcomes are in 13-02-RUN-NOTES.md.
- **aggregate_metrics.py uses statistics.median:** Never mean or SD at small n. At n=3, median = middle value. Timing metrics carry the cache-warmth caveat in all comparison.json caveats fields.
- **oh-self-plan.md source:** The verbatim source is action.task_list in TaskTrackerAction events (not the rendered TaskTrackerObservation text). This matches the Phase-12 approach (oh-self-plan.md in 12-03-SUMMARY).
- **F# canonical_tests discrepancy:** The extractor reports 0/3 PASS for fsharp/arm-a (all FAILs in extractor output). 13-02-RUN-NOTES.md confirms run-1 = PASS (events #200/202/204: 14/20/5). The gap is the extractor matching event #19 (cat heredoc write with Program.fs content containing "2+3*4") as the first match, recording an empty result. This is documented, not hidden.
- **final-source provenance:** Copied from last-rep (run-3) gitignored workspaces (oh-workdir-planning/arm-{a,b}/{lang}-r3/). No source was edited.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created missing Rust planning-artifact and final-source directories**

- **Found during:** Task 2 (oh-self-plan.md extraction)
- **Issue:** The Phase-13 Rust arm-a and arm-b directories had no planning-artifact or final-source subdirectories (the Phase-13 layout for Rust was shallower than F#/Scala since Rust was added as a top-up). The claude-plan.md and oh-self-plan.md had no target location.
- **Fix:** `mkdir -p` for rust/arm-{a,b}/planning-artifact and rust/arm-{a,b}/final-source; copied claude-plan.md from Phase-12 Rust arm-a.
- **Files modified:** New directories + claude-plan.md + oh-self-plan.md + final-source files created there
- **Committed in:** `f27dfd7` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 3 — missing directory structure for Rust arms)
**Impact on plan:** Minimal — structural only; all required artifacts produced.

## Issues Encountered

- **Extractor first-match limitation (known, documented):** For F# arm-a run-1 and several Scala arm-a/arm-b runs, the extractor records the first ObservationEvent whose command string contains the test expression. When agents write source code using multi-line heredocs (cat <<'SCALAEOF'...'SCALAEOF'), the command field includes the full heredoc body, which may contain the canonical test expression. The extractor then records the file-write observation (typically empty content or the heredoc delimiter as last line) rather than the actual test run. Effect: false-negative FAILs in canonical_tests. Resolution: documented in extractor_note field in all metrics files; comparison.json caveats note authoritative outcomes in 13-02-RUN-NOTES.md. The extractor was not modified per "REUSE AS-IS."
- **Scala arm-b canonical_tests EXIT_CODE pattern:** Scala arm-b runs used `scala-cli run ... 2>&1; echo "EXIT_CODE=$?"` which produces "EXIT_CODE=0" as the last line of the ObservationEvent content. The extractor's last-line check sees "EXIT_CODE=0" instead of the numeric result (14/20/5), producing false FAILs. Same resolution as above.

## Next Phase Readiness

- ANAL-01 + ANAL-02 + PCAP-02 + METH-03 all complete. Ready for 13-04 (부록 D chapter assembly).
- 13-04 should cite 13-02-RUN-NOTES.md as the authoritative pass/fail source, not comparison.json canonical_tests (which reflect extractor first-match). The comparison.json is authoritative for P1/P2 numeric metrics.
- Key numeric metrics for 부록 D: Rust arm-a median terminal_actions=12, arm-b=13 (essentially same). Scala arm-a median terminal_actions=37, arm-b=13 (arm-a more iterations). F# arm-a median terminal_actions=80, arm-b=74. Task tracker present in arm-b all examples (Rust: 7 obs, Scala: 9 obs, F#: 4-8 obs) and absent in arm-a all examples.
- Timing deltas carry the cache/run-order caveat — F# arm-a wall_clock median much higher than arm-b (OOD: arm-a tried longer), Scala arm-b wall_clock higher than arm-a (arm-b ran first, colder cache). Do NOT present these as planning-quality signals.

---
*Phase: 13-full-study-fsharp-scala-analysis*
*Completed: 2026-06-02*
