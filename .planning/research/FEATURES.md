# Feature Research

**Domain:** Agentic AI tutorial (mdBook) — Korean-language, hands-on, OpenHands + local Qwen LLM + F# FsLex/FsYacc calculator worked example
**Researched:** 2026-05-27
**Confidence:** HIGH

---

## Reframing: "Features" = Tutorial Sections/Chapters

For a tutorial/content project, "features" are the **chapters and sections** that compose the deliverable. This file maps each proposed section to its category (table stakes, differentiator, anti-feature), its complexity, and its dependencies.

---

## Table Stakes

Sections a credible agentic-AI tutorial MUST have. Missing any of these = the tutorial feels incomplete or unpublishable.

| Section | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **개념 입문: 에이전틱 AI란?** (Agentic AI Concept Intro) | Readers approaching a tutorial on agentic AI need a conceptual anchor before touching tools. Standard for every domain tutorial (freecodecamp, IBM, Microsoft all open this way). | LOW | Should contrast agentic AI vs. reactive/chatbot AI. Cover: autonomy, goal-directed behavior, the agent loop (perceive → plan → act → evaluate → iterate). Keep short; readers want to get to the example quickly. |
| **핵심 개념 설명** (Key Concepts Section) | Tool/function calling, the agent loop mechanics, plan→test→run lifecycle, memory/context — these are the vocabulary the rest of the tutorial references. Must be defined before the worked example references them. | MEDIUM | Four sub-concepts minimum: (1) tool calling, (2) the agent loop, (3) planning & task decomposition, (4) memory/context window. Readers need the vocabulary to follow the OpenHands run. |
| **환경 설정** (Environment / Setup) | No hands-on tutorial can skip setup. Readers must be able to reproduce the run. OpenHands via Docker + local Qwen endpoint configuration is non-trivial; a step-by-step walkthrough is mandatory. | HIGH | Covers: Docker install, OpenHands container launch, connecting to local OpenAI-compatible endpoint (`http://host.docker.internal:8000/v1`), model prefix format (`openai/<model-name>`), API key placeholder, timeout settings. Must include verification step (health check). |
| **예제 소개: F# FsLex/FsYacc 계산기** (Worked Example Introduction) | Readers must understand what OpenHands will build before they watch it build it. Without this framing, the OpenHands run transcript is opaque. | LOW | Briefly explain: what FsLex/FsYacc do (tokenize → parse → evaluate), what the target calculator does (`2+3*4 → 14`, operator precedence), why it's a good agentic example (multi-file, tool use required, compilable and testable). No need to teach F# deeply. |
| **OpenHands 실행 워크스루** (OpenHands Run Walkthrough) | This is the tutorial's core chapter — the actual agentic run. Every agentic AI tutorial needs a concrete, step-by-step demonstration of the agent doing real work. | HIGH | Must cover the full plan→write→test→run loop. Must use real captured output (not invented). Show iterations, errors-and-fixes, tool calls. Structure as annotated transcript with concept callouts. |
| **결과 확인** (Results / Verification) | Readers need to see success — the calculator actually running and producing `2+3*4 → 14`. Without this, the tutorial has no payoff moment. | LOW | Show the final compiled F# binary executing with sample inputs. Include the final source files. Verify correctness. |
| **트러블슈팅** (Troubleshooting Section) | Expected in any setup/run tutorial. Local LLM inference adds unique failure modes (timeout, tool-call failures, Docker networking). | MEDIUM | Cover: timeout configuration for slow local inference, Docker networking (`host.docker.internal` vs `localhost`), model prefix format errors, tool-calling failures with non-compliant models. |

---

## Differentiators

Sections that distinguish THIS tutorial from generic agentic AI guides. Not universally expected, but they are what makes the tutorial excellent rather than merely competent.

