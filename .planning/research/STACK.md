# Stack Research — v1.4 Planning Comparison

**Domain:** Korean mdBook tutorial — v1.4 milestone: compare two task-planning regimes (Claude-led decomposition vs OpenHands-native planning) on Qwen 35B
**Researched:** 2026-06-01
**Confidence:** HIGH (confirmed against installed binary v1.16.0 / SDK v1.21.0; source verified via GitHub API)

---

## Verified Versions (runtime, not assumed)

| Component | Confirmed Version | How Verified |
|-----------|-------------------|--------------|
| OpenHands CLI | **1.16.0** | `openhands --version` on this machine |
| OpenHands SDK | **v1.21.0** | banner: `OpenHands SDK v1.21.0` |
| litellm proxy (already running) | pre-existing | milestone context, not re-researched |
| Qwen 35B endpoint | `openai/qwen-35b` @ `127.0.0.1:4000` | milestone context |

---

## Core Question: Does OpenHands 1.16 / SDK 1.21 Have Native Planning?

**YES — a dedicated Planning Agent exists, introduced in v1.5.0 (March 2026), present in 1.16.0.**

Key facts (verified against SDK source at `OpenHands/software-agent-sdk` main branch):

1. **`get_planning_agent()`** — a first-class factory in `openhands.tools.preset.planning`. Returns an `Agent` with read-only tools: `GlobTool`, `GrepTool`, and `PlanningFileEditorTool` (the only writable surface).

2. **`PLAN.md` output path** — `.agents_tmp/PLAN.md` relative to workspace root (default; configurable via `plan_path` param to `get_planning_tools()`).

3. **System prompt** — `system_prompt_planning.j2`; directs the agent through four phases: Initial Understanding → Planning → Synthesis & User Alignment → Refinement. The agent clarifies ambiguities BEFORE writing the plan.

4. **PLAN.md structure** — five mandatory sections defined in `PLAN_STRUCTURE`:
   1. OBJECTIVE
   2. CONTEXT SUMMARY
   3. APPROACH OVERVIEW
   4. IMPLEMENTATION STEPS (goal + method + optional reference per step)
   5. TESTING AND VALIDATION

5. **TaskTrackerTool** — a separate in-process tool (`TaskTrackerAction` / `TaskTrackerObservation`) that tracks a live `task_list: TaskItem[]` during execution. Each `TaskItem` has `title`, `notes`, `status` (`"todo" | "in_progress" | "done"`). The command is `"view"` or `"plan"`. This is the "Task List tab" visible in the 1.5.0 GUI. It appears in the JSONL stream as `TaskTrackerAction` / `TaskTrackerObservation` event types.

6. **`PlanningFileEditorObservation`** — distinct observation type for the planning agent's file writes (separate from `FileEditorObservation`), confirming the planning agent operates in an isolated tool surface.

**Source:** `frontend/src/types/v1/core/base/action.ts`, `observation.ts`, `common.ts` (GitHub API verified); `openhands-tools/openhands/tools/preset/planning.py` (GitHub API verified); `examples/01_standalone_sdk/24_planning_agent_workflow.py` (GitHub API verified).

---

## Arm A: Claude-Led Decomposition → OpenHands Executes

**Goal:** Claude authors a task decomposition; feed it to OpenHands for execution.

### Mechanism Comparison

| Option | Mechanism | Headless Flag | Loaded How | Verdict |
|--------|-----------|---------------|------------|---------|
| A1 (RECOMMENDED) | Embed full plan in `-t` / `-f` task prompt | `-f plan.txt` | User message | Simplest; proven in prior milestones |
| A2 | `.agents_tmp/PLAN.md` pre-written + execution prompt | `-t "Read .agents_tmp/PLAN.md and implement all steps"` | File reference in message | Two-step but explicit; mirrors SDK example |
| A3 | `AGENTS.md` at workspace root | automatic (always injected) | `SystemPromptEvent.dynamic_context` | Persistent across sessions; but not task-specific |
| A4 | `.openhands/microagents/repo.md` (V0) | automatic (keyword-triggered or always) | Injected via microagent system | Works; older API, V1 renamed to skills |

