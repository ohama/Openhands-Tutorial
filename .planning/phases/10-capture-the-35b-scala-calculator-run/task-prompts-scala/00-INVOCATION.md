# 35B Scala Calculator Run — Invocation Reference

## Per-task command pattern

  OPENHANDS_SUPPRESS_BANNER=1 \
    LLM_MODEL="openai/qwen-35b" \
    LLM_BASE_URL="http://127.0.0.1:4000/v1" \
    LLM_API_KEY="dummy" \
    OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir-scala" \
    openhands --headless --json --yolo --override-with-envs \
    -t "$(cat task-prompts-scala/<prompt-file>)" \
    2>oh-workdir-scala/<task>.stderr.log \
    | tee oh-workdir-scala/<task>.jsonl

## Key notes

- `--override-with-envs` is REQUIRED (configures the LLM from env vars).
- `--yolo` runs autonomously (no confirmation prompts).
- `--headless --json` emits JSONL events to stdout — captured by `tee` into a per-task .jsonl file.
- Each invocation is a fresh ZERO-MEMORY conversation: the agent does not remember
  prior tasks. Files persist on disk (so task2 can `cat` what task1 produced; task3
  can `cat` Calc.scala); the agent rediscovers state via `ls`/`cat`.
- Bash-only file writes are enforced via the per-prompt IMPORTANT note (file_editor
  errors in this OpenHands setup — it requires a security_risk field that fails
  validation).
- The CLI exits 0 REGARDLESS of task success — DO NOT judge outcome from exit code.
  Judge ONLY from the JSONL contents (FinishAction present, exit codes inside
  TerminalObservations, actual command output).
- Run each invocation in the BACKGROUND (run_in_background=true) and POLL the JSONL
  until the run settles (FinishAction event appears, or no new events for ~60s of
  sustained idle, or ConversationErrorEvent).
- The scala-cli artifact cache is PRE-WARMED by the 10-01 preflight (the trivial
  `scala-cli run` already downloaded the compiler), so the agent's runs should NOT
  pay the 30-120s first-run download. If a run still appears to stall on artifact
  download, that is the cache miss — wait it out; it is not an error.
- TIMING NOTE: 35B measured per-LLM-call timing on this hardware is ~5.3s (v1 F#) /
  ~3.8s (v1.2 Rust). Budget ~4-10 minutes per task. DO NOT cite the legacy
  "~14-32s/call" figure as a measurement — it was a v1 pre-run PREDICTION, never
  measured (carried as a standing honesty rule from the v1.2 audit / STATE.md).
  Full run estimate: 15-40 minutes.

## Per-task JSONL filenames

| Task | Prompt file | JSONL filename |
|------|-------------|----------------|
| task1-scaffold     | task-prompts-scala/task1-scaffold.txt     | oh-workdir-scala/task1-scaffold.jsonl |
| task2-write-calc   | task-prompts-scala/task2-write-calc.txt   | oh-workdir-scala/task2-write-calc.jsonl |
| task2-calc-scaffold (fallback only) | task-prompts-scala/task2-calc-scaffold.txt | oh-workdir-scala/task2-calc-scaffold.jsonl |
| task3-buildtest    | task-prompts-scala/task3-buildtest.txt    | oh-workdir-scala/task3-buildtest.jsonl |

Stderr is captured in parallel as oh-workdir-scala/<task>.stderr.log for each.

## Scaffold-fallback policy summary (full rules in 10-RESEARCH.md §3)

The scaffold (task2-calc-scaffold.txt) is invoked ONLY if ALL the following are true
after the unaided task2 attempt:

1. The agent's `scala-cli run` (in task3) fails on the SAME root error class across
   3+ consecutive compile attempts within task3 (e.g., always the same type error,
   or always the same syntax error), with no syntactic variation in the fix attempts.
2. The fix attempts show no new diagnostic reasoning — the agent is cycling on
   identical fixes with the same result.
3. The JSONL shows the agent is stuck (repeated identical commands).

Do NOT trigger scaffold fallback if:
- The agent is making diverse fix attempts (even if all failing) — that is genuine
  error-and-fix and is the desired chapter material.
- The compile error changes between attempts — the agent is making progress.
- A test prints the WRONG number (e.g., 10-3-2 -> 9, the left-assoc bug) but the
  program compiles and runs — that is a genuine, valuable result; give the agent the
  chance to discover and self-correct it. A buggy-but-running calculator is a
  SUCCESSFUL unaided attempt at the task2 stage.

Scala is more in-distribution for 35B than FsLex was (v1); the bar to scaffold is
high. Only invoke if the agent demonstrably cannot produce compiling Scala at all.

If fallback IS triggered, that fact MUST be disclosed in CAPTURE-MANIFEST.md with
the failure reasons documented. did-write-calc-unaided = NO.
