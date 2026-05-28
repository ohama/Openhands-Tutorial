---
phase: 02-environment-setup-and-verification
plan: "02"
subsystem: environment
tags: [openhands, headless, litellm, qwen-local, dotnet, localworkspace, jsonl, tool-call]

# Dependency graph
requires:
  - phase: 02-environment-setup-and-verification
    plan: "01"
    provides: CLI 1.16.0 confirmed on PATH, litellm proxy qwen-local confirmed at 127.0.0.1:4000
provides:
  - End-to-end headless tool-call proof (SETUP-01/02/03/04 all satisfied)
  - Verbatim JSONL evidence: echo OPENHANDS_PING_OK action+observation (PING PASS)
  - Verbatim JSONL evidence: dotnet 10.0.203 in agent observation (DOTNET PASS)
  - Confirmed working invocation shape (env-var Mode A, --override-with-envs)
  - Confirmed bare `dotnet` works in agent PTY (no absolute path needed in Phase 3/4)
  - 02-VERIFICATION-EVIDENCE.md — authoritative source of truth for all captured outputs
affects: [02-03, 02-04, 02-05, 03-run-capture, 04-worked-example-chapter]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Headless invocation: LLM_MODEL/LLM_BASE_URL/LLM_API_KEY env vars + --override-with-envs (required)"
    - "JSONL parsing: ev.get('action') for ActionEvent; ev.get('observation') for ObservationEvent"
    - "LocalWorkspace PTY inherits host PATH — bare `dotnet` resolves correctly without absolute path"
    - "OPENHANDS_SUPPRESS_BANNER=1 suppresses SDK banner from stderr for clean JSONL capture"

key-files:
  created:
    - .planning/phases/02-environment-setup-and-verification/02-VERIFICATION-EVIDENCE.md
    - .planning/phases/02-environment-setup-and-verification/02-02-SUMMARY.md
  modified:
    - .gitignore (added oh-workdir/ to ignore scratch artifacts)

key-decisions:
  - "bare `dotnet` (not absolute path) works in agent LocalWorkspace PTY — Phase 3/4 tasks do NOT need /opt/homebrew/bin/dotnet prefix"
  - "--override-with-envs is REQUIRED on openhands --headless; without it env vars are silently ignored"
  - "OPENHANDS_SUPPRESS_BANNER=1 should be set when tee-ing JSONL to avoid banner lines mixing with JSON"
  - "oh-workdir/ scratch dir added to .gitignore — JSONL artifacts stay local, not committed"
  - "Each headless run completed in 14-15 seconds (not ~240s+) — qwen-local inference was fast during this session"

patterns-established:
  - "Capture pattern: pipe openhands JSONL to tee for both display and file save; stderr redirected to separate log"
  - "Verification pattern: python3 parse loop checking ev.get('action') and ev.get('observation') against full serialized JSON"

# Metrics
duration: 9min
completed: 2026-05-27
---

# Phase 2 Plan 02: End-to-End Headless Verification Summary

**Headless OpenHands CLI (env-var Mode A via --override-with-envs) calls qwen-local tool successfully: echo OPENHANDS_PING_OK action+observation confirmed (PING PASS) and dotnet 10.0.203 in agent PTY confirmed (DOTNET PASS) — all four SETUP criteria satisfied**

## Performance

- **Duration:** ~9 min
- **Started:** 2026-05-27T08:00:06Z
- **Completed:** 2026-05-27T08:09:00Z
- **Tasks:** 3
- **Files modified:** 3 (02-VERIFICATION-EVIDENCE.md, 02-02-SUMMARY.md, .gitignore)

## Accomplishments

- Ran headless openhands with `echo OPENHANDS_PING_OK` task; JSONL captured TerminalAction + TerminalObservation with sentinel in observation — **PING PASS** (SETUP-01/02/04)
- Ran headless openhands with `dotnet --version` task; JSONL captured dotnet 10.0.203 in TerminalObservation — **DOTNET PASS** (SETUP-03)
- Confirmed `--override-with-envs` correctly routes all three `LLM_*` env vars to the litellm proxy at 127.0.0.1:4000
- Confirmed LocalWorkspace PTY inherits host PATH; bare `dotnet` resolves without absolute path — no Phase 3/4 fallback needed
- Wrote 02-VERIFICATION-EVIDENCE.md with verbatim ActionEvent + ObservationEvent JSONL, timing, and fallback status