**Recommended for Arm A: Option A1 or A2.**

#### Option A1 — File-Seeded Prompt (Simplest)

Claude writes `armA-plan.txt` containing an explicit numbered task breakdown. OpenHands receives it as the task.

```bash
# Write Claude's plan to a file
cat > /path/to/workdir/armA-plan.txt << 'EOF'
You are implementing a Rust HTTP server. Execute each step in order:

Step 1: Scaffold the project with `cargo new http-server`.
Step 2: Add `tokio` and `hyper` to Cargo.toml.
Step 3: Implement a `/ping` endpoint returning 200 OK.
Step 4: Run `cargo build` and verify it succeeds.
Step 5: Run `cargo test` and fix any failures.
EOF

# Run OpenHands with the plan file as task
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL=openai/qwen-35b \
  LLM_BASE_URL=http://127.0.0.1:4000/v1 \
  LLM_API_KEY=dummy \
  OPENHANDS_WORK_DIR=/path/to/workdir \
  openhands --headless --json --yolo --override-with-envs \
    -f armA-plan.txt \
    2>err-armA.log | tee out-armA.jsonl
```

**Why this works:** The `--headless` flag enables always-approve mode. `-f` reads the file as the initial user message. The agent treats it as a single task and executes sequentially. This is what prior milestones did with per-task prompts, now consolidated.

#### Option A2 — Pre-write PLAN.md + Execution Prompt

Claude writes `.agents_tmp/PLAN.md` in the workspace using the SDK's five-section structure. Then pass a short execution prompt:

```bash
mkdir -p /path/to/workdir/.agents_tmp
cat > /path/to/workdir/.agents_tmp/PLAN.md << 'EOF'
# 1. OBJECTIVE
Implement a Rust HTTP server with /ping endpoint.

# 2. CONTEXT SUMMARY
Workspace: /workspace. Target: tokio + hyper server.

# 3. APPROACH OVERVIEW
Use tokio as async runtime, hyper as HTTP server library.

# 4. IMPLEMENTATION STEPS
Step 1 — cargo new: run `cargo new http-server`
Step 2 — add deps: edit Cargo.toml, add tokio and hyper
Step 3 — implement /ping: create src/main.rs with ping handler
Step 4 — build: run `cargo build`
Step 5 — test: run `cargo test`

# 5. TESTING AND VALIDATION
`cargo test` exits 0 and server responds to curl /ping with 200.
EOF

OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL=openai/qwen-35b \
  LLM_BASE_URL=http://127.0.0.1:4000/v1 \
  LLM_API_KEY=dummy \
  OPENHANDS_WORK_DIR=/path/to/workdir \
  openhands --headless --json --yolo --override-with-envs \
    -t "Read .agents_tmp/PLAN.md and implement all steps exactly as described." \
    2>err-armA.log | tee out-armA.jsonl
```

**Why this matters for the tutorial:** Option A2 makes the plan visible as a file artifact — readers see `PLAN.md`, understand Claude wrote it, and can observe the agent reading it. Strong narrative for the mdBook chapter.

#### Option A3 — AGENTS.md Workspace Injection

Place `AGENTS.md` at the workspace root. OpenHands SDK automatically loads it into `SystemPromptEvent.dynamic_context` at conversation start (confirmed via `test_repo_root_project_skills.py`). Works even when work_dir is a subdirectory — it walks up to the git repo root.

```
/path/to/workdir/
  AGENTS.md          ← Claude-authored plan injected automatically
  src/
  Cargo.toml
```

**Caveat:** Injection requires `AgentContext(load_project_skills=True)` or the headless CLI to enable project skill loading. Whether the headless CLI (`openhands --headless`) sets this flag by default is NOT confirmed from docs. Use A1 or A2 for certainty. A3 is better for persistent project context than for single-run plan injection.

