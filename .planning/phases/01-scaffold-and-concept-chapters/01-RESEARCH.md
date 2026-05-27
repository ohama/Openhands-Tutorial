# Phase 1: Scaffold & Concept Chapters — Research

**Researched:** 2026-05-27
**Domain:** mdBook initialization + Korean technical prose authoring + OpenHands V1 concept mapping
**Confidence:** HIGH

---

## Summary

Phase 1 is pure documentation work: no OpenHands runs, no Docker, no F#. The deliverables are (a) a working mdBook scaffold that builds cleanly with `mdbook build`, and (b) three written chapters covering agentic AI concepts, core vocabulary, and OpenHands V1 architecture. All content for this phase is run-independent and can be written immediately.

The existing research in STACK.md, ARCHITECTURE.md, and SUMMARY.md already covers the full mdBook chapter structure and the OpenHands V1 architecture in authoritative detail. This document adds the precise, Phase-1-scoped findings the planner needs: exact `book.toml` fields, the safe strategy for a partial `SUMMARY.md`, and the minimum correct set of OpenHands facts for the architecture chapter.

**Primary recommendation:** Initialize the full SUMMARY.md with ALL planned chapters as draft entries (no file paths) for chapters not written in Phase 1; only Phase-1 chapters get real file paths. `mdbook build` will treat drafts as disabled TOC links — no broken references, no missing-file errors. This is the official mdBook mechanism for in-progress books.

---

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| mdBook | 0.5.3 | Static site generator; turns Markdown into navigable HTML book | Project-standard; author has `mdbook` skill configured; zero JS framework overhead |
| `mdbook build` | (built-in) | Produce `book/` output directory for deploy | Standard command; run locally and in CI |
| `mdbook serve` | (built-in) | Local dev server with live reload at `http://localhost:3000` | Fast authoring feedback loop |

### Supporting

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| Homebrew (`brew install mdbook`) | — | Install mdBook without needing a Rust toolchain | Local authoring on macOS |

**No additional preprocessors in Phase 1.** Plain mdBook (built-in `links` and `index` preprocessors only) is correct for this phase. Mermaid, admonish, and other third-party preprocessors each require a separate Rust binary and a `[preprocessor]` entry in `book.toml`. They add complexity with no benefit in Phase 1. If diagrams are needed later (e.g., the agent loop), use a static diagram image (`assets/agent-loop.png`) or a code block with ASCII art — both build cleanly with zero deps.

---

## Architecture Patterns

### Recommended Book Directory Structure

```
OpenHandsTests/           ← git repo root
├── book.toml             ← build config (must be at root or specify src)
├── src/
│   ├── SUMMARY.md        ← single source of truth for chapter order
│   ├── about.md          ← prefix chapter (unnumbered intro)
│   ├── ch01-agentic-ai/
│   │   ├── overview.md   ← Phase 1: CONCEPT-01
│   │   └── concepts.md   ← Phase 1: CONCEPT-02
│   ├── ch02-openhands/
│   │   ├── overview.md   ← Phase 1: CONCEPT-03 (architecture chapter)
│   │   ├── agent-loop.md ← Phase 1: CONCEPT-03
│   │   ├── actions-observations.md  ← Phase 1: CONCEPT-03
│   │   ├── runtime.md    ← Phase 1: CONCEPT-03
│   │   └── llm-integration.md      ← Phase 1: CONCEPT-03
│   ├── ch03-setup/       ← Phase 2 (stub dir only in Phase 1)
│   ├── ch04-calculator/  ← Phase 4 (stub dir only)
│   ├── ch05-wrap-up/     ← Phase 5 (stub dir only)
│   └── appendix/         ← Phase 5 (stub dir only)
└── book/                 ← generated output (git-ignored)
```

**Note on directory creation:** Only create the actual `.md` files for Phase 1 chapters. Phase 2-5 chapters should appear in SUMMARY.md as draft entries (see below). Do NOT create empty directories for future phases — `mdbook build` does not need them.

### Pattern 1: Exact `book.toml` for This Project

```toml
[book]
title = "에이전틱 AI 튜토리얼: OpenHands로 배우는 AI 에이전트"
authors = ["ohama100"]
description = "OpenHands와 로컬 Qwen LLM을 사용하여 에이전틱 AI를 배우는 한국어 튜토리얼"
language = "ko"
src = "src"

[output.html]
site-url = "/OpenHandsTests/"
default-theme = "light"
preferred-dark-theme = "navy"

[output.html.search]
enable = true

[build]
create-missing = false
```

