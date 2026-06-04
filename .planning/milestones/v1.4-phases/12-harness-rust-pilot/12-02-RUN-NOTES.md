# 12-02 RUN-NOTES — Rust Pilot, Both Arms (live 35B)

Run date: 2026-06-02. Model: `openai/qwen-35b` via litellm proxy @127.0.0.1:4000. OpenHands 1.16 headless, default **CodeActAgent**, `--headless --json --yolo --override-with-envs`. ONE invocation per arm (no per-task split). Judged from JSONL, not exit code.

## Run order & proxy state (METH-02 / Pitfall 3)

- Strategy chosen: **Arm B first (cold cache), then Arm A** (B-first counterbalance for Rust per STATE v1.4 decisions). The litellm proxy was **NOT** restarted between arms (it is an externally-managed service).
- **Cache-warmth caveat (disclosed):** because the proxy was not restarted and Arm A ran second, Arm A benefited from a warmer KV/prefix cache than Arm B. Per-arm wall-clock therefore should NOT be read as a planning-quality signal in isolation for this pilot; the full study (Phase 13) counterbalances run order across F#/Scala. Timing here is recorded as derived from JSONL timestamps and labelled, not as a clean planning metric.
- Arm B start 09:24:13 → settle 09:25:13. Arm A start 09:31:49 → settle 09:32:38.

## Arm B — OpenHands self-plan (ran first)

- command: `OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openai/qwen-35b LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy OPENHANDS_WORK_DIR=.../oh-workdir-planning/arm-b/rust openhands --headless --json --yolo --override-with-envs -t "$(sed __WORKDIR__→arm-b/rust oh-goal-prompt.txt)" 2>arm-b/rust-run.stderr.log | tee arm-b/rust-run.jsonl`
- workspace-empty pre-run: `oh-workdir-planning/arm-b/rust` listed empty (only `./ ../`) before launch.
- settle: final MessageEvent (no FinishAction — normal for OH 1.16, as in v1/v1.2/v1.3). wall-clock 09:24:13 → 09:25:13 (~60s).
- jsonl-counts: kinds={MessageEvent:2, ActionEvent:19, ObservationEvent:18, AgentErrorEvent:1} TerminalActions=11. (1 AgentErrorEvent = a `file_editor` attempt that recovered to bash — same harmless pattern as v1.2/v1.3.)
- **canonical test (curl localhost:8080/): PASS** — JSONL ObservationEvent (event #33, 1-based) content `hello\nEXIT_CODE=0`, exit_code 0. (Two more curl observations at #31/#35 also returned `hello`.)
- disk: `oh-workdir-planning/arm-b/rust/src/main.rs` written by the agent.

## Arm A — Claude-authored plan embedded (ran second)

- command: same invocation pattern with `OPENHANDS_WORK_DIR=.../arm-a/rust` and `-t "$(sed __WORKDIR__→arm-a/rust oh-prompt.txt)"` → `arm-a/rust-run.jsonl`.
- workspace-empty pre-run: `oh-workdir-planning/arm-a/rust` listed empty before launch; isolated from arm-b (separate OPENHANDS_WORK_DIR; Arm A could not write into arm-b).
- settle: final MessageEvent. wall-clock 09:31:49 → 09:32:38 (~49s; warm-cache caveat above).
- jsonl-counts: kinds={MessageEvent:2, ActionEvent:14, ObservationEvent:14} TerminalActions=14, NonZeroExits=2.
- error-and-fix: 2 non-zero ObservationEvents at #17/#19 — `Cannot execute multiple commands at once` (the agent tried to chain commands; the runtime rejected it; the agent recovered by running them separately). A real, captured self-correction.
- **canonical test (curl localhost:8080/): PASS** — JSONL ObservationEvent (event #25, 1-based) content `hello\nexit_code: 0`, exit_code 0 (also #27).
- task-tracker events: **0** — Arm A did not self-plan via the tracker (it executed the supplied Claude plan). This is the expected, meaningful qualitative contrast with Arm B.

## Open unknown #1 — does the 35B emit TaskTracker events? → RESOLVED: YES

- Arm B JSONL: **TaskTrackerObservation = 7, TaskTracker actions/tool-uses = 14**, first task-tracker event at event #2 (1-based). The 35B self-plans via the `task_tracker` tool at the chosen Arm B phrasing ("Plan your own implementation steps using the task tracker, then execute each step").
- **No Arm B prompt adjustment / re-pilot needed.** Phase 13 can use the Arm B prompt as-is. The Arm B self-plan artifact for Phase 13 is the task-tracker task list (extractable from the TaskTracker events).
- Arm A JSONL: 0 task-tracker events (plan supplied) — confirms the arms differ on the planning axis as designed.

## Open unknown #2 — is token `usage` present in the JSONL? → RESOLVED: NO

- Scan of both JSONLs (top-level `usage`, and under `observation`/`metadata`/`llm_response`): `usage_present = False` for both arms; no sample found.
- **Decision: P3 token metrics are NOT feasible** for this study. Drop token counts from the metric set; rely on the P1/P2 metrics (TerminalAction count, event count, wall-clock, LLM-call gaps, error-fix cycles, AgentErrorEvent count, canonical pass/fail).

## Honesty preview (formal gate runs in 12-03)

- `source=agent` quick scan: Arm A 14 ActionEvents / 0 non-agent; Arm B 19 ActionEvents / 0 non-agent. (The lone `source=user` event per arm is the initial task-prompt MessageEvent, excluded from the gate.) No manual edits to any agent file. Both first-runs are THE runs (no re-runs; no cherry-picking). `~14–32s/call` is NOT cited as a measurement.

## Pilot outcome

Harness proven on Rust: both arms captured clean JSONL as single CodeActAgent invocations in isolated empty workspaces; both passed the canonical curl test; both open unknowns resolved (TaskTracker emits ✓; no token usage → P3 dropped). Ready for 12-03 (honesty gate + metrics_extractor + manifest + commit).
