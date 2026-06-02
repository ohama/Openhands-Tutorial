# Phase 12 Rust Pilot — CAPTURE-MANIFEST

Capture date: 2026-06-02
Study: v1.4 Planning Comparison (Rust pilot)
Author: Claude (Phase 12 execution agent)

---

## EVENT-NUMBERING CONVENTION

**All event numbers in this manifest are 1-based: JSONL line N = event #N.**
The first JSONL line is event #1. This matches metrics_extractor.py v1.4 output.
(Pitfall 8/11: the ARCHITECTURE.md reference uses 0-based `events.index()`; this
manifest and all extractor output use 1-based.)

---

## Study Design

**Research question (framing rule):** "Does an expert-authored plan help the 35B
execute?" — NOT "Claude plans better." Arm A provides the agent with a complete,
Claude-authored step-by-step plan embedded in the prompt; Arm B asks the 35B to
self-plan via the task tracker and then execute. The expert-plan benefit is what
is being measured; the planning origin (Claude vs. 35B) is the variable.

**Design:**
- v1.4 A/B parallel arms, Rust HTTP server task ("respond 'hello' on port 8080")
- **Arm A:** Expert-authored Claude plan embedded in prompt (CONTROL-BLOCK)
- **Arm B:** 35B self-plans via task tracker, then executes
- Single-session, one CodeActAgent invocation per arm (no per-task split)
- **n = 1 single-run observation** — this is a pilot, not a full study

---

## Version Block

| Field | Value |
|-------|-------|
| OpenHands CLI | 1.16.0 (banner output from `openhands --version`) |
| SDK | OpenHands SDK v1.21.0 |
| Model | `openai/qwen-35b` |
| LLM_BASE_URL | `http://127.0.0.1:4000/v1` (litellm proxy) |
| Agent | CodeActAgent (default headless) |
| Flags | `--headless --json --yolo --override-with-envs` |
| Capture date | 2026-06-02 |

---

## Run Conditions and Order

| Field | Arm B (ran FIRST) | Arm A (ran SECOND) |
|-------|-------------------|---------------------|
| Workspace | `oh-workdir-planning/arm-b/rust` | `oh-workdir-planning/arm-a/rust` |
| Pre-run workspace | Empty (verified: only `./` `../` listed) | Empty (verified: isolated from Arm B) |
| Clock start | 09:24:13 | 09:31:49 |
| Clock settle | 09:25:13 | 09:32:38 |
| Wall clock (derived) | 59.04s | 48.3s |
| Settled by | idle-timeout (no FinishAction — normal for OH 1.16) | idle-timeout |

**Run order rationale:** Arm B ran first (cold cache) for the Rust pilot; Arm A ran
second. This is the B-first counterbalance strategy per STATE v1.4 decisions.

**Proxy state:** The litellm proxy was NOT restarted between arms (externally-managed
service). Arm A therefore benefited from a warmer KV/prefix cache.

**Cache-warmth caveat (DISCLOSED):** Because the proxy was not restarted and Arm A
ran second, Arm A's wall-clock is shorter (48.3s vs 59.0s). This wall-clock
difference MUST NOT be read as a planning-quality signal in isolation for this pilot.
Timing here is recorded as derived from JSONL timestamps and labelled accordingly.
The full study (Phase 13) counterbalances run order across F#/Scala to control for
this effect.

**Arm isolation confirmed:** Each arm had a separate `OPENHANDS_WORK_DIR`; Arm A
could not write into Arm B's workspace.

---

## Honesty Gate Results

**Gate: PASS on both Rust JSONLs.**

| Arm | ActionEvents checked | Non-agent ActionEvents | Result |
|-----|---------------------|------------------------|--------|
| Arm A | 14 | 0 | PASS |
| Arm B | 19 | 0 | PASS |

**Arm A note:** Event #1 is a MessageEvent with source=user (the task-prompt delivery).
MessageEvents are NOT ActionEvents — the gate correctly excludes them (Pitfall 13).
All 14 ActionEvents in Arm A have source=agent.

**Arm B note:** Event #1 is likewise a source=user MessageEvent (excluded). All 19
ActionEvents in Arm B have source=agent.

No manual edits were made to any agent-written file. Both first-runs ARE the runs
(no re-runs, no cherry-picking). Both arms captured cleanly in a single invocation.

---

## Per-Arm Summary Table

Timing derived from JSONL event timestamps (first_event_ts → last_event_ts).
**NOT the v1 per-call prediction from the prior Rust pilot** — that earlier timing
estimate does not appear as a measurement here (Pitfall 12).

