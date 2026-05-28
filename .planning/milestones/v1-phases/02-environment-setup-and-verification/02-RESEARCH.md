# Phase 2: Environment Setup & Verification - Research

**Researched:** 2026-05-27
**Domain:** OpenHands CLI v1.21 on headless SSH Mac (Apple Silicon, Colima, local LLM proxy)
**Confidence:** HIGH — findings are derived from reading the installed source code at
`~/.local/share/uv/tools/openhands/lib/python3.12/site-packages/` and live probes of
the running services. No guesses.

---

## Summary

This phase must verify and document the ALREADY-WORKING environment for using OpenHands
headless CLI on a Mac that has no browser (SSH-only), uses Colima instead of Docker
Desktop, and runs LLM inference via a local litellm proxy in front of an MLX model.

The critical finding is that **OpenHands headless CLI (`openhands --headless`) uses a
`LocalWorkspace`** — it runs all tool calls (shell commands, file edits) on the HOST
machine, not inside any Docker container. Consequence:

- No `ghcr.io/openhands/agent-server` image pull is required.
- No custom sandbox image is needed.
- Docker is NOT used by the headless CLI at all.
- `dotnet` is already installed on the host (`/opt/homebrew/bin/dotnet`, version 10.0.203).
  SETUP-03 is already satisfied — no further action required.
- The LLM base_url must be host-reachable (`http://127.0.0.1:4000/v1`), not
  `host.docker.internal`, because the process runs on the host.

The only Docker requirement that matters here is for `openhands serve` (GUI web server),
which hard-codes `/var/run/docker.sock` and is NOT usable on this machine. The headless
path is fully Docker-free.

**Primary recommendation:** Verify the headless CLI end-to-end (litellm up → DOCKER_HOST
not needed → env vars set → openhands headless ping) and document the working
invocation. Document the Colima startup and litellm launchd status as SETUP-01/02 checks.

---

## Standard Stack

### Core (verified installed)

| Component | Version | Location | Purpose |
|-----------|---------|----------|---------|
| openhands SDK | 1.21.0 | `~/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands/` | Agent framework |
| openhands-cli | 1.16.0 | `~/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands_cli/` | CLI binary |
| openhands binary | `~/.local/bin/openhands` | uv-installed wrapper | Entry point |
| Python | 3.12.13 | uv-managed | Runtime |
| colima | installed via brew | `~/.colima/` | Docker daemon (replaces Docker Desktop) |
| docker CLI | 29.5.2 (host), server 29.2.1 | `/usr/local/bin/docker` | Container CLI |
| litellm proxy | running via launchd `com.ohama.litellm` | port 4000 | LLM gateway |
| MLX qwen model | `~/.../qwen36-35b` | launchd `com.ohama.qwen36-35b` port 8000 | Actual LLM |
| dotnet SDK | 10.0.203 | `/opt/homebrew/bin/dotnet` | Already on host |

### Key Architecture: LocalWorkspace

The headless CLI creates:

```python
# Source: openhands_cli/setup.py line 147-155
Workspace(working_dir=get_work_dir())
```

`Workspace(working_dir=...)` without a `host=` parameter returns a `LocalWorkspace`
(see `openhands/sdk/workspace/workspace.py`). `LocalWorkspace` executes commands via
`SubprocessTerminal` — a PTY subprocess on the host OS. No Docker is involved.

`get_work_dir()` returns `os.environ.get("OPENHANDS_WORK_DIR", os.getcwd())`.

### Docker context

- Active context: `colima` (socket: `unix:///Users/ohama/.colima/default/docker.sock`)
- Default context points to `/var/run/docker.sock` which does NOT exist.
- The docker CLI uses the `colima` context automatically (it is marked `*`).
- The Python `docker` SDK (inside the openhands venv) uses `DOCKER_HOST` env var.
  Verified: `DOCKER_HOST=unix:///Users/ohama/.colima/default/docker.sock` makes the
  Python SDK connect successfully.
- For the headless CLI: Docker is not called. Setting `DOCKER_HOST` is not needed.

---

## Architecture Patterns

### How --override-with-envs works

Source: `openhands_cli/stores/agent_store.py`

```
openhands --headless --json --yolo -t "..." --override-with-envs
```

