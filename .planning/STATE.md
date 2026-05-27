# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-27)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run a real F# FsLex/FsYacc calculator.
**Current focus:** Phase 2 — Environment Setup & Verification (in progress)

## Current Position

Phase: 2 of 5 (Environment Setup & Verification) — In progress
Plan: 2 of 5 complete in Phase 2 (02-01 preflight + 02-02 end-to-end verification). Phase 1 remains ✓ COMPLETE (3/3).
Status: In progress — 02-02 complete. Next: 02-03.
Last activity: 2026-05-27 — Completed 02-02-PLAN.md: end-to-end headless tool-call verification (PING PASS + DOTNET PASS)

Progress: [█████░░░░░] 25% (5/20 plans) — Phase 1 done + 02-01 + 02-02

## Performance Metrics

**Velocity:**
- Total plans completed: 3
- Average duration: ~10 min
- Total execution time: ~35 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-scaffold-and-concept-chapters | 3/3 ✓ | ~35 min | ~12 min |
| 02-environment-setup-and-verification | 2/5 | ~13 min | ~6.5 min |

**Recent Trend:**
- Last 5 plans: 01-01 (~15 min), 01-02 (partial/parallel), 01-03 (~4 min), 02-01 (~4 min), 02-02 (~9 min)
- Trend: Fast execution for preflight/evidence plans

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
- [02-02]: `--override-with-envs` is REQUIRED on openhands --headless; without it LLM_* env vars are silently ignored
- [02-02]: bare `dotnet` works in agent LocalWorkspace PTY (host PATH inherited); Phase 3/4 does NOT need /opt/homebrew/bin/dotnet prefix
- [02-02]: OPENHANDS_SUPPRESS_BANNER=1 recommended when tee-ing JSONL to keep output clean
- [02-02]: Observed headless run time 14-15s per tool-call cycle (plan warned ~240s+); qwen-local was fast during this session

### Phase 2 ENVIRONMENT — verified during execution (2026-05-27), DIVERGES from the 02 plans

The machine is a HEADLESS SSH Mac (Apple Silicon). Phase 2 plans assumed Docker Desktop + browser UI + ~/.openhands/config.toml + OpenHands 1.7 + raw MLX path. Verified reality:

- **Docker = Colima**, not Docker Desktop. `colima start --cpu 4 --memory 8 --disk 60` running. Daemon OK (`docker run hello-world` ✓). Socket at `/Users/ohama/.colima/default/docker.sock`; `/var/run/docker.sock` ABSENT → OpenHands needs `DOCKER_HOST=unix:///Users/ohama/.colima/default/docker.sock`.
- **LLM endpoint = existing litellm PROXY**, not the raw MLX server. A launchd agent `com.ohama.litellm` (PID 14555) runs litellm on `*:4000` (all interfaces), config `/Users/ohama/agent-stack/litellm/config.yaml`, exposing model alias **`qwen-local`** → routes to `openai//Users/ohama/llm-system/models/qwen36-35b` @ localhost:8000. `/v1/models` needs NO auth. Basic chat ✓ and TOOL CALLING ✓ both verified through the proxy. (MLX server itself is launchd `com.ohama.qwen36-35b` PID 73832 on 127.0.0.1:8000.)
  → Use **model `openai/qwen-local`**, base_url **`http://127.0.0.1:4000/v1`** (LLM is called from the HOST process in OpenHands V1, so host-reachable URL; NOT host.docker.internal). This ELIMINATES the double-slash model-path problem.
- **OpenHands actual version = SDK v1.21.0** (not 1.7). Installed via `uv tool install openhands --python 3.12`; binaries `openhands`, `openhands-acp` at ~/.local/bin. Python 3.12.13 via uv.
- **Config = env vars, not config.toml**: `openhands --headless --json --yolo --override-with-envs` reads `LLM_MODEL` / `LLM_BASE_URL` / `LLM_API_KEY`. No `~/.openhands/` yet.
- **Headless, no browser**: the `openhands serve` + localhost:3000 browser checkpoint is not doable over SSH. Use the headless CLI (`openhands --headless --json -t "..."`) for the run (Phase 3) and verify via curl/JSONL, not a browser.
- **RESOLVED by 02-02:** headless OpenHands tool-call path proven end-to-end. LocalWorkspace = host PTY (no Docker needed for primary path). `--override-with-envs` routes LLM_* to litellm proxy. echo OPENHANDS_PING_OK action+observation captured (PING PASS). dotnet 10.0.203 in agent observation (DOTNET PASS). See 02-VERIFICATION-EVIDENCE.md for verbatim outputs.

→ CONSEQUENCE: Phase 2 plans 02-01..02-05 and their must_haves are now out of sync with reality. Plans 02-01 and 02-02 executed successfully on the verified path. Remaining plans (02-03..02-05) may need adjustment.

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 2 — RESOLVED by 02-01]: Model id confirmed: `qwen-local` (as returned by /v1/models). Use `LLM_MODEL=openai/qwen-local`, `LLM_BASE_URL=http://127.0.0.1:4000/v1`.
- [Phase 2 — RESOLVED by 02-01]: OpenHands version is SDK v1.21.0 / CLI 1.16.0 (not 1.7). ARM64 implicit — uv installed native Python 3.12.13.
- [Phase 2 — RESOLVED by 02-02]: `--override-with-envs` confirmed REQUIRED; tool-call end-to-end proven (PING PASS + DOTNET PASS). Invocation shape confirmed working.
- [Phase 2 — RESOLVED by 02-02]: dotnet bare path works in agent PTY; no absolute path needed. 02-VERIFICATION-EVIDENCE.md is the authoritative source.
- [Phase 3]: 35B local model reliability over a long multi-step loop is empirical — task decomposition into ≥5 narrow tasks is the primary mitigation

## Session Continuity

Last session: 2026-05-27
Stopped at: Completed 02-02-PLAN.md (end-to-end headless verification). PING PASS + DOTNET PASS. 02-VERIFICATION-EVIDENCE.md written. Next: 02-03.
Resume file: None
