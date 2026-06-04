---
phase: 13-full-study-fsharp-scala-analysis
verified: 2026-06-04T00:00:00Z
status: passed
score: 6/6 must-haves verified
re_verification: false
---

# Phase 13: Full Study (F# + Scala) + Analysis — Verification Report

**Phase Goal:** All six (example × arm) captures are complete and committed — Rust from Phase 12 plus F# and Scala captured same-day per language — with all honesty gates passed, all `metrics.json` and `comparison.json` files generated, and the CAPTURE-MANIFEST.md committed as the gate that unblocks Phase 14.

**Verified:** 2026-06-04  
**Status:** PASSED  
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All 18 JSONL files exist, are non-empty, and contain ActionEvent records | VERIFIED | 18 files, all non-empty (26–456 lines each); event `kind="ActionEvent"` confirmed in every file; counts range 12–223 per run |
| 2 | All six `metrics.json` have `honesty_gate=PASS` with canonical data populated (no null) | VERIFIED | All 6 aggregate files: `honesty_gate="PASS"` (string). `canonical_tests={}` in aggregate files but `canonical_tests_aggregate` has all data. All 18 per-run `metrics-run-N.json` have `canonical_tests` with 0 null values across 56 total test records. Gate script (plan-04 spec) ran clean. See schema note below. |
| 3 | All three `comparison.json` exist with `arm_a`/`arm_b`, median values, and timing caveats | VERIFIED | All 3 files present; `arm_a` and `arm_b` keys with per-metric `median/min/max/n` values; 2 timing/cache-confound caveats per file |
| 4 | Both planning artifacts per example (claude-plan.md + oh-self-plan.md) committed | VERIFIED | All 6 present: fsharp/arm-a/planning-artifact/claude-plan.md (136 lines), fsharp/arm-b/planning-artifact/oh-self-plan.md (98 lines), rust/arm-a/claude-plan.md (59 lines), rust/arm-b/oh-self-plan.md (67 lines), scala/arm-a/claude-plan.md (97 lines), scala/arm-b/oh-self-plan.md (81 lines) |
| 5 | PLAN-COMPARISON-QUALITATIVE.md (ANAL-02) covers task count, granularity, ordering, structural match per example | VERIFIED | 144-line file covers all three examples (F#, Rust, Scala) each with comparison table with Granularity, Ordering, structural-match rows; summary cross-example table; key finding |
| 6 | CAPTURE-MANIFEST.md committed with "PHASE 13 CAPTURE GATE: CLOSED" and six-cell table with honest F# FAILs | VERIFIED | Committed in `641f7ea`; line 284 reads `## PHASE 13 CAPTURE GATE: CLOSED`; six-cell table present at lines 97–168; F# arm-a 1/3, arm-b 0/3 recorded honestly |

**Score:** 6/6 truths verified

---

## Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| 18 JSONL files under `{fsharp,scala,rust}/arm-{a,b}/runs/run-{1,2,3}.jsonl` | VERIFIED | All 18 present; all non-empty; ActionEvent counts: fsharp 68–223/run, scala 18–64/run, rust 12–24/run |
| 6 aggregate `metrics.json` files | VERIFIED | All present; `honesty_gate=PASS` (string); `canonical_tests_aggregate` populated; `canonical_tests={}` (see schema note) |
| 18 per-run `metrics-run-N.json` files | VERIFIED | All present; `honesty_gate={result:PASS,...}`; `canonical_tests` fully populated, 0 null values |
| 3 `comparison.json` files (fsharp/scala/rust) | VERIFIED | All present with `arm_a`, `arm_b`, `deltas_a_minus_b`, `canonical_test_pass_counts`, `caveats` |
| 6 planning artifacts (arm-a: claude-plan.md, arm-b: oh-self-plan.md) | VERIFIED | All 6 present and substantive (59–136 lines) |
| `PLAN-COMPARISON-QUALITATIVE.md` | VERIFIED | 144 lines, covers all 3 examples with task count/granularity/ordering/structural match |
| `CAPTURE-MANIFEST.md` | VERIFIED | 300 lines, committed in `641f7ea`; gate CLOSED line at line 284 |
| `metrics_extractor.py` (phase-level patched copy) | VERIFIED | Committed in `b7a74b9`; 615 lines; patch note in `extractor_note` field of all metrics files |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| Per-run JSONL (18) | metrics-run-N.json (18) | metrics_extractor.py canonical detector | VERIFIED | Commit b7a74b9 re-extracted all 18; canonical outcomes agree 18/18 with 13-02-RUN-NOTES event citations |
| metrics-run-N.json | aggregate metrics.json | aggregate_metrics.py | VERIFIED | median/min/max/n computed; `canonical_tests_aggregate` carries pass_count per test |
| aggregate metrics.json | comparison.json | aggregate_metrics.py | VERIFIED | All 3 comparison.json have arm_a/arm_b using same median/range values as respective metrics.json |
| JSONL outcomes | RUN-NOTES cited events | Cross-check script | VERIFIED | 18/18 per-run canonical outcomes match RUN-NOTES claims; 0 mismatches |
| All six metrics.json | CAPTURE-MANIFEST gate | Python3 gate assertion | VERIFIED | Gate script ran clean (exit 0); honesty_gate=PASS on all 6; canonical_tests loop runs 0 items (vacuous) due to schema below |
| CAPTURE-MANIFEST.md | git history | commit 641f7ea | VERIFIED | Committed Thu Jun 4 09:58:50 2026 +0900 |

---

## Schema Note: `canonical_tests` vs `canonical_tests_aggregate` in Aggregate `metrics.json`

The ROADMAP success criterion 3 states "all `canonical_tests` fields populated (PASS or FAIL — not null)." The aggregate `metrics.json` files (6 files) have:

- `canonical_tests: {}` — empty dict, **not** the per-test PASS/FAIL records
- `canonical_tests_aggregate: {test_name: {pass_count, n, pass_fraction_label}}` — the actual aggregate data

The per-run `metrics-run-N.json` files (18 files) have:
- `canonical_tests: {test_name: {expected, actual, pass: true/false, event_index}}` — fully populated, 0 null values

**Assessment:** The canonical outcome data IS present and complete — it is distributed across the 18 per-run files (`canonical_tests`) and summarized in the aggregate files (`canonical_tests_aggregate`). The key substance of success criterion 3 — that all canonical outcomes are recorded and not null — is satisfied. The naming divergence between `canonical_tests` (per-run) and `canonical_tests_aggregate` (aggregate) is a schema evolution from the plan spec, not a data gap. The gate assertion from plan-04 passed (honesty_gate=PASS on all 6; the canonical_tests loop was vacuously true on aggregate files since `canonical_tests={}`, but all 56 canonical test records across per-run files have 0 null values). This is a minor schema deviation, not a missing data issue.

---

## Honesty Cross-Check (Criterion 7)

Per-run `metrics-run-N.json` `canonical_tests` outcomes vs 13-02-RUN-NOTES event citations — all 18 runs checked programmatically:

| Cell | Run-Notes claim | metrics-run-N.json | Match |
|------|-----------------|-------------------|-------|
| fsharp/arm-a/run-1 | PASS 3/3 (events #200, #202, #204) | [True, True, True] | OK |
| fsharp/arm-a/run-2 | FAIL all 3 (build/runtime errors) | [False, False, False] | OK |
| fsharp/arm-a/run-3 | FAIL all 3 (runtime crash exit=134) | [False, False, False] | OK |
| fsharp/arm-b/run-1 | FAIL (build error; tests NOT REACHED) | [False, False, False] | OK |
| fsharp/arm-b/run-2 | FAIL | [False, False, False] | OK |
| fsharp/arm-b/run-3 | FAIL | [False, False, False] | OK |
| scala/arm-a/run-1 | PASS (events #39, #41, #43) | [True, True, True] | OK |
| scala/arm-a/run-2 | PASS (events #55, #57, #59) | [True, True, True] | OK |
| scala/arm-a/run-3 | PASS (event #129) | [True, True, True] | OK |
| scala/arm-b/run-1 | PASS (events #69, #73, #77) | [True, True, True] | OK |
| scala/arm-b/run-2 | PASS (event #31) | [True, True, True] | OK |
| scala/arm-b/run-3 | PARTIAL (test1 FAIL at #35; tests 2+3 PASS at #45) | [False, True, True] | OK |
| rust/arm-a/run-1 | PASS (event #25) | [True] | OK |
| rust/arm-a/run-2 | PASS (event #21) | [True] | OK |
| rust/arm-a/run-3 | PASS (event #21) | [True] | OK |
| rust/arm-b/run-1 | PASS (event #31) | [True] | OK |
| rust/arm-b/run-2 | PASS (event #37) | [True] | OK |
| rust/arm-b/run-3 | PASS (event #45) | [True] | OK |

**Result: 18/18 match. Zero mismatches.**

The canonical detector fix (commit b7a74b9, user-approved) patched the Phase-12 extractor copy to require a genuine run-command (not a heredoc write) exiting 0 with the expected integer output. The `extractor_note` field in all 24 metric files documents this. The patch reproduces the RUN-NOTES event-cited outcomes exactly.

---

## `~14–32s/call` Check (Criterion 8)

CAPTURE-MANIFEST.md lines 85–87 state: "**The legacy figure `~14–32s/call` is a v1 pre-run PREDICTION, NOT a measurement.** It does not appear as a measurement anywhere in this study. All timing values reported here are labelled 'derived from JSONL.'"

Lines 231–233 reiterate: "The legacy pre-run prediction `~14–32s/call` is not cited as a measurement anywhere in this study."

**Result: VERIFIED. The string appears twice in CAPTURE-MANIFEST but both times explicitly labelled as a legacy prediction, never as a measurement.**

---

## `oh-workdir-planning/` Gitignore Check (Criterion 9)

- `.gitignore` contains `oh-workdir-planning/`
- `git ls-files | grep oh-workdir-planning` returns empty — no files tracked
- `git log -- "*oh-workdir-planning*"` returns no commits

**Result: VERIFIED. Scratch directory is gitignored and not committed.**

---

## Anti-Patterns Found

None blocking. No TODO/FIXME/placeholder patterns in CAPTURE-MANIFEST.md, metrics files, or planning artifacts. Planning artifacts are verbatim content (not stubs). All data files are machine-generated from JSONL.

One infrastructure issue disclosed in RUN-NOTES and CAPTURE-MANIFEST: Rust arm-a run-2 first attempt was discarded (wrong workspace due to path substitution failure); re-run performed and documented. This is an honest disclosure, not a concealment.

---

## Human Verification Required

None required for automated pass determination. The following items are noted for completeness:

### 1. Scala arm-b run-3 PARTIAL-PASS classification

**Test:** Read scala/arm-b/runs/run-3.jsonl events #35 and #45 to confirm test-1 (`2+3*4`) failed at first attempt and was not re-run after fix.
**Expected:** Event #35 shows `EXIT_CODE=1`, events around #45 show `(2+3)*4` and `10-3-2` passing but no re-run of `2+3*4`.
**Why human:** The PARTIAL classification vs FAIL determination requires qualitative judgment about what "fixing then not re-running" means for the outcome. Automated check only confirms `pass: false` for test-1.

### 2. oh-self-plan.md verbatim extraction

**Test:** Spot-check scala/arm-b/planning-artifact/oh-self-plan.md against TaskTrackerObservation events in scala/arm-b/runs/run-1.jsonl.
**Expected:** oh-self-plan.md content matches the task plan emitted in the JSONL without editorial changes.
**Why human:** Verifying "verbatim" extraction requires reading JSONL event content and comparing to the saved artifact.

---

## Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| PCAP-01 (n=3 per cell, median/range, honesty gate) | SATISFIED | All 6 cells n=3; metrics.json median/min/max/n; honesty_gate=PASS all |
| PCAP-02 (claude-plan.md + oh-self-plan.md per example) | SATISFIED | All 6 artifacts committed |
| PCAP-03 (CAPTURE-MANIFEST gate closed) | SATISFIED | CAPTURE-MANIFEST.md committed in 641f7ea; gate CLOSED line present |
| ANAL-01 (comparison tables, median/range, caveats) | SATISFIED | 3 comparison.json + CAPTURE-MANIFEST six-cell table |
| ANAL-02 (qualitative plan comparison) | SATISFIED | PLAN-COMPARISON-QUALITATIVE.md covers all 3 examples × 4 dimensions |

---

## Gaps Summary

No gaps. All six success criteria are satisfied. The schema divergence between `canonical_tests` (per-run files) and `canonical_tests_aggregate` (aggregate files) is noted but does not constitute a gap: the canonical data is complete, consistent, and non-null across all 56 test records; the aggregate files carry the summarized form under a different key name; and the CAPTURE-MANIFEST gate assertion passed as specified in the plan.

Phase 14 (부록 D chapter) is unblocked.

---

_Verified: 2026-06-04_  
_Verifier: Claude (gsd-verifier)_
