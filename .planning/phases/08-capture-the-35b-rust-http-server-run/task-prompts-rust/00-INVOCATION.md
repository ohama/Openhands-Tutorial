# 35B Rust Run — Invocation Reference

## Per-task command pattern

  OPENHANDS_SUPPRESS_BANNER=1 \
    LLM_MODEL="openai/qwen-35b" \
    LLM_BASE_URL="http://127.0.0.1:4000/v1" \
    LLM_API_KEY="dummy" \
    OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir-rust" \
    openhands --headless --json --yolo --override-with-envs \
    -t "$(cat task-prompts-rust/<prompt-file>)" \
    2>oh-workdir-rust/<task>.stderr.log \
    | tee oh-workdir-rust/<task>.jsonl

## Key notes

- `--override-with-envs` is REQUIRED (configures the LLM from env vars).
- `--yolo` runs autonomously (no confirmation prompts).
- `--headless --json` emits JSONL events to stdout — captured by `tee` into a per-task .jsonl file.
- Each invocation is a fresh ZERO-MEMORY conversation: the agent does not remember
  prior tasks. Files persist on disk (so task2 can `cat` what task1 produced); the
  agent rediscovers state via `ls`/`cat`.
- Bash-only file writes are enforced via the per-prompt IMPORTANT note (file_editor
  errors in this OpenHands setup — it requires a security_risk field that fails
  validation).
- The CLI exits 0 REGARDLESS of task success — DO NOT judge outcome from exit code.
  Judge ONLY from the JSONL contents (FinishAction present, exit codes inside
  TerminalObservations, actual command output).
- Run each invocation in the BACKGROUND (run_in_background=true) and POLL the JSONL
  until the run settles (FinishAction event appears, or no new events for ~60s of
  sustained idle, or ConversationErrorEvent).
- 35B per-LLM-call timing on this hardware ≈ 5.3s (from v1 + v1.1 captured runs).
  Budget ~4–8 minutes per complex task; up to ~15 minutes if the agent gets stuck
  on borrow-checker iterations or runtime hangs. Full run estimate: 15–40 minutes.

## Per-task JSONL filenames

| Task | Prompt file | JSONL filename |
|------|-------------|----------------|
| task1-scaffold       | task-prompts-rust/task1-scaffold.txt       | oh-workdir-rust/task1-scaffold.jsonl |
| task2-server         | task-prompts-rust/task2-server.txt         | oh-workdir-rust/task2-server.jsonl |
| task2-server-scaffold (fallback only) | task-prompts-rust/task2-server-scaffold.txt | oh-workdir-rust/task2-server-scaffold.jsonl |
| task3-buildtest      | task-prompts-rust/task3-buildtest.txt      | oh-workdir-rust/task3-buildtest.jsonl |

Stderr is captured in parallel as oh-workdir-rust/<task>.stderr.log for each.

## Scaffold-fallback policy summary (full rules in 08-RESEARCH.md §5)

The scaffold (task2-server-scaffold.txt) is invoked ONLY if ALL the following are
true after the unaided task2 attempt:

1. The agent's cargo build (in task3) fails on the SAME root error class across
   3+ consecutive build attempts within task3 (e.g., always E0382 borrow conflict,
   or always the same syntax error).
2. The error variations show no syntactic progress — the agent is cycling on
   identical fix attempts with no new diagnostic reasoning.
3. The JSONL shows the agent is stuck (repeated identical commands).

Do NOT trigger scaffold fallback if:
- The agent is making diverse fix attempts (even if all failing) — that is genuine
  error-and-fix and is the desired chapter material.
- The build error changes between attempts — the agent is making progress.
- The agent hits a runtime hang (curl never returns) — give it one more attempt;
  task3 prompt already softly hints "if curl hangs, the server may be blocking".

If fallback IS triggered, that fact MUST be disclosed in CAPTURE-MANIFEST.md with
the failure reasons documented. did-write-server-unaided = NO.
