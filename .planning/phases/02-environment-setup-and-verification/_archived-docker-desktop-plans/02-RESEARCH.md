# Phase 2: Environment Setup & Verification — Research

**Researched:** 2026-05-27
**Domain:** OpenHands 1.7 install on macOS Apple Silicon; local Qwen MLX LLM config; custom .NET sandbox image; setup verification
**Confidence:** HIGH for install/run surface, env vars, and config file; HIGH for model-path model string (LiteLLM confirmed); MEDIUM for custom sandbox image flow (known bugs); HIGH for verification commands

---

## Summary

This phase installs OpenHands 1.7 via `uv tool install openhands --python 3.12`, launches it with `openhands serve` (GUI on port 3000), configures the local Qwen MLX endpoint via `~/.openhands/config.toml` (the [llm] section), builds a custom sandbox Docker image that adds .NET 10 SDK, points OpenHands at it via `SANDBOX_BASE_CONTAINER_IMAGE`, and verifies each layer with concrete commands before Phase 3's live run.

The five open questions from prior research are now resolved with high or medium confidence:

1. **Model-path model string:** `openai//Users/ohama/llm-system/models/qwen36-35b` (double slash) is valid. LiteLLM maintainers confirmed in discussion #2793 that multi-slash model names work with the `openai/` prefix. No alias server-side needed.
2. **OpenHands 1.7 run surface:** `openhands serve` starts a web GUI at http://localhost:3000 and is the primary user-facing mode. `openhands --headless -t "task"` is the scriptable/automation path. Both require Docker Desktop running.
3. **Config location and keys:** `~/.openhands/config.toml` is the authoritative user config file. The `[llm]` section uses keys `model`, `api_key`, `base_url`, `timeout`, `num_retries`, `retry_min_wait`, `retry_max_wait`. UI settings are persisted to `~/.openhands/agent_settings.json`.
4. **Custom .NET sandbox:** Use `SANDBOX_BASE_CONTAINER_IMAGE` env var (or `base_container_image` in `[sandbox]` of config.toml). Extend `nikolaik/python-nodejs:python3.12-nodejs22` with dotnet-install.sh. OpenHands builds a runtime layer on top at first start. ARM64 is natively supported in the agent-server image.
5. **SETUP-04 verifications:** Concrete command sequences are documented below.

**Primary recommendation:** Pre-populate `~/.openhands/config.toml` before launching `openhands serve`. Build the .NET custom image first and set `SANDBOX_BASE_CONTAINER_IMAGE` before any agent session. Run all four verification checks before beginning Phase 3.

---

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| uv | 0.11.14 (installed, Homebrew, aarch64) | Python toolchain mgr; installs openhands | Official recommended installer for OpenHands |
| OpenHands | 1.7 (May 2026) | Agentic AI runtime | The target application |
| Docker Desktop | Current (macOS) | Hosts sandbox containers | Required by OpenHands for runtime isolation |
| Python | 3.12 (via uv download) | Required runtime for openhands | OpenHands requires exactly 3.12 |
| .NET SDK | 10.0.300 | F# build toolchain inside sandbox | LTS, ARM64 native, latest stable |
| dotnet-install.sh | Official Microsoft script | Install .NET into the Dockerfile | Recommended non-apt install path |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| LiteLLM | (bundled with OpenHands) | LLM provider abstraction | Handles openai/ prefix routing |
| nikolaik/python-nodejs | python3.12-nodejs22 | Base sandbox image | Custom Dockerfile must extend this |
| ghcr.io/openhands/agent-server | latest-python (ARM64 native) | Runtime agent server inside sandbox | Pulled automatically; ARM64 confirmed |

### Confirmed Environment Facts

| Fact | Value | Confidence |
|------|-------|-----------|
| MLX server URL | http://127.0.0.1:8000/v1 | HIGH (verified live) |
| MLX server health | `{"status": "ok"}` at GET /health | HIGH (verified live) |
| Model ID (from /v1/models) | `/Users/ohama/llm-system/models/qwen36-35b` | HIGH (verified live) |
| uv version | 0.11.14 aarch64 | HIGH (verified) |
| Python 3.12 | Not pre-installed; uv can download cpython-3.12.13-macos-aarch64-none | HIGH (verified) |
| Docker Desktop | NOT currently installed/running | HIGH (verified — `docker` not in PATH) |
| openhands | NOT currently installed | HIGH (verified — not in PATH or uv tools) |
| ~/.openhands/ | Does not exist yet | HIGH (verified) |

