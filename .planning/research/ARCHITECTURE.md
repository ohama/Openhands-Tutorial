# Architecture Research

**Domain:** Korean mdBook tutorial — Agentic AI via OpenHands building F# FsLex/FsYacc calculator on local Qwen LLM
**Researched:** 2026-05-27
**Confidence:** HIGH (OpenHands V1 SDK paper + official docs verified; mdBook from official docs; FsLexYacc from fsprojects repo)

---

## Part 1 — mdBook Tutorial Architecture (Information Architecture)

### 1.1 How mdBook Is Structured

An mdBook project has a fixed layout:

```
my-tutorial/
├── book.toml          # Build configuration (title, author, output options)
├── src/
│   ├── SUMMARY.md     # Single source-of-truth: chapter list, order, hierarchy
│   ├── introduction.md
│   ├── chapter-1/
│   │   ├── README.md  # Chapter landing page
│   │   └── section-1.md
│   └── chapter-2.md
└── book/              # Generated HTML output (git-ignored)
```

`SUMMARY.md` is the authoritative file — mdBook will not render a chapter that is not listed there. The file URL in the generated HTML mirrors the file path in `src/`, so directory structure is part of the URL contract.

### 1.2 SUMMARY.md Chapter Types

| Type | Syntax | Behavior |
|------|--------|----------|
| Prefix chapter | `[Intro](intro.md)` before numbered list | Unnumbered, flat, rendered first; for forewords/prefaces |
| Part title | `# Part Name` (level-1 heading) | Unclickable grouping label; separates sections visually |
| Numbered chapter | `- [Title](path.md)` | Auto-numbered, main content |
| Sub-chapter | indented `  - [Title](path.md)` | Nested under parent; shown in nav |
| Draft chapter | `- [Title]` (no path) | Rendered as disabled link; signals planned content |
| Separator | `---` | Horizontal rule in sidebar |
| Suffix chapter | unnumbered after numbered list | Appendices, glossary |

### 1.3 Recommended Tutorial Chapter/Section Breakdown

This structure is designed for a Korean-language tutorial teaching agentic AI via OpenHands building an F# calculator.

