# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-27)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run a real F# FsLex/FsYacc calculator.
**Current focus:** Phase 2 — Environment Setup & Verification (next)

## Current Position

Phase: 1 of 5 (Scaffold & Concept Chapters) — ✓ COMPLETE, goal verified 5/5
Plan: 3 of 3 complete (01-01 scaffold, 01-02 concept+vocabulary, 01-03 architecture). NOTE: the roadmap originally sketched 4 plans; the planner collapsed them into 3 real plans (no 01-04).
Status: Phase 1 complete and verified. Ready to plan Phase 2.
Last activity: 2026-05-27 — Phase 1 verified (mdbook build green; 1부+2부 chapters written in Korean; CONCEPT-01/02/03, BOOK-01/02 satisfied)

Progress: [███░░░░░░░] 15% (3/20 plans) — Phase 1 of 5 done

## Performance Metrics

**Velocity:**
- Total plans completed: 3
- Average duration: ~10 min
- Total execution time: ~35 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-scaffold-and-concept-chapters | 3/3 ✓ | ~35 min | ~12 min |

**Recent Trend:**
- Last 5 plans: 01-01 (~15 min), 01-02 (partial/parallel), 01-03 (~4 min)
- Trend: Fast execution for content-writing plans

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Capture gate enforced — Phase 3 (run capture) strictly depends on Phase 2 (verified env); Phase 4 (worked-example chapter) strictly depends on Phase 3
- [Roadmap]: VERIFY-01 and VERIFY-02 placed in Phase 4 (not Phase 3) — verification content belongs in the walkthrough chapter, written from captured evidence
- [Roadmap]: BOOK-01 and BOOK-02 placed in Phase 1 — mdBook scaffold and Korean language constraint apply from the very first chapter
- [01-01]: mdbook installed via brew (0.5.3) — was not pre-installed; use /opt/homebrew/bin/mdbook in all subsequent plans
- [01-01]: mdBook 0.5.x site-url goes into 404.html base href, not index.html asset paths — this is correct behavior for GitHub Pages project sites
- [01-02]: Prose-only forward pointers to 4부 chapters — each vocabulary term ends with a "4부에서 볼 수 있습니다" sentence; no Markdown links to unwritten Phase 4 files
- [01-02]: Only allowed cross-chapter Markdown link is overview.md → concepts.md (same directory, both files exist)
- [01-03]: Prose-only forward references to 3부+ chapters — draft SUMMARY.md entries have no files; Markdown links produce dead links
- [01-03]: ASCII art used for all ch02 architecture diagrams — zero preprocessor dependencies, builds cleanly with mdBook 0.5.3

### Phase 2 ENVIRONMENT — verified during execution (2026-05-27), DIVERGES from the 02 plans

The machine is a HEADLESS SSH Mac (Apple Silicon). Phase 2 plans assumed Docker Desktop + browser UI + ~/.openhands/config.toml + OpenHands 1.7 + raw MLX path. Verified reality:

- **Docker = Colima**, not Docker Desktop. `colima start --cpu 4 --memory 8 --disk 60` running. Daemon OK (`docker run hello-world` ✓). Socket at `/Users/ohama/.colima/default/docker.sock`; `/var/run/docker.sock` ABSENT → OpenHands needs `DOCKER_HOST=unix:///Users/ohama/.colima/default/docker.sock`.
- **LLM endpoint = existing litellm PROXY**, not the raw MLX server. A launchd agent `com.ohama.litellm` (PID 14555) runs litellm on `*:4000` (all interfaces), config `/Users/ohama/agent-stack/litellm/config.yaml`, exposing model alias **`qwen-local`** → routes to `openai//Users/ohama/llm-system/models/qwen36-35b` @ localhost:8000. `/v1/models` needs NO auth. Basic chat ✓ and TOOL CALLING ✓ both verified through the proxy. (MLX server itself is launchd `com.ohama.qwen36-35b` PID 73832 on 127.0.0.1:8000.)
  → Use **model `openai/qwen-local`**, base_url **`http://127.0.0.1:4000/v1`** (LLM is called from the HOST process in OpenHands V1, so host-reachable URL; NOT host.docker.internal). This ELIMINATES the double-slash model-path problem.
- **OpenHands actual version = SDK v1.21.0** (not 1.7). Installed via `uv tool install openhands --python 3.12`; binaries `openhands`, `openhands-acp` at ~/.local/bin. Python 3.12.13 via uv.
- **Config = env vars, not config.toml**: `openhands --headless --json --yolo --override-with-envs` reads `LLM_MODEL` / `LLM_BASE_URL` / `LLM_API_KEY`. No `~/.openhands/` yet.
- **Headless, no browser**: the `openhands serve` + localhost:3000 browser checkpoint is not doable over SSH. Use the headless CLI (`openhands --headless --json -t "..."`) for the run (Phase 3) and verify via curl/JSONL, not a browser.
- Still TODO for Phase 2: build the .NET sandbox image and confirm `dotnet --version` inside an OpenHands sandbox session; run one headless OpenHands task that calls a tool end-to-end (proves SETUP-01/02/04 for real). NOTE: which workspace the headless CLI uses (Local vs Docker) and whether it pulls the multi-GB agent-server image must be confirmed by running it.

→ CONSEQUENCE: Phase 2 plans 02-01..02-05 and their must_haves are now out of sync with reality. Recommend RE-PLANNING Phase 2 against these verified facts before further execution, so plans + the 3부 setup chapter document what truly works.

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 2]: Exact model id string after `openai/` must be confirmed via `curl http://127.0.0.1:8000/v1/models` before configuring OpenHands
- [Phase 2]: `agent_settings.json` config key names not confirmed (official reference 404'd during research — validate against running OpenHands 1.7)
- [Phase 2]: OpenHands 1.7 ARM64 vs Rosetta status on Apple Silicon needs verification at setup time
- [Phase 3]: 35B local model reliability over a long multi-step loop is empirical — task decomposition into ≥5 narrow tasks is the primary mitigation

## Session Continuity

Last session: 2026-05-27
Stopped at: Phase 1 complete and verified (5/5). mdBook scaffold + 1부/2부 chapters written in Korean, mdbook build exits 0. Next: /gsd:plan-phase 2 (Environment Setup & Verification — the capture gate).
Resume file: None
