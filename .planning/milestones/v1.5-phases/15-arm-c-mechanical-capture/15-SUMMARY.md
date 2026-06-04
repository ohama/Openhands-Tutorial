---
phase: 15-arm-c-mechanical-capture
plan: "15"
subsystem: study-capture
tags: [openHands, qwen-35b, rust, a-b-comparison, planning, capture, gsd]

requires:
  - phase: 12-harness-rust-pilot
    provides: control block, metrics_extractor.py, Arm A/B capture procedure
provides:
  - Arm C (mechanical) live 35B capture — canonical PASS, honesty PASS, unaided authorship
  - captured-planning/rust/arm-c/ full artifact tree (jsonl, metrics, final-source, test-output)
affects:
  - planning-process-comparison.md (Arm C-mech promoted candidate → captured)

key-files:
  created:
    - .planning/milestones/v1.4-phases/15-arm-c-mechanical-capture/15-CAPTURE-MANIFEST.md
    - .planning/milestones/v1.4-phases/15-arm-c-mechanical-capture/15-SUMMARY.md
    - captured-planning/rust/arm-c/logs/run.jsonl + run.stderr.log
    - captured-planning/rust/arm-c/metrics.json
    - captured-planning/rust/arm-c/final-source/{Cargo.toml,Cargo.lock,src/main.rs}
    - captured-planning/rust/arm-c/test-output.txt
    - captured-planning/rust/arm-c/planning-artifact/ (oh-prompt, gsd-mechanical-plan, RESEARCH, gsd-01-PLAN, PROMPT-DIFF)

key-decisions:
  - "Arm C-mech promoted from .planning/docs candidate to a formal phase (15) with a real captured-planning/arm-c tree, run under the Phase-12 procedure"
  - "Solo n=1 follow-up capture (2026-06-04) — NOT counterbalanced vs Arm A/B (2026-06-02); cross-arm wall-clock comparison explicitly invalidated"
  - "First run IS the run: no re-runs, no cherry-pick, no hand-fix of agent source (study honesty discipline)"

duration: ~12min
completed: 2026-06-04
---

# Phase 15: Arm C (mechanical) Capture — Summary

**The 35B passed a std-only Rust HTTP server task given a code-free expert plan (GSD pitfall
guidance, no source) — writing its own implementation unaided and self-correcting 2 real Rust
compile errors. Canonical curl test PASS (event #31), honesty gate PASS (17/17 ActionEvents
source=agent).**

## What happened

1. **Promoted** Arm C-mech from a `.planning/docs/` candidate to formal **Phase 15** with a
   `captured-planning/rust/arm-c/` tree mirroring the Phase 12 study structure.
2. **Verified infra:** rust 1.95, OpenHands 1.16, litellm proxy (qwen-35b) live. (Colima was
   down but not needed — OH ran on the local workspace runtime, as in the Phase 12 runs.)
3. **Captured live, single invocation** into an isolated empty gitignored workspace, replicating
   the 12-02 command (`--headless --json --yolo --override-with-envs`, env-injected LLM_* + WORK_DIR).
4. **Extracted metrics** with the Phase 12 `metrics_extractor.py` (1-based events).
5. **Independently re-verified** on the host (fresh `cargo run` + two curls).

## Result

| Metric | Value |
|--------|-------|
| canonical curl_hello | **PASS** (event #31, exit 0); second request also PASS (loop survives) |
| honesty gate | **PASS** (17 ActionEvents, 0 non-agent) |
| Cargo.toml [dependencies] | empty (std-only ✓) |
| total events / TerminalActions | 36 / 17 |
| error-fix cycles | 3 (1 `cat` flag typo, 2 real Rust compile errors self-corrected) |
| TaskTracker events | 0 (supplied-plan arm — executed plan, didn't self-plan) |
| wall clock (derived) | 66.09s (NOT comparable to Arm A/B — see caveat) |

## Key finding

The 35B wrote an implementation that **differs** from the withheld GSD reference (used
`stream.read(&buf)` not `BufReader::read_line`; bound `0.0.0.0` not `127.0.0.1`; `.expect`
not `?`) — but applied the prose framing guidance **correctly** (Content-Length, Connection:
close, CRLF — no curl-hang, no EOF deadlock). It translated the failure-mode guidance into its
own std-only Rust. The only friction was ordinary Rust compile errors (unused import, missing
`Read` trait import) which it diagnosed and fixed itself.

→ Confirms the memory note "35B distribution-not-size": Rust is in-distribution, so the 35B
writes it unaided; the code-free expert plan helped it sidestep the protocol pitfalls without
handing over the answer. **Arm C-mech is a valid, study-usable arm.**

## Honesty / scope caveats (disclosed)

- **n=1 solo capture**, 2026-06-04. NOT counterbalanced against Arm A/B (2026-06-02, different
  cache state). Cross-arm **timing** comparisons are invalid; this is a feasibility/qualitative
  capture.
- First run is THE run. No manual edits to agent source. `~14–32s/call` v1 prediction not cited.
- Control-block symmetry to the study canonical proven (`PROMPT-DIFF.txt` → PASS).

## Next options

- Repeat under a counterbalanced run order (restart proxy, interleave with an Arm A re-run) if a
  defensible **timing** comparison across A/A·B/C is ever wanted (would need n>1).
- Extend Arm C-mech to F#/Scala (Phase 13 examples) to see if pitfall-guidance value holds for
  the OOD/in-distribution split.
