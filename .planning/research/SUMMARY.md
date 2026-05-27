# Project Research Summary

**Project:** OpenHands Agentic AI 튜토리얼 (Korean mdBook)
**Domain:** Technical tutorial / documentation — teaching agentic AI through a real OpenHands run on a local LLM
**Researched:** 2026-05-27
**Confidence:** MEDIUM-HIGH

## Executive Summary

This is a **documentation project**, not an application: a Korean-language mdBook tutorial that
teaches agentic AI by showing OpenHands — running on the author's local Qwen 35B — autonomously
build an F# FsLex/FsYacc calculator via a plan → write → test → run loop. The "product" is the
tutorial; the OpenHands run is its central, real, captured artifact. Experts build tutorials
like this by capturing a genuine run first (commands, iterations, errors-and-fixes) and writing
the prose around what actually happened, rather than fabricating idealized transcripts.

The recommended approach is a strict authoring dependency chain: draft scaffolding → write the
concept and architecture chapters → **stand up and verify the environment** → **capture a real
OpenHands run** → write the worked-example chapter from that capture → finish with verification
and wrap-up. The environment setup is the riskiest gate: OpenHands runs in Docker and must reach
the host's MLX server at `http://host.docker.internal:8000/v1` (NOT `127.0.0.1`), with a LiteLLM
model string prefixed `openai/`, a non-empty dummy API key, and a raised timeout (≥300–600s)
because the 35B model takes ~240s per tool call.

Key risks are concentrated in three places: (1) the local model being too slow/unreliable for a
long agentic loop, mitigated by decomposing the calculator build into small scoped tasks and
honestly framing model failures as part of the lesson; (2) configuration footguns
(`host.docker.internal`, `openai/` prefix, timeout, and the OpenHands sandbox lacking .NET by
default — it needs a custom Docker image); and (3) F#/FsYacc grammar correctness (operator
precedence via `%left` ordering) that the agent is likely to get wrong, which is itself good
tutorial material if captured.

## Key Findings

### Recommended Stack

Three layers: tutorial authoring, the OpenHands runtime, and the F# example project. All current
versions verified against official sources (May 2026).

**Core technologies:**
- **mdBook 0.5.3** (`brew install mdbook`) — tutorial authoring; deploy to GitHub Pages via `actions/deploy-pages@v4` (native Pages, not legacy `gh-pages` branch). Must set `site-url = "/<repo-name>/"` for project pages or deployed CSS/JS 404s.
- **OpenHands 1.7 / V1 SDK** (`uv tool install openhands --python 3.12`, then `openhands serve`) — the agentic system. Requires Docker Desktop running (sandboxes are containers); enable "Allow the default Docker socket to be used."
- **LiteLLM config (critical):** model string = `openai/qwen36-35b` (prefix tells LiteLLM to use the OpenAI client; exact id after `openai/` must match `GET /v1/models`); base_url from inside Docker = `http://host.docker.internal:8000/v1`; api_key = any non-empty string; `timeout`/`LLM_TIMEOUT` ≥ 300–600s.
- **.NET SDK 10.0.300** (LTS, ARM64-native) + **FsLexYacc 11.3.0** — the example project. FsLexYacc's MSBuild integration runs `fslex`/`fsyacc` automatically on `dotnet build`; `.fsl` + `.fsy` + generated files declared in `.fsproj`.

Full details, commands, and "what NOT to use" in `STACK.md`.

### Expected Features

Tutorial "features" = chapters/sections. From `FEATURES.md`:

**Must have (table stakes):**
- Concept intro: what agentic AI is, vs reactive/chatbot AI — users expect grounding before the demo
- Core vocabulary: tool calling, agent loop, planning, memory/context — must precede the run
- Environment setup: Docker + OpenHands + local Qwen endpoint (the hard part; `openai/` prefix, `host.docker.internal`, timeout)
- Worked-example intro + the OpenHands run walkthrough (the core chapter, real captured output)
- Results/verification (`2+3*4 → 14`, final source) and troubleshooting

