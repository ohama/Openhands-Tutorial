# OpenHands Agentic AI 튜토리얼

## What This Is

A **tutorial** that teaches **Agentic AI** using **OpenHands** as the worked example. The
tutorial explains what agentic AI is and how an agentic system works, then walks the reader
through OpenHands — running on a **local Qwen LLM** — creating a real project the OpenHands way:
**plan → write → test → run**, iterating on feedback. The concrete example the tutorial builds
is an **F# calculator using FsLex + FsYacc**. Written in Korean, published as an **mdBook** on
GitHub Pages. The audience is developers learning agentic AI hands-on.

## Core Value

A reader can finish the tutorial understanding what agentic AI is — and, by following along,
watch OpenHands (on a local Qwen server) autonomously plan, build, test, and run a real F#
FsLex/FsYacc calculator. The OpenHands run is the proof that agentic AI works.

## Current Milestone: v1.1 — Model Comparison (35B vs 122B)

**Goal:** Re-run the same OpenHands calculator build on the newly-available local **122B** model (`openai/qwen-122b` @ `http://127.0.0.1:4000/v1`), capture it honestly, and add a **35B vs 122B comparison chapter** to the published tutorial.

**Target features:**
- A real captured **122B** OpenHands run of the FsLex/FsYacc calculator — attempted **unaided first** (no lexer scaffolding), to test whether the bigger local model can write the `.fsl` lexer the 35B could not.
- A **comparison chapter/appendix** in the book: capability differences (did 122B write the lexer itself? how did its error-and-fix cycle compare?) and **measured speed** vs the 35B's ~14–32s/cycle.
- Honest framing throughout (real capture, no fabrication, scaffolding disclosed if used); all v1 content preserved.

## Requirements

### Validated

<!-- Shipped in v1 (2026-05-28). Live: https://ohama.github.io/Openhands-Tutorial/ -->

- ✓ Explains agentic AI concepts (tool/function calling, agent loop, plan→write→test→run, memory/context) — v1
- ✓ Introduces OpenHands as the example agentic system and maps its V1 architecture to those concepts — v1
- ✓ Documents setup: installing/running OpenHands + connecting to the local Qwen endpoint — v1
- ✓ Walks through OpenHands building the F# FsLex/FsYacc calculator end to end — v1
- ✓ Includes real captured OpenHands output (commands, iterations, the error-and-fix cycle) — v1
- ✓ Shows the calculator working (`2+3*4` → `14`, plus `(2+3)*4=20`, `10-3-2=5`) with the final F# source — v1
- ✓ Structured as an mdBook, builds cleanly — v1
- ✓ Published to GitHub Pages (live) — v1
- ✓ Written in Korean (English for technical terms) — v1

### Active

<!-- v1.1 — Model Comparison (35B vs 122B) -->

- [ ] Capture a real 122B OpenHands run of the calculator (attempt the lexer unaided first)
- [ ] Add a 35B-vs-122B comparison chapter to the published book
- [ ] Re-publish the updated book (live on GitHub Pages)

<!-- Still deferred to a later milestone: more worked examples, English translation, "build your own minimal agent in F#" appendix. -->

### Out of Scope

- Building our own agent from scratch in F# — superseded by the tutorial framing. OpenHands is
  the agent being demonstrated, not something we re-implement.
- Cloud/hosted LLM APIs — the tutorial uses the existing local Qwen server.
- Teaching F# language fundamentals — F#/FsLex/FsYacc appear only as the example project OpenHands builds.
- Contributing to or modifying OpenHands' source — we use it as-is.
- Comprehensive coverage of every OpenHands feature — the tutorial focuses on the agentic concepts and the one worked example.

## Context