```
SUMMARY.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Prefix] 이 튜토리얼에 대하여 (about.md)
   목적, 독자, 선행 지식, 소요 시간

# 1부: 에이전틱 AI란 무엇인가

1. 에이전틱 AI 개요 (ch01-agentic-ai/overview.md)
   - 기존 LLM vs 에이전트의 차이
   - 에이전트 루프 (agent loop) 개념
   - 왜 에이전틱 AI가 중요한가

2. 핵심 개념 (ch01-agentic-ai/concepts.md)
   - 툴/함수 호출 (tool/function calling)
   - 액션과 관찰 (action & observation)
   - 메모리와 컨텍스트 (memory/context window)
   - Plan → Write → Test → Run 루프

# 2부: OpenHands 아키텍처

3. OpenHands 개요 (ch02-openhands/overview.md)
   - OpenHands란 무엇인가 (CodeActAgent 중심)
   - 주요 컴포넌트 한눈에 보기

4. 에이전트 루프 상세 (ch02-openhands/agent-loop.md)
   - 5단계 루프: drain → check → prepare → call LLM → dispatch
   - EventLog 역할
   - 컨텍스트 압축 (condensation)

5. 액션과 관찰 타입 (ch02-openhands/actions-observations.md)
   - CmdRunAction, FileEditAction, IPythonRunCellAction 등
   - Observation 구조 (stdout/stderr/exit code, diff)
   - MCP 툴 통합

6. 런타임과 샌드박스 (ch02-openhands/runtime.md)
   - LocalWorkspace vs DockerWorkspace
   - FastAPI 액션 실행 서버 (컨테이너 내부)
   - 지속 bash 세션 (tmux), IPython 커널

7. LLM 연동: LiteLLM (ch02-openhands/llm-integration.md)
   - LiteLLM이 100+ provider를 추상화하는 방법
   - OpenAI-compatible 엔드포인트 설정 방법
   - function calling vs text-based fallback

# 3부: 환경 설정

8. OpenHands 설치 (ch03-setup/install.md)
   - Docker 설치 및 OpenHands 이미지 실행
   - CLI 모드와 GUI 모드

9. 로컬 Qwen 서버 연결 (ch03-setup/local-llm.md)
   - MLX 서버 (http://127.0.0.1:8000/v1) 확인
   - OpenHands 설정: Custom Model, Base URL, API Key
   - 툴 콜링 동작 확인
   - 성능 주의: 35B 모델은 요청당 ~240초

10. 첫 실행 테스트 (ch03-setup/first-run.md)
    - 간단한 "hello" 태스크로 에이전트 루프 확인
    - 이벤트 로그 읽는 방법

# 4부: OpenHands로 F# 계산기 만들기

11. 예제 프로젝트 소개 (ch04-calculator/intro.md)
    - FsLex / FsYacc 개요 (토큰 → 파싱 → AST → 계산)
    - 목표: `2+3*4` → `14`

12. 태스크 계획 단계 (ch04-calculator/planning.md)
    - OpenHands에 태스크 지시하기
    - 실제 캡처: OpenHands가 계획을 세우는 과정 (ThinkTool / MessageAction)
    - Plan → subtask 분해 관찰

13. 코드 작성 단계 (ch04-calculator/writing.md)
    - FileEditAction으로 .fsl, .fsy, .fsproj 생성
    - 실제 캡처: 파일 생성 이벤트 스트림
    - 에이전트가 FileWriteAction을 선택하는 이유

14. 빌드와 테스트 단계 (ch04-calculator/testing.md)
    - CmdRunAction으로 dotnet build/run 실행
    - ObservationEvent: stdout/stderr/exit code 읽기
    - 에러 발생 → 자가 수정 사이클 (실제 캡처)

15. 완성된 계산기 (ch04-calculator/result.md)
    - 최종 F# 소스 코드 전체
    - `2+3*4 → 14` 실행 결과
    - 에이전트가 수행한 전체 이터레이션 요약

# 5부: 정리와 심화

16. 개념 되짚기 (ch05-wrap-up/concepts-review.md)
    - 튜토리얼 전체의 agentic AI 개념 매핑표
    - 독자가 배운 것 체크리스트

17. 다음 단계 (ch05-wrap-up/next-steps.md)
    - 다른 LLM, 다른 태스크에 OpenHands 적용하기
    - 읽을거리와 참고자료

[Suffix] 부록 A: 자주 묻는 질문 (appendix/faq.md)
[Suffix] 부록 B: 트러블슈팅 (appendix/troubleshooting.md)
```

### 1.4 Chapter Dependency Order (Build Order)

Chapters are written in this dependency order — a chapter should not be authored before its prerequisites are validated:

```
[1] about.md                    ← no dependencies; author first (defines scope)
[2] ch01 overview + concepts    ← foundational; must come before all other chapters
[3] ch02 OpenHands architecture ← depends on research being complete (this doc)
[4] ch03 setup chapters         ← depends on ch02 concepts; requires live environment test
[5] ch04 calculator chapters    ← depends on ch03 (real runs); requires captured output
[6] ch05 wrap-up                ← depends on all prior chapters; synthesizes them
[7] appendices                  ← can be written in parallel with ch04/ch05
```

Critical path: ch04 blocks on real OpenHands runs with the local Qwen server. The captured output (actual command/observation pairs) must be collected before ch04 content can be finalized. Draft skeleton chapters can be written first; fill with real captured output in a second pass.

**Write order recommendation:**
1. Scaffold all chapters as drafts (`.md` files with `# Title` and bullet outline)
2. Write ch01 (concepts) — pure writing, no environment dependency
3. Write ch02 (OpenHands architecture) — verified against this ARCHITECTURE.md
4. Write ch03 (setup) — requires live Docker + OpenHands + Qwen test
5. Run OpenHands on the F# calculator task; capture full output
6. Write ch04 with real captured output interpolated
7. Write ch05 (synthesizes ch01–ch04)
8. Write appendices from accumulated troubleshooting notes

### 1.5 mdBook Project File Structure

