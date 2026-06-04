# 12-03 SUMMARY — Capture gate (Rust pilot)

**Status:** COMPLETE (human-verified + approved 2026-06-02).
**Date:** 2026-06-02.

## Outcome

The Phase 12 pilot capture gate is CLOSED. Both Rust arms passed the mechanical `source=agent` honesty gate, metrics were extracted, the Arm B self-plan was captured verbatim, both arms re-ran clean on the host, and `CAPTURE-MANIFEST.md` records the result + both open-unknown resolutions.

## Artifacts committed (under `.planning/phases/12-harness-rust-pilot/captured-planning/`)

- `rust/arm-a/` and `rust/arm-b/`: `logs/run.jsonl` + `run.stderr.log`, `final-source/` (agent-written Cargo project), `test-output.txt` (host re-run), `metrics.json`
- `rust/arm-b/planning-artifact/oh-self-plan.md` — the TaskTracker self-plan extracted verbatim (4 tasks)
- `rust/comparison.json` — Arm A vs Arm B
- `CAPTURE-MANIFEST.md` — gate record

## Results (from comparison.json / metrics.json)

| Arm | Events | TerminalActions | Wall (s, derived) | curl_hello | honesty_gate |
|-----|--------|-----------------|-------------------|------------|--------------|
| A (Claude plan) | 30 | 14 | 48.3 | PASS | PASS |
| B (self-plan) | 40 | 12 | 59.0 | PASS | PASS |

Wall delta A−B = −10.7s (Arm A faster) — **cache-warmth caveat applies** (Arm A ran second/warm; proxy not restarted). Recorded as derived-from-JSONL, NOT a clean planning signal; Phase 13 counterbalances run order. `~14–32s/call` not cited.

## Open unknowns — resolved & recorded in the manifest

- **#1 TaskTracker emission: YES** — Arm B emitted TaskTracker events (first at event #2). The 35B self-plans at the chosen Arm B phrasing; no prompt change needed for Phase 13.
- **#2 token `usage` in JSONL: NO** → **P3 token metrics dropped**.

## Deviations

- `metrics_extractor.py` patched once (auto-fix): skip ObservationEvents with `exit_code=None` (runtime multi-command rejections) when detecting the canonical curl result, so the real curl outcome is found. Self-test still passes. Committed with the artifacts.

## Honesty

source=agent gate PASS on both (0 non-agent ActionEvents; the lone source=user per arm is the task-prompt MessageEvent). No manual edits to agent files. No cherry-picking (both arms first-and-only runs). Live scratch (`oh-workdir-planning/`) stays gitignored; only copies committed. deploy.yml untouched.

## Phase 12 result

METH-01/02/03 satisfied; harness proven on the Rust pilot; both unknowns resolved. Phase 13 (F# + Scala full study) is unblocked.
