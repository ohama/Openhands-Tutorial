# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-05-28 after v1 milestone)

**Core value:** A reader finishes understanding what agentic AI is — and, by following along, watches OpenHands (on a local Qwen server) autonomously plan, build, test, and run a real F# FsLex/FsYacc calculator.
**Current focus:** v1.1 — Model Comparison (35B vs 122B) — defining requirements

## Current Position

Milestone: v1.1 (Model Comparison) — STARTED 2026-05-28. v1 shipped & archived (live: https://ohama.github.io/Openhands-Tutorial/).
Phase: Not started (defining requirements). Phase numbering continues at 6+.
Status: Defining requirements for v1.1. Goal: capture a real 122B OpenHands run of the calculator (lexer unaided first), add a 35B-vs-122B comparison chapter, re-publish.
Last activity: 2026-05-28 — v1.1 started; PROJECT.md updated with Current Milestone section + Active goals.

### v1.1 environment facts (confirmed 2026-05-28)
- litellm proxy at `http://127.0.0.1:4000/v1` now serves THREE aliases: `qwen-35b` (→35B @ :8000), **`qwen-122b` (→122B @ :8001, NEW)**, `qwen-local` (alias →35B). 122B MLX server is up (launchd `com.ohama.qwen122b`).
- 122B run config = same proven v1 invocation, just `LLM_MODEL=openai/qwen-122b`: `LLM_MODEL="openai/qwen-122b" LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" openhands --headless --json --yolo --override-with-envs -t "<task>"` (LocalWorkspace, host dotnet). v1 task-prompts are archived at .planning/milestones/v1-phases/03-capture-the-openhands-run/task-prompts/ — but v1.1 attempts the lexer UNAIDED (no provided Lexer.fsl) first.
- Decision: 122B attempts the WHOLE calculator (incl. .fsl lexer) unaided first → test if it can do what the 35B couldn't (which forced the lexer scaffold in v1). Fall back to scaffolding only if it can't, and document.

Progress: [░░░░░░░░░░] v1.1 0% — defining requirements.

## Performance Metrics

**Velocity:**
- Total plans completed: 5
- Average duration: ~8 min
- Total execution time: ~50 min

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 01-scaffold-and-concept-chapters | 3/3 ✓ | ~35 min | ~12 min |
| 02-environment-setup-and-verification | 3/5 | ~16 min | ~5.3 min |

**Recent Trend:**
- Last 5 plans: 01-03 (~4 min), 02-01 (~4 min), 02-02 (~9 min), 02-03 (~3 min)
- Trend: Fast execution; 02-03 was pure writing from captured evidence

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Phase 5 / PUBLISH]: GitHub repo = **ohama/Openhands-Tutorial** (PUBLIC, ALREADY EXISTS). `origin` set to https://github.com/ohama/Openhands-Tutorial. book.toml `site-url = "/Openhands-Tutorial/"`. Pages URL will be https://ohama.github.io/Openhands-Tutorial/. → Phase 5 plan 05-04 deploy MUST use this repo name (NOT the old "OpenHandsTests") and must SKIP `gh repo create` (repo exists) — just push `main`, add the Actions workflow, enable Pages (source=GitHub Actions), verify live. NOTE: `/Users/ohama/projs/OpenHandsTests/...` paths inside chapters are the real LOCAL working dir in verbatim captured commands — intentionally NOT changed.

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
- [02-03]: Real timing documented in chapters (~14-15s/call from evidence); plan's "240s" figure was a worst-case estimate, not measured — chapters cite real evidence
- [02-03]: dotnet PATH confirmed bare dotnet works; no /opt/homebrew/bin prefix needed in agent PTY
- [02-03]: 3부 documentation complete; SUMMARY.md wired; 4부/5부 remain () drafts; mdbook build green
- [03-01]: Verbatim known-good calc.fsproj (FixLineDirectives + FsLexYacc 11.3.0) embedded in task1-scaffold.txt — bypasses # 0 "" line-directive bug without stalling the run on a non-instructive error
- [03-01]: 10-3-2=5 is the critical third test case — 2+3*4 and (2+3)*4 both pass even with naive no-%left grammar; only 10-3-2 exposes the right-associativity bug
- [03-01]: task3-parser.txt states "left-to-right" as a behavioral outcome only — never names %left so the naive-grammar bug can emerge honestly
- [03-01]: task6-fix.txt uses <ACTUAL_WRONG_OUTPUT> placeholder — plan 03-02 executor substitutes the real captured value from task5-buildtest.jsonl before invoking
- [03-02]: qwen-local file_editor tool always omits security_risk field (AgentErrorEvent); prompt must explicitly say "use shell commands (tee/cat), not file editor tool"
- [03-02]: FsLex (.fsl) has NO %% separator; all agents confused FsLex with FsYacc and added %% which breaks the build
- [03-02]: FsLexYacc 11.3.0 lexeme extraction in action code = LexBuffer<_>.LexemeString lexbuf (not lexeme lexbuf)
- [03-02]: FsLex header braces must each be on own line at col 0; inline { open Parser } causes 2-space indented output in generated .fs causing F# light-mode compilation failure
- [03-02]: Manual Lexer.fsl fix classified as Deviation Rule 3 after 3 agents (94+27+16 TerminalActions) exhausted retry budget; genuine error cycle documented in JSONL logs
- [03-02-attempt2]: Lexer.fsl provided verbatim in task2-lexer.txt — eliminates FsLex out-of-distribution blocker; agent's real work is parser + evaluator
- [03-02-attempt2]: Genuine error-and-fix captured in task3-parser.jsonl: 4 build failures (%start missing, %start <int> syntax invalid, same, LexBuffer.FromText non-existent) → self-corrected to build success
- [03-02-attempt2]: Branch A taken — error-and-fix in task3, not task5; task5 passed all 3 cases cleanly on first build; task6-fix.txt not needed
- [03-02-attempt2]: Agent wrote %left PLUS MINUS / %left STAR SLASH from the start — no precedence bug surfaced; associativity (10-3-2=5) was correct all along
- [03-03]: OpenHands JSONL event structure is nested dicts: ev['action']['kind']=='TerminalAction', ev['observation']['kind']=='TerminalObservation', ev['observation']['content'][0]['text'] — plan assumed flat key-value pairs (adapted during execution)
- [03-03]: Error-and-fix cycle confirmed programmatically at task3-parser.jsonl events 10–30 (4 build failures: FSY000, parse error x2, FS0039 LexBuffer.FromText) → autonomous self-correction to Build succeeded
- [03-03]: captured/ committed with all Phase-4-ready artifacts; oh-workdir/ confirmed gitignored; Lexer.fsl/.fsproj documented as scaffolded via prompts (honest record for Phase 4 narration)