```
src/
├── SUMMARY.md
├── about.md
├── ch01-agentic-ai/
│   ├── overview.md
│   └── concepts.md
├── ch02-openhands/
│   ├── overview.md
│   ├── agent-loop.md
│   ├── actions-observations.md
│   ├── runtime.md
│   └── llm-integration.md
├── ch03-setup/
│   ├── install.md
│   ├── local-llm.md
│   └── first-run.md
├── ch04-calculator/
│   ├── intro.md
│   ├── planning.md
│   ├── writing.md
│   ├── testing.md
│   └── result.md
├── ch05-wrap-up/
│   ├── concepts-review.md
│   └── next-steps.md
└── appendix/
    ├── faq.md
    └── troubleshooting.md
```

---

## Part 2 — OpenHands Internal Architecture

### 2.1 Version Note

This section describes OpenHands V1 (SDK architecture), the current version as of 2026-05-27 (latest SDK release v1.23.1, 2026-05-25). V0 was deprecated April 2026. V1 refactored V0's monolithic sandbox-centric design into a modular four-package SDK.

Sources: arxiv.org/html/2511.03690v1 (SDK paper), dev.to deep dive, docs.openhands.dev/sdk/arch/events, github.com/OpenHands/software-agent-sdk.

### 2.2 System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────────────┐   │
│  │   CLI    │  │  Web UI  │  │  Remote Client (HTTP/WebSocket)  │   │
│  └────┬─────┘  └────┬─────┘  └──────────────┬───────────────────┘   │
└───────┼─────────────┼─────────────────────────┼─────────────────────┘
        │             │                         │
┌───────▼─────────────▼─────────────────────────▼─────────────────────┐
│                       openhands.sdk (Core)                           │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                     Conversation                              │    │
│  │  (runs the while-not-finished loop; owns ConversationState)  │    │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────────┐ │    │
│  │  │    Agent     │   │  EventLog    │   │  LLM (LiteLLM)   │ │    │
│  │  │  (stateless) │   │ (append-only)│   │  100+ providers  │ │    │
│  │  └──────┬───────┘   └──────────────┘   └────────┬─────────┘ │    │
│  │         │ step()                                 │           │    │
│  │         │ emits Actions                          │ call()    │    │
│  └──────────────────────────────────────────────────────────────┘    │
└───────────────────────────┬──────────────────────────────────────────┘
                            │ execute_action(action)
┌───────────────────────────▼──────────────────────────────────────────┐
│                    openhands.workspace                                │
│  ┌────────────────┐  ┌────────────────────┐  ┌────────────────────┐  │
│  │ LocalWorkspace │  │  DockerWorkspace   │  │ RemoteAPIWorkspace │  │
│  │ (host process) │  │ (container + HTTP) │  │ (network RPC)      │  │
│  └────────────────┘  └────────────────────┘  └────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.3 The Five-Phase Agent Loop

The Conversation object runs a `while not finished:` loop. Each iteration of the loop has exactly five phases:

```
Phase 1: DRAIN PENDING ACTIONS
  Execute any actions confirmed by user (WAITING_FOR_CONFIRMATION → execute)

Phase 2: HONOR USER BLOCKS
  If user rejected current message, stop or retry per policy

Phase 3: PREPARE LLM PROMPT
  - Filter EventLog for LLMConvertibleEvents
  - Group ActionEvents by llm_response_id (parallel tool calls)
  - Convert to LLM message format (system/user/assistant/tool roles)
  - Trigger condensation if event count > threshold (default: 80)

Phase 4: CALL LLM WITH RETRY
  - LiteLLM sends messages to configured model endpoint
  - Handles context-window overflow explicitly
  - Captures ThinkingBlock (Anthropic) / ReasoningItemModel (OpenAI)

Phase 5: CLASSIFY AND DISPATCH
  - Parse LLM response: tool call → ActionEvent, text → MessageEvent
  - Route to Workspace.execute_action() or emit message
  - Append resulting ObservationEvent to EventLog
  - Loop continues
```

Loop terminates when: `AgentFinishAction` emitted, budget (iteration/cost) exceeded, or unrecoverable error.

### 2.4 Event System (The Single Source of Truth)

All agent-environment interaction flows through an immutable, append-only EventLog. Events are never deleted; condensation marks ranges as "forgotten" without removing them, enabling deterministic replay.