---

## REQUIREMENT-BY-REQUIREMENT PLAYBOOK

### SETUP-01: Install and Run OpenHands (`openhands serve` starts)

#### Step 1: Install Docker Desktop

Docker Desktop must be installed and the default Docker socket must be enabled.

**Install:** Download from https://www.docker.com/products/docker-desktop/ (macOS Apple Silicon / ARM64).

**Enable socket (MANDATORY):**
Docker Desktop → Settings → Advanced → "Allow the default Docker socket to be used" → Apply & Restart.

**Verify Docker is working:**
```bash
docker info | grep "Server Version"
# Expected: Server Version: 28.x.x (or current)

docker run --rm hello-world
# Expected: "Hello from Docker!" message
```

**Note for planner:** Docker Desktop is NOT installed. This is Step 0 before anything else. The plan must include Docker Desktop installation as a prerequisite task. Without Docker Desktop, `openhands serve` will fail immediately.

#### Step 2: Install Python 3.12 via uv

uv 0.11.14 is already installed at `/opt/homebrew/bin/uv`. Python 3.12 is not pre-installed but uv can download it:

```bash
uv python install 3.12
# Downloads cpython-3.12.13-macos-aarch64-none
# Verifies with: uv run --python 3.12 python --version
```

#### Step 3: Install OpenHands

```bash
uv tool install openhands --python 3.12
# This installs the `openhands` CLI to ~/.local/bin/ (managed by uv)
# May take several minutes (large package)

# Verify:
openhands --version
# Expected: openhands 1.7.x
```

**PATH note:** If `openhands` is not found after install, add `~/.local/bin` to PATH:
```bash
export PATH="$HOME/.local/bin:$PATH"  # add to ~/.zshrc for persistence
```

#### Step 4: Launch GUI

```bash
openhands serve
# Launches GUI at http://localhost:3000
# Docker Desktop must be running; first run pulls agent-server images (~several GB)
```

**What `openhands serve` does:**
- Checks Docker socket availability
- Pulls `ghcr.io/openhands/agent-server` images if not cached
- Starts the OpenHands web server on port 3000
- Opens a browser tab (or print the URL)
- All agent sessions run inside Docker sandbox containers

**Alternative: headless mode** (for Phase 3 automation):
```bash
openhands --headless -t "task description" > run.jsonl 2>&1
```
Headless mode: no UI, auto-approves all actions, suitable for scripted runs and log capture.

**Verification of SETUP-01:**
- Browser opens http://localhost:3000 → OpenHands UI loads → "New Conversation" button is clickable.

---

### SETUP-02: Configure LLM to Use Local Qwen Endpoint

#### Confirmed model string

The MLX server advertises model ID: `/Users/ohama/llm-system/models/qwen36-35b`

LiteLLM model string = `openai//Users/ohama/llm-system/models/qwen36-35b`