| Section | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **실제 캡처된 OpenHands 실행 결과** (Real Captured Run Output) | Most agentic AI tutorials use invented or simplified output. Real captured transcripts — including actual errors, retries, and Qwen LLM latency — make the tutorial trustworthy and reproducible. This is the tutorial's strongest differentiator. | HIGH | Requires performing real OpenHands runs beforehand. Capture raw event stream, edit for length, annotate with concept markers. The errors-and-fixes are pedagogically critical: they show how the agent loop actually handles failure. |
| **개념 ↔ 행동 매핑 사이드바** (Concept-to-Action Mapping) | At each significant OpenHands action in the transcript, a sidebar or callout that says "이것이 tool calling입니다" / "이것이 plan→act→observe 루프입니다." Forces the reader to see the agentic concepts in action, not just read abstract definitions. No other open agentic-AI tutorial does this systematically. | MEDIUM | Each major agent action gets a "개념 연결" box. Tie: bash execution → tool use; iteration after test failure → agent loop; task decomposition into steps → planning; context carried across steps → memory. |
| **로컬 LLM 실제 성능 투명성** (Local LLM Performance Transparency) | The tutorial is honest about the 35B model being slow (~240s per tool call). Setting this expectation — and explaining *why* (local inference, token budget, reasoning overhead) — is rare in tutorials and builds trust. | LOW | One short section on performance expectations. Explain: why local inference is slower, what timeouts to set, how to tell if OpenHands is stuck vs. just slow. Helps readers not abandon a working setup. |
| **CodeAct 아키텍처 설명** (OpenHands CodeAct Architecture Sidebar) | Most tutorials treat the agent as a black box. Briefly explaining OpenHands' CodeAct approach (bash/Python as the tool interface, event stream as memory, conversation-owned state) maps to the conceptual framework and elevates reader understanding. | MEDIUM | 1-page sidebar or dedicated section. Cover: Agent as stateless function over history, event stream as append-only log, CodeAct's use of bash/Python instead of rigid tool schemas. Reference the ICLR 2025 paper if appropriate. |
| **재현 가능성 가이드** (Reproducibility Guide / "Follow Along" Path) | A checklist or step-by-step guide for readers who want to reproduce the exact run on their own hardware. Includes the exact OpenHands task prompt used, the model config, and the expected outputs. | MEDIUM | Appendix or standalone chapter. Include: the exact task string sent to OpenHands, the Docker run command, the model identifier, expected wall-clock time, how to verify the result. Allows readers to confirm they get the same answer. |
| **오류와 수정 사이클 해설** (Error-and-Fix Cycle Narration) | Within the run walkthrough, explicitly narrating the moments where OpenHands encounters a compile error or test failure and then self-corrects. Most tutorials only show the happy path. Showing failure-then-recovery is the clearest demonstration of autonomous error handling — the most important differentiating property of agentic systems. | MEDIUM | Annotate 2-3 key recovery moments in the transcript. For each: (1) what failed, (2) what the agent observed, (3) what it did next, (4) which agentic concept this exemplifies (self-correction, feedback loop, etc.). |

---

## Anti-Features