| Metric | Arm A | Arm B |
|--------|-------|-------|
| Arm description | Expert-authored Claude plan embedded | 35B self-plans via task tracker |
| Total events | 30 | 40 |
| Event kinds | MessageEvent:2, ActionEvent:14, ObservationEvent:14 | MessageEvent:2, ActionEvent:19, ObservationEvent:18, AgentErrorEvent:1 |
| TerminalAction count | 14 | 12 |
| Wall clock (derived from JSONL) | 48.3s | 59.0s |
| Avg LLM-call gap (derived from JSONL obs→act gaps) | 2.11s | 2.29s |
| Error-fix cycles (nonzero exit → next agent action) | 0 | 0 |
| Command rejections (exit_code=None, multi-cmd) | 2 (#17, #19) | 0 |
| AgentErrorEvent count | 0 | 1 (#9: tool validation; recovered) |
| TaskTrackerObservation events | 0 | 7 (#3,5,7,17,23,27,39) |
| TaskTrackerAction events | 0 | 7 (#2,4,6,16,22,26,38) |
| canonical curl_hello | **PASS** (event #25, exit=0) | **PASS** (event #31, exit=0) |
| Honesty gate | PASS | PASS |

**Arm A command rejections detail:** Events #17 and #19 are ObservationEvents with
exit_code=None — the runtime rejected multi-command strings ("Cannot execute multiple
commands at once"). The agent recovered by splitting commands. These are NOT nonzero
exit_code errors; they are runtime rejections. Recorded as a real, captured
self-correction.

**Arm B AgentErrorEvent detail:** Event #9: tool validation error ("Failed to provide
security_risk field in tool 'terminal'"). The agent recovered by falling back to bash.
Same harmless pattern as v1.2/v1.3 runs.

---

## RESOLVED OPEN UNKNOWN #1 — Does Arm B emit TaskTrackerObservation events?

**RESOLVED: YES**

Arm B emitted 7 TaskTrackerObservation events and 7 TaskTrackerAction events
(14 task-tracker events total).

- First task-tracker event: event #2 (1-based) — a TaskTrackerAction `view` command
- Initial self-plan: event #4 — TaskTrackerAction `plan` with 4 tasks:
  1. Initialize Rust project with Cargo
  2. Implement HTTP server in main.rs
  3. Build the project
  4. Run canonical test: curl -s http://localhost:8080/

The 35B successfully used the task_tracker tool at the Arm B prompt phrasing ("Plan
your own implementation steps using the task tracker, then execute each step"). No
prompt re-pilot was needed. The task-list progression (todo → in_progress → done)
is captured verbatim in `captured-planning/rust/arm-b/planning-artifact/oh-self-plan.md`.

**Phase 13 implication:** The Arm B prompt can be used as-is for F#/Scala. The
self-plan artifact (task list) is extractable from TaskTracker events in the JSONL.

Arm A emitted 0 task-tracker events — it executed the supplied Claude plan as designed.
This confirms the arms differ on the planning axis.

---

## RESOLVED OPEN UNKNOWN #2 — Is token `usage` present in the JSONL?

**RESOLVED: NO**

Scan of both JSONLs (top-level `usage` key, and nested under `observation`,
`metadata`, `llm_response` sub-keys): `usage_present = False` for both arms.
No sample found.

**Decision: P3 token metrics are NOT feasible for this study.**
Token counts are dropped from the metric set. The study relies on P1/P2 metrics:
TerminalAction count, total event count, wall-clock (derived), LLM-call gaps
(derived), error-fix cycles, AgentErrorEvent count, and canonical pass/fail.

---

## Arm A Framing Reminder

Arm A embedded a complete, Claude-authored step-by-step plan in the prompt. The
question is whether this expert plan helps the 35B execute more efficiently — not
whether "Claude plans better than 35B." The expert-plan framing is the study's
independent variable; any observed difference must be interpreted through the lens of
the cache-warmth caveat (run order, proxy restart policy) disclosed above.

---

## Capture Completeness

| Artifact | Status |
|----------|--------|
| arm-a/logs/run.jsonl | Committed (copy of live oh-workdir-planning/arm-a/rust-run.jsonl) |
| arm-b/logs/run.jsonl | Committed (copy of live oh-workdir-planning/arm-b/rust-run.jsonl) |
| arm-a/logs/run.stderr.log | Committed |
| arm-b/logs/run.stderr.log | Committed |
| arm-a/metrics.json | Committed (honesty_gate=PASS, curl_hello=PASS) |
| arm-b/metrics.json | Committed (honesty_gate=PASS, curl_hello=PASS) |
| comparison.json | Committed |
| arm-a/final-source/ | Committed (agent-written, no edits; target/ excluded) |
| arm-b/final-source/ | Committed (agent-written, no edits; target/ excluded) |
| arm-a/test-output.txt | Committed (fresh host re-run: curl→hello PASS) |
| arm-b/test-output.txt | Committed (fresh host re-run: curl→hello PASS) |
| arm-b/planning-artifact/oh-self-plan.md | Committed (TaskTracker task list verbatim) |
| arm-a/planning-artifact/oh-prompt.txt | Pre-existing (CONTROL-BLOCK prompt) |
| arm-b/planning-artifact/oh-goal-prompt.txt | Pre-existing (goal prompt) |
| Live scratch oh-workdir-planning/ | Gitignored (NOT committed) |
| .github/workflows/deploy.yml | Untouched |

---

## PHASE 12 PILOT CAPTURE GATE: CLOSED

Both Rust metrics.json committed with `honesty_gate=PASS` and `canonical_tests.curl_hello`
recorded (PASS for both arms). Both open unknowns resolved. No fabricated values;
no hand-edited agent source; no cherry-picked runs; the v1 per-call timing estimate
is not cited as a measurement.

**Phase 13 (F#/Scala full study) is unblocked.**
