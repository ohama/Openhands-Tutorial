# OpenHands Run — Invocation Reference

## Exact Per-Task Invocation

Run each task with the following shell pattern (substitute `<task-name>` for each task):

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
LLM_MODEL="openai/qwen-local" LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" \
OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir" \
openhands --headless --json --yolo --override-with-envs -t "$(cat <prompt-file>)" \
  2>oh-workdir/<task-name>.stderr.log | tee oh-workdir/<task-name>.jsonl
```

## Key Notes

- `--override-with-envs` is REQUIRED — without it, `LLM_*` env vars are silently ignored.
- `--yolo` enables autonomous mode (agent does not ask for user confirmation before running commands).
- `--headless --json` runs without UI and emits JSONL events to stdout.
- `OPENHANDS_SUPPRESS_BANNER=1` suppresses the ASCII banner for clean tee output.
- Each invocation is a **fresh, zero-memory conversation** — the agent has no knowledge of prior tasks. Files written by previous tasks persist on disk (LocalWorkspace = host filesystem), but the agent can only discover them by `ls`/`cat`-ing the working directory.
- The agent's initial working directory is `OPENHANDS_WORK_DIR` (i.e., `/Users/ohama/projs/OpenHandsTests/oh-workdir`). The calculator project lives in the `calc/` subdirectory — every prompt must instruct the agent to `cd calc` (except task 1, which creates it).
- bare `dotnet` (10.0.203) works in the agent's PTY — no absolute path prefix needed.
- FsLexYacc 11.3.0 is already in the local NuGet cache (`~/.nuget/packages/fslexyacc/11.3.0/`) — `dotnet restore` does NOT require network access.
- File writes must be bash-only: the qwen-local model's `file_editor` / `str_replace` tool calls fail validation (missing `security_risk` field). Every task prompt instructs the agent to write/edit files using only bash (printf, tee, quoted heredoc). Do not change this.

## Per-Task JSONL Log Filenames

The execute plan (03-02) will produce the following log files, in order:

| Task | Prompt File        | JSONL Log                | stderr Log                        |
|------|--------------------|--------------------------|-----------------------------------|
| 1    | task1-scaffold.txt | task1-scaffold.jsonl     | task1-scaffold.stderr.log         |
| 2    | task2-lexer.txt    | task2-lexer.jsonl        | task2-lexer.stderr.log            |
| 3    | task3-parser.txt   | task3-parser.jsonl       | task3-parser.stderr.log           |
| 4    | task4-evaluator.txt| task4-evaluator.jsonl    | task4-evaluator.stderr.log        |
| 5    | task5-buildtest.txt| task5-buildtest.jsonl    | task5-buildtest.stderr.log        |
| 6*   | task6-fix.txt      | task6-fix.jsonl          | task6-fix.stderr.log              |

*Task 6 is CONDITIONAL — run only if task 5 surfaces a failing test case (wrong output or build error that task 5 cannot self-correct).

## Concrete Example (Task 1)

```bash
cd /Users/ohama/projs/OpenHandsTests

OPENHANDS_SUPPRESS_BANNER=1 \
LLM_MODEL="openai/qwen-local" LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" \
OPENHANDS_WORK_DIR="/Users/ohama/projs/OpenHandsTests/oh-workdir" \
openhands --headless --json --yolo --override-with-envs -t "$(cat .planning/phases/03-capture-the-openhands-run/task-prompts/task1-scaffold.txt)" \
  2>oh-workdir/task1-scaffold.stderr.log | tee oh-workdir/task1-scaffold.jsonl
```

Repeat the pattern for each subsequent task, substituting the prompt file and log name.

## Verifying a Task Completed

After each task, scan the JSONL for a `FinishAction` event or a final `MessageEvent` from `source=agent`:

```bash
python3 -c "
import json
events = [json.loads(l) for l in open('oh-workdir/task1-scaffold.jsonl') if l.strip().startswith('{')]
has_finish = any(e.get('action',{}).get('kind') == 'FinishAction' for e in events)
has_error  = any(e.get('kind') == 'ConversationErrorEvent' for e in events)
print('FinishAction:', has_finish, '| ConversationErrorEvent:', has_error)
"
```