### Phase 2 ENVIRONMENT — verified during execution (2026-05-27), DIVERGES from the 02 plans

The machine is a HEADLESS SSH Mac (Apple Silicon). Phase 2 plans assumed Docker Desktop + browser UI + ~/.openhands/config.toml + OpenHands 1.7 + raw MLX path. Verified reality:

- **Docker = Colima**, not Docker Desktop. `colima start --cpu 4 --memory 8 --disk 60` running. Daemon OK (`docker run hello-world` ✓). Socket at `/Users/ohama/.colima/default/docker.sock`; `/var/run/docker.sock` ABSENT → OpenHands needs `DOCKER_HOST=unix:///Users/ohama/.colima/default/docker.sock`.
- **LLM endpoint = existing litellm PROXY**, not the raw MLX server. A launchd agent `com.ohama.litellm` (PID 14555) runs litellm on `*:4000` (all interfaces), config `/Users/ohama/agent-stack/litellm/config.yaml`, exposing model alias **`qwen-local`** → routes to `openai//Users/ohama/llm-system/models/qwen36-35b` @ localhost:8000. `/v1/models` needs NO auth. Basic chat ✓ and TOOL CALLING ✓ both verified through the proxy. (MLX server itself is launchd `com.ohama.qwen36-35b` PID 73832 on 127.0.0.1:8000.)
  → Use **model `openai/qwen-local`**, base_url **`http://127.0.0.1:4000/v1`** (LLM is called from the HOST process in OpenHands V1, so host-reachable URL; NOT host.docker.internal). This ELIMINATES the double-slash model-path problem.