- **Current State (v1 SHIPPED 2026-05-28):** The Korean mdBook is live at https://ohama.github.io/Openhands-Tutorial/ (repo `ohama/Openhands-Tutorial`, public, deployed via GitHub Actions). 21 chapters / ~2,255 lines. The verified run path turned out to be: **Colima** (not Docker Desktop) on a headless SSH Mac, OpenHands **1.16 headless CLI on LocalWorkspace**, configured by **env vars** (`openai/qwen-local` via the existing **litellm proxy** at `127.0.0.1:4000`, `--override-with-envs`), with **.NET on the host**. Measured tool-call cycles were **~14–32s** (the early "~240s/call" estimate below was never measured). The bullets below this one are the project's *original* pre-pivot assumptions, kept for history.
- **Greenfield** project in `/Users/ohama/projs/OpenHandsTests` (fresh git repo).
- **Deliverable is documentation (a tutorial), not an application.** Author has `mdbook` and
  `pages` skills configured for building/publishing mdBooks to GitHub Pages.
- **Local LLM server confirmed running and probed** (OpenHands will connect to this):
  - Endpoint: `http://127.0.0.1:8000/v1` (OpenAI-compatible)
  - Model id: `/Users/ohama/llm-system/models/qwen36-35b` (the author's "Qwen 3.6 35B")
  - Server: MLX-based on Apple GPU (system_fingerprint shows `macOS ... applegpu`)
  - Health endpoint `/health` returns `{"status":"ok"}`
  - **Native tool/function calling verified working**: a test request returned
    `finish_reason: "tool_calls"` with a correct OpenAI-format tool_call — important, since
    OpenHands relies on tool calling.
  - Prompt caching present (`cached_tokens` in usage).
- **Performance note:** the 35B model on local hardware is slow per request (a tool-calling
  request timed out at 60s, succeeded at ~240s). OpenHands runs will be slow; the tutorial
  should set expectations and use patient timeouts.
- **OpenHands:** https://github.com/OpenHands/OpenHands — the agentic AI system the tutorial
  teaches. Typically run via Docker/CLI; can target an OpenAI-compatible local model. Setup
  details (Docker, model config pointing at the local endpoint) must be verified during research.
- **FsLex / FsYacc:** F# lexer/parser generator tooling (`FsLexYacc` NuGet), the medium for the
  example calculator OpenHands builds (tokenize → parse → evaluate arithmetic).

## Constraints

- **Output format**: Tutorial authored as an mdBook, published to GitHub Pages.
- **Language**: Korean (English for technical terms).
- **Agent**: OpenHands used as-is (not re-implemented), connected to the local Qwen server.
- **LLM**: Local `qwen36-35b` via the MLX server at `http://127.0.0.1:8000/v1` — no cloud APIs.
- **Example project**: F# calculator using FsLex + FsYacc specifically.
- **Authenticity**: Key tutorial steps backed by real captured OpenHands runs, not invented output.
- **Performance**: Local 35B inference is slow — tutorial and any live runs must tolerate long latencies.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Pivot from "build an F# agent to learn" → "write a tutorial teaching agentic AI via OpenHands" | Author redirected: the deliverable is a tutorial, with OpenHands as the example agentic system | ✓ Good |
| OpenHands is used as-is (the agent we demonstrate), not re-implemented | Tutorial teaches agentic AI by showing a real, working agent | ✓ Good |
| Worked example = OpenHands building an F# FsLex/FsYacc calculator | Concrete, verifiable goal ("2+3*4 = 14") that shows the full plan→test→run loop | ✓ Good |
| Format = mdBook → GitHub Pages | Author has mdbook/pages skills set up; good for a navigable published tutorial | ✓ Good |
| Language = Korean (English technical terms) | Author communicates in Korean | ✓ Good |
| Depth = conceptual explanation backed by real captured OpenHands runs | Real runs prove agentic AI works and make the tutorial trustworthy | ✓ Good |
| OpenHands connects to existing local MLX Qwen server (OpenAI-compatible, tool calling verified) | Already installed and working; no new infra | ⚠️ Adjusted — connected via the existing **litellm proxy** (`qwen-local` @ `127.0.0.1:4000`) with OpenHands on **LocalWorkspace** (headless CLI); the raw-MLX/DockerWorkspace assumption changed during Phase 2 |

---
*Last updated: 2026-05-28 — started v1.1 milestone (35B vs 122B model comparison)*