#### What NOT to Use for Arm A

| Avoid | Why |
|-------|-----|
| Sequential per-task runs (prior milestone pattern) | Loses cross-step context; v1.4 specifically compares single-run planning |
| Calling `get_planning_agent()` directly in SDK | Planning agent has read-only tools (no execution) — it produces PLAN.md but cannot implement; requires a two-agent chain not available via headless CLI directly |
| Relying on keyword-triggered microagents for plan injection | Injection timing is non-deterministic for keyword triggers; `repo.md` microagent is better for repo context than task plans |

---

## Arm B: OpenHands-Native Planning (Self-Plan)

**Goal:** Give OpenHands the whole goal in one prompt; let it plan and execute autonomously.

### Mechanism

Use the default `CodeActAgent` (not the Planning Agent) with a comprehensive single prompt. The `CodeActAgent` has access to `TaskTrackerTool`, which it uses to maintain its own task list during execution.

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL=openai/qwen-35b \
  LLM_BASE_URL=http://127.0.0.1:4000/v1 \
  LLM_API_KEY=dummy \
  OPENHANDS_WORK_DIR=/path/to/workdir \
  openhands --headless --json --yolo --override-with-envs \
    -t "Build a complete Rust HTTP server with the following requirements:
       1. Use tokio + hyper for async HTTP.
       2. Implement a /ping endpoint that returns HTTP 200 with body 'pong'.
       3. All code must compile with 'cargo build'.
       4. Tests must pass with 'cargo test'.
       Plan your own implementation steps, then execute them." \
    2>err-armB.log | tee out-armB.jsonl
```

**Key phrasing for Arm B:** Include "Plan your own implementation steps" explicitly. This nudges the agent to emit `TaskTrackerAction` events with `command: "plan"` — which appear in the JSONL stream and produce the task list visible in the UI's Task List tab. Without this hint, the agent may skip the planning call.

**Alternative for true two-phase capture** (SDK-level, not headless CLI):

The SDK example `24_planning_agent_workflow.py` shows a clean two-phase approach using the Python SDK directly:

```python
from openhands.tools.preset.planning import get_planning_agent
from openhands.tools.preset.default import get_default_agent
from openhands.sdk import LLM, Conversation

llm = LLM(model="openai/qwen-35b", base_url="http://127.0.0.1:4000/v1",
          api_key="dummy", usage_id="agent")

# Phase 1: Planning Agent writes .agents_tmp/PLAN.md
planning_agent = get_planning_agent(llm=llm)
planning_conv = Conversation(agent=planning_agent, workspace="/path/to/workdir")
planning_conv.send_message("Plan this: [full goal]. Do NOT ask clarifying questions. Write the plan directly.")
planning_conv.run()

