# Roadmap: OpenHands Agentic AI 튜토리얼

## Overview

This tutorial is built around a strict authoring dependency chain: run-independent chapters (concepts, architecture) come first, then environment verification opens the capture gate, then the real OpenHands run is captured, then the worked-example chapter is written from that capture, and finally troubleshooting, reproducibility, and publishing complete the book. The deliverable is a Korean mdBook on GitHub Pages that teaches agentic AI through a real, verifiable OpenHands run building an F# FsLex/FsYacc calculator.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Scaffold & Concept Chapters** - Initialize the mdBook and write the run-independent concept/architecture chapters ✓
- [x] **Phase 2: Environment Setup & Verification** - Install and verify the full stack; this is the capture gate ✓
- [ ] **Phase 3: Capture the OpenHands Run** - Execute the real run and capture its output
- [ ] **Phase 4: Worked-Example Chapter** - Write the core walkthrough chapter from the captured run
- [ ] **Phase 5: Troubleshooting, Reproducibility & Publish** - Complete the book and ship it to GitHub Pages

## Phase Details

### Phase 1: Scaffold & Concept Chapters
**Goal**: The mdBook structure exists and the run-independent chapters (what agentic AI is, vocabulary, OpenHands architecture) are written
**Depends on**: Nothing (first phase)
**Requirements**: CONCEPT-01, CONCEPT-02, CONCEPT-03, BOOK-01, BOOK-02
**Success Criteria** (what must be TRUE):
  1. `mdbook build` succeeds on the initial scaffold (no broken links, no missing chapters referenced in SUMMARY.md)
  2. The concept chapter defines agentic AI, distinguishes it from reactive chatbots, and a reader new to the topic can state the difference in their own words after reading
  3. The vocabulary chapter defines tool/function calling, the agent loop, plan→write→test→run, and memory/context — each with a forward pointer to where it appears in the run
  4. The OpenHands V1 architecture chapter maps the step() loop, EventLog, and DockerWorkspace to the agentic concepts from the vocabulary chapter
  5. All prose is written in Korean (English for technical terms such as "agent loop", "tool calling", "EventLog")
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Scaffold: book.toml, full SUMMARY.md (Phase-1 real paths + Phase 2-5 drafts), about.md, mdbook build green
- [x] 01-02-PLAN.md — Concept + vocabulary chapter (ch01): agentic AI vs reactive chatbot; four terms with prose forward pointers
- [x] 01-03-PLAN.md — OpenHands V1 architecture chapter (ch02, 5 files): step() loop, EventLog, DockerWorkspace, LiteLLM mapped to vocabulary

### Phase 2: Environment Setup & Verification
**Goal**: The full stack is installed, configured, and smoke-tested so the OpenHands run can begin without configuration surprises
**Depends on**: Phase 1
**Requirements**: SETUP-01, SETUP-02, SETUP-03, SETUP-04
**Success Criteria** (what must be TRUE):
  1. OpenHands is installed via `uv tool install openhands --python 3.12` and runs on macOS via the headless CLI (`openhands --version` works; no browser needed)
  2. OpenHands connects to the local Qwen endpoint via env vars (`LLM_MODEL=openai/qwen-local`, `LLM_BASE_URL=http://127.0.0.1:4000/v1`, dummy key, `--override-with-envs`) — confirmed by a headless tool-call ping where the agent calls a tool and an action+observation appear in the JSONL
  3. `dotnet --version` (10.0.x) runs in the agent's LocalWorkspace (the host toolchain) — confirmed by the headless agent running it; no custom Docker image needed
  4. The pre-run verification checklist passes: `openhands --version`; litellm proxy lists `qwen-local` and tool calling works through it; the headless agent runs a tool and runs `dotnet --version` — real outputs captured in an evidence file
  5. The 3부 setup chapter covers every step a reader must take, matching the verified configuration exactly
**Plans**: 3 plans

Plans:
- [x] 02-01-PLAN.md — Confirm/record base stack: uv-installed OpenHands CLI 1.16.0 + PATH + Python 3.12; litellm proxy preflight (qwen-local @ 127.0.0.1:4000)
- [x] 02-02-PLAN.md — End-to-end headless verification: env-var run of openai/qwen-local, echo tool-call ping (action+observation), agent runs dotnet --version (10.0.203); 02-VERIFICATION-EVIDENCE.md (measured ~15s/call, not 240s)
- [x] 02-03-PLAN.md — Wrote 3부 setup chapter (3 files) from verified evidence; SUMMARY 3부 drafts→real paths; mdbook build green (4부/5부 stay drafts)

