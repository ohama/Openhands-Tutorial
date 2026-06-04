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

## Last Milestone: v1.4 — Planning Comparison (SHIPPED 2026-06-04 · Claude-led vs OpenHands-native task planning)

> ✅ Shipped 2026-06-04 — 부록 D live. **Result (mixed/inconclusive — itself the finding):** an expert-authored plan helps the 35B mainly when the task is **out-of-distribution** (F# Arm A 1/3 vs Arm B 0/3); for in-distribution work the 35B self-plans just as well (Scala 3/3 vs 2/3+PARTIAL; Rust 3/3 tie). Extends "distribution, not size" onto the planning axis. The goal/target detail below is retained for history. Next milestone: run `/gsd:new-milestone`.

**Goal:** For the three existing worked examples — F# FsLex/FsYacc calculator, Rust HTTP server, Scala 3 calculator — capture and compare two task-planning regimes on the local **35B**, then publish the findings as a new 부록 D. **Arm A (Claude-led):** Claude authors the task decomposition, it is converted into an OpenHands-consumable plan, and OpenHands executes it. **Arm B (OpenHands-native):** OpenHands is given the whole goal in a single prompt and plans + decomposes + executes it itself. Research question: **does who plans (Claude vs OpenHands itself) change execution efficiency?**

**Target features:**
- A documented, repeatable **capture method** for both arms, per example, on 35B, under the carried honesty discipline (real captured runs, `source=agent` on every ActionEvent, no manual edits, scaffolding disclosed). The two planning artifacts (Claude's task plan; OpenHands' self-generated plan) are saved per example for qualitative comparison.
- A **metrics harness** that extracts per-arm, from the captured JSONL: retries / error-fix cycles, wall-clock + per-call time, LLM-call & TerminalAction counts, and final canonical-test pass/fail (14/20/5; `hello`; 2+3*4=14 etc.).
- The comparison applied to **all three examples** (F# / Rust / Scala), Arm A vs Arm B.
- A published **부록 D "계획 방식 비교: Claude 계획 vs OpenHands 자체 계획"** chapter, written verbatim from the captured comparison data — honest about which arm wins on which metric, including mixed/inconclusive results (that is itself a finding). Live on GitHub Pages.

**Open unknown to resolve (research):** OpenHands 1.16 headless's native planning mechanism — is there a plan / task-list tool or artifact format ("OpenHands plan / Task"), or does "OpenHands-native planning" just mean single-prompt self-decomposition by the agent loop? And the cleanest, fair way to "convert a Claude plan into an OpenHands plan" so Arm A and Arm B differ only in *who planned*, not in how the plan is delivered.

**Why this is interesting (the honesty story):** every prior milestone used Claude-authored task decomposition (task1/task2/task3 prompts) without ever testing whether that decomposition *helped*. v1.4 makes the planning step itself the object of study — a fair, captured A/B on the same model and same goals. The result may favor Claude-led planning, OpenHands-native, or be mixed per-metric; whichever it is, it is reported honestly from real captured data.

**Why this is interesting (the honesty story):** v1 (F# FsLex) hit the model's boundary — a parser-generator DSL, deeply out-of-distribution. v1.2 (Rust std) was in-distribution and succeeded unaided. v1.3 returns to the *calculator* goal but in Scala, where `sealed trait` ADTs + pattern matching are the canonical idiom — testing whether the model can write unaided the very thing it needed a scaffolded lexer for in F#. New unknowns to capture honestly: **Scala 3** (newer, less training data — the model may emit Scala 2 syntax) and **`scala-cli`** tooling. Success or stumble, both are good chapter material — and it lets the book end on a direct calculator-to-calculator comparison across three languages.

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

<!-- Shipped in v1.2 (2026-06-01). Live: https://ohama.github.io/Openhands-Tutorial/ch06-rust-server/intro.html -->

- ✓ Captured a real 35B OpenHands run of a minimal std-only Rust HTTP server (`cargo new` → `TcpListener` accept loop → `curl localhost:8080/` → `hello\n`, exit 0) — unaided attempt 1, with two genuine build failures self-corrected (format! heredoc syntax; E0382 borrow-checker) — v1.2
- ✓ Added a new 6부 "다른 워킹 예제 - Rust HTTP 서버" chapter group, written verbatim from the captured run (code byte-identical to source; both errors verbatim) — v1.2
- ✓ Re-published the updated book (live on GitHub Pages; 6부 reachable from sidebar nav) — v1.2
- ✓ Confirmed the cross-language hypothesis: the same 35B that failed FsLex unaided succeeded at std Rust unaided — Rust is more in-distribution; per-call latency comparable (~3.8s Rust / ~5.3s F#), run-total difference is call count — v1.2

<!-- Shipped in v1.3 (2026-06-01). Live: https://ohama.github.io/Openhands-Tutorial/ch07-scala-calc/intro.html -->

- ✓ Captured a real 35B OpenHands run of a minimal Scala 3 arithmetic calculator (`scala-cli`, hand-rolled recursive-descent parser, std-only) — unaided attempt 1; one self-corrected compile error (`private` member accessed from `@main`); `2+3*4 → 14`, `(2+3)*4 → 20`, `10-3-2 → 5` — v1.3
- ✓ Added a new 7부 "다른 워킹 예제 - Scala 계산기" chapter group, written verbatim from the captured run (code byte-identical to source; honest "no sealed-trait ADT" framing) — v1.3
- ✓ Re-published the updated book (live on GitHub Pages; 7부 reachable from sidebar) — v1.3
- ✓ Completed the "calculator trilogy" (F# scaffolded / Rust unaided / Scala unaided) — confirms the 35B's limit is domain-distribution, not model size — v1.3

<!-- Shipped in v1.4 (2026-06-04). Live: https://ohama.github.io/Openhands-Tutorial/appendix-d-planning-comparison.html -->

- ✓ Captured, per example (F# / Rust / Scala) on the 35B, two planning arms — Arm A (Claude-authored numbered plan → executed) and Arm B (bare goal → 35B self-plans via its task tracker → executes) — at **n=3** per cell (18 real JSONL runs), both planning artifacts saved (`claude-plan.md` + verbatim `oh-self-plan.md`), 18/18 `source=agent` honesty gates PASS — v1.4
- ✓ Extracted per-arm metrics from the captured JSONL (TerminalAction & event counts, wall-clock + per-call gap, error-fix cycles, canonical-test pass/fail) into per-arm `metrics.json` (median/min–max) + per-example `comparison.json`; P3 token metrics dropped (no `usage` in JSONL) — v1.4
- ✓ Added 부록 D "계획 방식 비교 — Claude 계획 vs OpenHands 자체 계획", written verbatim from the committed capture, honest about the mixed/inconclusive result (an expert plan helps mainly on the OOD F# task; in-distribution Scala/Rust self-plan just as well) — v1.4
- ✓ Re-published live on GitHub Pages (HTTP 200 root + 부록 D + sidebar; `deploy.yml` unmodified) — v1.4

### Active

<!-- No active milestone. v1.4 shipped 2026-06-04. Start the next milestone with /gsd:new-milestone (which defines fresh requirements). Open candidates are tracked in STATE.md "Candidate next milestones" + MILESTONES.md "What's next". -->

(None — between milestones. Run `/gsd:new-milestone` to scope the next one.)

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
| v1.2: hold the model constant (35B), change the language to Rust (std-only) | Tests whether the v1 FsLex failure was about model size or domain-distribution; Rust is in-distribution where FsLex was not | ✓ Good — 35B wrote a working std Rust HTTP server unaided on attempt 1; hypothesis confirmed |
| v1.2: per-call timing must cite real measurements, never the v1 `~14–32s/call` pre-run prediction | Honesty core value — predictions never presented as measurements (the same correction v1.1 made for 부록 C) | ⚠️ Caught in audit — 6부 had re-introduced the prediction; fixed to derived ~5.3s/call before close-out (TD-6) |
| v1.3: third example = the *same calculator goal* as v1, but in Scala (hand-rolled recursive descent, std-only) | Closes the "calculator trilogy" and isolates the distribution axis — same goal that needed a scaffolded FsLex lexer in F# | ✓ Good — 35B wrote it unaided in Scala 3; capability is domain-distribution, not size |
| v1.3: document what the agent actually wrote, not the assumed design | The pre-run scope assumed a `sealed trait Expr` ADT; the agent used direct recursive descent (no ADT) | ✓ Good — caught at plan time; chapter honestly notes the no-ADT reality instead of claiming the assumed ADT |
| v1.4: make the *planning step itself* the object of study — a fair A/B (Arm A Claude plan vs Arm B 35B self-plan) on the same model + goals, symmetric prompts enforced by a literal diff | Every prior milestone used Claude-authored task decomposition without testing whether it helped | ✓ Good — mixed/inconclusive result reported honestly; an expert plan helps mainly on the OOD F# task, not in-distribution Scala/Rust |
| v1.4: both arms use the default headless CodeActAgent (Arm B self-plans via its TaskTracker); no SDK PlanningAgent | Single-session headless constraint; keeps the only difference "who planned," not "how the plan is delivered" | ✓ Good — 35B emitted TaskTracker steps unaided in Arm B; clean qualitative contrast (Arm A 0 tracker events) |
| v1.4: when a reused measurement tool is found wrong, fix the tool deterministically + re-run all inputs, never hand-edit outputs | Honesty core value — the canonical detector mis-scored (false-FAILs + nulls); reconciling outputs by hand would be unverifiable | ✓ Good — patched detector reproduced the JSONL-event-cited RUN-NOTES exactly (commit `b7a74b9`), zero nulls |

---
*Last updated: 2026-06-04 after v1.4 milestone (Planning Comparison) shipped. Between milestones — next: `/gsd:new-milestone`.*