**LLM-Visible Events** (sent to language model):

| Event Type | Source | Role in LLM Messages | Meaning |
|------------|--------|----------------------|---------|
| `SystemPromptEvent` | environment | system | Initial system context + tool schemas |
| `MessageEvent` | user/agent | user/assistant | Natural language turns |
| `ActionEvent` | agent | assistant | Tool invocation with reasoning |
| `ObservationEvent` | environment | tool | Tool execution result |
| `AgentErrorEvent` | environment | tool | Recoverable tool error (LLM can retry) |
| `CondensationSummaryEvent` | environment | user | Compressed history summary |

**Internal Events** (framework-only, not sent to LLM):

| Event Type | Purpose |
|------------|---------|
| `ConversationStateUpdateEvent` | Key-value state synchronization |
| `CondensationRequest` | Triggers context compression |
| `Condensation` | Result of history compression |
| `PauseEvent` | User-initiated pause |

Each event carries: `id`, `timestamp`, `source ∈ {user, agent, environment}`.

Note: `event.source` and LLM `role` are intentionally independent — a tool result has `source=environment` but `role=tool`.

### 2.5 Action Types (Complete, Verified)

**Execution actions:**

| Action | Produces Observation | Purpose |
|--------|---------------------|---------|
| `CmdRunAction(command, cwd, blocking)` | `CmdOutputObservation` (stdout+stderr+exit code) | Shell commands |
| `IPythonRunCellAction(code)` | `IPythonRunCellObservation` | Python in persistent kernel |
| `FileReadAction(path)` | `FileReadObservation` | Read file content |
| `FileWriteAction(path, content)` | `FileWriteObservation` | Write/overwrite file |
| `FileEditAction(path, str_replace=...)` | `FileEditObservation` (diff) | String-replacement edit |

**Interaction actions:**

| Action | Produces Observation | Purpose |
|--------|---------------------|---------|
| `BrowseURLAction(url)` | `BrowserOutputObservation` | Fetch and render webpage |
| `BrowseInteractiveAction(code)` | `BrowserOutputObservation` | Browser automation (Playwright) |
| `MessageAction(content, wait_for_response)` | (user response) | Chat with user |
| `AgentThinkAction(thought)` | (none) | Reasoning slot, no side effects |

**Meta actions:**

| Action | Produces Observation | Purpose |
|--------|---------------------|---------|
| `AgentFinishAction(thought, outputs)` | — | Terminates agent loop |
| `AgentDelegateAction(agent, inputs)` | `AgentDelegateObservation` | Sub-agent delegation |
| `RecallAction(query)` | `RecallObservation` | Microagent knowledge lookup |
| `CondensationAction(forgotten_ids, summary)` | — | Rewrites event history |
| `MCPAction` | `MCPObservation` | Model Context Protocol tools |

### 2.6 CodeActAgent Specifics

CodeActAgent is the flagship agent (currently the primary agent in V1). Its design principle: instead of 20 bespoke JSON tools, give the LLM bash, Python, and a browser DSL. Code is the universal action space.

Its system prompt encodes a four-phase methodology:
1. **Exploration** — file discovery: `grep`, `find`, `cat` via `CmdRunAction`
2. **Analysis** — hypothesis formation via `AgentThinkAction` (no side effects)
3. **Implementation** — minimal changes: prefer `FileEditAction(str_replace)` over full rewrites
4. **Verification** — run tests via `CmdRunAction`; confirm before `AgentFinishAction`

Self-correction is not a feature — it is a side effect of the observation loop. Every stderr, exit code, and error message is appended to the EventLog and visible to the LLM in the next prompt.

### 2.7 Runtime / Workspace Architecture

The agent code is identical regardless of workspace. The workspace is injected at construction time.

| Workspace | Isolation | Internal Mechanism | Use Case |
|-----------|-----------|-------------------|----------|
| `LocalWorkspace` | Host process + filesystem | Direct tool calls in-process | Development |
| `DockerWorkspace` | Container + internal server | FastAPI Action Execution Server inside container | Production / tutorial |
| `RemoteAPIWorkspace` | Network RPC | HTTP to remote agent server | Cloud/multi-tenant |

