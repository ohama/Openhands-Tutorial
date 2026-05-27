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

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Tutorial explains agentic AI concepts (tool/function calling, agent loop, plan→test→run, memory/context) in accessible terms
- [ ] Tutorial introduces OpenHands as the example agentic system and how its architecture maps to those concepts
- [ ] Tutorial documents setup: installing/running OpenHands and connecting it to the local Qwen server (OpenAI-compatible endpoint)
- [ ] Tutorial walks through OpenHands building the F# FsLex/FsYacc calculator end to end (plan → write → test → run)
- [ ] Tutorial includes real captured OpenHands output (commands, iterations, errors-and-fixes) at the key steps
- [ ] Tutorial shows the resulting calculator working (e.g., `2+3*4` → `14`) with the final F# source
- [ ] Tutorial is structured as an mdBook (chapters, navigation) and builds cleanly
- [ ] Tutorial is published to GitHub Pages
- [ ] Tutorial is written in Korean (English for technical terms)

### Out of Scope

- Building our own agent from scratch in F# — superseded by the tutorial framing. OpenHands is
  the agent being demonstrated, not something we re-implement.
- Cloud/hosted LLM APIs — the tutorial uses the existing local Qwen server.
- Teaching F# language fundamentals — F#/FsLex/FsYacc appear only as the example project OpenHands builds.
- Contributing to or modifying OpenHands' source — we use it as-is.
- Comprehensive coverage of every OpenHands feature — the tutorial focuses on the agentic concepts and the one worked example.

## Context

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
| Pivot from "build an F# agent to learn" → "write a tutorial teaching agentic AI via OpenHands" | Author redirected: the deliverable is a tutorial, with OpenHands as the example agentic system | — Pending |
| OpenHands is used as-is (the agent we demonstrate), not re-implemented | Tutorial teaches agentic AI by showing a real, working agent | — Pending |
| Worked example = OpenHands building an F# FsLex/FsYacc calculator | Concrete, verifiable goal ("2+3*4 = 14") that shows the full plan→test→run loop | — Pending |
| Format = mdBook → GitHub Pages | Author has mdbook/pages skills set up; good for a navigable published tutorial | — Pending (assumed) |
| Language = Korean (English technical terms) | Author communicates in Korean | — Pending (assumed) |
| Depth = conceptual explanation backed by real captured OpenHands runs | Real runs prove agentic AI works and make the tutorial trustworthy | — Pending (assumed) |
| OpenHands connects to existing local MLX Qwen server (OpenAI-compatible, tool calling verified) | Already installed and working; no new infra | — Pending |

---
*Last updated: 2026-05-27 after project pivot to tutorial framing*
