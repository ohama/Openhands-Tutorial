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

## Current Milestone: v1.2 — Rust Example (second worked example)

**Goal:** Add a second worked example to the tutorial — OpenHands on the local Qwen 35B autonomously builds a minimal Rust HTTP server (`GET / → "hello\n"`, std-only, no external crates) — captured honestly and added as a new 6부 to the published book.

**Target features:**
- A real captured 35B OpenHands run of a minimal Rust HTTP server: `cargo new` → `std::net::TcpListener` + accept loop → minimal HTTP/1.1 response writer → `curl localhost:8080/` returns `hello\n`. Decomposed into ~3–4 scoped tasks following the v1 pattern.
- A new **6부 "다른 워킨 예제: Rust HTTP 서버"** in the book — structurally parallel to 4부 (calculator), written verbatim from the captured run with concept↔action callouts, any error-and-fix narration, and final source. The 사용자 프롬프트 / 내부 프로세스 / 결과 callout pattern from v1.1 continues here.
- Honest framing: the same model (35B) tackling a different language (Rust). Whatever the agent does — including any blind spots in Rust ownership/lifetimes/std::io — is captured as written, not retouched. If scaffolding is needed for any task, it is disclosed (parallel to v1's FsLex scaffolding disclosure).
- Re-published live to GitHub Pages.

**Why this is interesting (the honesty story):** v1 showed 35B couldn't write FsLex (FsLex was deeply out-of-distribution); v1.1 showed 122B could (capability scales with size for narrow domains). v1.2 holds the model constant and changes the *language* to one that is far more in-distribution (Rust). The expected outcome is success — but if the agent stumbles anywhere (e.g., borrow checker, manual HTTP framing edge cases), that becomes capture material exactly as the FsLex story did. Either outcome is good educational material.

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

<!-- Shipped in v1.1 (2026-05-28). Live: https://ohama.github.io/Openhands-Tutorial/appendix-c-comparison.html -->

- ✓ Captured a real 122B OpenHands run of the calculator with the `.fsl` lexer attempted unaided first (122B succeeded; scaffold fallback never triggered) — v1.1
- ✓ Added a 35B-vs-122B comparison chapter (부록 C) to the published book, with verbatim citations from both runs and explicit setup-asymmetry disclosure — v1.1
- ✓ Re-published the updated book (live on GitHub Pages, HTTP 200 on root + new chapter) — v1.1
- ✓ Added beginner-friendly 📨 사용자 프롬프트 / ⚙️ 내부 프로세스 / ✅ 결과 callouts to 4 run-walkthrough chapters (additive, out-of-band) — v1.1

### Active

<!-- v1.2 — Rust Example (started 2026-05-28). First concrete instance of EXT-01.
     Rust is in-distribution for 35B in a way FsLex was not — this milestone tests that hypothesis honestly. -->

- [ ] Capture a real 35B OpenHands run of a minimal Rust HTTP server (`cargo new` → `std::net::TcpListener` accept loop → minimal HTTP/1.1 response → `curl localhost:8080/` returns `hello\n`)
- [ ] Add a new 6부 "다른 워킨 예제: Rust HTTP 서버" chapter group to the published book, written verbatim from the captured run with the 사용자 프롬프트 / 내부 프로세스 / 결과 callout pattern
- [ ] Re-publish the updated book (live on GitHub Pages)

<!-- Deferred to later milestones (carried forward):
     - EXT-01 expansion: Go / Python / other-language worked examples following the Rust precedent
     - EXT-02: English translation
     - EXT-03: "build your own minimal agent in F#" appendix
     - EXT-04 (optional): local-vs-cloud model comparison
     - Polish: 4 remaining tech-debt items from v1.1-MILESTONE-AUDIT.md (TD-2..TD-5) -->


### Out of Scope

- Building our own agent from scratch in F# — superseded by the tutorial framing. OpenHands is
  the agent being demonstrated, not something we re-implement.
- Cloud/hosted LLM APIs — the tutorial uses the existing local Qwen server.
- Teaching F# language fundamentals — F#/FsLex/FsYacc appear only as the example project OpenHands builds.
- Teaching Rust language fundamentals — Rust appears in v1.2 only as the example project the agent builds. Readers are expected to be able to follow Rust syntax at a basic level; the chapter focuses on what the agent does, not Rust pedagogy.
- HTTP framework deep-dive in the Rust example — v1.2 uses `std::net::TcpListener` deliberately (no `hyper`/`axum`/`actix`) to keep the agent's work at the byte-and-socket level the tutorial can show end-to-end. Framework-based variants are out of scope for v1.2 (could be a later milestone).
- Contributing to or modifying OpenHands' source — we use it as-is.
- Comprehensive coverage of every OpenHands feature — the tutorial focuses on the agentic concepts and the worked examples (currently: F# calculator + Rust HTTP server).

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
*Last updated: 2026-05-28 — started v1.2 milestone (Rust HTTP server worked example, 35B)*