**Critical fields explained:**

- `language = "ko"`: Sets `<html lang="ko">` in the generated HTML. This is the correct BCP 47 language tag for Korean. mdBook does not use this for locale/UI translation (mdBook's own UI stays in English); it only affects the `lang` attribute for screen readers and search engines.

- `site-url = "/OpenHandsTests/"`: **Must match the GitHub repository name exactly, with leading and trailing slash.** This is the root-relative path where the book is hosted on GitHub Pages for project pages (`https://ohama100.github.io/OpenHandsTests/`). Without this, CSS, JS, and navigation links will 404 on deployed Pages. For user/org pages (`username.github.io`), use `site-url = "/"`.

- `create-missing = false`: **Explicitly set this to `false` for Phase 1.** This means if SUMMARY.md accidentally references a real file that doesn't exist, `mdbook build` will fail loudly rather than silently creating an empty file. This makes broken-link bugs visible immediately. Works in tandem with the draft-chapter strategy (see below): draft chapters have no path, so they never trigger the missing-file check.

- `default-theme = "light"`: Sensible default; no reason to change.

- `preferred-dark-theme = "navy"`: The standard dark option; no reason to change.

**Fields NOT needed in Phase 1** (add later):
- `git-repository-url`: Add in Phase 5 when GitHub repo is public.
- `edit-url-template`: Optional quality-of-life; add in Phase 5.

### Pattern 2: Safe SUMMARY.md Strategy for a Partial Book

**The problem:** SUMMARY.md must not reference files that don't exist when `create-missing = false`, or `mdbook build` fails. But Phase 1 only writes ~7 chapter files out of the full ~17-chapter structure. The SUMMARY.md must represent the whole book structure from Day 1 to avoid renumbering URLs later.

**The solution: Draft chapters.** mdBook's official mechanism for planned-but-not-yet-written chapters is the draft chapter syntax: `- [Title]()` (link with empty href). Draft chapters render as disabled links in the sidebar TOC. They do NOT reference files, so they never trigger missing-file errors.

**Rule:** Every chapter written in Phase 1 gets a real file path. Every chapter to be written in Phases 2-5 appears as a draft entry in SUMMARY.md.

**Phase 1 SUMMARY.md (exact structure to commit):**

```markdown
# Summary

[이 튜토리얼에 대하여](about.md)

# 1부: 에이전틱 AI란 무엇인가

- [에이전틱 AI 개요](ch01-agentic-ai/overview.md)
- [핵심 개념과 용어](ch01-agentic-ai/concepts.md)

# 2부: OpenHands 아키텍처

- [OpenHands 개요](ch02-openhands/overview.md)
- [에이전트 루프 상세](ch02-openhands/agent-loop.md)
- [액션과 관찰 타입](ch02-openhands/actions-observations.md)
- [런타임과 샌드박스](ch02-openhands/runtime.md)
- [LLM 연동: LiteLLM](ch02-openhands/llm-integration.md)

# 3부: 환경 설정

- [OpenHands 설치]()
- [로컬 Qwen 서버 연결]()
- [첫 실행 테스트]()

# 4부: OpenHands로 F# 계산기 만들기

- [예제 프로젝트 소개]()
- [태스크 계획 단계]()
- [코드 작성 단계]()
- [빌드와 테스트 단계]()
- [완성된 계산기]()

# 5부: 정리와 심화

- [개념 되짚기]()
- [다음 단계]()

---

[부록 A: 자주 묻는 질문]()
[부록 B: 트러블슈팅]()
```

**Why this works:** Only chapters with `(path.md)` references are checked for file existence. Draft entries with `()` are never checked. `mdbook build` succeeds; sidebar shows all chapters but drafts are grayed out and unclickable.

**URL stability:** This SUMMARY.md structure is the full book from the start. Numbered chapter URLs (e.g., `/ch01-agentic-ai/overview.html`) will not change in later phases — adding file paths to draft entries doesn't change URLs. Renaming or reordering later would break URLs and break GitHub Pages navigation, so commit this structure and don't reorder.

### Pattern 3: File Naming Convention

- Use `kebab-case` for all directories and files: `ch01-agentic-ai/`, `agent-loop.md`.
- Use Korean part headings (`# 1부:`) and English-slugged file names. This is conventional for Korean mdBooks and avoids URL-encoding issues with Korean filenames.
- Every subdirectory chapter uses a subdirectory with individual `.md` files (not `README.md` inside the subdir) to keep URLs predictable. `README.md` files are auto-converted to `index.html` by the `index` preprocessor — useful but adds indirection. Explicit file names are simpler.

---

## OpenHands V1 Facts for the Architecture Chapter

The architecture chapter (CONCEPT-03) covers the `step()` loop, EventLog, DockerWorkspace, and LiteLLM. These facts are verified against ARCHITECTURE.md (which cites the SDK paper arXiv 2511.03690 and official SDK docs). The planner should ensure the writing tasks reference these specific facts.

### Minimal Correct Set (what the chapter MUST get right)

**1. The Five-Phase Agent Loop** (inside `Conversation.step()`, called by the `while not finished:` loop)

```
Phase 1: Drain pending actions (execute confirmed actions)
Phase 2: Honor user blocks (stop if user rejected)
Phase 3: Prepare LLM prompt (filter EventLog → convert to messages → condense if >80 events)
Phase 4: Call LLM with retry (LiteLLM → HTTP POST to model endpoint)
Phase 5: Classify and dispatch (tool call → ActionEvent → Workspace.execute_action(); text → MessageEvent)
```

**2. EventLog as append-only source of truth**

- Every agent-environment interaction is recorded as an event; events are never deleted.
- Condensation marks ranges as "forgotten" without removing them — full history is preserved for replay.
- Two categories: **LLM-visible** (sent to the model) and **internal** (framework-only).
- Key types: `SystemPromptEvent`, `MessageEvent`, `ActionEvent` (agent tool call), `ObservationEvent` (tool result), `AgentErrorEvent`, `CondensationSummaryEvent`.

**3. ActionEvent / ObservationEvent (the core interaction cycle)**

- Agent emits `ActionEvent` → Workspace executes → returns `ObservationEvent` appended to log.
- Key action subtypes for this tutorial: `CmdRunAction` (shell), `FileEditAction` (string-replace edit), `FileWriteAction`, `FileReadAction`, `AgentThinkAction` (pure reasoning, no side effects), `AgentFinishAction` (terminates loop).
- Observation carries: stdout + stderr + exit code (for `CmdRunAction`), diff (for `FileEditAction`), content (for `FileReadAction`).

**4. DockerWorkspace + Action Execution Server**

- Agent code is identical regardless of workspace — workspace is injected at construction time.
- `DockerWorkspace` runs a FastAPI Action Execution Server inside the container at `POST /execute_action`.
- Persistent bash session via tmux (preserves `cd` across actions); persistent IPython kernel.
- Self-correction is emergent: stderr/exit codes from failed commands re-enter the EventLog → LLM sees them in the next prompt → emits a fix action.

**5. LiteLLM + `openai/` prefix**

- LiteLLM wraps all LLM providers under one Chat Completions API surface.
- For a local OpenAI-compatible endpoint: model string = `openai/<model-id>` (the `openai/` prefix tells LiteLLM to use the OpenAI client library); `base_url` = `http://host.docker.internal:8000/v1` (when OpenHands is inside Docker targeting the host's MLX server).
- This is how the tutorial's local Qwen server is connected — the architecture chapter should make this explicit.

### V0-vs-V1 Trap to Avoid

V0 (deprecated April 2026) was a monolithic sandbox-centric design. V1 is a clean four-package SDK (`openhands-sdk`, `openhands-tools`, `openhands-workspace`, `openhands-agent-server`). Old blog posts and tutorials describe V0. The architecture chapter must describe V1. Sources: SDK paper (arXiv 2511.03690), SDK docs at docs.openhands.dev/sdk.

---

## Concept ↔ Component Mapping (shared by vocabulary and architecture chapters)

This table must be consistent across CONCEPT-02 (vocabulary) and CONCEPT-03 (architecture). The vocabulary chapter introduces the concept; the architecture chapter shows the OpenHands component that embodies it. Each vocabulary entry must include a forward pointer to where it appears in the run (Phase 4).

| Agentic Concept | OpenHands V1 Component | Forward Pointer (Phase 4) |
|----------------|------------------------|---------------------------|
| Tool/function calling | `ActionEvent` subtypes (CmdRunAction, FileEditAction, etc.) + tool schemas sent to LLM | 4부: 코드 작성 단계 (FileWriteAction, FileEditAction) |
| Agent loop | `Conversation.step()` in `while not finished:` | 4부: 태스크 계획 단계, 코드 작성 단계, 빌드와 테스트 단계 |
| Action | Any `ActionEvent` subtype | All 4부 chapters |
| Observation | `ObservationEvent` (stdout/stderr/exit code, diff, content) | 4부: 빌드와 테스트 단계 (build errors → self-correction) |
| Memory / context window | `EventLog` (append-only log); `CondensationSummaryEvent` (compression) | 4부: long multi-step run (condensation may trigger) |
| Plan → Write → Test → Run | CodeActAgent's 4-phase methodology: Explore → Analyze → Implement → Verify | All 4부 chapters, each representing one phase |
| Self-correction | Stderr in `CmdOutputObservation` → LLM emits fix `FileEditAction` | 4부: 빌드와 테스트 단계 (real error-and-fix cycle) |
| Sandbox / isolation | DockerWorkspace + FastAPI Action Execution Server inside container | 3부: OpenHands 설치 |
| LLM abstraction | LiteLLM + `openai/` prefix routing to local Qwen endpoint | 3부: 로컬 Qwen 서버 연결 |

**Authoring instruction for CONCEPT-02:** Each vocabulary entry should have a "튜토리얼에서 보기" (See in tutorial) callout box or inline sentence like: *"4부 '빌드와 테스트 단계'에서 OpenHands가 빌드 오류를 관찰(ObservationEvent)하고 수정 코드를 작성(FileEditAction)하는 장면을 볼 수 있습니다."*

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Partial book without missing-file errors | Manually create empty stub `.md` files for every chapter | Draft chapters in SUMMARY.md: `- [Title]()` | Official mechanism; stubs add noise, clutter git history, and require cleanup later |
| Korean language support | Custom CSS hacks | `language = "ko"` in `[book]` section | mdBook sets `<html lang="ko">` automatically; no custom work needed |
| Relative links between chapters | Absolute paths or manual URL construction | Standard relative Markdown links: `[see vocabulary](../ch01-agentic-ai/concepts.md)` | mdBook resolves relative paths from the source file location; this is the standard approach |
| Syntax diagrams | A third-party preprocessor (mdbook-mermaid adds deps) | ASCII art in a code block, or a static `.png` image in `src/assets/` | Zero extra deps; builds cleanly; sufficient for the agent-loop diagram |

**Key insight:** The draft-chapter approach is the correct solution for a partial book. Empty stub files look cleaner in the TOC (they appear as clickable links) but they require creating and later populating 10+ files that the planner didn't intend to write in Phase 1. Draft entries are designed exactly for this use case.

---

## Common Pitfalls

### Pitfall 1: Wrong `site-url` format

**What goes wrong:** CSS and JS assets 404 on deployed GitHub Pages; the book renders as unstyled HTML.
**Why it happens:** `site-url` defaults to `/`. Project pages are served at `/<repo>/` not `/`. If the repo is named `OpenHandsTests`, the site-url must be `/OpenHandsTests/` (including trailing slash).
**How to avoid:** Set `site-url = "/OpenHandsTests/"` in `book.toml` before the first `mdbook build`. Verify locally with `mdbook build && python3 -m http.server --directory book` and navigate to `http://localhost:8000/OpenHandsTests/`.
**Warning signs:** All CSS missing; navigation links go to `/chapter.html` instead of `/OpenHandsTests/chapter.html`.

### Pitfall 2: Referencing chapter files that don't exist with `create-missing = true`

**What goes wrong:** `mdbook build` silently creates empty stub files for every chapter listed in SUMMARY.md. Phase 1 commits 10+ empty files that need to be removed or filled in later, and they show up as clickable but blank pages in the deployed book.
**Why it happens:** `create-missing = true` is the mdBook default.
**How to avoid:** Set `create-missing = false` in `[build]`. Use draft chapter syntax `- [Title]()` for unwritten chapters. `mdbook build` will not try to open those files.
**Warning signs:** After `mdbook build`, `git status` shows many new empty `.md` files you didn't intend to create.

### Pitfall 3: Describing OpenHands V0 architecture

**What goes wrong:** The architecture chapter explains the wrong system. Readers running current OpenHands (V1 SDK) will be confused by component names and structure that don't match.
**Why it happens:** Most Google-findable OpenHands blog posts and older docs describe V0 (pre-April 2026).
**How to avoid:** Use ARCHITECTURE.md (this project's research doc, citing SDK paper arXiv 2511.03690) as the sole source for the architecture chapter. Do not consult external blog posts.
**Warning signs:** Chapter refers to components like `sandbox` (V0 term) instead of `workspace`; mentions `docker_sandbox` in config; doesn't mention EventLog or four-package SDK.

### Pitfall 4: Vocabulary chapter without forward pointers

**What goes wrong:** CONCEPT-02 reads like a glossary. Readers learn definitions but can't connect them to the real run they're about to see. The requirement explicitly demands forward pointers to where each concept appears.
**Why it happens:** It's easier to write isolated definitions.
**How to avoid:** After each vocabulary definition, include one sentence: *"[개념]은 4부의 [챕터 제목]에서 OpenHands가 [구체적 행동]할 때 볼 수 있습니다."*
**Warning signs:** Vocabulary chapter reads as a standalone glossary with no mentions of specific later chapters.

### Pitfall 5: Korean filenames in `src/`

**What goes wrong:** File system issues on case-insensitive macOS, URL-encoding problems in GitHub Pages, `git` percent-encodes Korean characters in `git status` output.
**Why it happens:** It seems natural to name files in Korean for a Korean book.
**How to avoid:** Use ASCII kebab-case for all `.md` filenames and directory names (e.g., `ch01-agentic-ai/`, `agent-loop.md`). Korean appears only in chapter titles within SUMMARY.md and in the file content.
**Warning signs:** Filenames like `에이전트-루프.md`; percent-encoded URLs in the deployed book.

---

## Code Examples

### Minimal `book.toml` for This Project

```toml
# Source: mdBook official docs + verified field names
[book]
title = "에이전틱 AI 튜토리얼: OpenHands로 배우는 AI 에이전트"
authors = ["ohama100"]
description = "OpenHands와 로컬 Qwen LLM을 사용하여 에이전틱 AI를 배우는 한국어 튜토리얼"
language = "ko"
src = "src"

[output.html]
site-url = "/OpenHandsTests/"
default-theme = "light"
preferred-dark-theme = "navy"

[output.html.search]
enable = true

[build]
create-missing = false
```

### `mdbook init` Invocation

```bash
# From the repo root (/Users/ohama/projs/OpenHandsTests/)
mdbook init .
# This creates: book.toml (minimal), src/SUMMARY.md, src/chapter_1.md
# Then replace book.toml and SUMMARY.md with the above content
# Delete src/chapter_1.md (it's a placeholder)
```

### Draft Chapter Syntax (SUMMARY.md)

```markdown
# Built but not yet written (renders as disabled TOC link):
- [OpenHands 설치]()

# Written in Phase 1 (renders as clickable link):
- [에이전틱 AI 개요](ch01-agentic-ai/overview.md)
```

### Relative Links Between Chapters

```markdown
<!-- In ch02-openhands/agent-loop.md, linking back to vocabulary chapter: -->
[핵심 개념 챕터](../ch01-agentic-ai/concepts.md)에서 정의한 에이전트 루프를 OpenHands가 어떻게 구현하는지 살펴봅니다.

<!-- In ch01-agentic-ai/concepts.md, forward pointer: -->
이 개념은 [4부: 빌드와 테스트 단계](../ch04-calculator/testing.md)에서 실제 오류-수정 사이클로 등장합니다.
<!-- Note: this link will be to a draft-chapter path; it will be dead until Phase 4 writes the file.
     Options: (1) omit the link and use prose only; (2) include the link knowing it'll be dead until Phase 4.
     Recommendation: use prose only ("4부에서 볼 수 있습니다") to avoid dead links in the deployed Phase 1 book. -->
```

**Forward pointer guidance:** Because the Phase 4+ chapters are drafts (no files yet), forward links to them will produce 404s in the deployed Phase 1 book. Use prose-only forward references ("4부에서 볼 수 있습니다") rather than Markdown links to chapter files that don't exist yet.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|---|---|---|---|
| `gh-pages` branch deploy | `actions/deploy-pages@v4` (GitHub Actions native) | GitHub, ~2023 | Cleaner CI; no branch push permissions needed |
| V0 OpenHands (monolithic sandbox) | V1 SDK (four-package modular) | April 2026 | Architecture chapter must describe V1 |
| `create-missing = true` default + stub files | Draft chapters `- [Title]()` | mdBook has supported drafts for years; awareness low | Cleaner partial-book strategy; no empty files |

---

## Open Questions

1. **Exact GitHub repo name for `site-url`**
   - What we know: PROJECT.md says the repo is at `/Users/ohama/projs/OpenHandsTests` — the directory is named `OpenHandsTests`.
   - What's unclear: The GitHub remote repo may have a different name (e.g., `openhands-tutorial`) if the author renames it when pushing.
   - Recommendation: Use `site-url = "/OpenHandsTests/"` as the default, but note in 01-01 plan that this must be confirmed against the actual GitHub repo name before the final build. It's easy to change in book.toml at any time before Phase 5 deploy.

2. **`about.md` as prefix chapter vs numbered chapter**
   - What we know: SUMMARY.md supports prefix chapters (lines before the first `# Part` heading) that are unnumbered.
   - What's unclear: Whether the author wants the intro page unnumbered (cleaner, typical for forewords) or numbered as chapter 1.
   - Recommendation: Make it a prefix chapter (unnumbered). This matches convention and avoids renumbering all subsequent chapters if the intro grows.

---

## Sources

### Primary (HIGH confidence)
- `rust-lang.github.io/mdBook/format/configuration/general.html` — `[book]` fields: `language`, `title`, `authors`, `description`, `src`; `[build]` fields: `create-missing` (default `true`, set `false` to error on missing files)
- `rust-lang.github.io/mdBook/format/configuration/renderers.html` — `[output.html]` fields: `site-url` (default `/`), `default-theme`, `preferred-dark-theme`, `search.enable`
- `rust-lang.github.io/mdBook/format/summary.html` — draft chapter syntax `- [Title]()` (no path = disabled TOC link, no file reference, never triggers missing-file check)
- `rust-lang.github.io/mdBook/cli/init.html` — `mdbook init` creates missing files from SUMMARY.md when `create-missing = true`
- `github.com/rust-lang/mdBook/blob/master/guide/book.toml` — official mdBook docs' own book.toml; `site-url = "/mdBook/"` confirms project-pages pattern
- `ARCHITECTURE.md` (this project, 2026-05-27, HIGH) — all OpenHands V1 facts; 5-phase step() loop; EventLog; ActionEvent/ObservationEvent; DockerWorkspace; LiteLLM; V0-vs-V1 distinction
- `STACK.md` (this project, 2026-05-27, HIGH) — mdBook 0.5.3 version; Homebrew install; `site-url` convention; GitHub Actions deploy pattern
- `SUMMARY.md research` (this project, 2026-05-27, HIGH) — concept↔component mapping table; phase structure rationale

### Secondary (MEDIUM confidence)
- GitHub issue #540 (rust-lang/mdBook) — confirmed that missing files were historically treated as empty pages; PR #541 introduced `create-missing` behavior
- GitHub issue #1246 (rust-lang/mdBook) — `mdbook serve` and `mdbook build` create files linked from SUMMARY.md if they don't exist when `create-missing = true`

---

## Metadata

**Confidence breakdown:**
- `book.toml` fields: HIGH — fetched from official mdBook docs
- `site-url` for project pages: HIGH — confirmed via mdBook's own book.toml using `/mdBook/` pattern
- `create-missing = false` + draft chapters: HIGH — confirmed from official config docs and issue history
- OpenHands V1 architecture facts: HIGH — ARCHITECTURE.md cites SDK paper + official SDK docs
- Korean `language = "ko"` support: HIGH — mdBook accepts any BCP 47 language code; sets `<html lang="...">` only
- Forward-pointer link strategy: MEDIUM — the dead-link risk of linking to unwritten chapters is a logical inference; use prose-only forward references as the safe default

**Research date:** 2026-05-27
**Valid until:** 2026-08-27 (mdBook is stable; OpenHands V1 SDK is current; reassess if mdBook 0.6+ releases)
