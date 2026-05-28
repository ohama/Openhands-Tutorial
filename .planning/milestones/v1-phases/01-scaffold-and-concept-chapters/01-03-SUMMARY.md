---
phase: 01-scaffold-and-concept-chapters
plan: "03"
subsystem: content-architecture-chapter
tags: [openhands, korean-prose, ch02, agent-loop, eventlog, docker-workspace, litellm, mdbook]

dependency-graph:
  requires:
    - "01-01 (mdBook scaffold, ch02 stub files)"
    - "01-RESEARCH (ARCHITECTURE.md Part 2, 01-RESEARCH.md V1 facts)"
  provides:
    - "Full Korean prose for all five src/ch02-openhands/*.md files"
    - "V1 concept-to-component mapping (step()=agent loop, EventLog=memory, DockerWorkspace=sandbox, LiteLLM=LLM abstraction)"
    - "mdbook build exits 0 with 2부 fully rendered"
  affects:
    - "01-02 (concepts.md must link back to agent-loop.md; links verified real)"
    - "Phase 4 (ch04 chapters forward-reference these as conceptual foundation)"

tech-stack:
  added: []
  patterns:
    - "Korean prose + English component names convention established for ch02"
    - "ASCII art code blocks for architecture diagrams (no preprocessor deps)"
    - "Prose-only forward references to Phase 3-5 draft chapters (no Markdown links)"

file-tracking:
  created: []
  modified:
    - src/ch02-openhands/overview.md
    - src/ch02-openhands/agent-loop.md
    - src/ch02-openhands/actions-observations.md
    - src/ch02-openhands/runtime.md
    - src/ch02-openhands/llm-integration.md

decisions:
  - id: "03-01"
    choice: "Prose-only forward references to 3부+ chapters"
    rationale: "3부+ chapters are draft entries in SUMMARY.md with no real files; Markdown links would produce dead links in deployed book"
  - id: "03-02"
    choice: "ASCII art for all architecture diagrams"
    rationale: "mdBook 0.5.3 has no mermaid preprocessor; ASCII code blocks build with zero dependencies per research"

metrics:
  duration: "~4 minutes"
  completed: "2026-05-27"
---

# Phase 1 Plan 03: OpenHands Architecture Chapter Summary

**One-liner:** Five Korean prose ch02 chapters mapping V1 step() loop, EventLog, DockerWorkspace, and LiteLLM to the agentic AI vocabulary terms from 1부.

## What Was Built

Three tasks wrote five full Korean prose files under `src/ch02-openhands/`, overwriting the H1-only stubs created in plan 01-01. All component names stay in English; all prose is Korean. `mdbook build` exits 0 with all five chapters rendered to HTML.

### Task 1: overview.md and agent-loop.md (commit bf00d61)

**overview.md** introduces OpenHands V1 as the four-package SDK (openhands-sdk, -tools, -workspace, -agent-server), distinguishes it from V0 (deprecated April 2026), and presents the five core components (Conversation, Agent, EventLog, LiteLLM, Workspace) with their 1부 concept mappings in a table. Sibling chapter links included.

**agent-loop.md** explains the five-phase `Conversation.step()` loop with an ASCII code block naming all phases (DRAIN, HONOR USER BLOCKS, PREPARE, CALL LLM, CLASSIFY & DISPATCH). Includes relative link to `../ch01-agentic-ai/concepts.md`. Documents EventLog append-only semantics, condensation at 80-event threshold, and contains the explicit mapping sentence: "이 step() 루프가 곧 1부에서 말한 agent loop입니다."

**Files:** 52 lines (overview.md), 65 lines (agent-loop.md)

### Task 2: actions-observations.md and runtime.md (commit a5ab165)