# Phase 2: Execution Agent reads PLAN.md and implements
exec_agent = get_default_agent(llm=llm, cli_mode=True)
exec_conv = Conversation(agent=exec_agent, workspace="/path/to/workdir")
exec_conv.send_message("Read .agents_tmp/PLAN.md and implement all steps.")
exec_conv.run()
```

**Note:** This SDK path produces richer plan artifacts but is NOT accessible via the headless CLI. Requires a Python harness script. JSONL capture must be implemented separately by logging `exec_conv.state.events`. This approach is viable for v1.4 if the harness is extended to a Python runner.

---

## Planning Agent vs CodeActAgent — Key Differences

| Aspect | Planning Agent | CodeActAgent (default) |
|--------|----------------|------------------------|
| Tools | Glob, Grep, PlanningFileEditorTool ONLY | Full toolset: Terminal, FileEditor, Browser, TaskTracker, etc. |
| Output | `PLAN.md` (`.agents_tmp/PLAN.md`) | Task list via `TaskTrackerAction`, plus actual code |
| Can execute? | No (read-only except PLAN.md) | Yes |
| Headless CLI | Not directly selectable — only via Python SDK | Yes (default) |
| Use case | Pre-execution planning step | Execution (with optional self-planning via TaskTrackerTool) |
| JSONL events | `PlanningFileEditorObservation` | `TaskTrackerObservation`, `TerminalObservation`, etc. |

---

## AGENTS.md / Microagents — Injection Mechanism (Definitive)

**File:** `AGENTS.md` at the git repository root (or workspace root)

**How injection works (source-verified):**

1. `load_project_skills(work_dir)` walks up from `work_dir` to the git root.
2. Finds `AGENTS.md` → creates a `Skill(name="agents", content=<file contents>)`.
3. On `LocalConversation` startup, the skill content is rendered into `SystemPromptEvent.dynamic_context.text`.
4. The agent sees it as part of its system prompt — **always loaded, unconditionally**, as long as `load_project_skills=True`.

**In headless CLI:** Whether `--headless` mode sets `load_project_skills=True` is not confirmed in public docs. Use Option A1 or A2 for guaranteed plan delivery.

**Also supported:** `.openhands/microagents/*.md` (V0 API, keyword-triggered) and `.agents/skills/*.md` (V1 API, `SKILL.md` files). For the comparison harness, AGENTS.md is simpler.

**Source:** `tests/sdk/conversation/test_repo_root_project_skills.py` (GitHub API read directly).

---

## Determinism / Seed / Temperature Controls

### Available Parameters (SDK v1.21.0)

Confirmed in `tests/sdk/config/test_llm_config.py` (source read directly):

| Parameter | Type | Default | Env var (env-override pattern) |
|-----------|------|---------|-------------------------------|
| `temperature` | `float \| None` | `None` (provider default) | `LLM_TEMPERATURE` (inferred from naming convention) |
| `top_p` | `float \| None` | `None` | `LLM_TOP_P` |
| `top_k` | `float \| None` | `None` | `LLM_TOP_K` |
| `seed` | `int \| None` | `None` | `LLM_SEED` (inferred) |

**Setting temperature in headless invocation:**

Via `config.toml` `[llm]` section (confirmed in `config.template.toml`):

```toml
[llm]
model = "openai/qwen-35b"
api_key = "dummy"
base_url = "http://127.0.0.1:4000/v1"
temperature = 0.0
seed = 42
timeout = 300
```

Via Python SDK:

```python
llm = LLM(
    model="openai/qwen-35b",
    base_url="http://127.0.0.1:4000/v1",
    api_key="dummy",
    temperature=0.0,
    seed=42,
    usage_id="agent",
)
```

### Determinism Reality Check

| Layer | Control | Effect |
|-------|---------|--------|
| litellm proxy (127.0.0.1:4000) | Pass `temperature=0` and `seed=N` in request body; litellm forwards to model | Reduces variance; does NOT guarantee identical outputs |
| Qwen 35B (local inference) | Sampling is inherently stochastic unless the inference backend supports reproducible seeds | Most local inference backends (vLLM, ollama, llama.cpp) do NOT guarantee determinism even with seed |
| OpenHands SDK | `seed` param passed through to LiteLLM completion call | Best-effort only |

**Practical recommendation for v1.4:** Run each arm 3 times and report median metric rather than relying on a single run. Use `temperature=0.2` (not 0.0 — temperature 0 causes issues with some models via LiteLLM, see GitHub issue #4131) and a fixed seed (e.g., `seed=42`) for reproducibility signal. Do not claim determinism — document variance in the tutorial chapter.

**UNVERIFIED:** Whether `LLM_TEMPERATURE` and `LLM_SEED` are the exact environment variable names accepted by `--override-with-envs`. The naming convention is consistent (e.g., `LLM_MODEL`, `LLM_API_KEY`, `LLM_BASE_URL`) but temperature/seed via env var in headless CLI has not been tested on this machine.

---

## Headless CLI Flags Reference (Confirmed Against v1.16.0)

```
openhands [flags] 

Confirmed flags:
  -t, --task TASK        Inline task string (seed conversation)
  -f, --file FILE        File whose contents seed the initial conversation
  --headless             Headless mode (no UI; always-approve)
  --json                 Stream JSONL events to stdout
  --yolo / --always-approve   Auto-approve all agent actions
  --override-with-envs   Apply LLM_MODEL, LLM_BASE_URL, LLM_API_KEY from env

Environment variables:
  OPENHANDS_SUPPRESS_BANNER=1   Suppress SDK startup banner
  OPENHANDS_WORK_DIR=<path>     Working directory for the agent
  LLM_MODEL=openai/qwen-35b
  LLM_BASE_URL=http://127.0.0.1:4000/v1
  LLM_API_KEY=dummy
```

**No `--agent-type` or `--plan-mode` flag exists in the headless CLI.** The Planning Agent is only accessible via Python SDK (`get_planning_agent()`), not via CLI flags.

**The `--yolo` flag is an alias for `--always-approve`.** Both are present and documented in `openhands --help`.

Full invocation pattern (already proven in prior milestones):

```bash
OPENHANDS_SUPPRESS_BANNER=1 LLM_MODEL=openai/qwen-35b LLM_BASE_URL=http://127.0.0.1:4000/v1 LLM_API_KEY=dummy OPENHANDS_WORK_DIR=<wd> openhands --headless --json --yolo --override-with-envs -t "<task>" 2>err.log | tee out.jsonl
```

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| `--file` with a very large prompt (>30K chars) | SDK default `max_message_chars=30000`; content will be truncated | Keep plans concise; use PLAN.md file reference instead |
| Planning Agent via headless CLI for Arm B | No CLI flag to select it; would require Python harness | Use CodeActAgent (default) with explicit "Plan your steps" prompt |
| `temperature=0.0` | LiteLLM issue #4131: some models error at exactly 0.0 | Use `temperature=0.1` or `0.2` |
| `--resume` for comparison runs | Continues a prior conversation, contaminating the baseline | Always start fresh conversations for each arm/run |
| `.openhands/microagents/` keyword-triggered agents for plan injection | Injection timing depends on keyword matching, not guaranteed at task start | Use `-f plan.txt` or pre-written PLAN.md |

---

## Recommended Invocation Summary

### Arm A (Claude-led, file-seeded — RECOMMENDED)

```bash
# 1. Claude writes the plan
python3 generate_arm_a_plan.py --goal "rust-server" --out /tmp/armA-run1/armA-plan.txt

# 2. OpenHands executes it
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL=openai/qwen-35b \
  LLM_BASE_URL=http://127.0.0.1:4000/v1 \
  LLM_API_KEY=dummy \
  OPENHANDS_WORK_DIR=/tmp/armA-run1 \
  openhands --headless --json --yolo --override-with-envs \
    -f /tmp/armA-run1/armA-plan.txt \
    2>/tmp/armA-run1/err.log | tee /tmp/armA-run1/out.jsonl
```

### Arm B (OpenHands-native, self-plan)

```bash
OPENHANDS_SUPPRESS_BANNER=1 \
  LLM_MODEL=openai/qwen-35b \
  LLM_BASE_URL=http://127.0.0.1:4000/v1 \
  LLM_API_KEY=dummy \
  OPENHANDS_WORK_DIR=/tmp/armB-run1 \
  openhands --headless --json --yolo --override-with-envs \
    -t "Build a Rust HTTP server with /ping endpoint using tokio+hyper. \
        Cargo build and cargo test must succeed. \
        First, create your own step-by-step implementation plan using the task tracker, then execute each step." \
    2>/tmp/armB-run1/err.log | tee /tmp/armB-run1/out.jsonl
```

### Capturable JSONL Events for Comparison Metrics

| Metric | Event Type | Field |
|--------|-----------|-------|
| Task plan (Arm B) | `TaskTrackerObservation` | `command=="plan"`, `task_list[]` |
| Terminal execution | `TerminalObservation` | `command`, `exit_code` |
| File writes | `FileEditorObservation` | `command=="create"`, `path`, `new_content` |
| Planning file write (SDK only) | `PlanningFileEditorObservation` | `path`, `new_content` |
| Agent finish | `FinishObservation` | `content` |
| Total steps | count of all action events | — |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Arm A plan delivery | `-f armA-plan.txt` | `.openhands/microagents/repo.md` | File flag is immediate and certain; microagent injection in headless mode unconfirmed |
| Arm B self-planning | `CodeActAgent` + "plan your steps" prompt | Python SDK `get_planning_agent()` + `get_default_agent()` two-phase | Two-phase SDK approach is richer but adds Python harness complexity not needed for v1.4 headless CLI comparison |
| Arm B plan capture | `TaskTrackerObservation` from JSONL | None (Planning Agent not accessible via CLI) | TaskTracker is in the default agent's toolset; confirmed in TypeScript types |
| Temperature control | `config.toml [llm] temperature=0.2` | `LLM_TEMPERATURE` env var | config.toml is confirmed; env var naming unverified for temperature |

---

## Version Compatibility Notes

| OpenHands Version | Planning Agent | TaskTrackerTool | AGENTS.md injection |
|-------------------|---------------|-----------------|---------------------|
| < 1.0.0 (V0/old) | No | No | Via `.openhands/microagents/repo.md` |
| 1.0.0 (SDK v1) | No | Partial (task tracker interface added) | Via AGENTS.md (SDK) |
| 1.5.0+ | YES (Planning Agent, PLAN.md) | YES (Task List tab) | Via AGENTS.md (SDK) |
| **1.16.0 (our version)** | **YES** | **YES** | **Via AGENTS.md (SDK)** |

---

## Sources

| Source | URL | Confidence |
|--------|-----|------------|
| OpenHands CLI installed version | `openhands --version` on host | HIGH (direct) |
| SDK version | startup banner `OpenHands SDK v1.21.0` | HIGH (direct) |
| CLI flags (--headless, -f, --yolo, --override-with-envs) | `openhands --help` on host | HIGH (direct) |
| Planning preset (`get_planning_agent`) | `openhands-tools/openhands/tools/preset/planning.py` (GitHub API) | HIGH |
| Planning system prompt phases | `openhands-sdk/openhands/sdk/agent/prompts/system_prompt_planning.j2` (GitHub API) | HIGH |
| PLAN.md path `.agents_tmp/PLAN.md` | `examples/01_standalone_sdk/24_planning_agent_workflow.py` (GitHub API) | HIGH |
| AGENTS.md injection mechanism | `tests/sdk/conversation/test_repo_root_project_skills.py` (GitHub API) | HIGH |
| TaskTrackerAction/Observation types | `frontend/src/types/v1/core/base/action.ts`, `observation.ts` (GitHub API) | HIGH |
| TaskItem structure | `frontend/src/types/v1/core/base/common.ts` (GitHub API) | HIGH |
| temperature/seed/top_p fields in LLM | `tests/sdk/config/test_llm_config.py` (GitHub API) | HIGH |
| config.toml template | `config.template.toml` (GitHub API) | HIGH |
| Planning Agent introduction (v1.5.0) | https://toolnavs.com/en/article/1218-openhands-releases-150-task-list-planning-agent-and-skill-slash-menus-are-launch | MEDIUM (third-party) |
| v1.5.0 release notes | GitHub releases page (WebFetch) | HIGH |
| Headless mode docs | https://docs.openhands.dev/openhands/usage/cli/headless | MEDIUM (incomplete) |
| Microagents docs | https://docs.openhands.dev/openhands/usage/microagents/microagents-repo | MEDIUM |
| LLM_TEMPERATURE / LLM_SEED as env vars | Inferred from naming convention + `--override-with-envs` pattern | LOW — UNVERIFIED |

---

*Stack research for: v1.4 Planning Comparison milestone — OpenHands CLI 1.16.0 / SDK v1.21.0*
*Researched: 2026-06-01*
