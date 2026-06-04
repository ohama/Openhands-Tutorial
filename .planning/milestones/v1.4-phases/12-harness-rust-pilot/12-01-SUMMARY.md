---
phase: 12-harness-rust-pilot
plan: "01"
subsystem: harness
tags: [python3, jsonl, rust, openHands, a-b-comparison, metrics, prompt-engineering]

# Dependency graph
requires:
  - phase: 08-capture-the-35b-rust-http-server-run
    provides: v1.2 Rust task prompts and Claude's 3-step decomposition (Arm A source)
  - phase: 10-capture-the-35b-scala-calculator-run
    provides: honesty gate pattern + JSONL schema (confirmed real schema)
provides:
  - oh-workdir-planning/ gitignored; arm-a/rust and arm-b/rust empty isolated workspaces
  - CONTROL-BLOCK-rust.txt (shared byte-identical control block for both arms)
  - Arm A prompt (oh-prompt.txt) — control block + Claude's 3-step numbered plan
  - Arm B prompt (oh-goal-prompt.txt) — control block + "Plan your own steps using the task tracker"
  - PROMPT-DIFF-rust.txt — literal diff evidence ending CONTROL-BLOCK SYMMETRY: PASS
  - metrics_extractor.py — JSONL → metrics.json per ARCHITECTURE.md schema, 1-based indices, self-validated