**actions-observations.md** documents the ActionEvent → Workspace → ObservationEvent → EventLog cycle with an ASCII diagram. Includes a six-row action-type table with corresponding ObservationEvent types. Explains self-correction as a side effect of the observation loop (stderr/exit code in CmdOutputObservation re-enters EventLog → LLM sees it → emits fix). Maps ActionEvent + tool schema to 'tool calling', ObservationEvent to 'observation'.

**runtime.md** explains the Workspace abstraction and injection-at-construction pattern. Three-row table for LocalWorkspace/DockerWorkspace/RemoteAPIWorkspace. ASCII diagram of DockerWorkspace internals: FastAPI Action Execution Server, tmux-based persistent bash session, persistent IPython kernel. Maps DockerWorkspace + Action Execution Server to 'sandbox / isolation'.

**Files:** 67 lines (actions-observations.md), 55 lines (runtime.md)

### Task 3: llm-integration.md and mdbook build (commit 3d77381)

**llm-integration.md** explains LiteLLM's role as a 100+ provider abstraction. Documents the three config values for this tutorial's local Qwen: `openai/<model-id>` prefix (tells LiteLLM to use OpenAI client), `http://host.docker.internal:8000/v1` Base URL (with explicit warning that 127.0.0.1 does not work from inside Docker), and placeholder API key. Mentions native function calling confirmation and NonNativeToolCallingMixin in one line. Forward reference to 3부 is prose-only (no Markdown link).

`mdbook build` exits 0 after all five files written. All five ch02 HTML pages rendered. No forbidden links to Phase 3-5 draft chapter files found in any ch02 file.

**Files:** 48 lines (llm-integration.md)

## Concept-to-Component Mappings Established

| Agentic AI Concept (1부) | OpenHands V1 Component | File |
|--------------------------|------------------------|------|
| agent loop | `Conversation.step()` `while not finished:` loop | agent-loop.md |
| memory / context | EventLog (append-only) + condensation | agent-loop.md |
| tool calling | ActionEvent + tool schemas sent to LLM | actions-observations.md |
| observation | ObservationEvent (stdout/stderr/exit code, diff) | actions-observations.md |
| sandbox / isolation | DockerWorkspace + FastAPI Action Execution Server | runtime.md |
| LLM abstraction | LiteLLM + `openai/` prefix routing | llm-integration.md |

## Decisions Made

| ID | Decision | Rationale |
|----|----------|-----------|
| 03-01 | Prose-only forward references to 3부+ chapters | Draft entries have no files; Markdown links would produce 404s in deployed book |
| 03-02 | ASCII art for all architecture diagrams | Zero preprocessor dependencies; mdBook 0.5.3 builds cleanly |

## Deviations from Plan

None — plan executed exactly as written. All five files meet or exceed minimum line counts; all required terms present; mdbook build exits 0; no V0 terms used.

## Verification Results

- All five files: correct H1, Korean prose, English component names
- overview.md: four-package SDK listed, V1 vs V0 distinction, five-component table
- agent-loop.md: step() mentioned, all five phases named, `../ch01-agentic-ai/concepts.md` linked, condensation documented, explicit mapping sentence present
- actions-observations.md: ActionEvent and ObservationEvent, self-correction explanation, concepts.md linked
- runtime.md: DockerWorkspace, Action Execution Server, tmux, concepts.md linked
- llm-integration.md: LiteLLM, openai/ prefix, host.docker.internal
- No V0 terms (docker_sandbox): confirmed by grep
- No Markdown links to Phase 3-5 draft chapters: confirmed by grep
- mdbook build: exit 0, all five ch02 HTML files in book/ch02-openhands/

## Next Phase Readiness

This plan delivers CONCEPT-03. The 2부 architecture chapter is complete and serves as the conceptual foundation for:
- 3부 setup chapters (readers can now understand what they are configuring)
- 4부 calculator chapters (readers can recognize EventLog, ActionEvent, ObservationEvent in real captures)

Blocker from STATE.md still applies: exact model-id string and `agent_settings.json` key names must be confirmed against running OpenHands 1.7 before Phase 2 (3부 setup content).