**Should have (competitive differentiators):**
- Real captured run output including errors and retries (no comparable Korean tutorial exists)
- Concept-to-action callouts woven into the walkthrough; error-and-fix cycle narration
- Honest local-LLM performance transparency (~240s/call); CodeAct/V1 architecture sidebar; reproducibility appendix

**Defer / exclude (anti-features):**
- Teaching F# from scratch; exhaustive OpenHands feature reference; fabricated transcripts; cloud-API promotion; re-implementing an agent from scratch; theory with no forward pointer; any tutorial without a verifiable end result

### Architecture Approach

Two architectures, both in `ARCHITECTURE.md`. (1) The **mdBook** is SUMMARY.md-driven: ~5 parts
(concepts → OpenHands architecture → setup → calculator walkthrough → wrap-up), where ch04
(calculator) cannot be finalized until a real run is captured. (2) **OpenHands V1** is a clean
four-package SDK (`openhands-sdk`, `-tools`, `-workspace`, `-agent-server`); V0's monolithic
design (pre-April 2026) is deprecated — avoid outdated blog posts.

**Major components (OpenHands V1):**
1. **Conversation.step() loop** — 5-phase `while not finished` agent loop (drain → check → prepare prompt → call LLM via LiteLLM → classify/dispatch)
2. **EventLog** — append-only single source of truth; ActionEvent / ObservationEvent; condensation for memory
3. **DockerWorkspace + Action Execution Server** — the sandbox where shell/file actions run; self-correction emerges because stderr/exit codes re-enter the EventLog for the next LLM turn

Concept ↔ component mapping (tool calling ↔ ActionEvent + LiteLLM schemas; agent loop ↔ step() loop; memory ↔ EventLog; plan→test→run ↔ CodeActAgent methodology; self-correction ↔ Observation→next call) is laid out for pairing each concept chapter with real behavior.

### Critical Pitfalls

Top items from `PITFALLS.md`:

1. **`127.0.0.1` vs `host.docker.internal`** — the #1 silent failure; every Docker example must use `host.docker.internal:8000`.
2. **LiteLLM model name** — needs `openai/` prefix and must match `/v1/models` exactly (possibly the ugly full path).
3. **Timeout / retry storm** — set `LLM_TIMEOUT` ≥ 600s; otherwise 8 retries × 240s = ~32 min of noise per stuck call.
4. **Sandbox lacks .NET** — base image `nikolaik/python-nodejs` has no dotnet; a custom Dockerfile (via `dotnet-install.sh`) is required before any F# run. Verify before the live capture.
5. **FsYacc precedence** — `%left PLUS MINUS` then `%left TIMES DIVIDE` (later = higher precedence) is required for `2+3*4 = 14`; `%nonassoc` is broken (issue #39) so use `%right` for unary minus. The agent will likely get this wrong — capture it.
6. **Agent stuck-loop on slow builds** — decompose into ≥5 narrow tasks (scaffold → lexer → parser → evaluator → integration), not one mega-prompt.

## Implications for Roadmap

Suggested phase structure (authoring dependency chain is the spine):

### Phase 1: Tutorial scaffold & concept chapters
**Rationale:** Independent of any run; can be written immediately and de-risks structure early.
**Delivers:** mdBook initialized (SUMMARY.md, book.toml, `site-url`), concept chapters (what agentic AI is, vocabulary), OpenHands V1 architecture chapter.
**Addresses:** concept intro, vocabulary, architecture sidebar.
**Avoids:** unmotivated theory (each concept points forward to where it appears in the run).

### Phase 2: Environment setup & verification (the gate)
**Rationale:** Highest-risk; nothing downstream works until the env is proven. Must precede capture.
**Delivers:** Setup chapter + a verified working stack: OpenHands installed, Docker reachable, custom .NET sandbox image, LLM config (`openai/` prefix, `host.docker.internal`, timeout), and a smoke test (tool-call ping, `dotnet --version` in sandbox).
**Uses:** OpenHands 1.7, LiteLLM config, .NET 10 image.
**Avoids:** pitfalls 1–4.

### Phase 3: Capture the real OpenHands run
**Rationale:** The central artifact; everything in the worked-example chapter depends on it. Decomposed tasks reduce stuck-loops.
**Delivers:** A full captured run (tee'd to log) of OpenHands building the FsLex/FsYacc calculator across scoped tasks, including the error-and-fix moments, ending at `2+3*4 → 14`.
**Avoids:** pitfalls 5–6; fabricated transcripts.

### Phase 4: Worked-example chapter from the capture
**Rationale:** Can only be written after Phase 3.
**Delivers:** The core walkthrough chapter with real output, concept-to-action callouts, error-and-fix narration, final source, and verification.

### Phase 5: Troubleshooting, reproducibility & publish
**Rationale:** Polish + shipping; depends on everything above being stable.
**Delivers:** Troubleshooting chapter (local-LLM failure modes, Docker networking), reproducibility appendix (exact task strings, Docker commands, expected outputs), GitHub Pages deploy via Actions.

### Phase Ordering Rationale
- The **capture gate** dominates: concept/architecture chapters (Phase 1) are run-independent and come first; the worked-example chapter (Phase 4) is strictly blocked on a real run (Phase 3), which is itself blocked on a verified environment (Phase 2).
- Setup is isolated as its own phase because it concentrates the highest-probability failures (Docker networking, model string, timeout, missing .NET).
- Publishing is last because deploy-path/`site-url` issues only surface on the live site.

### Research Flags

Phases likely needing deeper research / live validation during planning:
- **Phase 2:** confirm exact model id from `curl http://127.0.0.1:8000/v1/models`; whether OpenHands 1.7 image is ARM64-native or needs Rosetta; exact custom-Dockerfile recipe for .NET in the sandbox; `agent_settings.json` key names (official config reference page 404'd during research).
- **Phase 3:** how reliably the 35B model drives the multi-step loop (capability/decomposition tuning is empirical).

Phases with standard patterns (can skip deep research):
- **Phase 1** (mdBook authoring — well documented), **Phase 5** (mdBook → Pages deploy — established).

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | mdBook & F#/FsLexYacc HIGH (official sources); OpenHands LLM-config keys MEDIUM (some from community; runtime model-id must be confirmed) |
| Features | HIGH | Grounded in conventions of effective technical tutorials |
| Architecture | HIGH | OpenHands V1 verified against SDK docs/paper; mdBook against official docs |
| Pitfalls | HIGH | Each backed by a specific GitHub issue or official doc; MLX tool-call edge cases MEDIUM |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address
- **Exact model id after `openai/`:** confirm via `curl /v1/models` before configuring OpenHands (Phase 2).
- **.NET in the OpenHands sandbox:** the base image lacks dotnet; build and verify a custom image before the live capture (Phase 2).
- **OpenHands ARM64 image vs Rosetta:** verify at setup; file-only tasks tolerate Rosetta but native is faster (Phase 2).
- **`agent_settings.json` config keys:** official reference page 404'd; validate against the running version (Phase 2).
- **35B reliability in a long loop:** empirical; mitigate with task decomposition and honest framing (Phase 3).

## Sources

### Primary (HIGH confidence)
- mdBook official docs + Homebrew formula (0.5.3); GitHub Pages `actions/deploy-pages@v4`
- OpenHands GitHub repo + V1 SDK docs (v1.23.1, 2026-05-25) + SDK paper (arXiv 2511.03690)
- NuGet.org (FsLexYacc 11.3.0); Microsoft .NET download (SDK 10.0.300); official FsLexYacc docs

### Secondary (MEDIUM confidence)
- LiteLLM docs for OpenAI-compatible custom endpoints (`openai/` prefix, base_url)
- Community sources for `agent_settings.json` keys; ml-explore issue #613 (MLX tool-call edge cases)
- FsYacc issue #39 (`%nonassoc` broken → use `%right`)

### Tertiary (LOW confidence — needs validation)
- Exact MLX-advertised model id string; OpenHands 1.7 image ARM64 status

---
*Research completed: 2026-05-27*
*Ready for roadmap: yes*