affects:
  - 12-02 (runs both arms with these prompts; uses metrics_extractor.py)
  - 12-03 (capture gate; commits metrics.json artifacts)
  - 13-01 / 13-02 (F# and Scala arms reuse metrics_extractor.py)

# Tech tracking
tech-stack:
  added: [python3 (stdlib only — json, argparse, datetime, collections, tempfile)]
  patterns:
    - "Control-block symmetry: both arm prompts share byte-identical control block; only plan/self-plan block differs"
    - "1-based event numbering throughout metrics_extractor.py (enumerate start=1); matches CAPTURE-MANIFEST citation convention"
    - "Self-validation via --self-test flag: synthetic fixture exercises clean-PASS and dirty-FAIL paths inline"

key-files:
  created:
    - .planning/phases/12-harness-rust-pilot/task-prompts/CONTROL-BLOCK-rust.txt
    - .planning/phases/12-harness-rust-pilot/captured-planning/rust/arm-a/planning-artifact/claude-plan.md
    - .planning/phases/12-harness-rust-pilot/captured-planning/rust/arm-a/planning-artifact/oh-prompt.txt
    - .planning/phases/12-harness-rust-pilot/captured-planning/rust/arm-b/planning-artifact/oh-goal-prompt.txt
    - .planning/phases/12-harness-rust-pilot/task-prompts/PROMPT-DIFF-rust.txt
    - .planning/phases/12-harness-rust-pilot/metrics_extractor.py
    - .planning/phases/12-harness-rust-pilot/captured-planning/rust/arm-a/{logs,planning-artifact,final-source}/.gitkeep
    - .planning/phases/12-harness-rust-pilot/captured-planning/rust/arm-b/{logs,planning-artifact,final-source}/.gitkeep
  modified:
    - .gitignore (appended oh-workdir-planning/)

key-decisions:
  - "Arm A mechanical conversion: v1.2 task1/2/3 → 3 numbered single-session steps with state-handoff phrasing; no new planning detail added; no scaffolded source"
  - "Control block uses __WORKDIR__ token for diff normalization; each arm prompt substitutes its own path before the diff is computed"
  - "PROMPT-DIFF-rust.txt records the diff command, masked content explanation, and CONTROL-BLOCK SYMMETRY: PASS — mandatory METH-01 evidence"
  - "metrics_extractor.py uses enumerate(events, start=1) throughout; 0-based ARCHITECTURE.md reference snippet explicitly converted"
  - "Self-validation built into the script as --self-test flag (not a separate test file) — 6-event clean fixture + dirty source=user injection"

patterns-established:
  - "Symmetry diff pattern: normalize workdir to token, strip variable block, diff normalized copies; save literal evidence before any live run"
  - "Fixture self-validation inline: each extractor ships its own --self-test that exercises PASS and FAIL paths"
  - "Task tracker detection stub: task_tracker_observation_count/action_count emitted as 0 by default; 12-02 will confirm whether Arm B emits these"
  - "usage_present detection: scans top-level, observation, llm_response, metadata sub-keys; 12-02 will confirm P3 feasibility"

# Metrics
duration: 5min
completed: 2026-06-02
---

# Phase 12 Plan 01: Harness + Preflight Summary

**Rust pilot harness built: symmetric Arm A/B prompts (control block verified byte-identical by literal diff), gitignored arm-isolated workspaces, and metrics_extractor.py (550 lines, 1-based indexing, self-validated on synthetic fixture)**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-06-02T00:16:25Z
- **Completed:** 2026-06-02T00:21:00Z
- **Tasks:** 3/3
- **Files modified:** 9 created, 1 modified

## Accomplishments

- METH-01 prompt symmetry foundation established: Arm A and Arm B Rust prompts share a byte-identical control block (goal, std-only constraint, port 8080, canonical curl→hello test); only the plan/self-plan block differs; PROMPT-DIFF-rust.txt ends with `CONTROL-BLOCK SYMMETRY: PASS`
- METH-02 workspace isolation: `oh-workdir-planning/` gitignored; `arm-a/rust` and `arm-b/rust` are empty isolated workspaces ready for 12-02 live runs
- METH-03 metrics_extractor.py written (550 lines), self-validated: clean fixture → honesty_gate PASS + curl_hello.pass=true + event_index=5 (1-based); dirty source=user ActionEvent → honesty_gate FAIL at index 2

## Task Commits

1. **Task 1: Preflight — gitignore + arm-isolated empty workspaces** — `8fc7a65` (chore)
2. **Task 2: Write both Rust prompts + mandatory symmetry diff** — `b55c88a` (feat)
3. **Task 3: Write and self-validate metrics_extractor.py** — `b4ead0b` (feat)

**Plan metadata:** (see below — docs commit)

## Files Created/Modified

- `.gitignore` — appended `oh-workdir-planning/` (parallel to existing oh-workdir-* entries)
- `.planning/phases/12-harness-rust-pilot/task-prompts/CONTROL-BLOCK-rust.txt` — shared byte-identical control block (goal + constraints + curl canonical test)
- `.planning/phases/12-harness-rust-pilot/captured-planning/rust/arm-a/planning-artifact/claude-plan.md` — Arm A input: mechanical 3-step decomposition from v1.2 task1/2/3 prompts
- `.planning/phases/12-harness-rust-pilot/captured-planning/rust/arm-a/planning-artifact/oh-prompt.txt` — Arm A OH prompt: control block + 3 numbered steps with single-session state-handoff
- `.planning/phases/12-harness-rust-pilot/captured-planning/rust/arm-b/planning-artifact/oh-goal-prompt.txt` — Arm B OH prompt: control block + "Plan your own implementation steps using the task tracker, then execute each step. Do not ask for confirmation between steps."
- `.planning/phases/12-harness-rust-pilot/task-prompts/PROMPT-DIFF-rust.txt` — literal diff evidence: workdir masked, plan block stripped, diff shows 0 differences, ends `CONTROL-BLOCK SYMMETRY: PASS`
- `.planning/phases/12-harness-rust-pilot/metrics_extractor.py` — full JSONL extractor (550 lines): TerminalAction count, event counts, wall-clock, LLM-call-gap stats, error-fix cycles, honesty gate, curl_hello canonical test, usage_present, task_tracker counts — all indices 1-based
- `captured-planning/rust/arm-a/` and `arm-b/` artifact tree skeletons (`.gitkeep` files)

## Decisions Made

- **Arm A conversion is mechanical**: v1.2 task1-scaffold / task2-server / task3-buildtest content mapped to Steps 1/2/3 with single-session state-handoff phrasing added (e.g., "After Step 1, the rust-server/ directory exists"). No new planning detail. No scaffolded source (unaided discipline).
- **Control block uses `__WORKDIR__` token for diff normalization**: The PROMPT-DIFF-rust.txt masks arm-specific paths back to the token before diffing, so the path substitution is not counted as an asymmetry. Both prompts then substitute the real path.
- **metrics_extractor.py self-validates via `--self-test` flag**: 6-event synthetic fixture in-process; no external test file required. Covers: source=user MessageEvent not flagged (Pitfall 13), 1-based index on curl observation (event #5), PASS/FAIL gate.
- **task_tracker_observation_count and usage_present as stub detectors**: emitted in metrics.json to resolve open unknowns #1 and #2 when 12-02 runs live; 12-02 reads these fields to confirm P3 (token metrics) feasibility and TaskTracker emission.

## Deviations from Plan

None — plan executed exactly as written. All three tasks completed in the specified order with no unplanned additions or scope changes.

## Issues Encountered

None. The symmetry diff was clean on first attempt (diff exit 0 immediately). Self-validation passed on first run.

## Next Phase Readiness

- **12-02 is unblocked**: Both arm prompts exist and are verified symmetric. Both `oh-workdir-planning/arm-a/rust` and `arm-b/rust` are empty and gitignored. `metrics_extractor.py` is ready to parse the JSONL captures.
- **Before each 12-02 run**: verify the relevant workspace is empty (Pitfall 6/9 — workspace-state leakage) and restart or counterbalance litellm proxy (Pitfall — KV-cache warmth).
- **No blockers**: host toolchains (rustc/cargo 1.95.0), LLM proxy (qwen-35b), and OpenHands headless CLI all verified in prior milestones.

---
*Phase: 12-harness-rust-pilot*
*Completed: 2026-06-02*