**DockerWorkspace internals** (what runs inside the container):
- FastAPI Action Execution Server at `POST /execute_action`
- Persistent bash session via tmux (preserves `cd` state across actions)
- Persistent IPython kernel (one `%pip install` survives session)
- Headless Chromium browser (Playwright)
- String-replacement file editor with undo

Actions transmit as JSON POST bodies; structured observations return as JSON responses.

### 2.8 LLM / LiteLLM Integration

LiteLLM wraps all LLM providers under a single Chat Completions API surface. OpenHands uses it to support 100+ providers without per-provider code.

**For the tutorial's local Qwen setup:**
- Protocol: OpenAI-compatible Chat Completions API at `http://127.0.0.1:8000/v1`
- OpenHands config (GUI or CLI):
  - **Custom Model**: `openai/<served-model-name>` — the `openai/` prefix tells LiteLLM to use the OpenAI client library
  - **Base URL**: `http://host.docker.internal:8000/v1` (from inside Docker; resolves to host's loopback)
  - **API Key**: any placeholder (e.g. `local-llm`) — MLX server doesn't validate it
- Tool/function calling: confirmed working (verified `finish_reason: "tool_calls"`)
- **Performance**: ~240s per tool-call request on the 35B model (local Apple Silicon GPU); OpenHands timeout must be raised accordingly

**LiteLLM fallback for non-function-calling models:** `NonNativeToolCallingMixin` converts tool schemas to text and parses calls via regex. Not needed for Qwen (tool calling confirmed).

**RouterLLM pattern:** Allows per-request model selection (e.g., route text to small model, vision to large model). Not relevant for the tutorial's single-model setup.

### 2.9 Data/Control Flow: User Task → LLM → File/Shell Actions

```
User types task description
         │
         ▼
Conversation.send_message(task)
         │
         ├── MessageEvent appended to EventLog
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   AGENT LOOP (while not finished)            │
│                                                              │
│  EventLog → filter LLMConvertible → group by response_id    │
│           → convert to messages → check condensation trigger │
│                     │                                        │
│                     ▼                                        │
│          LiteLLM.call(messages, tools=tool_schemas)          │
│            └─ HTTP POST to http://127.0.0.1:8000/v1         │
│                        (or docker host alias)                │
│                     │                                        │
│                     ▼                                        │
│         LLM response: tool_calls=[{name, arguments}]         │
│                     │                                        │
│                     ▼                                        │
│         ActionEvent appended (e.g. CmdRunAction)            │
│                     │                                        │
│                     ▼                                        │
│   Workspace.execute_action(action)                           │
│     └─ DockerWorkspace: POST /execute_action inside container│
│          └─ bash runs command in tmux session                │
│                     │                                        │
│                     ▼                                        │
│         ObservationEvent appended (stdout/stderr/exit code)  │
│                     │                                        │
│                     └────────── back to top of loop          │
│                                                              │
│  Until: AgentFinishAction || budget exceeded || error        │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
Final outputs surfaced to user / CLI / Web UI
```

**For the F# calculator task specifically:**

```
"Build an F# FsLex/FsYacc calculator that computes 2+3*4=14"
         │
         ▼ [Exploration phase]
CmdRunAction: find . -name "*.fsproj"  →  CmdOutputObservation (empty)
CmdRunAction: dotnet --version         →  CmdOutputObservation ("8.0.x")
         │
         ▼ [Planning phase]
AgentThinkAction: "Need to create new F# console project, add FsLexYacc NuGet..."
         │
         ▼ [Implementation phase]
CmdRunAction: dotnet new console -lang F# -n Calculator
FileWriteAction: Calculator/Lexer.fsl  (lexer rules)
FileWriteAction: Calculator/Parser.fsy (parser grammar)
FileEditAction:  Calculator/Calculator.fsproj (add NuGet refs)
         │
         ▼ [Verification phase]
CmdRunAction: cd Calculator && dotnet build
   → ObservationEvent: build error (missing token type)
AgentThinkAction: "Token type undefined; need to define in Parser.fsy header"
FileEditAction: Parser.fsy (fix header)
CmdRunAction: dotnet build  →  ObservationEvent: "Build succeeded"
CmdRunAction: echo "2+3*4" | dotnet run
   → ObservationEvent: "14"
         │
         ▼
AgentFinishAction("Calculator working. 2+3*4 = 14", outputs={"result": "14"})
```

### 2.10 Memory and Context Management

Context window management (condensation) is critical for long runs:
- Default trigger: 80 events in EventLog
- Strategy: Preserve first 4 events (system prompt, task, initial context) + last ~40 recent events; LLM-summarize the middle
- Result: `CondensationSummaryEvent` replaces summarized range in next LLM call
- Effect: EventLog retains full history; LLM only sees compressed version
- Reported: 2× API cost reduction on long sessions without quality loss

For the local Qwen setup at ~240s/call, a long F# calculator task may involve 10–20 iterations = 2,400–4,800 seconds of inference. This is the primary practical constraint the tutorial must communicate.

---

## Part 3 — Concept ↔ OpenHands Component Mapping

| Agentic AI Concept | OpenHands Component | Where It Appears in Tutorial |
|--------------------|---------------------|------------------------------|
| **Tool/function calling** | `ActionEvent` + tool schemas sent to LLM; `CmdRunAction`, `FileEditAction` etc. | ch02 actions-observations.md; ch04 writing.md |
| **Agent loop** | `Conversation.step()` in `while not finished:` | ch02 agent-loop.md; ch04 all phases |
| **Action** | Any `ActionEvent` subtype (CmdRunAction, FileWriteAction...) | ch02 actions-observations.md |
| **Observation** | `ObservationEvent` (stdout, diff, browser output) | ch02 actions-observations.md |
| **Memory / context** | `EventLog` (append-only); `CondensationSummaryEvent` (compression) | ch02 agent-loop.md; ch04 testing.md |
| **Plan → Write → Test → Run** | CodeActAgent's 4-phase methodology (Explore→Analyze→Implement→Verify) | ch04 all chapters |
| **Self-correction** | Error in `CmdOutputObservation` → LLM sees stderr → emits fix `FileEditAction` | ch04 testing.md (real captured error) |
| **Sandbox / isolation** | DockerWorkspace + FastAPI Action Execution Server | ch02 runtime.md; ch03 install.md |
| **LLM abstraction** | LiteLLM wrapping OpenAI-compatible endpoint | ch02 llm-integration.md; ch03 local-llm.md |
| **Sub-agent delegation** | `AgentDelegateAction` → `AgentDelegateObservation` | ch02 overview (mention only; not used in tutorial) |
| **Reasoning / thinking** | `AgentThinkAction` (no side effect; pure reasoning slot) | ch02 agent-loop.md; ch04 planning.md |
| **Budget / termination** | Iteration/cost ceiling in Conversation; `AgentFinishAction` | ch02 agent-loop.md |

---

## Part 4 — F# FsLex/FsYacc Calculator Architecture (What OpenHands Builds)

Included so tutorial authors accurately describe what OpenHands is producing.

### 4.1 Compilation Pipeline

```
Input string: "2 + 3 * 4"
    │
    ▼ [FsLex: Lexer.fsl → Lexer.fs]
Token stream: INT(2), PLUS, INT(3), STAR, INT(4), EOF
    │
    ▼ [FsYacc: Parser.fsy → Parser.fs]
AST: Plus(Int 2, Times(Int 3, Int 4))
    │
    ▼ [Eval function: recursive pattern match]
Result: 14
```

### 4.2 Files OpenHands Will Create

| File | Role | Generator |
|------|------|-----------|
| `Lexer.fsl` | Lexer specification (regex → token rules) | FsLex → `Lexer.fs` |
| `Parser.fsy` | Grammar rules (token patterns → AST nodes) | FsYacc → `Parser.fs` |
| `AST.fs` | Discriminated union for expression types | Handwritten (or generated) |
| `Program.fs` | Entry point: read input, lex, parse, eval, print | Handwritten |
| `Calculator.fsproj` | MSBuild project with FsLexYacc NuGet reference | Project file |

### 4.3 NuGet Dependencies

- `FsLexYacc` — code generator (build-time tool)
- `FsLexYacc.Runtime` — runtime support library

### 4.4 Build Command Sequence

```bash
dotnet new console -lang F# -n Calculator
cd Calculator
dotnet add package FsLexYacc
# ... create .fsl and .fsy files ...
dotnet build    # FsLex and FsYacc run as MSBuild tasks
echo "2+3*4" | dotnet run
```

---

## Anti-Patterns

### Anti-Pattern 1: Writing Tutorial Without Real Captured Output

**What people do:** Write chapter 4 from memory or hypothetically, inventing agent output.
**Why it's wrong:** Real OpenHands runs on slow local LLM produce distinctive behavior — long waits, unexpected errors, iterative self-correction — that makes the tutorial authentic and trustworthy. Invented output will look wrong to readers who run it themselves.
**Do this instead:** Run the actual task first; capture the full session; then write the chapter around the real output.

### Anti-Pattern 2: Starting mdBook chapters Without SUMMARY.md Plan

**What people do:** Create `.md` files and add them to SUMMARY.md later ad-hoc.
**Why it's wrong:** SUMMARY.md controls URLs and navigation. Renaming or reorganizing after publishing breaks links and GitHub Pages navigation.
**Do this instead:** Design the full chapter structure and finalize SUMMARY.md before writing content.

### Anti-Pattern 3: Explaining V0 Architecture

**What people do:** Describe OpenHands using older blog posts or V0 documentation.
**Why it's wrong:** V0 was deprecated April 2026. V1 is a clean four-package SDK with different component names and structure. Readers running current OpenHands will be confused.
**Do this instead:** Use V1 SDK documentation and the arxiv SDK paper (2511.03690) as primary sources.

### Anti-Pattern 4: Using host loopback inside Docker

**What people do:** Configure OpenHands with Base URL `http://127.0.0.1:8000/v1`.
**Why it's wrong:** Inside a Docker container, `127.0.0.1` refers to the container itself, not the host. The local MLX server won't be reachable.
**Do this instead:** Use `http://host.docker.internal:8000/v1` as the Base URL when running OpenHands in Docker targeting a host-side LLM server.

---

## Integration Points

### OpenHands ↔ Local Qwen MLX Server

| Parameter | Value for This Tutorial |
|-----------|------------------------|
| Protocol | OpenAI Chat Completions (v1/chat/completions) |
| Custom Model string | `openai/qwen36-35b` (or whatever the serving name is) |
| Base URL (from Docker) | `http://host.docker.internal:8000/v1` |
| API Key | Any placeholder (server doesn't validate) |
| Tool calling mode | Native function calling (confirmed working) |
| Expected latency | ~240s per request |
| Timeout setting | Must be raised to ≥300s in OpenHands config |

### mdBook ↔ GitHub Pages

| Component | Role |
|-----------|------|
| `book.toml` | Configures title, author, HTML renderer options |
| `mdbook build` | Produces `book/` HTML output |
| GitHub Actions | CI workflow: `mdbook build` → deploy `book/` to `gh-pages` branch |
| `pages` skill | Author has this configured; handles CI setup |

---

## Sources

- OpenHands SDK paper (arxiv.org/abs/2511.03690, arXiv Nov 2024): V1 architecture, four-package design, event system, LiteLLM integration, agent loop
- dev.to/truongpx396/openhands-deep-dive: Detailed agent loop phases, action types, workspace internals, condensation mechanics
- docs.openhands.dev/sdk/arch/events: Event type hierarchy, LLMConvertibleEvent classification, role/source independence
- docs.openhands.dev/openhands/usage/llms/local-llms: Qwen local model configuration, model string format, base URL
- github.com/OpenHands/software-agent-sdk (v1.23.1, 2026-05-25): Four packages, LocalConversation vs RemoteConversation, workspace abstraction
- rust-lang.github.io/mdBook/format/summary.html: SUMMARY.md format spec, chapter types, nesting rules
- rust-lang.github.io/mdBook/guide/creating.html: Project layout, build process
- github.com/fsprojects/FsLexYacc: FsLex/FsYacc toolchain, NuGet packages, .fsl/.fsy file types

---

*Architecture research for: Korean mdBook tutorial — Agentic AI via OpenHands building F# FsLex/FsYacc calculator*
*Researched: 2026-05-27*