- **OpenHands actual version = SDK v1.21.0** (not 1.7). Installed via `uv tool install openhands --python 3.12`; binaries `openhands`, `openhands-acp` at ~/.local/bin. Python 3.12.13 via uv.
- **Config = env vars, not config.toml**: `openhands --headless --json --yolo --override-with-envs` reads `LLM_MODEL` / `LLM_BASE_URL` / `LLM_API_KEY`. No `~/.openhands/` yet.
- **Headless, no browser**: the `openhands serve` + localhost:3000 browser checkpoint is not doable over SSH. Use the headless CLI (`openhands --headless --json -t "..."`) for the run (Phase 3) and verify via curl/JSONL, not a browser.
- **RESOLVED by 02-02:** headless OpenHands tool-call path proven end-to-end. LocalWorkspace = host PTY (no Docker needed for primary path). `--override-with-envs` routes LLM_* to litellm proxy. echo OPENHANDS_PING_OK action+observation captured (PING PASS). dotnet 10.0.203 in agent observation (DOTNET PASS). See 02-VERIFICATION-EVIDENCE.md for verbatim outputs.

→ RESOLVED: Phase 2 was re-planned to 3 plans against this verified environment and all 3 executed + verified 5/5. The original Docker-Desktop 5-plan sketch is archived under the phase dir's _archived-docker-desktop-plans/.

### Phase 3 invocation facts (carry forward)

The exact OpenHands invocation Phase 3 will use to build the calculator (proven in 02-02):
```
LLM_MODEL="openai/qwen-local" LLM_BASE_URL="http://127.0.0.1:4000/v1" LLM_API_KEY="dummy" \
OPENHANDS_WORK_DIR="<scratch dir>" \
openhands --headless --json --yolo --override-with-envs -t "<task>" | tee run.jsonl
```
LocalWorkspace = agent runs on the host (no container). bare `dotnet` (10.0.203) works in the agent PTY. JSONL events: ActionEvent (TerminalAction) + ObservationEvent (TerminalObservation). Simple tasks ran ~15s; the multi-step calculator build will be longer — decompose into ≥5 scoped tasks (RUN-02).

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 2 — RESOLVED by 02-01]: Model id confirmed: `qwen-local` (as returned by /v1/models). Use `LLM_MODEL=openai/qwen-local`, `LLM_BASE_URL=http://127.0.0.1:4000/v1`.
- [Phase 2 — RESOLVED by 02-01]: OpenHands version is SDK v1.21.0 / CLI 1.16.0 (not 1.7). ARM64 implicit — uv installed native Python 3.12.13.
- [Phase 2 — RESOLVED by 02-02]: `--override-with-envs` confirmed REQUIRED; tool-call end-to-end proven (PING PASS + DOTNET PASS). Invocation shape confirmed working.
- [Phase 2 — RESOLVED by 02-02]: dotnet bare path works in agent PTY; no absolute path needed. 02-VERIFICATION-EVIDENCE.md is the authoritative source.
- [Phase 3 — COMPLETE]: All 3 plans done; captured/ committed; Phase 4 ready to start

## Session Continuity

Last session: 2026-05-28
Stopped at: 05-04 Task 1 committed (0bdbe63 — deploy.yml + book.toml repo fields). Paused at publish checkpoint (Task 2): user must authorize `git push -u origin main` + `gh api ... pages` enable. Repo is ohama/Openhands-Tutorial (already public on GitHub). Warning: pushing makes .planning/ history public.
Resume file: None — continuation agent should resume 05-04 Task 2 after user confirms publish authorization.