Sections or design choices to explicitly NOT include. These are common in tutorials of this type but make the result worse.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **F# 언어 입문 챕터** (Teaching F# from scratch) | F# and FsLex/FsYacc are the *subject* OpenHands builds, not what the reader is learning. Teaching F# syntax would double the tutorial length and dilute the agentic AI focus. Audience is assumed to be programming-literate. | Provide a 1-paragraph "F# 계산기 소개" that explains what the calculator does (tokenize, parse, evaluate arithmetic), with a pointer to F# resources for those curious — then move on. |
| **OpenHands 기능 참조 문서** (Exhaustive OpenHands Feature Reference) | The tutorial teaches agentic AI concepts *through* OpenHands, not OpenHands as a product. A feature matrix of every OpenHands capability (web browsing, multi-agent, GUI, etc.) would overwhelm and distract. | Cover only the features OpenHands uses in the worked example: bash execution, file editing, the iterative coding loop. Link to official OpenHands docs for everything else. |
| **조작된 또는 이상적화된 트랜스크립트** (Fabricated or Idealized Transcripts) | A tutorial that shows a perfectly clean first-pass agent run is dishonest and pedagogically inferior. Readers who try to reproduce it will be confused when their own run has errors. | Use real captured output. If a full transcript is too long, edit for length but keep representative errors and retries. Label edited sections clearly. |
| **클라우드 API 마케팅 또는 비교** (Cloud/vendor API promotion) | The tutorial explicitly uses a local Qwen server. Recommending OpenAI/Anthropic/Gemini APIs or comparing them to the local setup adds length, creates confusion, and undermines the "run it yourself" premise. | Stay focused on the local endpoint. One note in setup: "OpenHands also supports cloud APIs, but this tutorial uses a local model." No more. |
| **에이전트를 처음부터 구현하기** (Re-implementing an agent from scratch) | Building a custom agent loop in F# or Python teaches programming, not agentic AI in practice. It's a different tutorial. OpenHands is the agent being demonstrated. | Use OpenHands as-is. The tutorial teaches agentic AI by observing a real, working agent — not by rewriting one. |
| **완벽한 설치 경로 보장** (Guaranteeing a single install path) | Docker versions, macOS/Linux differences, Apple Silicon networking quirks — there is no single perfect setup path. Claiming one exists will frustrate readers whose environment differs slightly. | Document the tested path (Docker + macOS + Apple Silicon MLX), call out known variation points, and give readers enough context to adapt. |
| **동기 없는 이론 섹션** (Unmotivated theory sections) | Long conceptual sections before any code or demo lose readers. (This is one of the most widely cited technical tutorial anti-patterns: see Divio documentation framework "too much explanation, not enough how-to.") | Motivate every concept section by pointing forward: "이 개념은 [section X]에서 OpenHands가 [Y]를 할 때 직접 볼 수 있습니다." Each definition should have a "where you'll see this in the run" pointer. |
| **완료되지 않은 예시 또는 결과 없는 튜토리얼** (Tutorial without a verifiable end result) | Tutorials that end with "and then you'd see results" (without actually showing them) feel unfinished and untrustworthy. | Show the final compiled calculator running: exact command, exact output (`2+3*4 = 14`), and the full final source files. The payoff must be concrete. |

---

## Feature Dependencies

Reading order and authoring dependencies between sections:

```
[개념 입문: 에이전틱 AI란?]
    └──must precede──> [핵심 개념 설명]
                           └──must precede──> [OpenHands 실행 워크스루]
                                                  └──must precede──> [결과 확인]

[환경 설정]
    └──must precede──> [OpenHands 실행 워크스루]

[예제 소개: F# FsLex/FsYacc 계산기]
    └──must precede──> [OpenHands 실행 워크스루]

[실제 캡처된 OpenHands 실행 결과] ──produces──> [OpenHands 실행 워크스루]
    └──must precede authoring of──> [오류와 수정 사이클 해설]
    └──must precede authoring of──> [재현 가능성 가이드]

[개념 ↔ 행동 매핑 사이드바] ──woven into──> [OpenHands 실행 워크스루]
    └──requires──> [핵심 개념 설명] (concepts must be defined before they're referenced)

[CodeAct 아키텍처 설명]
    └──enhances──> [OpenHands 실행 워크스루] (placed before or as sidebar during walkthrough)

[로컬 LLM 실제 성능 투명성]
    └──belongs in──> [환경 설정] or just before [OpenHands 실행 워크스루]

[트러블슈팅]
    └──placed after──> [환경 설정] (setup errors) and after [결과 확인] (run errors)
```

### Dependency Notes

- **Concept intro must precede everything:** Readers who don't know what tool calling is cannot follow the run transcript annotations.
- **Real run must be captured before the walkthrough chapter can be written:** The walkthrough chapter is authored *from* the real run, not before it. This is the highest authoring dependency in the project.
- **Setup must precede the run:** Readers cannot follow along without a working OpenHands + local Qwen environment. The setup section must be complete and verified before the run walkthrough is credible.
- **F# calculator intro is a framing chapter, not a prerequisite for concepts:** It can appear before or after the concept intro, but must precede the run walkthrough.
- **Concept-to-action mapping is woven into the walkthrough, not a standalone chapter:** It is implemented as callout boxes or sidebars within the run transcript, not a separate section.

---

## MVP Definition (Chapter Ordering for v1 Publication)

### Publish With (v1 — minimum complete tutorial)

The minimum chapter set that makes the tutorial coherent and publishable:

