# 12-02 SUMMARY — Run both arms live on the Rust pilot

**Status:** COMPLETE. Both arms captured; both open unknowns resolved.
**Date:** 2026-06-02. Model `openai/qwen-35b`, OpenHands 1.16 headless default CodeActAgent, one invocation per arm.

## Outcome

| Arm | Planning | Wall-clock* | TerminalActions | Tracker events | Canonical curl | Notes |
|-----|----------|-------------|-----------------|----------------|----------------|-------|
| B (self-plan, ran 1st / cold) | OpenHands self-plans via task_tracker | ~60s | 11 | 7 obs / 14 actions | **PASS** (`hello`, exit 0, #33) | 1 file_editor AgentError, recovered |
| A (Claude plan embedded, ran 2nd / warm) | Claude's numbered plan supplied | ~49s | 14 | 0 | **PASS** (`hello`, exit 0, #25) | 2 multi-command errors, self-corrected |

*Timing carries a cache-warmth caveat (Arm A ran second on a warmer cache; proxy not restarted). Not a clean planning signal for the pilot — Phase 13 counterbalances run order. Derived from JSONL timestamps; `~14–32s/call` never cited.

## Open unknowns — both RESOLVED

- **#1 TaskTracker emission: YES.** Arm B emitted 7 `TaskTrackerObservation` + 14 tracker actions (first at event #2). The 35B self-plans at the chosen Arm B phrasing → no Arm B prompt change needed for Phase 13.
- **#2 token `usage` in JSONL: NO** (both arms). → **P3 token metrics dropped**; rely on P1/P2 metrics.

## Requirement evidence (METH-02)

Both arms ran as single CodeActAgent invocations in arm-isolated, verified-empty, gitignored workspaces; run order + proxy state + cache caveat documented in RUN-NOTES; both produced real non-empty JSONL with Action+Observation events; honesty preview shows 0 non-agent ActionEvents in both. First-run-is-the-run (no cherry-picking); no manual edits.

## Notable (feeds Phase 13 + 부록 D)

Both planning regimes produced a working Rust server (curl→hello) on the 35B. Early differentiators visible: Arm B spent actions on task-tracker self-planning (7 obs/14 actions) then executed; Arm A executed Claude's plan directly (0 tracker) but hit 2 multi-command-chaining errors it self-corrected. TerminalAction counts (B 11 / A 14) and error profiles differ — exactly the comparison material the milestone studies. (n=1 pilot; the full study repeats per the n=3-where-feasible policy.)

## Next

12-03: blocking `source=agent` honesty gate → run `metrics_extractor.py` over both JSONLs → `metrics.json` ×2 + `comparison.json` → extract Arm B self-plan artifact → host re-run → CAPTURE-MANIFEST.md (records both unknown resolutions) → human-verify checkpoint → commit `captured-planning/rust/`.