This double-slash format is **confirmed valid** by LiteLLM maintainer (discussion #2793, April 2024): multi-slash model names with `openai/` prefix work correctly. LiteLLM passes the part after `openai/` as the `model` parameter to the OpenAI-compatible client and routes to the configured `base_url`.

**Fallback if double-slash is rejected at runtime:** Configure the MLX server to expose an alias with a shorter name (e.g., `qwen35b`). Most MLX-LM servers support `--model-alias` or similar flag. Check MLX server startup command.

#### Config file path and syntax

**Location:** `~/.openhands/config.toml` (created on first run or manually before first run)

**Complete [llm] section:**

```toml
[llm]
model = "openai//Users/ohama/llm-system/models/qwen36-35b"
api_key = "dummy"
base_url = "http://host.docker.internal:8000/v1"
timeout = 600
num_retries = 2
retry_min_wait = 300
retry_max_wait = 600
```

**Key explanations:**
- `model`: The LiteLLM model string. `openai/` tells LiteLLM to use OpenAI-compatible chat completions adapter. The full path after `openai/` is what LiteLLM sends as `model=` to the endpoint.
- `api_key`: Any non-empty string. The MLX server ignores auth; LiteLLM requires non-empty.
- `base_url`: Must use `host.docker.internal` not `127.0.0.1`. Docker containers cannot reach the host's loopback via `127.0.0.1`. Docker Desktop resolves `host.docker.internal` to the host IP.
- `timeout = 600`: 10 minutes. The 35B model takes ~240s per tool-call. Default is 0 (no timeout in theory, but retry fires at 15s = disaster). Recommend 600 to be safe.
- `num_retries = 2`: Reduce from default 8. With 240s/call, 8 retries = 32 minutes of thrash.
- `retry_min_wait = 300`: Don't retry before 5 minutes (longer than one typical inference).

**Environment variable equivalents** (for docker run or env-based config):

```bash
export LLM_MODEL="openai//Users/ohama/llm-system/models/qwen36-35b"
export LLM_API_KEY="dummy"
export LLM_BASE_URL="http://host.docker.internal:8000/v1"
export LLM_TIMEOUT=600
export LLM_NUM_RETRIES=2
export LLM_RETRY_MIN_WAIT=300
export LLM_RETRY_MAX_WAIT=600
export LLM_DROP_PARAMS=true  # Suppress any unsupported params silently
```

Pass `--override-with-envs` to openhands CLI if using env vars (not persisted to config.toml).

**UI alternative:** Settings → LLM → Advanced toggle → fill in Custom Model / Base URL / API Key fields. UI settings persist to `~/.openhands/agent_settings.json`. For the tutorial, config.toml is preferred (visible, versionable, reproducible).

#### Verification: tool-call ping from inside Docker sandbox (SETUP-04 part A)

A "tool-call ping" means: OpenHands sends a request to the LLM that requires a tool call, the LLM responds with `finish_reason: tool_calls`, and OpenHands executes the resulting action. This confirms the full loop works.

**Command to run BEFORE Phase 3:**
```bash
openhands --headless -t "List the current directory using bash" --json 2>&1 | tee /tmp/openhands-ping.jsonl
```

**What to look for in output:**
- A JSONL line with `"type": "action"` and `"action": "run"` (CmdRunAction) — this means the LLM produced a tool call that OpenHands dispatched.
- A JSONL line with `"type": "observation"` and `"content"` showing directory listing — this means the sandbox executed the command and returned output.
- No lines containing `APIConnectionError`, `APITimeoutError`, or `LiteLLM.BadRequestError`.

**If it fails:**
1. Check MLX server is up: `curl http://127.0.0.1:8000/health` → `{"status": "ok"}`
2. Check Docker can reach host: `docker run --rm curlimages/curl curl http://host.docker.internal:8000/health` → should return same
3. Check model string: `curl http://127.0.0.1:8000/v1/models` — confirm `/Users/ohama/llm-system/models/qwen36-35b` is still the advertised ID
4. If `LiteLLM.BadRequestError: model not found` → the double-slash model string is rejected → use alias fallback (see above)

**Pre-flight: Verify Docker can reach host LLM** (no OpenHands involved):
```bash
docker run --rm --add-host host.docker.internal:host-gateway curlimages/curl \
  curl -s http://host.docker.internal:8000/v1/models
# Expected: the same JSON as curl http://127.0.0.1:8000/v1/models
```
If this fails, `openhands serve` will not reach the LLM either.

---

### SETUP-03: Build .NET-Enabled OpenHands Sandbox Image

#### How custom sandbox images work in OpenHands 1.7

OpenHands builds a runtime layer on top of your base image at first use. Mechanism:
1. You provide a Dockerfile extending `nikolaik/python-nodejs:python3.12-nodejs22` (Debian-based required).
2. You build: `docker build -t openhands-dotnet-sandbox .`
3. You set `SANDBOX_BASE_CONTAINER_IMAGE=openhands-dotnet-sandbox` (env var) or `base_container_image = "openhands-dotnet-sandbox"` in `~/.openhands/config.toml` under `[sandbox]`.
4. When a session starts, OpenHands builds a final runtime image that includes the agent execution server on top of your image. This is an automatic one-time operation — expect 5–10 minutes on the first session. Subsequent sessions reuse the cached runtime.

**IMPORTANT:** The image must be Debian-based. The agent server is injected by OpenHands; you do not need to install it yourself.

**IMPORTANT for config.toml approach:** `SANDBOX_BASE_CONTAINER_IMAGE` can also be set as an env var before launching `openhands serve` — this avoids editing config.toml and allows easy switching:
```bash
export SANDBOX_BASE_CONTAINER_IMAGE=openhands-dotnet-sandbox
openhands serve
```

#### Dockerfile

```dockerfile
# File: Dockerfile.openhands-dotnet
FROM nikolaik/python-nodejs:python3.12-nodejs22

# Install .NET 10 SDK (ARM64 native via official script)
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN wget -qO /tmp/dotnet-install.sh https://dot.net/v1/dotnet-install.sh \
    && chmod +x /tmp/dotnet-install.sh \
    && /tmp/dotnet-install.sh --channel 10.0 --install-dir /usr/local/share/dotnet \
    && rm /tmp/dotnet-install.sh

ENV DOTNET_ROOT=/usr/local/share/dotnet
ENV PATH=$PATH:/usr/local/share/dotnet

# Verify the install baked in
RUN dotnet --version
```

**Build command:**
```bash
docker build \
  --platform linux/arm64 \
  -f Dockerfile.openhands-dotnet \
  -t openhands-dotnet-sandbox \
  .
```

**Note on platform:** The agent-server image from `ghcr.io/openhands/agent-server` is ARM64-native (confirmed: architecture detection returns `linux/arm64` on Apple Silicon; images are tagged with `-arm64` variants). Build the custom image as `linux/arm64` to match. If `docker build` defaults to ARM64 on Apple Silicon, the `--platform` flag is optional but explicit is better.

**Note on .NET 10 + ARM64:** .NET 10.0.300 is fully native on ARM64 Linux (Debian/Ubuntu). No Rosetta needed. dotnet-install.sh downloads the arm64 binary automatically based on the container's architecture.

**Config.toml [sandbox] section:**
```toml
[sandbox]
base_container_image = "openhands-dotnet-sandbox"
```

**Or as environment variable (preferred for tutorial — more explicit):**
```bash
export SANDBOX_BASE_CONTAINER_IMAGE=openhands-dotnet-sandbox
```

#### Known risk: Custom sandbox image build hanging

Issue #6952 (closed) showed that custom sandbox image builds can sometimes hang at "DOCKER BUILD STARTED". Root cause was unclear and the issue was closed without a confirmed fix. Mitigation: watch the Docker Desktop dashboard for build activity; if it hangs >5 minutes after "DOCKER BUILD STARTED" appears in logs, kill OpenHands, run `docker system prune` to clear partial layers, and restart.

Also: Issue #6001 showed a case where Docker CLI wasn't available inside the openhands-app container for building. This affects Docker-mode deployment; the `uv tool install + openhands serve` path should not have this issue (OpenHands communicates with Docker Desktop via the socket, not by running docker CLI inside a container).

---

### SETUP-04: Pre-Run Verification Checklist

All four checks must pass before beginning Phase 3. Run in this order:

#### Check 1: MLX Server Up and Model Advertised

```bash
curl http://127.0.0.1:8000/health
# Expected: {"status": "ok"}

curl http://127.0.0.1:8000/v1/models | python3 -m json.tool
# Expected: data[0].id == "/Users/ohama/llm-system/models/qwen36-35b"
```

**Why:** Confirms the LLM server is running before Docker connectivity test.

#### Check 2: Docker Reaches Host LLM Endpoint

```bash
docker run --rm --add-host host.docker.internal:host-gateway curlimages/curl \
  curl -s http://host.docker.internal:8000/health
# Expected: {"status": "ok"}
```

**Why:** Proves sandbox containers can reach the MLX server. This is the most commonly misconfigured step. If this fails, OpenHands will not reach the LLM at all.

**If it fails:**
- Ensure Docker Desktop has `Allow the default Docker socket to be used` enabled
- Check that `--add-host host.docker.internal:host-gateway` is present
- On macOS Docker Desktop, `host.docker.internal` should resolve automatically even without `--add-host` since Docker Desktop 4.x — but the explicit flag is safer

#### Check 3: `dotnet --version` Inside OpenHands Sandbox

After `SANDBOX_BASE_CONTAINER_IMAGE=openhands-dotnet-sandbox openhands serve` is running:

**Via UI:**
1. Open http://localhost:3000 → New Conversation
2. Type: `Run this command: dotnet --version`
3. Expected agent response: executes `dotnet --version` via CmdRunAction, observes `10.0.300` (or close)

**Via headless (scriptable):**
```bash
SANDBOX_BASE_CONTAINER_IMAGE=openhands-dotnet-sandbox \
  openhands --headless -t "Run dotnet --version and tell me the output" --json 2>&1 | tee /tmp/dotnet-verify.jsonl
```
Look for `"10.0."` in an observation content line.

**If `dotnet: command not found`:**
- The custom sandbox image was not used (SANDBOX_BASE_CONTAINER_IMAGE not set or overridden by UI settings)
- Or the Dockerfile didn't properly add dotnet to PATH
- Rebuild image and confirm: `docker run --rm openhands-dotnet-sandbox dotnet --version` should print `10.0.300`

#### Check 4: Tool-Call Ping (LLM → Tool Dispatch Loop)

This was described in SETUP-02 above. Condensed:

```bash
openhands --headless -t "Run: echo hello && echo world" --json 2>&1 | tee /tmp/toolcall-ping.jsonl
# Look for: {"type": "action", "action": "run", ...} followed by {"type": "observation", ...}
# This proves the full LLM → tool-call → sandbox execution loop works
```

**Estimated time:** With the 35B model, this single tool call takes ~240s. Budget 10 minutes for this verification.

---

## Architecture Patterns

### Config File Priority Order

OpenHands resolves configuration in this priority order (later overrides earlier):
1. Built-in defaults (e.g., `LLM_NUM_RETRIES=8`)
2. `~/.openhands/config.toml` (user config file)
3. Environment variables with `--override-with-envs` flag
4. UI settings (persisted to `~/.openhands/agent_settings.json`)

**Recommendation for tutorial:** Use `~/.openhands/config.toml` as the single source of truth. This is visible, versionable, and reproducible. Avoid relying on UI-persisted settings for tutorial documentation.

### Project Structure for This Phase

```
~/.openhands/
├── config.toml              # LLM + sandbox config (created manually)
└── agent_settings.json      # UI-persisted settings (auto-created on first UI run)

/Users/ohama/projs/OpenHandsTests/
└── sandbox/
    └── Dockerfile.openhands-dotnet   # Custom sandbox image definition
```

### Recommended Phase Execution Order

1. Install Docker Desktop → verify `docker run hello-world`
2. Enable Docker socket in Desktop settings
3. Install Python 3.12 via uv → `uv python install 3.12`
4. Install openhands → `uv tool install openhands --python 3.12`
5. Write `~/.openhands/config.toml` with [llm] and [sandbox] sections
6. Build custom sandbox image → `docker build -t openhands-dotnet-sandbox ...`
7. Run Check 1 (MLX server)
8. Run Check 2 (Docker → host LLM)
9. `SANDBOX_BASE_CONTAINER_IMAGE=openhands-dotnet-sandbox openhands serve` → first run pulls/builds images
10. Run Check 3 (dotnet in sandbox)
11. Run Check 4 (tool-call ping)
12. Write 3부 chapter matching verified config exactly

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| LLM provider routing | Custom HTTP routing logic | LiteLLM's `openai/` prefix + `base_url` | LiteLLM already handles model routing, retries, timeouts |
| .NET install in Dockerfile | Manual curl+tar+extract | `dotnet-install.sh` official script | Handles ARM64 detection, channel selection, PATH setup |
| Docker-host connectivity | Custom networking | `host.docker.internal` + Docker Desktop socket | Standard Docker Desktop approach; no extra config |
| Model string alias | MLX server-side alias config | Double-slash model string `openai//path` | LiteLLM confirmed working; simpler than modifying server |
| Session transcript capture | Screen recording / copy-paste | `openhands --headless --json 2>&1 | tee logfile.jsonl` | Structured JSONL output; replayable; exact timestamps |

---

## Common Pitfalls (Phase 2 specific)

### Pitfall 1: Docker Desktop not installed / socket not enabled

**What goes wrong:** `openhands serve` fails immediately with "Cannot connect to Docker daemon" or similar. No agent sessions can start.

**How to avoid:** Install Docker Desktop before any openhands command. Enable "Allow the default Docker socket to be used" in Docker Desktop → Settings → Advanced.

**Warning sign:** `Error: Python executable not found: docker` or `Cannot connect to Docker socket`.

### Pitfall 2: Model double-slash string rejected

**What goes wrong:** LiteLLM rejects `openai//Users/...` model string at runtime even though it's confirmed valid in theory. Some versions of LiteLLM had URL-parsing issues with leading slashes.

**How to detect:** OpenHands logs show `LiteLLM.BadRequestError: model not found` or `LiteLLM.AuthenticationError`.

**Fallback:** Start MLX server with a model alias. Check server startup command for `--model-alias qwen35b` or equivalent. Then use `openai/qwen35b` as the model string. This requires knowing the exact MLX-LM CLI flag — run `mlx_lm.server --help` or consult mlx-lm docs. Exact flag: **only knowable by running it** — tell planner to try the double-slash first and have this fallback ready.

### Pitfall 3: Python 3.12 not downloaded before openhands install

**What goes wrong:** `uv tool install openhands --python 3.12` tries to use system Python 3.14 (which is installed) and may fail if OpenHands requires exactly 3.12.

**How to avoid:** Run `uv python install 3.12` first, then install openhands.

**Note:** uv 0.11.14 (installed) supports `--python 3.12` and will download if needed. This should be seamless but the download adds time.

### Pitfall 4: Custom sandbox image build hangs

**What goes wrong:** OpenHands hangs at "DOCKER BUILD STARTED" with no progress. Symptom of partial layer cache corruption or Docker daemon resource exhaustion.

**How to avoid:** Pre-build the image manually (`docker build ...`) before starting openhands. Set `SANDBOX_BASE_CONTAINER_IMAGE` so OpenHands uses the pre-built image directly without rebuilding at startup.

**Recovery:** `docker system prune -f && docker build -t openhands-dotnet-sandbox .` then restart openhands.

### Pitfall 5: `host.docker.internal` not resolving from sandbox container

**What goes wrong:** Issue #12229 / #12500 document cases where dynamically-spawned sandbox containers (not the main openhands container) cannot resolve `host.docker.internal`. This is a known bug, status unclear in 1.7.

**How to detect:** Check 2 (docker run curl test) passes but Check 4 (tool-call ping) fails with connection error to 8000. The main openhands container can reach the host, but the spawned sandbox container cannot.

**Workaround (if hit):** The workaround proposed in #12229 is `AGENT_SERVER_EXTRA_HOSTS`. If this env var is available in 1.7: `export AGENT_SERVER_EXTRA_HOSTS="host.docker.internal:host-gateway"`. **Only knowable by running it** — the planner must test this path and document the outcome.

---

## Code Examples

### Complete `~/.openhands/config.toml`

```toml
[llm]
model = "openai//Users/ohama/llm-system/models/qwen36-35b"
api_key = "dummy"
base_url = "http://host.docker.internal:8000/v1"
timeout = 600
num_retries = 2
retry_min_wait = 300
retry_max_wait = 600

[sandbox]
base_container_image = "openhands-dotnet-sandbox"
```

### Complete Dockerfile for .NET Sandbox

```dockerfile
# File: sandbox/Dockerfile.openhands-dotnet
FROM nikolaik/python-nodejs:python3.12-nodejs22

# Install prerequisites for dotnet-install.sh
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    libicu-dev \
    && rm -rf /var/lib/apt/lists/*

# Install .NET 10 SDK (official script; ARM64-aware)
RUN wget -qO /tmp/dotnet-install.sh https://dot.net/v1/dotnet-install.sh \
    && chmod +x /tmp/dotnet-install.sh \
    && /tmp/dotnet-install.sh --channel 10.0 --install-dir /usr/local/share/dotnet \
    && rm /tmp/dotnet-install.sh

ENV DOTNET_ROOT=/usr/local/share/dotnet
ENV PATH=$PATH:/usr/local/share/dotnet
ENV DOTNET_CLI_TELEMETRY_OPTOUT=1
ENV DOTNET_NOLOGO=1

# Sanity check baked into image
RUN dotnet --version
```

Build:
```bash
docker build --platform linux/arm64 -f sandbox/Dockerfile.openhands-dotnet -t openhands-dotnet-sandbox .
# Expected last lines:
# Successfully built <sha>
# Successfully tagged openhands-dotnet-sandbox:latest
# (The RUN dotnet --version step will print e.g. "10.0.300")
```

### Phase 3 Capture Command (for tutorial transcript)

```bash
SANDBOX_BASE_CONTAINER_IMAGE=openhands-dotnet-sandbox \
  openhands --headless \
  -f /Users/ohama/projs/OpenHandsTests/phase3-task.txt \
  --json \
  2>&1 | tee /Users/ohama/projs/OpenHandsTests/captured/phase3-run.jsonl
```

The `phase3-task.txt` file contains the task description for Phase 3. The JSONL output is the raw transcript for the 3부/4부 chapters.

---

## 3부 Chapter: What to Document and in What Order

The 3부 chapter (ch03-setup) must document the verified config exactly. Based on this research, the chapter sections are:

1. **ch03-setup/install.md** — Docker Desktop install + socket enable; `uv python install 3.12`; `uv tool install openhands --python 3.12`; `openhands serve` launch; screenshot of UI at localhost:3000.
2. **ch03-setup/local-llm.md** — Explain `host.docker.internal` vs `127.0.0.1`; the double-slash model string and why; the exact `~/.openhands/config.toml` snippet (verified values); timeout rationale (240s/call → 600s config); UI alternative path.
3. **ch03-setup/sandbox-dotnet.md** (add to chapter list) — The Dockerfile; the build command; the `base_container_image` config key; first-run image build time warning; `docker run openhands-dotnet-sandbox dotnet --version` verification.
4. **ch03-setup/first-run.md** — The four verification checks in order; expected outputs; what each check proves; how to interpret JSONL output; "patience" callout box for ~240s wait.

**Chapter content rule:** Every command shown in the chapter must have been run and its output verified. No invented outputs.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `uvx openhands@latest serve` | `uv tool install openhands --python 3.12 && openhands serve` | Late 2025 | Install step is now separate from run; settings persist across sessions |
| `docker.all-hands.dev/all-hands-ai/...` image names | `docker.openhands.dev/openhands/...` | Oct 2025 (org rename) | All image references updated; old names may still redirect |
| V0 architecture (monolithic sandbox) | V1 SDK (four-package modular) | Apr 2026 | DockerWorkspace, ActionExecutionServer, EventLog — tutorial uses V1 terminology |
| config.toml in source repo root | `~/.openhands/config.toml` | 2025 | User config is now in home dir, not source repo |
| `LLM_TIMEOUT=0` default (unlimited) | `LLM_TIMEOUT=0` (still default, but retry fires at 15s) | Ongoing | Always set explicit timeout for slow local LLMs |

---

## Open Questions

1. **Double-slash model string at runtime**
   - What we know: LiteLLM maintainer confirmed multi-slash names work in discussion #2793. The exact string `openai//Users/ohama/llm-system/models/qwen36-35b` is untested on the installed OpenHands version.
   - What's unclear: Whether the version of LiteLLM bundled with OpenHands 1.7 has any URL-parsing regression with leading-slash model names.
   - Recommendation: In the execution plan, test the double-slash string first. If `LiteLLM.BadRequestError: model not found` appears → use MLX server alias fallback. Command to check: `mlx_lm.server --help | grep alias`. CONFIDENCE: HIGH that it works; LOW confidence it can't break.

2. **`host.docker.internal` from sandbox sub-containers**
   - What we know: Issues #12229 and #12500 documented failures where dynamically-spawned sandbox containers couldn't resolve `host.docker.internal`. Both were closed without confirmed fixes.
   - What's unclear: Whether OpenHands 1.7 fixed this or if it affects the `uv tool install + openhands serve` path.
   - Recommendation: Run Check 2 (docker curl test) AND Check 4 (tool-call ping) and compare. If 2 passes but 4 fails, this bug is the cause. Try `AGENT_SERVER_EXTRA_HOSTS=host.docker.internal:host-gateway` env var before openhands serve.

3. **`openhands serve` first-run image pull time**
   - What we know: It pulls `ghcr.io/openhands/agent-server` images (ARM64 native confirmed). Size unknown.
   - What's unclear: Exact download size and time on Apple Silicon internet connection.
   - Recommendation: Pre-pull images before the tutorial recording: `docker pull ghcr.io/openhands/agent-server:latest-python`. Check the package page for latest tag. Only knowable by doing it.

4. **Custom sandbox runtime build time**
   - What we know: OpenHands builds a runtime layer on top of the custom base image on first session start.
   - What's unclear: How long this takes with the openhands-dotnet-sandbox base (which includes .NET SDK and thus has large layers).
   - Recommendation: Time this during setup. If >15 minutes, document as a one-time cost in the tutorial.

---

## Sources

### Primary (HIGH confidence)
- `https://docs.openhands.dev/openhands/usage/run-openhands/local-setup` — install sequence, openhands serve, Docker socket requirement, port 3000 (checked 2026-05-27)
- `https://docs.openhands.dev/openhands/usage/environment-variables` — complete env var reference with defaults (checked 2026-05-27)
- `https://docs.openhands.dev/openhands/usage/cli/command-reference` — CLI subcommands, headless flag, --override-with-envs (checked 2026-05-27)
- `https://docs.openhands.dev/openhands/usage/cli/headless` — headless mode, JSONL output, --json flag (checked 2026-05-27)
- `https://docs.openhands.dev/openhands/usage/advanced/custom-sandbox-guide` — SANDBOX_BASE_CONTAINER_IMAGE, Dockerfile FROM requirement, build+run workflow (checked 2026-05-27)
- `https://docs.openhands.dev/openhands/usage/llms/local-llms` — openai/ prefix, host.docker.internal, local LLM setup (checked 2026-05-27)
- `https://github.com/BerriAI/litellm/discussions/2793` — LiteLLM maintainer confirmed multi-slash model names work with openai/ prefix (MEDIUM-HIGH — community discussion, not official docs)
- `https://github.com/OpenHands/software-agent-sdk/pkgs/container/agent-server` — ARM64 image variants confirmed, latest python tag (checked 2026-05-27)
- Live environment probe: `curl http://127.0.0.1:8000/v1/models` → model ID confirmed `/Users/ohama/llm-system/models/qwen36-35b` (checked 2026-05-27)
- Live environment probe: `uv --version` → 0.11.14 aarch64 (checked 2026-05-27)
- Live environment probe: `curl http://127.0.0.1:8000/health` → `{"status": "ok"}` (checked 2026-05-27)

### Secondary (MEDIUM confidence)
- `https://www.glukhov.org/ai-devtools/openhands/` — agent_settings.json path, LLM JSON key names (community blog, not official)
- `https://deepwiki.com/OpenHands/OpenHands/5.4-sandbox-configuration` — base vs runtime image semantics (community wiki)
- `https://github.com/OpenHands/OpenHands/issues/12229`, `#12500` — host.docker.internal sub-container resolution bug (open/closed issue, workaround unclear)
- Search result confirming `~/.openhands/config.toml` as user config path (cited in multiple sources)

### Tertiary (LOW confidence)
- `https://docs.openhands.dev/openhands/usage/llms/custom-llm-configs` — named [llm.name] config sections; [llm] key examples (partial — some keys not confirmed with defaults)

---

## Metadata

**Confidence breakdown:**
- Install/run surface (openhands serve, headless): HIGH — official docs confirmed
- Config file path and keys: HIGH — multiple sources consistent; env var table from official docs
- Model double-slash string: MEDIUM-HIGH — LiteLLM maintainer confirmed valid; untested at runtime
- Custom sandbox image: MEDIUM — official docs show SANDBOX_BASE_CONTAINER_IMAGE; known bugs with custom builds; build mechanism details unclear
- ARM64 support: HIGH — agent-server package shows arm64 variants; detect_platform() code confirmed
- host.docker.internal sub-container bug: MEDIUM risk — issues closed, fix unclear

**Research date:** 2026-05-27
**Valid until:** 2026-06-27 (stable area, but OpenHands moves fast — recheck if >1 month elapses)