> Note: re-planned 2026-05-27 against the verified headless-CLI + LocalWorkspace path. The original 5-plan Docker-Desktop / config.toml / custom-sandbox sketch is stale (archived). Docker is NOT on the critical path; dotnet is on the host; LLM config is via env vars + `--override-with-envs`.

### Phase 3: Capture the OpenHands Run
**Goal**: A real, complete OpenHands session that builds the F# FsLex/FsYacc calculator is captured to a log file
**Depends on**: Phase 2 (capture gate — environment must be verified first)
**Requirements**: RUN-01, RUN-02, RUN-03
**Success Criteria** (what must be TRUE):
  1. A full OpenHands session log exists on disk (commands + output, tee'd to a file) covering the complete calculator build
  2. The run is decomposed into at least 5 scoped tasks (scaffold → lexer → parser → evaluator → integration), not a single mega-prompt
  3. The log contains at least one real error-and-fix cycle (a failed build or test followed by OpenHands correcting itself) that can be narrated in the tutorial
  4. The calculator binary in the sandbox correctly evaluates `2+3*4` to `14`, proving operator precedence works
**Plans**: TBD

Plans:
- [ ] 03-01: Design the task decomposition (write the 5+ scoped task strings for the OpenHands run)
- [ ] 03-02: Execute the OpenHands run with tee logging; iterate if the run stalls or the model fails on a task
- [ ] 03-03: Verify the captured run meets criteria (error-and-fix present, `2+3*4 → 14` confirmed, log is complete)

### Phase 4: Worked-Example Chapter
**Goal**: The core tutorial chapter walks the reader through the real run step by step, with concept callouts, the error-and-fix narration, final source, and verification output
**Depends on**: Phase 3 (cannot be written until the real run is captured)
**Requirements**: WALK-01, WALK-02, WALK-03, VERIFY-01, VERIFY-02
**Success Criteria** (what must be TRUE):
  1. The calculator intro section explains what the calculator does (tokenize → parse → evaluate) without teaching F# from scratch
  2. The walkthrough uses real captured output at every key step (no invented or idealized transcripts)
  3. At least three concept-to-action callouts appear in the walkthrough, each linking a step in the run to a vocabulary term from the concept chapter
  4. The error-and-fix cycle is narrated explicitly, showing what OpenHands observed, what it decided, and how it corrected its code
  5. The chapter ends with the calculator correctly evaluating `2+3*4 → 14`, at least one parenthesized expression, and an honest performance note (~240s/call on local 35B hardware)
**Plans**: TBD

Plans:
- [ ] 04-01: Write the calculator intro section (what it does, F# at a glance, no language tutorial)
- [ ] 04-02: Write the step-by-step walkthrough from the captured log (concept callouts woven in)
- [ ] 04-03: Write the error-and-fix narration section from the real captured failure moment
- [ ] 04-04: Write the final F# source section (lexer .fsl, parser .fsy with %left precedence, evaluator)
- [ ] 04-05: Write the verification section (`2+3*4 → 14`, parentheses case, performance transparency)

### Phase 5: Troubleshooting, Reproducibility & Publish
**Goal**: The book is complete with troubleshooting and reproducibility chapters, builds cleanly, and is live on GitHub Pages
**Depends on**: Phase 4
**Requirements**: TROUBLE-01, REPRO-01, BOOK-03
**Success Criteria** (what must be TRUE):
  1. The troubleshooting chapter covers all five top failure modes: `host.docker.internal` vs `127.0.0.1`, `openai/` model prefix, timeout/retry storm, missing .NET in sandbox, and FsYacc `%left` precedence ordering
  2. The reproducibility appendix contains the exact task strings, Docker/run commands, config values, and expected outputs used in the real run — enough for a reader to reproduce it
  3. `mdbook build` succeeds on the complete book (no broken links, all chapters render, navigation works)
  4. A GitHub Actions workflow deploys the book to GitHub Pages and the live URL serves all chapters with correct CSS/JS (no 404s on assets)
**Plans**: TBD

Plans:
- [ ] 05-01: Write troubleshooting chapter (five failure modes, diagnostic steps)
- [ ] 05-02: Write reproducibility appendix (exact task strings, commands, config, expected outputs)
- [ ] 05-03: Final mdbook build check (all chapters, navigation, no broken links)
- [ ] 05-04: Set up GitHub Actions deploy workflow and verify live GitHub Pages site

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Scaffold & Concept Chapters | 3/3 | ✓ Complete | 2026-05-27 |
| 2. Environment Setup & Verification | 3/3 | ✓ Complete | 2026-05-27 |
| 3. Capture the OpenHands Run | 0/3 | Not started | - |
| 4. Worked-Example Chapter | 0/5 | Not started | - |
| 5. Troubleshooting, Reproducibility & Publish | 0/4 | Not started | - |