- [ ] **개념 입문: 에이전틱 AI란?** — Without this, readers have no context.
- [ ] **핵심 개념 설명** (tool calling, agent loop, planning, memory) — Vocabulary needed for the walkthrough.
- [ ] **환경 설정** — Readers cannot follow along without a working setup.
- [ ] **예제 소개: F# FsLex/FsYacc 계산기** — Framing for what OpenHands will build.
- [ ] **OpenHands 실행 워크스루** (with inline concept-to-action callouts) — The core chapter; tutorial purpose.
- [ ] **결과 확인** — Payoff: `2+3*4 → 14`, final source files.
- [ ] **트러블슈팅** — Required for hands-on tutorial credibility.

### Add After Initial Publication (v1.x)

- [ ] **CodeAct 아키텍처 설명** — Deepens understanding but not required for the happy path. Add when tutorial has been validated with readers.
- [ ] **재현 가능성 가이드 / 부록** — Checklist appendix for readers who want to reproduce exactly. Useful once the run is stabilized.
- [ ] **로컬 LLM 실제 성능 투명성** (as a standalone section, if not already woven into setup) — Can be a blog-post-style addendum.

### Future Consideration (v2+)

- [ ] **다른 언어/프로젝트로 확장** (extending the example to another language) — Only if the tutorial gains an audience that wants more examples.
- [ ] **다중 에이전트 패턴** (multi-agent patterns with OpenHands) — Once v1 is established; requires significantly more research and captures.

---

## Feature Prioritization Matrix

