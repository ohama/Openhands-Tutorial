# 122B OpenHands Invocation Reference

## Per-Task Command Pattern

Run each task with:

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL="openai/qwen-122b" \
  LLM_BASE_URL="http://127.0.0.1:4000/v1" \
  LLM_API_KEY="dummy" \
  OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir-122b" \
  openhands --headless --json --yolo --override-with-envs \
  -t "$(cat <prompt-file>)" \
  2>oh-workdir-122b/<task>.stderr.log \
  | tee oh-workdir-122b/<task>.jsonl
```

Substitute `<prompt-file>` and `<task>` per the table below.

Run from: `/Users/ohama/projs/OpenHandsTests/`

## Per-Task JSONL Filename Table

| Task | Prompt File | JSONL Output | Notes |
|------|-------------|--------------|-------|
| task1 | task-prompts-122b/task1-scaffold.txt | oh-workdir-122b/task1-scaffold.jsonl | Always run |
| task2 attempt 1 | task-prompts-122b/task2-lexer-unaided.txt | oh-workdir-122b/task2-lexer-unaided.jsonl | Always run (unaided first) |
| task2 retry | task-prompts-122b/task2-lexer-unaided-retry.txt | oh-workdir-122b/task2-lexer-unaided-retry.jsonl | Only if attempt 1 stuck/no valid FsLex |
| task2 fallback | task-prompts-122b/task2-lexer-scaffold.txt | oh-workdir-122b/task2-lexer-scaffold.jsonl | Only if BOTH unaided attempts fail; disclose in CAPTURE-MANIFEST |
| task3 | task-prompts-122b/task3-parser.txt | oh-workdir-122b/task3-parser.jsonl | Always run |
| task4 | task-prompts-122b/task4-evaluator.txt | oh-workdir-122b/task4-evaluator.jsonl | Always run |
| task5 | task-prompts-122b/task5-buildtest.txt | oh-workdir-122b/task5-buildtest.jsonl | Always run |
| task6 | task-prompts-122b/task6-fix.txt | oh-workdir-122b/task6-fix.jsonl | Only if task5 fails |

Stderr logs: each invocation also redirects stderr to `oh-workdir-122b/<task>.stderr.log`.

## Key Notes

**`--override-with-envs` is REQUIRED.** Without it, the env-var LLM config (model/base_url/api_key) does not take effect. This is proven in v1.

**`--yolo` enables autonomous mode.** Agent proceeds without confirmation prompts.

**`--headless --json` emits JSONL.** Each line is a JSON event (ActionEvent, ObservationEvent, AgentFinishAction, ConversationErrorEvent, etc.). The pipe to `tee` writes the JSONL to disk while also streaming to stdout for monitoring.

**Each invocation is a fresh zero-memory conversation.** Files persist on disk between tasks; the agent rediscovers them with `ls`/`cat` at task start. There is no shared memory or context between tasks — the next task prompt must orient the agent from scratch.

**Bash-only file writes.** All task prompts instruct the agent to use bash (`cat > FILE <<'EOF'`/`printf`/`tee`) and NOT the `file_editor` tool. The `file_editor` tool errors in this setup (requires a `security_risk` field that fails validation).

**CLI exits 0 regardless of task outcome.** Do not rely on exit code to determine success. Judge from the JSONL: look for `FinishAction` events for success, `ConversationErrorEvent` for iteration cap exceeded, and inspect the final file state with `cat oh-workdir-122b/calc/Lexer.fsl` etc.

**Run in background + poll.** For long tasks (especially task2 lexer and task3 parser), run with `&` and poll the JSONL for completion:

```bash
OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL="openai/qwen-122b" \
  LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" \
  OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir-122b" \
  openhands --headless --json --yolo --override-with-envs \
  -t "$(cat task-prompts-122b/task1-scaffold.txt)" \
  2>oh-workdir-122b/task1-scaffold.stderr.log \
  | tee oh-workdir-122b/task1-scaffold.jsonl &

# Poll for completion (FinishAction or ConversationErrorEvent):
tail -f oh-workdir-122b/task1-scaffold.jsonl | grep -m1 '"type":"FinishAction"\|ConversationErrorEvent'
```

**Speed expectations (122B vs 35B).** 122B generates ~27-47 tok/s on this machine, roughly 25-30% slower per token than 35B. Budget:
- Simple tasks (task1 scaffold, task4 evaluator): ~2-4 minutes
- Complex tasks (task2 lexer unaided, task3 parser): ~6-8 minutes
- Worst case (task2 stuck on lexer debugging): up to ~15 minutes
- OpenHands default 500-iteration cap is more than enough; no special timeout needed.

## Preflight Checklist (before running task1)

- [ ] `git check-ignore oh-workdir-122b` returns `oh-workdir-122b` (scratch dir gitignored)
- [ ] `ls oh-workdir-122b/` is empty (no stale calc/ from prior aborted attempt)
- [ ] `curl -s http://127.0.0.1:4000/v1/models | grep qwen-122b` returns a match (proxy live)
- [ ] `openhands --version` confirms CLI is available

## Model Configuration

| Parameter | Value |
|-----------|-------|
| LLM_MODEL | `openai/qwen-122b` |
| LLM_BASE_URL | `http://127.0.0.1:4000/v1` |
| LLM_API_KEY | `dummy` (litellm proxy; no real key needed) |
| OPENHANDS_WORK_DIR | `/Users/ohama/projs/OpenHandsTests/oh-workdir-122b` |
| Proxy backend | `http://127.0.0.1:8001` (Qwen2.5-122B via launchd `com.ohama.qwen122b`) |