## SETUP Criteria Mapping

| Criterion | Description | Evidence | Status |
|-----------|-------------|---------|--------|
| SETUP-01 | OpenHands CLI installed and callable | `openhands --version` → 1.16.0 (from 02-01) | PASS |
| SETUP-02 | LLM gateway reachable and tool-calling works | PING run: action+observation with qwen-local | PASS |
| SETUP-03 | .NET SDK accessible in agent workspace | dotnet run: 10.0.203 in TerminalObservation | PASS |
| SETUP-04 | Full pre-run checklist with verbatim evidence | 02-VERIFICATION-EVIDENCE.md contains all 4 items | PASS |

## Task Commits

Tasks 1-2 produced JSONL evidence only (saved to gitignored oh-workdir/). Task 3 wrote the evidence and summary files. Final commit covers both files + .gitignore.

1. **Task 1: Headless tool-call ping** — echo action+observation captured, PING PASS confirmed
2. **Task 2: Agent runs dotnet --version** — 10.0.203 in observation, DOTNET PASS confirmed
3. **Task 3: Write 02-VERIFICATION-EVIDENCE.md + 02-02-SUMMARY.md** — committed in `docs(02-02)` commit

## Files Created/Modified

- `.planning/phases/02-environment-setup-and-verification/02-VERIFICATION-EVIDENCE.md` — verbatim real outputs; authoritative source of truth for Phase 3/4 doc writing
- `.planning/phases/02-environment-setup-and-verification/02-02-SUMMARY.md` — this file
- `.gitignore` — added `oh-workdir/` line (scratch artifacts not committed)

## Decisions Made

- **No dotnet PATH fallback needed:** Bare `dotnet` works in agent PTY (host PATH inherited). Plan's fallback to `/opt/homebrew/bin/dotnet` was documented but not needed. Phase 3/4 plans can use bare `dotnet`.
- **`--override-with-envs` is mandatory:** Without it, all three `LLM_*` env vars are silently ignored and the run fails or uses wrong settings. This flag must appear in all headless invocations.
- **Timing note:** Plan warned ~240s+ per run; actual was 14-15s. The model was warm (MLX launchd already loaded weights). Phase 3 timing estimates should use real observed values, not the worst-case plan estimate.
- **`OPENHANDS_SUPPRESS_BANNER=1` recommended:** The SDK banner printed to stderr is harmless but should be suppressed when parsing JSONL for clean output.

## Deviations from Plan

None — plan executed exactly as written. All three tasks completed on first attempt. No fallbacks were required (dotnet bare path worked, no auth errors, no missing observations).

The only minor variance: wall-clock times were 14-15 seconds per run, not the ~240s+ the plan warned. This is a positive deviation — qwen-local was faster than worst-case.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Phase 3/4 Notes (Downstream Implications)

1. **Working invocation for Phase 3 agent run:**
   ```sh
   OPENHANDS_SUPPRESS_BANNER=1 \
   LLM_MODEL="openai/qwen-local" \
   LLM_BASE_URL="http://127.0.0.1:4000/v1" \
   LLM_API_KEY="dummy" \
   OPENHANDS_WORK_DIR="<project-dir>" \
   openhands --headless --json --yolo --override-with-envs \
     -t '<task>'
   ```

2. **dotnet PATH:** Bare `dotnet` commands work in agent tasks — no absolute path prefix needed.

3. **Evidence source:** `02-VERIFICATION-EVIDENCE.md` is the authoritative real-output record. The Phase 4 Korean chapter on 3부/4부 setup should quote from this file.

## Next Phase Readiness

Ready for 02-03 (next plan in Phase 2). The capture gate proof is complete:

- OpenHands → qwen-local tool-call path is verified end-to-end
- dotnet is accessible in agent workspace
- The exact Phase 3 invocation shape is confirmed working
- 02-VERIFICATION-EVIDENCE.md provides all verbatim outputs for doc writing

No blockers.

---
*Phase: 02-environment-setup-and-verification*
*Completed: 2026-05-27*