| Section | Reader Value | Authoring Cost | Priority |
|---------|-------------|----------------|----------|
| 개념 입문 + 핵심 개념 설명 | HIGH | LOW | P1 |
| 환경 설정 | HIGH | MEDIUM | P1 |
| 예제 소개 (F# 계산기) | HIGH | LOW | P1 |
| OpenHands 실행 워크스루 | HIGH | HIGH | P1 |
| 결과 확인 | HIGH | LOW | P1 |
| 트러블슈팅 | HIGH | MEDIUM | P1 |
| 개념 ↔ 행동 매핑 callouts | HIGH | MEDIUM | P1 (woven in) |
| 오류와 수정 사이클 해설 | HIGH | MEDIUM | P1 (woven in) |
| 로컬 LLM 성능 투명성 | MEDIUM | LOW | P2 |
| CodeAct 아키텍처 설명 | MEDIUM | MEDIUM | P2 |
| 재현 가능성 가이드 / 부록 | MEDIUM | MEDIUM | P2 |

**Priority key:**
- P1: Must have for v1 publication
- P2: Should have, add after v1 core is written
- P3: Nice to have, future consideration

---

## What Makes Agentic AI Tutorials Good vs. Mediocre

Based on analysis of existing tutorials (freecodecamp Agentic AI Handbook, agenticloops-ai/agentic-ai-engineering, Microsoft AI Agents for Beginners, IBM 2026 Guide, OpenHands deep-dive on DEV.to, Temporal agentic loop docs):

### What good tutorials do

1. **Define the agent loop concretely before using it.** Every strong tutorial (freecodecamp, agenticloops) opens by defining the perceive→plan→act→evaluate cycle, then shows it in action. Abstract-before-concrete is the correct order here because "agent" is a fuzzy term readers may confuse with simple chatbots.

2. **Show a complete run, including failures.** The agenticloops-ai curriculum explicitly includes "self-critique and iterative refinement" as its own module. The freecodecamp handbook's hands-on section goes end-to-end. Tutorials that only show a clean success run fail to convey *why* agents are more powerful than pipelines.

3. **Connect every concrete action to an abstract concept.** The best tutorials (Temporal's agentic loop docs, the OpenHands DEV.to deep dive) annotate each step of the transcript with the agentic pattern it exemplifies. This is the difference between a demo and a tutorial.

4. **Be honest about setup complexity and performance.** OpenHands + local LLM has real friction (Docker, model prefix format, slow inference). Tutorials that paper over this lose readers at setup. Transparency about the `openai/<model>` prefix requirement, `host.docker.internal` networking, and ~240s inference times is not a weakness — it's what lets readers debug their own setups.

5. **Have a concrete, verifiable payoff.** A calculator that produces `2+3*4 = 14` is a perfect tutorial payoff: simple to verify, impossible to fake, and meaningful (it demonstrates operator precedence, not just addition).

6. **Keep concept sections short and forward-referencing.** The Divio documentation framework distinguishes tutorials (learning by doing) from explanations (understanding). A tutorial's concept sections should be brief and always point forward: "you will see this concept in action in the next section."

### What mediocre tutorials do

1. **Show only the happy path** — readers don't learn how the agent handles real errors.
2. **Invent output** — readers cannot verify or reproduce, and the transcript often looks suspiciously perfect.
3. **Treat the agent as a black box** — readers finish with a "wow" but no understanding of *why* the agent behaved as it did.
4. **Teach the tool before the concept** — readers can follow the steps but don't generalize to other tools or agents.
5. **Scope-creep into adjacent topics** (teaching F#, reviewing all OpenHands features) — dilutes the core learning objective.
6. **No explicit "what to do when things go wrong" section** — tutorial readers almost always hit problems; a troubleshooting section is not optional.

---

## Competitor / Comparable Tutorial Analysis

| Tutorial | What It Gets Right | What This Tutorial Improves |
|----------|-------------------|----------------------------|
| freecodecamp Agentic AI Handbook (2025) | Good conceptual coverage, 9-chapter structure, hands-on Python section | Uses LangChain not a real agent system; no error/retry demonstration; no local LLM |
| agenticloops-ai/agentic-ai-engineering | Progressive curriculum, self-critique module, testing module | Builds from scratch rather than using a real production agent; English only |
| Microsoft AI Agents for Beginners | 12-lesson structure, multiple languages, accessible | Focuses on design principles over real runs; no local LLM; invented examples |
| OpenHands DEV.to deep dive (April 2026) | Best architectural explanation of OpenHands V1 | Architecture-focused, not tutorial-shaped; no worked example; English only |
| Temporal agentic loop docs | Excellent step-by-step agent loop documentation | Platform-specific; not tutorial-shaped; no complete worked example |

This tutorial's unique combination: **real captured run** + **local model** + **complete project** (multi-file F# calculator) + **Korean language** + **concept-to-action mapping** + **showing errors-and-fixes** = no direct equivalent exists.

---

## Sources

- [GitHub: agenticloops-ai/agentic-ai-engineering](https://github.com/agenticloops-ai/agentic-ai-engineering) — curriculum structure for agentic AI learning
- [OpenHands Getting Started Docs](https://docs.openhands.dev/sdk/getting-started) — setup requirements and core concepts
- [OpenHands Local LLMs Docs](https://docs.openhands.dev/openhands/usage/llms/local-llms) — configuration for local OpenAI-compatible endpoints
- [OpenHands Deep Dive — DEV Community (April 2026)](https://dev.to/truongpx396/openhands-deep-dive-build-your-own-guide-1al0) — CodeAct architecture, agent loop phases, self-correction patterns
- [freecodecamp: The Agentic AI Handbook](https://www.freecodecamp.org/news/the-agentic-ai-handbook/) — chapter structure, perceive→plan→act→evaluate loop, memory/tool calling coverage
- [you.com: The Agent Loop](https://you.com/resources/the-agent-loop-how-ai-agents-actually-work-and-how-to-build-one) — canonical loop definition, common mistakes, error handling
- [InfoWorld: Best practices for building agentic systems](https://www.infoworld.com/article/4154570/best-practices-for-building-agentic-systems.html) — tool selection, observability, human-in-loop
- [Microsoft AI Agents for Beginners — Agentic Design Patterns](https://microsoft.github.io/ai-agents-for-beginners/03-agentic-design-patterns/) — course structure reference
- [IBM 2026 Guide to AI Agents](https://www.ibm.com/think/ai-agents) — educational explainer patterns
- [Temporal: Basic Agentic Loop with Tool Calling](https://docs.temporal.io/ai-cookbook/agentic-loop-tool-call-openai-python) — annotated agent loop documentation style
- [FsLexYacc Official Docs](https://fsprojects.github.io/FsLexYacc/) — F# lexer/parser tooling for the worked example
- [thanos.codes: Using FSLexYacc](https://thanos.codes/blog/using-fslexyacc-the-fsharp-lexer-and-parser/) — calculator example reference

---
*Feature research for: Agentic AI tutorial (Korean mdBook, OpenHands + local Qwen LLM + F# FsLex/FsYacc calculator)*
*Researched: 2026-05-27*
