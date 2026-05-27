# FSharpAgent — Agentic AI Lab

## What This Is

A hands-on learning project for studying and practicing **agentic AI** by building an
OpenHands-style coding agent **in F#**, powered by a local Qwen LLM. The agent works the way
OpenHands does — it plans, writes code, tests, and runs, looping on feedback until a task is
done. Learning proceeds through small F# console examples (each teaching one agentic concept),
culminating in a capstone agent that autonomously creates a working **calculator using FsLex +
FsYacc**. The audience is the author (self-directed learning).

## Core Value

By the end, the author understands agentic AI from the inside — having personally built the
tool-calling, agent loop, file/shell operations, and memory — demonstrated by an F# agent that
autonomously produces a working FsLex/FsYacc calculator.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] F# console program can call the local Qwen LLM and get a chat completion
- [ ] Agent can invoke tools via native function calling (OpenAI-format tool_calls)
- [ ] Agent runs an observe → think → act → repeat loop until a goal is met
- [ ] Agent has file tools (read file, write file, list directory)
- [ ] Agent has a shell tool (run a command, capture stdout/stderr/exit code)
- [ ] Agent maintains conversation memory / manages context across loop iterations
- [ ] Capstone agent autonomously creates an F# calculator project using FsLex + FsYacc
- [ ] Capstone agent compiles the project (`dotnet build`), reads errors, and fixes them in a loop
- [ ] Capstone agent verifies the calculator works (e.g., `2+3*4` evaluates to `14`)
- [ ] Each agentic concept is introduced as its own small, runnable F# console example before the capstone

### Out of Scope

- Running the real OpenHands (Python) tool as the working agent — OpenHands is a **reference
  blueprint** for the plan→test→run lifecycle, not a dependency. (Author wants to build the
  agent themselves, in F#, to learn the internals.)
- Cloud/hosted LLM APIs — the project uses the existing local Qwen server only.
- Web UI / GUI — console programs only.
- Production hardening (auth, sandboxing beyond basic safety, deployment) — this is a learning lab.
- Multi-agent orchestration — single agent is the scope for this milestone.
- Languages other than F# for the agent itself.

## Context

- **Greenfield** project in `/Users/ohama/projs/OpenHandsTests` (fresh git repo).
- **Local LLM server confirmed running and probed:**
  - Endpoint: `http://127.0.0.1:8000/v1` (OpenAI-compatible)
  - Model id: `/Users/ohama/llm-system/models/qwen36-35b` (the author's "Qwen 3.6 35B")
  - Server: MLX-based on Apple GPU (system_fingerprint shows `macOS ... applegpu`)
  - Health endpoint `/health` returns `{"status":"ok"}`
  - **Native tool/function calling verified working**: a test request returned
    `finish_reason: "tool_calls"` with a correct OpenAI-format tool_call.
  - Prompt caching is present (`cached_tokens` in usage) — context reuse across turns is cheap.
- **Performance note:** the 35B model on local hardware is slow per request (basic completion
  took noticeable time; a tool-calling request timed out at 60s and succeeded at ~240s). Code,
  examples, and any tests must use generous HTTP timeouts.
- **OpenHands as reference:** https://github.com/OpenHands/OpenHands — studied for its agent
  architecture (action/observation cycle, tools for file edits and shell, plan→test→run
  project-creation workflow). We re-create those ideas in F#, not the Python code.
- **FsLex / FsYacc:** F# lexer/parser generator tooling (the `FsLexYacc` NuGet package),
  the classic medium for the capstone calculator (tokenize → parse → evaluate arithmetic).

## Constraints

- **Tech stack**: Agent and all examples written in F# (.NET) — the author is practicing F#.
- **Tech stack**: Capstone calculator must use FsLex + FsYacc specifically (not hand-written parsing).
- **LLM**: Local `qwen36-35b` via the existing MLX server at `http://127.0.0.1:8000/v1` only —
  no cloud APIs.
- **API shape**: OpenAI-compatible chat completions with native `tools` / `tool_calls`.
- **Performance**: Local 35B inference is slow — design for long, single-request latencies
  (generous timeouts, minimal unnecessary calls).
- **Learning-first**: Build each agentic capability by hand to understand it; favor clarity
  over abstraction or premature framework use.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Build the agent in F# ourselves rather than run real OpenHands | The author's goal is to learn agentic internals (tool calling, loop, file/shell, memory) by building them; F# is the practice language | — Pending |
| OpenHands is a conceptual/workflow reference, not a runtime dependency | Want to emulate plan→test→run lifecycle without Python coupling | — Pending |
| Capstone task = build a FsLex/FsYacc calculator | Concrete, verifiable goal ("2+3*4 = 14") that exercises file + shell tools and the iterate-on-errors loop | — Pending |
| Learning shape = small examples first, then capstone | Each agentic concept gets an isolated, runnable example before integration | — Pending |
| Use existing local MLX Qwen server (OpenAI-compatible, native tool calling) | Already installed, verified working with tool_calls; no new infra needed | — Pending |
| Design for slow inference (generous timeouts) | 35B local inference observed to take tens of seconds to minutes per call | — Pending |

---
*Last updated: 2026-05-27 after initialization*