With `--override-with-envs`:
1. Reads `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` from environment.
2. If `~/.openhands/agent_settings.json` exists: loads it, then overrides LLM fields.
3. If `~/.openhands/agent_settings.json` does NOT exist (our case — `~/.openhands`
   doesn't exist yet): requires `LLM_API_KEY` AND `LLM_MODEL` to create a default agent.
   `LLM_BASE_URL` is optional but needed for local proxy.
4. Creates default agent with `TerminalTool`, `FileEditorTool`, `TaskTrackerTool`,
   `TaskToolSet`.
5. Saves nothing to disk (env overrides are NOT persisted).

Without `--override-with-envs`: env vars are silently ignored. The CLI warns about them
on stderr but doesn't use them.

### First-run vs. configured-run

Two usage modes:

**Mode A — Pure env-var mode (no persisted config):**
- `~/.openhands/agent_settings.json` does NOT exist.
- REQUIRES: `LLM_API_KEY` + `LLM_MODEL` (and `LLM_BASE_URL` for local proxy).
- Must use `--override-with-envs`.
- Agent is ephemeral — recreated from env each run.

**Mode B — Persisted config + optional override:**
- Run interactive UI once to configure LLM in the textual settings screen, saves
  `~/.openhands/agent_settings.json`.
- Or create it manually (JSON of `Agent.model_dump()`).
- Then `--override-with-envs` applies on top.

For CI / scripted use (this project): Mode A is correct and simpler.

### Working directory

`get_work_dir()` = `OPENHANDS_WORK_DIR` env var, or `os.getcwd()`. The agent operates
there. For project work: set `OPENHANDS_WORK_DIR=/path/to/project` or `cd` there.

---

## SETUP-01: Verify OpenHands + Colima running (exact checks)

### Pre-condition checks

```bash
# 1. Colima running?
colima status 2>/dev/null | grep -E "running|stopped"
# Expected: "running"

# 2. Docker CLI works?
docker info --format '{{.ServerVersion}}' 2>&1
# Expected: "29.2.1" (or similar, no error)

# 3. docker context is colima?
docker context ls | grep "^\*"
# Expected: "colima *   colima   unix:///Users/ohama/.colima/default/docker.sock"

# 4. /var/run/docker.sock absent (expected on this machine)
ls /var/run/docker.sock 2>/dev/null && echo "EXISTS" || echo "ABSENT (correct)"
```

### If Colima is stopped, start it:
```bash
colima start --cpu 4 --memory 8 --disk 60
# Wait ~30s. Re-check: colima status
```

---

## SETUP-02: Verify litellm proxy + qwen reachable (exact checks)

### LiteLLM proxy

```bash
# 1. launchd agent status
launchctl list | grep com.ohama.litellm
# Expected: entry with PID (not "-")

# 2. Model listing
curl -s http://127.0.0.1:4000/v1/models | python3 -m json.tool
# Expected: {"data": [{"id": "qwen-local", ...}], "object": "list"}

# 3. Tool-call ping (run on host)
curl -s http://127.0.0.1:4000/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen-local",
    "messages": [{"role":"user","content":"Run echo hello using the bash tool"}],
    "tools": [{"type":"function","function":{"name":"bash","description":"Run shell","parameters":{"type":"object","properties":{"command":{"type":"string"}},"required":["command"]}}}],
    "tool_choice": "auto"
  }' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['choices'][0]['finish_reason'])"
# Expected: "tool_calls"
# Note: this takes ~240s due to MLX inference time.
```

### MLX model

```bash
# MLX model process
launchctl list | grep com.ohama.qwen36-35b
# Expected: entry with PID

# Direct model check (should NOT be needed for OpenHands — go via proxy)
curl -s http://127.0.0.1:8000/v1/models | python3 -m json.tool
```

---

## SETUP-03: dotnet in the sandbox

**Finding: Already satisfied. No action needed.**

Since headless CLI uses `LocalWorkspace` (host), `dotnet` calls go to the host.
Verified: `dotnet --version` → `10.0.203` at `/opt/homebrew/bin/dotnet`.

The agent's shell inherits the host environment, including `/opt/homebrew/bin` in PATH
(assuming user's shell profile sets it). The TerminalTool spawns a PTY subprocess that
reads the user's shell configuration.

**Verification:**
```bash
# On host (outside OpenHands)
dotnet --version
# Expected: 10.0.203
which dotnet
# Expected: /opt/homebrew/bin/dotnet
```

**If PATH is wrong inside the agent's shell:** The TerminalTool PTY may not source the
full `.zshrc`. To guarantee PATH visibility, set `OPENHANDS_WORK_DIR` and export
`DOTNET_ROOT` or use absolute path in agent tasks.

**Docker sandbox path (NOT needed but documented for reference):**
If the project ever needs `DockerWorkspace` (e.g., for isolation), the correct base image
is `ghcr.io/openhands/agent-server:latest-python` (default in `DockerWorkspace.server_image`).
For ARM64, pass `platform="linux/arm64"` to `DockerWorkspace(...)`. The Dockerfile to add
.NET would use the `dotnet-install.sh` script. But this path is NOT required for the
current project.

---

## SETUP-04: End-to-end verification checklist

### Concrete tool-call ping through OpenHands headless

This is the only check that requires running the full agent. It will take ~240s
(one MLX inference cycle).

```bash
# Set env vars
export LLM_MODEL="openai/qwen-local"
export LLM_BASE_URL="http://127.0.0.1:4000/v1"
export LLM_API_KEY="dummy"
export OPENHANDS_WORK_DIR="/tmp/oh-verify"
mkdir -p /tmp/oh-verify

# Run headless ping
openhands \
  --headless \
  --json \
  --yolo \
  --override-with-envs \
  -t 'Run the bash command: echo OPENHANDS_PING_OK' \
  2>/dev/null
```

**How to read JSONL output to confirm success:**

Each line is a JSON object. An `ActionEvent` (tool call) has:
- `"tool_name"` field
- `"action"` field with the command

An `ObservationEvent` (tool result) has:
- `"tool_name"` field  
- `"observation"` field with output

```bash
# Pipe to filter for relevant events:
openhands --headless --json --yolo --override-with-envs \
  -t 'Run the bash command: echo OPENHANDS_PING_OK' 2>/dev/null | \
  python3 -c "
import sys, json
for line in sys.stdin:
    try:
        ev = json.loads(line)
        t = ev.get('type', ev.get('tool_name', ''))
        if 'observation' in ev or 'action' in ev:
            print(json.dumps(ev, indent=2)[:500])
    except: pass
"
```

**Expected success indicators:**
1. A JSON line where `action.command` contains `echo OPENHANDS_PING_OK` (ActionEvent).
2. A JSON line where `observation.output` contains `OPENHANDS_PING_OK` (ObservationEvent).
3. Process exits 0.

### Full SETUP-04 checklist

```
[ ] colima status → running
[ ] docker info → ServerVersion present (no error)
[ ] curl 127.0.0.1:4000/v1/models → {"data":[{"id":"qwen-local",...}]}
[ ] launchctl list | grep com.ohama.litellm → has PID
[ ] launchctl list | grep com.ohama.qwen36-35b → has PID
[ ] dotnet --version → 10.0.203 (on host)
[ ] openhands --headless --json --yolo --override-with-envs -t 'echo OPENHANDS_PING_OK' → ActionEvent + ObservationEvent in JSONL
```

---

## Common Pitfalls

### Pitfall 1: env vars ignored without --override-with-envs
**What goes wrong:** `LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY` are set but OpenHands
uses stored settings (or fails with "Agent specification not found").
**Why:** By default the CLI ignores env vars and warns on stderr.
**How to avoid:** Always include `--override-with-envs` in headless invocations.
**Warning signs:** stderr shows "Environment variable(s) ... detected but will be ignored."

### Pitfall 2: MissingEnvironmentVariablesError
**What goes wrong:** `openhands --override-with-envs` fails with "Missing required
environment variable(s): LLM_API_KEY, LLM_MODEL".
**Why:** No `~/.openhands/agent_settings.json` and env vars not all set.
**How to avoid:** Must export all three: `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`.
Even if `api_key` is ignored by the local proxy, it must be non-empty.

### Pitfall 3: litellm proxy down between sessions
**What goes wrong:** litellm launchd agent may not be running after reboot or
if manually stopped.
**Why:** `com.ohama.litellm` is a launchd agent (user domain).
**How to avoid:** Add litellm check to pre-flight. Restart with:
`launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ohama.litellm.plist`
or simply `launchctl start com.ohama.litellm`.

### Pitfall 4: Colima socket path
**What goes wrong:** Python docker SDK fails with "No such file or directory" for
`/var/run/docker.sock`.
**Why:** The default docker socket path doesn't exist; Colima uses
`~/.colima/default/docker.sock`.
**How to avoid:** Set `DOCKER_HOST=unix:///Users/ohama/.colima/default/docker.sock`
before any Python code that calls `docker.from_env()`. (The CLI headless mode does NOT
need this — only `DockerWorkspace`-based code does.)

### Pitfall 5: openhands serve NOT usable on this machine
**What goes wrong:** `openhands serve` tries to mount `/var/run/docker.sock` into a
container. This path is absent.
**Why:** The gui_launcher hard-codes `-v /var/run/docker.sock:/var/run/docker.sock`.
**How to avoid:** Do NOT use `openhands serve`. Use `openhands --headless` exclusively.

### Pitfall 6: --json only works with --headless
**What goes wrong:** `--json` alone produces no JSONL output.
**Why:** Source code: `json_mode = args.json and args.headless`. Without `--headless`,
`json_mode` is False regardless.
**How to avoid:** Always pair `--json` with `--headless`.

### Pitfall 7: TTY / Textual app in non-TTY SSH session
**What goes wrong:** Running `openhands` without `--headless` in SSH session may print
"OpenHands CLI terminal UI may not work correctly in this environment".
**Why:** Textual detects non-TTY.
**How to avoid:** Always use `--headless` in SSH sessions. Or set `TTY_INTERACTIVE=1`
as workaround (not recommended).

### Pitfall 8: dotnet PATH not in agent's PTY shell
**What goes wrong:** Agent runs `dotnet --version` and gets "command not found".
**Why:** The TerminalTool PTY sources the user's shell, but Homebrew PATH setup
(`eval "$(/opt/homebrew/bin/brew shellenv)"`) may not be sourced in non-login shells.
**How to avoid:** In agent tasks that need dotnet, either:
  - Use absolute path: `/opt/homebrew/bin/dotnet`
  - Or add to task preamble: `export PATH="/opt/homebrew/bin:$PATH"`
  - Or create `~/.openhands/hooks.json` to inject PATH.

---

## Code Examples

### Minimal verified headless invocation

```bash
export LLM_MODEL="openai/qwen-local"
export LLM_BASE_URL="http://127.0.0.1:4000/v1"
export LLM_API_KEY="dummy"

openhands \
  --headless \
  --json \
  --yolo \
  --override-with-envs \
  -t "Run: echo hello from openhands" \
  2>/dev/null
```

### Parse JSONL to extract action+observation pair

```python
import json, sys

events = []
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        ev = json.loads(line)
        events.append(ev)
    except json.JSONDecodeError:
        pass

actions     = [e for e in events if 'action' in e and e.get('action')]
observations = [e for e in events if 'observation' in e and e.get('observation')]
print(f"Actions: {len(actions)}, Observations: {len(observations)}")
for obs in observations:
    print("Output:", str(obs.get('observation', {}))[:200])
```

### Check litellm health

```bash
curl -sf http://127.0.0.1:4000/health && echo "OK" || echo "FAIL"
curl -sf http://127.0.0.1:4000/v1/models | python3 -c "
import sys, json
d = json.load(sys.stdin)
ids = [m['id'] for m in d['data']]
print('Models:', ids)
assert 'qwen-local' in ids, 'qwen-local not found!'
print('PASS')
"
```

### Check colima + docker

```bash
colima status 2>&1 | head -3
docker info --format '{{.ServerVersion}}' 2>&1
docker run --rm hello-world 2>&1 | grep "Hello from Docker"
```

---

## State of the Art

| Old Assumption | Correct Reality | Impact |
|----------------|-----------------|--------|
| config.toml for settings | env vars with `--override-with-envs` | No config file needed |
| OpenHands 1.7 | openhands SDK 1.21.0 / CLI 1.16.0 | Different API |
| Docker Desktop | Colima (CLI-only, SSH-friendly) | Socket path differs |
| Raw MLX server URL | litellm proxy `qwen-local@4000` | Cleaner model name |
| Browser UI required | `--headless --json` CLI | No browser needed |
| Docker sandbox for agent | LocalWorkspace on host | No container image needed |
| .NET must be in sandbox image | dotnet 10 already on host | SETUP-03 trivially satisfied |

---

## Open Questions

1. **PATH inside agent PTY shell**
   - What we know: `TerminalTool` uses `SubprocessTerminal` (PTY). Homebrew installs to
     `/opt/homebrew/bin`. PTY may not source full login shell profile.
   - What's unclear: Whether `/opt/homebrew/bin` is in PATH for non-login PTY shells
     on this specific user account.
   - Recommendation: In PLAN.md, add a verification step:
     `openhands --headless --yolo --override-with-envs -t "which dotnet"` and check
     output contains `/opt/homebrew/bin/dotnet`. If not, add PATH export to
     `~/.openhands/hooks.json` or use absolute path in agent tasks.
   - **Command:** `openhands --headless --json --yolo --override-with-envs -t "which dotnet && dotnet --version" 2>/dev/null | python3 -c "import sys,json; [print(json.loads(l).get('observation',{}).get('output','')) for l in sys.stdin if 'observation' in l]"`

2. **Colima persistence after reboot**
   - What we know: Colima is started manually via `colima start`. There may or may not
     be a launchd agent for it.
   - What's unclear: Whether Colima auto-starts on login or must be started manually.
   - Recommendation: Planner should add: `launchctl list | grep colima` check, and note
     the manual restart command in the setup docs.

3. **Inference time budget**
   - What we know: ~240s per tool-call cycle on this machine.
   - What's unclear: Whether the textual TUI timeout / conversation will work without
     an explicit `--timeout` (no such flag found in v1.16.0 argparser).
   - Recommendation: The PLAN.md should note long waits are expected; verification
     tasks should wait at least 300s for first response. The headless mode has no
     interactive timeout.

---

## Sources

### Primary (HIGH confidence — source code read)
- `/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands_cli/setup.py` — workspace creation (LocalWorkspace confirmed)
- `/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands_cli/stores/agent_store.py` — env var handling, `--override-with-envs` logic
- `/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands_cli/argparsers/main_parser.py` — CLI flags
- `/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands/sdk/workspace/workspace.py` — Workspace factory: no-host → LocalWorkspace
- `/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands/sdk/workspace/local.py` — LocalWorkspace: host-only, no Docker
- `/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands_cli/gui_launcher.py` — serve hard-codes `/var/run/docker.sock`
- `/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands/tools/terminal/terminal/subprocess_terminal.py` — PTY subprocess on host
- `/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands_cli/utils.py` — json_callback output format, default tool list
- `/Users/ohama/.local/share/uv/tools/openhands/lib/python3.12/site-packages/openhands/workspace/docker/workspace.py` — DockerWorkspace (SDK feature, not used by CLI headless)

### Primary (HIGH confidence — live probe)
- `curl http://127.0.0.1:4000/v1/models` → `{"data":[{"id":"qwen-local",...}]}` confirmed
- `dotnet --version` → `10.0.203` at `/opt/homebrew/bin/dotnet` confirmed
- `docker context ls` → `colima *` with socket `unix:///Users/ohama/.colima/default/docker.sock` confirmed
- `ls /var/run/docker.sock` → ABSENT confirmed
- `DOCKER_HOST=unix:///Users/ohama/.colima/default/docker.sock python -c "import docker; docker.from_env().version()"` → `29.2.1` confirmed

---

## Metadata

**Confidence breakdown:**
- SETUP-01 (install + Colima): HIGH — all commands verified live
- SETUP-02 (litellm + LLM config): HIGH — curl confirmed, source code confirms env var path
- SETUP-03 (dotnet): HIGH — dotnet 10.0.203 already on host; LocalWorkspace confirmed by source
- SETUP-04 (end-to-end ping): MEDIUM — command constructed from source code; actual run not done
  (agent would take ~240s and runs live LLM inference; not safe to run during research)
- mdBook docs: HIGH — Phase 1 settled this; not re-researched here

**Research date:** 2026-05-27
**Valid until:** 2026-06-27 (openhands_cli 1.16.x is stable; check if SDK/CLI updates change env var handling)
